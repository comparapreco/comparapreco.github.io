/* Compara Preço — Auth, perfil e persistência do usuário
 * Funciona em dois modos:
 * - Firebase ativo: sincroniza dados por usuário no Firestore e Login Google.
 * - Fallback local: mantém a experiência funcionando via localStorage em GitHub Pages.
 */
(function () {
  'use strict';

  const DEFAULT_COLLECTIONS_ROOT = 'users';
  const LOCAL_USER_KEY = 'compara_local_user';
  const LOCAL_DATA_PREFIX = 'compara_user_data_';
  const VIEW_HISTORY_KEY = 'compara_view_history';
  const CLICK_HISTORY_KEY = 'compara_click_history';

  const state = {
    initialized: false,
    firebaseReady: false,
    user: null,
    listeners: [],
    initPromise: null
  };

  function isFirebaseConfigured() {
    const config = window.COMPARA_FIREBASE_CONFIG || {};
    const options = window.COMPARA_FIREBASE_OPTIONS || {};
    return Boolean(options.enabled && config.apiKey && config.authDomain && config.projectId && config.appId);
  }

  function loadScript(src) {
    return new Promise((resolve, reject) => {
      if (document.querySelector(`script[src="${src}"]`)) return resolve();
      const script = document.createElement('script');
      script.src = src;
      script.async = true;
      script.onload = resolve;
      script.onerror = reject;
      document.head.appendChild(script);
    });
  }

  async function loadFirebaseCompat() {
    await loadScript('https://www.gstatic.com/firebasejs/10.12.5/firebase-app-compat.js');
    await loadScript('https://www.gstatic.com/firebasejs/10.12.5/firebase-auth-compat.js');
    await loadScript('https://www.gstatic.com/firebasejs/10.12.5/firebase-firestore-compat.js');
  }

  function createLocalUser() {
    const existing = localStorage.getItem(LOCAL_USER_KEY);
    if (existing) return JSON.parse(existing);

    const id = 'local_' + Math.random().toString(36).slice(2) + Date.now().toString(36);
    const user = {
      uid: id,
      displayName: 'Visitante Compara Preço',
      email: '',
      photoURL: '',
      isAnonymous: true,
      provider: 'local'
    };
    localStorage.setItem(LOCAL_USER_KEY, JSON.stringify(user));
    return user;
  }

  function normalizeUser(user) {
    if (!user) return null;
    return {
      uid: user.uid,
      displayName: user.displayName || 'Usuário Compara Preço',
      email: user.email || '',
      photoURL: user.photoURL || '',
      isAnonymous: Boolean(user.isAnonymous),
      provider: user.provider || (user.providerData && user.providerData[0] ? user.providerData[0].providerId : 'google')
    };
  }

  function notifyAuthChange() {
    window.dispatchEvent(new CustomEvent('compara:auth-change', { detail: { user: state.user, firebaseReady: state.firebaseReady } }));
    state.listeners.forEach(listener => {
      try { listener(state.user, state.firebaseReady); } catch (error) { console.error(error); }
    });
  }

  async function ensureProfile(user) {
    if (!state.firebaseReady || !user || user.provider === 'local') return;
    const db = firebase.firestore();
    const root = (window.COMPARA_FIREBASE_OPTIONS && window.COMPARA_FIREBASE_OPTIONS.collectionsRoot) || DEFAULT_COLLECTIONS_ROOT;
    const ref = db.collection(root).doc(user.uid);
    const snap = await ref.get();
    const profile = {
      uid: user.uid,
      displayName: user.displayName,
      email: user.email,
      photoURL: user.photoURL,
      updatedAt: firebase.firestore.FieldValue.serverTimestamp()
    };
    if (!snap.exists) {
      await ref.set({ ...profile, createdAt: firebase.firestore.FieldValue.serverTimestamp(), settings: defaultSettings() }, { merge: true });
    } else {
      await ref.set(profile, { merge: true });
    }
  }

  function defaultSettings() {
    return {
      newsletter: false,
      pushNotifications: false,
      dailyDigest: true,
      publicProfile: false,
      targetCategories: []
    };
  }

  function localKey(collection) {
    const uid = state.user ? state.user.uid : 'guest';
    return `${LOCAL_DATA_PREFIX}${uid}_${collection}`;
  }

  function parseLocal(collection, fallback) {
    try {
      const value = localStorage.getItem(localKey(collection));
      return value ? JSON.parse(value) : fallback;
    } catch (_) {
      return fallback;
    }
  }

  function saveLocal(collection, value) {
    localStorage.setItem(localKey(collection), JSON.stringify(value));
    window.dispatchEvent(new CustomEvent('compara:data-change', { detail: { collection, value } }));
    return value;
  }

  async function init() {
    if (state.initPromise) return state.initPromise;

    state.initPromise = (async () => {
      if (isFirebaseConfigured()) {
        try {
          await loadFirebaseCompat();
          if (!firebase.apps.length) firebase.initializeApp(window.COMPARA_FIREBASE_CONFIG);
          state.firebaseReady = true;
          firebase.auth().onAuthStateChanged(async firebaseUser => {
            state.user = firebaseUser ? normalizeUser(firebaseUser) : createLocalUser();
            await ensureProfile(state.user);
            notifyAuthChange();
          });
        } catch (error) {
          console.warn('Firebase indisponível; usando fallback local.', error);
          state.firebaseReady = false;
          state.user = createLocalUser();
          notifyAuthChange();
        }
      } else {
        state.firebaseReady = false;
        state.user = createLocalUser();
        notifyAuthChange();
      }

      state.initialized = true;
      renderHeaderAuth();
      window.addEventListener('compara:auth-change', renderHeaderAuth);
      return state.user;
    })();

    return state.initPromise;
  }

  async function signInGoogle() {
    await init();
    if (!state.firebaseReady) {
      alert('Para ativar Login Google, preencha assets/js/firebase-config.js com os dados do Firebase e defina enabled: true. Enquanto isso, seus dados ficam salvos neste navegador.');
      return state.user;
    }
    const provider = new firebase.auth.GoogleAuthProvider();
    provider.setCustomParameters({ prompt: 'select_account' });
    const result = await firebase.auth().signInWithPopup(provider);
    state.user = normalizeUser(result.user);
    await ensureProfile(state.user);
    notifyAuthChange();
    return state.user;
  }

  async function signOut() {
    if (state.firebaseReady) await firebase.auth().signOut();
    state.user = createLocalUser();
    notifyAuthChange();
  }

  async function getCollection(collection, fallback) {
    await init();
    if (state.firebaseReady && state.user && state.user.provider !== 'local') {
      const root = (window.COMPARA_FIREBASE_OPTIONS && window.COMPARA_FIREBASE_OPTIONS.collectionsRoot) || DEFAULT_COLLECTIONS_ROOT;
      const snap = await firebase.firestore().collection(root).doc(state.user.uid).collection(collection).get();
      return snap.docs.map(doc => ({ id: doc.id, ...doc.data() }));
    }
    return parseLocal(collection, fallback || []);
  }

  async function setCollection(collection, values) {
    await init();
    const normalized = Array.isArray(values) ? values : [];
    if (state.firebaseReady && state.user && state.user.provider !== 'local') {
      const root = (window.COMPARA_FIREBASE_OPTIONS && window.COMPARA_FIREBASE_OPTIONS.collectionsRoot) || DEFAULT_COLLECTIONS_ROOT;
      const base = firebase.firestore().collection(root).doc(state.user.uid).collection(collection);
      const current = await base.get();
      const batch = firebase.firestore().batch();
      current.docs.forEach(doc => batch.delete(doc.ref));
      normalized.forEach(item => {
        const id = String(item.id || item.productId || Date.now() + Math.random());
        batch.set(base.doc(id), { ...item, id, updatedAt: firebase.firestore.FieldValue.serverTimestamp() }, { merge: true });
      });
      await batch.commit();
      window.dispatchEvent(new CustomEvent('compara:data-change', { detail: { collection, value: normalized } }));
      return normalized;
    }
    return saveLocal(collection, normalized);
  }

  async function upsertItem(collection, item) {
    const list = await getCollection(collection, []);
    const id = String(item.id || item.productId || Date.now());
    const index = list.findIndex(entry => String(entry.id || entry.productId) === id || String(entry.productId) === String(item.productId));
    const payload = { ...item, id, updatedAt: new Date().toISOString() };
    if (index >= 0) list[index] = { ...list[index], ...payload };
    else list.push(payload);
    return setCollection(collection, list);
  }

  async function removeItem(collection, id) {
    const list = await getCollection(collection, []);
    return setCollection(collection, list.filter(entry => String(entry.id || entry.productId) !== String(id)));
  }

  async function getSettings() {
    await init();
    const defaults = defaultSettings();
    if (state.firebaseReady && state.user && state.user.provider !== 'local') {
      const root = (window.COMPARA_FIREBASE_OPTIONS && window.COMPARA_FIREBASE_OPTIONS.collectionsRoot) || DEFAULT_COLLECTIONS_ROOT;
      const doc = await firebase.firestore().collection(root).doc(state.user.uid).get();
      return { ...defaults, ...(doc.exists && doc.data().settings ? doc.data().settings : {}) };
    }
    return { ...defaults, ...parseLocal('settings', {}) };
  }

  async function saveSettings(settings) {
    await init();
    const merged = { ...(await getSettings()), ...settings };
    if (state.firebaseReady && state.user && state.user.provider !== 'local') {
      const root = (window.COMPARA_FIREBASE_OPTIONS && window.COMPARA_FIREBASE_OPTIONS.collectionsRoot) || DEFAULT_COLLECTIONS_ROOT;
      await firebase.firestore().collection(root).doc(state.user.uid).set({ settings: merged, updatedAt: firebase.firestore.FieldValue.serverTimestamp() }, { merge: true });
      return merged;
    }
    saveLocal('settings', merged);
    return merged;
  }

  function trackProductView(product) {
    if (!product || !product.id) return;
    const history = JSON.parse(localStorage.getItem(VIEW_HISTORY_KEY) || '[]');
    const item = {
      productId: product.id,
      name: product.name || product.title,
      category: product.custom_category_slug || '',
      price: product.price || 0,
      viewedAt: new Date().toISOString()
    };
    const filtered = history.filter(entry => entry.productId !== product.id).slice(0, 99);
    localStorage.setItem(VIEW_HISTORY_KEY, JSON.stringify([item, ...filtered]));
  }

  function trackProductClick(product) {
    if (!product || !product.id) return;
    const history = JSON.parse(localStorage.getItem(CLICK_HISTORY_KEY) || '[]');
    history.unshift({
      productId: product.id,
      name: product.name || product.title,
      category: product.custom_category_slug || '',
      price: product.price || 0,
      clickedAt: new Date().toISOString()
    });
    localStorage.setItem(CLICK_HISTORY_KEY, JSON.stringify(history.slice(0, 200)));
  }

  function getBehaviorHistory() {
    return {
      views: JSON.parse(localStorage.getItem(VIEW_HISTORY_KEY) || '[]'),
      clicks: JSON.parse(localStorage.getItem(CLICK_HISTORY_KEY) || '[]')
    };
  }

  function renderHeaderAuth() {
    const headers = document.querySelectorAll('.header-inner');
    if (!headers.length) return;
    headers.forEach(header => {
      let slot = header.querySelector('.compara-auth-widget');
      if (!slot) {
        slot = document.createElement('div');
        slot.className = 'compara-auth-widget';
        header.appendChild(slot);
      }
      const user = state.user;
      const label = user && !user.isAnonymous && user.provider !== 'local' ? (user.displayName || 'Conta') : 'Entrar';
      const photo = user && user.photoURL ? `<img src="${escapeHtml(user.photoURL)}" alt="${escapeHtml(label)}">` : '<span class="compara-auth-avatar">👤</span>';
      slot.innerHTML = `
        <a class="compara-auth-link" href="${relativePath('minha-lista/')}">Minha lista</a>
        <button class="compara-auth-button" type="button" data-auth-action="${user && user.provider !== 'local' ? 'logout' : 'login'}">${photo}<span>${escapeHtml(label)}</span></button>
      `;
      slot.querySelector('[data-auth-action]')?.addEventListener('click', async () => {
        const action = slot.querySelector('[data-auth-action]').dataset.authAction;
        if (action === 'login') await signInGoogle(); else await signOut();
      });
    });
  }

  function relativePath(target) {
    const pathParts = window.location.pathname.split('/').filter(Boolean);
    const isGithub = window.location.hostname.includes('github.io');
    const depth = isGithub ? Math.max(pathParts.length - 1, 0) : pathParts.length;
    return '../'.repeat(depth) + target;
  }

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text || '';
    return div.innerHTML;
  }

  window.Compara PreçoAuth = {
    init,
    signInGoogle,
    signOut,
    getUser: () => state.user,
    isFirebaseReady: () => state.firebaseReady,
    onAuthChange: listener => { state.listeners.push(listener); return () => state.listeners = state.listeners.filter(item => item !== listener); },
    getCollection,
    setCollection,
    upsertItem,
    removeItem,
    getSettings,
    saveSettings,
    trackProductView,
    trackProductClick,
    getBehaviorHistory,
    defaultSettings
  };

  document.addEventListener('DOMContentLoaded', init);
})();
