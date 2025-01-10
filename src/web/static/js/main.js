document.addEventListener('DOMContentLoaded', function () {
    const uploadForm = document.getElementById('uploadForm');
    const configForm = document.getElementById('configForm');

    // Handle file upload
    uploadForm.addEventListener('submit', async function (e) {
        e.preventDefault();

        const formData = new FormData();
        const fileInput = document.getElementById('dataFile');
        formData.append('file', fileInput.files[0]);

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            if (response.ok) {
                alert('File uploaded successfully');
                runBacktest(fileInput.files[0].name);
            } else {
                alert(`Upload failed: ${result.error}`);
            }
        } catch (error) {
            alert('Error uploading file');
        }
    });

    async function runBacktest(filename) {
        const formData = new FormData();
        formData.append('filename', filename);
        formData.append('initialCapital', document.getElementById('initialCapital').value);
        formData.append('stopLoss', document.getElementById('stopLoss').value);
        formData.append('takeProfit', document.getElementById('takeProfit').value);

        try {
            const response = await fetch('/backtest', {
                method: 'POST',
                body: formData
            });

            const results = await response.json();
            if (response.ok) {
                updateResults(results);
            } else {
                alert(`Backtest failed: ${results.error}`);
            }
        } catch (error) {
            alert('Error running backtest');
        }
    }

    function updateResults(results) {
        // Update statistics
        document.getElementById('totalReturn').textContent =
            `${(results.total_return * 100).toFixed(2)}%`;
        document.getElementById('winRate').textContent =
            `${(results.win_rate * 100).toFixed(2)}%`;
        document.getElementById('maxDrawdown').textContent =
            `${(results.max_drawdown * 100).toFixed(2)}%`;
        document.getElementById('totalTrades').textContent =
            results.total_trades;

        // Plot equity curve
        const trace = {
            y: results.equity_curve,
            type: 'scatter',
            mode: 'lines',
            name: 'Equity Curve'
        };

        const layout = {
            title: 'Equity Curve',
            yaxis: { title: 'Portfolio Value' },
            xaxis: { title: 'Trade Number' }
        };

        Plotly.newPlot('equityCurve', [trace], layout);
    }
}); 