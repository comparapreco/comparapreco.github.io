// ========== CONFIGURAÇÃO ==========
const BASE_URL = 'https://comparapreco.github.io/';
const DATA_URL = 'data/products/offers.json';

let allProducts = [];
let favoriteIds = new Set();
let alertIds = new Set();

// ========== UTILITÁRIOS ==========
function formatPrice(value) {
  return parseFloat(value).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text || '';
  return div.innerHTML;
}

function getOfferBadges(product, index) {
  const badges = [];
  const discount = product.custom_discount_pct || 0;
  
  // Menor Preço da História
  if (discount >= 40) {
    badges.push('<span class="badge badge-lowest" style="background: #ff6b6b; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; margin: 2px;">🏆 MENOR PREÇO</span>');
  }
  
  // Baixou
  if (discount >= 25 && discount < 40) {
    badges.push('<span class="badge badge-down" style="background: #51cf66; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; margin: 2px;">📉 BAIXOU</span>');
  }
  
  // Destaque
  if (index < 5) {
    badges.push('<span class="badge badge-featured" style="background: #ffd43b; color: #333; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; margin: 2px;">⭐ DESTAQUE</span>');
  }
  
  return badges.join(' ');
}

// ========== RENDERIZAÇÃO DE PRODUTOS ==========

function renderProducts(products) {
  const grid = document.getElementById('featuredGrid');
  if (!grid) return;

  if (products.length === 0) {
    grid.innerHTML = '<p style="text-align: center; padding: 40px;">Nenhuma oferta encontrada.</p>';
    return;
  }

  const sorted = [...products].sort((a, b) => (b.custom_discount_pct || 0) - (a.custom_discount_pct || 0));
  const limited = sorted.slice(0, 24);

  grid.innerHTML = limited.map((p, idx) => {
    const badges = getOfferBadges(p, idx);
    const affiliate = p.custom_affiliate_url || p.permalink || '#';
    
    return `
      <div class="product-card-refactored" onclick="window.open('${escapeHtml(affiliate)}', '_blank', 'noopener noreferrer')">
        <div class="product-card-img-container">
          <img src="${escapeHtml(p.image || p.thumbnail)}" alt="${escapeHtml(p.name)}" loading="lazy">
          <div class="product-card-discount">
            ↓ ${p.custom_discount_pct || 0}% OFF
          </div>
          <div class="product-card-badges">
            ${badges}
          </div>
        </div>
        <div class="product-card-content">
          <h3 class="product-card-title">
            ${escapeHtml(p.name)}
          </h3>
          <div class="product-card-old-price">
            R$ ${formatPrice(p.original_price || p.originalPrice || p.price)}
          </div>
          <div class="product-card-price">
            R$ ${formatPrice(p.price)}
          </div>
          <a href="${escapeHtml(affiliate)}" target="_blank" rel="noopener noreferrer" class="product-card-btn" onclick="event.stopPropagation()">
            Ver Oferta no ML
          </a>
        </div>
      </div>
    `;
  }).join('');
}

  const sorted = [...products].sort((a, b) => (b.custom_discount_pct || 0) - (a.custom_discount_pct || 0));
  const limited = sorted.slice(0, 24);

  grid.innerHTML = limited.map((p, idx) => {
    const badges = getOfferBadges(p, idx);
    const affiliate = p.custom_affiliate_url || p.permalink || '#';
    
    return `
      <div class="product-card" style="border: 1px solid #e0e0e0; border-radius: 12px; overflow: hidden; transition: all 0.3s; cursor: pointer;">
        <div style="position: relative; overflow: hidden; background: #f5f5f5; height: 200px; display: flex; align-items: center; justify-content: center;">
          <img src="${escapeHtml(p.image || p.thumbnail)}" alt="${escapeHtml(p.name)}" loading="lazy" style="max-width: 100%; max-height: 100%; object-fit: contain;">
          <div style="position: absolute; top: 10px; right: 10px; background: #ff6b6b; color: white; padding: 6px 12px; border-radius: 20px; font-weight: bold; font-size: 14px;">
            ↓ ${p.custom_discount_pct || 0}% OFF
          </div>
          <div style="position: absolute; top: 10px; left: 10px; display: flex; flex-wrap: wrap; gap: 4px;">
            ${badges}
          </div>
        </div>
        <div style="padding: 15px;">
          <h3 style="margin: 0 0 10px 0; font-size: 14px; font-weight: 600; line-height: 1.4; color: #333;">
            ${escapeHtml(p.name).substring(0, 60)}...
          </h3>
          <div style="margin-bottom: 10px;">
            <span style="font-size: 12px; color: #999; text-decoration: line-through;">R$ ${formatPrice(p.original_price || p.originalPrice || p.price)}</span>
          </div>
          <div style="font-size: 20px; font-weight: bold; color: #ff6b6b; margin-bottom: 15px;">
            R$ ${formatPrice(p.price)}
          </div>
          <a href="${escapeHtml(affiliate)}" target="_blank" rel="noopener noreferrer" class="btn" style="display: block; text-align: center; background: #667eea; color: white; padding: 10px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 14px;">
            Ver Oferta no ML
          </a>
        </div>
      </div>
    `;
  }).join('');
}

