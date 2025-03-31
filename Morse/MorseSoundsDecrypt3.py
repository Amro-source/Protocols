import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
import pyaudio
import sounddevice as sd  # Alternative to pyaudio
from scipy.signal import find_peaks, butter, filtfilt

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

def generate_morse_audio(morse_code, sample_rate=22050, frequency=800, volume=0.8):
    dot_duration = 0.1  # seconds
    audio = np.array([], dtype=np.float32)
    
    for char in morse_code:
        if char == '.':
            tone = librosa.tone(frequency, sr=sample_rate, duration=dot_duration) * volume
            silence = np.zeros(int(dot_duration * sample_rate))
        elif char == '-':
            tone = librosa.tone(frequency, sr=sample_rate, duration=3*dot_duration) * volume
            silence = np.zeros(int(dot_duration * sample_rate))
        elif char == ' ':
            tone = np.array([], dtype=np.float32)
            silence = np.zeros(int(3*dot_duration * sample_rate))
        elif char == '/':
            tone = np.array([], dtype=np.float32)
            silence = np.zeros(int(7*dot_duration * sample_rate))
        
        audio = np.concatenate((audio, tone, silence))
    
    return audio, sample_rate

def play_morse_audio(audio, sample_rate):
    sd.play(audio, sample_rate)
    sd.wait()

def decode_morse_audio(audio, sample_rate=22050):
    # Normalize audio
    audio = audio / np.max(np.abs(audio))
    
    # Bandpass filter (500-2000 Hz)
    nyq = 0.5 * sample_rate
    low = 500 / nyq
    high = 2000 / nyq
    b, a = butter(5, [low, high], btype='band')
    filtered = filtfilt(b, a, audio)
    
    # Compute energy envelope
    envelope = np.abs(filtered)
    window_size = int(0.02 * sample_rate)  # 20ms window
    smoothed = np.convolve(envelope, np.ones(window_size)/window_size, mode='same')
    
    # Threshold detection (dynamic)
    threshold = 0.2 * np.max(smoothed)
    signal = smoothed > threshold
    
    # Find state changes
    changes = np.diff(signal.astype(int))
    starts = np.where(changes == 1)[0]
    ends = np.where(changes == -1)[0]
    
    # Handle edge cases
    if len(starts) == 0 or len(ends) == 0:
        return ""
    if ends[0] < starts[0]:
        starts = np.insert(starts, 0, 0)
    if starts[-1] > ends[-1]:
        ends = np.append(ends, len(signal)-1)
    
    # Morse timing parameters (seconds)
    dot_time = 0.1
    dash_time = 3 * dot_time
    symbol_gap = dot_time
    letter_gap = 3 * dot_time
    word_gap = 7 * dot_time
    
    morse_code = []
    prev_end = 0
    
    for i, (start, end) in enumerate(zip(starts, ends)):
        # Calculate gap (silence) before this symbol
        gap = (start - prev_end) / sample_rate
        
        # Determine gap type
        if i > 0:
            if gap > word_gap * 0.7:
                morse_code.append(' / ')
            elif gap > letter_gap * 0.7:
                morse_code.append(' ')
        
        # Calculate symbol duration
        duration = (end - start) / sample_rate
        
        # Determine symbol type
        if duration > dash_time * 0.7:  # 70% of dash time
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

def visualize_decoding(audio, sample_rate):
    # Filter
    nyq = 0.5 * sample_rate
    b, a = butter(5, [500/nyq, 2000/nyq], btype='band')
    filtered = filtfilt(b, a, audio)
    
    # Envelope
    envelope = np.abs(filtered)
    window_size = int(0.02 * sample_rate)
    smoothed = np.convolve(envelope, np.ones(window_size)/window_size, mode='same')
    
    # Threshold
    threshold = 0.2 * np.max(smoothed)
    signal = smoothed > threshold
    
    # Plot
    plt.figure(figsize=(12, 6))
    plt.plot(audio, alpha=0.3, label='Original')
    plt.plot(filtered, alpha=0.5, label='Filtered')
    plt.plot(smoothed, 'r', label='Envelope')
    plt.axhline(threshold, color='g', linestyle='--', label='Threshold')
    plt.legend()
    plt.title('Morse Code Decoding Visualization')
    plt.xlabel('Samples')
    plt.ylabel('Amplitude')
    plt.show()

def test_morse_system():
    test_message = "SOS"  # Start with simple message
    print(f"Testing message: {test_message}")
    
    morse = encode_to_morse(test_message)
    print(f"Morse code: {morse}")
    
    audio, sr = generate_morse_audio(morse)
    print("Playing Morse code audio...")
    play_morse_audio(audio, sr)
    
    # Visualize the decoding process
    visualize_decoding(audio, sr)
    
    decoded_morse = decode_morse_audio(audio, sr)
    print(f"Decoded Morse: {decoded_morse}")
    
    decoded_text = decode_morse_to_text(decoded_morse)
    print(f"Decoded text: {decoded_text}")
    
    success = test_message == decoded_text
    print(f"Test {'passed' if success else 'failed'}")
    return success

if __name__ == "__main__":
    test_morse_system()
