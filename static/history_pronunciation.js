document.addEventListener('DOMContentLoaded', () => {
    const historyContainer = document.getElementById('history-container');
    const dateFilter = document.getElementById('date-filter');
    const rangeFilter = document.getElementById('range-filter');
    let charts = {};

    function fetchHistory() {
        const feature = 'pronunciation';
        const selectedDate = dateFilter.value;
        const range = rangeFilter.value;

        fetch('/get_history', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ feature })
        })
        .then(response => response.json())
        .then(data => {
            historyContainer.innerHTML = '';
            let filteredHistory = data.history;

            if (selectedDate) {
                const selectedDateObj = new Date(selectedDate);
                if (range === 'day') {
                    filteredHistory = data.history.filter(item => {
                        const itemDate = new Date(item.timestamp);
                        return itemDate.toDateString() === selectedDateObj.toDateString();
                    });
                } else if (range === 'week') {
                    const weekStart = new Date(selectedDateObj);
                    weekStart.setDate(selectedDateObj.getDate() - selectedDateObj.getDay());
                    const weekEnd = new Date(weekStart);
                    weekEnd.setDate(weekStart.getDate() + 6);
                    filteredHistory = data.history.filter(item => {
                        const itemDate = new Date(item.timestamp);
                        return itemDate >= weekStart && itemDate <= weekEnd;
                    });
                }
            }

            // filteredHistory.forEach(item => {
            //     const itemDiv = document.createElement('div');
            //     itemDiv.className = 'history-item';
            //     itemDiv.innerHTML = `
            //         <p><strong>Date:</strong> ${new Date(item.timestamp).toLocaleString()}</p>
            //         <p><strong>Sentence:</strong> ${item.details.sentence}</p>
            //         <p><strong>WER:</strong> ${item.details.wer}</p>
            //         <p><strong>WPS:</strong> ${item.details.wps}</p>
            //         <p><strong>CER:</strong> ${item.details.cer || 'N/A'}</p>
            //         <button class="visualize-btn" data-id="${item.id}">Visualize</button>
            //         <div class="graph-container" id="graph-${item.id}" style="display: none;">
            //             <canvas id="canvas-${item.id}"></canvas>
            //         </div>`;
            //     historyContainer.appendChild(itemDiv);
            // });

            // Aggregate data for graphs
            const labels = filteredHistory.map(item => new Date(item.timestamp).toLocaleDateString());
            const werData = filteredHistory.map(item => item.details.wer);
            const wpsData = filteredHistory.map(item => item.details.wps);
            const cerData = filteredHistory.map(item => item.details.cer || 0);

            // Update graphs
            if (charts['aggregate']) {
                charts['aggregate'].destroy();
            }
            const aggregateCanvas = document.createElement('canvas');
            aggregateCanvas.id = 'aggregate-canvas';
            const aggregateContainer = document.createElement('div');
            aggregateContainer.className = 'graph-container';
            aggregateContainer.appendChild(aggregateCanvas);
            historyContainer.insertBefore(aggregateContainer, historyContainer.firstChild);

            charts['aggregate'] = new Chart(aggregateCanvas, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'WER',
                            data: werData,
                            borderColor: '#7c3aed',
                            backgroundColor: 'rgba(124, 58, 237, 0.2)',
                            fill: true
                        },
                        {
                            label: 'WPS',
                            data: wpsData,
                            borderColor: '#10b981',
                            backgroundColor: 'rgba(16, 185, 129, 0.2)',
                            fill: true
                        },
                        {
                            label: 'CER',
                            data: cerData,
                            borderColor: '#3b82f6',
                            backgroundColor: 'rgba(59, 130, 246, 0.2)',
                            fill: true
                        }
                    ]
                },
                options: {
                    scales: {
                        y: { beginAtZero: true }
                    },
                    plugins: {
                        legend: { display: true }
                    }
                }
            });

            document.querySelectorAll('.visualize-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    const id = btn.getAttribute('data-id');
                    const graphContainer = document.getElementById(`graph-${id}`);
                    const canvas = document.getElementById(`canvas-${id}`);
                    graphContainer.style.display = graphContainer.style.display === 'none' ? 'block' : 'none';

                    if (graphContainer.style.display === 'block' && !charts[id]) {
                        const item = filteredHistory.find(h => h.id == id);
                        charts[id] = new Chart(canvas, {
                            type: 'bar',
                            data: {
                                labels: ['WER', 'WPS', 'CER'],
                                datasets: [{
                                    label: 'Metrics',
                                    data: [item.details.wer, item.details.wps, item.details.cer || 0],
                                    backgroundColor: ['#7c3aed', '#10b981', '#3b82f6'],
                                    borderColor: ['#5b21b6', '#059669', '#1e40af'],
                                    borderWidth: 1
                                }]
                            },
                            options: {
                                scales: {
                                    y: { beginAtZero: true, max: Math.max(item.details.wer, item.details.wps, item.details.cer || 1) }
                                },
                                plugins: {
                                    legend: { display: false }
                                }
                            }
                        });
                    }
                });
            });
        })
        .catch(error => {
            console.error('Error fetching history:', error);
            historyContainer.innerHTML = '<p>Error loading history.</p>';
        });
    }

    dateFilter.addEventListener('change', fetchHistory);
    rangeFilter.addEventListener('change', fetchHistory);
    fetchHistory();
});