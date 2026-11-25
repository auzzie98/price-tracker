(function () {
  "use strict";

  var BASELINE_DATE = "2026-11-23";
  var RANGE_DAYS = { "1d": 1, "1w": 7, "1m": 30, "1y": 365 };
  var selectedRange = "1m";
  var selectedMaker = "all";
  var selectedSort = "drop";
  var gpuProducts = [];
  var indexPoints = [];

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

  function formatDate(period) {
    if (!period) return "Date not available";
    return new Intl.DateTimeFormat("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric"
    }).format(new Date(period + "T12:00:00"));
  }

  function makerFor(product) {
    var chip = String(product.chip || "").toUpperCase();
    if (chip.indexOf("RTX") === 0 || chip.indexOf("GTX") === 0) return "NVIDIA";
    if (chip.indexOf("RX") === 0) return "AMD";
    if (chip.indexOf("ARC") === 0) return "Intel";
    return "Unknown";
  }

  function getPoints(product) {
    return (product.price_points || []).slice().sort(function (first, second) {
      return first.period.localeCompare(second.period);
    });
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

  function changeClass(value) {
    if (value < 0) return "change-cheaper";
    if (value > 0) return "change-pricier";
    return "change-neutral";
  }

  function renderChange(value) {
    if (value === null) {
      return '<span class="gpu-change-unavailable" aria-label="Not enough price data">-</span>';
    }
    var sign = value > 0 ? "+" : "";
    return '<span class="' + changeClass(value) + '">' +
      escapeHtml(sign + value.toFixed(2) + "%") + "</span>";
  }

  function median(values) {
    if (!values.length) return null;
    var sorted = values.slice().sort(function (first, second) {
      return first - second;
    });
    var middle = Math.floor(sorted.length / 2);
    if (sorted.length % 2) return sorted[middle];
    return (sorted[middle - 1] + sorted[middle]) / 2;
  }

  function renderStats() {
    var prices = gpuProducts
      .filter(function (product) { return product.price_cents !== null; })
      .map(function (product) { return product.price_cents; });
    var observations = gpuProducts.reduce(function (total, product) {
      return total + getPoints(product).reduce(function (productTotal, point) {
        return productTotal + (Number(point.retailers_used) || 0);
      }, 0);
    }, 0);

    document.getElementById("gpu-lowest-price").textContent = prices.length
      ? formatMoney(Math.min.apply(null, prices))
      : "-";
    document.getElementById("gpu-highest-price").textContent = prices.length
      ? formatMoney(Math.max.apply(null, prices))
      : "-";
    document.getElementById("gpu-median-price").textContent = prices.length
      ? formatMoney(median(prices))
      : "-";
    document.getElementById("gpu-observation-count").textContent =
      new Intl.NumberFormat("en-US").format(observations);
  }

  function filterRange(points, range) {
    if (range === "all" || !points.length) return points;
    var latest = new Date(points[points.length - 1].period + "T12:00:00");
    var cutoff = new Date(latest);
    cutoff.setDate(cutoff.getDate() - RANGE_DAYS[range]);
    var cutoffPeriod = [
      cutoff.getFullYear(),
      String(cutoff.getMonth() + 1).padStart(2, "0"),
      String(cutoff.getDate()).padStart(2, "0")
    ].join("-");
    return points.filter(function (point) {
      return point.period >= cutoffPeriod;
    });
  }

  function renderIndexChart() {
    var points = filterRange(indexPoints, selectedRange);
    var valueElement = document.getElementById("gpu-index-value");
    var statusElement = document.getElementById("gpu-index-status");
    var canvas = document.getElementById("gpu-index-chart");

    if (!points.length) {
      valueElement.textContent = "Not available";
      statusElement.textContent = "The GPU index has no observations yet.";
      statusElement.classList.remove("error-state");
      var context = canvas.getContext("2d");
      context.clearRect(0, 0, canvas.width, canvas.height);
      return;
    }

    var latest = points[points.length - 1];
    valueElement.textContent = Number(latest.value).toFixed(2);
    statusElement.textContent = points.length === 1
      ? "Latest index reading: " + formatDate(latest.period) + "."
      : points.length + " real index observations are available for this range.";
    statusElement.classList.remove("error-state");

    window.PriceTrackerChart.draw(
      canvas,
      points.map(function (point) { return Number(point.value); }),
      selectedRange,
      valueElement,
      null,
      points.map(function (point) { return point.period; }),
      {
        valueFormatter: function (value) { return Number(value).toFixed(2); },
        useActualDates: true,
        singlePointMessage: "One index observation is available, so no change is shown yet.",
        neutralColor: "#9CA3AF",
        segmentColorByPrevious: true,
        suppressCurrentValueTick: true
      }
    );
  }

  function observationIsUsable(observation) {
    var source = String(observation.source_url || "");
    var isBaseline = source === "Nov 23, 2026 baseline snapshot";
    var isDirectRetailerPage = /^https?:\/\//i.test(source) &&
      !/example\.com\/mock/i.test(source);
    return observation.in_stock && (isBaseline || isDirectRetailerPage);
  }

  function getLatestSources(product) {
    var points = getPoints(product);
    if (!points.length) return [];
    var latestPeriod = points[points.length - 1].period;
    var observations = product.retailer_prices || [];
    var byRetailer = {};

    observations.forEach(function (observation) {
      if (!observationIsUsable(observation) ||
          String(observation.observed_at || "").slice(0, 10) !== latestPeriod) {
        return;
      }
      if (!byRetailer[observation.retailer_id]) {
        byRetailer[observation.retailer_id] = observation;
      }
    });

    return Object.keys(byRetailer).map(function (retailerId) {
      return byRetailer[retailerId];
    }).sort(function (first, second) {
      return first.retailer_name.localeCompare(second.retailer_name);
    });
  }

  function sortProducts(products) {
    return products.slice().sort(function (first, second) {
      var firstHasPrice = first.price_cents !== null;
      var secondHasPrice = second.price_cents !== null;
      if (firstHasPrice !== secondHasPrice) return firstHasPrice ? -1 : 1;

      if (selectedSort === "model") {
        return first.model.localeCompare(second.model);
      }

      if (selectedSort === "drop" || selectedSort === "rise") {
        var firstChange = getChange(getPoints(first), 30);
        var secondChange = getChange(getPoints(second), 30);
        if (firstChange !== null && secondChange === null) return -1;
        if (firstChange === null && secondChange !== null) return 1;
        if (firstChange !== null && secondChange !== null && firstChange !== secondChange) {
          return selectedSort === "drop"
            ? firstChange - secondChange
            : secondChange - firstChange;
        }
      }

      if (selectedSort === "highest" && firstHasPrice && first.price_cents !== second.price_cents) {
        return second.price_cents - first.price_cents;
      }
      if (firstHasPrice && first.price_cents !== second.price_cents) {
        return first.price_cents - second.price_cents;
      }
      return first.model.localeCompare(second.model);
    });
  }

  function sourceLinks(sources, product) {
    if (product.retailer_price_error) {
      return '<span class="gpu-price-source">Source data unavailable</span>';
    }
    if (!sources.length) {
      return '<span class="gpu-price-source">Source not verified</span>';
    }
    var labels = sources.map(function (source) {
      if (!source.product_url) return escapeHtml(source.retailer_name);
      return '<a href="' + escapeHtml(source.product_url) + '" target="_blank" rel="noopener noreferrer">' +
        escapeHtml(source.retailer_name) + "</a>";
    }).join("");
    var countLabel = sources.length === 1 ? "1 retailer" : sources.length + " retailers";
    return '<span class="gpu-price-source">' + countLabel + "</span>" +
      '<span class="gpu-retailer-links">' + labels + "</span>";
  }

  function renderRow(product) {
    var points = getPoints(product);
    var hasPrice = product.price_cents !== null;
    var latestPoint = points.length ? points[points.length - 1] : null;
    var sources = getLatestSources(product);
    var dateLabel = latestPoint
      ? "Median price, " + formatDate(latestPoint.period)
      : "Price not verified";
    var priceMarkup = hasPrice
      ? '<span class="gpu-price-value">' + escapeHtml(formatMoney(product.price_cents)) + "</span>" +
        '<span class="gpu-price-source">' + escapeHtml(dateLabel) + "</span>"
      : '<span class="gpu-price-unavailable">Not verified</span>';
    var trendMarkup = points.length
      ? '<canvas class="gpu-sparkline" data-product-id="' + escapeHtml(product.id) +
        '" aria-label="' + escapeHtml(product.model) + ' price trend"></canvas>'
      : '<span class="gpu-change-unavailable" aria-label="No price history">-</span>';

    return '<tr data-product-id="' + escapeHtml(product.id) + '">' +
      '<td data-column="model" data-label="Model"><a class="gpu-model-link" href="/product/' +
      encodeURIComponent(product.id) + '">' + escapeHtml(product.model) + "</a></td>" +
      '<td data-column="maker" data-label="Maker">' + escapeHtml(makerFor(product)) + "</td>" +
      '<td data-column="price" data-label="Median price">' + priceMarkup + "</td>" +
      '<td data-column="seven-day" data-label="7 days">' + renderChange(getChange(points, 7)) + "</td>" +
      '<td data-column="thirty-day" data-label="30 days">' + renderChange(getChange(points, 30)) + "</td>" +
      '<td data-column="trend" data-label="30-day trend">' + trendMarkup + "</td>" +
      '<td data-column="prices" data-label="Prices">' + sourceLinks(sources, product) + "</td>" +
      "</tr>";
  }

  function renderTable() {
    var visible = gpuProducts.filter(function (product) {
      return selectedMaker === "all" || makerFor(product) === selectedMaker;
    });
    var sorted = sortProducts(visible);
    var tableBody = document.getElementById("gpu-table-body");
    document.getElementById("gpu-model-count").textContent =
      "Showing " + sorted.length + " of " + gpuProducts.length + " GPUs";

    if (!sorted.length) {
      tableBody.innerHTML =
        '<tr><td colspan="7" class="gpu-table-message">No GPUs match this filter.</td></tr>';
      return;
    }

    tableBody.innerHTML = sorted.map(renderRow).join("");
    tableBody.querySelectorAll(".gpu-sparkline").forEach(function (canvas) {
      var product = gpuProducts.find(function (item) {
        return item.id === canvas.dataset.productId;
      });
      if (product) drawSparkline(canvas, getPoints(product));
    });
  }

  function drawSparkline(canvas, points) {
    var width = Math.max(1, canvas.clientWidth || 132);
    var height = 34;
    var ratio = window.devicePixelRatio || 1;
    canvas.width = Math.round(width * ratio);
    canvas.height = Math.round(height * ratio);
    var context = canvas.getContext("2d");
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    context.clearRect(0, 0, width, height);
    if (!points.length) return;

    var values = points.map(function (point) { return point.price_cents; });
    var minimum = Math.min.apply(null, values);
    var maximum = Math.max.apply(null, values);
    var spread = maximum - minimum || Math.abs(maximum) * 0.1 || 1;
    var chartMinimum = minimum - spread * 0.08;
    var chartMaximum = maximum + spread * 0.08;
    var x = function (index) {
      return points.length === 1
        ? width - 4
        : 4 + index / (points.length - 1) * (width - 8);
    };
    var y = function (value) {
      return 4 + (chartMaximum - value) / (chartMaximum - chartMinimum) * (height - 8);
    };
    context.lineWidth = 2;
    context.lineCap = "round";
    context.lineJoin = "round";

    if (points.length === 1) {
      var singleY = y(values[0]);
      context.beginPath();
      context.moveTo(4, singleY);
      context.lineTo(width - 4, singleY);
      context.strokeStyle = "#9CA3AF";
      context.stroke();
      context.beginPath();
      context.arc(width - 4, singleY, 2.5, 0, Math.PI * 2);
      context.fillStyle = "#9CA3AF";
      context.fill();
      return;
    }

    for (var index = 0; index < points.length - 1; index++) {
      var firstValue = values[index];
      var secondValue = values[index + 1];
      context.beginPath();
      context.moveTo(x(index), y(firstValue));
      context.lineTo(x(index + 1), y(secondValue));
      context.strokeStyle = secondValue < firstValue
        ? "#00C805"
        : secondValue > firstValue ? "#FF5000" : "#9CA3AF";
      context.stroke();
    }

    var last = values.length - 1;
    context.beginPath();
    context.arc(x(last), y(values[last]), 2.5, 0, Math.PI * 2);
    context.fillStyle = values[last] < values[last - 1]
      ? "#00C805"
      : values[last] > values[last - 1] ? "#FF5000" : "#9CA3AF";
    context.fill();
  }

  function updateRanges() {
    document.querySelectorAll(".gpu-range-button").forEach(function (button) {
      var active = button.dataset.range === selectedRange;
      button.classList.toggle("active", active);
      button.setAttribute("aria-pressed", String(active));
    });
    renderIndexChart();
  }

  function updateFilters() {
    document.querySelectorAll(".gpu-filter-button").forEach(function (button) {
      var active = button.dataset.maker === selectedMaker;
      button.classList.toggle("active", active);
      button.setAttribute("aria-pressed", String(active));
    });
    renderTable();
  }

  function showLoadError(error) {
    console.error("Could not load GPU page data.", error);
    var status = document.getElementById("gpu-index-status");
    status.textContent = "GPU index data could not be loaded.";
    status.classList.add("error-state");
    ["gpu-index-value", "gpu-lowest-price", "gpu-highest-price", "gpu-median-price",
      "gpu-observation-count", "gpu-model-count"].forEach(function (id) {
      document.getElementById(id).textContent = "Data unavailable";
    });
    document.getElementById("gpu-table-body").innerHTML =
      '<tr><td colspan="7" class="gpu-table-message error-state">' +
      "GPU catalog data could not be loaded. Please reload to try again.</td></tr>";
  }

  function loadPage() {
    return Promise.all([
      getJson("/api/catalog"),
      getJson("/api/indexes/GPUs")
    ]).then(function (responses) {
      gpuProducts = responses[0].products.filter(function (product) {
        return product.category === "GPUs";
      }).map(function (product) {
        product.retailer_prices = [];
        return product;
      });

      var series = responses[1].index_values || [];
      indexPoints = series.filter(function (point) {
        return point.period >= BASELINE_DATE;
      }).map(function (point) {
        return {
          period: point.period,
          value: point.index_value,
          skus_used: point.skus_used
        };
      });

      return Promise.all(gpuProducts.filter(function (product) {
        return product.price_cents !== null;
      }).map(function (product) {
        return getJson("/api/products/" + encodeURIComponent(product.id) + "/retailer-prices")
          .then(function (data) {
            product.retailer_prices = data.retailer_prices || [];
          })
          .catch(function (error) {
            product.retailer_price_error = true;
            console.error("Could not load GPU price sources for " + product.id + ".", error);
          });
      }));
    }).then(function () {
      renderStats();
      renderIndexChart();
      renderTable();
    }).catch(showLoadError);
  }

  document.querySelectorAll(".gpu-range-button").forEach(function (button) {
    button.addEventListener("click", function () {
      selectedRange = button.dataset.range;
      updateRanges();
    });
  });

  document.querySelectorAll(".gpu-filter-button").forEach(function (button) {
    button.addEventListener("click", function () {
      selectedMaker = button.dataset.maker;
      updateFilters();
    });
  });

  document.getElementById("gpu-sort").addEventListener("change", function (event) {
    selectedSort = event.target.value;
    renderTable();
  });

  window.addEventListener("resize", function () {
    renderIndexChart();
    document.querySelectorAll(".gpu-sparkline").forEach(function (canvas) {
      var product = gpuProducts.find(function (item) {
        return item.id === canvas.dataset.productId;
      });
      if (product) drawSparkline(canvas, getPoints(product));
    });
  });

  loadPage();
})();
