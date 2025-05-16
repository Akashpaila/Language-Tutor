document.addEventListener('DOMContentLoaded', () => {
    const youtubeInput = document.getElementById('youtubeInput');
    const localInput = document.getElementById('localInput');
    const radioButtons = document.querySelectorAll('input[name="inputType"]');

    radioButtons.forEach(radio => {
        radio.addEventListener('change', () => {
            if (radio.value === 'youtube') {
                youtubeInput.classList.remove('hidden');
                localInput.classList.add('hidden');
            } else {
                youtubeInput.classList.add('hidden');
                localInput.classList.remove('hidden');
            }
        });
    });
});

function transcribe() {
    const inputType = document.querySelector('input[name="inputType"]:checked').value;
    const loading = document.getElementById('loading');
    const result = document.getElementById('result');
    const error = document.getElementById('error');
    const transcribedText = document.getElementById('transcribedText');
    const translatedText = document.getElementById('translatedText');
    const summarizedText = document.getElementById('summarizedText');

    // Reset UI
    loading.classList.remove('hidden');
    result.classList.add('hidden');
    error.classList.add('hidden');
    transcribedText.textContent = '';
    translatedText.innerHTML = '';
    summarizedText.innerHTML = '';
    error.textContent = '';

    if (inputType === 'youtube') {
        const urlInput = document.getElementById('youtubeUrl').value;
        if (!urlInput) {
            loading.classList.add('hidden');
            error.textContent = 'Please enter a YouTube URL';
            error.classList.remove('hidden');
            return;
        }

        fetch('/transcribe_youtube', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: urlInput }),
        })
        .then(response => response.json())
        .then(data => {
            loading.classList.add('hidden');
            if (data.error) {
                error.textContent = data.error;
                error.classList.remove('hidden');
            } else {
                transcribedText.textContent = data.transcription;
                result.classList.remove('hidden');
            }
        })
        .catch(err => {
            loading.classList.add('hidden');
            error.textContent = 'An error occurred while transcribing the video.';
            error.classList.remove('hidden');
            console.error('Fetch error:', err);
        });
    } else {
        const fileInput = document.getElementById('localFile');
        const file = fileInput.files[0];
        if (!file) {
            loading.classList.add('hidden');
            error.textContent = 'Please select a file';
            error.classList.remove('hidden');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        fetch('/transcribe_local', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            loading.classList.add('hidden');
            if (data.error) {
                error.textContent = data.error;
                error.classList.remove('hidden');
            } else {
                transcribedText.textContent = data.transcription;
                result.classList.remove('hidden');
            }
        })
        .catch(err => {
            loading.classList.add('hidden');
            error.textContent = 'An error occurred while transcribing the file.';
            error.classList.remove('hidden');
            console.error('Fetch error:', err);
        });
    }
}

function translateText() {
    const transcribedText = document.getElementById('transcribedText').textContent;
    const targetLanguage = document.getElementById('targetLanguage').value;
    const loading = document.getElementById('loading');
    const translatedText = document.getElementById('translatedText');
    const error = document.getElementById('error');

    // Reset UI
    loading.classList.remove('hidden');
    translatedText.classList.add('hidden');
    error.classList.add('hidden');
    error.textContent = '';

    fetch('/translate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: transcribedText, target_lang: targetLanguage }),
    })
    .then(response => response.json())
    .then(data => {
        loading.classList.add('hidden');
        if (data.error) {
            error.textContent = data.error;
            error.classList.remove('hidden');
        } else {
            let tableHtml = '<table><tr><th>Original (English)</th><th>Translated</th></tr>';
            data.translations.forEach(translation => {
                tableHtml += `<tr><td>${translation.original}</td><td>${translation.translated}</td></tr>`;
            });
            tableHtml += '</table>';
            translatedText.innerHTML = tableHtml;
            translatedText.classList.remove('hidden');
        }
    })
    .catch(err => {
        loading.classList.add('hidden');
        error.textContent = 'An error occurred while translating the text.';
        error.classList.remove('hidden');
        console.error('Fetch error:', err);
    });
}

function summarizeText() {
    const transcribedText = document.getElementById('transcribedText').textContent;
    const loading = document.getElementById('loading');
    const summarizedText = document.getElementById('summarizedText');
    const error = document.getElementById('error');

    // Reset UI
    loading.classList.remove('hidden');
    summarizedText.classList.add('hidden');
    error.classList.add('hidden');
    error.textContent = '';

    fetch('/summarize', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: transcribedText }),
    })
    .then(response => response.json())
    .then(data => {
        loading.classList.add('hidden');
        if (data.error) {
            error.textContent = data.error;
            error.classList.remove('hidden');
        } else {
            summarizedText.innerHTML = `<h3>Summary</h3><p>${data.summary}</p>`;
            summarizedText.classList.remove('hidden');
        }
    })
    .catch(err => {
        loading.classList.add('hidden');
        error.textContent = 'An error occurred while summarizing the text.';
        error.classList.remove('hidden');
        console.error('Fetch error:', err);
    });
}

function downloadText() {
    const text = document.getElementById('transcribedText').textContent;
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'transcription.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

