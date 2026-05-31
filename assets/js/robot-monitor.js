/**
 * 🤖 ROBOT MONITOR - Sistema de Monitoramento em Tempo Real
 * Exibe status do robô, histórico de disparos e alertas de falhas
 * 
 * Funcionalidades:
 * - Dashboard com status do robô (verde/vermelho)
 * - Histórico de últimos disparos
 * - Notificações de erro em tempo real
 * - Log de artigos processados
 * - Integração com GitHub API
 */

class RobotMonitor {
  constructor(config = {}) {
    this.config = {
      githubToken: config.githubToken || '',
      owner: 'radardeprecos',
      repo: 'radar',
      checkInterval: config.checkInterval || 5 * 60 * 1000, // 5 minutos
      maxHistoryItems: config.maxHistoryItems || 50,
      ...config
    };

    this.storageKey = 'robotMonitorData';
    this.data = this.loadData();
    this.lastCommitSha = this.data.lastCommitSha || '';
    this.lastCheckTime = this.data.lastCheckTime || null;
    this.isOnline = true;

    this.init();
  }

  /**
   * Inicializa o monitor
   */
  init() {
    console.log('🤖 Robot Monitor iniciado');
    this.renderDashboard();
    this.checkRobotStatus();
    
    // Verifica status a cada intervalo
    setInterval(() => this.checkRobotStatus(), this.config.checkInterval);
    
    // Atualiza UI a cada 10 segundos
    setInterval(() => this.updateUI(), 10000);
  }

  /**
   * Carrega dados do localStorage
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
      history: [],
      lastCommitSha: '',
      lastCheckTime: null,
      status: 'unknown', // online, offline, error
      lastSuccessTime: null,
      failureCount: 0,
      successCount: 0,
      lastError: null
    };
  }

  /**
   * Salva dados em localStorage
   */
  saveData() {
    localStorage.setItem(this.storageKey, JSON.stringify(this.data));
  }

  /**
   * Verifica status do robô consultando GitHub
   */
  async checkRobotStatus() {
    try {
      console.log('🔍 Verificando status do robô...');
      
      const commits = await this.fetchCommits();
      if (!commits || commits.length === 0) {
        this.setStatus('offline', 'Nenhum commit encontrado');
        return;
      }

      const latestCommit = commits[0];
      const commitTime = new Date(latestCommit.commit.author.date);
      const timeSinceLastCommit = Date.now() - commitTime.getTime();
      const hoursAgo = timeSinceLastCommit / (1000 * 60 * 60);

      // Se o último commit foi há menos de 1 hora, robô está ativo
      if (hoursAgo < 1) {
        this.setStatus('online', 'Robô ativo e funcionando');
        this.recordSuccess(latestCommit);
      } else if (hoursAgo < 24) {
        this.setStatus('warning', `Último disparo há ${hoursAgo.toFixed(1)} horas`);
      } else {
        this.setStatus('offline', `Último disparo há ${Math.floor(hoursAgo)} horas`);
      }

      this.lastCheckTime = new Date();
      this.saveData();
      
    } catch (error) {
      console.error('❌ Erro ao verificar status:', error);
      this.setStatus('error', `Erro: ${error.message}`);
    }
  }

