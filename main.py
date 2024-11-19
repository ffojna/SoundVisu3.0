import sounddevice as sd
import scipy.io.wavfile
import numpy as np
import scipy.fftpack
import os, keyboard, time
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox, font
import threading
from modules.CustomCheckbox import CustomCheckbox


# paths to images (mapujesz tutaj odpowiednie obrazy (ścieżki) do dźwięków)
NOTE_IMAGES = {
    "E2": "images/E2.png",
    "F2": "images/F2.png",
    "F#2": "images/F#2.png",
    "G2": "images/G2.png",
    "G#2": "images/G#2.png",
    "A2": "images/A2.png",
    "A#2": "images/A#2.png",
    "B2": "images/B2.png",
    "C3": "images/C3.png",
    "C#3": "images/C#3.png",
    "D3": "images/D3.png",
    "D#3": "images/D#3.png",
    "E3": "images/E3.png",
    "F3": "images/F3.png",
    "F#3": "images/F#3.png",
    "G3": "images/G3.png",
    "G#3": "images/G#3.png",
    "A3": "images/A3.png",
    "A#3": "images/A#3.png",
    "B3": "images/B3.png",
    "C4": "images/C4.png",
    "C#4": "images/C#4.png",
    "D4": "images/D4.png",
    "D#4": "images/D#4.png",
    "E4": "images/E4.png",
    "F4": "images/F4.png",
    "F#4": "images/F#4.png",
    "G4": "images/G4.png",
    "G#4": "images/G#4.png",
    "A4": "images/A4.png",
    "A#4": "images/A#4.png",
    "B4": "images/B4.png",
    "C5": "images/C5.png",
    "C#5": "images/C#5.png",
    "D5": "images/D5.png",
    "D#5": "images/D#5.png",
    "E5": "images/E5.png"
}

# general settings
SAMPLE_FREQ = 44100                         # sample frequency in Hz
WINDOW_SIZE = 4096                          # window size of the DFT in samples
WINDOW_STEP = int(WINDOW_SIZE / 2)          # step size of window
WINDOW_T_LEN = WINDOW_SIZE / SAMPLE_FREQ    # length of window in seconds
SAMPLE_T_LENGTH = 1 / SAMPLE_FREQ           # length between two samples in seconds (to też ze wzoru)
DEFAULT_NOISE_GATE_THRESHOLD = 0.05
DEFAULT_NUM_OF_SAMLPES = 4
DEFAULT_BASS_THRESHOLD = 334                # frequencies bellow which are considered as bass frequencies
DEFAULT_BASS_REDUCTION = -6


# setting up variables
num_of_samples = DEFAULT_NUM_OF_SAMLPES
noise_gate = DEFAULT_NOISE_GATE_THRESHOLD
bass_threshold = DEFAULT_BASS_THRESHOLD
bass_reduction = DEFAULT_BASS_REDUCTION
windowSamples = np.zeros(WINDOW_SIZE)
closestNote = ''

# funciton to find closest note for given pitch
CONCERT_PITCH = 440
ALL_NOTES = ["A","A#","B","C","C#","D","D#","E","F","F#","G","G#"]

