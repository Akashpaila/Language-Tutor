# import os
# import random
# import json
# import sqlite3
# import numpy as np
# from datetime import datetime
# from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
# from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
# from werkzeug.security import generate_password_hash, check_password_hash
# from python_speech_features import mfcc
# import librosa
# from scipy.spatial.distance import cosine
# from pydub import AudioSegment
# import speech_recognition as sr
# import jiwer
# import soundfile as sf
# import inflect
# import difflib
# import re
# import vosk
# from vosk import Model, KaldiRecognizer
# import whisper
# import language_tool_python
# from textblob import TextBlob
# import yt_dlp
# import tempfile
# import logging
# import nltk
# from deep_translator import GoogleTranslator
# from transformers import pipeline
# nltk.download('punkt')
# nltk.download('punkt_tab')

# app = Flask(__name__, template_folder="templates")
# app.secret_key = os.urandom(24).hex()  # Secure random key

# # Configure logging
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)

# # Flask-Login setup
# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = 'login'

# # SQLite database setup
# DATABASE = 'users.db'

# def init_db():
#     with sqlite3.connect(DATABASE) as conn:
#         c = conn.cursor()
#         # Create users table if it doesn't exist
#         c.execute('''CREATE TABLE IF NOT EXISTS users (
#             name TEXT NOT NULL,
#             email TEXT UNIQUE NOT NULL,
#             mobile TEXT NOT NULL
#         )''')
#         # Check existing columns
#         c.execute("PRAGMA table_info(users)")
#         columns = [col[1] for col in c.fetchall()]
#         # Add id column if missing
#         if 'id' not in columns:
#             c.execute("ALTER TABLE users ADD COLUMN id INTEGER")
#             # Populate id with unique values
#             c.execute("SELECT rowid, * FROM users")
#             rows = c.fetchall()
#             for i, row in enumerate(rows, 1):
#                 c.execute("UPDATE users SET id = ? WHERE rowid = ?", (i, row[0]))
#             # Make id primary key (requires creating a new table)
#             c.execute('''CREATE TABLE users_new (
#                 id INTEGER PRIMARY KEY,
#                 name TEXT NOT NULL,
#                 email TEXT UNIQUE NOT NULL,
#                 mobile TEXT NOT NULL,
#                 mfcc_features TEXT
#             )''')
#             c.execute('''INSERT INTO users_new (id, name, email, mobile, mfcc_features)
#                         SELECT id, name, email, mobile, mfcc_features FROM users''')
#             c.execute("DROP TABLE users")
#             c.execute("ALTER TABLE users_new RENAME TO users")
#         # Add mfcc_features column if missing
#         if 'mfcc_features' not in columns:
#             c.execute("ALTER TABLE users ADD COLUMN mfcc_features TEXT")
#         # Create user_history table
#         c.execute('''CREATE TABLE IF NOT EXISTS user_history (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             user_id INTEGER,
#             feature TEXT,
#             timestamp TEXT,
#             details TEXT,
#             FOREIGN KEY (user_id) REFERENCES users(id)
#         )''')
#         conn.commit()

# init_db()

# # User class for Flask-Login
# class User(UserMixin):
#     def __init__(self, id, name, email, mobile, mfcc_features):
#         self.id = id
#         self.name = name
#         self.email = email
#         self.mobile = mobile
#         self.mfcc_features = mfcc_features

# @login_manager.user_loader
# def load_user(user_id):
#     with sqlite3.connect(DATABASE) as conn:
#         c = conn.cursor()
#         c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
#         user = c.fetchone()
#         if user:
#             return User(user[0], user[1], user[2], user[3], user[4])
#         return None

# TEXT_FOLDER = r"D:/B-Tech/Last Sem/Major/New Dataset/Processed_Text"
# AUDIO_FOLDER = r"D:/B-Tech/Last Sem/Major/New Dataset/Processed_Audio"

# p = inflect.engine()

# # Initialize summarization pipeline
# summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# def convert_numbers_to_words(text):
#     words = text.split()
#     new_text = []
#     for word in words:
#         if word.isdigit():
#             new_text.append(p.number_to_words(word))
#         else:
#             new_text.append(word)
#     return " ".join(new_text)

# def preprocess_text(text, expand_abbrevs=True):
#     text = re.sub(r"[^\w\s':-]", "", text)
#     if expand_abbrevs:
#         text = expand_abbreviations(text)
#     return text

# def expand_abbreviations(text):
#     abbreviation_map = {
#         "mr": "mister",
#         "mrs": "misses",
#         "dr": "doctor",
#         "sr": "senior",
#         "jr": "junior"
#     }
#     words = text.lower().split()
#     expanded = [abbreviation_map.get(word, word) for word in words]
#     return " ".join(expanded)

# def extract_mfcc(audio_path):
#     y, sr = librosa.load(audio_path, sr=16000)
#     y = librosa.util.normalize(y)  # Normalize audio
#     mfcc_features = mfcc(y, sr, nfft=1200)
#     return mfcc_features.mean(axis=0).tolist()

# def verify_speaker(stored_mfcc, new_audio_path):
#     new_mfcc = extract_mfcc(new_audio_path)
#     stored_mfcc = json.loads(stored_mfcc)
#     similarity = 1 - cosine(stored_mfcc, new_mfcc)
#     print(f"Similarity: {similarity}")  # Debug
#     return similarity > 0.65  # Lowered threshold

# @app.route('/')
# def landing():
#     return render_template("landing.html")

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         name = request.form.get('name')
#         email = request.form.get('email')
#         mobile = request.form.get('mobile')
#         audio_file = request.files.get('audio')

#         if not all([name, email, mobile, audio_file]):
#             flash('All fields are required!')
#             return redirect(url_for('register'))

#         audio_path = 'temp_register.wav'
#         audio_file.save(audio_path)
        
#         try:
#             mfcc_features = extract_mfcc(audio_path)
#             with sqlite3.connect(DATABASE) as conn:
#                 c = conn.cursor()
#                 c.execute("INSERT INTO users (name, email, mobile, mfcc_features) VALUES (?, ?, ?, ?)",
#                          (name, email, mobile, json.dumps(mfcc_features)))
#                 conn.commit()
#             os.remove(audio_path)
#             flash('Registration successful! Please log in.')
#             return redirect(url_for('login'))
#         except sqlite3.IntegrityError:
#             flash('Email already registered!')
#             return redirect(url_for('register'))
#         except Exception as e:
#             flash(f'Error: {str(e)}')
#             return redirect(url_for('register'))
#     return render_template('register.html', random_text=generate_text(10))

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         name = request.form.get('name')
#         email = request.form.get('email')
#         audio_file = request.files.get('audio')

#         if not all([name, email, audio_file]):
#             flash('All fields are required!')
#             return redirect(url_for('login'))

#         audio_path = 'temp_login.wav'
#         audio_file.save(audio_path)

#         with sqlite3.connect(DATABASE) as conn:
#             c = conn.cursor()
#             c.execute("SELECT * FROM users WHERE email = ? AND name = ?", (email, name))
#             user = c.fetchone()

#         if not user:
#             flash('Invalid name or email!')
#             os.remove(audio_path)
#             return redirect(url_for('login'))
#         if user[4] is None:
#             flash('Please update your voice profile.')
#             os.remove(audio_path)
#             return redirect(url_for('update_profile'))
#         if verify_speaker(user[4], audio_path):
#             user_obj = User(user[0], user[1], user[2], user[3], user[4])
#             login_user(user_obj)
#             os.remove(audio_path)
#             return redirect(url_for('index'))
#         else:
#             flash('Voice verification failed!')
#             os.remove(audio_path)
#             return redirect(url_for('login'))
#     return render_template('login.html', random_text=generate_text(10))

# @app.route('/update_profile', methods=['GET', 'POST'])
# @login_required
# def update_profile():
#     if request.method == 'POST':
#         audio_file = request.files.get('audio')
#         if not audio_file:
#             flash('Audio file is required!')
#             return redirect(url_for('update_profile'))

#         audio_path = 'temp_update.wav'
#         audio_file.save(audio_path)

#         try:
#             mfcc_features = extract_mfcc(audio_path)
#             with sqlite3.connect(DATABASE) as conn:
#                 c = conn.cursor()
#                 c.execute("UPDATE users SET mfcc_features = ? WHERE id = ?",
#                          (json.dumps(mfcc_features), current_user.id))
#                 conn.commit()
#             os.remove(audio_path)
#             flash('Voice profile updated successfully!')
#             return redirect(url_for('index'))
#         except Exception as e:
#             flash(f'Error: {str(e)}')
#             os.remove(audio_path)
#             return redirect(url_for('update_profile'))
#     return render_template('update_profile.html', random_text=generate_text(10))

# @app.route('/logout')
# @login_required
# def logout():
#     logout_user()
#     return redirect(url_for('landing'))

# @app.route('/index')
# @login_required
# def index():
#     return render_template("home.html")

# @app.route('/dashboard')
# @login_required
# def dashboard():
#     return render_template("dashboard.html")

# @app.route('/own_text')
# @login_required
# def own_text():
#     return render_template('index.html')

# @app.route('/text_to_speech')
# @login_required
# def text_to_speech():
#     return render_template('text_to_speech.html')

# @app.route('/speech_to_text')
# @login_required
# def speech_to_text():
#     return render_template('speech_to_text.html')

# @app.route('/grammar_analysis')
# @login_required
# def grammar_analysis():
#     return render_template('grammar_analysis.html')

# @app.route('/youtube_transcription')
# @login_required
# def youtube_transcription():
#     return render_template('yt.html')

# @app.route('/conversation_module')
# @login_required
# def conversation_module():
#     return render_template('conversation_module.html')

# @app.route('/accent_learning')
# @login_required
# def accent_learning():
#     return render_template('accent_learning.html')

# @app.route('/history_pronunciation')
# @login_required
# def history_pronunciation():
#     return render_template('history_pronunciation.html')

# @app.route('/history_grammar')
# @login_required
# def history_grammar():
#     return render_template('history_grammar.html')

# @app.route('/history_youtube')
# @login_required
# def history_youtube():
#     return render_template('history_youtube.html')

# @app.route('/history_speech_to_text')
# @login_required
# def history_speech_to_text():
#     return render_template('history_speech_to_text.html')

# @app.route('/history_text_to_speech')
# @login_required
# def history_text_to_speech():
#     return render_template('history_text_to_speech.html')

# @app.route('/history_conversation')
# @login_required
# def history_conversation():
#     return render_template('history_conversation.html')

# @app.route('/history_accent')
# @login_required
# def history_accent():
#     return render_template('history_accent.html')

