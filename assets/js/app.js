async function loadTemplate(url, targetSelector) {
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const html = await response.text();
        document.querySelector(targetSelector).innerHTML = html;
    } catch (error) {
        console.error(`Erro ao carregar template ${url}:`, error);
    }
}

// ========== CONFIGURAÇÃO ==========
const DATA_URL = '/data/database/all_products.json';

let allProducts = [];

// ========== UTILITÁRIOS ==========
function formatPrice(value) {
    return parseFloat(value).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function getRandomProducts(products, count) {
    return [...products].sort(() => Math.random() - 0.5).slice(0, count);
}

// ========== SKELETON LOADING ==========
function createSkeletonCard() {
    return `
        <div class="product-card skeleton-card">
            <div class="skeleton skeleton-image"></div>
            <div class="skeleton skeleton-text" style="height: 20px; margin-bottom: 12px;"></div>
            <div class="skeleton skeleton-text" style="height: 16px; width: 80%; margin-bottom: 12px;"></div>
            <div class="skeleton skeleton-text short" style="height: 24px; margin-bottom: 12px;"></div>
            <div class="skeleton skeleton-text short" style="height: 40px;"></div>
        </div>
    `;
}

function showSkeletonLoading(gridId, count = 12) {
    const grid = document.getElementById(gridId);
    if (!grid) return;
    grid.innerHTML = Array(count).fill(0).map(() => createSkeletonCard()).join('');
}

// ========== LÓGICA DE SELOS ==========
/**
 * Retorna os selos (badges) a serem exibidos no card do produto.
 * Regras:
 *  - badge-discount: sempre que desconto > 5% (canto superior esquerdo)
 *  - badge-hot: desconto > 50% (canto superior direito, animado)
 *  - badge-flash: desconto entre 30% e 50% (canto superior direito)
 *  - badge-best-price: desconto >= 60% (sobrescreve badge-discount no canto esq.)
 */
function getBadges(discount) {
    const badges = { left: '', right: '' };

    // Selo esquerdo (desconto / melhor preço)
    if (discount >= 60) {
        badges.left = `<span class="badge-best-price">⭐ Melhor Preço</span>`;
    } else if (discount > 5) {
        badges.left = `<span class="badge-discount">${discount}% OFF</span>`;
    }

    // Selo direito (intensidade da oferta)
    if (discount > 50) {
        badges.right = `<span class="badge-hot">🔥 HOT</span>`;
    } else if (discount >= 30) {
        badges.right = `<span class="badge-flash">⚡ Relâmpago</span>`;
    }

    return badges;
}

// ========== RENDERIZAÇÃO DE PRODUTOS ==========
function createProductCard(p) {
    const discount = p.custom_discount_pct || 0;
    const price = parseFloat(p.price);
    const oldPrice = p.original_price ? parseFloat(p.original_price) : (price / (1 - discount / 100));
    const savings = oldPrice - price;

    const badges = getBadges(discount);

    return `
        <div class="product-card">
            ${badges.left}
            ${badges.right}
            <img
                src="${p.image}"
                alt="${p.name}"
                class="product-img"
                loading="lazy"
                onerror="this.src='/assets/img/placeholder.png'"
            >
            <h3 class="product-title">${p.name}</h3>
            <div class="price-box">
                ${oldPrice > price ? `<span class="old-price">De R$ ${formatPrice(oldPrice)}</span>` : ''}
                <div class="current-price">R$ ${formatPrice(price)}</div>
                ${savings > 1 ? `<span class="savings">💰 Economize R$ ${formatPrice(savings)}</span>` : ''}
            </div>
            <a href="${p.custom_affiliate_url}" class="btn-buy" target="_blank" rel="noopener noreferrer">
                Ver Oferta Ninja 🚀
            </a>
        </div>
    `;
}

function renderProducts(products, gridId = 'featuredGrid', limit = 24) {
    const grid = document.getElementById(gridId);
    if (!grid) return;

    if (products.length === 0) {
        grid.innerHTML = '<p style="text-align: center; padding: 40px; grid-column: 1 / -1; color: var(--text-muted);">Nenhuma oferta encontrada.</p>';
        return;
    }

    // Ordenar por desconto com DIVERSIFICAÇÃO de categorias
    const sorted = [...products].sort((a, b) => (b.custom_discount_pct || 0) - (a.custom_discount_pct || 0));

    const diversified = [];
    const seenCats = {};
    for (const p of sorted) {
        const cat = p.custom_category_slug || 'outros';
        seenCats[cat] = (seenCats[cat] || 0) + 1;
        if (seenCats[cat] <= 4) {
            diversified.push(p);
        }
        if (diversified.length >= limit) break;
    }

    grid.innerHTML = diversified.map(p => createProductCard(p)).join('');

    // Animação fade-in escalonada
    const cards = grid.querySelectorAll('.product-card');
    cards.forEach((card, index) => {
        card.style.animation = `fadeIn 0.5s ease-out ${index * 0.04}s both`;
    });
}

// ========== BUSCA ==========
function setupSearch() {
    const searchInput = document.getElementById('mainSearch');
    if (!searchInput) return;

    let searchTimeout;
    searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        const query = e.target.value.toLowerCase().trim();

        if (query.length === 0) {
            renderProducts(allProducts, 'featuredGrid', 24);
            return;
        }

        searchTimeout = setTimeout(() => {
            const filtered = allProducts.filter(p =>
                p.name.toLowerCase().includes(query) ||
                (p.category && p.category.toLowerCase().includes(query))
            );
            renderProducts(filtered, 'featuredGrid', 24);
        }, 300);
    });
}

