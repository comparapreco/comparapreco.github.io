// PWA Registration e Notificações Push
(function() {
  'use strict';

  // Registrar Service Worker
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
      navigator.serviceWorker.register('/service-worker.js', {
        scope: '/'
      }).then(function(registration) {
        console.log('Service Worker registrado com sucesso:', registration);

        // Verificar atualizações
        registration.addEventListener('updatefound', function() {
          const newWorker = registration.installing;
          newWorker.addEventListener('statechange', function() {
            if (newWorker.state === 'activated') {
              // Notificar usuário sobre atualização
              showUpdateNotification();
            }
          });
        });
      }).catch(function(error) {
        console.log('Erro ao registrar Service Worker:', error);
      });

      // Verificar atualizações a cada 1 hora
      setInterval(function() {
        navigator.serviceWorker.getRegistration('/').then(function(registration) {
          if (registration) {
            registration.update();
          }
        });
      }, 3600000);
    });
  }

  // Solicitar permissão de notificações
  function requestNotificationPermission() {
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission().then(function(permission) {
        if (permission === 'granted') {
          console.log('Permissão de notificação concedida');
          enablePushNotifications();
        }
      });
    }
  }

  // Habilitar notificações push
  function enablePushNotifications() {
    if ('serviceWorker' in navigator && 'PushManager' in window) {
      navigator.serviceWorker.getRegistration('/').then(function(registration) {
        if (registration) {
          registration.pushManager.getSubscription().then(function(subscription) {
            if (!subscription) {
              // Criar nova subscription (em produção, usar VAPID key real)
              const vapidPublicKey = 'BEL0-VAPID-PUBLIC-KEY-HERE';
              registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: urlBase64ToUint8Array(vapidPublicKey)
              }).then(function(subscription) {
                console.log('Push subscription criada:', subscription);
                // Enviar subscription para servidor
                sendSubscriptionToServer(subscription);
              }).catch(function(error) {
                console.log('Erro ao criar push subscription:', error);
              });
            }
          });
        }
      });
    }
  }

  // Converter VAPID key
  function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
      .replace(/\-/g, '+')
      .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
  }

  // Enviar subscription para servidor
  function sendSubscriptionToServer(subscription) {
    fetch('/api/subscribe-push/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        subscription: subscription.toJSON()
      })
    }).then(function(response) {
      if (response.ok) {
        console.log('Subscription enviada para servidor');
      }
    }).catch(function(error) {
      console.log('Erro ao enviar subscription:', error);
    });
  }

  // Mostrar notificação de atualização
  function showUpdateNotification() {
    const message = document.createElement('div');
    message.style.cssText = `
      position: fixed;
      bottom: 20px;
      right: 20px;
      background: #0f766e;
      color: white;
      padding: 16px 24px;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      z-index: 9999;
      font-family: system-ui, -apple-system, sans-serif;
      font-size: 14px;
      display: flex;
      gap: 12px;
      align-items: center;
    `;
    message.innerHTML = `
      <span>✨ Nova versão disponível!</span>
      <button style="
        background: white;
        color: #0f766e;
        border: none;
        padding: 6px 12px;
        border-radius: 4px;
        cursor: pointer;
        font-weight: 600;
        font-size: 12px;
      ">Atualizar</button>
    `;

    const button = message.querySelector('button');
    button.addEventListener('click', function() {
      window.location.reload();
    });

    document.body.appendChild(message);

    // Remover após 10 segundos
    setTimeout(function() {
      message.remove();
    }, 10000);
  }

  // Detectar modo offline/online
  window.addEventListener('online', function() {
    console.log('Voltou online');
    showStatusMessage('✓ Você está online', 'success');
  });

  window.addEventListener('offline', function() {
    console.log('Ficou offline');
    showStatusMessage('⚠ Você está offline. Algumas funcionalidades podem estar limitadas.', 'warning');
  });

  function showStatusMessage(text, type) {
    const message = document.createElement('div');
    message.style.cssText = `
      position: fixed;
      top: 20px;
      left: 50%;
      transform: translateX(-50%);
      background: ${type === 'success' ? '#10b981' : '#f59e0b'};
      color: white;
      padding: 12px 20px;
      border-radius: 6px;
      z-index: 9998;
      font-family: system-ui, -apple-system, sans-serif;
      font-size: 13px;
    `;
    message.textContent = text;
    document.body.appendChild(message);

    setTimeout(function() {
      message.remove();
    }, 3000);
  }

  // Solicitar permissão ao carregar a página
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', requestNotificationPermission);
  } else {
    requestNotificationPermission();
  }

  // Expor funções globalmente
  window.Compara PreçoPWA = {
    requestNotificationPermission: requestNotificationPermission,
    enablePushNotifications: enablePushNotifications,
    showUpdateNotification: showUpdateNotification
  };
})();
