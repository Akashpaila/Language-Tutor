let mediaRecorder;
let audioChunks = [];

document.getElementById("recordButton").addEventListener("click", async () => {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };

        mediaRecorder.start();
        document.getElementById("recordButton").disabled = true;
        document.getElementById("stopButton").disabled = false;
        document.getElementById("recordStatus").textContent = "Recording...";
    } catch (error) {
        alert("Error accessing microphone: " + error.message);
    }
});

document.getElementById("stopButton").addEventListener("click", () => {
    if (mediaRecorder && mediaRecorder.state === "recording") {
        mediaRecorder.stop();
        document.getElementById("recordButton").disabled = false;
        document.getElementById("stopButton").disabled = true;
        document.getElementById("recordStatus").textContent = "Idle";
    }
});

document.getElementById("loginForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    if (audioChunks.length === 0) {
        alert("Please record your voice before submitting.");
        return;
    }

    const formData = new FormData();
    formData.append("name", document.getElementById("name").value);
    formData.append("email", document.getElementById("email").value);
    const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
    formData.append("audio", audioBlob, "login_audio.webm");

    document.getElementById("recordStatus").textContent = "Processing...";

    try {
        const response = await fetch("/login", {
            method: "POST",
            body: formData
        });
        const result = await response.json();

        if (result.error) {
            alert(result.error);
        } else {
            alert(result.success);
            window.location.href = result.redirect;
        }
        document.getElementById("recordStatus").textContent = "Idle";
    } catch (error) {
        alert("Error logging in: " + error.message);
        document.getElementById("recordStatus").textContent = "Idle";
    }
});