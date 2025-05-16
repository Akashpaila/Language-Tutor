// let mediaRecorder;
// let audioChunks = [];
// let expectedText = "";

// document.addEventListener("DOMContentLoaded", function () {
//     const wordCountInput = document.getElementById("wordCount"); 
//     const difficultyRadios = document.getElementsByName("difficulty");
//     const customTextArea = document.getElementById('customTextArea');
//     const modelSelect = document.getElementById('modelSelect');
//     const resultDisplay = document.getElementById('resultDisplay');

//     // Show/hide custom textarea based on radio button selection
//     difficultyRadios.forEach(radio => {
//         radio.addEventListener("change", function () {
//             if (this.value === "beginner") {
//                 wordCountInput.value = 10; 
//                 wordCountInput.disabled = true;
//                 customTextArea.classList.add('hidden');
//             } else if (this.value === "intermediate") {
//                 wordCountInput.value = 25;
//                 wordCountInput.disabled = true;
//                 customTextArea.classList.add('hidden');
//             } else if (this.value === "advanced") {
//                 wordCountInput.disabled = false;
//                 customTextArea.classList.add('hidden');
//             } else if (this.value === "custom") {
//                 wordCountInput.disabled = true;
//                 customTextArea.classList.remove('hidden');
//                 expectedText = document.getElementById('referenceText').value || ""; // Set expected text to custom input
//                 document.getElementById("displayText").textContent = expectedText; // Update displayed text
//             }
//         });
//     });

//     // Initial check to set default state (e.g., Advanced is checked)
//     const checkedRadio = document.querySelector('input[name="difficulty"]:checked');
//     if (checkedRadio) {
//         checkedRadio.dispatchEvent(new Event('change'));
//     }

//     document.getElementById("generateText").addEventListener("click", () => {
//         const wordCount = document.getElementById("wordCount").value;

//         fetch("/generate_text", {
//             method: "POST",
//             headers: { "Content-Type": "application/json" },
//             body: JSON.stringify({ word_count: parseInt(wordCount) })
//         })
//         .then(response => response.json())
//         .then(data => {
//             expectedText = data.text;
//             document.getElementById("displayText").textContent = expectedText;
//         })
//         .catch(error => console.error("Error fetching text:", error));
//     });

//     document.getElementById("startRecord").addEventListener("click", () => {
//         navigator.mediaDevices.getUserMedia({ audio: true })
//             .then(stream => {
//                 mediaRecorder = new MediaRecorder(stream);
//                 mediaRecorder.start();

//                 mediaRecorder.ondataavailable = event => {
//                     audioChunks.push(event.data);
//                 };

//                 document.getElementById("startRecord").disabled = true;
//                 document.getElementById("stopRecord").disabled = false;
//             })
//             .catch(error => console.error("Error accessing microphone:", error));
//     });

//     document.getElementById("stopRecord").addEventListener("click", () => {
//         mediaRecorder.stop();
//         mediaRecorder.onstop = () => {
//             const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
//             const audioURL = URL.createObjectURL(audioBlob);
//             document.getElementById("audioPlayer").src = audioURL;

//             document.getElementById("stopRecord").disabled = true;
//             document.getElementById("playAudio").disabled = false;
//             document.getElementById("analyzeAudio").disabled = false;
//         };
//     });

//     document.getElementById("playAudio").addEventListener("click", () => {
//         document.getElementById("audioPlayer").play();
//     });

//     document.getElementById("analyzeAudio").addEventListener("click", () => {
//         const name = document.getElementById('name').value.trim();
//         const email = document.getElementById('email').value.trim();
//         const selectedDifficulty = document.querySelector('input[name="difficulty"]:checked').value;

//         if (!name || !email) {
//             alert("Please enter both Name and Email before analyzing.");
//             return;
//         }

//         let textToAnalyze;
//         if (selectedDifficulty === "custom") {
//             textToAnalyze = document.getElementById('referenceText').value.trim();
//             if (!textToAnalyze) {
//                 alert("Please enter reference text for custom analysis.");
//                 return;
//             }
//             expectedText = textToAnalyze; // Update expected text for custom input
//         } else {
//             textToAnalyze = expectedText; // Use generated text for other levels
//         }

//         const formData = new FormData();
//         formData.append('name', name);
//         formData.append('email', email);
//         formData.append("audio", new Blob(audioChunks, { type: "audio/wav" }));
//         formData.append("expected_text", textToAnalyze);