# def generate_text(word_count):
#     text_files = os.listdir(TEXT_FOLDER)
#     random.shuffle(text_files)
#     combined_text = ""
#     for file in text_files:
#         with open(os.path.join(TEXT_FOLDER, file), "r", encoding="utf-8") as f:
#             content = f.read().strip()
#             words = content.split()
#             if len(combined_text.split()) + len(words) <= word_count:
#                 combined_text += " " + content
#             if len(combined_text.split()) >= word_count:
#                 break
#     return combined_text.strip()

# @app.route("/generate_text", methods=["POST"])
# @login_required
# def get_text():
#     data = request.get_json()
#     word_count = data.get("word_count", 10)
#     generated_text = generate_text(word_count)
#     return jsonify({"text": generated_text})

# def convert_audio_to_wav(input_path, output_path):
#     audio = AudioSegment.from_file(input_path)
#     audio = audio.set_frame_rate(16000).set_channels(1)
#     audio = audio + 20
#     audio.export(output_path, format="wav")

# def merge_split_words(expected_words, recognized_words):
#     merged_recognized = []
#     i = 0
#     while i < len(recognized_words):
#         if i < len(recognized_words) - 1:
#             combined_word = recognized_words[i] + recognized_words[i + 1]
#             best_match = difflib.get_close_matches(combined_word, expected_words, n=1, cutoff=0.6)
#             if best_match:
#                 merged_recognized.append(best_match[0])
#                 i += 2
#                 continue
#         if recognized_words[i] in expected_words:
#             merged_recognized.append(recognized_words[i])
#         else:
#             best_match = difflib.get_close_matches(recognized_words[i], expected_words, n=1, cutoff=0.6)
#             merged_recognized.append(best_match[0] if best_match else recognized_words[i])
#         i += 1
#     return merged_recognized

# def recognize_speech_vosk(audio_path):
#     model_path = r"D:\B-Tech\Last Sem\Major\Pronunciation Analysis Flaws Rectification\Model\vosk_model"
#     if not os.path.exists(model_path):
#         return "Vosk model not found"
#     vosk.SetLogLevel(-1)
#     model = vosk.Model(model_path)
#     with sf.SoundFile(audio_path) as audio_file:
#         audio_data = audio_file.read(dtype="int16")
#         sample_rate = audio_file.samplerate
#     rec = vosk.KaldiRecognizer(model, sample_rate)
#     rec.AcceptWaveform(audio_data.tobytes())
#     result = json.loads(rec.FinalResult())
#     return result.get("text", "").lower().strip()

# def recognize_speech_whisper(audio_path):
#     model = whisper.load_model("base")
#     result = model.transcribe(audio_path)
#     return result["text"].lower().strip()

# @app.route('/check_grammar', methods=['POST'])
# @login_required
# def check_grammar():
#     data = request.get_json()
#     text = data.get("text", "")
#     tool = language_tool_python.LanguageTool('en-US')
#     matches = tool.check(text)
#     corrected_text = tool.correct(text)
#     suggestions = [{
#         "rule": match.ruleId,
#         "message": match.message,
#         "replacements": match.replacements
#     } for match in matches]
#     # Store history
#     with sqlite3.connect(DATABASE) as conn:
#         c = conn.cursor()
#         c.execute("INSERT INTO user_history (user_id, feature, timestamp, details) VALUES (?, ?, ?, ?)",
#                   (current_user.id, 'grammar', datetime.now().isoformat(),
#                    json.dumps({'text': text, 'corrections': ', '.join([m['message'] for m in suggestions])})))
#         conn.commit()
#     return jsonify({
#         "matches": suggestions,
#         "corrected": str(TextBlob(corrected_text).correct())
#     })

# def cer(expected_words, recognized_words):
#     expected_text = " ".join(expected_words)
#     recognized_text = " ".join(recognized_words)
#     expected_chars = " ".join(list(expected_text))
#     recognized_chars = " ".join(list(recognized_text))
#     cer_value = jiwer.wer(expected_chars, recognized_chars)
#     if len(expected_text) == 0:
#         return 0.0 if len(recognized_text) == 0 else 1.0
#     return cer_value

# @app.route("/analyze_audio", methods=["POST"])
# @login_required
# def analyze_audio():
#     if "audio" not in request.files:
#         return jsonify({"error": "No audio file uploaded"}), 400

#     audio_file = request.files["audio"]
#     original_audio_path = "temp_input.webm"
#     converted_audio_path = "temp.wav"

#     audio_file.save(original_audio_path)

#     try:
#         convert_audio_to_wav(original_audio_path, converted_audio_path)

#         recognizer = sr.Recognizer()
#         with sr.AudioFile(converted_audio_path) as source:
#             audio_data = recognizer.record(source)

#         google_raw = recognizer.recognize_google(audio_data).lower().strip()
#         vosk_raw = recognize_speech_vosk(converted_audio_path)
#         whisper_raw = recognize_speech_whisper(converted_audio_path)

#         expected_text = request.form.get("expected_text", "").strip().lower()
#         if not expected_text:
#             return jsonify({"error": "Expected text is missing"}), 400

#         has_numbers = bool(re.search(r'\d+', expected_text))
#         honorifics = {"mr", "mrs", "dr", "sr", "jr"}
#         has_honorifics = any(word in honorifics for word in expected_text.split())

#         if has_numbers:
#             google_custom = preprocess_text(google_raw, expand_abbrevs=not has_honorifics)
#             vosk_custom = preprocess_text(vosk_raw, expand_abbrevs=not has_honorifics)
#             whisper_custom = preprocess_text(whisper_raw, expand_abbrevs=not has_honorifics)
#         else:
#             google_custom = preprocess_text(convert_numbers_to_words(google_raw), expand_abbrevs=not has_honorifics)
#             vosk_custom = preprocess_text(convert_numbers_to_words(vosk_raw), expand_abbrevs=not has_honorifics)
#             whisper_custom = preprocess_text(convert_numbers_to_words(whisper_raw), expand_abbrevs=not has_honorifics)

#         y, sample_rate = librosa.load(converted_audio_path, sr=16000)
#         duration = librosa.get_duration(y=y, sr=sample_rate)

#         def compute_wps(text): return len(text.split()) / duration if duration > 0 else 0

#         google_raw_wps = compute_wps(google_raw)
#         google_custom_wps = compute_wps(google_custom)
#         vosk_raw_wps = compute_wps(vosk_raw)
#         vosk_custom_wps = compute_wps(vosk_custom)
#         whisper_raw_wps = compute_wps(whisper_raw)
#         whisper_custom_wps = compute_wps(whisper_custom)

#         expected_words = expected_text.split()
#         google_raw_words = google_raw.split()
#         google_custom_words = google_custom.split()
#         vosk_raw_words = vosk_raw.split()
#         vosk_custom_words = vosk_custom.split()
#         whisper_raw_words = whisper_raw.split()
#         whisper_custom_words = whisper_custom.split()

#         google_merged = merge_split_words(expected_words, google_custom_words)
#         vosk_merged = merge_split_words(expected_words, vosk_custom_words)
#         whisper_merged = merge_split_words(expected_words, whisper_custom_words)

#         def wer(a, b): return jiwer.wer(" ".join(a), " ".join(b))
#         def mispronounced(a, b): return [word for word in a if word not in b]

#         def get_pace(wps):
#             if wps < 1.3:
#                 return "Slow"
#             elif wps < 2.25:
#                 return "Medium Pace"
#             else:
#                 return "Fast Paced"

#         result = {
#             "google_raw": {
#                 "recognized_text": " ".join(google_raw_words),
#                 "wer": round(wer(expected_words, google_raw_words), 2),
#                 "cer": round(cer(expected_words, google_raw_words), 2),
#                 "mispronounced_words": mispronounced(expected_words, google_raw_words),
#                 "wps": round(google_raw_wps, 2),
#                 "pace": get_pace(google_raw_wps)
#             },
#             "google_custom": {
#                 "recognized_text": " ".join(google_merged),
#                 "wer": round(wer(expected_words, google_merged), 2),
#                 "cer": round(cer(expected_words, google_merged), 2),
#                 "mispronounced_words": mispronounced(expected_words, google_merged),
#                 "wps": round(google_custom_wps, 2),
#                 "pace": get_pace(google_custom_wps)
#             },
#             "vosk_raw": {
#                 "recognized_text": " ".join(vosk_raw_words),
#                 "wer": round(wer(expected_words, vosk_raw_words), 2),
#                 "cer": round(cer(expected_words, vosk_raw_words), 2),
#                 "mispronounced_words": mispronounced(expected_words, vosk_raw_words),
#                 "wps": round(vosk_raw_wps, 2),
#                 "pace": get_pace(vosk_raw_wps)
#             },
#             "vosk_custom": {
#                 "recognized_text": " ".join(vosk_merged),
#                 "wer": round(wer(expected_words, vosk_merged), 2),
#                 "cer": round(cer(expected_words, vosk_merged), 2),
#                 "mispronounced_words": mispronounced(expected_words, vosk_merged),
#                 "wps": round(vosk_custom_wps, 2),
#                 "pace": get_pace(vosk_custom_wps)
#             },
#             "whisper_raw": {
#                 "recognized_text": " ".join(whisper_raw_words),
#                 "wer": round(wer(expected_words, whisper_raw_words), 2),
#                 "cer": round(cer(expected_words, whisper_raw_words), 2),
#                 "mispronounced_words": mispronounced(expected_words, whisper_raw_words),
#                 "wps": round(whisper_raw_wps, 2),
#                 "pace": get_pace(whisper_raw_wps)
#             },
#             "whisper_custom": {
#                 "recognized_text": " ".join(whisper_merged),
#                 "wer": round(wer(expected_words, whisper_merged), 2),
#                 "cer": round(cer(expected_words, whisper_merged), 2),
#                 "mispronounced_words": mispronounced(expected_words, whisper_merged),
#                 "wps": round(whisper_custom_wps, 2),
#                 "pace": get_pace(whisper_custom_wps)
#             }
#         }
#         # Store history
#         with sqlite3.connect(DATABASE) as conn:
#             c = conn.cursor()
#             c.execute("INSERT INTO user_history (user_id, feature, timestamp, details) VALUES (?, ?, ?, ?)",
#                       (current_user.id, 'pronunciation', datetime.now().isoformat(),
#                        json.dumps({'sentence': expected_text, 'wer': result['google_custom']['wer'], 'wps': result['google_custom']['wps'], 'cer': result['google_custom']['cer']})))
#             conn.commit()
#         return jsonify(result)

