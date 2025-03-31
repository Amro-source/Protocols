
import winsound
import time

# Morse code mapping
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

def encode_to_morse(text):
    """Encode text to Morse code"""
    morse_code = ''
    for char in text.upper():
        if char in MORSE_CODE_DICT:
            morse_code += MORSE_CODE_DICT[char] + ' '
    return morse_code

def play_morse_code(morse_code):
    """Play Morse code as sound"""
    dot_duration = 200  # milliseconds
    dash_duration = 3 * dot_duration
    gap_duration = 2 * dot_duration

    for char in morse_code:
        if char == '.':
            winsound.Beep(1000, dot_duration)  # 1000 Hz frequency
            time.sleep(dot_duration / 1000)
        elif char == '-':
            winsound.Beep(1000, dash_duration)  # 1000 Hz frequency
            time.sleep(dash_duration / 1000)
        elif char == ' ':
            time.sleep(gap_duration / 1000)
        elif char == '/':
            time.sleep(2 * gap_duration / 1000)

# Example usage
if __name__ == "__main__":
    text = "Hello World"
    morse_code = encode_to_morse(text)
    print(f"Text: {text}")
    print(f"Morse Code: {morse_code}")

    play_morse_code(morse_code)