//         fetch("/analyze_audio", { method: "POST", body: formData })
//         .then(response => response.json())
//         .then(data => {
//             // Store all results in an object
//             const allResults = {
//                 google_raw: data.google_raw,
//                 google: data.google_custom,
//                 vosk: data.vosk,
//                 whisper: data.whisper
//             };

//             // Update dropdown to show results based on selection
//             modelSelect.addEventListener('change', function() {
//                 const selectedModel = this.value;
//                 const modelResult = allResults[selectedModel] || { error: "No result for this model" };

//                 let resultHtml = `<strong>Results for ${selectedModel}:</strong><br>`;
//                 resultHtml += `Recognized Speech: ${modelResult.recognized_text || 'N/A'}<br>`;
//                 resultHtml += `Word Error Rate (WER): ${modelResult.wer || 'N/A'}<br>`;
//                 resultHtml += `Mispronounced Words: ${modelResult.mispronounced_words ? modelResult.mispronounced_words.join(', ') : 'N/A'}<br>`;
//                 resultHtml += `Words Per Second (WPS): ${modelResult.wps || 'N/A'}<br>`;
//                 resultHtml += `Pace of the Speech: ${modelResult.pace || 'N/A'}<br>`;
//                 if (modelResult.per_word_confidence) {
//                     resultHtml += `Per Word Confidence: ${modelResult.per_word_confidence || 'N/A'}<br>`;
//                 }
//                 if (modelResult.per_word_timings) {
//                     resultHtml += `Per Word Timings: ${modelResult.per_word_timings || 'N/A'}<br>`;
//                 }

//                 resultDisplay.innerHTML = resultHtml;
//             });

//             // Trigger dropdown change to show initial result (e.g., first model)
//             modelSelect.selectedIndex = 0;
//             modelSelect.dispatchEvent(new Event('change'));

//         })
//         .catch(error => console.error("Error analyzing speech:", error));
//     });
// });





// let mediaRecorder;
// let audioChunks = [];
// let expectedText = "";

// document.addEventListener("DOMContentLoaded", function () {
//     const wordCountInput = document.getElementById("wordCount"); 
//     const difficultyRadios = document.getElementsByName("difficulty");
//     const customTextArea = document.getElementById('customTextArea');
//     const generateTextButton = document.getElementById('generateText'); // New reference
//     const modelSelect = document.getElementById('modelSelect');
//     const resultDisplay = document.getElementById('resultDisplay');
//     const startRecordButton = document.getElementById('startRecord');
//     const stopRecordButton = document.getElementById('stopRecord');
//     const playAudioButton = document.getElementById('playAudio');
//     const analyzeAudioButton = document.getElementById('analyzeAudio');

//     // Show/hide custom textarea and word count/generate text based on radio button selection
//     difficultyRadios.forEach(radio => {
//         radio.addEventListener("change", function () {
//             if (this.value === "beginner") {
//                 wordCountInput.value = 10; 
//                 wordCountInput.disabled = true;
//                 customTextArea.classList.add('hidden');
//                 wordCountInput.style.display = 'block'; // Show word count
//                 generateTextButton.style.display = 'block'; // Show generate button
//             } else if (this.value === "intermediate") {
//                 wordCountInput.value = 25;
//                 wordCountInput.disabled = true;
//                 customTextArea.classList.add('hidden');
//                 wordCountInput.style.display = 'block'; // Show word count
//                 generateTextButton.style.display = 'block'; // Show generate button
//             } else if (this.value === "advanced") {
//                 wordCountInput.disabled = false;
//                 customTextArea.classList.add('hidden');
//                 wordCountInput.style.display = 'block'; // Show word count
//                 generateTextButton.style.display = 'block'; // Show generate button
//             } else if (this.value === "custom") {
//                 wordCountInput.disabled = true;
//                 customTextArea.classList.remove('hidden');
//                 wordCountInput.style.display = 'none'; // Hide word count
//                 generateTextButton.style.display = 'none'; // Hide generate button
//                 expectedText = document.getElementById('referenceText').value || ""; // Set expected text to custom input
//                 document.getElementById("displayText").textContent = expectedText; // Update displayed text
//             }
//         });
//     });

