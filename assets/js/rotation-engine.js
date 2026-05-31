/**
 * 🔄 ROTATION ENGINE - Sistema de Rotação Inteligente de Conteúdo
 * Implementa A/B testing, análise de CTR e otimização automática
 * 
 * Funcionalidades:
 * - Rotação de produtos em destaque (Hero)
 * - A/B testing de títulos e descrições
 * - Rastreamento de clicks e impressões
 * - Análise de performance em tempo real
 * - Armazenamento local de dados
 */

class RotationEngine {
  constructor() {
    this.storageKey = 'comparaRotationData';
    this.rotationInterval = 60000; // 1 minuto (ajustável)
    this.data = this.loadData();
    this.currentVariant = this.selectVariant();
    this.init();
  }

  /**
   * Inicializa o engine e começa rastreamento
   */
  init() {
    console.log('🔄 Rotation Engine iniciado');
    this.trackPageView();
    this.startHeroRotation();
    this.setupClickTracking();
    this.startAnalytics();
  }

  /**
   * Carrega dados de rotação do localStorage
   */
  loadData() {
    const stored = localStorage.getItem(this.storageKey);
    return stored ? JSON.parse(stored) : this.getDefaultData();
  }

  /**
   * Retorna estrutura padrão de dados
   */
  getDefaultData() {
    return {
      products: {},
      variants: {},
      sessions: 0,
      lastUpdate: new Date().toISOString(),
      aTestResults: {}
    };
  }

  /**
   * Salva dados em localStorage
   */
  saveData() {
    localStorage.setItem(this.storageKey, JSON.stringify(this.data));
  }

  /**
   * Registra visualização de página
   */
  trackPageView() {
    this.data.sessions = (this.data.sessions || 0) + 1;
    this.saveData();
    
    // Enviar para GA4
    if (typeof gtag !== 'undefined') {
      gtag('event', 'page_view', {
        'custom_rotation_session': this.data.sessions
      });
    }
  }

  /**
   * Seleciona variante para o usuário (A ou B)
   */
  selectVariant() {
    const storedVariant = sessionStorage.getItem('userVariant');
    if (storedVariant) return storedVariant;

    const variant = Math.random() < 0.5 ? 'A' : 'B';
    sessionStorage.setItem('userVariant', variant);
    return variant;
  }

  /**
   * Inicia rotação automática do Hero (destaque)
   */
  startHeroRotation() {
    const heroSection = document.getElementById('heroProduct');
    if (!heroSection) return;

    // Rotaciona a cada minuto
    setInterval(() => {
      this.rotateHero();
    }, this.rotationInterval);

    // Primeira rotação imediata
    this.rotateHero();
  }

  /**
   * Rotaciona o produto em destaque
   */
  rotateHero() {
    const heroSection = document.getElementById('heroProduct');
    if (!heroSection) return;

    // Obtém todos os produtos com dados de performance
    const allProducts = this.getTopPerformingProducts(1);
    if (allProducts.length === 0) return;

    const selectedProduct = allProducts[0];
    this.renderHeroProduct(heroSection, selectedProduct);
    
    // Rastreia impressão
    this.trackImpression(selectedProduct.id);
  }

  /**
   * Obtém produtos com melhor performance
   */
  getTopPerformingProducts(limit = 5) {
    const productCards = document.querySelectorAll('.product-card');
    const products = [];

    productCards.forEach(card => {
      const productId = card.getAttribute('data-product-id') || this.generateProductId(card);
      const productData = this.data.products[productId] || {
        id: productId,
        clicks: 0,
        impressions: 0,
        ctr: 0
      };

      // Calcula CTR
      productData.ctr = productData.impressions > 0 
        ? (productData.clicks / productData.impressions * 100).toFixed(2)
        : 0;

      products.push({
        ...productData,
        element: card,
        title: card.querySelector('h3')?.textContent || '',
        price: card.querySelector('.price-tag')?.textContent || '',
        image: card.querySelector('img')?.src || '',
        link: card.querySelector('.btn')?.href || ''
      });
    });

    // Ordena por CTR (decrescente)
    return products
      .sort((a, b) => parseFloat(b.ctr) - parseFloat(a.ctr))
      .slice(0, limit);
  }

  /**
   * Gera ID único para produto
   */
  generateProductId(element) {
    const title = element.querySelector('h3')?.textContent || '';
    return 'prod_' + btoa(title).substring(0, 12);
  }

  /**
   * Renderiza produto no Hero
   */
  renderHeroProduct(heroSection, product) {
    const template = `
      <div class="hero-content" data-hero-product-id="${product.id}">
        <div class="hero-text">
          <span class="badge" style="background: var(--primary); color: white;">⚡ DESTAQUE!</span>
          <h1>${this.getTitleVariant(product.title)}</h1>
          <p>${this.getDescriptionVariant(product.title)}</p>
          <div class="price-tag" style="font-size: 32px;">${product.price}</div>
          <a href="${product.link}" class="btn" style="padding: 15px 30px; font-size: 18px;">Ver Detalhes</a>
        </div>
        <div class="hero-img">
          <img src="${product.image}" alt="${product.title}" loading="lazy" width="300" height="300" style="width:100%;height:auto;">
        </div>
      </div>
    `;

    heroSection.innerHTML = template;
    
    // Configura rastreamento de cliques
    const heroLink = heroSection.querySelector('.btn');
    if (heroLink) {
      heroLink.addEventListener('click', () => {
        this.trackClick(product.id, 'hero');
      });
    }
  }

