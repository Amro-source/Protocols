import numpy as np
from scipy.signal import butter, lfilter, find_peaks
import pyaudio
import matplotlib.pyplot as plt  # For debugging

# Morse code dictionary
MORSE_CODE_DICT = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
    'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
    'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..',
    '0': '-----', '1': '.----', '2': '..---', '3': '...--', '4': '....-',
    '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.',
    ' ': '/'
}

REVERSE_MORSE_DICT = {v: k for k, v in MORSE_CODE_DICT.items()}

def encode_to_morse(text):
    return ' '.join(MORSE_CODE_DICT[char] for char in text.upper() if char in MORSE_CODE_DICT)

def play_morse_code(morse_code, frequency=800, sample_rate=44100, volume=0.5):
    dot_duration = 0.1  # seconds
    audio = np.array([], dtype=np.float32)
    
    for char in morse_code:
        if char == '.':
            t = np.linspace(0, dot_duration, int(dot_duration * sample_rate), False)
            tone = volume * np.sin(2 * np.pi * frequency * t)
            audio = np.concatenate((audio, tone))
            audio = np.concatenate((audio, np.zeros(int(dot_duration * sample_rate))))
        elif char == '-':
            t = np.linspace(0, 3*dot_duration, int(3*dot_duration * sample_rate), False)
            tone = volume * np.sin(2 * np.pi * frequency * t)
            audio = np.concatenate((audio, tone))
            audio = np.concatenate((audio, np.zeros(int(dot_duration * sample_rate))))
        elif char == ' ':
            audio = np.concatenate((audio, np.zeros(int(3*dot_duration * sample_rate))))
        elif char == '/':
            audio = np.concatenate((audio, np.zeros(int(7*dot_duration * sample_rate))))

    audio = np.int16(audio * (2**15 - 1) / np.max(np.abs(audio)))
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=sample_rate, output=True)
    stream.write(audio.tobytes())
    stream.stop_stream()
    stream.close()
    p.terminate()
    return audio

def decode_morse_audio(audio, sample_rate=44100, debug=False):
    # Convert to float and normalize
    audio = audio.astype(np.float32) / (2**15 - 1)
    
    # Bandpass filter
    nyq = 0.5 * sample_rate
    low = 500 / nyq
    high = 2000 / nyq
    b, a = butter(5, [low, high], btype='band')
    filtered = lfilter(b, a, audio)
    
    # Rectify and smooth
    envelope = np.abs(filtered)
    window_size = int(0.02 * sample_rate)  # 20ms smoothing window
    smoothed = np.convolve(envelope, np.ones(window_size)/window_size, mode='same')
    
    # Dynamic threshold
    threshold = 0.2 * np.max(smoothed)
    signal = smoothed > threshold
    
    # Find signal edges
    rising = np.where(np.diff(signal.astype(int)) > 0)[0]
    falling = np.where(np.diff(signal.astype(int)) < 0)[0]
    
    # Handle edge cases
    if len(rising) == 0 or len(falling) == 0:
        return ""
    
    if falling[0] < rising[0]:
        rising = np.insert(rising, 0, 0)
    if rising[-1] > falling[-1]:
        falling = np.append(falling, len(signal)-1)
    
    # Calculate durations in seconds
    durations = (falling - rising) / sample_rate
    gaps = (rising[1:] - falling[:-1]) / sample_rate
    
    # Morse timing parameters
    dot_time = 0.1
    dash_time = 3 * dot_time
    symbol_gap = dot_time
    letter_gap = 3 * dot_time
    word_gap = 7 * dot_time
    
    morse_code = []
    prev_end = falling[0] if len(falling) > 0 else 0
    
    # Debug plot
    if debug:
        plt.figure(figsize=(12, 6))
        plt.plot(audio, label='Original')
        plt.plot(smoothed, label='Smoothed')
        plt.axhline(threshold, color='r', linestyle='--', label='Threshold')
        for r in rising:
            plt.axvline(r, color='g', linestyle=':', alpha=0.5)
        for f in falling:
            plt.axvline(f, color='r', linestyle=':', alpha=0.5)
        plt.legend()
        plt.show()
    
    for i, (start, end) in enumerate(zip(rising, falling)):
        # Check gap before this symbol
        if i > 0:
            gap = (start - prev_end) / sample_rate
            if gap > word_gap * 0.7:
                morse_code.append(' / ')
            elif gap > letter_gap * 0.7:
                morse_code.append(' ')
        
        # Determine symbol
        duration = (end - start) / sample_rate
        if duration > dash_time * 0.7:  # 70% of dash time as threshold
            morse_code.append('-')
        else:
            morse_code.append('.')
        
        prev_end = end
    
    return ''.join(morse_code).strip()

def decode_morse_to_text(morse_code):
    words = morse_code.split('/')
    text = []
    for word in words:
        letters = word.strip().split()
        for letter in letters:
            if letter in REVERSE_MORSE_DICT:
                text.append(REVERSE_MORSE_DICT[letter])
        text.append(' ')
    return ''.join(text).strip()

def test_morse_system():
    test_text = "THE QUICK BROWN FOX"
    print(f"Original text: {test_text}")
    
    morse = encode_to_morse(test_text)
    print(f"Morse code: {morse}")
    
    audio = play_morse_code(morse)
    
    decoded_morse = decode_morse_audio(audio, debug=True)  # Enable debug plots
    print(f"Decoded Morse: {decoded_morse}")
    
    decoded_text = decode_morse_to_text(decoded_morse)
    print(f"Decoded text: {decoded_text}")
    
    success = test_text == decoded_text
    print(f"Test {'passed' if success else 'failed'}")
    return success

if __name__ == "__main__":
    test_morse_system()
