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
    var plotWidth = Math.max(1, width - 72);
    var plotHeight = height - 44;

    return values.map(function (value, index) {
      var x = values.length === 1 ? plotWidth / 2 : index / (values.length - 1) * plotWidth;
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

    ctx.beginPath();
    ctx.moveTo(points[0].x, points[0].y);
    for (var i = 1; i < points.length; i++) {
      ctx.lineTo(points[i].x, points[i].y);
    }
    ctx.lineTo(points[points.length - 1].x, height - 32);
    ctx.lineTo(points[0].x, height - 32);
    ctx.closePath();
    var gradient = ctx.createLinearGradient(0, 12, 0, height - 32);
    gradient.addColorStop(0, lineColor === "#00C805" ? "rgba(0,200,5,0.28)" : lineColor === "#FF5000" ? "rgba(255,80,0,0.28)" : "rgba(156,163,175,0.14)");
    gradient.addColorStop(1, "rgba(0,0,0,0)");
    ctx.fillStyle = gradient;
    ctx.fill();

    ctx.lineWidth = state.hovered ? 3 : 2;
    ctx.lineCap = "butt";
    ctx.lineJoin = "miter";
    for (var segmentIndex = 0; segmentIndex < points.length - 1; segmentIndex++) {
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
    ctx.fillText("$" + chartMax.toFixed(2), width - 62, 12);
    ctx.fillText("$" + ((chartMin + chartMax) / 2).toFixed(2), width - 62, height / 2);
    ctx.fillText("$" + chartMin.toFixed(2), width - 62, height - 44);

    var currentY = points[points.length - 1].y;
    ctx.fillStyle = lineColor;
    ctx.fillRect(width - 68, currentY - 10, 68, 20);
    ctx.fillStyle = "#FFFFFF";
    ctx.font = "bold 12px Arial";
    ctx.textAlign = "center";
    ctx.fillText("$" + endValue.toFixed(2), width - 34, currentY + 4);

    var dates = getDates(values.length, state.range);
    var labelIndexes = state.range === "1m"
      ? [0, Math.round((values.length - 1) * 7 / 22), Math.round((values.length - 1) * 14 / 22), values.length - 1]
      : [0, Math.round((values.length - 1) * 0.25), Math.round((values.length - 1) * 0.5), Math.round((values.length - 1) * 0.75), values.length - 1];
    ctx.fillStyle = "#9CA3AF";
    ctx.font = "11px Arial";
    ctx.textBaseline = "middle";
    labelIndexes.forEach(function (index, position) {
      var point = points[index];
      ctx.textAlign = position === 0 ? "left" : position === labelIndexes.length - 1 ? "right" : "center";
      var text = state.range === "1m"
        ? ["Nov 1", "Nov 8", "Nov 15", "Nov 22"][position]
        : formatAxisDate(dates[index], state.range);
      ctx.fillText(text, point.x, height - 12);
    });

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
    var plotWidth = Math.max(1, rect.width - 72);
    var clampedX = Math.max(0, Math.min(plotWidth, cssX));
    var index = Math.round(clampedX / plotWidth * (state.values.length - 1));
    index = Math.max(0, Math.min(state.values.length - 1, index));
    state.hoverIndex = index;
    state.hovered = true;

    if (state.priceElement) state.priceElement.textContent = "$" + state.values[index].toFixed(2);
    var dates = getDates(state.values.length, state.range);
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
    state.tooltip = state.tooltip || createTooltip(canvas);
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
    draw: function (canvas, values, range, priceElement, hoverDateElement) {
      attach({
        canvas: canvas,
        values: values,
        range: range,
        priceElement: priceElement,
        hoverDateElement: hoverDateElement
      });
    }
  };
})();
