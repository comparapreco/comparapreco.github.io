/**
 * Sistema de Favoritos - Radar de Preços
 * Gerencia favoritos e lista de desejos usando LocalStorage
 */

const FavoritesManager = {
  STORAGE_KEYS: {
    FAVORITOS: 'radar_favoritos',
    DESEJOS: 'radar_desejos'
  },

  /**
   * Inicializa o sistema de favoritos
   */
  init() {
    this.injectFavoriteButtons();
    this.setupEventListeners();
  },

  /**
   * Adiciona botões de favorito a todos os produtos
   */
  injectFavoriteButtons() {
    // Encontra todos os cards de produto
    const productCards = document.querySelectorAll('[data-product-id]');
    
    productCards.forEach(card => {
      const productId = card.dataset.productId;
      const productTitle = card.dataset.productTitle || 'Produto';
      const productPrice = card.dataset.productPrice || 0;
      const productImage = card.dataset.productImage || '';

      // Verifica se já tem botão de favorito
      if (card.querySelector('.favorite-btn')) return;

      // Cria o botão
      const favoriteBtn = document.createElement('button');
      favoriteBtn.className = 'favorite-btn';
      favoriteBtn.innerHTML = '❤️ Favoritar';
      favoriteBtn.dataset.productId = productId;
      favoriteBtn.onclick = (e) => {
        e.preventDefault();
        this.toggleFavorite(productId, productTitle, productPrice, productImage);
      };

      // Verifica se já está nos favoritos
      if (this.isFavorited(productId)) {
        favoriteBtn.classList.add('active');
        favoriteBtn.innerHTML = '❤️ Removido de Favoritos';
      }

      // Injeta o botão
      const actionContainer = card.querySelector('.product-actions') || 
                             card.querySelector('.favorite-actions') ||
                             card;
      actionContainer.appendChild(favoriteBtn);
    });
  },

  /**
   * Alterna favorito
   */
  toggleFavorite(productId, title, price, image) {
    const favoritos = JSON.parse(localStorage.getItem(this.STORAGE_KEYS.FAVORITOS)) || [];
    const index = favoritos.findIndex(f => f.id === productId);

    if (index > -1) {
      // Remove dos favoritos
      favoritos.splice(index, 1);
      this.showNotification('Removido dos favoritos');
    } else {
      // Adiciona aos favoritos
      favoritos.push({
        id: productId,
        title,
        price,
        image,
        addedAt: new Date().toISOString()
      });
      this.showNotification('Adicionado aos favoritos!');
    }

    localStorage.setItem(this.STORAGE_KEYS.FAVORITOS, JSON.stringify(favoritos));
    this.injectFavoriteButtons(); // Atualiza UI
  },

  /**
   * Verifica se um produto está nos favoritos
   */
  isFavorited(productId) {
    const favoritos = JSON.parse(localStorage.getItem(this.STORAGE_KEYS.FAVORITOS)) || [];
    return favoritos.some(f => f.id === productId);
  },

  /**
   * Obtém todos os favoritos
   */
  getFavorites() {
    return JSON.parse(localStorage.getItem(this.STORAGE_KEYS.FAVORITOS)) || [];
  },

  /**
   * Adiciona à lista de desejos
   */
  addToWishlist(productId, title, price, image) {
    const desejos = JSON.parse(localStorage.getItem(this.STORAGE_KEYS.DESEJOS)) || [];
    
    if (!desejos.find(d => d.id === productId)) {
      desejos.push({
        id: productId,
        title,
        price,
        image,
        targetPrice: null,
        addedAt: new Date().toISOString()
      });
      localStorage.setItem(this.STORAGE_KEYS.DESEJOS, JSON.stringify(desejos));
      this.showNotification('Adicionado à lista de desejos!');
    }
  },

  /**
   * Exibe notificação
   */
  showNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
    notification.style.cssText = `
      position: fixed;
      bottom: 20px;
      right: 20px;
      background: var(--primary);
      color: white;
      padding: 16px 24px;
      border-radius: 8px;
      font-weight: 700;
      z-index: 9999;
      animation: slideIn 0.3s ease-out;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
      notification.style.animation = 'slideOut 0.3s ease-out';
      setTimeout(() => notification.remove(), 300);
    }, 3000);
  },

  /**
   * Setup event listeners
   */
  setupEventListeners() {
    // Sincroniza favoritos entre abas
    window.addEventListener('storage', (e) => {
      if (e.key === this.STORAGE_KEYS.FAVORITOS || e.key === this.STORAGE_KEYS.DESEJOS) {
        this.injectFavoriteButtons();
      }
    });
  }
};

// Inicializa quando o DOM está pronto
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => FavoritesManager.init());
} else {
  FavoritesManager.init();
}
