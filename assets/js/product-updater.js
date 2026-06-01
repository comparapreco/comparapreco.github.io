// ========== ROBÔ DE ATUALIZAÇÃO DE PRODUTOS ==========
// Este script adiciona selos de "ATUALIZADO" e coloca produtos novos no topo

function addUpdatedBadge(products) {
  return products.map(product => {
    // Se o produto não tem data de atualização, usar a data atual
    if (!product.data_atualizacao) {
      product.data_atualizacao = new Date().toISOString();
    }
    return product;
  });
}

function sortProductsByRecency(products) {
  return [...products].sort((a, b) => {
    // Primeiro: ordenar por data de atualização (mais recentes primeiro)
    const dateA = new Date(a.data_atualizacao || new Date());
    const dateB = new Date(b.data_atualizacao || new Date());
    
    if (dateB.getTime() !== dateA.getTime()) {
      return dateB.getTime() - dateA.getTime();
    }
    
    // Segundo: ordenar por desconto (maior desconto primeiro)
    return (b.custom_discount_pct || 0) - (a.custom_discount_pct || 0);
  });
}

function getDaysAgoText(dateString) {
  if (!dateString) return null;
  
  const date = new Date(dateString);
  const now = new Date();
  const diffTime = Math.abs(now - date);
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  
  if (diffDays === 0) return "Hoje";
  if (diffDays === 1) return "Ontem";
  if (diffDays <= 7) return `${diffDays}d atrás`;
  if (diffDays <= 30) return `${Math.floor(diffDays / 7)}s atrás`;
  return `${Math.floor(diffDays / 30)}m atrás`;
}

// Interceptar a função renderProducts original
const originalRenderProducts = window.renderProducts;

window.renderProducts = function(products) {
  // Adicionar badges de atualização
  const productsWithBadges = addUpdatedBadge(products);
  
  // Ordenar por recência
  const sortedProducts = sortProductsByRecency(productsWithBadges);
  
  // Chamar a função original com os produtos ordenados
  originalRenderProducts.call(this, sortedProducts);
};

// Exportar funções para uso externo
window.productUpdater = {
  addUpdatedBadge,
  sortProductsByRecency,
  getDaysAgoText
};

console.log("✅ Robô de atualização de produtos ativado!");