//     // Initial check to set default state (e.g., Advanced is checked)
//     const checkedRadio = document.querySelector('input[name="difficulty"]:checked');
//     if (checkedRadio) {
//         checkedRadio.dispatchEvent(new Event('change'));
//     }

//     document.getElementById("generateText").addEventListener("click", () => {
//         const wordCount = document.getElementById("wordCount").value;

//         fetch("/generate_text", {
//             method: "POST",
//             headers: { "Content-Type": "application/json" },
//             body: JSON.stringify({ word_count: parseInt(wordCount) })
//         })
//         .then(response => response.json())
//         .then(data => {
//             expectedText = data.text;
//             document.getElementById("displayText").textContent = expectedText;
//         })
//         .catch(error => console.error("Error fetching text:", error));
//     });

//     document.getElementById("startRecord").addEventListener("click", () => {
//         navigator.mediaDevices.getUserMedia({ audio: true })
//             .then(stream => {
//                 mediaRecorder = new MediaRecorder(stream);
//                 mediaRecorder.start();

//                 mediaRecorder.ondataavailable = event => {
//                     audioChunks.push(event.data);
//                 };

//                 startRecordButton.disabled = true;
//                 stopRecordButton.disabled = false;
//                 playAudioButton.disabled = true; // Disable play until recording stops
//                 analyzeAudioButton.disabled = true; // Disable analyze until recording stops
//             })
//             .catch(error => console.error("Error accessing microphone:", error));
//     });

//     document.getElementById("stopRecord").addEventListener("click", () => {
//         mediaRecorder.stop();
//         mediaRecorder.onstop = () => {
//             const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
//             const audioURL = URL.createObjectURL(audioBlob);
//             document.getElementById("audioPlayer").src = audioURL;

//             stopRecordButton.disabled = true;
//             startRecordButton.disabled = false;
//             playAudioButton.disabled = false;
//             analyzeAudioButton.disabled = false;
//         };
//     });

//     document.getElementById("playAudio").addEventListener("click", () => {
//         document.getElementById("audioPlayer").play();
//     });

//     document.getElementById("analyzeAudio").addEventListener("click", () => {
//         const name = document.getElementById('name').value.trim();
//         const email = document.getElementById('email').value.trim();
//         const selectedDifficulty = document.querySelector('input[name="difficulty"]:checked').value;

//         if (!name || !email) {
//             alert("Please enter both Name and Email before analyzing.");
//             return;
//         }

//         let textToAnalyze;
//         if (selectedDifficulty === "custom") {
//             textToAnalyze = document.getElementById('referenceText').value.trim();
//             if (!textToAnalyze) {
//                 alert("Please enter reference text for custom analysis.");
//                 return;
//             }
//             expectedText = textToAnalyze; // Update expected text for custom input
//         } else {
//             textToAnalyze = expectedText; // Use generated text for other levels
//         }

//         const formData = new FormData();
//         formData.append('name', name);
//         formData.append('email', email);
//         formData.append("audio", new Blob(audioChunks, { type: "audio/wav" }));
//         formData.append("expected_text", textToAnalyze);

//         fetch("/analyze_audio", { method: "POST", body: formData })
//         .then(response => response.json())
//         .then(data => {
//             // Store all results in an object
//             const allResults = {
//                 google_raw: data.google_raw,
//                 google: data.google_custom,
//                 vosk: data.vosk,
//                 whisper: data.whisper
//             };

//             // Update dropdown to show results based on selection
//             modelSelect.addEventListener('change', function() {
//                 const selectedModel = this.value;
//                 const modelResult = allResults[selectedModel] || { error: "No result for this model" };

//                 let resultHtml = `<strong>Results for ${selectedModel}:</strong><br>`;
//                 resultHtml += `Recognized Speech: ${modelResult.recognized_text || 'N/A'}<br>`;
//                 resultHtml += `Word Error Rate (WER): ${modelResult.wer || 'N/A'}<br>`;
//                 resultHtml += `Mispronounced Words: ${modelResult.mispronounced_words ? modelResult.mispronounced_words.join(', ') : 'N/A'}<br>`;
//                 resultHtml += `Words Per Second (WPS): ${modelResult.wps || 'N/A'}<br>`;
//                 resultHtml += `Pace of the Speech: ${modelResult.pace || 'N/A'}<br>`;
//                 if (modelResult.per_word_confidence) {
//                     resultHtml += `Per Word Confidence: ${modelResult.per_word_confidence || 'N/A'}<br>`;
//                 }
//                 if (modelResult.per_word_timings) {
//                     resultHtml += `Per Word Timings: ${modelResult.per_word_timings || 'N/A'}<br>`;
//                 }