def find_closest_note(pitch):
    i = int(np.round(np.log2(pitch/CONCERT_PITCH) * 12))
    closest_note = ALL_NOTES[i % 12] + str(4 + (i + 9) // 12) # ze wzoru na i
    closest_pitch = CONCERT_PITCH*2**(i/12)                 # ze wzoru na f(i)
    return closest_note, closest_pitch

# setting up the image display
def update_image(img_path):
    new_image = Image.open(img_path)
    new_display = ImageTk.PhotoImage(new_image)
    label.config(image=new_display)
    label.image = new_display

recent_freqs = []
def image_callback(indata, frames, time, status):
    global windowSamples, closestNote
    if status:
        print(status)
    if any(indata):
        windowSamples = np.roll(windowSamples, -frames)
        windowSamples[-frames:] = indata[:, 0]
        magnitudeSpec = abs(scipy.fftpack.fft(windowSamples)[:len(windowSamples)//2])
        
        # obniżam basowe o 3 dB
        # po analizie zauważyłem, że przy mieszaniu dźwięków te dominują nad sopranami i przy melodiach się gubią
        freq_bin_bass = int(bass_threshold / (SAMPLE_FREQ / WINDOW_SIZE))
        magnitudeSpec[:freq_bin_bass] *= 10 ** (bass_reduction / 20)
        
        magnitudeSpec[:int(62 / (SAMPLE_FREQ / WINDOW_SIZE))] = 0
        
        maxInd = np.argmax(magnitudeSpec)
        maxFreq = maxInd * (SAMPLE_FREQ / WINDOW_SIZE)
        # new_closestNote, closestPitch = find_closest_note(maxFreq)
        
        recent_freqs.append(maxFreq)
        if len(recent_freqs) > num_of_samples:
            recent_freqs.pop(0)
            
        # avgFreq = np.mean(recent_freqs)   # po średniej
        avgFreq = max(set(recent_freqs), key=recent_freqs.count)
        new_closestNote, closestPitch = find_closest_note(avgFreq)
        
        # noise gate
        if noise_gate_active.get():
            if magnitudeSpec[maxInd] < noise_gate:
                return
        
        if new_closestNote != closestNote:
            closestNote = new_closestNote
            os.system('cls' if os.name=='nt' else 'clear')
            diffPitch = maxFreq - closestPitch
            print(f"Closest note: {closestNote} {diffPitch:.1f}")
            print(recent_freqs)
            print(avgFreq)
            if closestNote in NOTE_IMAGES:
                img_path = NOTE_IMAGES[closestNote]
                update_image(img_path)
                
                
    else:
        print("no input")

# stop the program button
running = True
def stop_loop():
    global running
    running = False
    print("Stopping...")
    on_closing()
keyboard.add_hotkey('esc', stop_loop)

def check_num_of_samples():
    global num_of_samples
    entry_content = num_of_samples_spinbox.get()
    if entry_content.strip() != "":
        try:
            num_of_samples = int(entry_content)
        except ValueError:
            messagebox.showerror("Invalid Input", "Number of samples\nPlease enter a positive integer.")
    else:
        num_of_samples = DEFAULT_NUM_OF_SAMLPES
        
    print(f"Number of samples:\t{num_of_samples}")
    
def check_noise_gate():
    global noise_gate
    entry_content = noise_gate_entry.get()
    if entry_content.strip() != "":
        try:
            noise_gate_value = float(entry_content)
            if noise_gate_value >= 0:
                noise_gate = noise_gate_value
            else:
                raise ValueError("Negative value")
        except ValueError:
            messagebox.showerror("Invalid Input", "Noise Gate Threshold\nPlease enter a positive float.")
    else:
        noise_gate = DEFAULT_NOISE_GATE_THRESHOLD
        
    print(f"Noise Gate threshold:\t{noise_gate}")
    
def check_bass_threshold():
    global bass_threshold
    entry_content = bass_threshold_entry.get()
    if entry_content.strip() != "":
        try:
            value = float(entry_content)
            if value >= 0:
                bass_threshold = value
            else:
                raise ValueError("Negative value")
        except ValueError:
            messagebox.showerror("Invalid Input", "Bass Threshold\nPlease enter a positive float.")
    else:
        bass_threshold = DEFAULT_BASS_THRESHOLD
        
    print(f"Bass threshold:\t{bass_threshold}")
    
def check_bass_reduction():
    global bass_reduction
    entry_content = bass_reduction_entry.get()
    if entry_content.strip() != "":
        try:
            value = float(entry_content)
        except ValueError:
            messagebox.showerror("Invalid Input", "Bass reduction\nPlease enter a float.")
    else:
        bass_reduction = DEFAULT_BASS_REDUCTION
        
    print(f"Bass reduction:\t{bass_reduction}")
    
def start_apploop():
    global audio_thread, welcome_label, num_of_samples_label, num_of_samples_spinbox, noise_gate_label, noise_gate_entry, custom_checkbox, start_button, tuner_button, bass_threshold_label, bass_threshold_entry, bass_reduction_label, bass_reduction_entry
    print("Values:")
    check_num_of_samples()
    if noise_gate_active.get():
        print("Using noise gate:")
        check_noise_gate()
    else:
        print("Noise gate is turned off.")
    check_bass_threshold()
    check_bass_reduction()
    
    # destroing all widgets
    welcome_label.destroy()
    num_of_samples_label.destroy()
    num_of_samples_spinbox.destroy()
    custom_checkbox.destroy()
    noise_gate_label.destroy()
    noise_gate_entry.destroy()
    tuner_button.destroy()
    start_button.destroy()
    bass_threshold_label.destroy()
    bass_threshold_entry.destroy()
    bass_reduction_label.destroy()
    bass_reduction_entry.destroy()
    
    time.sleep(3)
    
    audio_thread = threading.Thread(target=start_audio_stream)
    audio_thread.start()

def start_tunerloop():
    pass

root = tk.Tk()
root.title("SoundVisu v2.0")
root.configure(bg='#333333')

image_frame = tk.Frame(root, bg='#333333')
image_frame.grid(row=0, column=0, columnspan=2, sticky='n')
image = Image.open("images/init.png")
display = ImageTk.PhotoImage(image)
label = tk.Label(image_frame, image=display, bg='#333333')
label.grid(row=0, column=0, columnspan=3, sticky='news')
#root.geometry("1920x1050")

# main menu
bold_rubik = font.Font(family="Rubik", size=14, weight="bold")

welcome_label = tk.Label(root, text="Welcome to SoundVisu!", bg='#333333', font=bold_rubik, fg='#FFFFFF')

num_of_samples_label = tk.Label(root, text="Number of samples:", bg='#333333', font=("Rubik", 14), fg='#FFFFFF')
defualt_numsamples = tk.StringVar(root)
defualt_numsamples.set(str(DEFAULT_NUM_OF_SAMLPES))
num_of_samples_spinbox = tk.Spinbox(root, from_=1, to=100, textvariable=defualt_numsamples)

noise_gate_active = tk.BooleanVar()
custom_checkbox = CustomCheckbox(root, variable=noise_gate_active, onvalue=True, offvalue=False)
noise_gate_label = tk.Label(root, text="Noise gate threshold:", bg='#333333', font=("Rubik", 14), fg='#FFFFFF')
noise_gate_entry = tk.Entry(root)

bass_threshold_label = tk.Label(root, text="Frequency of highest bass:", bg='#333333', font=("Rubik", 14), fg='#FFFFFF')
bass_threshold_entry = tk.Entry(root)

bass_reduction_label = tk.Label(root, text="Bass reduction (in dB):", bg='#333333', font=("Rubik", 14), fg='#FFFFFF')
bass_reduction_entry = tk.Entry(root)

start_button_image = ImageTk.PhotoImage(Image.open("images/bStart.png"))
start_button = tk.Button(root, image=start_button_image, bg='#333333', fg='#FFFFFF', command=start_apploop)

tuner_button_image = ImageTk.PhotoImage(Image.open("images/bTuner.png"))
tuner_button = tk.Button(root, image=tuner_button_image, bg='#333333', fg='#FFFFFF')

# TODO device select button

welcome_label.grid(row=1, column=0, columnspan=3)
num_of_samples_label.grid(row=2, column=1, padx=20)
num_of_samples_spinbox.grid(row=2, column=2, padx=20)
custom_checkbox.grid(row=3, column=0, padx=20)
noise_gate_label.grid(row=3, column=1, padx=20)
noise_gate_entry.grid(row=3, column=2, padx=20)
bass_threshold_label.grid(row=4, column=1, padx=20)
bass_threshold_entry.grid(row=4, column=2, padx=20)
bass_reduction_label.grid(row=5, column=1, padx=20,)
bass_reduction_entry.grid(row=5, column=2, padx=20)
start_button.grid(row=6, column=2, pady=20)
tuner_button.grid(row=6, column=1)


def start_audio_stream():
    try:
        with sd.InputStream(channels=1, callback=image_callback, blocksize=WINDOW_STEP, samplerate=SAMPLE_FREQ):
            while running:
                root.update_idletasks()
                root.update()
    except Exception as e:
        print(str(e))

def on_closing():
    global running
    running = False
    root.destroy()


# closing window
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()

# ensure proper closing
running = False
audio_thread.join()