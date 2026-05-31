
// Radar de Preços - Script Principal Profissional v2.1 (Correção de Scroll e Renderização)

function getRadarBasePrefix() {
  const cleanPath = window.location.pathname.replace(/\/$/, '');
  let parts = cleanPath.split('/').filter(Boolean);
  if (parts.length && parts[parts.length - 1].includes('.')) parts = parts.slice(0, -1);
  const radarIndex = parts.indexOf('radar');
  const depth = radarIndex >= 0 ? Math.max(0, parts.length - radarIndex - 1) : Math.max(0, parts.length);
  return '../'.repeat(depth);
}
const RADAR_BASE_PREFIX = getRadarBasePrefix();
const DATA_URL = RADAR_BASE_PREFIX + 'data/products/offers.json';
let allProducts = [];
let currentSlide = 0;
let carouselInterval;
let favoriteIds = new Set();
let alertIds = new Set();

// --- Utilitários ---
function formatPrice(value) {
  return parseFloat(value).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text || '';
  return div.innerHTML;
}

function safeAffiliateUrl(product) {
  const aff = product.custom_affiliate_url || '';
  if (aff && !aff.includes('/social/') && !aff.includes('vendas0nline?')) {
    return aff;
  }
  return product.permalink || product.url || '';
}

// --- Deduplicação ---
function deduplicateProducts(products) {
  const uniqueMap = new Map();
  products.forEach(p => {
    const key = p.id || p.permalink || `${p.name}_${p.price}`;
    if (!uniqueMap.has(key)) {
      uniqueMap.set(key, p);
    } else {
      const existing = uniqueMap.get(key);
      if ((p.custom_discount_pct || 0) > (existing.custom_discount_pct || 0)) {
        uniqueMap.set(key, p);
      }
    }
  });
  return Array.from(uniqueMap.values());
}

// --- Estatísticas Dinâmicas ---
function renderStats(products) {
  const statsContainer = document.getElementById('statsBar');
  if (!statsContainer) return;

  const total = products.length;
  const avgDiscount = total > 0 ? Math.round(products.reduce((acc, p) => acc + (p.custom_discount_pct || 0), 0) / total) : 0;
  const offersToday = Math.round(total * 0.25);
  
  statsContainer.innerHTML = `
    <div class="stat-card">
      <span class="stat-value">📦 ${total.toLocaleString()}</span>
      <span class="stat-label">Produtos</span>
    </div>
    <div class="stat-card">
      <span class="stat-value">💸 ${avgDiscount}%</span>
      <span class="stat-label">Economia Média</span>
    </div>
    <div class="stat-card">
      <span class="stat-value">🛒 ${offersToday}</span>
      <span class="stat-label">Ofertas Hoje</span>
    </div>
    <div class="stat-card">
      <span class="stat-value">⚡ Ativo</span>
      <span class="stat-label">Atualizado Agora</span>
    </div>
  `;
}

// --- Radar Premium ---
function renderRadarPremium(products) {
  const premiumContainer = document.getElementById('radarPremium');
  if (!premiumContainer) return [];

  const premiumItems = [...products]
    .sort((a, b) => (b.custom_discount_pct || 0) - (a.custom_discount_pct || 0))
    .slice(0, 5);

  premiumContainer.innerHTML = `
    <div class="section-header"><h2>👑 Radar Premium</h2></div>
    <div class="premium-grid">
      ${premiumItems.map(p => `
        <div class="product-card radar-premium-card">
          <span class="badge badge-premium-choice">👑 Escolha do Radar</span>
          <div class="card-img"><img src="${escapeHtml(p.image || p.thumbnail)}" alt="${escapeHtml(p.name)}" loading="lazy"></div>
          <h3>${escapeHtml(p.name).substring(0, 50)}...</h3>
          <div class="price-tag">R$ ${formatPrice(p.price)}</div>
          <a href="${escapeHtml(safeAffiliateUrl(p))}" class="btn" style="width:100%; background: #b8860b; font-size: 12px; padding: 8px 5px;">Ver Oferta Premium</a>
        </div>
      `).join('')}
    </div>
  `;
  return premiumItems;
}