#     except sr.UnknownValueError:
#         google_raw = google_custom = vosk_raw = vosk_custom = whisper_raw = whisper_custom = ""
#         google_raw_wps = google_custom_wps = vosk_raw_wps = vosk_custom_wps = whisper_raw_wps = whisper_custom_wps = 0
#     except Exception as e:
#         print(f"Error: {str(e)}")
#         return jsonify({"error": str(e)}), 500
#     finally:
#         if os.path.exists(original_audio_path): os.remove(original_audio_path)
#         if os.path.exists(converted_audio_path): os.remove(converted_audio_path)

# @app.route('/transcribe_youtube', methods=['POST'])
# @login_required
# def transcribe_youtube():
#     logger.debug("Received request for /transcribe_youtube")
#     data = request.get_json()
#     youtube_url = data.get('url', '')
    
#     if not youtube_url:
#         logger.error("No URL provided")
#         return jsonify({'error': 'No URL provided'}), 400

#     try:
#         with tempfile.TemporaryDirectory() as temp_dir:
#             logger.debug(f"Created temporary directory: {temp_dir}")
#             audio_path = os.path.join(temp_dir, 'audio.%(ext)s')
            
#             ydl_opts = {
#                 'format': 'bestaudio/best',
#                 'outtmpl': audio_path,
#                 'postprocessors': [{
#                     'key': 'FFmpegExtractAudio',
#                     'preferredcodec': 'mp3',
#                     'preferredquality': '192',
#                 }],
#                 'quiet': True,
#                 'no_warnings': True,
#             }
            
#             logger.debug(f"Downloading audio from URL: {youtube_url}")
#             with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#                 ydl.download([youtube_url])
            
#             downloaded_audio = os.path.join(temp_dir, 'audio.mp3')
#             if not os.path.exists(downloaded_audio):
#                 logger.error("Downloaded audio file not found")
#                 return jsonify({'error': 'Failed to download audio'}), 500
            
#             logger.debug(f"Downloaded audio file: {downloaded_audio}")
            
#             wav_path = os.path.join(temp_dir, 'audio.wav')
#             logger.debug(f"Converting {downloaded_audio} to WAV: {wav_path}")
#             convert_audio_to_wav(downloaded_audio, wav_path)
            
#             if not os.path.exists(wav_path):
#                 logger.error("WAV file conversion failed")
#                 return jsonify({'error': 'Failed to convert audio to WAV'}), 500
            
#             logger.debug(f"Converted WAV file: {wav_path}")
            
#             logger.debug("Starting Whisper transcription")
#             transcription = recognize_speech_whisper(wav_path)
#             logger.debug("Transcription completed")
            
#             # Store history
#             with sqlite3.connect(DATABASE) as conn:
#                 c = conn.cursor()
#                 c.execute("INSERT INTO user_history (user_id, feature, timestamp, details) VALUES (?, ?, ?, ?)",
#                           (current_user.id, 'youtube', datetime.now().isoformat(),
#                            json.dumps({'url': youtube_url, 'transcription': transcription})))
#                 conn.commit()
            
#             return jsonify({'transcription': transcription})
            
#     except Exception as e:
#         logger.error(f"Error during transcription: {str(e)}")
#         return jsonify({'error': f'Failed to transcribe video: {str(e)}'}), 500

# @app.route('/transcribe_local', methods=['POST'])
# @login_required
# def transcribe_local():
#     logger.debug("Received request for /transcribe_local")
    
#     if 'file' not in request.files:
#         logger.error("No file uploaded")
#         return jsonify({'error': 'No file uploaded'}), 400
    
#     file = request.files['file']
#     if file.filename == '':
#         logger.error("No file selected")
#         return jsonify({'error': 'No file selected'}), 400
    
#     try:
#         with tempfile.TemporaryDirectory() as temp_dir:
#             logger.debug(f"Created temporary directory: {temp_dir}")
#             original_path = os.path.join(temp_dir, file.filename)
#             wav_path = os.path.join(temp_dir, 'audio.wav')
            
#             file.save(original_path)
#             logger.debug(f"Saved uploaded file: {original_path}")
            
#             logger.debug(f"Converting {original_path} to WAV: {wav_path}")
#             convert_audio_to_wav(original_path, wav_path)
            
#             if not os.path.exists(wav_path):
#                 logger.error("WAV file conversion failed")
#                 return jsonify({'error': 'Failed to convert audio to WAV'}), 500
            
#             logger.debug(f"Converted WAV file: {wav_path}")
            
#             logger.debug("Starting Whisper transcription")
#             transcription = recognize_speech_whisper(wav_path)
#             logger.debug("Transcription completed")
            
#             # Store history
#             with sqlite3.connect(DATABASE) as conn:
#                 c = conn.cursor()
#                 c.execute("INSERT INTO user_history (user_id, feature, timestamp, details) VALUES (?, ?, ?, ?)",
#                           (current_user.id, 'speech_to_text', datetime.now().isoformat(),
#                            json.dumps({'transcription': transcription})))
#                 conn.commit()
            
#             return jsonify({'transcription': transcription})
            
#     except Exception as e:
#         logger.error(f"Error during local transcription: {str(e)}")
#         return jsonify({'error': f'Failed to transcribe file: {str(e)}'}), 500

# @app.route('/translate', methods=['POST'])
# @login_required
# def translate():
#     logger.debug("Received request for /translate")
#     data = request.get_json()
#     text = data.get('text', '')
#     target_lang = data.get('target_lang', 'en')
    
#     if not text:
#         logger.error("No text provided")
#         return jsonify({'error': 'No text provided'}), 400

#     try:
#         sentences = nltk.sent_tokenize(text)
#         translations = []
#         translator = GoogleTranslator(source='en', target=target_lang)
#         for sentence in sentences:
#             translated = translator.translate(sentence)
#             translations.append({
#                 'original': sentence,
#                 'translated': translated
#             })
#         # Store history
#         with sqlite3.connect(DATABASE) as conn:
#             c = conn.cursor()
#             c.execute("INSERT INTO user_history (user_id, feature, timestamp, details) VALUES (?, ?, ?, ?)",
#                       (current_user.id, 'text_to_speech', datetime.now().isoformat(),
#                        json.dumps({'text': text, 'target_lang': target_lang})))
#             conn.commit()
#         return jsonify({'translations': translations})
#     except Exception as e:
#         logger.error(f"Error during translation: {str(e)}")
#         return jsonify({'error': f'Failed to translate text: {str(e)}'}), 500

# @app.route('/summarize', methods=['POST'])
# @login_required
# def summarize():
#     logger.debug("Received request for /summarize")
#     data = request.get_json()
#     text = data.get('text', '')
    
#     if not text:
#         logger.error("No text provided")
#         return jsonify({'error': 'No text provided'}), 400

#     try:
#         summary = summarizer(text, max_length=300, min_length=100, do_sample=False)
#         summary_text = summary[0]['summary_text']
#         # Store history
#         with sqlite3.connect(DATABASE) as conn:
#             c = conn.cursor()
#             c.execute("INSERT INTO user_history (user_id, feature, timestamp, details) VALUES (?, ?, ?, ?)",
#                       (current_user.id, 'text_to_speech', datetime.now().isoformat(),
#                        json.dumps({'text': text, 'summary': summary_text})))
#             conn.commit()
#         return jsonify({'summary': summary_text})
#     except Exception as e:
#         logger.error(f"Error during summarization: {str(e)}")
#         return jsonify({'error': f'Failed to summarize text: {str(e)}'}), 500

# @app.route('/get_history', methods=['POST'])
# @login_required
# def get_history():
#     data = request.get_json()
#     feature = data.get('feature', 'all')
#     with sqlite3.connect(DATABASE) as conn:
#         c = conn.cursor()
#         if feature == 'all':
#             c.execute("SELECT id, feature, timestamp, details FROM user_history WHERE user_id = ? ORDER BY timestamp DESC", (current_user.id,))
#         else:
#             c.execute("SELECT id, feature, timestamp, details FROM user_history WHERE user_id = ? AND feature = ? ORDER BY timestamp DESC", (current_user.id, feature))
#         history = [{'id': row[0], 'feature': row[1], 'timestamp': row[2], 'details': json.loads(row[3])} for row in c.fetchall()]
#     return jsonify({'history': history})

# if __name__ == "__main__":
#     app.run(debug=True)

#########################################

# import os
# import random
# import json
# import sqlite3
# import numpy as np
# from datetime import datetime
# from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
# from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
# from werkzeug.security import generate_password_hash, check_password_hash
# from python_speech_features import mfcc
# import librosa
# from scipy.spatial.distance import cosine
# from pydub import AudioSegment
# import speech_recognition as sr
# import jiwer
# import soundfile as sf
# import inflect
# import difflib
# import re
# import vosk
# from vosk import Model, KaldiRecognizer
# import whisper
# import language_tool_python
# from textblob import TextBlob
# import yt_dlp
# import tempfile
# import logging
# import nltk
# from deep_translator import GoogleTranslator
# from transformers import pipeline
# nltk.download('punkt')
# nltk.download('punkt_tab')

# app = Flask(__name__, template_folder="templates")
# app.secret_key = os.urandom(24).hex()  # Secure random key

# # Configure logging
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)

# # Flask-Login setup
# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = 'login'

# # SQLite database setup
# DATABASE = 'users.db'

# def init_db():
#     with sqlite3.connect(DATABASE) as conn:
#         c = conn.cursor()
#         # Create users table if it doesn't exist
#         c.execute('''CREATE TABLE IF NOT EXISTS users (
#             name TEXT NOT NULL,
#             email TEXT UNIQUE NOT NULL,
#             mobile TEXT NOT NULL
#         )''')
#         # Check existing columns
#         c.execute("PRAGMA table_info(users)")
#         columns = [col[1] for col in c.fetchall()]
#         # Add id column if missing
#         if 'id' not in columns:
#             c.execute("ALTER TABLE users ADD COLUMN id INTEGER")
#             # Populate id with unique values
#             c.execute("SELECT rowid, * FROM users")
#             rows = c.fetchall()
#             for i, row in enumerate(rows, 1):
#                 c.execute("UPDATE users SET id = ? WHERE rowid = ?", (i, row[0]))
#             # Make id primary key (requires creating a new table)
#             c.execute('''CREATE TABLE users_new (
#                 id INTEGER PRIMARY KEY,
#                 name TEXT NOT NULL,
#                 email TEXT UNIQUE NOT NULL,
#                 mobile TEXT NOT NULL,
#                 mfcc_features TEXT
#             )''')
#             c.execute('''INSERT INTO users_new (id, name, email, mobile, mfcc_features)
#                         SELECT id, name, email, mobile, mfcc_features FROM users''')
#             c.execute("DROP TABLE users")
#             c.execute("ALTER TABLE users_new RENAME TO users")
#         # Add mfcc_features column if missing
#         if 'mfcc_features' not in columns:
#             c.execute("ALTER TABLE users ADD COLUMN mfcc_features TEXT")
#         # Create user_history table
#         c.execute('''CREATE TABLE IF NOT EXISTS user_history (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             user_id INTEGER,
#             feature TEXT,
#             timestamp TEXT,
#             details TEXT,
#             FOREIGN KEY (user_id) REFERENCES users(id)
#         )''')
#         conn.commit()