// ========== ATUALIZAR ESTATÍSTICAS ==========
function updateStats(products) {
    const totalOffersEl = document.getElementById('totalOffers');
    const totalComparativesEl = document.getElementById('totalComparatives');
    const totalProductsEl = document.getElementById('totalProducts');

    if (totalOffersEl) totalOffersEl.textContent = (products.length).toLocaleString('pt-BR') + '+';
    if (totalComparativesEl) totalComparativesEl.textContent = Math.floor(products.length * 0.06).toLocaleString('pt-BR') + '+';
    if (totalProductsEl) totalProductsEl.textContent = Math.floor(products.length * 0.2).toLocaleString('pt-BR') + '+';
}

// ========== MENU HAMBURGUER MOBILE ==========
function setupMobileMenu() {
    const toggle = document.querySelector('.menu-toggle');
    const nav = document.querySelector('.nav-links');
    if (!toggle || !nav) return;

    toggle.addEventListener('click', () => {
        nav.classList.toggle('open');
        toggle.textContent = nav.classList.contains('open') ? '✕' : '☰';
    });

    // Fechar menu ao clicar em um link
    nav.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            nav.classList.remove('open');
            toggle.textContent = '☰';
        });
    });

    // Fechar menu ao clicar fora
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.header') && nav.classList.contains('open')) {
            nav.classList.remove('open');
            toggle.textContent = '☰';
        }
    });
}

// ========== INICIALIZAÇÃO ==========
async function init() {
    try {
        // Mostrar skeleton loading
        showSkeletonLoading('featuredGrid', 12);
        showSkeletonLoading('comparativesGrid', 12);
        showSkeletonLoading('guidesGrid', 12);

        // Carregar dados
        const response = await fetch(DATA_URL + '?t=' + Date.now());
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        allProducts = Array.isArray(data) ? data : [];

        // Atualizar estatísticas
        updateStats(allProducts);

        // Renderizar produtos na página inicial
        if (document.getElementById('featuredGrid')) {
            renderProducts(allProducts, 'featuredGrid', 24);
        }

        // Renderizar ofertas na página de ofertas
        if (document.getElementById('offersGrid')) {
            renderProducts(allProducts, 'offersGrid', 50);
        }

        // Renderizar comparativos
        if (document.getElementById('comparativesGrid')) {
            const comparatives = getRandomProducts(allProducts, 12);
            renderProducts(comparatives, 'comparativesGrid', 12);
        }

        // Renderizar guias
        if (document.getElementById('guidesGrid')) {
            const guides = getRandomProducts(allProducts, 12);
            renderProducts(guides, 'guidesGrid', 12);
        }

        // Setup busca e menu mobile
        setupSearch();
        setupMobileMenu();

        console.log('✅ Radar Ninja carregado com sucesso!', allProducts.length, 'produtos');
    } catch (error) {
        console.error('❌ Erro ao carregar dados:', error);
        const grid = document.getElementById('featuredGrid');
        if (grid) {
            grid.innerHTML = '<p style="text-align: center; padding: 40px; grid-column: 1 / -1; color: var(--danger);">Erro ao carregar ofertas. Tente novamente mais tarde.</p>';
        }
    }
}

// Inicializar quando o DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

// ========== LAZY LOADING OTIMIZADO ==========
if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                if (img.dataset.src) {
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    observer.unobserve(img);
                }
            }
        });
    });

    document.querySelectorAll('img[data-src]').forEach(img => imageObserver.observe(img));
}

// ========== SMOOTH SCROLL ==========
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
});

// ========== ANALYTICS ==========
function trackEvent(category, action, label) {
    if (typeof gtag !== 'undefined') {
        gtag('event', action, {
            'event_category': category,
            'event_label': label
        });
    }
}

document.addEventListener('click', (e) => {
    const buyBtn = e.target.closest('.btn-buy');
    if (buyBtn) {
        const productTitle = buyBtn.closest('.product-card')?.querySelector('.product-title')?.textContent || 'Unknown';
        trackEvent('engagement', 'product_click', productTitle);
    }
});
