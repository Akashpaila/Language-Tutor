# from flask import Flask, render_template, request, jsonify
# import os
# import random
# import speech_recognition as sr
# import librosa
# import jiwer

# app = Flask(__name__, template_folder="templates")
# @app.route('/')
# def index():
#     return render_template("index.html")
# TEXT_FOLDER = r"D:/B-Tech/Last Sem/Major/New Dataset/Processed_Text"
# AUDIO_FOLDER = r"D:/B-Tech/Last Sem/Major/New Dataset/Processed_Audio"

# def generate_text(word_count):
#     text_files = os.listdir(TEXT_FOLDER)
#     random.shuffle(text_files) 

#     combined_text = ""
#     selected_files = []

#     for file in text_files:
#         with open(os.path.join(TEXT_FOLDER, file), "r", encoding="utf-8") as f:
#             content = f.read().strip()
#             words = content.split()
            
#             if len(combined_text.split()) + len(words) <= word_count:
#                 combined_text += " " + content
#                 selected_files.append(file)
            
#             if len(combined_text.split()) >= word_count:
#                 break

#     return combined_text.strip()

# @app.route("/generate_text", methods=["POST"])
# def get_text():
#     data = request.get_json()
#     word_count = data.get("word_count", 10)  
#     generated_text = generate_text(word_count)
#     return jsonify({"text": generated_text})
# @app.route("/analyze_audio", methods=["POST"])
# def analyze_audio():
#     if "audio" not in request.files:
#         return jsonify({"error": "No audio file uploaded"}), 400

#     audio_file = request.files["audio"]
#     audio_path = os.path.join("temp.wav")  
#     audio_file.save(audio_path)

#     # Speech Recognition
#     recognizer = sr.Recognizer()
#     with sr.AudioFile(audio_path) as source:
#         audio_data = recognizer.record(source)

#     try:
#         recognized_text = recognizer.recognize_google(audio_data)
#     except sr.UnknownValueError:
#         return jsonify({"error": "Could not recognize speech."}), 400

#     expected_text = request.form["expected_text"]

#     wer = jiwer.wer(expected_text, recognized_text)
    
#     expected_words = expected_text.split()
#     recognized_words = recognized_text.split()
#     mispronounced_words = [word for word in expected_words if word not in recognized_words]

#     y, sample_rate = librosa.load(audio_path, sr=None)
#     duration = librosa.get_duration(y=y, sr=sample_rate)  # Use new variable

#     wps = len(recognized_words) / duration if duration > 0 else 0

#     return jsonify({
#         "recognized_text": recognized_text,
#         "wer": round(wer, 2),
#         "mispronounced_words": mispronounced_words,
#         "wps": round(wps, 2)
#     })

# if __name__ == "__main__":
#     app.run(debug=True)