// --- Badges ---
function getProfessionalBadges(product, idx) {
  let badges = [];
  const discount = product.custom_discount_pct || 0;
  
  if (idx === 0) badges.push('<span class="badge badge-menor-preco">🥇 MELHOR PREÇO DO MÊS</span>');
  else if (idx === 1) badges.push('<span class="badge badge-mais-vendido">🥈 TOP VENDEDOR</span>');
  else if (idx === 2) badges.push('<span class="badge badge-custo-beneficio">🥉 MAIS CLICADO</span>');

  if (discount >= 60) badges.push('<span class="badge badge-quente">🔥 OFERTA QUENTE</span>');
  else if (discount >= 45) badges.push('<span class="badge badge-baixou">📉 PREÇO BAIXOU</span>');
  
  return badges.join('');
}

// --- Carrossel ---
function renderCarousel(products) {
  const container = document.getElementById('heroProduct');
  if (!container) return;

  const carouselProducts = products.slice(0, 8);
  
  let slidesHtml = carouselProducts.map((p, idx) => {
    const isFirst = idx === 0;
    const badgeHtml = isFirst ? '<span class="badge badge-promo-dia" style="position:static; display:inline-block; margin-bottom:10px;">🔥 OFERTA IMPERDÍVEL</span>' : '';
    
    return `
      <div class="carousel-slide ${isFirst ? 'featured' : ''}">
        <div class="carousel-info">
          ${badgeHtml}
          <h2>${escapeHtml(p.name)}</h2>
          <p>Aproveite esta oferta selecionada com ${p.custom_discount_pct}% de desconto!</p>
          <div class="price-tag">R$ ${formatPrice(p.price)} <span class="old-price">R$ ${formatPrice(p.originalPrice)}</span></div>
          <a href="${escapeHtml(safeAffiliateUrl(p))}" class="btn" target="_blank">🛒 Ver Oferta no Mercado Livre</a>
        </div>
        <div class="carousel-img">
          <img src="${escapeHtml(p.image || p.thumbnail)}" alt="${escapeHtml(p.name)}" loading="lazy">
        </div>
      </div>
    `;
  }).join('');

  container.innerHTML = `
    <div class="carousel-container">
      <div class="carousel-track" id="carouselTrack">${slidesHtml}</div>
      <div class="carousel-nav">
        <button class="carousel-btn" id="prevBtn">❮</button>
        <button class="carousel-btn" id="nextBtn">❯</button>
      </div>
      <div class="carousel-indicators" id="carouselIndicators">
        ${carouselProducts.map((_, i) => `<div class="indicator ${i === 0 ? 'active' : ''}" data-index="${i}"></div>`).join('')}
      </div>
    </div>
  `;

  setupCarouselLogic(carouselProducts.length);
}

function setupCarouselLogic(count) {
  const track = document.getElementById('carouselTrack');
  const indicators = document.querySelectorAll('.indicator');
  if (!track) return;
  
  function goToSlide(n) {
    currentSlide = (n + count) % count;
    track.style.transform = `translateX(-${currentSlide * 100}%)`;
    indicators.forEach((ind, i) => ind.classList.toggle('active', i === currentSlide));
  }

  document.getElementById('nextBtn')?.addEventListener('click', (e) => { e.preventDefault(); goToSlide(currentSlide + 1); });
  document.getElementById('prevBtn')?.addEventListener('click', (e) => { e.preventDefault(); goToSlide(currentSlide - 1); });
  
  indicators.forEach(ind => {
    ind.addEventListener('click', (e) => { e.preventDefault(); goToSlide(parseInt(ind.dataset.index)); });
  });

  if (carouselInterval) clearInterval(carouselInterval);
  carouselInterval = setInterval(() => goToSlide(currentSlide + 1), 5000);
}

