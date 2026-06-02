// ========== CONFIGURAÇÃO ==========
const DATA_URL = '/data/database/all_products.json';

let allProducts = [];

// ========== UTILITÁRIOS ==========
function formatPrice(value) {
    return parseFloat(value).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

// ========== RENDERIZAÇÃO DE PRODUTOS ==========
function createProductCard(p) {
    const discount = p.custom_discount_pct || 0;
    const price = parseFloat(p.price);
    const oldPrice = p.original_price ? parseFloat(p.original_price) : (price / (1 - discount/100));
    const savings = oldPrice - price;
    
    return `
        <div class="product-card">
            ${discount > 5 ? `<span class="badge-discount">${discount}% OFF</span>` : ''}
            <img src="${p.image}" alt="${p.name}" class="product-img" loading="lazy">
            <h3 class="product-title">${p.name}</h3>
            <div class="price-box">
                ${oldPrice > price ? `<span class="old-price">R$ ${formatPrice(oldPrice)}</span>` : ''}
                <div class="current-price">R$ ${formatPrice(price)}</div>
                ${savings > 0 ? `<span class="savings">Economize R$ ${formatPrice(savings)}</span>` : ''}
            </div>
            <a href="${p.custom_affiliate_url}" class="btn-buy" target="_blank">Ver Oferta</a>
        </div>
    `;
}

function renderProducts(products) {
    const grid = document.getElementById('featuredGrid');
    if (!grid) return;

    if (products.length === 0) {
        grid.innerHTML = '<p style="text-align: center; padding: 40px; grid-column: 1 / -1;">Nenhuma oferta encontrada.</p>';
        return;
    }

    // Ordenar por desconto
    const sorted = [...products].sort((a, b) => (b.custom_discount_pct || 0) - (a.custom_discount_pct || 0));
    const limited = sorted.slice(0, 24);
    grid.innerHTML = limited.map(p => createProductCard(p)).join('');
}

// ========== BUSCA ==========
function setupSearch() {
    const searchInput = document.getElementById('mainSearch');
    if (!searchInput) return;
    
    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();
        const filtered = allProducts.filter(p => 
            p.name.toLowerCase().includes(query)
        );
        renderProducts(filtered);
    });
}

// ========== INICIALIZAÇÃO ==========
async function init() {
    try {
        const response = await fetch(DATA_URL + '?t=' + Date.now());
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        allProducts = Array.isArray(data) ? data : [];
        renderProducts(allProducts);
        setupSearch();
    } catch (error) {
        console.error('Erro ao carregar dados:', error);
    }
}

document.addEventListener('DOMContentLoaded', init);
