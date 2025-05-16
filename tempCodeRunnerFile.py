from flask import Flask, render_template, request, jsonify
import os
import random
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
import language_tool_python
from textblob import TextBlob

app = Flask(__name__, template_folder="templates")

TEXT_FOLDER = r"D:/B-Tech/Last Sem/Major/New Dataset/Processed_Text"
AUDIO_FOLDER = r"D:/B-Tech/Last Sem/Major/New Dataset/Processed_Audio"

p = inflect.engine()

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

@app.route('/')
def index():
    return render_template("home.html")

@app.route('/index')
def index_page():
    return render_template("index.html")

@app.route('/own_text')
def own_text():
    return render_template('own_text.html')

@app.route('/text_to_speech')
def text_to_speech():
    return render_template('text_to_speech.html')

@app.route('/speech_to_text')
def speech_to_text():
    return render_template('speech_to_text.html')

@app.route('/grammar_analysis')
def grammar_analysis():
    return render_template('grammar_analysis.html')

def generate_text(word_count):
    text_files = os.listdir(TEXT_FOLDER)
    random.shuffle(text_files)
    combined_text = ""
    for file in text_files:
        with open(os.path.join(TEXT_FOLDER, file), "r", encoding="utf-8") as f:
            content = f.read().strip()
            words = content.split()
            if len(combined_text.split()) + len(words) <= word_count:
                combined_text += " " + content
            if len(combined_text.split()) >= word_count:
                break
    return combined_text.strip()

@app.route("/generate_text", methods=["POST"])
def get_text():
    data = request.get_json()
    word_count = data.get("word_count", 10)
    generated_text = generate_text(word_count)
    return jsonify({"text": generated_text})

def convert_audio_to_wav(input_path, output_path):
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_frame_rate(16000).set_channels(1)
    audio.export(output_path, format="wav")

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

def recognize_speech_vosk(audio_path):
    model_path = r"D:\B-Tech\Last Sem\Major\Pronunciation Analysis Flaws Rectification\Model\vosk_model"
    if not os.path.exists(model_path):
        return "Vosk model not found"
    vosk.SetLogLevel(-1)
    model = vosk.Model(model_path)
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

@app.route('/check_grammar', methods=['POST'])
def check_grammar():
    data = request.get_json()
    text = data.get("text", "")
    tool = language_tool_python.LanguageTool('en-US')
    matches = tool.check(text)
    corrected_text = tool.correct(text)

    suggestions = [{
        "rule": match.ruleId,
        "message": match.message,
        "replacements": match.replacements
    } for match in matches]

    return jsonify({
        "matches": suggestions,
        "corrected": str(TextBlob(corrected_text).correct())
    })

@app.route("/analyze_audio", methods=["POST"])
def analyze_audio():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file uploaded"}), 400

    audio_file = request.files["audio"]
    original_audio_path = "temp_input.webm"
    converted_audio_path = "temp.wav"

    audio_file.save(original_audio_path)

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

    except sr.UnknownValueError:
        google_raw = google_custom = vosk_raw = vosk_custom = whisper_raw = whisper_custom = ""
        google_raw_wps = google_custom_wps = vosk_raw_wps = vosk_custom_wps = whisper_raw_wps = whisper_custom_wps = 0
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(original_audio_path): os.remove(original_audio_path)
        if os.path.exists(converted_audio_path): os.remove(converted_audio_path)

    expected_text = request.form.get("expected_text", "").strip().lower()
    if not expected_text:
        return jsonify({"error": "Expected text is missing"}), 400

    expected_words = expected_text.split()
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

    return jsonify({
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
    })

if __name__ == "__main__":
    app.run(debug=True)
