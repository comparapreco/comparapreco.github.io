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

function getDaysAgo(dateString) {
  if (!dateString) return null;
  const date = new Date(dateString);
  const now = new Date();
  const diffTime = Math.abs(now - date);
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  return diffDays;
}

function getOfferBadges(product, index) {
  const badges = [];
  const discount = product.custom_discount_pct || 0;
  const daysAgo = getDaysAgo(product.data_atualizacao);
  
  // Badge de Atualizado (novo)
  if (daysAgo !== null && daysAgo <= 3) {
    let daysText = 'Hoje';
    if (daysAgo === 1) daysText = 'Ontem';
    if (daysAgo === 2) daysText = '2d atrás';
    if (daysAgo === 3) daysText = '3d atrás';
    badges.push(`<span class="badge badge-new" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 6px 12px; border-radius: 20px; font-size: 11px; font-weight: bold; margin: 2px; display: inline-block;">✨ ATUALIZADO ${daysText}</span>`);
  }
  
  // Menor Preço da História
  if (discount >= 40) {
    badges.push('<span class="badge badge-lowest" style="background: #ff6b6b; color: white; padding: 6px 12px; border-radius: 20px; font-size: 11px; font-weight: bold; margin: 2px; display: inline-block;">🏆 MENOR PREÇO</span>');
  }
  
  // Baixou
  if (discount >= 25 && discount < 40) {
    badges.push('<span class="badge badge-down" style="background: #51cf66; color: white; padding: 6px 12px; border-radius: 20px; font-size: 11px; font-weight: bold; margin: 2px; display: inline-block;">📉 BAIXOU</span>');
  }
  
  // Destaque
  if (index < 5) {
    badges.push('<span class="badge badge-featured" style="background: #ffd43b; color: #333; padding: 6px 12px; border-radius: 20px; font-size: 11px; font-weight: bold; margin: 2px; display: inline-block;">⭐ DESTAQUE</span>');
  }
  
  return badges.join(' ');
}

// ========== RENDERIZAÇÃO DE PRODUTOS ==========
function renderProducts(products) {
  const grid = document.getElementById('featuredGrid');
  if (!grid) return;

  if (products.length === 0) {
    grid.innerHTML = '<p style="text-align: center; padding: 40px; grid-column: 1 / -1;">Nenhuma oferta encontrada.</p>';
    return;
  }

  // Ordenar: primeiro os atualizados, depois por desconto
  const sorted = [...products].sort((a, b) => {
    const daysA = getDaysAgo(a.data_atualizacao) || 999;
    const daysB = getDaysAgo(b.data_atualizacao) || 999;
    
    if (daysA !== daysB) return daysA - daysB;
    return (b.custom_discount_pct || 0) - (a.custom_discount_pct || 0);
  });
  
  const limited = sorted.slice(0, 24);

  grid.innerHTML = limited.map((p, idx) => {
    const badges = getOfferBadges(p, idx);
    const affiliate = p.custom_affiliate_url || p.permalink || '#';
    const discount = p.custom_discount_pct || 0;
    
    return `
      <div class="product-card-modern" style="
        background: white;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        cursor: pointer;
        display: flex;
        flex-direction: column;
        height: 100%;
      " onmouseover="this.style.boxShadow='0 8px 16px rgba(0,0,0,0.15)'; this.style.transform='translateY(-4px)'" onmouseout="this.style.boxShadow='0 2px 8px rgba(0,0,0,0.1)'; this.style.transform='translateY(0)'">
        
        <!-- Imagem do Produto -->
        <div style="
          position: relative;
          overflow: hidden;
          background: #f8f9fa;
          height: 200px;
          display: flex;
          align-items: center;
          justify-content: center;
        ">
          <img src="${escapeHtml(p.image || p.thumbnail)}" alt="${escapeHtml(p.name)}" loading="lazy" style="
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
            transition: transform 0.3s ease;
          " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
          
          <!-- Badge de Desconto -->
          <div style="
            position: absolute;
            top: 10px;
            right: 10px;
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
            color: white;
            padding: 8px 14px;
            border-radius: 8px;
            font-weight: bold;
            font-size: 14px;
            box-shadow: 0 2px 8px rgba(255, 107, 107, 0.3);
          ">
            ↓ ${discount}% OFF
          </div>
          
          <!-- Badges de Promoção -->
          <div style="
            position: absolute;
            top: 10px;
            left: 10px;
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            max-width: 90%;
          ">
            ${badges}
          </div>
        </div>
        
        <!-- Conteúdo do Produto -->
        <div style="
          padding: 16px;
          flex-grow: 1;
          display: flex;
          flex-direction: column;
        ">
          <!-- Título -->
          <h3 style="
            margin: 0 0 12px 0;
            font-size: 14px;
            font-weight: 600;
            line-height: 1.4;
            color: #333;
            min-height: 42px;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
          ">
            ${escapeHtml(p.name)}
          </h3>
          
          <!-- Preços -->
          <div style="margin-bottom: 12px;">
            <span style="
              font-size: 12px;
              color: #999;
              text-decoration: line-through;
              display: block;
              margin-bottom: 4px;
            ">
              R$ ${formatPrice(p.original_price || p.originalPrice || p.price)}
            </span>
            <span style="
              font-size: 22px;
              font-weight: bold;
              color: #ff6b6b;
              display: block;
            ">
              R$ ${formatPrice(p.price)}
            </span>
          </div>
          
          <!-- Botão de Ação -->
          <a href="${escapeHtml(affiliate)}" target="_blank" rel="noopener noreferrer" style="
            display: block;
            text-align: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            font-size: 14px;
            margin-top: auto;
            transition: all 0.3s ease;
            border: none;
            cursor: pointer;
          " onmouseover="this.style.transform='scale(1.02)'; this.style.boxShadow='0 4px 12px rgba(102, 126, 234, 0.4)'" onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='none'">
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
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 20px; text-align: center;">
      <div>
        <div style="font-size: 28px; font-weight: bold; color: #667eea;">${total}</div>
        <div style="font-size: 12px; color: #999; margin-top: 4px;">Ofertas Ativas</div>
      </div>
      <div>
        <div style="font-size: 28px; font-weight: bold; color: #51cf66;">${avgDiscount}%</div>
        <div style="font-size: 12px; color: #999; margin-top: 4px;">Desconto Médio</div>
      </div>
    </div>
  `;
}

// ========== BUSCA ==========
function setupSearch() {
  const searchInput = document.getElementById('searchInput');
  if (!searchInput) return;
  
  searchInput.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase();
    const filtered = allProducts.filter(p => 
      p.name.toLowerCase().includes(query) || 
      (p.title && p.title.toLowerCase().includes(query))
    );
    renderProducts(filtered);
  });
}

// ========== TEMA ==========
function setupTheme() {
  const themeToggle = document.getElementById('themeToggle');
  if (!themeToggle) return;
  
  const isDark = localStorage.getItem('theme') === 'dark';
  if (isDark) {
    document.documentElement.setAttribute('data-theme', 'dark');
    themeToggle.textContent = '☀️';
  }
  
  themeToggle.addEventListener('click', () => {
    const current = document.documentElement.getAttribute('data-theme');
    const newTheme = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    themeToggle.textContent = newTheme === 'dark' ? '☀️' : '🌙';
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
