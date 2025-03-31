import tkinter as tk
from tkinter import ttk
import librosa
import numpy as np
from scipy.signal import butter, lfilter, freqz
import matplotlib.pyplot as plt

def design_filter():
    cutoff = float(cutoff_entry.get())
    order = int(order_entry.get())
    type = filter_type.get()
    nyq = 0.5 * 44100  # Nyquist frequency for 44.1 kHz sampling rate
    normal_cutoff = cutoff / nyq
    
    if type == 'Lowpass':
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
    elif type == 'Highpass':
        b, a = butter(order, normal_cutoff, btype='high', analog=False)
    elif type == 'Bandpass':
        low_cutoff = float(low_cutoff_entry.get())
        high_cutoff = float(high_cutoff_entry.get())
        low_normal_cutoff = low_cutoff / nyq
        high_normal_cutoff = high_cutoff / nyq
        b, a = butter(order, [low_normal_cutoff, high_normal_cutoff], btype='band', analog=False)
    
    w, h = freqz(b, a)
    plt.plot(w, np.abs(h))
    plt.xlabel('Frequency')
    plt.ylabel('Amplitude')
    plt.title('Filter Frequency Response')
    plt.show()

root = tk.Tk()
root.title("Digital Filter Designer")

filter_type = tk.StringVar()
filter_type.set('Lowpass')

cutoff_label = tk.Label(root, text="Cutoff Frequency (Hz):")
cutoff_label.grid(row=0, column=0, padx=5, pady=5)
cutoff_entry = tk.Entry(root, width=10)
cutoff_entry.grid(row=0, column=1, padx=5, pady=5)

order_label = tk.Label(root, text="Filter Order:")
order_label.grid(row=1, column=0, padx=5, pady=5)
order_entry = tk.Entry(root, width=10)
order_entry.grid(row=1, column=1, padx=5, pady=5)

filter_type_label = tk.Label(root, text="Filter Type:")
filter_type_label.grid(row=2, column=0, padx=5, pady=5)
filter_type_option = ttk.OptionMenu(root, filter_type, 'Lowpass', 'Highpass', 'Bandpass')
filter_type_option.grid(row=2, column=1, padx=5, pady=5)

low_cutoff_label = tk.Label(root, text="Low Cutoff Frequency (Hz):")
low_cutoff_label.grid(row=3, column=0, padx=5, pady=5)
low_cutoff_entry = tk.Entry(root, width=10)
low_cutoff_entry.grid(row=3, column=1, padx=5, pady=5)

high_cutoff_label = tk.Label(root, text="High Cutoff Frequency (Hz):")
high_cutoff_label.grid(row=4, column=0, padx=5, pady=5)
high_cutoff_entry = tk.Entry(root, width=10)
high_cutoff_entry.grid(row=4, column=1, padx=5, pady=5)

design_button = tk.Button(root, text="Design Filter", command=design_filter)
design_button.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

root.mainloop()