# init_db()

# # User class for Flask-Login
# class User(UserMixin):
#     def __init__(self, id, name, email, mobile, mfcc_features):
#         self.id = id
#         self.name = name
#         self.email = email
#         self.mobile = mobile
#         self.mfcc_features = mfcc_features

# @login_manager.user_loader
# def load_user(user_id):
#     with sqlite3.connect(DATABASE) as conn:
#         c = conn.cursor()
#         c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
#         user = c.fetchone()
#         if user:
#             return User(user[0], user[1], user[2], user[3], user[4])
#         return None

# TEXT_FOLDER = r"D:/B-Tech/Last Sem/Major/New Dataset/Processed_Text"
# AUDIO_FOLDER = r"D:/B-Tech/Last Sem/Major/New Dataset/Processed_Audio"

# p = inflect.engine()

# # Initialize summarization pipeline
# summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# def convert_numbers_to_words(text):
#     words = text.split()
#     new_text = []
#     for word in words:
#         if word.isdigit():
#             new_text.append(p.number_to_words(word))
#         else:
#             new_text.append(word)
#     return " ".join(new_text)

# def preprocess_text(text, expand_abbrevs=True):
#     text = re.sub(r"[^\w\s':-]", "", text)
#     if expand_abbrevs:
#         text = expand_abbreviations(text)
#     return text

# def expand_abbreviations(text):
#     abbreviation_map = {
#         "mr": "mister",
#         "mrs": "misses",
#         "dr": "doctor",
#         "sr": "senior",
#         "jr": "junior"
#     }
#     words = text.lower().split()
#     expanded = [abbreviation_map.get(word, word) for word in words]
#     return " ".join(expanded)

# def custom_preprocess_text(text, use_abbrevs=True):
#     # Initialize inflect engine for number-to-word conversion
#     p = inflect.engine()
    
#     # Split text into words
#     words = text.split()
#     processed_words = []
    
#     # Define honorifics mapping (to abbreviate, e.g., "mister" to "mr")
#     honorific_map = {
#         "mister": "mr",
#         "misses": "mrs",
#         "doctor": "dr",
#         "senior": "sr",
#         "junior": "jr"
#     }
    
#     for word in words:
#         word_lower = word.lower()
        
#         # Check for numbers
#         if word.isdigit():
#             processed_words.append(p.number_to_words(word))
#             continue
        
#         # Check for honorifics (if use_abbrevs is True)
#         if use_abbrevs and word_lower in honorific_map.values():
#             processed_words.append(honorific_map[word_lower])
#             continue
        
#         # Preserve all other words, including small words like "a", "the", "an"
#         processed_words.append(word)
    
#     return " ".join(processed_words)

# def extract_mfcc(audio_path):
#     y, sr = librosa.load(audio_path, sr=16000)
#     y = librosa.util.normalize(y)  # Normalize audio
#     mfcc_features = mfcc(y, sr, nfft=1200)
#     return mfcc_features.mean(axis=0).tolist()

# def verify_speaker(stored_mfcc, new_audio_path):
#     new_mfcc = extract_mfcc(new_audio_path)
#     stored_mfcc = json.loads(stored_mfcc)
#     similarity = 1 - cosine(stored_mfcc, new_mfcc)
#     print(f"Similarity: {similarity}")  # Debug
#     return similarity > 0.65  # Lowered threshold

# @app.route('/')
# def landing():
#     return render_template("landing.html")

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         name = request.form.get('name')
#         email = request.form.get('email')
#         mobile = request.form.get('mobile')
#         audio_file = request.files.get('audio')

#         if not all([name, email, mobile, audio_file]):
#             flash('All fields are required!')
#             return redirect(url_for('register'))

#         audio_path = 'temp_register.wav'
#         audio_file.save(audio_path)
        
#         try:
#             mfcc_features = extract_mfcc(audio_path)
#             with sqlite3.connect(DATABASE) as conn:
#                 c = conn.cursor()
#                 c.execute("INSERT INTO users (name, email, mobile, mfcc_features) VALUES (?, ?, ?, ?)",
#                          (name, email, mobile, json.dumps(mfcc_features)))
#                 conn.commit()
#             os.remove(audio_path)
#             flash('Registration successful! Please log in.')
#             return redirect(url_for('login'))
#         except sqlite3.IntegrityError:
#             flash('Email already registered!')
#             return redirect(url_for('register'))
#         except Exception as e:
#             flash(f'Error: {str(e)}')
#             return redirect(url_for('register'))
#     return render_template('register.html', random_text=generate_text(10))

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         name = request.form.get('name')
#         email = request.form.get('email')
#         audio_file = request.files.get('audio')

#         if not all([name, email, audio_file]):
#             flash('All fields are required!')
#             return redirect(url_for('login'))

#         audio_path = 'temp_login.wav'
#         audio_file.save(audio_path)

#         with sqlite3.connect(DATABASE) as conn:
#             c = conn.cursor()
#             c.execute("SELECT * FROM users WHERE email = ? AND name = ?", (email, name))
#             user = c.fetchone()

#         if not user:
#             flash('Invalid name or email!')
#             os.remove(audio_path)
#             return redirect(url_for('login'))
#         if user[4] is None:
#             flash('Please update your voice profile.')
#             os.remove(audio_path)
#             return redirect(url_for('update_profile'))
#         if verify_speaker(user[4], audio_path):
#             user_obj = User(user[0], user[1], user[2], user[3], user[4])
#             login_user(user_obj)
#             os.remove(audio_path)
#             return redirect(url_for('index'))
#         else:
#             flash('Voice verification failed!')
#             os.remove(audio_path)
#             return redirect(url_for('login'))
#     return render_template('login.html', random_text=generate_text(10))

# @app.route('/update_profile', methods=['GET', 'POST'])
# @login_required
# def update_profile():
#     if request.method == 'POST':
#         audio_file = request.files.get('audio')
#         if not audio_file:
#             flash('Audio file is required!')
#             return redirect(url_for('update_profile'))

#         audio_path = 'temp_update.wav'
#         audio_file.save(audio_path)

#         try:
#             mfcc_features = extract_mfcc(audio_path)
#             with sqlite3.connect(DATABASE) as conn:
#                 c = conn.cursor()
#                 c.execute("UPDATE users SET mfcc_features = ? WHERE id = ?",
#                          (json.dumps(mfcc_features), current_user.id))
#                 conn.commit()
#             os.remove(audio_path)
#             flash('Voice profile updated successfully!')
#             return redirect(url_for('index'))
#         except Exception as e:
#             flash(f'Error: {str(e)}')
#             os.remove(audio_path)
#             return redirect(url_for('update_profile'))
#     return render_template('update_profile.html', random_text=generate_text(10))

# @app.route('/logout')
# @login_required
# def logout():
#     logout_user()
#     return redirect(url_for('landing'))

# @app.route('/index')
# @login_required
# def index():
#     return render_template("home.html")

# @app.route('/dashboard')
# @login_required
# def dashboard():
#     return render_template("dashboard.html")

# @app.route('/own_text')
# @login_required
# def own_text():
#     return render_template('index.html')

# @app.route('/text_to_speech')
# @login_required
# def text_to_speech():
#     return render_template('text_to_speech.html')

# @app.route('/speech_to_text')
# @login_required
# def speech_to_text():
#     return render_template('speech_to_text.html')

# @app.route('/grammar_analysis')
# @login_required
# def grammar_analysis():
#     return render_template('grammar_analysis.html')

# @app.route('/youtube_transcription')
# @login_required
# def youtube_transcription():
#     return render_template('yt.html')

# @app.route('/conversation_module')
# @login_required
# def conversation_module():
#     return render_template('conversation_module.html')

# @app.route('/accent_learning')
# @login_required
# def accent_learning():
#     return render_template('accent_learning.html')

# @app.route('/history_pronunciation')
# @login_required
# def history_pronunciation():
#     return render_template('history_pronunciation.html')

# @app.route('/history_grammar')
# @login_required
# def history_grammar():
#     return render_template('history_grammar.html')

# @app.route('/history_youtube')
# @login_required
# def history_youtube():
#     return render_template('history_youtube.html')

# @app.route('/history_speech_to_text')
# @login_required
# def history_speech_to_text():
#     return render_template('history_speech_to_text.html')

# @app.route('/history_text_to_speech')
# @login_required
# def history_text_to_speech():
#     return render_template('history_text_to_speech.html')

# @app.route('/history_conversation')
# @login_required
# def history_conversation():
#     return render_template('history_conversation.html')

# @app.route('/history_accent')
# @login_required
# def history_accent():
#     return render_template('history_accent.html')

# def generate_text(word_count):
#     text_files = os.listdir(TEXT_FOLDER)
#     random.shuffle(text_files)
#     combined_text = ""
#     for file in text_files:
#         with open(os.path.join(TEXT_FOLDER, file), "r", encoding="utf-8") as f:
#             content = f.read().strip()
#             words = content.split()
#             if len(combined_text.split()) + len(words) <= word_count:
#                 combined_text += " " + content
#             if len(combined_text.split()) >= word_count:
#                 break
#     return combined_text.strip()

# @app.route("/generate_text", methods=["POST"])
# @login_required
# def get_text():
#     data = request.get_json()
#     word_count = data.get("word_count", 10)
#     generated_text = generate_text(word_count)
#     return jsonify({"text": generated_text})

# def convert_audio_to_wav(input_path, output_path):
#     audio = AudioSegment.from_file(input_path)
#     audio = audio.set_frame_rate(16000).set_channels(1)
#     audio = audio + 20
#     audio.export(output_path, format="wav")

