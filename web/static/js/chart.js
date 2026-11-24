(function () {
  "use strict";

  var END_DATE = new Date(2026, 10, 23, 12, 0, 0);
  var states = new WeakMap();

  function getDates(count, range) {
    var dates = [];
    for (var i = 0; i < count; i++) {
      var date = new Date(END_DATE);
      if (range === "1d") {
        date.setHours(9);
        date.setMinutes(Math.round(i * 900 / (count - 1)));
      } else if (range === "1w") {
        date.setDate(END_DATE.getDate() - 6 + i);
        date.setHours(9 + (i % 9));
      } else if (range === "1m") {
        date.setDate(END_DATE.getDate() - 22 + i);
      } else if (range === "1y") {
        date.setDate(END_DATE.getDate());
        date.setMonth(END_DATE.getMonth() - 11 + Math.floor(i * 11 / (count - 1)));
      } else {
        date.setMonth(END_DATE.getMonth() - 35 + Math.floor(i * 35 / (count - 1)));
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

  function segmentColor(value, startValue) {
    var valueCents = Math.round(value * 100);
    var startCents = Math.round(startValue * 100);
    if (valueCents < startCents) return "#00C805";
    return "#FF5000";
  }

  function createTooltip(canvas) {
    var tooltip = document.createElement("div");
    tooltip.className = "chart-tooltip";
    tooltip.setAttribute("role", "tooltip");
    canvas.parentElement.appendChild(tooltip);
    return tooltip;
  }

  function createSinglePointNote(canvas) {
    var note = document.createElement("p");
    note.className = "chart-single-point-note";
    canvas.parentElement.appendChild(note);
    return note;
  }

  function layout(state) {
    var canvas = state.canvas;
    var width = Math.max(1, canvas.clientWidth || canvas.offsetWidth);
    var height = 300;
    var values = state.values;
    var dataMin = Math.min.apply(null, values);
    var dataMax = Math.max.apply(null, values);
    var spread = dataMax - dataMin;
    if (spread === 0) spread = Math.abs(dataMax) * 0.1 || 1;
    var chartMin = dataMin - spread * 0.08;
    var chartMax = dataMax + spread * 0.08;
    var plotWidth = Math.max(1, width - 96);
    var plotHeight = height - 44;

    return values.map(function (value, index) {
      var x = values.length === 1 ? plotWidth : index / (values.length - 1) * plotWidth;
      var y = 12 + (chartMax - value) / (chartMax - chartMin) * plotHeight;
      return { x: x, y: y, value: value };
    });
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
    var startValue = values[0];
    var endValue = values[values.length - 1];
    var lineColor = endValue < startValue ? "#00C805" : "#FF5000";

    if (values.length === 1) {
      var flatY = points[0].y;
      ctx.beginPath();
      ctx.moveTo(0, flatY);
      ctx.lineTo(points[0].x, flatY);
      ctx.strokeStyle = "#9CA3AF";
      ctx.lineWidth = state.hovered ? 3 : 2;
      ctx.lineCap = "butt";
      ctx.lineJoin = "miter";
      ctx.stroke();

      ctx.beginPath();
      ctx.arc(points[0].x, flatY, 5, 0, Math.PI * 2);
      ctx.fillStyle = lineColor;
      ctx.fill();
      ctx.strokeStyle = "#FFFFFF";
      ctx.lineWidth = 2;
      ctx.stroke();
    }

    if (values.length > 1) {
      ctx.beginPath();
      ctx.moveTo(points[0].x, points[0].y);
      for (var i = 1; i < points.length; i++) {
        ctx.lineTo(points[i].x, points[i].y);
      }
      ctx.lineTo(points[points.length - 1].x, height - 32);
      ctx.lineTo(points[0].x, height - 32);
      ctx.closePath();
      var gradient = ctx.createLinearGradient(0, 12, 0, height - 32);
      gradient.addColorStop(0, lineColor === "#00C805" ? "rgba(0,200,5,0.28)" : "rgba(255,80,0,0.28)");
      gradient.addColorStop(1, "rgba(0,0,0,0)");
      ctx.fillStyle = gradient;
      ctx.fill();
    } else {
      ctx.beginPath();
      ctx.moveTo(0, points[0].y);
      ctx.lineTo(points[0].x, points[0].y);
      ctx.lineTo(points[0].x, height - 32);
      ctx.lineTo(0, height - 32);
      ctx.closePath();
      ctx.fillStyle = lineColor === "#00C805" ? "rgba(0,200,5,0.18)" : "rgba(255,80,0,0.18)";
      ctx.fill();
    }

    ctx.lineWidth = state.hovered ? 3 : 2;
    ctx.lineCap = "butt";
    ctx.lineJoin = "miter";
    if (state.dates && state.dates.length === values.length && values.length === 2) {
      var baselinePoint = points[0];
      var approvedPoint = points[1];
      ctx.beginPath();
      ctx.moveTo(baselinePoint.x, baselinePoint.y);
      ctx.lineTo(approvedPoint.x, baselinePoint.y);
      ctx.strokeStyle = values[0] < startValue ? "#00C805" : values[0] > startValue ? "#FF5000" : "#9CA3AF";
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(approvedPoint.x, baselinePoint.y);
      ctx.lineTo(approvedPoint.x, approvedPoint.y);
      ctx.strokeStyle = values[1] < startValue ? "#00C805" : values[1] > startValue ? "#FF5000" : "#9CA3AF";
      ctx.stroke();
    }

    for (var segmentIndex = 0; values.length > 1 && !(state.dates && state.dates.length === values.length && values.length === 2) && segmentIndex < points.length - 1; segmentIndex++) {
      var first = points[segmentIndex];
      var second = points[segmentIndex + 1];
      var firstCents = Math.round(first.value * 100);
      var secondCents = Math.round(second.value * 100);
      var startCents = Math.round(startValue * 100);
      ctx.beginPath();
      ctx.moveTo(first.x, first.y);

      if ((firstCents < startCents && secondCents > startCents) ||
          (firstCents > startCents && secondCents < startCents)) {
        var fraction = (startCents - firstCents) / (secondCents - firstCents);
        var crossingX = first.x + (second.x - first.x) * fraction;
        var crossingY = first.y + (second.y - first.y) * fraction;
        ctx.lineTo(crossingX, crossingY);
        ctx.strokeStyle = firstCents < startCents ? "#00C805" : "#FF5000";
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(crossingX, crossingY);
        ctx.lineTo(second.x, second.y);
        ctx.strokeStyle = secondCents < startCents ? "#00C805" : "#FF5000";
        ctx.stroke();
      } else {
        ctx.lineTo(second.x, second.y);
        ctx.strokeStyle = segmentColor(second.value, startValue);
        ctx.stroke();
      }
    }

    var dataMin = Math.min.apply(null, values);
    var dataMax = Math.max.apply(null, values);
    var spread = dataMax - dataMin;
    if (spread === 0) spread = Math.abs(dataMax) * 0.1 || 1;
    var chartMin = dataMin - spread * 0.08;
    var chartMax = dataMax + spread * 0.08;
    ctx.fillStyle = "#9CA3AF";
    ctx.font = "12px Arial";
    ctx.textAlign = "left";
    ctx.textBaseline = "middle";
    ctx.fillText("$" + chartMax.toFixed(2), width - 88, 12);
    ctx.fillText("$" + ((chartMin + chartMax) / 2).toFixed(2), width - 88, height / 2);
    ctx.fillText("$" + chartMin.toFixed(2), width - 88, height - 44);

    var currentY = points[points.length - 1].y;
    ctx.fillStyle = lineColor;
    ctx.fillRect(width - 112, currentY - 12, 100, 24);
    ctx.fillStyle = "#FFFFFF";
    ctx.font = "bold 12px Arial";
    ctx.textAlign = "center";
    // Offset further left so price tag doesn't overlap y-axis label or the rightmost dot
    var priceX = width - 72;
    ctx.fillText("$" + endValue.toFixed(2), priceX, currentY + 4);

    var dates = state.dates && state.dates.length === values.length
      ? state.dates.map(function (date) { return new Date(date + "T12:00:00"); })
      : getDates(values.length, state.range);
    var labelIndexes = state.range === "1d"
      ? [0, Math.round((values.length - 1) * 0.333), Math.round((values.length - 1) * 0.667), values.length - 1]
      : state.range === "1m"
        ? [0]
        : [0, Math.round((values.length - 1) * 0.25), Math.round((values.length - 1) * 0.5), Math.round((values.length - 1) * 0.75), values.length - 1];
    // Draw x-axis labels: 4-5 labels for "all" range, spaced properly, inside chart area
    ctx.fillStyle = "#9CA3AF";
    ctx.font = "11px Arial";
    ctx.textBaseline = "middle";

    // Determine which label indices to show, limiting "all" range to 5 labels max
    var actualLabelIndexes;
    if (state.range === "all") {
      // For "all" range, show at most 5 labels spread evenly across the data
      var maxLabels = 5;
      if (values.length <= maxLabels) {
        actualLabelIndexes = labelIndexes;
      } else {
        // Calculate evenly-spaced indices
        var step = (values.length - 1) / (maxLabels - 1);
        actualLabelIndexes = [];
        for (var i = 0; i < maxLabels; i++) {
          actualLabelIndexes.push(Math.round(i * step));
        }
      }
    } else {
      actualLabelIndexes = labelIndexes;
    }

    if (state.range === "1m") {
      var monthLabels = ["Nov 1", "Nov 8", "Nov 15", "Nov 22"];
      var monthFractions = [0.03, 0.31, 0.59, 0.87];
      monthLabels.forEach(function (text, position) {
        var xPos = monthFractions[position] * (width - 96);
        ctx.textAlign = position === 0 ? "left" : position === monthLabels.length - 1 ? "right" : "center";
        ctx.fillText(text, xPos, height - 12);
      });
    } else {
      actualLabelIndexes.forEach(function (index, position) {
      var point = points[index];
      // For "all" range, ensure last label stays inside chart area (not at extreme right edge)
      var xPos;
      if (state.range === "all" && position === actualLabelIndexes.length - 1) {
        // Place last label inside, at least 12px from right edge
        var plotWidthForLabels = width - 96; // same as layout plotWidth
        xPos = Math.max(12, Math.min(plotWidthForLabels - 12, point.x));
        ctx.textAlign = "center";
      } else {
        ctx.textAlign = position === 0 ? "left" : position === actualLabelIndexes.length - 1 ? "right" : "center";
        xPos = point.x;
      }
      var text = values.length === 1
        ? "Nov 23"
        : state.range === "1d"
        ? ["9 AM", "12 PM", "3 PM", "6 PM"][position]
        : formatAxisDate(dates[index], state.range);
      ctx.fillText(text, xPos, height - 12);
      });
    }

    if (state.hovered && state.hoverIndex !== null) {
      var hoverPoint = points[state.hoverIndex];
      ctx.save();
      ctx.strokeStyle = "#9CA3AF";
      ctx.setLineDash([4, 4]);
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(hoverPoint.x, 12);
      ctx.lineTo(hoverPoint.x, height - 32);
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.beginPath();
      ctx.arc(hoverPoint.x, hoverPoint.y, 5, 0, Math.PI * 2);
      ctx.fillStyle = segmentColor(hoverPoint.value, startValue);
      ctx.fill();
      ctx.strokeStyle = "#FFFFFF";
      ctx.lineWidth = 2;
      ctx.stroke();
      ctx.restore();
    }

    if (values.length === 1) {
      state.singlePointNote.textContent =
        "Only 1 data point so far, more points will appear as you approve receipts.";
      state.singlePointNote.classList.add("visible");
    } else {
      state.singlePointNote.textContent = "";
      state.singlePointNote.classList.remove("visible");
    }
  }

  function clearHover(state) {
    state.hovered = false;
    state.hoverIndex = null;
    state.tooltip.classList.remove("visible");
    if (state.priceElement && state.values.length) {
      state.priceElement.textContent = "$" + state.values[state.values.length - 1].toFixed(2);
    }
    if (state.hoverDateElement) state.hoverDateElement.textContent = "";
    draw(state);
  }

  function handlePointer(event, state) {
    if (!state.values.length) return;
    var rect = state.canvas.getBoundingClientRect();
    var cssX = event.clientX - rect.left;
    var plotWidth = Math.max(1, rect.width - 96);
    var clampedX = Math.max(0, Math.min(plotWidth, cssX));
    var index = Math.round(clampedX / plotWidth * (state.values.length - 1));
    index = Math.max(0, Math.min(state.values.length - 1, index));
    state.hoverIndex = index;
    state.hovered = true;

    if (state.priceElement) state.priceElement.textContent = "$" + state.values[index].toFixed(2);
    var dates = state.dates && state.dates.length === state.values.length
      ? state.dates.map(function (date) { return new Date(date + "T12:00:00"); })
      : getDates(state.values.length, state.range);
    var dateText = formatDate(dates[index], state.range);
    if (state.hoverDateElement) state.hoverDateElement.textContent = dateText;

    var point = layout(state)[index];
    state.tooltip.innerHTML =
      "<strong>$" + state.values[index].toFixed(2) + "</strong>" +
      "<span>" + dateText + "</span>";
    var tooltipWidth = 170;
    var left = point.x + 12 + (state.canvas.offsetLeft || 0);
    if (left + tooltipWidth > rect.width - 4) left = point.x - tooltipWidth - 12;
    left = Math.max(4, left);
    var top = Math.max(8, point.y - 74 + (state.canvas.offsetTop || 0));
    state.tooltip.style.left = left + "px";
    state.tooltip.style.top = top + "px";
    state.tooltip.classList.add("visible");
    draw(state);
  }

  function attach(options) {
    var canvas = options.canvas;
    var state = states.get(canvas) || {};
    state.canvas = canvas;
    state.values = options.values || [];
    state.range = options.range || "1m";
    state.priceElement = options.priceElement || null;
    state.hoverDateElement = options.hoverDateElement || null;
    state.dates = options.dates || null;
    state.tooltip = state.tooltip || createTooltip(canvas);
    state.singlePointNote = state.singlePointNote || createSinglePointNote(canvas);
    state.hoverIndex = null;
    state.hovered = false;
    states.set(canvas, state);

    if (!state.listenersAttached) {
      canvas.addEventListener("pointermove", function (event) { handlePointer(event, state); });
      canvas.addEventListener("pointerdown", function (event) {
        if (event.pointerType === "touch") {
          event.preventDefault();
          handlePointer(event, state);
        }
      });
      canvas.addEventListener("pointerleave", function () { clearHover(state); });
      canvas.addEventListener("pointerup", function (event) {
        if (event.pointerType === "touch") handlePointer(event, state);
      });
      canvas.addEventListener("pointercancel", function () { clearHover(state); });
      state.listenersAttached = true;
    }

    if (state.priceElement && state.values.length) {
      state.priceElement.textContent = "$" + state.values[state.values.length - 1].toFixed(2);
    }
    draw(state);
  }

  window.PriceTrackerChart = {
    attach: attach,
    draw: function (canvas, values, range, priceElement, hoverDateElement, dates) {
      attach({
        canvas: canvas,
        values: values,
        range: range,
        priceElement: priceElement,
        hoverDateElement: hoverDateElement,
        dates: dates
      });
    }
  };
})();
