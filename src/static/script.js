document.addEventListener("DOMContentLoaded", () => {
    const chartContainer = document.getElementById("trading-chart");
    let chart = null;
    let candlestickSeries = null;

    // --- Chart Initialization ---
    function initializeChart() {
        if (!chartContainer || typeof LightweightCharts === "undefined") {
            console.error("Chart container or LightweightCharts library not found.");
            return;
        }
        try {
            chart = LightweightCharts.createChart(chartContainer, {
                width: chartContainer.clientWidth,
                height: chartContainer.clientHeight, // Use container height
                layout: {
                    background: { color: "#131722" }, // Dark background
                    textColor: "#d1d4dc", // Light text
                },
                grid: {
                    vertLines: { color: "#2a2e39" },
                    horzLines: { color: "#2a2e39" },
                },
                crosshair: { mode: LightweightCharts.CrosshairMode.Normal },
                rightPriceScale: { borderColor: "#474d57" },
                timeScale: {
                    borderColor: "#474d57",
                    timeVisible: true,
                    secondsVisible: false, // Assuming daily/hourly data initially
                },
            });

            candlestickSeries = chart.addSeries({
                type: "candlestick",
                upColor: "#00b894", downColor: "#e74c3c",
                borderDownColor: "#e74c3c", borderUpColor: "#00b894",
                wickDownColor: "#e74c3c", wickUpColor: "#00b894",
            });

            // Handle chart resizing
            const resizeObserver = new ResizeObserver(entries => {
                const { width, height } = entries[0].contentRect;
                chart.resize(width, height);
            });
            resizeObserver.observe(chartContainer);

            console.log("Trading chart initialized.");
            if(chartContainer) chartContainer.innerHTML = "<p style='color: #d1d4dc;'>Carregando dados do gráfico...</p>"; // Loading message
            fetchChartData(); // Fetch data from backend
        } catch (error) {
            console.error("Error initializing chart:", error);
            if(chartContainer) chartContainer.innerHTML = "<p style=	color: red;	>Erro ao inicializar o gráfico.</p>";
        }
    }

    // --- Fetch Chart Data --- 
    async function fetchChartData(asset = "BTC/USD") { // Default asset
        if (!candlestickSeries) {
            console.error("Candlestick series not initialized.");
            return;
        }
        console.log(`Fetching chart data for ${asset}...`);
        try {
            // Use URLSearchParams for query parameters
            const params = new URLSearchParams({ asset: asset });
            const response = await fetch(`/api/chart-data?${params.toString()}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data && data.length > 0) {
                console.log(`Received ${data.length} data points. Setting chart data.`);
                candlestickSeries.setData(data);
                // Optional: Fit content after setting data
                // chart.timeScale().fitContent(); 
            } else {
                console.warn("Received empty data array from backend.");
                candlestickSeries.setData([]); // Clear chart if no data
            }
        } catch (error) {
            console.error("Error fetching or processing chart data:", error);
            // Display error message in the chart area
             if(chartContainer) chartContainer.innerHTML = `<p style="color: orange;">Erro ao carregar dados do gráfico: ${error.message}</p>`;
        }
    }

    // --- UI Element References ---
    const startButton = document.getElementById("start-button");
    const stopButton = document.getElementById("stop-button");
    const configPanel = document.getElementById("config-panel");
    const statusPanel = document.getElementById("status-panel");
    const resultModal = document.getElementById("result-modal");
    const modalOkButton = document.getElementById("modal-ok-button");
    const modalMessage = document.getElementById("modal-message");
    const balanceElement = document.querySelector(".balance"); // For updating balance display
    const currentPnlElement = document.querySelector("#config-panel .current-pnl");
    const livePnlElement = document.querySelector("#status-panel .live-pnl");

    // --- Event Listeners ---
    if (startButton) {
        startButton.addEventListener("click", handleStartOperation);
    }
    if (stopButton) {
        stopButton.addEventListener("click", handleStopOperation);
    }
    if (modalOkButton) {
        modalOkButton.addEventListener("click", () => {
            if(resultModal) resultModal.style.display = "none";
        });
    }

    // --- UI State Functions ---
    function showConfigPanel() {
        if(configPanel) configPanel.style.display = "flex";
        if(statusPanel) statusPanel.style.display = "none";
    }

    function showStatusPanel() {
        if(configPanel) configPanel.style.display = "none";
        if(statusPanel) statusPanel.style.display = "flex";
    }

    function showModal(message, isError = false) {
        if(modalMessage) {
            modalMessage.innerHTML = message.replace(/\n/g, "<br>"); // Replace newline chars with <br> for HTML
        }
        if(resultModal) {
             resultModal.style.display = "flex";
             const modalHeader = resultModal.querySelector(".modal-header span");
             const modalContent = resultModal.querySelector(".modal-content");
             if(modalHeader) modalHeader.textContent = isError ? "⚠️ Erro" : "📈 Resultado";
             if(modalContent) {
                modalContent.className = isError ? "modal-content error" : "modal-content success";
             } 
        }
    }

    // --- Backend Interaction ---
    async function handleStartOperation() {
        console.log("Start button clicked");
        startButton.disabled = true; // Disable button during request
        startButton.textContent = "Processando...";

        // 1. Get and Validate parameters
        const aiModel = document.getElementById("ai-model")?.value;
        const strategy = document.getElementById("strategy")?.value;
        const entryValueElement = document.getElementById("entry-value");
        const targetValueElement = document.getElementById("target-value");
        const stopLossElement = document.getElementById("stop-loss");

        const entryValue = parseFloat(entryValueElement?.value);
        const targetValue = parseFloat(targetValueElement?.value);
        const stopLoss = parseFloat(stopLossElement?.value);
        const asset = document.querySelector(".asset-selector .asset-name")?.textContent || "BTC/USD";

        // Basic Validations
        if (isNaN(entryValue) || entryValue <= 0) {
            showModal("Erro de Validação: O Valor de entrada deve ser um número positivo.", true);
            startButton.disabled = false;
            startButton.textContent = "▷ INICIAR";
            return;
        }
        if (isNaN(targetValue) || targetValue <= 0) {
            showModal("Erro de Validação: A Meta deve ser um número positivo.", true);
            startButton.disabled = false;
            startButton.textContent = "▷ INICIAR";
            return;
        }
        if (isNaN(stopLoss) || stopLoss <= 0) {
            showModal("Erro de Validação: O Stop Loss deve ser um número positivo.", true);
            startButton.disabled = false;
            startButton.textContent = "▷ INICIAR";
            return;
        }
        if (targetValue <= entryValue) {
            showModal("Erro de Validação: A Meta deve ser maior que o Valor de entrada.", true);
            startButton.disabled = false;
            startButton.textContent = "▷ INICIAR";
            return;
        }

        const params = { asset, aiModel, strategy, entryValue, targetValue, stopLoss };
        console.log("Parameters:", params);

        // 2. Update UI to show status (optional, maybe wait for backend confirmation)
        // showStatusPanel(); 
        // Update status panel fields if switching immediately
        // ... (code to update status fields)

        // 3. Call backend API
        try {
            const response = await fetch("/api/start_backtest", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(params),
            });
            const result = await response.json();
            console.log("Backend response:", result);

            if (result.success) {
                // 4. Handle successful backtest completion
                let successMsg = result.message || "Backtest concluído com sucesso.";
                if (result.stats) {
                    // Display some key stats
                    const stats = result.stats;
                    successMsg += `\nRetorno Final: ${stats["Return [%]"]?.toFixed(2)}%`;
                    successMsg += ` | Trades: ${stats["# Trades"]}`;
                    successMsg += ` | Win Rate: ${stats["Win Rate [%]"]?.toFixed(2)}%`;
                }
                if (result.plot_warning) {
                    successMsg += `\n\nAviso Gráfico: ${result.plot_warning}`;
                }
                showModal(successMsg);
                // Optionally update chart with trade markers if backend provides them
                // Optionally display link to the plot HTML
                if(result.plot_path) {
                     console.log("Plot available at:", result.plot_path);
                     // You could add a link or button to view the plot
                }
            } else {
                // 5. Handle error from backend
                showModal(`Erro no backtest: ${result.error || "Erro desconhecido"}`, true);
            }
        } catch (error) {
            console.error("Error calling backend:", error);
            showModal(`Erro de comunicação: ${error.message}`, true);
        } finally {
            // 6. Re-enable button and reset text, stay on config panel for now
            startButton.disabled = false;
            startButton.textContent = "▷ INICIAR";
            showConfigPanel(); // Stay on config panel to allow new runs
        }
    }

    function handleStopOperation() {
        console.log("Stop button clicked - Functionality not implemented yet");
        // TODO: Implement logic to stop the ongoing operation (call backend API)
        showModal("Função PARAR ainda não implementada.", true);
        // showConfigPanel(); // Switch back to config panel if needed
    }
    
    // --- Initial Balance Fetch (Example) ---
    async function fetchInitialBalance() {
        // This endpoint doesn't exist yet in the modified routes, add if needed
        /*
        try {
            const response = await fetch("/api/balance");
            const data = await response.json();
            if (data.formatted_balance && balanceElement) {
                balanceElement.textContent = data.formatted_balance;
            }
        } catch (error) {
            console.error("Error fetching initial balance:", error);
            if(balanceElement) balanceElement.textContent = "Erro";
        }
        */
       if(balanceElement) balanceElement.textContent = "R$ 10.000,00 (Simulado)"; // Placeholder
    }

    // --- Initialize ---
    initializeChart();
    showConfigPanel(); // Show config panel by default
    fetchInitialBalance(); // Fetch initial balance
});

