let mediaRecorder;
let audioChunks = [];

// Start recording audio
function startRecording() {
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.start();

            audioChunks = [];
            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                const audioFile = new File([audioBlob], 'recorded_audio.webm', { type: 'audio/webm' });
                uploadAudio(audioFile);
            };

            alert("Recording started...");
        })
        .catch(error => alert("Error accessing microphone: " + error));
}

// Stop recording audio
function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== "inactive") {
        mediaRecorder.stop();
        alert("Recording stopped.");
    } else {
        alert("No active recording.");
    }
}

// Upload audio for analysis
function uploadAudio(audioFile) {
    const formData = new FormData();
    formData.append("audio", audioFile);

    const expectedText = document.getElementById("textInput").value.trim();
    if (expectedText) {
        formData.append("expected_text", expectedText);
    }

    fetch("/analyze_audio", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => displayResults(data))
    .catch(error => alert("Error analyzing audio: " + error));
}

// Analyze uploaded text and audio
function analyzeOwnText() {
    const textInput = document.getElementById("textInput").value.trim();
    const textFile = document.getElementById("textFile").files[0];
    const audioFile = document.getElementById("audioFile").files[0];

    if (!textInput && !textFile) {
        alert("Please enter text or upload a text file.");
        return;
    }

    const formData = new FormData();

    if (textInput) {
        formData.append("expected_text", textInput);
    }

    if (textFile) {
        const reader = new FileReader();
        reader.onload = function (e) {
            formData.append("expected_text", e.target.result);
            if (audioFile) {
                formData.append("audio", audioFile);
            }
            sendAnalysisRequest(formData);
        };
        reader.readAsText(textFile);
    } else {
        if (audioFile) {
            formData.append("audio", audioFile);
        }
        sendAnalysisRequest(formData);
    }
}

// Send request to backend for analysis
function sendAnalysisRequest(formData) {
    fetch("/analyze_audio", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => displayResults(data))
    .catch(error => alert("Error analyzing data: " + error));
}

// Display results
function displayResults(data) {
    const resultDiv = document.getElementById("result");
    if (data.error) {
        resultDiv.innerHTML = `<p style="color: red;">Error: ${data.error}</p>`;
        return;
    }

    resultDiv.innerHTML = `
        <h3>Analysis Results:</h3>
        <p><strong>Recognized Text:</strong> ${data.recognized_text || 'N/A'}</p>
        <p><strong>Word Error Rate (WER):</strong> ${data.wer}</p>
        <p><strong>Mispronounced Words:</strong> ${data.mispronounced_words.join(", ") || 'None'}</p>
        <p><strong>Speech Rate (Words per Second):</strong> ${data.wps}</p>
    `;
}
