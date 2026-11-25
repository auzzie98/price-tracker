(function () {
  "use strict";

  var currentRange = "all";
  var rangeMonths = { "1m": 1, "3m": 3, "6m": 6, "1y": 12 };
  var loadedProductData = null;

  function byId(id) {
    return document.getElementById(id);
  }

  function setText(id, value) {
    byId(id).textContent = value;
  }

  function formatMoney(cents) {
    if (typeof cents !== "number" || !Number.isFinite(cents)) return "-";
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD"
    }).format(cents / 100);
  }

  function parseDate(value) {
    if (!value) return null;
    var date = new Date(value.length === 10 ? value + "T12:00:00" : value);
    return Number.isNaN(date.getTime()) ? null : date;
  }

  function formatDate(value, includeYear) {
    var date = parseDate(value);
    if (!date) return "-";
    return date.toLocaleDateString("en-US", includeYear
      ? { month: "short", day: "numeric", year: "numeric" }
      : { month: "short", day: "numeric" });
  }

  function formatObservedDate(value) {
    return formatDate(value, true);
  }

  function getProductId() {
    var match = window.location.pathname.match(/^\/product\/([^/]+)\/?$/);
    return match ? decodeURIComponent(match[1]) : "";
  }

  function getCategoryPath(category) {
    return category === "GPUs" ? "/gpus" : "/#models";
  }

  function getPricePoints(product) {
    return (product.price_points || []).filter(function (point) {
      return typeof point.price_cents === "number" && parseDate(point.period);
    }).sort(function (left, right) {
      return left.period.localeCompare(right.period);
    });
  }

  function getRangeStart(points, range) {
    if (range === "all" || !points.length) return null;
    var lastDate = parseDate(points[points.length - 1].period);
    var start = new Date(lastDate);
    start.setMonth(start.getMonth() - rangeMonths[range]);
    return start;
  }

  function filterPoints(points, range) {
    var start = getRangeStart(points, range);
    if (!start) return points.slice();
    return points.filter(function (point) {
      return parseDate(point.period) >= start;
    });
  }

  function filterObservations(observations) {
    return (observations || []).filter(function (observation) {
      return !observation.is_excluded &&
        !observation.is_mock &&
        observation.source_label !== "Unverified source";
    }).sort(function (left, right) {
      return String(right.observed_at).localeCompare(String(left.observed_at));
    });
  }

  function appendCell(row, value, className, label) {
    var cell = document.createElement("td");
    if (className) cell.className = className;
    if (label) cell.dataset.label = label;
    cell.textContent = value;
    row.appendChild(cell);
    return cell;
  }

  function makeLink(text, href) {
    var link = document.createElement("a");
    link.textContent = text;
    link.href = href;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    return link;
  }

  function appendRetailerCell(row, name, url) {
    var cell = document.createElement("td");
    cell.dataset.label = "Retailer";
    if (url) {
      cell.appendChild(makeLink(name, url));
    } else {
      cell.textContent = name;
    }
    row.appendChild(cell);
    return cell;
  }

  function availabilityStatus(availability, retailerName, retailerCount) {
    if (!availability) return null;
    var segments = availability.split(",");
    var segment = segments.find(function (item) {
      return item.toLowerCase().includes(retailerName.toLowerCase());
    });
    if (!segment && retailerCount === 1) segment = availability;
    if (!segment) return null;
    var text = segment.toLowerCase();
    if (/out of stock|sold out/.test(text)) return "Out of stock";
    if (/low stock|limited stock/.test(text)) return "Low stock";
    if (/in stock|available|in-store|pickup/.test(text)) return "In stock";
    return null;
  }

  function observationStatus(observation) {
    if (!observation) return "Not recorded";
    return observation.in_stock ? "In stock" : "Out of stock";
  }

  function retailerDateNote(value) {
    return value ? "Checked " + formatObservedDate(value) : "";
  }

  function renderBuyRows(product, observations, retailerNames) {
    var body = byId("product-retailer-rows");
    body.replaceChildren();
    var latestByRetailer = {};
    observations.forEach(function (observation) {
      if (!latestByRetailer[observation.retailer_id]) {
        latestByRetailer[observation.retailer_id] = observation;
      }
    });

    var offers = [];
    var offeredRetailers = {};
    if (product.home_offer) {
      offers = (product.home_offer.retailer_ids || []).map(function (retailerId) {
        var name = retailerNames[retailerId];
        var url = product.retailer_urls && product.retailer_urls[retailerId];
        if (!name || !url) return null;
        offeredRetailers[retailerId] = true;
        var observation = latestByRetailer[retailerId];
        var offerStock = availabilityStatus(
          product.home_offer.availability,
          name,
          product.home_offer.retailer_ids.length
        );
        return {
          name: name,
          url: url,
          priceCents: product.home_offer.price_cents,
          date: product.home_offer.checked_on,
          stock: offerStock || observationStatus(observation),
          stockDate: !offerStock && observation
            ? formatObservedDate(observation.observed_at)
            : ""
        };
      }).filter(Boolean);
    }

    Object.keys(latestByRetailer).forEach(function (retailerId) {
      if (offeredRetailers[retailerId]) return;
      var observation = latestByRetailer[retailerId];
      var url = observation.product_url ||
        (product.retailer_urls && product.retailer_urls[retailerId]);
      if (!url) return;
      offers.push({
        name: observation.retailer_name,
        url: url,
        priceCents: observation.price_cents,
        date: observation.observed_at,
        stock: observationStatus(observation),
        stockDate: formatObservedDate(observation.observed_at)
      });
    });

    offers.sort(function (left, right) {
      return left.name.localeCompare(right.name);
    });
    if (!offers.length) {
      var emptyRow = body.insertRow();
      appendCell(emptyRow, "No current retailer prices are verified.", "product-empty-cell")
        .colSpan = 4;
      return;
    }

    offers.forEach(function (offer) {
      var row = body.insertRow();
      var retailerCell = appendRetailerCell(row, offer.name, offer.url);
      if (offer.date) {
        var date = document.createElement("small");
        date.textContent = retailerDateNote(offer.date);
        retailerCell.appendChild(date);
      }
      appendCell(row, formatMoney(offer.priceCents), "product-table-price", "Price");
      var stockCell = appendCell(row, offer.stock, null, "Stock");
      if (offer.stockDate) {
        var notedDate = document.createElement("small");
        notedDate.textContent = "Observed " + offer.stockDate;
        stockCell.appendChild(notedDate);
      }
      var linkCell = document.createElement("td");
      linkCell.dataset.label = "Link";
      linkCell.appendChild(makeLink("View deal", offer.url));
      row.appendChild(linkCell);
    });
  }

  function renderObservations(observations) {
    var body = byId("product-observation-rows");
    body.replaceChildren();
    if (!observations.length) {
      appendCell(body.insertRow(), "No verified observations yet.", "product-empty-cell")
        .colSpan = 4;
      return;
    }

    observations.forEach(function (observation) {
      var row = body.insertRow();
      appendRetailerCell(row, observation.retailer_name, observation.product_url);
      appendCell(row, formatObservedDate(observation.observed_at), null, "Date");
      appendCell(row, observation.source_label, null, "Source");
      appendCell(row, formatMoney(observation.price_cents), "product-table-price", "Price");
    });
  }

  function percentChange(points, days) {
    if (points.length < 2) return null;
    var latest = points[points.length - 1];
    var target = parseDate(latest.period);
    target.setDate(target.getDate() - days);
    var baseline = null;
    for (var index = points.length - 2; index >= 0; index--) {
      if (parseDate(points[index].period) <= target) {
        baseline = points[index];
        break;
      }
    }
    if (!baseline || baseline.price_cents === 0) return null;
    return (latest.price_cents - baseline.price_cents) / baseline.price_cents * 100;
  }

  function formatChange(value) {
    if (value === null) return "-";
    var sign = value > 0 ? "+" : "";
    return sign + value.toFixed(2) + "%";
  }

  function renderOtherModels(product, products) {
    var container = byId("product-other-models");
    container.replaceChildren();
    var related = products.filter(function (item) {
      return item.category === product.category && item.id !== product.id;
    });
    if (!related.length) {
      var empty = document.createElement("p");
      empty.className = "product-empty-cell";
      empty.textContent = "No other models in this category.";
      container.appendChild(empty);
      return;
    }

    related.forEach(function (item) {
      var points = getPricePoints(item);
      var latest = points.length ? points[points.length - 1] : null;
      var change = percentChange(points, 30);
      var currentPrice = item.home_offer
        ? item.home_offer.price_cents
        : latest ? latest.price_cents : null;
      var card = document.createElement("a");
      card.className = "product-other-card";
      card.href = "/product/" + encodeURIComponent(item.id);

      var title = document.createElement("strong");
      title.textContent = item.model;
      card.appendChild(title);

      var price = document.createElement("span");
      price.textContent = currentPrice === null ? "-" : formatMoney(currentPrice);
      card.appendChild(price);

      var movement = document.createElement("span");
      movement.textContent = formatChange(change);
      if (change !== null) {
        movement.classList.add(change < 0 ? "price-dropped" : change > 0 ? "price-rose" : "price-unchanged");
      }
      card.appendChild(movement);
      container.appendChild(card);
    });
  }

  function updateStats(points, observations, range) {
    var selected = filterPoints(points, range);
    if (!selected.length) {
      setText("product-period-low", "-");
      setText("product-period-high", "-");
      setText("product-period-median", "-");
    } else {
      var prices = selected.map(function (point) { return point.price_cents; });
      var sorted = prices.slice().sort(function (left, right) { return left - right; });
      setText("product-period-low", formatMoney(sorted[0]));
      setText("product-period-high", formatMoney(sorted[sorted.length - 1]));
      var middle = Math.floor(sorted.length / 2);
      var median = sorted.length % 2
        ? sorted[middle]
        : (sorted[middle - 1] + sorted[middle]) / 2;
      setText("product-period-median", formatMoney(median));
    }

    var start = getRangeStart(points, range);
    var selectedObservations = observations.filter(function (observation) {
      var date = parseDate(observation.observed_at);
      return date && (!start || date >= start);
    });
    setText(
      "product-observation-count",
      selectedObservations.length ? String(selectedObservations.length) : "-"
    );
  }

  function drawChart(points, range) {
    var canvas = byId("product-chart");
    var empty = byId("product-chart-empty");
    var selected = filterPoints(points, range);
    var context = canvas.getContext("2d");
    context.clearRect(0, 0, canvas.width, canvas.height);
    empty.hidden = selected.length > 0;
    if (!selected.length) return;
    window.PriceTrackerChart.draw(
      canvas,
      selected.map(function (point) { return point.price_cents / 100; }),
      range,
      null,
      byId("product-chart-tooltip"),
      selected.map(function (point) { return point.period; }),
      {
        valueFormatter: function (value) { return formatMoney(Math.round(value * 100)); },
        useActualDates: true,
        neutralColor: "#9CA3AF",
        singlePointMessage: "Only one verified price point is available so far."
      }
    );
  }

  function renderProduct(product, products, retailerRows, retailerNames) {
    var points = getPricePoints(product);
    var observations = filterObservations(retailerRows);
    loadedProductData = { points: points, observations: observations };
    var latest = points.length ? points[points.length - 1] : null;
    var categoryPath = getCategoryPath(product.category);
    var categoryLink = byId("product-category-link");
    categoryLink.href = categoryPath;
    categoryLink.textContent = product.category;
    setText("product-category", product.category);
    setText("product-title", product.model);
    setText("product-breadcrumb-name", product.model);
    setText("product-brand", product.brand || "-");
    setText("product-type", {
      GPUs: "Graphics card",
      CPUs: "Processor",
      RAM: "Memory"
    }[product.category] || product.category);
    setText("product-mpn", product.mpn || "-");

    if (latest) {
      setText("product-current-price", formatMoney(latest.price_cents));
      setText("product-price-label", "Median price, " + formatDate(latest.period, false));
    } else {
      setText("product-current-price", "-");
      setText("product-price-label", "Median price not verified");
    }

    renderBuyRows(product, observations, retailerNames);
    renderObservations(observations);
    renderOtherModels(product, products);
    updateStats(points, observations, currentRange);
    drawChart(points, currentRange);
    byId("product-page").setAttribute("aria-label", product.model + " product details");
    document.title = product.model + " - Price Tracker";
  }

  function showError(message) {
    var error = byId("product-page-error");
    error.textContent = message;
    error.hidden = false;
  }

  async function loadProduct() {
    var productId = getProductId();
    if (!productId) {
      showError("This product page does not have a product ID.");
      return;
    }

    try {
      var responses = await Promise.all([
        fetch("/api/catalog"),
        fetch("/api/products/" + encodeURIComponent(productId) + "/retailer-prices"),
        fetch("/api/retailers")
      ]);
      if (responses.some(function (response) { return !response.ok; })) {
        throw new Error("One or more product data requests failed.");
      }
      var data = await Promise.all(responses.map(function (response) { return response.json(); }));
      var products = data[0].products || [];
      var product = products.find(function (item) { return item.id === productId; });
      if (!product) {
        showError("This product is not in the verified catalog.");
        return;
      }
      var retailerNames = {};
      (data[2].retailers || []).forEach(function (retailer) {
        retailerNames[retailer.id] = retailer.name;
      });
      renderProduct(
        product,
        products,
        data[1].retailer_prices || [],
        retailerNames
      );
    } catch (error) {
      console.error("Could not load product page data.", error);
      showError("Product data could not be loaded. Try refreshing the page.");
    }
  }

  document.querySelectorAll(".product-range-buttons button").forEach(function (button) {
    button.addEventListener("click", function () {
      currentRange = button.dataset.range;
      document.querySelectorAll(".product-range-buttons button").forEach(function (item) {
        item.setAttribute("aria-pressed", String(item === button));
      });
      if (loadedProductData) {
        updateStats(loadedProductData.points, loadedProductData.observations, currentRange);
        drawChart(loadedProductData.points, currentRange);
      }
    });
  });

  loadProduct();
})();
