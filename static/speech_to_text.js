// let recordBtn = document.getElementById("recordBtn");
// let stopBtn = document.getElementById("stopBtn");
// let convertBtn = document.getElementById("convertBtn");
// let transcribedText = document.getElementById("transcribedText");
// let downloadBtn = document.getElementById("downloadBtn");
// let recognition;
// let audioBlob;

// // Audio Recording with Web Speech API
// recordBtn.onclick = () => {
//     recognition = new webkitSpeechRecognition();
//     recognition.lang = "en-US";
//     recognition.continuous = true;
//     recognition.interimResults = false;

//     recognition.onresult = (event) => {
//         let transcript = event.results[0][0].transcript;
//         transcribedText.value = transcript;
//         downloadBtn.style.display = "block";
//     };

//     recognition.start();
//     recordBtn.style.display = "none";
//     stopBtn.style.display = "inline-block";
// };

// stopBtn.onclick = () => {
//     recognition.stop();
//     recordBtn.style.display = "inline-block";
//     stopBtn.style.display = "none";
// };

// // Upload File
// convertBtn.onclick = () => {
//     let file = document.getElementById("fileInput").files[0];
//     if (file) {
//         let reader = new FileReader();
//         reader.readAsDataURL(file);
//         reader.onload = () => {
//             fetch("https://api.whisper.ai/v1/transcribe", {
//                 method: "POST",
//                 headers: { "Content-Type": "application/json" },
//                 body: JSON.stringify({ audio: reader.result }),
//             })
//                 .then((res) => res.json())
//                 .then((data) => {
//                     transcribedText.value = data.text;
//                     downloadBtn.style.display = "block";
//                 });
//         };
//     }
// };

// // Download Text
// downloadBtn.onclick = () => {
//     let blob = new Blob([transcribedText.value], { type: "text/plain" });
//     let url = URL.createObjectURL(blob);
//     let a = document.createElement("a");
//     a.href = url;
//     a.download = "transcription.txt";
//     a.click();
// };


// let recordBtn = document.getElementById("recordBtn");
// let stopBtn = document.getElementById("stopBtn");
// let convertBtn = document.getElementById("convertBtn");
// let transcribedText = document.getElementById("transcribedText");
// let downloadBtn = document.getElementById("downloadBtn");
// let recognition;

// let inputRadios = document.querySelectorAll("input[name='inputType']");
// let recordContainer = document.getElementById("recordContainer");
// let uploadContainer = document.getElementById("uploadContainer");
// let linkContainer = document.getElementById("linkContainer");

// inputRadios.forEach((radio) => {
//     radio.addEventListener("change", () => {
//         recordContainer.style.display = "none";
//         uploadContainer.style.display = "none";
//         linkContainer.style.display = "none";

//         if (radio.value === "record") {
//             recordContainer.style.display = "block";
//         } else if (radio.value === "upload") {
//             uploadContainer.style.display = "block";
//         } else if (radio.value === "link") {
//             linkContainer.style.display = "block";
//         }
//     });
// });

// recordBtn.onclick = () => {
//     recognition = new webkitSpeechRecognition();
//     recognition.lang = "en-US";
//     recognition.continuous = true;
//     recognition.interimResults = false;

//     recognition.onresult = (event) => {
//         let transcript = event.results[0][0].transcript;
//         transcribedText.value = transcript;
//         downloadBtn.style.display = "block";
//     };

//     recognition.start();
//     recordBtn.style.display = "none";
//     stopBtn.style.display = "inline-block";
// };

// stopBtn.onclick = () => {
//     recognition.stop();
//     recordBtn.style.display = "inline-block";
//     stopBtn.style.display = "none";
// };

// convertBtn.onclick = () => {
//     let file = document.getElementById("fileInput").files[0];
//     if (file) {
//         let reader = new FileReader();
//         reader.onload = () => {
//             transcribedText.value = "File uploaded: " + file.name;
//             downloadBtn.style.display = "block";
//         };
//         reader.readAsDataURL(file);
//     } else {
//         alert("Please upload an audio file.");
//     }
// };

// downloadBtn.onclick = () => {
//     let blob = new Blob([transcribedText.value], { type: "text/plain" });
//     let url = URL.createObjectURL(blob);
//     let a = document.createElement("a");
//     a.href = url;
//     a.download = "transcription.txt";
//     a.click();
// };


let recordBtn = document.getElementById("recordBtn");
let stopBtn = document.getElementById("stopBtn");
let convertBtn = document.getElementById("convertBtn");
let transcribedText = document.getElementById("transcribedText");
let downloadBtn = document.getElementById("downloadBtn");
let inputRadios = document.querySelectorAll("input[name='inputType']");
let recordContainer = document.getElementById("recordContainer");
let uploadContainer = document.getElementById("uploadContainer");
let linkContainer = document.getElementById("linkContainer");
let recognition;

// inputRadios.forEach((radio) => {
//     radio.addEventListener("change", () => {
//         recordContainer.style.display = "none";
//         uploadContainer.style.display = "none";
//         linkContainer.style.display = "none";

//         if (radio.value === "record") {
//             recordContainer.style.display = "block";
//         } else if (radio.value === "upload") {
//             uploadContainer.style.display = "block";
//         } else if (radio.value === "link") {
//             linkContainer.style.display = "block";
//         }
//     });
// });

recordBtn.onclick = () => {
    recognition = new webkitSpeechRecognition();
    recognition.lang = "en-US";
    recognition.continuous = true;
    recognition.interimResults = false;

    recognition.onresult = (event) => {
        let transcript = event.results[0][0].transcript;
        transcribedText.value = transcript;
        downloadBtn.style.display = "block";
    };

    recognition.start();
    recordBtn.style.display = "none";
    stopBtn.style.display = "inline-block";
};

stopBtn.onclick = () => {
    recognition.stop();
    recordBtn.style.display = "inline-block";
    stopBtn.style.display = "none";
};

// convertBtn.onclick = async () => {
//     let file = document.getElementById("fileInput").files[0];
//     let link = document.getElementById("audioLink").value;

//     if (file) {
//         await transcribeAudio(file);
//     } else if (link) {
//         await transcribeLink(link);
//     } else {
//         alert("Please upload a file or enter a link.");
//     }
// };

async function transcribeAudio(file) {
    let formData = new FormData();
    formData.append("file", file);
    formData.append("model", "whisper-1");

    let response = await fetch("https://api.openai.com/v1/audio/transcriptions", {
        method: "POST",
        headers: {
            // uncomment the below line as it is being blocked by the github to upload as this is the api key.
            // Authorization: `Bearer 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`
        },
        body: formData,
    });

    let data = await response.json();
    transcribedText.value = data.text;
    downloadBtn.style.display = "block";
}

async function transcribeLink(link) {
    let response = await fetch(link);
    let blob = await response.blob();
    let file = new File([blob], "audio.mp3", { type: blob.type });
    await transcribeAudio(file);
}

downloadBtn.onclick = () => {
    let blob = new Blob([transcribedText.value], { type: "text/plain" });
    let url = URL.createObjectURL(blob);
    let a = document.createElement("a");
    a.href = url;
    a.download = "transcription.txt";
    a.click();
};
