// Price Tracker chart component, Task 8 and Task 9.
// One component, TradingView Lightweight Charts, line and area series only.
// Same component for dollar charts and index charts.
// The only difference is the vertical axis label and the data source.

// Initialize Lightweight Chart for index data
// chartId: canvas element id
// chartName: category name (CPUs, GPUs, RAM)
// range: time range (1D, 1W, 1M, 1Y)
function initIndexChart(chartId, chartName, range) {
  // Check if LightweightCharts is available
  if (typeof LightweightCharts === 'undefined') {
    // Show placeholder if LightweightCharts not loaded yet
    const chart = LightweightCharts.createChart({
      container: chartId,
      style: 'dark',
      locale: 'en',
      rightToLeft: false,
      grid: {
        vertLines: true,
        horzLines: false,
        gridLineColor: '#29372F',
        leftOffset: 0,
        rightOffset: 0
      },
      leftScale: { visible: false },
      rightScale: { visible: false },
      crosshair: { mode: 'normal' },
      volume: { visible: false }
    });
    chart.addTextAnnotation({
      text: 'No data yet',
      position: 'center',
      color: '#666666',
      isTransparent: true
    });
    return;
  }
  
  const chartConfig = {
    container: chartId,
    style: 'dark',
    locale: 'en',
    rightToLeft: false,
    grid: {
      vertLines: true,
      horzLines: false,
      gridLineColor: '#29372F',
      leftOffset: 10,
      rightOffset: 10
    },
    leftScale: {
      visible: true,
      color: '#F4F8F5',
      scaleMargins: { top: 0.1, bottom: 0.1 }
    },
    rightScale: {
      visible: false
    },
    crosshair: {
      mode: 'normal'
    },
    volume: { visible: false }
  };
  
  // Store chart config for later update when data arrives
  window.lightweightChartConfigs = window.lightweightChartConfigs || {};
  window.lightweightChartConfigs[chartId] = chartConfig;
}

// Update index chart with data points
function updateIndexChart(chartId, dataPoints) {
  // Check if LightweightCharts is available
  if (typeof LightweightCharts === 'undefined') return;
  
  const chartConfig = window.lightweightChartConfigs && window.lightweightChartConfigs[chartId];
  if (!chartConfig) return;
  
  const chart = LightweightCharts.createChart(chartConfig);
  
  if (dataPoints && dataPoints.length > 0) {
    const traces = dataPoints.map(function(dp) {
      return {
        time: dp.period,
        value: dp.index_value
      };
    });
    chart.setMarks(traces);
  } else {
    // No data - show placeholder
    chart.addTextAnnotation({
      text: 'No data yet',
      position: 'center',
      color: '#666666',
      isTransparent: true
    });
  }
}
