// Service Worker para Radar de Preços
const CACHE_NAME = 'radar-precos-v1';
const STATIC_ASSETS = [
  '/radar/',
  '/radar/index.html',
  '/radar/assets/css/style.css',
  '/radar/assets/js/app.js',
  '/radar/noticias/',
  '/radar/comparativos/',
  '/radar/alertas/',
  '/radar/rankings/',
  '/radar/estatisticas/',
  '/radar/black-friday/',
  '/radar/cupons/',
  '/radar/melhores-2026/'
];

// Instalação do Service Worker
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('Cache aberto');
      return cache.addAll(STATIC_ASSETS).catch((error) => {
        console.log('Erro ao cachear alguns arquivos:', error);
        // Continua mesmo se alguns arquivos falharem
        return Promise.resolve();
      });
    })
  );
  self.skipWaiting();
});

// Ativação do Service Worker
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('Deletando cache antigo:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// Estratégia de cache: Network First, com fallback para Cache
self.addEventListener('fetch', (event) => {
  // Ignorar requisições não-GET
  if (event.request.method !== 'GET') {
    return;
  }

  // Ignorar requisições externas
  if (!event.request.url.includes('/radar/')) {
    return;
  }

  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // Se a requisição foi bem-sucedida, cachear a resposta
        if (response.ok) {
          const cache = caches.open(CACHE_NAME);
          cache.then((c) => c.put(event.request, response.clone()));
        }
        return response;
      })
      .catch(() => {
        // Se falhar, tentar obter do cache
        return caches.match(event.request).then((response) => {
          return response || new Response('Página não disponível offline', {
            status: 503,
            statusText: 'Service Unavailable',
            headers: new Headers({
              'Content-Type': 'text/plain'
            })
          });
        });
      })
  );
});

// Receber mensagens do cliente
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }

  // Notificação de alerta de preço
  if (event.data && event.data.type === 'SHOW_NOTIFICATION') {
    const { title, options } = event.data;
    self.registration.showNotification(title, options);
  }
});

// Notificações Push
self.addEventListener('push', (event) => {
  if (event.data) {
    const data = event.data.json();
    const options = {
      body: data.body || 'Nova oferta encontrada!',
      icon: '/radar/assets/icon-192.png',
      badge: '/radar/assets/badge-72.png',
      tag: 'price-alert',
      requireInteraction: true,
      actions: [
        {
          action: 'open',
          title: 'Ver Oferta'
        },
        {
          action: 'close',
          title: 'Fechar'
        }
      ],
      data: {
        url: data.url || '/radar/'
      }
    };

    event.waitUntil(
      self.registration.showNotification(data.title || 'Radar de Preços', options)
    );
  }
});

// Clique em notificação
self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  if (event.action === 'close') {
    return;
  }

  const urlToOpen = event.notification.data.url || '/radar/';

  event.waitUntil(
    clients.matchAll({
      type: 'window',
      includeUncontrolled: true
    }).then((windowClients) => {
      // Verificar se já existe uma janela aberta
      for (let i = 0; i < windowClients.length; i++) {
        const client = windowClients[i];
        if (client.url === urlToOpen && 'focus' in client) {
          return client.focus();
        }
      }
      // Se não existir, abrir uma nova janela
      if (clients.openWindow) {
        return clients.openWindow(urlToOpen);
      }
    })
  );
});

// Sincronização em background (para alertas)
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-alerts') {
    event.waitUntil(
      fetch('/radar/api/sync-alerts/')
        .then((response) => {
          if (response.ok) {
            return response.json();
          }
          throw new Error('Erro ao sincronizar alertas');
        })
        .then((data) => {
          // Processar alertas e mostrar notificações
          if (data.alerts && data.alerts.length > 0) {
            data.alerts.forEach((alert) => {
              self.registration.showNotification('🔥 Oferta Encontrada!', {
                body: `${alert.product} caiu para R$ ${alert.price}!`,
                icon: '/radar/assets/icon-192.png',
                tag: `alert-${alert.id}`,
                data: { url: alert.url }
              });
            });
          }
        })
        .catch((error) => {
          console.error('Erro na sincronização:', error);
        })
    );
  }
});
