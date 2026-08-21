const state = { products: [], histories: {}, selectedId: null };

const productList = document.querySelector('#product-list');
const status = document.querySelector('#status');
const productCount = document.querySelector('#product-count');
const latestScrape = document.querySelector('#latest-scrape');
const chartUnit = document.querySelector('#chart-unit');
const chart = d3.select('#price-chart');
const emptyChart = document.querySelector('#empty-chart');

// Muted colors keep overlapping product histories distinct without becoming loud.
const colorScale = d3.scaleOrdinal([
  '#284b63',
  '#3c6e71',
  '#9b5c4a',
  '#b18432',
  '#a86b45',
  '#7c4f5a',
  '#6e7f86',
]);

function formatPrice(value, currency = 'EUR') {
  if (value === null || value === undefined) return 'No price';
  return new Intl.NumberFormat('es-ES', { style: 'currency', currency }).format(value);
}

function renderProducts() {
  productList.replaceChildren();
  state.products.forEach(product => {
    const button = document.createElement('button');
    button.className = 'product-button';
    button.dataset.productId = product.id;
    button.innerHTML = `<span class="product-name">${product.name}</span><span class="product-price">${formatPrice(product.price, product.currency)}</span>`;
    
    // Hover over sidebar button to highlight corresponding line on the chart
    button.addEventListener('mouseenter', () => highlightProduct(product.id));
    button.addEventListener('mouseleave', () => resetHighlight());
    
    // Click button to isolate/select product title
    button.addEventListener('click', () => selectProduct(product.id));
    productList.append(button);
  });
}

function drawChart() {
  const width = chart.node().clientWidth || 600;
  const height = 350;
  const margin = { top: 20, right: 20, bottom: 42, left: 58 };
  
  chart.attr('viewBox', `0 0 ${width} ${height}`).selectAll('*').remove();

  // Combine all product histories into arrays for plotting
  const allSeries = state.products.map(product => {
    const rawHistory = state.histories[product.id] || [];
    return {
      product,
      values: rawHistory.map(item => ({ ...item, date: new Date(item.scraped_at) }))
    };
  }).filter(series => series.values.length > 0);

  const hasData = allSeries.length > 0;
  emptyChart.hidden = hasData;
  chartUnit.textContent = hasData ? 'price per unit' : '';
  if (!hasData) return;

  // Flatten values across all products to calculate global X and Y domains
  const allPoints = allSeries.flatMap(s => s.values);
  const x = d3.scaleTime()
    .domain(d3.extent(allPoints, d => d.date))
    .range([margin.left, width - margin.right]);

  const y = d3.scaleLinear()
    .domain([0, d3.max(allPoints, d => d.unit_price_eur) * 1.15 || 1])
    .nice()
    .range([height - margin.bottom, margin.top]);

  const line = d3.line()
    .x(d => x(d.date))
    .y(d => y(d.unit_price_eur));

  // Axes
  chart.append('g')
    .attr('class', 'axis')
    .attr('transform', `translate(0,${height - margin.bottom})`)
    .call(d3.axisBottom(x).ticks(5));

  chart.append('g')
    .attr('class', 'axis')
    .attr('transform', `translate(${margin.left},0)`)
    .call(d3.axisLeft(y).ticks(5).tickFormat(value => `${value.toFixed(2)}€`));

  // Render Overlaid Lines (50% Opacity)
  allSeries.forEach(series => {
    const lineColor = colorScale(series.product.id);

    chart.append('path')
      .datum(series.values)
      .attr('class', `chart-line line-product-${series.product.id}`)
      .attr('d', line)
      .attr('fill', 'none')
      .style('stroke', lineColor)
      .attr('stroke-width', 2)
      .attr('opacity', 0.5);

    // Data points for hover feedback
    chart.selectAll(`.chart-dot-${series.product.id}`)
      .data(series.values)
      .join('circle')
      .attr('class', `chart-dot chart-dot-${series.product.id}`)
      .attr('r', 4)
      .attr('cx', item => x(item.date))
      .attr('cy', item => y(item.unit_price_eur))
      .style('fill', lineColor)
      .style('stroke', lineColor)
      .attr('opacity', 0.5)
      .on('mouseenter', () => highlightProduct(series.product.id))
      .on('mouseleave', () => resetHighlight())
      .append('title')
      .text(item => `${series.product.name}\n${formatPrice(item.unit_price_eur)} - ${item.scraped_at}`);
  });
}

function highlightProduct(productId) {
  // Dim all lines to 15% opacity, highlight selected line at 100% opacity
  chart.selectAll('.chart-line')
    .attr('opacity', 0.15)
    .attr('stroke-width', 2);

  chart.selectAll('.chart-dot')
    .attr('opacity', 0.15);

  chart.selectAll(`.line-product-${productId}`)
    .attr('opacity', 1)
    .attr('stroke-width', 4);

  chart.selectAll(`.chart-dot-${productId}`)
    .attr('opacity', 1);
}

function resetHighlight() {
  // Restore all lines to 50% opacity
  chart.selectAll('.chart-line')
    .attr('opacity', 0.5)
    .attr('stroke-width', 2);

  chart.selectAll('.chart-dot')
    .attr('opacity', 0.5);
}

function selectProduct(productId) {
  state.selectedId = productId;
  document.querySelectorAll('.product-button').forEach(button => {
    button.classList.toggle('is-selected', Number(button.dataset.productId) === productId);
  });
}

async function loadProducts() {
  const response = await fetch('/api/products');
  state.products = await response.json();
  productCount.textContent = state.products.length;
  latestScrape.textContent = state.products.reduce((latest, item) => item.scraped_at > latest ? item.scraped_at : latest, '-') || '-';
  status.textContent = state.products.length ? 'Loading history...' : 'No database records';

  renderProducts();

  // Fetch price history for all products in parallel
  const historyPromises = state.products.map(product =>
    fetch(`/api/products/${product.id}/price-history`)
      .then(res => res.json())
      .then(data => { state.histories[product.id] = data; })
  );

  await Promise.all(historyPromises);

  status.textContent = state.products.length ? 'Ready' : 'No database records';
  drawChart();
}

loadProducts().catch(error => { 
  status.textContent = 'Unable to load data'; 
  console.error(error); 
});