# import sounddevice as sd
# import numpy as np
# from faster_whisper import WhisperModel
# import queue
# import threading
# from transformers import pipeline

# # Configuration
# SAMPLE_RATE = 16000
# BLOCK_DURATION = 2  # seconds
# MODEL_SIZE = "base"

# # Load models
# model = WhisperModel(MODEL_SIZE, device="cpu")  # Use CPU only
# sentiment_analyzer = pipeline("sentiment-analysis")

# # Audio stream queue
# audio_queue = queue.Queue()

# # Audio callback function
# def audio_callback(indata, frames, time, status):
#     if status:
#         print("Status:", status)
#     audio_queue.put(indata.copy())

# # Transcription + sentiment loop
# def transcription_loop():
#     print("Listening and transcribing...\n")
#     while True:
#         audio_block = audio_queue.get()
#         if audio_block is None:
#             break
#         mono_audio = audio_block.mean(axis=1)
#         segments, _ = model.transcribe(mono_audio, language="en", beam_size=5)
#         for segment in segments:
#             text = segment.text.strip()
#             if not text:
#                 continue
#             print(f"\n🗣️  Transcribed: {text}")
#             try:
#                 sentiment = sentiment_analyzer(text)[0]
#                 label = sentiment["label"]
#                 score = sentiment["score"]
#                 print(f"🧠  Sentiment: {label} (Confidence: {score:.2f})")
#             except Exception as e:
#                 print("Sentiment analysis error:", str(e))

# # Run the audio stream
# try:
#     with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="float32",
#                         callback=audio_callback, blocksize=int(SAMPLE_RATE * BLOCK_DURATION)):
#         thread = threading.Thread(target=transcription_loop)
#         thread.start()
#         thread.join()
# except KeyboardInterrupt:
#     print("\nStopped by user.")


import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel
import queue
import threading
import soundfile as sf  # For saving audio
from transformers import pipeline

# Configuration
SAMPLE_RATE = 16000
BLOCK_DURATION = 2  # seconds
MODEL_SIZE = "base"

# Load models
model = WhisperModel(MODEL_SIZE, device="cpu")
sentiment_analyzer = pipeline("sentiment-analysis")

# Audio queue and buffer
audio_queue = queue.Queue()
audio_buffer = []  # To store audio blocks
stop_event = threading.Event()

# Audio callback function
def audio_callback(indata, frames, time, status):
    if status:
        print("Status:", status)
    audio_queue.put(indata.copy())
    audio_buffer.append(indata.copy())  # Save to buffer

# Transcription + sentiment loop
def transcription_loop():
    print("🎤 Listening... Press Enter to stop and save.\n")
    while not stop_event.is_set():
        try:
            audio_block = audio_queue.get(timeout=1)
        except queue.Empty:
            continue
        mono_audio = audio_block.mean(axis=1)
        segments, _ = model.transcribe(mono_audio, language="en", beam_size=5)
        for segment in segments:
            text = segment.text.strip()
            if not text:
                continue
            print(f"\n🗣️  Transcribed: {text}")
            try:
                sentiment = sentiment_analyzer(text)[0]
                label = sentiment["label"]
                score = sentiment["score"]
                print(f"🧠  Sentiment: {label} (Confidence: {score:.2f})")
            except Exception as e:
                print("Sentiment analysis error:", str(e))

# Background thread for transcription
def start_transcription():
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="float32",
                        callback=audio_callback, blocksize=int(SAMPLE_RATE * BLOCK_DURATION)):
        transcription_loop()

# Run transcription in a thread
thread = threading.Thread(target=start_transcription)
thread.start()

# Wait for user to press Enter to stop
input("\nPress Enter to stop recording and save audio...\n")
stop_event.set()
thread.join()

# Save recorded audio
if audio_buffer:
    all_audio = np.concatenate(audio_buffer, axis=0)
    sf.write("recorded_audio.wav", all_audio, SAMPLE_RATE)
    print("✅ Audio saved as 'recorded_audio.wav'")
else:
    print("❌ No audio recorded.")