//                 resultDisplay.innerHTML = resultHtml;
//             });

//             // Trigger dropdown change to show initial result (e.g., first model)
//             modelSelect.selectedIndex = 0;
//             modelSelect.dispatchEvent(new Event('change'));

//             // Reset recording state after analysis
//             resetRecordingState();
//         })
//         .catch(error => console.error("Error analyzing speech:", error));
//     });

//     // Function to reset recording state
//     function resetRecordingState() {
//         audioChunks = []; // Clear audio chunks
//         document.getElementById("audioPlayer").src = ""; // Clear audio player source
//         startRecordButton.disabled = false; // Re-enable start recording
//         stopRecordButton.disabled = true; // Disable stop recording
//         playAudioButton.disabled = true; // Disable play audio
//         analyzeAudioButton.disabled = true; // Disable analyze until new recording
//     }
// });

//////////////////////////////////////////////// 

// let mediaRecorder;
// let audioChunks = [];
// let expectedText = "";

// document.addEventListener("DOMContentLoaded", function () {
//     const wordCountInput = document.getElementById("wordCount"); 
//     const difficultyRadios = document.getElementsByName("difficulty");
//     const customTextArea = document.getElementById('customTextArea');
//     const modelSelect = document.getElementById('modelSelect');
//     const resultDisplay = document.getElementById('resultDisplay');
//     const startRecordButton = document.getElementById('startRecord');
//     const stopRecordButton = document.getElementById('stopRecord');
//     const playAudioButton = document.getElementById('playAudio');
//     const analyzeAudioButton = document.getElementById('analyzeAudio');

//     // Show/hide custom textarea based on radio button selection
//     difficultyRadios.forEach(radio => {
//         radio.addEventListener("change", function () {
//             if (this.value === "beginner") {
//                 wordCountInput.value = 10; 
//                 wordCountInput.disabled = true;
//                 customTextArea.classList.add('hidden');
//             } else if (this.value === "intermediate") {
//                 wordCountInput.value = 25;
//                 wordCountInput.disabled = true;
//                 customTextArea.classList.add('hidden');
//             } else if (this.value === "advanced") {
//                 wordCountInput.disabled = false;
//                 customTextArea.classList.add('hidden');
//             } else if (this.value === "custom") {
//                 wordCountInput.disabled = true;
//                 customTextArea.classList.remove('hidden');
//                 expectedText = document.getElementById('referenceText').value || ""; // Set expected text to custom input
//                 document.getElementById("displayText").textContent = expectedText; // Update displayed text
//             }
//         });
//     });

//     // Initial check to set default state (e.g., Advanced is checked)
//     const checkedRadio = document.querySelector('input[name="difficulty"]:checked');
//     if (checkedRadio) {
//         checkedRadio.dispatchEvent(new Event('change'));
//     }

//     document.getElementById("generateText").addEventListener("click", () => {
//         const wordCount = document.getElementById("wordCount").value;

//         fetch("/generate_text", {
//             method: "POST",
//             headers: { "Content-Type": "application/json" },
//             body: JSON.stringify({ word_count: parseInt(wordCount) })
//         })
//         .then(response => response.json())
//         .then(data => {
//             expectedText = data.text;
//             document.getElementById("displayText").textContent = expectedText;
//         })
//         .catch(error => console.error("Error fetching text:", error));
//     });

//     document.getElementById("startRecord").addEventListener("click", () => {
//         navigator.mediaDevices.getUserMedia({ audio: true })
//             .then(stream => {
//                 mediaRecorder = new MediaRecorder(stream);
//                 mediaRecorder.start();

//                 mediaRecorder.ondataavailable = event => {
//                     audioChunks.push(event.data);
//                 };

//                 startRecordButton.disabled = true;
//                 stopRecordButton.disabled = false;
//                 playAudioButton.disabled = true; // Disable play until recording stops
//                 analyzeAudioButton.disabled = true; // Disable analyze until recording stops
//             })
//             .catch(error => console.error("Error accessing microphone:", error));
//     });

