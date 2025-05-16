let btn = document.getElementById("speechBtn");
let downloadBtn = document.getElementById("downloadBtn");
let textInput = document.querySelector("#textInput input");
let fileInput = document.getElementById("fileInput");
let radios = document.querySelectorAll("input[name='inputType']");
let msg = new SpeechSynthesisUtterance();
let audioBlob;

radios.forEach(radio => {
    radio.addEventListener("change", () => {
        if (radio.value === "text") {
            document.getElementById("textInput").style.display = "block";
            document.getElementById("fileInputContainer").style.display = "none";
        } else {
            document.getElementById("textInput").style.display = "none";
            document.getElementById("fileInputContainer").style.display = "block";
        } 
    });
});

btn.addEventListener("click", () => {
    let selectedType = document.querySelector("input[name='inputType']:checked").value;
    
    if (selectedType === "text" && textInput.value !== "") {
        msg.text = textInput.value;
        speakText(msg.text);
    } else if (selectedType === "file" && fileInput.files.length > 0) {
        let file = fileInput.files[0];
        let reader = new FileReader();
        reader.onload = function (e) {
            msg.text = e.target.result;
            speakText(msg.text);
        };
        reader.readAsText(file);
    } else {
        alert("Please enter text or upload a file.");
    }
});

function speakText(text) {
    msg.text = text;
    window.speechSynthesis.speak(msg);

    let audioContext = new AudioContext();
    let mediaStream = audioContext.createMediaStreamDestination();
    let mediaRecorder = new MediaRecorder(mediaStream.stream);
    mediaRecorder.ondataavailable = (e) => {
        audioBlob = e.data;
        downloadBtn.style.display = "block";
    };

    let audioSource = audioContext.createOscillator();
    audioSource.connect(mediaStream);
    audioSource.start();
    mediaRecorder.start();

    msg.onend = () => {
        mediaRecorder.stop();
    };
}

downloadBtn.addEventListener("click", () => {
    if (audioBlob) {
        let url = URL.createObjectURL(audioBlob);
        let a = document.createElement("a");
        a.href = url;
        a.download = "speech.mp3";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }
});