# def merge_split_words(expected_words, recognized_words):
#     merged_recognized = []
#     i = 0
#     while i < len(recognized_words):
#         if i < len(recognized_words) - 1:
#             combined_word = recognized_words[i] + recognized_words[i + 1]
#             best_match = difflib.get_close_matches(combined_word, expected_words, n=1, cutoff=0.6)
#             if best_match:
#                 merged_recognized.append(best_match[0])
#                 i += 2
#                 continue
#         if recognized_words[i] in expected_words:
#             merged_recognized.append(recognized_words[i])
#         else:
#             best_match = difflib.get_close_matches(recognized_words[i], expected_words, n=1, cutoff=0.6)
#             merged_recognized.append(best_match[0] if best_match else recognized_words[i])
#         i += 1
#     return merged_recognized

# def recognize_speech_vosk(audio_path):
#     model_path = r"D:\B-Tech\Last Sem\Major\Pronunciation Analysis Flaws Rectification\Model\vosk_model"
#     if not os.path.exists(model_path):
#         return "Vosk model not found"
#     vosk.SetLogLevel(-1)
#     model = vosk.Model(model_path)
#     with sf.SoundFile(audio_path) as audio_file:
#         audio_data = audio_file.read(dtype="int16")
#         sample_rate = audio_file.samplerate
#     rec = vosk.KaldiRecognizer(model, sample_rate)
#     rec.AcceptWaveform(audio_data.tobytes())
#     result = json.loads(rec.FinalResult())
#     return result.get("text", "").lower().strip()

# def recognize_speech_whisper(audio_path):
#     model = whisper.load_model("base")
#     result = model.transcribe(audio_path)
#     return result["text"].lower().strip()

# @app.route('/check_grammar', methods=['POST'])
# @login_required
# def check_grammar():
#     data = request.get_json()
#     text = data.get("text", "")
#     tool = language_tool_python.LanguageTool('en-US')
#     matches = tool.check(text)
#     corrected_text = tool.correct(text)
#     suggestions = [{
#         "rule": match.ruleId,
#         "message": match.message,
#         "replacements": match.replacements
#     } for match in matches]
#     # Store history
#     with sqlite3.connect(DATABASE) as conn:
#         c = conn.cursor()
#         c.execute("INSERT INTO user_history (user_id, feature, timestamp, details) VALUES (?, ?, ?, ?)",
#                   (current_user.id, 'grammar', datetime.now().isoformat(),
#                    json.dumps({'text': text, 'corrections': ', '.join([m['message'] for m in suggestions])})))
#         conn.commit()
#     return jsonify({
#         "matches": suggestions,
#         "corrected": str(TextBlob(corrected_text).correct())
#     })

# def cer(expected_words, recognized_words):
#     expected_text = " ".join(expected_words)
#     recognized_text = " ".join(recognized_words)
#     expected_chars = " ".join(list(expected_text))
#     recognized_chars = " ".join(list(recognized_text))
#     cer_value = jiwer.wer(expected_chars, recognized_chars)
#     if len(expected_text) == 0:
#         return 0.0 if len(recognized_text) == 0 else 1.0
#     return cer_value

# @app.route("/analyze_audio", methods=["POST"])
# @login_required
# def analyze_audio():
#     if "audio" not in request.files:
#         return jsonify({"error": "No audio file uploaded"}), 400

#     audio_file = request.files["audio"]
#     original_audio_path = "temp_input.webm"
#     converted_audio_path = "temp.wav"

#     audio_file.save(original_audio_path)

#     try:
#         convert_audio_to_wav(original_audio_path, converted_audio_path)

#         recognizer = sr.Recognizer()
#         with sr.AudioFile(converted_audio_path) as source:
#             audio_data = recognizer.record(source)

#         google_raw = recognizer.recognize_google(audio_data).lower().strip()
#         vosk_raw = recognize_speech_vosk(converted_audio_path)
#         whisper_raw = recognize_speech_whisper(converted_audio_path)

#         expected_text = request.form.get("expected_text", "").strip().lower()
#         if not expected_text:
#             return jsonify({"error": "Expected text is missing"}), 400

#         has_numbers = bool(re.search(r'\d+', expected_text))
#         honorifics = {"mr", "mrs", "dr", "sr", "jr"}
#         has_honorifics = any(word in honorifics for word in expected_text.split())

#         # Apply custom preprocessing to preserve small words
#         google_custom = custom_preprocess_text(google_raw, use_abbrevs=has_honorifics)
#         vosk_custom = custom_preprocess_text(vosk_raw, use_abbrevs=has_honorifics)
#         whisper_custom = custom_preprocess_text(whisper_raw, use_abbrevs=has_honorifics)

#         y, sample_rate = librosa.load(converted_audio_path, sr=16000)
#         duration = librosa.get_duration(y=y, sr=sample_rate)

#         def compute_wps(text): return len(text.split()) / duration if duration > 0 else 0

#         google_raw_wps = compute_wps(google_raw)
#         google_custom_wps = compute_wps(google_custom)
#         vosk_raw_wps = compute_wps(vosk_raw)
#         vosk_custom_wps = compute_wps(vosk_custom)
#         whisper_raw_wps = compute_wps(whisper_raw)
#         whisper_custom_wps = compute_wps(whisper_custom)

#         expected_words = expected_text.split()
#         google_raw_words = google_raw.split()
#         google_custom_words = google_custom.split()
#         vosk_raw_words = vosk_raw.split()
#         vosk_custom_words = vosk_custom.split()
#         whisper_raw_words = whisper_raw.split()
#         whisper_custom_words = whisper_custom.split()

#         google_merged = merge_split_words(expected_words, google_custom_words)
#         vosk_merged = merge_split_words(expected_words, vosk_custom_words)
#         whisper_merged = merge_split_words(expected_words, whisper_custom_words)

#         def wer(a, b): return jiwer.wer(" ".join(a), " ".join(b))
#         def mispronounced(a, b): return [word for word in a if word not in b]

#         def get_pace(wps):
#             if wps < 1.3:
#                 return "Slow"
#             elif wps < 2.25:
#                 return "Medium Pace"
#             else:
#                 return "Fast Paced"

#         result = {
#             "google_raw": {
#                 "recognized_text": " ".join(google_raw_words),
#                 "wer": round(wer(expected_words, google_raw_words), 2),
#                 "cer": round(cer(expected_words, google_raw_words), 2),
#                 "mispronounced_words": mispronounced(expected_words, google_raw_words),
#                 "wps": round(google_raw_wps, 2),
#                 "pace": get_pace(google_raw_wps)
#             },
#             "google_custom": {
#                 "recognized_text": " ".join(google_merged),
#                 "wer": round(wer(expected_words, google_merged), 2),
#                 "cer": round(cer(expected_words, google_merged), 2),
#                 "mispronounced_words": mispronounced(expected_words, google_merged),
#                 "wps": round(google_custom_wps, 2),
#                 "pace": get_pace(google_custom_wps)
#             },
#             "vosk_raw": {
#                 "recognized_text": " ".join(vosk_raw_words),
#                 "wer": round(wer(expected_words, vosk_raw_words), 2),
#                 "cer": round(cer(expected_words, vosk_raw_words), 2),
#                 "mispronounced_words": mispronounced(expected_words, vosk_raw_words),
#                 "wps": round(vosk_raw_wps, 2),
#                 "pace": get_pace(vosk_raw_wps)
#             },
#             "vosk_custom": {
#                 "recognized_text": " ".join(vosk_merged),
#                 "wer": round(wer(expected_words, vosk_merged), 2),
#                 "cer": round(cer(expected_words, vosk_merged), 2),
#                 "mispronounced_words": mispronounced(expected_words, vosk_merged),
#                 "wps": round(vosk_custom_wps, 2),
#                 "pace": get_pace(vosk_custom_wps)
#             },
#             "whisper_raw": {
#                 "recognized_text": " ".join(whisper_raw_words),
#                 "wer": round(wer(expected_words, whisper_raw_words), 2),
#                 "cer": round(cer(expected_words, whisper_raw_words), 2),
#                 "mispronounced_words": mispronounced(expected_words, whisper_raw_words),
#                 "wps": round(whisper_raw_wps, 2),
#                 "pace": get_pace(whisper_raw_wps)
#             },
#             "whisper_custom": {
#                 "recognized_text": " ".join(whisper_merged),
#                 "wer": round(wer(expected_words, whisper_merged), 2),
#                 "cer": round(cer(expected_words, whisper_merged), 2),
#                 "mispronounced_words": mispronounced(expected_words, whisper_merged),
#                 "wps": round(whisper_custom_wps, 2),
#                 "pace": get_pace(whisper_custom_wps)
#             }
#         }
#         # Store history
#         with sqlite3.connect(DATABASE) as conn:
#             c = conn.cursor()
#             c.execute("INSERT INTO user_history (user_id, feature, timestamp, details) VALUES (?, ?, ?, ?)",
#                       (current_user.id, 'pronunciation', datetime.now().isoformat(),
#                        json.dumps({'sentence': expected_text, 'wer': result['google_custom']['wer'], 'wps': result['google_custom']['wps'], 'cer': result['google_custom']['cer']})))
#             conn.commit()
#         return jsonify(result)

#     except sr.UnknownValueError:
#         google_raw = google_custom = vosk_raw = vosk_custom = whisper_raw = whisper_custom = ""
#         google_raw_wps = google_custom_wps = vosk_raw_wps = vosk_custom_wps = whisper_raw_wps = whisper_custom_wps = 0
#         return jsonify({"error": "Could not understand audio"}), 400
#     except Exception as e:
#         print(f"Error: {str(e)}")
#         return jsonify({"error": str(e)}), 500
#     finally:
#         if os.path.exists(original_audio_path): os.remove(original_audio_path)
#         if os.path.exists(converted_audio_path): os.remove(converted_audio_path)

# @app.route('/transcribe_youtube', methods=['POST'])
# @login_required
# def transcribe_youtube():
#     logger.debug("Received request for /transcribe_youtube")
#     data = request.get_json()
#     youtube_url = data.get('url', '')
    
#     if not youtube_url:
#         logger.error("No URL provided")
#         return jsonify({'error': 'No URL provided'}), 400

#     try:
#         with tempfile.TemporaryDirectory() as temp_dir:
#             logger.debug(f"Created temporary directory: {temp_dir}")
#             audio_path = os.path.join(temp_dir, 'audio.%(ext)s')
            
#             ydl_opts = {
#                 'format': 'bestaudio/best',
#                 'outtmpl': audio_path,
#                 'postprocessors': [{
#                     'key': 'FFmpegExtractAudio',
#                     'preferredcodec': 'mp3',
#                     'preferredquality': '192',
#                 }],
#                 'quiet': True,
#                 'no_warnings': True,
#             }
            
#             logger.debug(f"Downloading audio from URL: {youtube_url}")
#             with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#                 ydl.download([youtube_url])
            
