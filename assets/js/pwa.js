// Fase 10 — PWA, instalação e notificações locais do Radar
(function () {
  'use strict';

  const ROOT_PATH = window.location.pathname.includes('/radar/') ? '/radar/' : '/';
  let deferredPrompt = null;

  function createInstallButton() {
    if (document.getElementById('radarInstallPwa')) return;
    const button = document.createElement('button');
    button.id = 'radarInstallPwa';
    button.className = 'radar-auth-button';
    button.style.position = 'fixed';
    button.style.right = '16px';
    button.style.bottom = '16px';
    button.style.zIndex = '80';
    button.style.display = 'none';
    button.textContent = 'Instalar Radar';
    button.addEventListener('click', async () => {
      if (!deferredPrompt) return;
      deferredPrompt.prompt();
      await deferredPrompt.userChoice;
      deferredPrompt = null;
      button.style.display = 'none';
    });
    document.body.appendChild(button);
  }

  async function registerServiceWorker() {
    if (!('serviceWorker' in navigator)) return;
    try {
      await navigator.serviceWorker.register(ROOT_PATH + 'sw.js', { scope: ROOT_PATH });
    } catch (error) {
      console.warn('Service worker não registrado:', error);
    }
  }

  async function requestNotifications() {
    if (!('Notification' in window)) return false;
    if (Notification.permission === 'granted') return true;
    if (Notification.permission === 'denied') return false;
    const permission = await Notification.requestPermission();
    return permission === 'granted';
  }

  async function notify(title, options = {}) {
    const allowed = await requestNotifications();
    if (!allowed) return;
    if ('serviceWorker' in navigator) {
      const registration = await navigator.serviceWorker.ready;
      registration.showNotification(title, {
        badge: ROOT_PATH + 'assets/icons/icon-192.png',
        icon: ROOT_PATH + 'assets/icons/icon-192.png',
        ...options
      });
    } else {
      new Notification(title, options);
    }
  }

  function exposeApi() {
    window.RadarPWA = {
      requestNotifications,
      notify,
      async testPriceAlert() {
        await notify('Radar de Preços', {
          body: 'Exemplo de alerta: um produto monitorado atingiu o preço desejado.',
          data: { url: ROOT_PATH + 'minha-lista/' }
        });
      }
    };
  }

  window.addEventListener('beforeinstallprompt', event => {
    event.preventDefault();
    deferredPrompt = event;
    createInstallButton();
    const button = document.getElementById('radarInstallPwa');
    if (button) button.style.display = 'inline-flex';
  });

  window.addEventListener('appinstalled', () => {
    deferredPrompt = null;
    const button = document.getElementById('radarInstallPwa');
    if (button) button.style.display = 'none';
  });

  document.addEventListener('DOMContentLoaded', () => {
    createInstallButton();
    registerServiceWorker();
    exposeApi();
  });
})();
