window.mockCatalog = (function() {
  function history(base, range, trend, seed) {
    var count = 30;
    var values = [];
    var value = base;
    var offset = seed * 0.017;

    for (var i = 0; i < count; i++) {
      var progress = i / (count - 1);
      var wave = Math.sin((i + seed) * 0.82) * (base * 0.006);
      var smallMove = Math.cos((i * 1.37) + offset) * (base * 0.003);
      var rangeScale = range === '1d' ? 0.002 : range === '1w' ? 0.004 : range === '1m' ? 0.008 : 0.012;
      value = base + (base * trend * progress) + wave * rangeScale / 0.008 + smallMove;
      values.push(Math.round(value * 100) / 100);
    }

    values[count - 1] = base * (1 + trend);
    values[count - 1] = Math.round(values[count - 1] * 100) / 100;
    values.dates = mockDates(count, range);
    return values;
  }

  function mockDates(count, range) {
    var end = new Date(2026, 10, 23, 12, 0, 0);
    var dates = [];
    for (var i = 0; i < count; i++) {
      var date = new Date(end);
      if (range === '1d') {
        date.setHours(Math.floor(i * 24 / count), (i * 60 / count) % 60, 0, 0);
      } else if (range === '1w') {
        date.setDate(end.getDate() - (count - 1 - i));
      } else if (range === '1m') {
        date.setDate(end.getDate() - (count - 1 - i));
      } else if (range === '1y') {
        date.setDate(end.getDate() - Math.round((count - 1 - i) * 365 / (count - 1)));
      } else {
        date.setMonth(end.getMonth() - Math.round((count - 1 - i) * 36 / (count - 1)));
      }
      dates.push(date);
    }
    return dates;
  }

  function ranges(base, trend, seed) {
    return {
      '1d': history(base, '1d', trend * 0.25, seed),
      '1w': history(base, '1w', trend * 0.5, seed + 1),
      '1m': history(base, '1m', trend, seed + 2),
      '1y': history(base, '1y', trend * 2, seed + 3),
      'all': history(base, '1y', trend * 3, seed + 4)
    };
  }

  var products = [
    { id: 'asus-dual-rtx5070-12g', name: 'ASUS Dual RTX 5070 12GB', mpn: 'DUAL-RTX5070-12G', category: 'GPUs', brand: 'ASUS', price: 579.99, change: -0.3, trend: -0.003, seed: 11, retailers: ['Newegg', 'Micro Center'] },
    { id: 'rtx3080', name: 'RTX 3080', mpn: 'MPN to check', category: 'GPUs', brand: 'NVIDIA', price: 999.99, change: 0.5, trend: 0.005, seed: 14, retailers: ['Newegg', 'Micro Center'] },
    { id: 'rtx2060', name: 'RTX 2060', mpn: 'MPN to check', category: 'GPUs', brand: 'NVIDIA', price: 349.99, change: -1.2, trend: -0.012, seed: 17, retailers: ['Newegg', 'Micro Center'] },
    { id: 'amd-ryzen-7-9800x3d', name: 'AMD Ryzen 7 9800X3D', mpn: '100-100001084WOF', category: 'CPUs', brand: 'AMD', price: 469.99, change: 0.8, trend: 0.008, seed: 21, retailers: ['Newegg', 'Best Buy', 'Micro Center', 'B and H'] },
    { id: 'amd-ryzen-5-7600x', name: 'AMD Ryzen 5 7600X', mpn: 'MPN to check', category: 'CPUs', brand: 'AMD', price: 249.99, change: -1.5, trend: -0.015, seed: 24, retailers: ['Newegg', 'Micro Center'] },
    { id: 'intel-core-i7-14700k', name: 'Intel Core i7-14700K', mpn: 'MPN to check', category: 'CPUs', brand: 'Intel', price: 399.99, change: 0.3, trend: 0.003, seed: 28, retailers: ['Newegg', 'Micro Center', 'Best Buy'] },
    { id: 'corsair-vengeance-32gb-ddr5-6000-cl30', name: 'Corsair Vengeance 32GB DDR5-6000 CL30', mpn: 'CMK32GX5M2B6000Z30', category: 'RAM', brand: 'Corsair', price: 239.99, change: -2.1, trend: -0.021, seed: 31, retailers: ['Newegg', 'Best Buy', 'B and H'] },
    { id: 'gskill-trident-z5-32gb-ddr5-6000-cl30', name: 'G.Skill Trident Z5 32GB DDR5-6000 CL30', mpn: 'MPN to check', category: 'RAM', brand: 'G.Skill', price: 259.99, change: -0.9, trend: -0.009, seed: 35, retailers: ['Newegg', 'Micro Center'] },
    { id: 'kingston-fury-beast-32gb-ddr5-5600', name: 'Kingston Fury Beast 32GB DDR5-5600', mpn: 'MPN to check', category: 'RAM', brand: 'Kingston', price: 189.99, change: 1.1, trend: 0.011, seed: 39, retailers: ['Newegg', 'Amazon'] }
  ];

  products.forEach(function(product) {
    product.histories = ranges(product.price, product.trend, product.seed);
  });

  return {
    products: products,
    aliases: {
      'asus-dual-rtx-5070': 'asus-dual-rtx5070-12g',
      'rtx-3080': 'rtx3080',
      'rtx-2060': 'rtx2060',
      'amd-ryzen-5-7600x': 'amd-ryzen-5-7600x',
      'intel-core-i7-14700k': 'intel-core-i7-14700k',
      'corsair-vengeance-32gb-ddr5-6000-cl30': 'corsair-vengeance-32gb-ddr5-6000-cl30',
      'gskill-trident-z5-32gb-ddr5-6000-cl30': 'gskill-trident-z5-32gb-ddr5-6000-cl30',
      'kingston-fury-beast-32gb-ddr5-5600': 'kingston-fury-beast-32gb-ddr5-5600'
    },
    getById: function(id) {
      var resolvedId = this.aliases[id] || id;
      return products.find(function(product) { return product.id === resolvedId; });
    },
    getByCategory: function(category) {
      return products.filter(function(product) { return product.category === category; });
    }
  };
})();