//     document.getElementById("stopRecord").addEventListener("click", () => {
//         mediaRecorder.stop();
//         mediaRecorder.onstop = () => {
//             const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
//             const audioURL = URL.createObjectURL(audioBlob);
//             document.getElementById("audioPlayer").src = audioURL;

//             stopRecordButton.disabled = true;
//             startRecordButton.disabled = false;
//             playAudioButton.disabled = false;
//             analyzeAudioButton.disabled = false;
//         };
//     });

//     document.getElementById("playAudio").addEventListener("click", () => {
//         document.getElementById("audioPlayer").play();
//     });

//     document.getElementById("analyzeAudio").addEventListener("click", () => {
//         const name = document.getElementById('name').value.trim();
//         const email = document.getElementById('email').value.trim();
//         const selectedDifficulty = document.querySelector('input[name="difficulty"]:checked').value;

//         if (!name || !email) {
//             alert("Please enter both Name and Email before analyzing.");
//             return;
//         }

//         let textToAnalyze;
//         if (selectedDifficulty === "custom") {
//             textToAnalyze = document.getElementById('referenceText').value.trim();
//             if (!textToAnalyze) {
//                 alert("Please enter reference text for custom analysis.");
//                 return;
//             }
//             expectedText = textToAnalyze; // Update expected text for custom input
//         } else {
//             textToAnalyze = expectedText; // Use generated text for other levels
//         }

//         const formData = new FormData();
//         formData.append('name', name);
//         formData.append('email', email);
//         formData.append("audio", new Blob(audioChunks, { type: "audio/wav" }));
//         formData.append("expected_text", textToAnalyze);

//         fetch("/analyze_audio", { method: "POST", body: formData })
//         .then(response => response.json())
//         .then(data => {
//             // Store all results in an object
//             const allResults = {
//                 google_raw: data.google_raw,
//                 google: data.google_custom,
//                 vosk: data.vosk,
//                 whisper: data.whisper
//             };

//             // Update dropdown to show results based on selection
//             modelSelect.addEventListener('change', function() {
//                 const selectedModel = this.value;
//                 const modelResult = allResults[selectedModel] || { error: "No result for this model" };

//                 let resultHtml = `<strong>Results for ${selectedModel}:</strong><br>`;
//                 resultHtml += `Recognized Speech: ${modelResult.recognized_text || 'N/A'}<br>`;
//                 resultHtml += `Word Error Rate (WER): ${modelResult.wer || 'N/A'}<br>`;
//                 resultHtml += `Mispronounced Words: ${modelResult.mispronounced_words ? modelResult.mispronounced_words.join(', ') : 'N/A'}<br>`;
//                 resultHtml += `Words Per Second (WPS): ${modelResult.wps || 'N/A'}<br>`;
//                 resultHtml += `Pace of the Speech: ${modelResult.pace || 'N/A'}<br>`;
//                 if (modelResult.per_word_confidence) {
//                     resultHtml += `Per Word Confidence: ${modelResult.per_word_confidence || 'N/A'}<br>`;
//                 }
//                 if (modelResult.per_word_timings) {
//                     resultHtml += `Per Word Timings: ${modelResult.per_word_timings || 'N/A'}<br>`;
//                 }

//                 resultDisplay.innerHTML = resultHtml;
//             });

//             // Trigger dropdown change to show initial result (e.g., first model)
//             modelSelect.selectedIndex = 0;
//             modelSelect.dispatchEvent(new Event('change'));

//             // Reset recording state after analysis
//             resetRecordingState();
//         })
//         .catch(error => console.error("Error analyzing speech:", error));
//     });

//     // Function to reset recording state
//     function resetRecordingState() {
//         audioChunks = []; // Clear audio chunks
//         document.getElementById("audioPlayer").src = ""; // Clear audio player source
//         startRecordButton.disabled = false; // Re-enable start recording
//         stopRecordButton.disabled = true; // Disable stop recording
//         playAudioButton.disabled = true; // Disable play audio
//         analyzeAudioButton.disabled = true; // Disable analyze until new recording
//     }
// });


////////////////////////////////////////////// 

// let mediaRecorder;
// let audioChunks = [];
// let expectedText = "";

// document.addEventListener("DOMContentLoaded", function () {
//     const wordCountInput = document.getElementById("wordCount");
//     const difficultyRadios = document.getElementsByName("difficulty");
//     const customTextArea = document.getElementById('customTextArea');
//     const modelSelect = document.getElementById('modelSelect');
//     const resultDisplay = document.getElementById('resultDisplay');
//     const startRecordButton = document.getElementById('startRecord');
//     const stopRecordButton = document.getElementById('stopRecord');
//     const playAudioButton = document.getElementById('playAudio');
//     const analyzeAudioButton = document.getElementById('analyzeAudio');