// ========== RENDERIZAÇÃO DE ESTATÍSTICAS ==========
function renderStats(products) {
  const statsBar = document.getElementById('statsBar');
  if (!statsBar) return;

  const total = products.length;
  const avgDiscount = total > 0 ? Math.round(products.reduce((acc, p) => acc + (p.custom_discount_pct || 0), 0) / total) : 0;

  statsBar.innerHTML = `
    <div class="stat-card">
      <span class="stat-value">📦 ${total.toLocaleString()}</span>
      <span class="stat-label">Produtos</span>
    </div>
    <div class="stat-card">
      <span class="stat-value">💸 ${avgDiscount}%</span>
      <span class="stat-label">Economia Média</span>
    </div>
    <div class="stat-card">
      <span class="stat-value">🛒 ${Math.round(total * 0.25)}</span>
      <span class="stat-label">Ofertas Hoje</span>
    </div>
    <div class="stat-card">
      <span class="stat-value">⚡ Ativo</span>
      <span class="stat-label">Atualizado Agora</span>
    </div>
  `;
}

// ========== RENDERIZAÇÃO DE BLOG ==========
async function renderBlog() {
  const blogGrid = document.getElementById('blogGrid');
  if (!blogGrid) return;

  try {
    const response = await fetch('noticias/index.html');
    const html = await response.text();
    
    // Extrair notícias do HTML
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');
    const newsItems = doc.querySelectorAll('[data-news-item]');
    
    if (newsItems.length === 0) {
      // Se não encontrar data-news-item, tenta outro seletor
      const fallbackItems = doc.querySelectorAll('.news-item, article');
      if (fallbackItems.length > 0) {
        let blogHtml = '';
        for (let i = 0; i < Math.min(3, fallbackItems.length); i++) {
          const item = fallbackItems[i];
          const title = item.querySelector('h3, h2')?.textContent || 'Artigo';
          const excerpt = item.querySelector('p')?.textContent || 'Leia mais...';
          const link = item.querySelector('a')?.href || 'noticias/';
          
          blogHtml += `
            <div style="background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
              <h3 style="margin: 0 0 10px 0; font-size: 16px; color: #333;">${escapeHtml(title)}</h3>
              <p style="margin: 0 0 15px 0; color: #666; font-size: 14px; line-height: 1.5;">${escapeHtml(excerpt.substring(0, 100))}...</p>
              <a href="${escapeHtml(link)}" style="color: #667eea; text-decoration: none; font-weight: bold;">Leia mais →</a>
            </div>
          `;
        }
        blogGrid.innerHTML = blogHtml;
      }
    } else {
      let blogHtml = '';
      for (let i = 0; i < Math.min(3, newsItems.length); i++) {
        const item = newsItems[i];
        const title = item.querySelector('h3')?.textContent || 'Artigo';
        const excerpt = item.querySelector('p')?.textContent || 'Leia mais...';
        const link = item.querySelector('a')?.href || 'noticias/';
        
        blogHtml += `
          <div style="background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <h3 style="margin: 0 0 10px 0; font-size: 16px; color: #333;">${escapeHtml(title)}</h3>
            <p style="margin: 0 0 15px 0; color: #666; font-size: 14px; line-height: 1.5;">${escapeHtml(excerpt.substring(0, 100))}...</p>
            <a href="${escapeHtml(link)}" style="color: #667eea; text-decoration: none; font-weight: bold;">Leia mais →</a>
          </div>
        `;
      }
      blogGrid.innerHTML = blogHtml;
    }
  } catch (e) {
    console.error('Erro ao carregar blog:', e);
    blogGrid.innerHTML = '<p style="text-align: center; padding: 20px;">Confira nossos artigos em <a href="noticias/">Blog</a></p>';
  }
}

// ========== BUSCA ==========
function setupSearch() {
  const searchInput = document.getElementById('searchInput');
  if (!searchInput) return;

  searchInput.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase();
    const filtered = allProducts.filter(p => 
      p.name.toLowerCase().includes(query) || 
      (p.custom_category_slug || '').includes(query)
    );
    renderProducts(filtered);
  });
}

// ========== TEMA ESCURO ==========
function setupTheme() {
  const themeToggle = document.getElementById('themeToggle');
  if (!themeToggle) return;

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

// ========== INICIALIZAÇÃO ==========
async function init() {
  try {
    console.log('Iniciando carregamento de dados...');
    const response = await fetch(DATA_URL + '?t=' + Date.now());
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    allProducts = Array.isArray(data) ? data : [];
    
    console.log(`✅ ${allProducts.length} produtos carregados`);
    
    renderStats(allProducts);
    renderProducts(allProducts);
    await renderBlog();
    setupSearch();
    setupTheme();
    
  } catch (error) {
    console.error('❌ Erro ao carregar dados:', error);
    const grid = document.getElementById('featuredGrid');
    if (grid) {
      grid.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 40px;">
          <p style="font-size: 16px; color: #666;">⚠️ Erro ao carregar ofertas</p>
          <p style="font-size: 14px; color: #999;">Tente recarregar a página em alguns instantes</p>
        </div>
      `;
    }
  }
}

// ========== INICIAR QUANDO DOM ESTIVER PRONTO ==========
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