  /**
   * Retorna título em variante A ou B
   */
  getTitleVariant(originalTitle) {
    const variants = {
      'A': originalTitle,
      'B': `🔥 ${originalTitle} - MELHOR PREÇO!`
    };
    return variants[this.currentVariant] || originalTitle;
  }

  /**
   * Retorna descrição em variante A ou B
   */
  getDescriptionVariant(productTitle) {
    const variantA = 'Oferta fresquinha saindo do forno para você.';
    const variantB = 'Aproveite este preço incrível agora mesmo. Ofertas limitadas!';
    
    return this.currentVariant === 'A' ? variantA : variantB;
  }

  /**
   * Configura rastreamento de cliques
   */
  setupClickTracking() {
    document.addEventListener('click', (e) => {
      const btn = e.target.closest('.btn');
      if (!btn) return;

      const productCard = btn.closest('.product-card');
      if (!productCard) return;

      const productId = productCard.getAttribute('data-product-id') || this.generateProductId(productCard);
      this.trackClick(productId, 'product-card');
    });
  }

  /**
   * Rastreia clique em produto
   */
  trackClick(productId, source = 'unknown') {
    if (!this.data.products[productId]) {
      this.data.products[productId] = {
        clicks: 0,
        impressions: 0,
        lastSeen: new Date().toISOString()
      };
    }

    this.data.products[productId].clicks++;
    this.data.products[productId].lastClicked = new Date().toISOString();
    this.saveData();

    // Enviar para GA4
    if (typeof gtag !== 'undefined') {
      gtag('event', 'affiliate_click', {
        'product_id': productId,
        'click_source': source,
        'user_variant': this.currentVariant,
        'ctr': this.calculateCTR(productId)
      });
    }

    console.log(`📊 Click rastreado: ${productId} (${source})`);
  }

  /**
   * Rastreia impressão de produto
   */
  trackImpression(productId) {
    if (!this.data.products[productId]) {
      this.data.products[productId] = {
        clicks: 0,
        impressions: 0
      };
    }

    this.data.products[productId].impressions++;
    this.data.products[productId].lastImpression = new Date().toISOString();
    this.saveData();

    console.log(`👁️ Impressão rastreada: ${productId}`);
  }

  /**
   * Inicia coleta de analytics
   */
  startAnalytics() {
    // A cada 5 minutos, analisa e otimiza
    setInterval(() => {
      this.analyzePerformance();
      this.optimizeContent();
    }, 5 * 60 * 1000);
  }

  /**
   * Analisa performance geral
   */
  analyzePerformance() {
    const topProducts = this.getTopPerformingProducts(10);
    const stats = {
      timestamp: new Date().toISOString(),
      totalImpressions: 0,
      totalClicks: 0,
      averageCTR: 0,
      topProducts: topProducts.slice(0, 5)
    };

    topProducts.forEach(p => {
      stats.totalImpressions += p.impressions;
      stats.totalClicks += p.clicks;
    });

    stats.averageCTR = stats.totalImpressions > 0 
      ? (stats.totalClicks / stats.totalImpressions * 100).toFixed(2)
      : 0;

    this.data.analytics = stats;
    this.saveData();

    console.log('📈 Performance Analysis:', stats);
    this.sendAnalyticsToServer(stats);
  }

  /**
   * Otimiza conteúdo baseado em performance
   */
  optimizeContent() {
    const topProducts = this.getTopPerformingProducts(5);
    
    // Move top performers para posições mais visíveis
    const grid = document.getElementById('featuredGrid');
    if (!grid) return;

    topProducts.forEach((product, index) => {
      if (product.element) {
        product.element.style.order = -1 - index; // Move para o topo
        product.element.style.animation = 'highlightPulse 0.5s ease';
      }
    });

    console.log('🎯 Conteúdo otimizado com base em performance');
  }

  /**
   * Calcula CTR de um produto
   */
  calculateCTR(productId) {
    const product = this.data.products[productId];
    if (!product || product.impressions === 0) return 0;
    return (product.clicks / product.impressions * 100).toFixed(2);
  }

  /**
   * Envia dados para servidor (implementar backend)
   */
  sendAnalyticsToServer(stats) {
    // Implementar chamada API para enviar dados para backend
    console.log('📤 Preparado para enviar dados ao servidor:', stats);
    
    // Exemplo:
    // fetch('/api/analytics', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify(stats)
    // });
  }

  /**
   * Retorna relatório de performance
   */
  getPerformanceReport() {
    return {
      sessions: this.data.sessions,
      products: this.data.products,
      topPerformers: this.getTopPerformingProducts(10),
      variant: this.currentVariant,
      lastUpdate: new Date().toISOString()
    };
  }

  /**
   * Exporta dados para análise (CSV)
   */
  exportDataAsCSV() {
    const topProducts = this.getTopPerformingProducts(50);
    let csv = 'Product ID,Impressions,Clicks,CTR(%),Last Click\n';

    topProducts.forEach(p => {
      csv += `"${p.id}",${p.impressions},${p.clicks},${p.ctr},"${p.lastClicked || 'N/A'}"\n`;
    });

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `rotation-report-${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();

    console.log('📥 Relatório exportado como CSV');
  }
}

// Inicializa engine ao carregar página
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    window.rotationEngine = new RotationEngine();
  });
} else {
  window.rotationEngine = new RotationEngine();
}
