const state = { products: [], selectedId: null };

const productList = document.querySelector('#product-list');
const status = document.querySelector('#status');
const productCount = document.querySelector('#product-count');
const latestScrape = document.querySelector('#latest-scrape');
const chartTitle = document.querySelector('#chart-title');
const chartUnit = document.querySelector('#chart-unit');
const chart = d3.select('#price-chart');
const emptyChart = document.querySelector('#empty-chart');

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
    button.addEventListener('click', () => selectProduct(product.id));
    productList.append(button);
  });
  if (state.products.length && state.selectedId === null) selectProduct(state.products[0].id);
}

function drawChart(product, history) {
  const width = chart.node().clientWidth || 600;
  const height = 350;
  const margin = { top: 20, right: 20, bottom: 42, left: 58 };
  chart.attr('viewBox', `0 0 ${width} ${height}`).selectAll('*').remove();
  emptyChart.hidden = history.length > 0;
  chartTitle.textContent = product.name;
  chartUnit.textContent = history.length ? 'price per unit' : '';
  if (!history.length) return;

  const values = history.map(item => ({ ...item, date: new Date(item.scraped_at) }));
  const x = d3.scaleTime().domain(d3.extent(values, item => item.date)).range([margin.left, width - margin.right]);
  const y = d3.scaleLinear().domain([0, d3.max(values, item => item.unit_price_eur) * 1.15 || 1]).nice().range([height - margin.bottom, margin.top]);
  const line = d3.line().x(item => x(item.date)).y(item => y(item.unit_price_eur));
  chart.append('g').attr('class', 'axis').attr('transform', `translate(0,${height - margin.bottom})`).call(d3.axisBottom(x).ticks(Math.min(values.length, 5)));
  chart.append('g').attr('class', 'axis').attr('transform', `translate(${margin.left},0)`).call(d3.axisLeft(y).ticks(5).tickFormat(value => `${value.toFixed(2)}€`));
  chart.append('path').datum(values).attr('class', 'chart-line').attr('d', line);
  chart.selectAll('.chart-dot').data(values).join('circle').attr('class', 'chart-dot').attr('r', 5).attr('cx', item => x(item.date)).attr('cy', item => y(item.unit_price_eur)).append('title').text(item => `${formatPrice(item.unit_price_eur)} - ${item.scraped_at}`);
}

async function selectProduct(productId) {
  state.selectedId = productId;
  document.querySelectorAll('.product-button').forEach(button => button.classList.toggle('is-selected', Number(button.dataset.productId) === productId));
  const product = state.products.find(item => item.id === productId);
  const history = await fetch(`/api/products/${productId}/price-history`).then(response => response.json());
  drawChart(product, history);
}

async function loadProducts() {
  const response = await fetch('/api/products');
  state.products = await response.json();
  productCount.textContent = state.products.length;
  latestScrape.textContent = state.products.reduce((latest, item) => item.scraped_at > latest ? item.scraped_at : latest, '-') || '-';
  status.textContent = state.products.length ? 'Ready' : 'No database records';
  renderProducts();
}

loadProducts().catch(error => { status.textContent = 'Unable to load data'; console.error(error); });