//     // Show/hide custom textarea based on radio button selection
//     difficultyRadios.forEach(radio => {
//         radio.addEventListener("change", function () {
//             if (this.value === "beginner") {
//                 wordCountInput.value = 10;
//                 wordCountInput.disabled = true;
//                 customTextArea.classList.add('hidden');
//             } else if (this.value === "intermediate") {
//                 wordCountInput.value = 25;
//                 wordCountInput.disabled = true;
//                 customTextArea.classList.add('hidden');
//             } else if (this.value === "advanced") {
//                 wordCountInput.disabled = false;
//                 customTextArea.classList.add('hidden');
//             } else if (this.value === "custom") {
//                 wordCountInput.disabled = true;
//                 customTextArea.classList.remove('hidden');
//                 expectedText = document.getElementById('referenceText').value || "";
//                 document.getElementById("displayText").textContent = expectedText;
//             }
//         });
//     });

//     // Initial check to set default state
//     const checkedRadio = document.querySelector('input[name="difficulty"]:checked');
//     if (checkedRadio) {
//         checkedRadio.dispatchEvent(new Event('change'));
//     }

//     document.getElementById("generateText").addEventListener("click", () => {
//         const wordCount = document.getElementById("wordCount").value;

//         fetch("/generate_text", {
//             method: "POST",
//             headers: { "Content-Type": "application/json" },
//             body: JSON.stringify({ word_count: parseInt(wordCount) })
//         })
//         .then(response => response.json())
//         .then(data => {
//             expectedText = data.text;
//             document.getElementById("displayText").textContent = expectedText;
//         })
//         .catch(error => console.error("Error fetching text:", error));
//     });

//     document.getElementById("startRecord").addEventListener("click", () => {
//         navigator.mediaDevices.getUserMedia({ audio: true })
//             .then(stream => {
//                 mediaRecorder = new MediaRecorder(stream);
//                 mediaRecorder.start();

//                 mediaRecorder.ondataavailable = event => {
//                     audioChunks.push(event.data);
//                 };

//                 startRecordButton.disabled = true;
//                 stopRecordButton.disabled = false;
//                 playAudioButton.disabled = true;
//                 analyzeAudioButton.disabled = true;
//             })
//             .catch(error => console.error("Error accessing microphone:", error));
//     });

//     document.getElementById("stopRecord").addEventListener("click", () => {
//         mediaRecorder.stop();
//         mediaRecorder.onstop = () => {
//             const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
//             const audioURL = URL.createObjectURL(audioBlob);
//             document.getElementById("audioPlayer").src = audioURL;

//             stopRecordButton.disabled = true;
//             startRecordButton.disabled = false;
//             playAudioButton.disabled = false;
//             analyzeAudioButton.disabled = false;
//         };
//     });

//     document.getElementById("playAudio").addEventListener("click", () => {
//         document.getElementById("audioPlayer").play();
//     });

//     document.getElementById("analyzeAudio").addEventListener("click", () => {
//         const name = document.getElementById('name').value.trim();
//         const email = document.getElementById('email').value.trim();
//         const selectedDifficulty = document.querySelector('input[name="difficulty"]:checked').value;

//         if (!name || !email) {
//             alert("Please enter both Name and Email before analyzing.");
//             return;
//         }

//         let textToAnalyze;
//         if (selectedDifficulty === "custom") {
//             textToAnalyze = document.getElementById('referenceText').value.trim();
//             if (!textToAnalyze) {
//                 alert("Please enter reference text for custom analysis.");
//                 return;
//             }
//             expectedText = textToAnalyze;
//         } else {
//             textToAnalyze = expectedText;
//         }

//         const formData = new FormData();
//         formData.append('name', name);
//         formData.append('email', email);
//         formData.append("audio", new Blob(audioChunks, { type: "audio/webm" }), "speech.webm");
//         formData.append("expected_text", textToAnalyze);