#             downloaded_audio = os.path.join(temp_dir, 'audio.mp3')
#             if not os.path.exists(downloaded_audio):
#                 logger.error("Downloaded audio file not found")
#                 return jsonify({'error': 'Failed to download audio'}), 500
            
#             logger.debug(f"Downloaded audio file: {downloaded_audio}")
            
#             wav_path = os.path.join(temp_dir, 'audio.wav')
#             logger.debug(f"Converting {downloaded_audio} to WAV: {wav_path}")
#             convert_audio_to_wav(downloaded_audio, wav_path)
            
#             if not os.path.exists(wav_path):
#                 logger.error("WAV file conversion failed")
#                 return jsonify({'error': 'Failed to convert audio to WAV'}), 500
            
#             logger.debug(f"Converted WAV file: {wav_path}")
            
#             logger.debug("Starting Whisper transcription")
#             transcription = recognize_speech_whisper(wav_path)
#             logger.debug("Transcription completed")
            
#             # Store history
#             with sqlite3.connect(DATABASE) as conn:
#                 c = conn.cursor()
#                 c.execute("INSERT INTO user_history (user_id, feature, timestamp, details) VALUES (?, ?, ?, ?)",
#                           (current_user.id, 'youtube', datetime.now().isoformat(),
#                            json.dumps({'url': youtube_url, 'transcription': transcription})))
#                 conn.commit()
            
#             return jsonify({'transcription': transcription})
            
#     except Exception as e:
#         logger.error(f"Error during transcription: {str(e)}")
#         return jsonify({'error': f'Failed to transcribe video: {str(e)}'}), 500

# @app.route('/transcribe_local', methods=['POST'])
# @login_required
# def transcribe_local():
#     logger.debug("Received request for /transcribe_local")
    
#     if 'file' not in request.files:
#         logger.error("No file uploaded")
#         return jsonify({'error': 'No file uploaded'}), 400
    
#     file = request.files['file']
#     if file.filename == '':
#         logger.error("No file selected")
#         return jsonify({'error': 'No file selected'}), 400
    
#     try:
#         with tempfile.TemporaryDirectory() as temp_dir:
#             logger.debug(f"Created temporary directory: {temp_dir}")
#             original_path = os.path.join(temp_dir, file.filename)
#             wav_path = os.path.join(temp_dir, 'audio.wav')
            
#             file.save(original_path)
#             logger.debug(f"Saved uploaded file: {original_path}")
            
#             logger.debug(f"Converting {original_path} to WAV: {wav_path}")
#             convert_audio_to_wav(original_path, wav_path)
            
#             if not os.path.exists(wav_path):
#                 logger.error("WAV file conversion failed")
#                 return jsonify({'error': 'Failed to convert audio to WAV'}), 500
            
#             logger.debug(f"Converted WAV file: {wav_path}")
            
#             logger.debug("Starting Whisper transcription")
#             transcription = recognize_speech_whisper(wav_path)
#             logger.debug("Transcription completed")
            
#             # Store history
#             with sqlite3.connect(DATABASE) as conn:
#                 c = conn.cursor()
#                 c.execute("INSERT INTO user_history (user_id, feature, timestamp, details) VALUES (?, ?, ?, ?)",
#                           (current_user.id, 'speech_to_text', datetime.now().isoformat(),
#                            json.dumps({'transcription': transcription})))
#                 conn.commit()
            
#             return jsonify({'transcription': transcription})
            
#     except Exception as e:
#         logger.error(f"Error during local transcription: {str(e)}")
#         return jsonify({'error': f'Failed to transcribe file: {str(e)}'}), 500

# @app.route('/translate', methods=['POST'])
# @login_required
# def translate():
#     logger.debug("Received request for /translate")
#     data = request.get_json()
#     text = data.get('text', '')
#     target_lang = data.get('target_lang', 'en')
    
#     if not text:
#         logger.error("No text provided")
#         return jsonify({'error': 'No text provided'}), 400

#     try:
#         sentences = nltk.sent_tokenize(text)
#         translations = []
#         translator = GoogleTranslator(source='en', target=target_lang)
#         for sentence in sentences:
#             translated = translator.translate(sentence)
#             translations.append({
#                 'original': sentence,
#                 'translated': translated
#             })
#         # Store history
#         with sqlite3.connect(DATABASE) as conn:
#             c = conn.cursor()
#             c.execute("INSERT INTO user_history (user_id, feature, timestamp, details) VALUES (?, ?, ?, ?)",
#                       (current_user.id, 'text_to_speech', datetime.now().isoformat(),
#                        json.dumps({'text': text, 'target_lang': target_lang})))
#             conn.commit()
#         return jsonify({'translations': translations})
#     except Exception as e:
#         logger.error(f"Error during translation: {str(e)}")
#         return jsonify({'error': f'Failed to translate text: {str(e)}'}), 500


# @app.route('/summarize', methods=['POST'])
# @login_required
# def summarize():
#     logger.debug("Received request for /summarize")
#     data = request.get_json()
#     text = data.get('text', '')
    
#     if not text:
#         logger.error("No text provided")
#         return jsonify({'error': 'No text provided'}), 400

#     try:
#         summary = summarizer(text, max_length=300, min_length=100, do_sample=False)
#         summary_text = summary[0]['summary_text']
#         # Store history
#         with sqlite3.connect(DATABASE) as conn:
#             c = conn.cursor()
#             c.execute("INSERT INTO user_history (user_id, feature, timestamp, details) VALUES (?, ?, ?, ?)",
#                       (current_user.id, 'text_to_speech', datetime.now().isoformat(),
#                        json.dumps({'text': text, 'summary': summary_text})))
#             conn.commit()
#         return jsonify({'summary': summary_text})
#     except Exception as e:
#         logger.error(f"Error during summarization: {str(e)}")
#         return jsonify({'error': f'Failed to summarize text: {str(e)}'}), 500
# # @app.route('/summarize', methods=['POST'])
# # @login_required
# # def summarize():
# #     logger.debug("Received request for /summarize")
# #     data = request.get_json()
# #     text = data.get('text', '')
    
# #     if not text:
# #         logger.error("No text provided")
# #         return jsonify({'error': 'No text provided'}), 400

# #     try:
# #         summary = summarizer(text, max_length=300, min_length=100, do_sample=False)
# #         summary_text = summary[0]['summary_text']
# #         # Store history
# #         with sqlite3.connect(DATABASE) as conn:
# #             c = conn.cursor()
# #             c.execute("INSERT INTO user_history (user_id, feature, timestamp, details) VALUES (?, ?, ?, - 1, do_sample=False)
# #         summary_text = summary[0]['summary_text']
# #         # Store history
# #         with sqlite3.connect(DATABASE) as conn:
# #             c = conn.cursor()
# #             c.execute("INSERT INTO user_history (user_id, feature, timestamp, details) VALUES (?, ?, ?, ?)",
# #                       (current_user.id, 'text_to_speech', datetime.now().isoformat(),
# #                        json.dumps({'text': text, 'summary': summary_text})))
# #             conn.commit()
# #         return jsonify({'summary': summary_text})
# #     except Exception as e:
# #         logger.error(f"Error during summarization: {str(e)}")
# #         return jsonify({'error': f'Failed to summarize text: {str(e)}'}), 500

# @app.route('/get_history', methods=['POST'])
# @login_required
# def get_history():
#     data = request.get_json()
#     feature = data.get('feature', 'all')
#     with sqlite3.connect(DATABASE) as conn:
#         c = conn.cursor()
#         if feature == 'all':
#             c.execute("SELECT id, feature, timestamp, details FROM user_history WHERE user_id = ? ORDER BY timestamp DESC", (current_user.id,))
#         else:
#             c.execute("SELECT id, feature, timestamp, details FROM user_history WHERE user_id = ? AND feature = ? ORDER BY timestamp DESC", (current_user.id, feature))
#         history = [{'id': row[0], 'feature': row[1], 'timestamp': row[2], 'details': json.loads(row[3])} for row in c.fetchall()]
#     return jsonify({'history': history})

# if __name__ == "__main__":
#     app.run(debug=True)

################################

import os
import random
import json
import sqlite3
import numpy as np
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from python_speech_features import mfcc
import librosa
from scipy.spatial.distance import cosine
from pydub import AudioSegment
import speech_recognition as sr
import jiwer
import soundfile as sf
import inflect
import difflib
import re
import vosk
from vosk import Model, KaldiRecognizer
import whisper
import language_tool_python
from textblob import TextBlob
import yt_dlp
import tempfile
import logging
import nltk
from deep_translator import GoogleTranslator
from transformers import pipeline
nltk.download('punkt')
nltk.download('punkt_tab')

