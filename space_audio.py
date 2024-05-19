import pyaudio
import wave
import keyboard
import os

import numpy as np
import matplotlib.pyplot as plt

def plot_soundwave(input_file):
    wf = wave.open(input_file, 'rb')
    channels = wf.getnchannels()
    sample_width = wf.getsampwidth()
    frame_rate = wf.getframerate()
    frames = wf.readframes(-1)

    if sample_width == 1:
        data = np.frombuffer(frames, dtype=np.uint8)
    elif sample_width == 2:
        data = np.frombuffer(frames, dtype=np.int16)
    else:
        raise ValueError("Unsupported sample width")

    data = data.astype(np.float32)
    data /= np.max(np.abs(data), axis=0)

    time = np.linspace(0, len(data) / frame_rate, num=len(data))

    plt.figure(figsize=(10, 4))
    plt.plot(time, data, color='blue')
    plt.title('Soundwave')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.grid(True)
    plt.show()


def record_audio(output_file, duration=5):
    chunk = 1024
    sample_format = pyaudio.paInt16
    channels = 1
    fs = 44100
    seconds = duration
    filename = output_file

    p = pyaudio.PyAudio()

    print("Recording...")
    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True)

    frames = []

    for i in range(0, int(fs / chunk * seconds)):
        data = stream.read(chunk)
        frames.append(data)

    print("Length of recorded frames:", len(frames))

    stream.stop_stream()
    stream.close()
    p.terminate()

    print("Finished recording.")

    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()


# def play_audio(input_file):
#     plot_soundwave("recorded_audio.wav")
#
#     chunk = 1024
#     wf = wave.open(input_file, 'rb')
#     p = pyaudio.PyAudio()
#     stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
#                     channels=wf.getnchannels(),
#                     rate=wf.getframerate(),
#                     output=True)
#
#     print("Playing audio...")
#
#     data = wf.readframes(chunk)
#     while data:
#         stream.write(data)
#         data = wf.readframes(chunk)
#
#     # Close the stream and terminate PyAudio after playback finishes
#     stream.close()
#     p.terminate()
#
#     print("Finished playing audio.")
from pydub import AudioSegment
def create_audio_clips(input_file, output_folder, clip_times):
    audio = AudioSegment.from_file(input_file)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for i, (start_time, end_time) in enumerate(clip_times, start=1):
        clip = audio[start_time * 1000:end_time * 1000]
        clip.export(f"{output_folder}/next_song_{i}.wav", format="wav")

input_file = "next_song_full.wav"
output_folder = "next_song"
clip_times = [(0, 3), (3, 6), (6, 9), (9, 12), (12, 15), (15, 18), (18, 21)]



def start_recording():
    output_file = "recorded_audio.wav"
    create_audio_clips(input_file, output_folder, clip_times)

    keyboard.wait('space')
    record_audio(output_file)
    #play_audio(output_file)

start_recording()