//         fetch("/analyze_audio", { method: "POST", body: formData })
//         .then(response => response.json())
//         .then(data => {
//             // Store all results in an object
//             const allResults = {
//                 google_raw: data.google_raw,
//                 google_custom: data.google_custom,
//                 vosk_raw: data.vosk_raw,
//                 vosk_custom: data.vosk_custom,
//                 whisper_raw: data.whisper_raw,
//                 whisper_custom: data.whisper_custom
//             };

//             // Update dropdown to show results based on selection
//             modelSelect.addEventListener('change', function() {
//                 const selectedModel = this.value;
//                 const modelResult = allResults[selectedModel] || { error: "No result for this model" };

//                 let resultHtml = `<strong>Results for ${selectedModel.replace('_', ' ').toUpperCase()}:</strong><br>`;
//                 if (modelResult.error) {
//                     resultHtml += `Error: ${modelResult.error}<br>`;
//                 } else {
//                     resultHtml += `Recognized Speech: ${modelResult.recognized_text || 'N/A'}<br>`;
//                     resultHtml += `Word Error Rate (WER): ${modelResult.wer || 'N/A'}<br>`;
//                     resultHtml += `Mispronounced Words: ${modelResult.mispronounced_words && modelResult.mispronounced_words.length ? modelResult.mispronounced_words.join(', ') : 'None'}<br>`;
//                     resultHtml += `Words Per Second (WPS): ${modelResult.wps || 'N/A'}<br>`;
//                     resultHtml += `Pace of the Speech: ${modelResult.pace || 'N/A'}<br>`;
//                 }

//                 resultDisplay.innerHTML = resultHtml;
//             }, { once: false }); // Ensure listener persists across multiple analyses

//             // Trigger dropdown change to show initial result
//             modelSelect.selectedIndex = 0;
//             modelSelect.dispatchEvent(new Event('change'));

//             // Reset recording state after analysis
//             resetRecordingState();
//         })
//         .catch(error => {
//             console.error("Error analyzing speech:", error);
//             resultDisplay.innerHTML = `<p>Error: ${error.message}</p>`;
//         });
//     });

//     // Function to reset recording state
//     function resetRecordingState() {
//         audioChunks = [];
//         document.getElementById("audioPlayer").src = "";
//         startRecordButton.disabled = false;
//         stopRecordButton.disabled = true;
//         playAudioButton.disabled = true;
//         analyzeAudioButton.disabled = true;
//     }
// });

let mediaRecorder;
let audioChunks = [];
let expectedText = "";