app = Flask(__name__, template_folder="templates")
app.secret_key = os.urandom(24).hex()  # Secure random key

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# SQLite database setup
DATABASE = 'users.db'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        # Create users table if it doesn't exist
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            mobile TEXT NOT NULL
        )''')
        # Check existing columns
        c.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in c.fetchall()]
        # Add id column if missing
        if 'id' not in columns:
            c.execute("ALTER TABLE users ADD COLUMN id INTEGER")
            # Populate id with unique values
            c.execute("SELECT rowid, * FROM users")
            rows = c.fetchall()
            for i, row in enumerate(rows, 1):
                c.execute("UPDATE users SET id = ? WHERE rowid = ?", (i, row[0]))
            # Make id primary key (requires creating a new table)
            c.execute('''CREATE TABLE users_new (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                mobile TEXT NOT NULL,
                mfcc_features TEXT
            )''')
            c.execute('''INSERT INTO users_new (id, name, email, mobile, mfcc_features)
                        SELECT id, name, email, mobile, mfcc_features FROM users''')
            c.execute("DROP TABLE users")
            c.execute("ALTER TABLE users_new RENAME TO users")
        # Add mfcc_features column if missing
        if 'mfcc_features' not in columns:
            c.execute("ALTER TABLE users ADD COLUMN mfcc_features TEXT")
        # Create user_history table
        c.execute('''CREATE TABLE IF NOT EXISTS user_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            feature TEXT,
            timestamp TEXT,
            details TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )''')
        conn.commit()

init_db()

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, name, email, mobile, mfcc_features):
        self.id = id
        self.name = name
        self.email = email
        self.mobile = mobile
        self.mfcc_features = mfcc_features

@login_manager.user_loader
def load_user(user_id):
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = c.fetchone()
        if user:
            return User(user[0], user[1], user[2], user[3], user[4])
        return None

TEXT_FOLDER = r"D:/B-Tech/Last Sem/Major/New Dataset/Processed_Text"
AUDIO_FOLDER = r"D:/B-Tech/Last Sem/Major/New Dataset/Processed_Audio"

p = inflect.engine()

# Initialize summarization pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def convert_numbers_to_words(text):
    words = text.split()
    new_text = []
    for word in words:
        if word.isdigit():
            new_text.append(p.number_to_words(word))
        else:
            new_text.append(word)
    return " ".join(new_text)

def preprocess_text(text, expand_abbrevs=True):
    text = re.sub(r"[^\w\s':-]", "", text)
    if expand_abbrevs:
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

def custom_preprocess_text(text, use_abbrevs=True):
    # Initialize inflect engine for number-to-word conversion
    p = inflect.engine()
    
    # Split text into words, preserving original spacing
    words = text.split()
    processed_words = []
    
    # Define honorifics mapping (to abbreviate, e.g., "mister" to "mr")
    honorific_map = {
        "mister": "mr",
        "misses": "mrs",
        "doctor": "dr",
        "senior": "sr",
        "junior": "jr"
    }
    
    for word in words:
        # Check for numbers
        if word.isdigit():
            logger.debug(f"Converting number '{word}' to words")
            processed_words.append(p.number_to_words(word))
            continue
        
        # Check for honorifics (case-insensitive)
        word_lower = word.lower()
        if use_abbrevs and word_lower in honorific_map:
            logger.debug(f"Abbreviating honorific '{word}' to '{honorific_map[word_lower]}'")
            processed_words.append(honorific_map[word_lower])
            continue
        
        # Preserve the word exactly as it is
        logger.debug(f"Preserving word '{word}'")
        processed_words.append(word)
    
    processed_text = " ".join(processed_words)
    logger.debug(f"Input: '{text}' -> Output: '{processed_text}'")
    return processed_text

def extract_mfcc(audio_path):
    y, sr = librosa.load(audio_path, sr=16000)
    y = librosa.util.normalize(y)  # Normalize audio
    mfcc_features = mfcc(y, sr, nfft=1200)
    return mfcc_features.mean(axis=0).tolist()

def verify_speaker(stored_mfcc, new_audio_path):
    new_mfcc = extract_mfcc(new_audio_path)
    stored_mfcc = json.loads(stored_mfcc)
    similarity = 1 - cosine(stored_mfcc, new_mfcc)
    print(f"Similarity: {similarity}")  # Debug
    return similarity > 0.30  # Lowered threshold

@app.route('/')
def landing():
    return render_template("landing.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        audio_file = request.files.get('audio')

        if not all([name, email, mobile, audio_file]):
            flash('All fields are required!')
            return redirect(url_for('register'))

        audio_path = 'temp_register.wav'
        audio_file.save(audio_path)
        
        try:
            mfcc_features = extract_mfcc(audio_path)
            with sqlite3.connect(DATABASE) as conn:
                c = conn.cursor()
                c.execute("INSERT INTO users (name, email, mobile, mfcc_features) VALUES (?, ?, ?, ?)",
                         (name, email, mobile, json.dumps(mfcc_features)))
                conn.commit()
            os.remove(audio_path)
            flash('Registration successful! Please log in.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already registered!')
            return redirect(url_for('register'))
        except Exception as e:
            flash(f'Error: {str(e)}')
            return redirect(url_for('register'))
    return render_template('register.html', random_text=generate_text(10))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        audio_file = request.files.get('audio')

        if not all([name, email, audio_file]):
            flash('All fields are required!')
            return redirect(url_for('login'))

        audio_path = 'temp_login.wav'
        audio_file.save(audio_path)

        with sqlite3.connect(DATABASE) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE email = ? AND name = ?", (email, name))
            user = c.fetchone()

        if not user:
            flash('Invalid name or email!')
            os.remove(audio_path)
            return redirect(url_for('login'))
        if user[4] is None:
            flash('Please update your voice profile.')
            os.remove(audio_path)
            return redirect(url_for('update_profile'))
        if verify_speaker(user[4], audio_path):
            user_obj = User(user[0], user[1], user[2], user[3], user[4])
            login_user(user_obj)
            os.remove(audio_path)
            return redirect(url_for('index'))
        else:
            flash('Voice verification failed!')
            os.remove(audio_path)
            return redirect(url_for('login'))
    return render_template('login.html', random_text=generate_text(10))

@app.route('/update_profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    if request.method == 'POST':
        audio_file = request.files.get('audio')
        if not audio_file:
            flash('Audio file is required!')
            return redirect(url_for('update_profile'))

        audio_path = 'temp_update.wav'
        audio_file.save(audio_path)

        try:
            mfcc_features = extract_mfcc(audio_path)
            with sqlite3.connect(DATABASE) as conn:
                c = conn.cursor()
                c.execute("UPDATE users SET mfcc_features = ? WHERE id = ?",
                         (json.dumps(mfcc_features), current_user.id))
                conn.commit()
            os.remove(audio_path)
            flash('Voice profile updated successfully!')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error: {str(e)}')
            os.remove(audio_path)
            return redirect(url_for('update_profile'))
    return render_template('update_profile.html', random_text=generate_text(10))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('landing'))

@app.route('/index')
@login_required
def index():
    return render_template("home.html")

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route('/own_text')
@login_required
def own_text():
    return render_template('index.html')

@app.route('/text_to_speech')
@login_required
def text_to_speech():
    return render_template('text_to_speech.html')

@app.route('/speech_to_text')
@login_required
def speech_to_text():
    return render_template('speech_to_text.html')

@app.route('/grammar_analysis')
@login_required
def grammar_analysis():
    return render_template('grammar_analysis.html')

@app.route('/youtube_transcription')
@login_required
def youtube_transcription():
    return render_template('yt.html')

@app.route('/conversation_module')
@login_required
def conversation_module():
    return render_template('conversation_module.html')

@app.route('/accent_learning')
@login_required
def accent_learning():
    return render_template('accent_learning.html')

@app.route('/history_pronunciation')
@login_required
def history_pronunciation():
    return render_template('history_pronunciation.html')

@app.route('/history_grammar')
@login_required
def history_grammar():
    return render_template('history_grammar.html')

@app.route('/history_youtube')
@login_required
def history_youtube():
    return render_template('history_youtube.html')

@app.route('/history_speech_to_text')
@login_required
def history_speech_to_text():
    return render_template('history_speech_to_text.html')

@app.route('/history_text_to_speech')
@login_required
def history_text_to_speech():
    return render_template('history_text_to_speech.html')

@app.route('/history_conversation')
@login_required
def history_conversation():
    return render_template('history_conversation.html')

@app.route('/history_accent')
@login_required
def history_accent():
    return render_template('history_accent.html')

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
@login_required
def get_text():
    data = request.get_json()
    word_count = data.get("word_count", 10)
    generated_text = generate_text(word_count)
    return jsonify({"text": generated_text})

def convert_audio_to_wav(input_path, output_path):
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_frame_rate(16000).set_channels(1)
    audio = audio + 20
    audio.export(output_path, format="wav")

def merge_split_words(expected_words, recognized_words):
    merged_recognized = []
    i = 0
    while i < len(recognized_words):
        if i < len(recognized_words) - 1:
            combined_word = recognized_words[i] + recognized_words[i + 1]
            best_match = difflib.get_close_matches(combined_word, expected_words, n=1, cutoff=0.6)
            if best_match:
                merged_recognized.append(best_match[0])
                i += 2
                continue
        if recognized_words[i] in expected_words:
            merged_recognized.append(recognized_words[i])
        else:
            best_match = difflib.get_close_matches(recognized_words[i], expected_words, n=1, cutoff=0.6)
            merged_recognized.append(best_match[0] if best_match else recognized_words[i])
        i += 1
    return merged_recognized

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
@login_required
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
    # Store history
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO user_history (user_id, feature, timestamp, details) VALUES (?, ?, ?, ?)",
                  (current_user.id, 'grammar', datetime.now().isoformat(),
                   json.dumps({'text': text, 'corrections': ', '.join([m['message'] for m in suggestions])})))
        conn.commit()
    return jsonify({
        "matches": suggestions,
        "corrected": str(TextBlob(corrected_text).correct())
    })

def cer(expected_words, recognized_words):
    expected_text = " ".join(expected_words)
    recognized_text = " ".join(recognized_words)
    expected_chars = " ".join(list(expected_text))
    recognized_chars = " ".join(list(recognized_text))
    cer_value = jiwer.wer(expected_chars, recognized_chars)
    if len(expected_text) == 0:
        return 0.0 if len(recognized_text) == 0 else 1.0
    return cer_value

@app.route("/analyze_audio", methods=["POST"])
@login_required
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
        vosk_raw = recognize_speech_vosk(converted_audio_path)
        whisper_raw = recognize_speech_whisper(converted_audio_path)

        expected_text = request.form.get("expected_text", "").strip().lower()
        if not expected_text:
            return jsonify({"error": "Expected text is missing"}), 400

        honorifics = {"mr", "mrs", "dr", "sr", "jr"}
        has_honorifics = any(word in honorifics for word in expected_text.split())

        # Apply custom preprocessing to preserve raw output except for numbers and honorifics
        logger.debug(f"Processing Google raw: '{google_raw}'")
        google_custom = custom_preprocess_text(google_raw, use_abbrevs=has_honorifics)
        logger.debug(f"Processing Vosk raw: '{vosk_raw}'")
        vosk_custom = custom_preprocess_text(vosk_raw, use_abbrevs=has_honorifics)
        logger.debug(f"Processing Whisper raw: '{whisper_raw}'")
        whisper_custom = custom_preprocess_text(whisper_raw, use_abbrevs=has_honorifics)

        y, sample_rate = librosa.load(converted_audio_path, sr=16000)
        duration = librosa.get_duration(y=y, sr=sample_rate)

        def compute_wps(text): return len(text.split()) / duration if duration > 0 else 0

        google_raw_wps = compute_wps(google_raw)
        google_custom_wps = compute_wps(google_custom)
        vosk_raw_wps = compute_wps(vosk_raw)
        vosk_custom_wps = compute_wps(vosk_custom)
        whisper_raw_wps = compute_wps(whisper_raw)
        whisper_custom_wps = compute_wps(whisper_custom)

        expected_words = expected_text.split()
        google_raw_words = google_raw.split()
        google_custom_words = google_custom.split()
        vosk_raw_words = vosk_raw.split()
        vosk_custom_words = vosk_custom.split()
        whisper_raw_words = whisper_raw.split()
        whisper_custom_words = whisper_custom.split()

        logger.debug(f"Google custom words before merge: {google_custom_words}")
        logger.debug(f"Vosk custom words before merge: {vosk_custom_words}")
        logger.debug(f"Whisper custom words before merge: {whisper_custom_words}")

        google_merged = merge_split_words(expected_words, google_custom_words)
        vosk_merged = merge_split_words(expected_words, vosk_custom_words)
        whisper_merged = merge_split_words(expected_words, whisper_custom_words)

        logger.debug(f"Google merged words: {google_merged}")
        logger.debug(f"Vosk merged words: {vosk_merged}")
        logger.debug(f"Whisper merged words: {whisper_merged}")

        def wer(a, b): return jiwer.wer(" ".join(a), " ".join(b))
        def mispronounced(a, b): return [word for word in a if word not in b]

        def get_pace(wps):
            if wps < 1.3:
                return "Slow"
            elif wps < 2.25:
                return "Medium Pace"
            else:
                return "Fast Paced"

        result = {
            "google_raw": {
                "recognized_text": " ".join(google_raw_words),
                "wer": round(wer(expected_words, google_raw_words), 2),
                "cer": round(cer(expected_words, google_raw_words), 2),
                "mispronounced_words": mispronounced(expected_words, google_raw_words),
                "wps": round(google_raw_wps, 2),
                "pace": get_pace(google_raw_wps)
            },
            "google_custom": {
                "recognized_text": " ".join(google_merged),
                "wer": round(wer(expected_words, google_merged), 2),
                "cer": round(cer(expected_words, google_merged), 2),
                "mispronounced_words": mispronounced(expected_words, google_merged),
                "wps": round(google_custom_wps, 2),
                "pace": get_pace(google_custom_wps)
            },
            "vosk_raw": {
                "recognized_text": " ".join(vosk_raw_words),
                "wer": round(wer(expected_words, vosk_raw_words), 2),
                "cer": round(cer(expected_words, vosk_raw_words), 2),
                "mispronounced_words": mispronounced(expected_words, vosk_raw_words),
                "wps": round(vosk_raw_wps, 2),
                "pace": get_pace(vosk_raw_wps)
            },
            "vosk_custom": {
                "recognized_text": " ".join(vosk_merged),
                "wer": round(wer(expected_words, vosk_merged), 2),
                "cer": round(cer(expected_words, vosk_merged), 2),
                "mispronounced_words": mispronounced(expected_words, vosk_merged),
                "wps": round(vosk_custom_wps, 2),
                "pace": get_pace(vosk_custom_wps)
            },
            "whisper_raw": {
                "recognized_text": " ".join(whisper_raw_words),
                "wer": round(wer(expected_words, whisper_raw_words), 2),
                "cer": round(cer(expected_words, whisper_raw_words), 2),
                "mispronounced_words": mispronounced(expected_words, whisper_raw_words),
                "wps": round(whisper_raw_wps, 2),
                "pace": get_pace(whisper_raw_wps)
            },
            "whisper_custom": {
                "recognized_text": " ".join(whisper_merged),
                "wer": round(wer(expected_words, whisper_merged), 2),
                "cer": round(cer(expected_words, whisper_merged), 2),
                "mispronounced_words": mispronounced(expected_words, whisper_merged),
                "wps": round(whisper_custom_wps, 2),
                "pace": get_pace(whisper_custom_wps)
            }
        }
        # Store history
        with sqlite3.connect(DATABASE) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO user_history (user_id, feature, timestamp, details) VALUES (?, ?, ?, ?)",
                      (current_user.id, 'pronunciation', datetime.now().isoformat(),
                       json.dumps({'sentence': expected_text, 'wer': result['google_custom']['wer'], 'wps': result['google_custom']['wps'], 'cer': result['google_custom']['cer']})))
            conn.commit()
        return jsonify(result)

    except sr.UnknownValueError:
        google_raw = google_custom = vosk_raw = vosk_custom = whisper_raw = whisper_custom = ""
        google_raw_wps = google_custom_wps = vosk_raw_wps = vosk_custom_wps = whisper_raw_wps = whisper_custom_wps = 0
        return jsonify({"error": "Could not understand audio"}), 400
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(original_audio_path): os.remove(original_audio_path)
        if os.path.exists(converted_audio_path): os.remove(converted_audio_path)

@app.route('/transcribe_youtube', methods=['POST'])
@login_required
def transcribe_youtube():
    logger.debug("Received request for /transcribe_youtube")
    data = request.get_json()
    youtube_url = data.get('url', '')
    
    if not youtube_url:
        logger.error("No URL provided")
        return jsonify({'error': 'No URL provided'}), 400

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            logger.debug(f"Created temporary directory: {temp_dir}")
            audio_path = os.path.join(temp_dir, 'audio.%(ext)s')
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': audio_path,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True,
                'no_warnings': True,
            }
            
            logger.debug(f"Downloading audio from URL: {youtube_url}")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([youtube_url])
            
            downloaded_audio = os.path.join(temp_dir, 'audio.mp3')
            if not os.path.exists(downloaded_audio):
                logger.error("Downloaded audio file not found")
                return jsonify({'error': 'Failed to download audio'}), 500
            
            logger.debug(f"Downloaded audio file: {downloaded_audio}")
            
            wav_path = os.path.join(temp_dir, 'audio.wav')
            logger.debug(f"Converting {downloaded_audio} to WAV: {wav_path}")
            convert_audio_to_wav(downloaded_audio, wav_path)
            
            if not os.path.exists(wav_path):
                logger.error("WAV file conversion failed")
                return jsonify({'error': 'Failed to convert audio to WAV'}), 500
            
            logger.debug(f"Converted WAV file: {wav_path}")
            
            logger.debug("Starting Whisper transcription")
            transcription = recognize_speech_whisper(wav_path)
            logger.debug("Transcription completed")
            
            # Store history
            with sqlite3.connect(DATABASE) as conn:
                c = conn.cursor()
                c.execute("INSERT INTO user_history (user_id, feature, timestamp, details) VALUES (?, ?, ?, ?)",
                          (current_user.id, 'youtube', datetime.now().isoformat(),
                           json.dumps({'url': youtube_url, 'transcription': transcription})))
                conn.commit()
            
            return jsonify({'transcription': transcription})
            
    except Exception as e:
        logger.error(f"Error during transcription: {str(e)}")
        return jsonify({'error': f'Failed to transcribe video: {str(e)}'}), 500

@app.route('/transcribe_local', methods=['POST'])
@login_required
def transcribe_local():
    logger.debug("Received request for /transcribe_local")
    
    if 'file' not in request.files:
        logger.error("No file uploaded")
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        logger.error("No file selected")
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            logger.debug(f"Created temporary directory: {temp_dir}")
            original_path = os.path.join(temp_dir, file.filename)
            wav_path = os.path.join(temp_dir, 'audio.wav')
            
            file.save(original_path)
            logger.debug(f"Saved uploaded file: {original_path}")
            
            logger.debug(f"Converting {original_path} to WAV: {wav_path}")
            convert_audio_to_wav(original_path, wav_path)
            
            if not os.path.exists(wav_path):
                logger.error("WAV file conversion failed")
                return jsonify({'error': 'Failed to convert audio to WAV'}), 500
            
            logger.debug(f"Converted WAV file: {wav_path}")
            
            logger.debug("Starting Whisper transcription")
            transcription = recognize_speech_whisper(wav_path)
            logger.debug("Transcription completed")
            
            # Store history
            with sqlite3.connect(DATABASE) as conn:
                c = conn.cursor()
                c.execute("INSERT INTO user_history (user_id, feature, timestamp, details) VALUES (?, ?, ?, ?)",
                          (current_user.id, 'speech_to_text', datetime.now().isoformat(),
                           json.dumps({'transcription': transcription})))
                conn.commit()
            
            return jsonify({'transcription': transcription})
            
    except Exception as e:
        logger.error(f"Error during local transcription: {str(e)}")
        return jsonify({'error': f'Failed to transcribe file: {str(e)}'}), 500

@app.route('/translate', methods=['POST'])
@login_required
def translate():
    logger.debug("Received request for /translate")
    data = request.get_json()
    text = data.get('text', '')
    target_lang = data.get('target_lang', 'en')
    
    if not text:
        logger.error("No text provided")
        return jsonify({'error': 'No text provided'}), 400

    try:
        sentences = nltk.sent_tokenize(text)
        translations = []
        translator = GoogleTranslator(source='en', target=target_lang)
        for sentence in sentences:
            translated = translator.translate(sentence)
            translations.append({
                'original': sentence,
                'translated': translated
            })
        # Store history
        with sqlite3.connect(DATABASE) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO user_history (user_id, feature, timestamp, details) VALUES (?, ?, ?, ?)",
                      (current_user.id, 'text_to_speech', datetime.now().isoformat(),
                       json.dumps({'text': text, 'target_lang': target_lang})))
            conn.commit()
        return jsonify({'translations': translations})
    except Exception as e:
        logger.error(f"Error during translation: {str(e)}")
        return jsonify({'error': f'Failed to translate text: {str(e)}'}), 500

@app.route('/summarize', methods=['POST'])
@login_required
def summarize():
    logger.debug("Received request for /summarize")
    data = request.get_json()
    text = data.get('text', '')
    
    if not text:
        logger.error("No text provided")
        return jsonify({'error': 'No text provided'}), 400

    try:
        summary = summarizer(text, max_length=300, min_length=100, do_sample=False)
        summary_text = summary[0]['summary_text']
        # Store history
        with sqlite3.connect(DATABASE) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO user_history (user_id, feature, timestamp, details) VALUES (?, ?, ?, ?)",
                      (current_user.id, 'text_to_speech', datetime.now().isoformat(),
                       json.dumps({'text': text, 'summary': summary_text})))
            conn.commit()
        return jsonify({'summary': summary_text})
    except Exception as e:
        logger.error(f"Error during summarization: {str(e)}")
        return jsonify({'error': f'Failed to summarize text: {str(e)}'}), 500

@app.route('/get_history', methods=['POST'])
@login_required
def get_history():
    data = request.get_json()
    feature = data.get('feature', 'all')
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        if feature == 'all':
            c.execute("SELECT id, feature, timestamp, details FROM user_history WHERE user_id = ? ORDER BY timestamp DESC", (current_user.id,))
        else:
            c.execute("SELECT id, feature, timestamp, details FROM user_history WHERE user_id = ? AND feature = ? ORDER BY timestamp DESC", (current_user.id, feature))
        history = [{'id': row[0], 'feature': row[1], 'timestamp': row[2], 'details': json.loads(row[3])} for row in c.fetchall()]
    return jsonify({'history': history})

if __name__ == "__main__":
    app.run(debug=True)