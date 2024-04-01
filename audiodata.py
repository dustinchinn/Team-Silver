import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf

def plot_sound_file(filename):

    data, samplerate = sf.read(filename)

    time = np.arange(0, len(data)) / samplerate

    rms = np.sqrt(np.mean(data ** 2))
    dbfs = 20 * np.log10(rms / 1.0) 

 
    plt.figure(figsize=(10, 5))
    plt.plot(time, data, color='b')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.title('Sound Waveform')
    plt.grid(True)

 
    plt.text(0.05, 0.95, f'DBFS: {dbfs:.2f} dB', transform=plt.gca().transAxes, ha='left', va='top', color='red')

    plt.show()


filename = "output.wav"
plot_sound_file(filename)