document.addEventListener("DOMContentLoaded", function () {
    const wordCountInput = document.getElementById("wordCount");
    const difficultyRadios = document.getElementsByName("difficulty");
    const customTextArea = document.getElementById('customTextArea');
    const modelSelect = document.getElementById('modelSelect');
    const resultDisplay = document.getElementById('resultDisplay');
    const startRecordButton = document.getElementById('startRecord');
    const stopRecordButton = document.getElementById('stopRecord');
    const playAudioButton = document.getElementById('playAudio');
    const analyzeAudioButton = document.getElementById('analyzeAudio');

    // Show/hide custom textarea based on radio button selection
    difficultyRadios.forEach(radio => {
        radio.addEventListener("change", function () {
            if (this.value === "beginner") {
                wordCountInput.value = 10;
                wordCountInput.disabled = true;
                customTextArea.classList.add('hidden');
            } else if (this.value === "intermediate") {
                wordCountInput.value = 25;
                wordCountInput.disabled = true;
                customTextArea.classList.add('hidden');
            } else if (this.value === "advanced") {
                wordCountInput.disabled = false;
                customTextArea.classList.add('hidden');
            } else if (this.value === "custom") {
                wordCountInput.disabled = true;
                customTextArea.classList.remove('hidden');
                expectedText = document.getElementById('referenceText').value || "";
                document.getElementById("displayText").textContent = expectedText;
            }
        });
    });

    // Initial check to set default state
    const checkedRadio = document.querySelector('input[name="difficulty"]:checked');
    if (checkedRadio) {
        checkedRadio.dispatchEvent(new Event('change'));
    }

    document.getElementById("generateText").addEventListener("click", () => {
        const wordCount = document.getElementById("wordCount").value;

        fetch("/generate_text", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ word_count: parseInt(wordCount) })
        })
        .then(response => response.json())
        .then(data => {
            expectedText = data.text;
            document.getElementById("displayText").textContent = expectedText;
        })
        .catch(error => console.error("Error fetching text:", error));
    });

    document.getElementById("startRecord").addEventListener("click", () => {
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                mediaRecorder = new MediaRecorder(stream);
                mediaRecorder.start();

                mediaRecorder.ondataavailable = event => {
                    audioChunks.push(event.data);
                };

                startRecordButton.disabled = true;
                stopRecordButton.disabled = false;
                playAudioButton.disabled = true;
                analyzeAudioButton.disabled = true;
            })
            .catch(error => console.error("Error accessing microphone:", error));
    });

    document.getElementById("stopRecord").addEventListener("click", () => {
        mediaRecorder.stop();
        mediaRecorder.onstop = () => {
            const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
            const audioURL = URL.createObjectURL(audioBlob);
            document.getElementById("audioPlayer").src = audioURL;

            stopRecordButton.disabled = true;
            startRecordButton.disabled = false;
            playAudioButton.disabled = false;
            analyzeAudioButton.disabled = false;
        };
    });

    document.getElementById("playAudio").addEventListener("click", () => {
        document.getElementById("audioPlayer").play();
    });

    document.getElementById("analyzeAudio").addEventListener("click", () => {
        const name = document.getElementById('name').value.trim();
        const email = document.getElementById('email').value.trim();
        const selectedDifficulty = document.querySelector('input[name="difficulty"]:checked').value;

        if (!name || !email) {
            alert("Please enter both Name and Email before analyzing.");
            return;
        }

        let textToAnalyze;
        if (selectedDifficulty === "custom") {
            textToAnalyze = document.getElementById('referenceText').value.trim();
            if (!textToAnalyze) {
                alert("Please enter reference text for custom analysis.");
                return;
            }
            expectedText = textToAnalyze;
        } else {
            textToAnalyze = expectedText;
        }

        const formData = new FormData();
        formData.append('name', name);
        formData.append('email', email);
        formData.append("audio", new Blob(audioChunks, { type: "audio/webm" }), "speech.webm");
        formData.append("expected_text", textToAnalyze);

        fetch("/analyze_audio", { method: "POST", body: formData })
        .then(response => response.json())
        .then(data => {
            // Store all results in an object
            const allResults = {
                google_raw: data.google_raw,
                google_custom: data.google_custom,
                vosk_raw: data.vosk_raw,
                vosk_custom: data.vosk_custom,
                whisper_raw: data.whisper_raw,
                whisper_custom: data.whisper_custom
            };

            // Update dropdown to show results based on selection
            modelSelect.addEventListener('change', function() {
                const selectedModel = this.value;
                const modelResult = allResults[selectedModel] || { error: "No result for this model" };

                let resultHtml = `<strong>Results for ${selectedModel.replace('_', ' ').toUpperCase()}:</strong><br>`;
                if (modelResult.error) {
                    resultHtml += `Error: ${modelResult.error}<br>`;
                } else {
                    resultHtml += `Recognized Speech: ${modelResult.recognized_text || 'N/A'}<br>`;
                    resultHtml += `Word Error Rate (WER): ${modelResult.wer || 'N/A'}<br>`;
                    resultHtml += `Character Error Rate (CER): ${modelResult.cer || 'N/A'}<br>`;
                    resultHtml += `Mispronounced Words: ${modelResult.mispronounced_words && modelResult.mispronounced_words.length ? modelResult.mispronounced_words.join(', ') : 'None'}<br>`;
                    resultHtml += `Words Per Second (WPS): ${modelResult.wps || 'N/A'}<br>`;
                    resultHtml += `Pace of the Speech: ${modelResult.pace || 'N/A'}<br>`;
                }

                resultDisplay.innerHTML = resultHtml;
            }, { once: false }); // Ensure listener persists across multiple analyses

            // Trigger dropdown change to show initial result
            modelSelect.selectedIndex = 0;
            modelSelect.dispatchEvent(new Event('change'));

            // Reset recording state after analysis
            resetRecordingState();
        })
        .catch(error => {
            console.error("Error analyzing speech:", error);
            resultDisplay.innerHTML = `<p>Error: ${error.message}</p>`;
        });
    });

    // Function to reset recording state
    function resetRecordingState() {
        audioChunks = [];
        document.getElementById("audioPlayer").src = "";
        startRecordButton.disabled = false;
        stopRecordButton.disabled = true;
        playAudioButton.disabled = true;
        analyzeAudioButton.disabled = true;
    }
});