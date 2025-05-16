import os
import speech_recognition as sr
import librosa
import jiwer
import soundfile as sf
from pydub import AudioSegment
import inflect
import difflib
import re
import vosk
import json
from vosk import Model, KaldiRecognizer
import whisper
import sounddevice as sd
import numpy as np
import threading
import sys

# Initialize inflect engine
p = inflect.engine()

# Paths (same as app.py)
VOSK_MODEL_PATH = r"D:\B-Tech\Last Sem\Major\Pronunciation Analysis Flaws Rectification\Model\vosk_model"

# Post-processing functions from app.py
def convert_numbers_to_words(text):
    words = text.split()
    new_text = []
    for word in words:
        if word.isdigit():
            new_text.append(p.number_to_words(word))
        else:
            new_text.append(word)
    return " ".join(new_text)

def preprocess_text(text):
    text = text.replace("-", " ")
    text = re.sub(r"[^\w\s':-]", "", text)
    text = expand_abbreviations(text)
    return text

def expand_abbreviations(text):
    abbreviation_map = {
        "mr": "mister",
        "mrs": "misses",
        "dr": "doctor",
        "sr": "senior",
        "jr": "junior"
    }
    words = text.lower().split()
    expanded = [abbreviation_map.get(word, word) for word in words]
    return " ".join(expanded)

def merge_split_words(expected_words, recognized_words):
    merged_recognized = []
    i = 0
    while i < len(recognized_words):
        if i < len(recognized_words) - 1:
            combined_word = recognized_words[i] + recognized_words[i + 1]
            best_match = difflib.get_close_matches(combined_word, expected_words, n=1, cutoff=0.8)
            if best_match:
                merged_recognized.append(best_match[0])
                i += 2
                continue
        merged_recognized.append(recognized_words[i])
        i += 1
    return merged_recognized

# Transcription functions from app.py
def recognize_speech_vosk(audio_path):
    if not os.path.exists(VOSK_MODEL_PATH):
        return "Vosk model not found"
    vosk.SetLogLevel(-1)
    model = vosk.Model(VOSK_MODEL_PATH)
    with sf.SoundFile(audio_path) as audio_file:
        audio_data = audio_file.read(dtype="int16")
        sample_rate = audio_file.samplerate
    rec = vosk.KaldiRecognizer(model, sample_rate)
    rec.AcceptWaveform(audio_data.tobytes())
    result = json.loads(rec.FinalResult())
    return result.get("text", "").lower().strip()

def recognize_speech_whisper(audio_path):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result["text"].lower().strip()

# Audio conversion function from app.py
def convert_audio_to_wav(input_path, output_path):
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_frame_rate(16000).set_channels(1)
    audio.export(output_path, format="wav")