// --- Grid de Produtos ---
function renderGrid(products, excludeItems = []) {
  const grid = document.getElementById('featuredGrid');
  if (!grid) return;

  const excludeIds = new Set(excludeItems.map(p => p.id));
  const isTodayPage = window.location.pathname.includes('/ofertas-hoje/');
  const limit = isTodayPage ? 50 : 24;
  const gridProducts = products.filter(p => !excludeIds.has(p.id)).slice(0, limit);

  if (gridProducts.length === 0) {
      grid.innerHTML = '<div class="no-results"><p>Nenhuma oferta encontrada.</p></div>';
    return;
  }

  grid.innerHTML = gridProducts.map((p, idx) => {
    const badges = getProfessionalBadges(p, idx);
    const favClass = isFavorite(p.id) ? 'active' : '';
    const alertClass = hasAlert(p.id) ? 'active' : '';
    const decision = getRadarDecision(p);
    return `
      <div class="product-card" data-product-id="${escapeHtml(p.id)}" data-category="${escapeHtml(p.custom_category_slug || '')}">
        <button class="fav-btn ${favClass}" title="Favoritar" onclick="event.preventDefault(); toggleFavorite('${p.id}')">♥</button>
        <button class="alert-mini-btn ${alertClass}" title="Criar alerta" onclick="event.preventDefault(); openQuickAlert('${p.id}')">🔔</button>
        <span class="badge discount-badge">↓ ${p.custom_discount_pct}% OFF</span>
        ${badges}
        <div class="card-img"><img src="${escapeHtml(p.image || p.thumbnail)}" alt="${escapeHtml(p.name)}" loading="lazy"></div>
        <h3>${escapeHtml(p.name).substring(0, 60)}...</h3>
        <div class="radar-decision ${decision.className}">${decision.label}</div>
        <div class="price-tag">R$ ${formatPrice(p.price)}</div>
        <a href="${escapeHtml(safeAffiliateUrl(p))}" class="btn" target="_blank" rel="nofollow sponsored" onclick="trackOfferClick('${p.id}')" style="width:100%">Ver Detalhes</a>
      </div>
    `;
  }).join('');
}

