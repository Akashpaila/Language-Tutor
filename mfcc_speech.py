import pyaudio
import wave
import numpy as np
import librosa
import matplotlib.pyplot as plt
import keyboard
import time

# Recording parameters
FORMAT = pyaudio.paInt16  # Audio format (16-bit PCM)
CHANNELS = 1              # Mono audio
RATE = 44100              # Sampling rate (Hz)
CHUNK = 1024              # Buffer size
OUTPUT_FILENAME = "recorded_speech.wav"

def record_audio():
    """Record audio from the microphone until the user presses Enter."""
    audio = pyaudio.PyAudio()
    
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    
    print("Recording... Press Enter to stop.")
    frames = []
 
    while not keyboard.is_pressed('enter'):
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)
        time.sleep(0.01)  # Small sleep to prevent CPU overload
    
    print("Recording finished.")

    stream.stop_stream()
    stream.close()
    audio.terminate()

    wf = wave.open(OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    
    return OUTPUT_FILENAME

def extract_mfcc(audio_file):
    """Extract MFCCs from the audio file."""
    y, sr = librosa.load(audio_file, sr=RATE)

    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    
    return y, sr, mfccs

def visualize_mfcc(mfccs, sr):
    """Visualize MFCCs with values and plots."""
    print("\nMFCC Values (shape: {}):".format(mfccs.shape))
    print(mfccs)
    
    # Plot 1: MFCC Heatmap (Spectrogram-like visualization)
    plt.figure(figsize=(10, 6))
    plt.subplot(2, 1, 1)
    librosa.display.specshow(mfccs, sr=sr, x_axis='time')
    plt.colorbar(format='%+2.0f dB')
    plt.title('MFCC Heatmap')
    plt.xlabel('Time (s)')
    plt.ylabel('MFCC Coefficients')
    
    # Plot 2: MFCC Coefficients over Time (Line Plot for first few coefficients)
    plt.subplot(2, 1, 2)
    for i in range(min(5, mfccs.shape[0])):  # Plot first 5 MFCCs
        plt.plot(mfccs[i], label=f'MFCC {i+1}')
    plt.title('MFCC Coefficients over Time')
    plt.xlabel('Frame')
    plt.ylabel('Amplitude')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('mfcc_visualization.png')
    plt.show()

def main():
    # Step 1: Record audio
    audio_file = record_audio()
    
    # Step 2: Extract MFCCs
    y, sr, mfccs = extract_mfcc(audio_file)
    
    # Step 3: Visualize MFCCs
    visualize_mfcc(mfccs, sr)
    
    print("\nMFCC visualization saved as 'mfcc_visualization.png'")

if __name__ == "__main__":
    main()

    