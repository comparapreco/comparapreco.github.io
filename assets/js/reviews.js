/**
 * Sistema de Comentários e Avaliações - Radar de Preços
 * Gerencia avaliações de produtos com estrelas e comentários usando LocalStorage
 */

const ReviewsManager = {
  STORAGE_KEY: 'radar_reviews',

  /**
   * Inicializa o sistema de avaliações
   */
  init() {
    this.renderReviewsSection();
    this.setupEventListeners();
  },

  /**
   * Renderiza a seção de comentários em uma página de produto
   */
  renderReviewsSection() {
    const reviewsContainer = document.getElementById('reviewsSection');
    if (!reviewsContainer) return;

    const productId = reviewsContainer.dataset.productId;
    const reviews = this.getProductReviews(productId);
    const avgRating = this.calculateAverageRating(reviews);

    const html = `
      <div class="reviews-container">
        <div class="reviews-header">
          <h2>⭐ Avaliações e Comentários</h2>
          <div class="rating-summary">
            <div class="rating-stars">${this.renderStars(avgRating)}</div>
            <span class="rating-text">${avgRating.toFixed(1)} de 5 (${reviews.length} avaliações)</span>
          </div>
        </div>

        <div class="review-form-section">
          <h3>Deixe sua avaliação</h3>
          <form class="review-form" onsubmit="ReviewsManager.submitReview(event, '${productId}')">
            <div class="form-group">
              <label>Sua avaliação:</label>
              <div class="star-rating" id="starRating">
                ${[1,2,3,4,5].map(i => `
                  <span class="star" data-rating="${i}" onclick="ReviewsManager.setRating(${i})">★</span>
                `).join('')}
              </div>
              <input type="hidden" id="selectedRating" value="0">
            </div>

            <div class="form-group">
              <label>Seu nome:</label>
              <input type="text" id="reviewerName" placeholder="Digite seu nome" required>
            </div>

            <div class="form-group">
              <label>Seu comentário:</label>
              <textarea id="reviewComment" placeholder="Compartilhe sua experiência com este produto..." rows="4" required></textarea>
            </div>

            <button type="submit" class="submit-btn">Publicar Avaliação</button>
          </form>
        </div>

        <div class="reviews-list">
          <h3>Comentários dos Usuários</h3>
          ${reviews.length === 0 ? '<p class="no-reviews">Nenhuma avaliação ainda. Seja o primeiro a avaliar!</p>' : ''}
          ${reviews.map(review => `
            <div class="review-item">
              <div class="review-header">
                <div class="reviewer-info">
                  <strong>${review.name}</strong>
                  <span class="review-date">${new Date(review.date).toLocaleDateString('pt-BR')}</span>
                </div>
                <div class="review-rating">${this.renderStars(review.rating)}</div>
              </div>
              <p class="review-text">${this.escapeHtml(review.comment)}</p>
              <div class="review-actions">
                <button class="helpful-btn" onclick="ReviewsManager.markHelpful(this)">👍 Útil (${review.helpful || 0})</button>
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    `;

    reviewsContainer.innerHTML = html;
  },

  /**
   * Renderiza estrelas
   */
  renderStars(rating) {
    return [1, 2, 3, 4, 5]
      .map(i => `<span class="star ${i <= rating ? 'filled' : ''}">★</span>`)
      .join('');
  },

  /**
   * Define a avaliação selecionada
   */
  setRating(rating) {
    document.getElementById('selectedRating').value = rating;
    const stars = document.querySelectorAll('#starRating .star');
    stars.forEach((star, i) => {
      if (i < rating) {
        star.classList.add('selected');
      } else {
        star.classList.remove('selected');
      }
    });
  },

  /**
   * Submete uma nova avaliação
   */
  submitReview(event, productId) {
    event.preventDefault();

    const rating = parseInt(document.getElementById('selectedRating').value);
    const name = document.getElementById('reviewerName').value.trim();
    const comment = document.getElementById('reviewComment').value.trim();

    if (rating === 0 || !name || !comment) {
      alert('Por favor, preencha todos os campos e selecione uma avaliação.');
      return;
    }

    const review = {
      id: Date.now(),
      rating,
      name,
      comment,
      date: new Date().toISOString(),
      helpful: 0
    };

    const reviews = this.getProductReviews(productId);
    reviews.unshift(review);
    this.saveProductReviews(productId, reviews);

    // Reseta o formulário
    document.querySelector('.review-form').reset();
    document.getElementById('selectedRating').value = 0;
    document.querySelectorAll('#starRating .star').forEach(s => s.classList.remove('selected'));

    // Renderiza novamente
    this.renderReviewsSection();
    alert('Avaliação publicada com sucesso!');
  },

  /**
   * Marca uma avaliação como útil
   */
  markHelpful(btn) {
    btn.classList.toggle('marked');
    const count = parseInt(btn.textContent.match(/\d+/)[0]) || 0;
    btn.innerHTML = `👍 Útil (${btn.classList.contains('marked') ? count + 1 : count})`;
  },

  /**
   * Obtém avaliações de um produto
   */
  getProductReviews(productId) {
    const allReviews = JSON.parse(localStorage.getItem(this.STORAGE_KEY)) || {};
    return allReviews[productId] || this.getSeededReviews(productId);
  },

  /**
   * Salva avaliações de um produto
   */
  saveProductReviews(productId, reviews) {
    const allReviews = JSON.parse(localStorage.getItem(this.STORAGE_KEY)) || {};
    allReviews[productId] = reviews;
    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(allReviews));
  },

  /**
   * Retorna avaliações "semente" para prova social
   */
  getSeededReviews(productId) {
    const seededReviews = {
      'galaxy-a36': [
        {
          id: 1,
          rating: 5,
          name: 'João Silva',
          comment: 'Excelente custo-benefício! Câmera muito boa e bateria dura o dia todo. Recomendo!',
          date: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
          helpful: 24
        },
        {
          id: 2,
          rating: 4,
          name: 'Maria Santos',
          comment: 'Bom celular, mas o carregamento poderia ser mais rápido. Mesmo assim, vale muito a pena.',
          date: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
          helpful: 18
        },
        {
          id: 3,
          rating: 5,
          name: 'Carlos Oliveira',
          comment: 'Comprei há 2 meses e continua funcionando perfeitamente. Muito satisfeito!',
          date: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
          helpful: 15
        }
      ],
      'lg-oled-55': [
        {
          id: 1,
          rating: 5,
          name: 'Ana Costa',
          comment: 'Melhor TV que já tive! Imagem perfeita, cores vibrantes. Muito feliz com a compra.',
          date: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(),
          helpful: 32
        },
        {
          id: 2,
          rating: 5,
          name: 'Roberto Dias',
          comment: 'Qualidade de imagem incomparável. Assistir filmes é uma experiência completamente diferente.',
          date: new Date(Date.now() - 8 * 24 * 60 * 60 * 1000).toISOString(),
          helpful: 28
        }
      ]
    };

    return seededReviews[productId] || [];
  },

  /**
   * Calcula a avaliação média
   */
  calculateAverageRating(reviews) {
    if (reviews.length === 0) return 0;
    const sum = reviews.reduce((acc, review) => acc + review.rating, 0);
    return sum / reviews.length;
  },

  /**
   * Escapa HTML para prevenir XSS
   */
  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  },

  /**
   * Setup event listeners
   */
  setupEventListeners() {
    // Sincroniza avaliações entre abas
    window.addEventListener('storage', (e) => {
      if (e.key === this.STORAGE_KEY) {
        this.renderReviewsSection();
      }
    });
  }
};

// Inicializa quando o DOM está pronto
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => ReviewsManager.init());
} else {
  ReviewsManager.init();
}