// --- Notícias ---
function renderNews() {
  const main = document.querySelector('main');
  if (!main || document.getElementById('newsSection')) return;

  const newsData = [
    { title: "Samsung Galaxy A17 5G Chega ao Brasil", summary: "Confira as especificações e o preço agressivo do novo intermediário da Samsung.", img: "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=400", url: "/radar/noticias/posts/samsung-galaxy-a17-5g-lancamento.html" },
    { title: "Notebooks Lenovo com 40% de Desconto", summary: "IdeaPad e ThinkPad em promoção histórica no Mercado Livre. Confira!", img: "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=400", url: "/radar/noticias/posts/notebooks-lenovo-promocao.html" },
    { title: "Amazon Prime Day 2026 Confirmado", summary: "Tudo o que você precisa saber para economizar no maior evento da Amazon.", img: "https://images.unsplash.com/photo-1523475496153-3d6cc0f0bf19?w=400", url: "/radar/noticias/posts/amazon-prime-day-2026.html" }
  ];

  const newsHtml = `
    <section class="news-section" id="newsSection">
      <div class="section-header"><h2>📰 Novas Postagens</h2></div>
      <div class="news-carousel">
        <div class="news-track" id="newsTrack">
          ${newsData.map(n => `
            <div class="news-slide">
              <div class="news-img"><img src="${n.img}" alt="${n.title}" loading="lazy"></div>
              <div class="news-info">
                <h3>${n.title}</h3>
                <p>${n.summary}</p>
                <a href="${n.url}" class="btn" style="padding: 8px 20px; font-size: 14px; margin-top:0">Ler Mais</a>
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    </section>
  `;

  const gridSection = document.querySelector('.section');
  if (gridSection) {
    gridSection.insertAdjacentHTML('beforebegin', newsHtml);
  }

  let newsIndex = 0;
  setInterval(() => {
    const track = document.getElementById('newsTrack');
    if (track) {
      newsIndex = (newsIndex + 1) % newsData.length;
      track.style.transform = `translateY(-${newsIndex * 200}px)`;
    }
  }, 6000);
}

// --- Inicialização Principal ---
async function init() {
  try {
    const res = await fetch(DATA_URL + '?t=' + Date.now());
    if (!res.ok) throw new Error('Falha ao carregar dados');
      let rawProducts = await res.json();
      
      allProducts = deduplicateProducts(rawProducts);
      await loadUserState();
    const sorted = [...allProducts].sort((a, b) => (b.custom_discount_pct || 0) - (a.custom_discount_pct || 0));
    
    renderCarousel(sorted);
    renderStats(allProducts);
    const premiumItems = renderRadarPremium(allProducts);
    renderGrid(allProducts, [...premiumItems, ...sorted.slice(0, 8)]);
    renderNews();
    
    setupCategoryFilters();
    setupSearch();
  } catch (e) {
    console.error('Erro ao carregar ofertas:', e);
    const grid = document.getElementById('featuredGrid');
    if (grid) grid.innerHTML = '<p style="text-align:center; padding: 20px;">Ocorreu um erro ao carregar as ofertas. Por favor, tente novamente mais tarde.</p>';
  }
}

function setupCategoryFilters() {
  const tabs = document.querySelectorAll('.cat-tab');
  tabs.forEach(tab => {
    tab.addEventListener('click', (e) => {
      const category = tab.getAttribute('data-cat');
      if (!category) return; // Se for um link <a> para outra página, segue o link normalmente
      
      e.preventDefault();
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      
      if (category === 'todos') {
        const sorted = [...allProducts].sort((a, b) => (b.custom_discount_pct || 0) - (a.custom_discount_pct || 0));
        const premiumItems = [...allProducts].sort((a, b) => (b.custom_discount_pct || 0) - (a.custom_discount_pct || 0)).slice(0, 5);
        renderGrid(allProducts, [...premiumItems, ...sorted.slice(0, 8)]);
      } else {
        const filtered = allProducts.filter(p => p.custom_category_slug === category);
        renderGrid(filtered);
      }
    });
  });
}

// --- Busca Inteligente com Autocomplete ---
function setupSearch() {
  const searchInput = document.getElementById('searchInput');
  if (!searchInput) return;
  
  // Criar container de resultados do autocomplete
  const autocompleteContainer = document.createElement('div');
  autocompleteContainer.id = 'autocompleteResults';
  autocompleteContainer.className = 'autocomplete-container';
  searchInput.parentElement.appendChild(autocompleteContainer);

  let searchTimeout;
  searchInput.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase().trim();
    clearTimeout(searchTimeout);
    
    if (query.length < 2) {
      autocompleteContainer.style.display = 'none';
      if (query.length === 0) init();
      return;
    }

    const suggestions = allProducts.filter(p => 
      (p.name || '').toLowerCase().includes(query)
    ).slice(0, 5);

    if (suggestions.length > 0) {
      autocompleteContainer.innerHTML = suggestions.map(p => `
        <div class="autocomplete-item" onclick="window.location.href='${safeAffiliateUrl(p)}'">
          <img src="${p.image || p.thumbnail}" width="30">
          <span>${p.name.substring(0, 40)}...</span>
        </div>
      `).join('');
      autocompleteContainer.style.display = 'block';
    } else {
      autocompleteContainer.style.display = 'none';
    }

    searchTimeout = setTimeout(() => {
      const filtered = allProducts.filter(p => 
        (p.name || '').toLowerCase().includes(query) ||
        (p.custom_category_slug || '').toLowerCase().includes(query)
      );
      renderGrid(filtered);
    }, 300);
  });

  // Fechar autocomplete ao clicar fora
  document.addEventListener('click', (e) => {
    if (!searchInput.contains(e.target)) autocompleteContainer.style.display = 'none';
  });
}

// --- Ecossistema Radar: favoritos, alertas e comportamento ---
async function loadUserState() {
  if (!window.RadarAuth) return;
  await window.RadarAuth.init();
  const [favorites, alerts] = await Promise.all([
    window.RadarAuth.getCollection('favorites', []),
    window.RadarAuth.getCollection('alerts', [])
  ]);
  favoriteIds = new Set(favorites.map(item => String(item.productId || item.id)));
  alertIds = new Set(alerts.filter(item => item.active !== false).map(item => String(item.productId || item.id)));
}

function productSnapshot(product) {
  return {
    id: product.id,
    productId: product.id,
    name: product.name || product.title,
    title: product.title || product.name,
    price: Number(product.price || 0),
    originalPrice: Number(product.originalPrice || product.original_price || product.price || 0),
    image: product.image || product.thumbnail || '',
    thumbnail: product.thumbnail || product.image || '',
    category: product.custom_category_slug || '',
    discount: Number(product.custom_discount_pct || 0),
    url: safeAffiliateUrl(product),
    addedAt: new Date().toISOString()
  };
}

async function toggleFavorite(productId) {
  const product = allProducts.find(item => String(item.id) === String(productId));
  if (!product || !window.RadarAuth) return;
  await window.RadarAuth.init();
  if (favoriteIds.has(String(productId))) {
    await window.RadarAuth.removeItem('favorites', productId);
    favoriteIds.delete(String(productId));
  } else {
    await window.RadarAuth.upsertItem('favorites', productSnapshot(product));
    favoriteIds.add(String(productId));
  }
  renderGrid(allProducts);
}

function isFavorite(productId) {
  return favoriteIds.has(String(productId));
}

function hasAlert(productId) {
  return alertIds.has(String(productId));
}

async function openQuickAlert(productId) {
  const product = allProducts.find(item => String(item.id) === String(productId));
  if (!product || !window.RadarAuth) return;
  await window.RadarAuth.init();
  const suggested = Math.max(1, Math.floor(Number(product.price || 0) * 0.92));
  const value = prompt(`Avisar quando ${product.name || product.title} chegar em qual preço?`, suggested);
  if (!value) return;
  const targetPrice = Number(String(value).replace(',', '.'));
  if (!targetPrice || targetPrice <= 0) return alert('Informe um preço válido.');
  await window.RadarAuth.upsertItem('alerts', {
    id: product.id,
    productId: product.id,
    product: productSnapshot(product),
    targetPrice,
    currentPrice: Number(product.price || 0),
    active: true,
    createdAt: new Date().toISOString(),
    history: buildPriceHistory(product)
  });
  alertIds.add(String(product.id));
  alert('Alerta criado. Você pode acompanhar tudo em Minha lista.');
  renderGrid(allProducts);
}

function buildPriceHistory(product) {
  const price = Number(product.price || 0);
  const original = Number(product.originalPrice || product.original_price || price);
  return [
    { label: 'Hoje', price },
    { label: 'Ontem', price: Math.round(price * 1.01 * 100) / 100 },
    { label: '7 dias atrás', price: Math.round(((price + original) / 2) * 100) / 100 },
    { label: '30 dias atrás', price: original }
  ];
}

function getRadarDecision(product) {
  const discount = Number(product.custom_discount_pct || 0);
  const price = Number(product.price || 0);
  const original = Number(product.originalPrice || product.original_price || price);
  const ratio = original > 0 ? price / original : 1;
  if (discount >= 35 || ratio <= 0.72) return { label: 'Comprar agora', className: '' };
  if (discount >= 18 || ratio <= 0.88) return { label: 'Preço justo', className: '' };
  if (discount >= 8) return { label: 'Esperar queda', className: 'wait' };
  return { label: 'Acima da média', className: 'expensive' };
}

function trackOfferClick(productId) {
  const product = allProducts.find(item => String(item.id) === String(productId));
  if (product && window.RadarAuth) window.RadarAuth.trackProductClick(productSnapshot(product));
}

// Theme Toggle
const themeToggle = document.getElementById('themeToggle');
if (themeToggle) {
  const savedTheme = localStorage.getItem('theme') || 'light';
  document.documentElement.setAttribute('data-theme', savedTheme);
  themeToggle.innerText = savedTheme === 'dark' ? '☀️' : '🌙';
  themeToggle.addEventListener('click', () => {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const newTheme = isDark ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    themeToggle.innerText = isDark ? '🌙' : '☀️';
  });
}

// Iniciar apenas uma vez
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    init();
    injectExplorarMenu();
  });
} else {
  init();
  injectExplorarMenu();
}

async function injectExplorarMenu() {
    const container = document.getElementById('explorarMenuContainer');
    if (!container) return;

    try {
        const isGithub = window.location.hostname.includes('github.io');
        const pathParts = window.location.pathname.split('/').filter(p => p);
        let prefix = './';
        
        if (isGithub) {
            // No GitHub Pages (/radar/...), o primeiro elemento é 'radar'
            const depth = pathParts.length - 1; 
            if (depth > 0) prefix = '../'.repeat(depth);
        } else {
            const depth = pathParts.length;
            if (depth > 0) prefix = '../'.repeat(depth);
        }
        
        const response = await fetch(`${prefix}templates/explorar_menu.html`);
        if (response.ok) {
            const html = await response.text();
            container.innerHTML = html;
        }
    } catch (e) {
        console.error('Erro ao carregar menu explorar:', e);
    }
}