  /**
   * Busca commits do GitHub
   */
  async fetchCommits(page = 1) {
    try {
      const url = `https://api.github.com/repos/${this.config.owner}/${this.config.repo}/commits?per_page=20&page=${page}`;
      
      const headers = {
        'Accept': 'application/vnd.github.v3+json'
      };

      // Adiciona token se disponível (aumenta rate limit)
      if (this.config.githubToken) {
        headers['Authorization'] = `token ${this.config.githubToken}`;
      }

      const response = await fetch(url, { headers });
      
      if (!response.ok) {
        throw new Error(`GitHub API error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Erro ao buscar commits:', error);
      throw error;
    }
  }

  /**
   * Define status do robô
   */
  setStatus(status, message) {
    const oldStatus = this.data.status;
    this.data.status = status;
    this.data.lastStatusMessage = message;
    this.data.lastCheckTime = new Date().toISOString();

    // Se mudou de online para offline, registra erro
    if (oldStatus === 'online' && status !== 'online') {
      this.recordFailure(message);
    }

    this.saveData();
    console.log(`🤖 Status: ${status} - ${message}`);
  }

  /**
   * Registra sucesso do robô
   */
  recordSuccess(commit) {
    this.data.lastSuccessTime = new Date().toISOString();
    this.data.successCount = (this.data.successCount || 0) + 1;
    this.data.failureCount = 0; // Reset contador de falhas
    this.data.lastError = null;

    const historyItem = {
      type: 'success',
      timestamp: this.data.lastSuccessTime,
      commitSha: commit.sha,
      commitMessage: commit.commit.message,
      author: commit.commit.author.name,
      url: commit.html_url
    };

    this.addToHistory(historyItem);
    this.notifySuccess(commit);
  }

  /**
   * Registra falha do robô
   */
  recordFailure(message) {
    this.data.failureCount = (this.data.failureCount || 0) + 1;
    this.data.lastError = {
      timestamp: new Date().toISOString(),
      message: message
    };

    const historyItem = {
      type: 'failure',
      timestamp: this.data.lastError.timestamp,
      message: message
    };

    this.addToHistory(historyItem);
    this.notifyFailure(message);
  }

  /**
   * Adiciona item ao histórico
   */
  addToHistory(item) {
    if (!Array.isArray(this.data.history)) {
      this.data.history = [];
    }

    this.data.history.unshift(item); // Adiciona no início
    
    // Mantém apenas os últimos N items
    if (this.data.history.length > this.config.maxHistoryItems) {
      this.data.history = this.data.history.slice(0, this.config.maxHistoryItems);
    }

    this.saveData();
  }

  /**
   * Notifica sucesso
   */
  notifySuccess(commit) {
    const message = `✅ Robô disparou com sucesso!\n${commit.commit.message}`;
    console.log(message);
    
    // Mostrar notificação no desktop (se permitido)
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification('🤖 Robô Ativo', {
        body: commit.commit.message,
        icon: '✅'
      });
    }
  }

  /**
   * Notifica falha
   */
  notifyFailure(message) {
    const fullMessage = `❌ Robô não disparou!\n${message}`;
    console.error(fullMessage);
    
    // Mostrar notificação no desktop
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification('🚨 Robô Offline', {
        body: message,
        icon: '❌'
      });
    }
  }

  /**
   * Renderiza o dashboard
   */
  renderDashboard() {
    const dashboard = document.getElementById('robotMonitorDashboard');
    if (!dashboard) {
      console.warn('⚠️ Elemento #robotMonitorDashboard não encontrado');
      return;
    }

    dashboard.innerHTML = `
      <div class="robot-monitor" style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 20px;
        color: white;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        font-family: 'Inter', sans-serif;
      ">
        <!-- CABEÇALHO -->
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
          <div>
            <h2 style="margin: 0; font-size: 24px;">🤖 Status do Robô</h2>
            <p style="margin: 5px 0 0 0; opacity: 0.9; font-size: 14px;">Monitoramento em tempo real</p>
          </div>
          <button id="robotRefreshBtn" style="
            background: rgba(255,255,255,0.2);
            border: 2px solid white;
            color: white;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.3s;
          ">🔄 Atualizar</button>
        </div>

        <!-- STATUS PRINCIPAL -->
        <div style="
          background: rgba(255,255,255,0.1);
          backdrop-filter: blur(10px);
          border-radius: 8px;
          padding: 15px;
          margin-bottom: 15px;
        ">
          <div style="display: flex; align-items: center; gap: 12px;">
            <div id="robotStatusIndicator" style="
              width: 20px;
              height: 20px;
              border-radius: 50%;
              background: #4ade80;
              animation: pulse 2s infinite;
              box-shadow: 0 0 10px rgba(74,222,128,0.6);
            "></div>
            <div>
              <div style="font-size: 16px; font-weight: 600;" id="robotStatusText">Verificando...</div>
              <div style="font-size: 13px; opacity: 0.8;" id="robotStatusMessage">Conectando ao GitHub...</div>
            </div>
          </div>
        </div>

        <!-- ESTATÍSTICAS -->
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 15px;">
          <div style="
            background: rgba(74,222,128,0.2);
            border-left: 4px solid #4ade80;
            padding: 10px;
            border-radius: 4px;
          ">
            <div style="font-size: 12px; opacity: 0.8;">Sucessos</div>
            <div style="font-size: 20px; font-weight: 700;" id="robotSuccessCount">0</div>
          </div>
          <div style="
            background: rgba(239,68,68,0.2);
            border-left: 4px solid #ef4444;
            padding: 10px;
            border-radius: 4px;
          ">
            <div style="font-size: 12px; opacity: 0.8;">Falhas</div>
            <div style="font-size: 20px; font-weight: 700;" id="robotFailureCount">0</div>
          </div>
        </div>

        <!-- ÚLTIMO DISPARO -->
        <div style="
          background: rgba(255,255,255,0.05);
          border: 1px solid rgba(255,255,255,0.1);
          border-radius: 8px;
          padding: 12px;
          margin-bottom: 15px;
          font-size: 13px;
        ">
          <div style="opacity: 0.7; margin-bottom: 5px;">Última verificação:</div>
          <div style="font-family: monospace; word-break: break-all;" id="robotLastCheck">-</div>
        </div>

        <!-- HISTÓRICO -->
        <div>
          <div style="font-size: 14px; font-weight: 600; margin-bottom: 10px;">📋 Histórico (últimos 10)</div>
          <div id="robotHistory" style="
            background: rgba(255,255,255,0.05);
            border-radius: 6px;
            max-height: 250px;
            overflow-y: auto;
            border: 1px solid rgba(255,255,255,0.1);
          ">
            <div style="padding: 15px; text-align: center; opacity: 0.6;">
              Carregando histórico...
            </div>
          </div>
        </div>

        <!-- BOTÃO ATIVAR NOTIFICAÇÕES -->
        <button id="robotNotifBtn" style="
          width: 100%;
          background: rgba(255,255,255,0.2);
          border: 1px solid rgba(255,255,255,0.3);
          color: white;
          padding: 10px;
          border-radius: 6px;
          margin-top: 15px;
          cursor: pointer;
          font-size: 13px;
          font-weight: 500;
          transition: all 0.3s;
        ">🔔 Ativar Notificações do Robô</button>
      </div>

      <style>
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }

        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateX(-10px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }

        .robot-monitor .history-item {
          animation: slideIn 0.3s ease;
          padding: 10px;
          border-bottom: 1px solid rgba(255,255,255,0.05);
          font-size: 12px;
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .robot-monitor .history-item:hover {
          background: rgba(255,255,255,0.05);
        }

        .robot-monitor .history-item:last-child {
          border-bottom: none;
        }

        .robot-monitor .status-success {
          color: #4ade80;
        }

        .robot-monitor .status-failure {
          color: #ef4444;
        }

        .robot-monitor .status-warning {
          color: #f59e0b;
        }
      </style>
    `;

    // Configura event listeners
    document.getElementById('robotRefreshBtn').addEventListener('click', () => {
      this.checkRobotStatus();
    });

    document.getElementById('robotNotifBtn').addEventListener('click', () => {
      this.requestNotificationPermission();
    });
  }

  /**
   * Atualiza a UI com dados atuais
   */
  updateUI() {
    // Atualiza indicador de status
    const indicator = document.getElementById('robotStatusIndicator');
    const statusText = document.getElementById('robotStatusText');
    const statusMessage = document.getElementById('robotStatusMessage');
    
    if (!indicator || !statusText) return;

    const status = this.data.status;
    const statusMessages = {
      'online': { color: '#4ade80', text: '✅ Online', icon: '✅' },
      'offline': { color: '#ef4444', text: '❌ Offline', icon: '❌' },
      'warning': { color: '#f59e0b', text: '⚠️ Aviso', icon: '⚠️' },
      'error': { color: '#ef4444', text: '❌ Erro', icon: '❌' },
      'unknown': { color: '#6b7280', text: '❓ Desconhecido', icon: '❓' }
    };

    const statusInfo = statusMessages[status] || statusMessages['unknown'];
    indicator.style.background = statusInfo.color;
    indicator.style.boxShadow = `0 0 10px ${statusInfo.color}99`;
    statusText.textContent = statusInfo.text;
    statusMessage.textContent = this.data.lastStatusMessage || 'Verificando...';

    // Atualiza contadores
    document.getElementById('robotSuccessCount').textContent = this.data.successCount || 0;
    document.getElementById('robotFailureCount').textContent = this.data.failureCount || 0;

    // Atualiza última verificação
    if (this.data.lastCheckTime) {
      const lastCheck = new Date(this.data.lastCheckTime);
      const timeAgo = this.getTimeAgo(lastCheck);
      document.getElementById('robotLastCheck').textContent = `${lastCheck.toLocaleString()} (${timeAgo})`;
    }

    // Atualiza histórico
    this.updateHistory();
  }

  /**
   * Atualiza exibição do histórico
   */
  updateHistory() {
    const historyContainer = document.getElementById('robotHistory');
    if (!historyContainer || !Array.isArray(this.data.history)) return;

    const items = this.data.history.slice(0, 10);
    
    if (items.length === 0) {
      historyContainer.innerHTML = '<div style="padding: 15px; text-align: center; opacity: 0.6;">Sem histórico ainda</div>';
      return;
    }

    historyContainer.innerHTML = items.map(item => {
      const timestamp = new Date(item.timestamp);
      const timeAgo = this.getTimeAgo(timestamp);
      
      if (item.type === 'success') {
        return `
          <div class="history-item status-success">
            <span>✅</span>
            <div style="flex: 1;">
              <strong>${item.commitMessage.split('\n')[0]}</strong>
              <div style="opacity: 0.7; font-size: 11px;">${timeAgo}</div>
            </div>
            <a href="${item.url}" target="_blank" style="
              color: inherit;
              text-decoration: none;
              opacity: 0.7;
              font-size: 11px;
              padding: 2px 6px;
              background: rgba(74,222,128,0.1);
              border-radius: 3px;
            ">Ver</a>
          </div>
        `;
      } else {
        return `
          <div class="history-item status-failure">
            <span>❌</span>
            <div style="flex: 1;">
              <strong>Falha</strong>
              <div style="opacity: 0.7; font-size: 11px;">${item.message}</div>
              <div style="opacity: 0.6; font-size: 10px;">${timeAgo}</div>
            </div>
          </div>
        `;
      }
    }).join('');
  }

  /**
   * Converte timestamp para tempo relativo
   */
  getTimeAgo(date) {
    const seconds = Math.floor((Date.now() - date.getTime()) / 1000);
    
    if (seconds < 60) return 'agora';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m atrás`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h atrás`;
    return `${Math.floor(seconds / 86400)}d atrás`;
  }

  /**
   * Solicita permissão para notificações
   */
  requestNotificationPermission() {
    if (!('Notification' in window)) {
      alert('Este navegador não suporta notificações');
      return;
    }

    if (Notification.permission === 'granted') {
      alert('✅ Notificações já ativadas!');
      return;
    }

    if (Notification.permission !== 'denied') {
      Notification.requestPermission().then(permission => {
        if (permission === 'granted') {
          alert('✅ Notificações ativadas com sucesso!');
          new Notification('🤖 Monitor Ativado', {
            body: 'Você receberá notificações quando o robô dispara ou falha'
          });
        }
      });
    }
  }

  /**
   * Exporta relatório de atividade
   */
  exportReport() {
    const report = {
      exportedAt: new Date().toISOString(),
      robotStatus: this.data.status,
      statistics: {
        successCount: this.data.successCount,
        failureCount: this.data.failureCount,
        lastSuccessTime: this.data.lastSuccessTime,
        lastErrorTime: this.data.lastError?.timestamp
      },
      history: this.data.history.slice(0, 20)
    };

    return JSON.stringify(report, null, 2);
  }
}

// Inicializa monitor quando a página carrega
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    window.robotMonitor = new RobotMonitor({
      checkInterval: 5 * 60 * 1000, // Verifica a cada 5 minutos
      maxHistoryItems: 50
    });
  });
} else {
  window.robotMonitor = new RobotMonitor({
    checkInterval: 5 * 60 * 1000,
    maxHistoryItems: 50
  });
}
