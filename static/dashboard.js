document.addEventListener('DOMContentLoaded', () => {
    const featureFilter = document.getElementById('feature-filter');
    const historyContainer = document.getElementById('history-container');
    let charts = {};

    function fetchHistory(feature = 'all') {
        fetch('/get_history', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ feature })
        })
        .then(response => response.json())
        // .then(data => {
        //     historyContainer.innerHTML = '';
        //     data.history.forEach(item => {
        //         const itemDiv = document.createElement('div');
        //         itemDiv.className = 'history-item';
        //         let detailsHtml = '';
        //         if (item.feature === 'pronunciation') {
        //             detailsHtml = `<p>Sentence: ${item.details.sentence}</p>
        //                           <p>WER: ${item.details.wer}</p>
        //                           <p>WPS: ${item.details.wps}</p>
        //                           <button class="visualize-btn" data-id="${item.id}">Visualize</button>
        //                           <div class="graph-container" id="graph-${item.id}" style="display: none;">
        //                               <canvas id="canvas-${item.id}"></canvas>
        //                           </div>`;
        //         } else if (item.feature === 'grammar') {
        //             detailsHtml = `<p>Text: ${item.details.text}</p>
        //                           <p>Corrections: ${item.details.corrections}</p>`;
        //         } else if (item.feature === 'conversation') {
        //             detailsHtml = `<p>Topic: ${item.details.topic}</p>
        //                           <p>Response: ${item.details.response}</p>`;
        //         } else if (item.feature === 'accent') {
        //             detailsHtml = `<p>Accent: ${item.details.accent}</p>
        //                           <p>Exercise: ${item.details.exercise}</p>`;
        //         } else if (item.feature === 'youtube') {
        //             detailsHtml = `<p>URL: ${item.details.url}</p>
        //                           <p>Transcription: ${item.details.transcription}</p>`;
        //         } else if (item.feature === 'speech_to_text') {
        //             detailsHtml = `<p>Transcription: ${item.details.transcription}</p>`;
        //         } else if (item.feature === 'text_to_speech') {
        //             detailsHtml = item.details.target_lang
        //                 ? `<p>Text: ${item.details.text}</p>
        //                    <p>Target Language: ${item.details.target_lang}</p>`
        //                 : `<p>Text: ${item.details.text}</p>
        //                    <p>Summary: ${item.details.summary}</p>`;
        //         }
            //     itemDiv.innerHTML = `<p><strong>${item.feature.charAt(0).toUpperCase() + item.feature.slice(1)}</strong>: ${new Date(item.timestamp).toLocaleString()}</p>
            //                         ${detailsHtml}`;
            //     historyContainer.appendChild(itemDiv);
            // });

            // document.querySelectorAll('.visualize-btn').forEach(btn => {
            //     btn.addEventListener('click', () => {
            //         const id = btn.getAttribute('data-id');
            //         const graphContainer = document.getElementById(`graph-${id}`);
            //         const canvas = document.getElementById(`canvas-${id}`);
            //         graphContainer.style.display = graphContainer.style.display === 'none' ? 'block' : 'none';

            //         if (graphContainer.style.display === 'block' && !charts[id]) {
            //             const item = data.history.find(h => h.id == id);
            //             charts[id] = new Chart(canvas, {
            //                 type: 'bar',
            //                 data: {
            //                     labels: ['WER', 'WPS'],
            //                     datasets: [{
            //                         label: 'Metrics',
            //                         data: [item.details.wer, item.details.wps],
            //                         backgroundColor: ['#7c3aed', '#10b981'],
            //                         borderColor: ['#5b21b6', '#059669'],
            //                         borderWidth: 1
            //                     }]
            //                 },
            //                 options: {
            //                     scales: {
            //                         y: { beginAtZero: true, max: Math.max(item.details.wer, item.details.wps, 1) }
            //                     },
            //                     plugins: {
            //                         legend: { display: false }
            //                     }
            //                 }
            //             });
            //         }
            //     });
            // });
        // })
        .catch(error => {
            console.error('Error fetching history:', error);
            historyContainer.innerHTML = '<p>Error loading history.</p>';
        });
    }

    featureFilter.addEventListener('change', () => {
        fetchHistory(featureFilter.value);
        Object.values(charts).forEach(chart => chart.destroy());
        charts = {};
    });

    fetchHistory();
});