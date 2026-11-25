(function () {
  "use strict";

  var BASELINE_DATE = "2026-11-23";
  var CATEGORIES = ["GPUs", "CPUs", "RAM"];
  var RANGE_DAYS = { "1d": 1, "1w": 7, "1m": 30, "1y": 365 };
  var selectedCategory = "GPUs";
  var selectedRange = "1d";
  var selectedFilter = "all";
  var selectedSort = "category-price";
  var categoryHistory = {};
  var categoryIndexes = {};
  var models = [];
  var retailers = {};

  function getJson(url) {
    return fetch(url).then(function (response) {
      if (!response.ok) {
        throw new Error("Request failed: " + url + " (" + response.status + ")");
      }
      return response.json();
    });
  }

  function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, function (character) {
      return {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        "\"": "&quot;",
        "'": "&#39;"
      }[character];
    });
  }

  function formatMoney(cents) {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD"
    }).format(cents / 100);
  }

  function formatDate(value, options) {
    if (!value) return "Not available";
    var date = new Date(value.slice(0, 10) + "T12:00:00");
    return new Intl.DateTimeFormat("en-US", options || {
      month: "short",
      day: "numeric",
      year: "numeric"
    }).format(date);
  }

  function formatPercent(value) {
    var sign = value > 0 ? "+" : "";
    return sign + value.toFixed(2) + "%";
  }

  function changeClass(value) {
    if (value < 0) return "change-cheaper";
    if (value > 0) return "change-pricier";
    return "change-neutral";
  }

  function getChange(points, days) {
    if (!points || points.length < 2) return null;
    var latest = points[points.length - 1];
    var target = new Date(latest.period + "T12:00:00");
    target.setDate(target.getDate() - days);
    var targetPeriod = [
      target.getFullYear(),
      String(target.getMonth() + 1).padStart(2, "0"),
      String(target.getDate()).padStart(2, "0")
    ].join("-");
    var previous = points.find(function (point) {
      return point.period === targetPeriod;
    });
    if (!previous || previous.price_cents <= 0) return null;
    return (latest.price_cents - previous.price_cents) / previous.price_cents * 100;
  }

  function renderChange(value) {
    if (value === null) {
      return '<span class="change-unavailable" aria-label="Not enough price data">-</span>';
    }
    return '<span class="' + changeClass(value) + '">' +
      escapeHtml(formatPercent(value)) + "</span>";
  }

  function showError(element, message) {
    if (!element) return;
    element.textContent = message;
    element.classList.add("error-state");
  }

  function loadHero() {
    return Promise.all([
      getJson("/api/catalog"),
      getJson("/api/health"),
      getJson("/api/retailers")
    ]).then(function (responses) {
      var catalog = responses[0];
      var health = responses[1];
      var configuredRetailers = responses[2].retailers;
      document.getElementById("stat-models").textContent = catalog.products.length;
      document.getElementById("stat-observations").textContent =
        new Intl.NumberFormat("en-US").format(health.observation_count);
      document.getElementById("stat-retailers").textContent = configuredRetailers.length;
      document.getElementById("stat-approved-date").textContent =
        formatDate(health.last_approved_at);
      configuredRetailers.forEach(function (retailer) {
        retailers[retailer.id] = retailer;
      });
    }).catch(function (error) {
      console.error("Could not load Home page statistics.", error);
      showError(
        document.getElementById("stat-observations"),
        "Data unavailable"
      );
      showError(document.getElementById("stat-models"), "Data unavailable");
      showError(document.getElementById("stat-retailers"), "Data unavailable");
      showError(document.getElementById("stat-approved-date"), "Data unavailable");
    });
  }

  function getIndexSeries(category) {
    return getJson("/api/indexes/" + encodeURIComponent(category)).then(function (data) {
      return (data.index_values || []).filter(function (point) {
        return point.period >= BASELINE_DATE;
      }).map(function (point) {
        return {
          period: point.period,
          value: point.index_value,
          skus_used: point.skus_used
        };
      });
    });
  }

  function getIndexChange(points) {
    if (!points || points.length < 2) return null;
    var first = points[0].value;
    var last = points[points.length - 1].value;
    if (!first) return null;
    return (last - first) / first * 100;
  }

  function renderIndexCards() {
    var container = document.getElementById("index-cards");
    container.innerHTML = CATEGORIES.map(function (category) {
      var history = categoryHistory[category] || [];
      var current = categoryIndexes[category];
      var hasHistory = history.length > 0;
      var value = hasHistory && current
        ? Number(current.index_value).toFixed(2)
        : "Not enough data yet";
      var change = getIndexChange(history);
      var changeText = change === null
        ? '<span class="change-unavailable">Not enough data yet</span>'
        : '<span class="' + changeClass(change) + '">' +
          escapeHtml(formatPercent(change)) + "</span>";
      var selected = category === selectedCategory ? " selected" : "";
      return '<button type="button" class="index-card' + selected +
        '" data-index-category="' + escapeHtml(category) + '">' +
        '<span class="index-card-name">' + escapeHtml(category) + "</span>" +
        '<strong class="index-card-value">' + escapeHtml(value) + "</strong>" +
        '<span class="index-card-change">' + changeText + "</span>" +
        "</button>";
    }).join("");

    container.querySelectorAll("[data-index-category]").forEach(function (button) {
      button.addEventListener("click", function () {
        selectedCategory = button.dataset.indexCategory;
        renderIndexCards();
        drawSelectedIndex();
      });
    });
  }

  function filterRange(points) {
    if (selectedRange === "all" || !points.length) return points;
    var latest = new Date(points[points.length - 1].period + "T12:00:00");
    var cutoff = new Date(latest);
    cutoff.setDate(cutoff.getDate() - RANGE_DAYS[selectedRange]);
    var cutoffPeriod = [
      cutoff.getFullYear(),
      String(cutoff.getMonth() + 1).padStart(2, "0"),
      String(cutoff.getDate()).padStart(2, "0")
    ].join("-");
    return points.filter(function (point) {
      return point.period >= cutoffPeriod;
    });
  }

  function drawIndexChart(points) {
    var canvas = document.getElementById("index-chart");
    var context = canvas.getContext("2d");
    var width = Math.max(1, canvas.clientWidth);
    var height = Math.max(260, canvas.clientHeight);
    var ratio = window.devicePixelRatio || 1;
    canvas.width = Math.round(width * ratio);
    canvas.height = Math.round(height * ratio);
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    context.clearRect(0, 0, width, height);
    context.fillStyle = "#050505";
    context.fillRect(0, 0, width, height);

    if (!points.length) {
      context.fillStyle = "#9ca3af";
      context.font = "14px Arial";
      context.textAlign = "center";
      context.textBaseline = "middle";
      context.fillText("Not enough data yet", width / 2, height / 2);
      return;
    }

    var values = points.map(function (point) { return point.value; });
    var minimum = Math.min.apply(null, values);
    var maximum = Math.max.apply(null, values);
    var spread = maximum - minimum || Math.abs(maximum) * 0.04 || 1;
    var chartMin = minimum - spread * 0.12;
    var chartMax = maximum + spread * 0.12;
    var left = 18;
    var top = 20;
    var bottom = height - 42;
    var right = width - 104;
    var plotWidth = Math.max(1, right - left);
    var plotHeight = Math.max(1, bottom - top);

    function pointAt(index) {
      return {
        x: points.length === 1 ? left + plotWidth / 2 : left + index / (points.length - 1) * plotWidth,
        y: top + (chartMax - values[index]) / (chartMax - chartMin) * plotHeight
      };
    }

    context.font = "11px Arial";
    context.textBaseline = "middle";
    context.textAlign = "right";
    context.strokeStyle = "#242424";
    context.fillStyle = "#9ca3af";
    [0, 0.5, 1].forEach(function (fraction) {
      var y = top + plotHeight * fraction;
      var value = chartMax - (chartMax - chartMin) * fraction;
      context.beginPath();
      context.moveTo(left, y);
      context.lineTo(right, y);
      context.stroke();
      context.fillText(value.toFixed(2), width - 10, y);
    });

    var firstValue = values[0];
    var lastValue = values[values.length - 1];
    var color = lastValue < firstValue
      ? "#00c805"
      : lastValue > firstValue
        ? "#ff4d4d"
        : "#9ca3af";
    context.beginPath();
    points.forEach(function (point, index) {
      var position = pointAt(index);
      if (index === 0) context.moveTo(position.x, position.y);
      else context.lineTo(position.x, position.y);
    });
    context.strokeStyle = color;
    context.lineWidth = 2;
    context.stroke();

    points.forEach(function (point, index) {
      var position = pointAt(index);
      context.beginPath();
      context.arc(position.x, position.y, 3.5, 0, Math.PI * 2);
      context.fillStyle = color;
      context.fill();
    });

    var latestPosition = pointAt(points.length - 1);
    var tagY = Math.max(top, Math.min(bottom - 22, latestPosition.y - 11));
    var tagX = Math.max(left, right - 94);
    context.fillStyle = color;
    context.fillRect(tagX, tagY, 88, 22);
    context.fillStyle = "#050505";
    context.font = "bold 11px Arial";
    context.textAlign = "center";
    context.fillText(lastValue.toFixed(2), tagX + 44, tagY + 11);

    var labelCount = Math.min(5, points.length);
    for (var labelIndex = 0; labelIndex < labelCount; labelIndex++) {
      var pointIndex = labelCount === 1
        ? 0
        : Math.round(labelIndex * (points.length - 1) / (labelCount - 1));
      var labelPosition = pointAt(pointIndex);
      context.fillStyle = "#9ca3af";
      context.font = "11px Arial";
      context.textAlign = labelIndex === 0
        ? "left"
        : labelIndex === labelCount - 1
          ? "right"
          : "center";
      context.fillText(formatDate(points[pointIndex].period, {
        month: "short",
        day: "numeric"
      }), labelPosition.x, height - 16);
    }
  }

  function drawSelectedIndex() {
    var points = filterRange(categoryHistory[selectedCategory] || []);
    var index = categoryIndexes[selectedCategory];
    var valueElement = document.getElementById("index-chart-value");
    var changeElement = document.getElementById("index-chart-change");
    document.getElementById("index-chart-category").textContent = selectedCategory;

    if (points.length && index) {
      valueElement.textContent = Number(index.index_value).toFixed(2);
      var change = getIndexChange(categoryHistory[selectedCategory] || []);
      changeElement.textContent = change === null
        ? "Not enough data yet"
        : formatPercent(change);
      changeElement.className = change === null ? "change-unavailable" : changeClass(change);
    } else {
      valueElement.textContent = "Not enough data yet";
      changeElement.textContent = "Not enough data yet";
      changeElement.className = "change-unavailable";
    }
    drawIndexChart(points);
  }

  function loadIndexes() {
    return Promise.all([
      getJson("/api/indexes"),
      getIndexSeries("GPUs"),
      getIndexSeries("CPUs"),
      getIndexSeries("RAM")
    ]).then(function (responses) {
      (responses[0].categories || []).forEach(function (item) {
        categoryIndexes[item.category] = item;
      });
      CATEGORIES.forEach(function (category, index) {
        categoryHistory[category] = responses[index + 1];
      });
      renderIndexCards();
      drawSelectedIndex();
    }).catch(function (error) {
      console.error("Could not load category prices.", error);
      showError(document.getElementById("index-cards"), "Price level data unavailable.");
      drawIndexChart([]);
    });
  }

  function renderMoverList(elementId, entries, direction) {
    var list = document.getElementById(elementId);
    if (!entries || !entries.length) {
      list.innerHTML = '<li class="empty-state">Not enough data yet</li>';
      return;
    }
    list.innerHTML = entries.map(function (item) {
      var change = Number(item.change_percent);
      return '<li class="mover-row">' +
        '<a href="/product/' + encodeURIComponent(item.sku_id) + '">' +
        escapeHtml(item.model) + "</a>" +
        '<span class="mover-category">' + escapeHtml(item.category) + "</span>" +
        '<span class="' + (direction === "cheaper" ? "change-cheaper" : "change-pricier") +
        '">' + escapeHtml(formatPercent(change)) + "</span>" +
        "</li>";
    }).join("");
  }

  function loadMovers() {
    return getJson("/api/movers?range=1d").then(function (data) {
      renderMoverList("cheaper-list", data.cheaper, "cheaper");
      renderMoverList("pricier-list", data.pricier, "pricier");
    }).catch(function (error) {
      console.error("Could not load price movers.", error);
      showError(document.getElementById("cheaper-list"), "Mover data unavailable.");
      showError(document.getElementById("pricier-list"), "Mover data unavailable.");
    });
  }

  function isExactRetailerPage(retailerId, pageUrl) {
    var retailer = retailers[retailerId];
    if (!retailer || !pageUrl || !retailer.base_url) return false;
    try {
      var page = new URL(pageUrl);
      var base = new URL(retailer.base_url);
      var pageHost = page.hostname.toLowerCase();
      var baseHost = base.hostname.toLowerCase();
      if (page.protocol !== "https:" && page.protocol !== "http:") return false;
      if (pageHost !== baseHost && !pageHost.endsWith("." + baseHost)) return false;
      return !/\/p\/pl(?:\/|$)|\/search(?:\/|$)/i.test(page.pathname);
    } catch (error) {
      return false;
    }
  }

  function renderRetailerLinks(urls) {
    var links = Object.keys(urls || {}).filter(function (retailerId) {
      return isExactRetailerPage(retailerId, urls[retailerId]);
    }).sort(function (left, right) {
      return retailers[left].name.localeCompare(retailers[right].name);
    });
    if (!links.length) {
      return '<span class="retailer-unavailable">No retailer page listed</span>';
    }
    return '<span class="retailer-links">' + links.map(function (retailerId) {
      return '<a href="' + escapeHtml(urls[retailerId]) +
        '" target="_blank" rel="noopener noreferrer">' +
        escapeHtml(retailers[retailerId].name) + "</a>";
    }).join("") + "</span>";
  }

  function getModelChange(model, days) {
    return getChange(model.price_points || [], days);
  }

  function compareNullable(left, right, direction) {
    if (left === null && right === null) return 0;
    if (left === null) return 1;
    if (right === null) return -1;
    return (left - right) * direction;
  }

  function getModelSortPrice(model) {
    var offer = model.home_offer;
    if (offer && offer.price_cents !== null &&
        Number.isFinite(Number(offer.price_cents))) {
      return Number(offer.price_cents);
    }
    var points = model.price_points || [];
    if (points.length && Number.isFinite(Number(points[points.length - 1].price_cents))) {
      return Number(points[points.length - 1].price_cents);
    }
    return null;
  }

  function sortModels(items) {
    var sorted = items.slice();
    sorted.sort(function (left, right) {
      var leftPrice = getModelSortPrice(left);
      var rightPrice = getModelSortPrice(right);
      if (leftPrice === null && rightPrice !== null) return 1;
      if (rightPrice === null && leftPrice !== null) return -1;

      if (selectedSort === "category-price") {
        var categoryOrder = CATEGORIES.indexOf(left.category) - CATEGORIES.indexOf(right.category);
        if (categoryOrder !== 0) return categoryOrder;
        var categoryPriceOrder = compareNullable(leftPrice, rightPrice, 1);
        if (categoryPriceOrder !== 0) return categoryPriceOrder;
      } else if (selectedSort === "price-low-high") {
        var lowPriceOrder = compareNullable(leftPrice, rightPrice, 1);
        if (lowPriceOrder !== 0) return lowPriceOrder;
      } else if (selectedSort === "price-high-low") {
        var highPriceOrder = compareNullable(leftPrice, rightPrice, -1);
        if (highPriceOrder !== 0) return highPriceOrder;
      } else if (selectedSort === "change-7d") {
        var weeklyOrder = compareNullable(
          getModelChange(left, 7),
          getModelChange(right, 7),
          1
        );
        if (weeklyOrder !== 0) return weeklyOrder;
      } else if (selectedSort === "change-30d") {
        var monthlyOrder = compareNullable(
          getModelChange(left, 30),
          getModelChange(right, 30),
          1
        );
        if (monthlyOrder !== 0) return monthlyOrder;
      }
      return left.model.localeCompare(right.model);
    });
    return sorted;
  }

  function drawSparkline(canvas, points) {
    var context = canvas.getContext("2d");
    var width = Math.max(1, canvas.clientWidth || 88);
    var height = Math.max(1, canvas.clientHeight || 30);
    var ratio = window.devicePixelRatio || 1;
    canvas.width = Math.round(width * ratio);
    canvas.height = Math.round(height * ratio);
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    context.clearRect(0, 0, width, height);
    if (!points.length) return;

    var first = points[0].price_cents;
    var last = points[points.length - 1].price_cents;
    var color = last < first ? "#00c805" : last > first ? "#ff4d4d" : "#9ca3af";
    if (points.length === 1) {
      context.beginPath();
      context.arc(width / 2, height / 2, 3, 0, Math.PI * 2);
      context.fillStyle = "#9ca3af";
      context.fill();
      return;
    }

    var values = points.map(function (point) { return point.price_cents; });
    var minimum = Math.min.apply(null, values);
    var maximum = Math.max.apply(null, values);
    var spread = maximum - minimum || Math.abs(maximum) * 0.04 || 1;
    var chartMin = minimum - spread * 0.15;
    var chartMax = maximum + spread * 0.15;
    context.beginPath();
    points.forEach(function (point, index) {
      var x = index / (points.length - 1) * (width - 4) + 2;
      var y = 3 + (chartMax - point.price_cents) / (chartMax - chartMin) * (height - 6);
      if (index === 0) context.moveTo(x, y);
      else context.lineTo(x, y);
    });
    context.strokeStyle = color;
    context.lineWidth = 2;
    context.lineCap = "round";
    context.lineJoin = "round";
    context.stroke();
  }

  function renderModelPrice(model, latest) {
    var offer = model.home_offer;
    if (offer && Number.isFinite(Number(offer.price_cents))) {
      var sourceNames = (offer.retailer_ids || []).map(function (retailerId) {
        return retailers[retailerId] ? retailers[retailerId].name : null;
      }).filter(Boolean);
      var includesRetailerNames = offer.availability && sourceNames.some(function (name) {
        return offer.availability.toLowerCase().includes(name.toLowerCase());
      });
      var detailParts = includesRetailerNames ? [offer.availability] : sourceNames;
      if (!includesRetailerNames && offer.availability) {
        detailParts.push(offer.availability);
      }
      detailParts.push(formatDate(offer.checked_on, { month: "short", day: "numeric" }));
      var detail = detailParts.filter(Boolean).join(", ");
      return '<span class="model-last-price">' +
        formatMoney(Number(offer.price_cents)) + "</span>" +
        '<span class="model-price-date">' + escapeHtml(detail) + "</span>";
    }
    if (latest) {
      return '<span class="model-last-price">' +
        formatMoney(latest.price_cents) + "</span>" +
        '<span class="model-price-date">Median price, ' +
        escapeHtml(formatDate(latest.period, { month: "short", day: "numeric" })) +
        "</span>";
    }
    return '<span class="change-unavailable">Not verified</span>';
  }

  function renderModels() {
    var body = document.getElementById("models-table-body");
    var filtered = selectedFilter === "all"
      ? models
      : models.filter(function (model) { return model.category === selectedFilter; });
    var sorted = sortModels(filtered);
    document.getElementById("model-count").textContent =
      sorted.length + (sorted.length === 1 ? " model" : " models");
    if (!sorted.length) {
      body.innerHTML = '<tr><td class="empty-state" colspan="7">No models found.</td></tr>';
      return;
    }

    body.innerHTML = sorted.map(function (model) {
      var points = (model.price_points || []).filter(function (point) {
        return point.period >= BASELINE_DATE;
      });
      var latest = points.length ? points[points.length - 1] : null;
      var latestPrice = renderModelPrice(model, latest);
      var chart = points.length
        ? '<canvas class="model-sparkline" width="88" height="30" aria-label="' +
          escapeHtml(model.model) + ' price sparkline"></canvas>'
        : '<span class="change-unavailable" aria-label="No price data">-</span>';
      return '<tr>' +
        '<td data-label="Model"><a class="model-link" href="/product/' +
          encodeURIComponent(model.id) + '">' + escapeHtml(model.model) + "</a></td>" +
        '<td data-label="Category">' + escapeHtml(model.category) + "</td>" +
        '<td data-label="Latest price">' + latestPrice + "</td>" +
        '<td data-label="7 day change">' + renderChange(getModelChange(model, 7)) + "</td>" +
        '<td data-label="30 day change">' + renderChange(getModelChange(model, 30)) + "</td>" +
        '<td data-label="Price trend">' + chart + "</td>" +
        '<td data-label="Retailers">' + renderRetailerLinks(model.retailer_urls) + "</td>" +
        "</tr>";
    }).join("");

    body.querySelectorAll(".model-sparkline").forEach(function (canvas, index) {
      var model = sorted.find(function (item) {
        return canvas.getAttribute("aria-label") === item.model + " price sparkline";
      });
      if (model) {
        drawSparkline(canvas, (model.price_points || []).filter(function (point) {
          return point.period >= BASELINE_DATE;
        }));
      }
    });
  }

  function loadModels() {
    return Promise.all([
      getJson("/api/catalog"),
      getJson("/api/retailers")
    ]).then(function (responses) {
      models = responses[0].products.map(function (product) {
        product.price_points = (product.price_points || []).filter(function (point) {
          return point.period >= BASELINE_DATE;
        });
        return product;
      });
      responses[1].retailers.forEach(function (retailer) {
        retailers[retailer.id] = retailer;
      });
      renderModels();
    }).catch(function (error) {
      console.error("Could not load the model catalog.", error);
      document.getElementById("model-count").textContent = "Model data unavailable.";
      showError(document.getElementById("models-table-body"), "Model data unavailable.");
    });
  }

  document.querySelectorAll("[data-range]").forEach(function (button) {
    button.addEventListener("click", function () {
      selectedRange = button.dataset.range;
      document.querySelectorAll("[data-range]").forEach(function (rangeButton) {
        rangeButton.classList.toggle("active", rangeButton === button);
      });
      drawSelectedIndex();
    });
  });

  document.querySelectorAll("[data-category]").forEach(function (button) {
    button.addEventListener("click", function () {
      selectedFilter = button.dataset.category;
      document.querySelectorAll(".filter-button").forEach(function (filterButton) {
        filterButton.classList.toggle("active", filterButton === button);
      });
      renderModels();
    });
  });

  document.getElementById("model-sort").addEventListener("change", function (event) {
    selectedSort = event.target.value;
    renderModels();
  });

  window.addEventListener("resize", function () {
    drawSelectedIndex();
    renderModels();
  });

  Promise.all([loadHero(), loadIndexes(), loadMovers(), loadModels()]);
})();
