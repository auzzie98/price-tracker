(function () {
  "use strict";

  var END_DATE = new Date(2026, 10, 23, 12, 0, 0);
  var states = new WeakMap();

  function getDates(count, range) {
    var dates = [];
    var end = new Date(END_DATE);

    for (var i = 0; i < count; i++) {
      var date = new Date(end);
      if (range === "1d") {
        date.setMinutes(0, 0, 0);
        date.setHours(24 * i / count);
      } else if (range === "1w") {
        date = new Date(end);
        date.setDate(end.getDate() - (count - 1 - i));
        date.setHours(9 + Math.round((i % 9) * 0.25));
      } else if (range === "1m") {
        date = new Date(end);
        date.setDate(end.getDate() - (count - 1 - i));
      } else if (range === "1y") {
        date = new Date(end);
        date.setDate(end.getDate() - Math.round((count - 1 - i) * 365 / (count - 1)));
      } else {
        date = new Date(end);
        date.setMonth(end.getMonth() - Math.round((count - 1 - i) * 36 / (count - 1)));
      }
      dates.push(date);
    }
    return dates;
  }

  function formatDate(date, range) {
    if (range === "1d") {
      return date.toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit" });
    }
    if (range === "1w") {
      return date.toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric" }) +
        ", " + date.toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit" });
    }
    return date.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
  }

  function formatAxisDate(date, range) {
    if (range === "1d") {
      return date.toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit" });
    }
    if (range === "1w") {
      return date.toLocaleDateString("en-US", { weekday: "short" });
    }
    if (range === "1m") {
      return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
    }
    if (range === "1y") {
      return date.toLocaleDateString("en-US", { month: "short" });
    }
    return date.toLocaleDateString("en-US", { month: "short", year: "numeric" });
  }

  function createTooltip(canvas) {
    var tooltip = document.createElement("div");
    tooltip.className = "chart-tooltip";
    tooltip.setAttribute("role", "tooltip");
    canvas.parentElement.appendChild(tooltip);
    return tooltip;
  }

  function drawSmoothLine(ctx, points) {
    if (!points.length) return;
    ctx.beginPath();
    ctx.moveTo(points[0].x, points[0].y);
    for (var i = 1; i < points.length - 1; i++) {
      var midpointX = (points[i].x + points[i + 1].x) / 2;
      var midpointY = (points[i].y + points[i + 1].y) / 2;
      ctx.quadraticCurveTo(points[i].x, points[i].y, midpointX, midpointY);
    }
    var last = points[points.length - 1];
    ctx.quadraticCurveTo(points[points.length - 2].x, points[points.length - 2].y, last.x, last.y);
  }

  function attach(options) {
    var canvas = options.canvas;
    var state = states.get(canvas) || {};
    state.canvas = canvas;
    state.values = options.values || [];
    state.range = options.range || "1m";
    state.priceElement = options.priceElement || null;
    state.tooltip = state.tooltip || createTooltip(canvas);
    state.hoverIndex = null;
    state.hovered = false;
    states.set(canvas, state);
    if (state.priceElement && state.values.length) {
      state.priceElement.textContent = "$" + state.values[state.values.length - 1].toFixed(2);
    }

    if (!state.listenersAttached) {
      canvas.addEventListener("pointermove", function (event) {
        handlePointer(event, state);
      });
      canvas.addEventListener("pointerdown", function (event) {
        if (event.pointerType === "touch") {
          event.preventDefault();
          handlePointer(event, state);
        }
      });
      canvas.addEventListener("pointerleave", function () {
        clearHover(state);
      });
      canvas.addEventListener("pointerup", function (event) {
        if (event.pointerType === "touch") {
          handlePointer(event, state);
        }
      });
      canvas.addEventListener("pointercancel", function () {
        clearHover(state);
      });
      state.listenersAttached = true;
    }

    draw(state);
  }

  function clearHover(state) {
    state.hovered = false;
    state.hoverIndex = null;
    state.tooltip.classList.remove("visible");
    if (state.priceElement && state.values.length) {
      state.priceElement.textContent = "$" + state.values[state.values.length - 1].toFixed(2);
    }
    draw(state);
  }

  function handlePointer(event, state) {
    if (!state.values.length) return;
    var rect = state.canvas.getBoundingClientRect();
    var cssX = event.clientX - rect.left;
    var cssWidth = rect.width;
    var plotWidth = Math.max(1, cssWidth - 72);
    var clampedX = Math.max(0, Math.min(plotWidth, cssX));
    var index = Math.round(clampedX / plotWidth * (state.values.length - 1));
    index = Math.max(0, Math.min(state.values.length - 1, index));
    state.hoverIndex = index;
    state.hovered = true;

    if (state.priceElement) {
      state.priceElement.textContent = "$" + state.values[index].toFixed(2);
    }

    var dates = getDates(state.values.length, state.range);
    var point = layout(state)[index];
    state.tooltip.innerHTML =
      "<strong>$" + state.values[index].toFixed(2) + "</strong>" +
      "<span>" + formatDate(dates[index], state.range) + "</span>";

    var tooltipWidth = 170;
    var tooltipLeft = point.x + 12 + (state.canvas.offsetLeft || 0);
    if (tooltipLeft + tooltipWidth > cssWidth - 4) {
      tooltipLeft = point.x - tooltipWidth - 12;
    }
    tooltipLeft = Math.max(4, tooltipLeft);
    var tooltipTop = Math.max(8, point.y - 74 + (state.canvas.offsetTop || 0));
    state.tooltip.style.left = tooltipLeft + "px";
    state.tooltip.style.top = tooltipTop + "px";
    state.tooltip.classList.add("visible");
    draw(state);
  }

  function layout(state) {
    var canvas = state.canvas;
    var cssWidth = Math.max(1, canvas.clientWidth || canvas.offsetWidth);
    var cssHeight = 300;
    var values = state.values;
    var dataMin = Math.min.apply(null, values);
    var dataMax = Math.max.apply(null, values);
    var range = dataMax - dataMin;
    if (range === 0) range = Math.abs(dataMax) * 0.1 || 1;
    var chartMin = dataMin - range * 0.08;
    var chartMax = dataMax + range * 0.08;
    var chartRange = chartMax - chartMin;
    var plotWidth = Math.max(1, cssWidth - 72);
    var plotHeight = cssHeight - 44;

    function x(index) {
      if (values.length === 1) return plotWidth / 2;
      return index / (values.length - 1) * plotWidth;
    }
    function y(value) {
      return 12 + (chartMax - value) / chartRange * plotHeight;
    }

    var points = values.map(function (value, index) {
      return { x: x(index), y: y(value), value: value };
    });
    return points;
  }

  function draw(state) {
    var canvas = state.canvas;
    var values = state.values;
    if (!canvas || !values.length) return;

    var dpr = window.devicePixelRatio || 1;
    var width = Math.max(1, canvas.clientWidth || canvas.offsetWidth);
    var height = 300;
    canvas.width = Math.round(width * dpr);
    canvas.height = Math.round(height * dpr);

    var ctx = canvas.getContext("2d");
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = "#000000";
    ctx.fillRect(0, 0, width, height);

    var points = layout(state);
    var startingValue = values[0];
    var endValue = values[values.length - 1];
    var lineColor = Math.round(endValue * 100) < Math.round(startingValue * 100)
      ? "#00C805"
      : Math.round(endValue * 100) > Math.round(startingValue * 100)
        ? "#FF5000"
        : "#9CA3AF";

    ctx.save();
    ctx.beginPath();
    points.forEach(function (point, index) {
      if (index === 0) ctx.moveTo(point.x, point.y);
      else ctx.lineTo(point.x, point.y);
    });
    ctx.lineTo(points[points.length - 1].x, height - 32);
    ctx.lineTo(points[0].x, height - 32);
    ctx.closePath();
    var gradient = ctx.createLinearGradient(0, 12, 0, height - 32);
    gradient.addColorStop(0, lineColor === "#00C805" ? "rgba(0,200,5,0.22)" : lineColor === "#FF5000" ? "rgba(255,80,0,0.22)" : "rgba(156,163,175,0.12)");
    gradient.addColorStop(1, "rgba(0,0,0,0)");
    ctx.fillStyle = gradient;
    ctx.fill();
    ctx.restore();

    ctx.lineWidth = state.hovered ? 3 : 2;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    for (var i = 0; i < points.length - 1; i++) {
      var segment = [points[i], points[i + 1]];
      var endCents = Math.round(values[i + 1] * 100);
      var startCents = Math.round(startingValue * 100);
      ctx.beginPath();
      ctx.moveTo(segment[0].x, segment[0].y);
      var controlX = (segment[0].x + segment[1].x) / 2;
      var controlY = (segment[0].y + segment[1].y) / 2;
      ctx.quadraticCurveTo(controlX, segment[0].y, controlX, controlY);
      ctx.quadraticCurveTo(controlX, segment[1].y, segment[1].x, segment[1].y);
      ctx.strokeStyle = endCents < startCents ? "#00C805" : endCents > startCents ? "#FF5000" : "#9CA3AF";
      ctx.stroke();
    }

    if (state.hovered && state.hoverIndex !== null) {
      var point = points[state.hoverIndex];
      ctx.save();
      ctx.strokeStyle = "#9CA3AF";
      ctx.setLineDash([4, 4]);
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(point.x, 12);
      ctx.lineTo(point.x, height - 32);
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.beginPath();
      ctx.arc(point.x, point.y, 5, 0, Math.PI * 2);
      ctx.fillStyle = lineColor;
      ctx.fill();
      ctx.strokeStyle = "#FFFFFF";
      ctx.lineWidth = 2;
      ctx.stroke();
      ctx.restore();
    }

    var dataMin = Math.min.apply(null, values);
    var dataMax = Math.max.apply(null, values);
    var range = dataMax - dataMin;
    if (range === 0) range = Math.abs(dataMax) * 0.1 || 1;
    var chartMin = dataMin - range * 0.08;
    var chartMax = dataMax + range * 0.08;
    ctx.fillStyle = "#9CA3AF";
    ctx.font = "12px Arial";
    ctx.textAlign = "left";
    ctx.textBaseline = "middle";
    ctx.fillText("$" + chartMax.toFixed(2), width - 62, 12);
    ctx.fillText("$" + ((chartMin + chartMax) / 2).toFixed(2), width - 62, height / 2);
    ctx.fillText("$" + chartMin.toFixed(2), width - 62, height - 44);

    var dates = getDates(values.length, state.range);
    var labelIndexes = [0, Math.round((values.length - 1) * 0.25), Math.round((values.length - 1) * 0.5), Math.round((values.length - 1) * 0.75), values.length - 1];
    ctx.font = "11px Arial";
    ctx.textBaseline = "middle";
    labelIndexes.forEach(function (index, position) {
      var point = points[index];
      ctx.textAlign = position === 0 ? "left" : position === labelIndexes.length - 1 ? "right" : "center";
      ctx.fillText(formatAxisDate(dates[index], state.range), point.x, height - 12);
    });
  }

  window.PriceTrackerChart = {
    attach: attach,
    draw: function (canvas, values, range, priceElement) {
      attach({ canvas: canvas, values: values, range: range, priceElement: priceElement });
    }
  };
})();
