document.addEventListener('DOMContentLoaded', function () {
    const strategyForm = document.getElementById('strategyForm');
    const strategyType = document.getElementById('strategyType');

    // Set default dates
    const today = new Date();
    const threeYearsAgo = new Date(today.getFullYear() - 3, today.getMonth(), today.getDate());
    document.getElementById('startDate').value = threeYearsAgo.toISOString().split('T')[0];
    document.getElementById('endDate').value = today.toISOString().split('T')[0];

    // Show/hide strategy specific parameters based on selection
    strategyType.addEventListener('change', function () {
        const hamiltonianParams = document.getElementById('hamiltonianParams');
        const momentumParams = document.getElementById('momentumParams');
        const meanReversionParams = document.getElementById('meanReversionParams');

        // Hide all parameter sections first
        [hamiltonianParams, momentumParams, meanReversionParams].forEach(section => {
            if (section) section.style.display = 'none';
        });

        // Show selected strategy parameters
        switch (this.value) {
            case 'hamiltonian':
                if (hamiltonianParams) hamiltonianParams.style.display = 'block';
                break;
            case 'momentum':
                if (momentumParams) momentumParams.style.display = 'block';
                break;
            case 'meanReversion':
                if (meanReversionParams) meanReversionParams.style.display = 'block';
                break;
        }
    });

    strategyForm.addEventListener('submit', async function (e) {
        e.preventDefault();
        console.log("Form submitted"); // Debug log

        const params = {
            strategy_type: strategyType.value,
            symbol: document.getElementById('stockSymbol').value.toUpperCase(),
            start_date: document.getElementById('startDate').value,
            end_date: document.getElementById('endDate').value,
            initial_capital: parseFloat(document.getElementById('initialCapital').value),
        };

        // Add strategy-specific parameters
        switch (strategyType.value) {
            case 'hamiltonian':
                params.damping = parseFloat(document.getElementById('damping').value);
                params.external_influence = parseFloat(document.getElementById('externalInfluence').value);
                params.friction = parseFloat(document.getElementById('friction').value);
                break;
            case 'momentum':
                params.lookback_period = parseInt(document.getElementById('lookbackPeriod')?.value || 20);
                params.threshold = parseFloat(document.getElementById('momentumThreshold')?.value || 0);
                break;
            case 'meanReversion':
                params.window = parseInt(document.getElementById('window')?.value || 20);
                params.std_dev = parseFloat(document.getElementById('stdDev')?.value || 2.0);
                break;
        }

        try {
            console.log("Sending request with params:", params); // Debug log
            const response = await fetch('/run_strategy', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(params)
            });

            const results = await response.json();
            console.log("Received results:", results); // Debug log

            if (response.ok) {
                updateResults(results);
                plotCharts(results);
            } else {
                alert(`Strategy failed: ${results.error}`);
            }
        } catch (error) {
            console.error("Error:", error); // Debug log
            alert('Error running strategy');
        }
    });

    function plotCharts(results) {
        console.log("Plotting charts with data:", results);

        try {
            // Plot equity curve with stock price comparison
            const equityTrace = {
                x: results.dates,
                y: results.equity_curve,
                type: 'scatter',
                mode: 'lines',
                name: 'Portfolio Value',
                yaxis: 'y2'
            };

            const stockTrace = {
                x: results.stock_data.dates,
                y: results.stock_data.prices,
                type: 'scatter',
                mode: 'lines',
                name: 'Stock Price',
                yaxis: 'y1'
            };

            const equityLayout = {
                title: 'Portfolio Value vs Stock Price',
                yaxis: {
                    title: 'Stock Price ($)',
                    side: 'left'
                },
                yaxis2: {
                    title: 'Portfolio Value ($)',
                    side: 'right',
                    overlaying: 'y'
                },
                xaxis: { title: 'Date' }
            };

            Plotly.newPlot('equityCurve', [stockTrace, equityTrace], equityLayout);

            // Plot trading signals
            const priceTrace = {
                x: results.dates,
                y: results.prices,
                type: 'scatter',
                mode: 'lines',
                name: 'Price'
            };

            const buyTrace = {
                x: results.buy_dates,
                y: results.buy_prices,
                type: 'scatter',
                mode: 'markers',
                name: 'Buy',
                marker: {
                    color: 'green',
                    size: 10,
                    symbol: 'triangle-up'
                }
            };

            const sellTrace = {
                x: results.sell_dates,
                y: results.sell_prices,
                type: 'scatter',
                mode: 'markers',
                name: 'Sell',
                marker: {
                    color: 'red',
                    size: 10,
                    symbol: 'triangle-down'
                }
            };

            const volumeTrace = {
                x: results.stock_data.dates,
                y: results.stock_data.volume,
                type: 'bar',
                name: 'Volume',
                yaxis: 'y2'
            };

            const priceLayout = {
                title: 'Price and Trading Signals',
                yaxis: { title: 'Price ($)' },
                yaxis2: {
                    title: 'Volume',
                    overlaying: 'y',
                    side: 'right'
                },
                xaxis: { title: 'Date' }
            };

            Plotly.newPlot('priceChart', [priceTrace, buyTrace, sellTrace, volumeTrace], priceLayout);
        } catch (error) {
            console.error("Error plotting charts:", error);
            alert('Error plotting charts. Check console for details.');
        }
    }

    function updateResults(results) {
        // Update metrics display
        if (results.metrics) {
            document.getElementById('totalReturn').textContent =
                `${results.metrics['Total Return'].toFixed(2)}%`;
            document.getElementById('annualReturn').textContent =
                `${results.metrics['Annual Return'].toFixed(2)}%`;
            document.getElementById('sharpeRatio').textContent =
                results.metrics['Sharpe Ratio'].toFixed(2);
            document.getElementById('maxDrawdown').textContent =
                `${results.metrics['Max Drawdown'].toFixed(2)}%`;
        }
    }
}); 