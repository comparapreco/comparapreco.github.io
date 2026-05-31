/*
 * Configuração Firebase do Radar de Preços.
 *
 * Para ativar Login Google, Firestore e sincronização real entre dispositivos:
 * 1. Crie um projeto no Firebase Console.
 * 2. Ative Authentication > Google.
 * 3. Ative Firestore Database.
 * 4. Adicione o domínio do GitHub Pages em Authentication > Authorized domains.
 * 5. Substitua os valores abaixo pelos dados públicos do app web Firebase.
 *
 * Observação: estes valores de configuração não são senha. As regras do Firestore
 * e os domínios autorizados são o que protegem o acesso real aos dados.
 */
window.RADAR_FIREBASE_CONFIG = {
  apiKey: "",
  authDomain: "",
  projectId: "",
  storageBucket: "",
  messagingSenderId: "",
  appId: ""
};

window.RADAR_FIREBASE_OPTIONS = {
  enabled: false,
  collectionsRoot: "users",
  publicProfilesRoot: "publicProfiles"
};
