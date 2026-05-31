/**
 * Sistema de Analytics - Radar de Preços
 * Rastreia cliques, visualizações e gera métricas de performance
 */

const RadarAnalytics = {
  STORAGE_KEY: 'radar_analytics',
  
  /**
   * Inicializa o sistema de analytics
   */
  init() {
    this.trackPageView();
    this.trackProductClicks();
    this.trackCategoryViews();
  },

  /**
   * Registra visualização de página
   */
  trackPageView() {
    const page = window.location.pathname;
    const analytics = this.getAnalytics();
    
    if (!analytics.pageViews) analytics.pageViews = {};
    if (!analytics.pageViews[page]) analytics.pageViews[page] = 0;
    
    analytics.pageViews[page]++;
    analytics.lastUpdate = new Date().toISOString();
    
    this.saveAnalytics(analytics);
  },

  /**
   * Rastreia cliques em produtos
   */
  trackProductClicks() {
    document.addEventListener('click', (e) => {
      const productLink = e.target.closest('[data-product-id]');
      if (!productLink) return;

      const productId = productLink.dataset.productId;
      const productName = productLink.dataset.productName || 'Unknown';
      const category = productLink.dataset.category || 'uncategorized';

      const analytics = this.getAnalytics();
      
      if (!analytics.productClicks) analytics.productClicks = {};
      if (!analytics.productClicks[productId]) {
        analytics.productClicks[productId] = {
          name: productName,
          category: category,
          clicks: 0
        };
      }
      
      analytics.productClicks[productId].clicks++;
      analytics.lastUpdate = new Date().toISOString();
      
      this.saveAnalytics(analytics);
    });
  },

  /**
   * Rastreia visualizações de categoria
   */
  trackCategoryViews() {
    const categoryElements = document.querySelectorAll('[data-category]');
    categoryElements.forEach(el => {
      el.addEventListener('click', () => {
        const category = el.dataset.category;
        const analytics = this.getAnalytics();
        
        if (!analytics.categoryViews) analytics.categoryViews = {};
        if (!analytics.categoryViews[category]) analytics.categoryViews[category] = 0;
        
        analytics.categoryViews[category]++;
        analytics.lastUpdate = new Date().toISOString();
        
        this.saveAnalytics(analytics);
      });
    });
  },

  /**
   * Obtém dados de analytics
   */
  getAnalytics() {
    return JSON.parse(localStorage.getItem(this.STORAGE_KEY)) || {
      pageViews: {},
      productClicks: {},
      categoryViews: {},
      lastUpdate: new Date().toISOString()
    };
  },

  /**
   * Salva dados de analytics
   */
  saveAnalytics(data) {
    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(data));
  },

  /**
   * Obtém top 10 produtos mais clicados
   */
  getTopProducts(limit = 10) {
    const analytics = this.getAnalytics();
    return Object.entries(analytics.productClicks || {})
      .map(([id, data]) => ({ id, ...data }))
      .sort((a, b) => b.clicks - a.clicks)
      .slice(0, limit);
  },

  /**
   * Obtém CTR por categoria
   */
  getCategoryMetrics() {
    const analytics = this.getAnalytics();
    const categoryViews = analytics.categoryViews || {};
    const productClicks = analytics.productClicks || {};

    const metrics = {};
    
    Object.entries(productClicks).forEach(([id, data]) => {
      const cat = data.category;
      if (!metrics[cat]) {
        metrics[cat] = { views: 0, clicks: 0, ctr: 0 };
      }
      metrics[cat].clicks += data.clicks;
    });

    Object.entries(categoryViews).forEach(([cat, views]) => {
      if (!metrics[cat]) metrics[cat] = { views: 0, clicks: 0, ctr: 0 };
      metrics[cat].views = views;
    });

    // Calcula CTR
    Object.entries(metrics).forEach(([cat, data]) => {
      data.ctr = data.views > 0 ? ((data.clicks / data.views) * 100).toFixed(2) : 0;
    });

    return metrics;
  },

  /**
   * Obtém páginas mais visitadas
   */
  getMostVisitedPages(limit = 10) {
    const analytics = this.getAnalytics();
    return Object.entries(analytics.pageViews || {})
      .map(([page, views]) => ({ page, views }))
      .sort((a, b) => b.views - a.views)
      .slice(0, limit);
  },

  /**
   * Calcula estimativa de receita
   */
  estimateRevenue() {
    const topProducts = this.getTopProducts();
    const avgCommission = 0.05; // 5% de comissão média
    const avgProductPrice = 1500; // Preço médio de produto

    const totalClicks = topProducts.reduce((sum, p) => sum + p.clicks, 0);
    const conversionRate = 0.02; // 2% de conversão estimada
    const estimatedSales = totalClicks * conversionRate;
    const estimatedRevenue = estimatedSales * avgProductPrice * avgCommission;

    return {
      totalClicks,
      estimatedSales: Math.round(estimatedSales),
      estimatedRevenue: estimatedRevenue.toFixed(2),
      conversionRate: (conversionRate * 100).toFixed(2)
    };
  },

  /**
   * Reseta dados (apenas para testes)
   */
  reset() {
    localStorage.removeItem(this.STORAGE_KEY);
  }
};

// Inicializa quando o DOM está pronto
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => RadarAnalytics.init());
} else {
  RadarAnalytics.init();
}
