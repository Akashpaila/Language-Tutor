let recognition;
let isRecording = false;

const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");
const transcriptArea = document.getElementById("transcript");
const checkGrammarBtn = document.getElementById("checkGrammarBtn");
const resultDiv = document.getElementById("grammarResult");

if ('webkitSpeechRecognition' in window) {
    recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onresult = (event) => {
        const transcript = Array.from(event.results)
            .map(result => result[0].transcript)
            .join('');
        transcriptArea.value += transcript.trim() + " ";
    };

    recognition.onerror = (e) => {
        console.error("Speech recognition error:", e);
    };
} else {
    alert("Your browser does not support Web Speech API");
}

startBtn.addEventListener("click", () => {
    if (recognition && !isRecording) {
        transcriptArea.value = "";
        recognition.start();
        isRecording = true;
        startBtn.disabled = true;
        stopBtn.disabled = false;
    }
});

stopBtn.addEventListener("click", () => {
    if (recognition && isRecording) {
        recognition.stop();
        isRecording = false;
        startBtn.disabled = false;
        stopBtn.disabled = true;
    }
});

checkGrammarBtn.addEventListener("click", async () => {
    const text = transcriptArea.value.trim();
    if (!text) {
        alert("Please provide some transcribed text.");
        return;
    }

    const response = await fetch("/check_grammar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text })
    });

    const result = await response.json();
    resultDiv.innerHTML = `
        <h3>Suggestions:</h3>
        <ul>
            ${result.matches.map(m => `<li><strong>${m.rule}</strong>: ${m.message}</li>`).join("")}
        </ul>
        <h3>Corrected Text:</h3>
        <p>${result.corrected}</p>
    `;
});