# Recording function
def record_audio(output_path, sample_rate=16000):
    print("Recording... Press Enter to stop.")
    recording = []
    stop_event = threading.Event()

    def callback(indata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        recording.append(indata.copy())

    # Start recording in a separate thread
    with sd.InputStream(samplerate=sample_rate, channels=1, callback=callback):
        input_thread = threading.Thread(target=lambda: input() or stop_event.set())
        input_thread.start()
        stop_event.wait()
        input_thread.join()

    # Save recording
    audio_data = np.concatenate(recording, axis=0)
    sf.write(output_path, audio_data, sample_rate)
    print("Recording stopped.")

# Main analysis function
def analyze_audio(audio_path, expected_text):
    original_audio_path = audio_path
    converted_audio_path = "temp.wav"

    try:
        convert_audio_to_wav(original_audio_path, converted_audio_path)

        recognizer = sr.Recognizer()
        with sr.AudioFile(converted_audio_path) as source:
            audio_data = recognizer.record(source)

        google_raw = recognizer.recognize_google(audio_data).lower().strip()
        google_custom = preprocess_text(convert_numbers_to_words(google_raw))

        vosk_raw = recognize_speech_vosk(converted_audio_path)
        vosk_custom = preprocess_text(convert_numbers_to_words(vosk_raw))

        whisper_raw = recognize_speech_whisper(converted_audio_path)
        whisper_custom = preprocess_text(convert_numbers_to_words(whisper_raw))

        y, sample_rate = librosa.load(converted_audio_path, sr=16000)
        duration = librosa.get_duration(y=y, sr=sample_rate)

        def compute_wps(text): return len(text.split()) / duration if duration > 0 else 0

        google_raw_wps = compute_wps(google_raw)
        google_custom_wps = compute_wps(google_custom)
        vosk_raw_wps = compute_wps(vosk_raw)
        vosk_custom_wps = compute_wps(vosk_custom)
        whisper_raw_wps = compute_wps(whisper_raw)
        whisper_custom_wps = compute_wps(whisper_custom)

        expected_words = expected_text.strip().lower().split()
        google_raw_words = google_raw.split()
        google_custom_words = google_custom.split()
        vosk_raw_words = vosk_raw.split()
        vosk_custom_words = vosk_custom.split()
        whisper_raw_words = whisper_raw.split()
        whisper_custom_words = whisper_custom.split()

        google_merged = merge_split_words(expected_words, google_custom_words)
        vosk_merged = merge_split_words(expected_words, vosk_custom_words)
        whisper_merged = merge_split_words(expected_words, whisper_custom_words)

        def wer(a, b): return jiwer.wer(" ".join(a), " ".join(b))
        def mispronounced(a, b): return [word for word in a if word not in b]

        def get_pace(wps):
            if wps < 1.3:
                return "Slow"
            elif wps < 2.25:
                return "Medium Pace"
            else:
                return "Fast Paced"

        results = {
            "google_raw": {
                "recognized_text": " ".join(google_raw_words),
                "wer": round(wer(expected_words, google_raw_words), 2),
                "mispronounced_words": mispronounced(expected_words, google_raw_words),
                "wps": round(google_raw_wps, 2),
                "pace": get_pace(google_raw_wps)
            },
            "google_custom": {
                "recognized_text": " ".join(google_merged),
                "wer": round(wer(expected_words, google_merged), 2),
                "mispronounced_words": mispronounced(expected_words, google_merged),
                "wps": round(google_custom_wps, 2),
                "pace": get_pace(google_custom_wps)
            },
            "vosk_raw": {
                "recognized_text": " ".join(vosk_raw_words),
                "wer": round(wer(expected_words, vosk_raw_words), 2),
                "mispronounced_words": mispronounced(expected_words, vosk_raw_words),
                "wps": round(vosk_raw_wps, 2),
                "pace": get_pace(vosk_raw_wps)
            },
            "vosk_custom": {
                "recognized_text": " ".join(vosk_merged),
                "wer": round(wer(expected_words, vosk_merged), 2),
                "mispronounced_words": mispronounced(expected_words, vosk_merged),
                "wps": round(vosk_custom_wps, 2),
                "pace": get_pace(vosk_custom_wps)
            },
            "whisper_raw": {
                "recognized_text": " ".join(whisper_raw_words),
                "wer": round(wer(expected_words, whisper_raw_words), 2),
                "mispronounced_words": mispronounced(expected_words, whisper_raw_words),
                "wps": round(whisper_raw_wps, 2),
                "pace": get_pace(whisper_raw_wps)
            },
            "whisper_custom": {
                "recognized_text": " ".join(whisper_merged),
                "wer": round(wer(expected_words, whisper_merged), 2),
                "mispronounced_words": mispronounced(expected_words, whisper_merged),
                "wps": round(whisper_custom_wps, 2),
                "pace": get_pace(whisper_custom_wps)
            }
        }

        return results

    except sr.UnknownValueError:
        print("Error: Could not transcribe audio.")
        return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None
    finally:
        if os.path.exists(original_audio_path):
            os.remove(original_audio_path)
        if os.path.exists(converted_audio_path):
            os.remove(converted_audio_path)

# Pretty-print results
def print_results(results):
    if not results:
        return
    for model, result in results.items():
        print(f"\nResults for {model.replace('_', ' ').upper()}:")
        print(f"  Recognized Text: {result['recognized_text']}")
        print(f"  Word Error Rate (WER): {result['wer']}")
        print(f"  Mispronounced Words: {', '.join(result['mispronounced_words']) if result['mispronounced_words'] else 'None'}")
        print(f"  Words Per Second (WPS): {result['wps']}")
        print(f"  Pace: {result['pace']}")

# Main execution
if __name__ == "__main__":
    # Prompt for custom text
    print("Enter the text you will speak:")
    expected_text = input().strip()
    if not expected_text:
        print("Error: No text provided.")
        sys.exit(1)

    # Record audio
    audio_path = "temp_input.wav"
    record_audio(audio_path)

    # Analyze audio
    results = analyze_audio(audio_path, expected_text)

    # Print results
    print_results(results)