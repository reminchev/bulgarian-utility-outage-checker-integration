class BulgarianUtilityOutageCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  setConfig(config) {
    if (!config.entity) {
      throw new Error('Моля, задайте entity (binary_sensor)');
    }
    this.config = config;
    this.render();
  }

  set hass(hass) {
    this._hass = hass;
    this.render();
  }

  getCardSize() {
    return 3;
  }

  render() {
    if (!this.config || !this._hass) {
      return;
    }

    const entityId = this.config.entity;
    const entity = this._hass.states[entityId];
    
    if (!entity) {
      this.shadowRoot.innerHTML = `
        <ha-card>
          <div style="padding: 16px;">
            <div style="color: var(--error-color); font-weight: bold;">
              Грешка: Entity не е намерен
            </div>
          </div>
        </ha-card>
      `;
      return;
    }

    // Get related entities (status, last check, next check sensors)
    const deviceId = entityId.replace('binary_sensor.', '');
    const statusEntityId = `sensor.${deviceId.replace('_outage', '')}_status`;
    const lastCheckEntityId = `sensor.${deviceId.replace('_outage', '')}_последна_проверка`;
    const nextCheckEntityId = `sensor.${deviceId.replace('_outage', '')}_следваща_проверка`;
    
    const statusEntity = this._hass.states[statusEntityId];
    const lastCheckEntity = this._hass.states[lastCheckEntityId];
    const nextCheckEntity = this._hass.states[nextCheckEntityId];

    const hasOutage = entity.state === 'on';
    const outageType = entity.attributes.outage_type || 'Unknown';
    const details = entity.attributes.details || [];
    const lastCheck = lastCheckEntity ? lastCheckEntity.state : 'N/A';
    const nextCheck = nextCheckEntity ? this.formatDateTime(nextCheckEntity.state) : 'N/A';
    
    // Determine colors and icons
    let statusColor = hasOutage ? '#f44336' : '#4caf50';
    let statusIcon = hasOutage ? 'mdi:alert-circle' : 'mdi:check-circle';
    let statusText = hasOutage ? outageType : 'Няма аварии';
    
    if (outageType.includes('Планирана')) {
      statusColor = '#ff9800';
      statusIcon = 'mdi:calendar-clock';
    }

    this.shadowRoot.innerHTML = `
      <style>
        ha-card {
          padding: 16px;
          cursor: default;
        }
        .header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 16px;
          padding-bottom: 12px;
          border-bottom: 2px solid var(--divider-color);
        }
        .header-left {
          display: flex;
          align-items: center;
          gap: 12px;
        }
        .status-icon {
          color: ${statusColor};
          font-size: 36px;
        }
        .title {
          font-size: 18px;
          font-weight: 500;
          color: var(--primary-text-color);
        }
        .status-text {
          font-size: 16px;
          font-weight: bold;
          color: ${statusColor};
          margin-top: 4px;
        }
        .check-button {
          padding: 8px 16px;
          background-color: var(--primary-color);
          color: var(--text-primary-color);
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
          font-weight: 500;
          transition: background-color 0.3s;
          display: flex;
          align-items: center;
          gap: 6px;
        }
        .check-button:hover {
          background-color: var(--primary-color-dark);
        }
        .check-button:active {
          transform: scale(0.98);
        }
        .info-section {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 12px;
          margin-top: 12px;
        }
        .info-item {
          background: var(--card-background-color);
          padding: 12px;
          border-radius: 8px;
          border: 1px solid var(--divider-color);
        }
        .info-label {
          font-size: 12px;
          color: var(--secondary-text-color);
          margin-bottom: 4px;
          display: flex;
          align-items: center;
          gap: 6px;
        }
        .info-value {
          font-size: 14px;
          font-weight: 500;
          color: var(--primary-text-color);
        }
        .details-section {
          margin-top: 16px;
          padding-top: 12px;
          border-top: 1px solid var(--divider-color);
        }
        .details-title {
          font-size: 14px;
          font-weight: 500;
          color: var(--primary-text-color);
          margin-bottom: 8px;
        }
        .details-list {
          max-height: 200px;
          overflow-y: auto;
        }
        .detail-item {
          padding: 8px;
          margin-bottom: 4px;
          background: var(--secondary-background-color);
          border-radius: 4px;
          font-size: 13px;
          color: var(--primary-text-color);
        }
        .no-details {
          color: var(--secondary-text-color);
          font-style: italic;
          font-size: 13px;
        }
        ha-icon {
          width: 20px;
          height: 20px;
        }
        .loading {
          opacity: 0.6;
          pointer-events: none;
        }
      </style>
      <ha-card>
        <div class="header">
          <div class="header-left">
            <ha-icon class="status-icon" icon="${statusIcon}"></ha-icon>
            <div>
              <div class="title">${this.config.title || 'Проверка за Аварии'}</div>
              <div class="status-text">${statusText}</div>
            </div>
          </div>
          <button class="check-button" @click="${() => this.checkNow()}">
            <ha-icon icon="mdi:refresh"></ha-icon>
            <span>Провери сега</span>
          </button>
        </div>
        
        <div class="info-section">
          <div class="info-item">
            <div class="info-label">
              <ha-icon icon="mdi:clock-check"></ha-icon>
              <span>Последна проверка</span>
            </div>
            <div class="info-value">${lastCheck}</div>
          </div>
          <div class="info-item">
            <div class="info-label">
              <ha-icon icon="mdi:clock-alert"></ha-icon>
              <span>Следваща проверка</span>
            </div>
            <div class="info-value">${nextCheck}</div>
          </div>
        </div>
        
        ${hasOutage && details.length > 0 ? `
          <div class="details-section">
            <div class="details-title">Детайли за аварията:</div>
            <div class="details-list">
              ${details.map(detail => `<div class="detail-item">${detail}</div>`).join('')}
            </div>
          </div>
        ` : hasOutage ? `
          <div class="details-section">
            <div class="no-details">Няма допълнителна информация.</div>
          </div>
        ` : ''}
      </ha-card>
    `;

    // Attach event listeners
    const button = this.shadowRoot.querySelector('.check-button');
    if (button) {
      button.addEventListener('click', () => this.checkNow());
    }
  }

  formatDateTime(isoString) {
    if (!isoString || isoString === 'Unknown' || isoString === 'N/A') {
      return 'N/A';
    }
    
    try {
      const date = new Date(isoString);
      const now = new Date();
      const diff = date - now;
      
      if (diff < 0) {
        return 'Скоро';
      }
      
      const minutes = Math.floor(diff / 60000);
      const hours = Math.floor(minutes / 60);
      const days = Math.floor(hours / 24);
      
      if (days > 0) {
        return `след ${days} ${days === 1 ? 'ден' : 'дни'}`;
      } else if (hours > 0) {
        return `след ${hours} ${hours === 1 ? 'час' : 'часа'}`;
      } else if (minutes > 0) {
        return `след ${minutes} мин.`;
      } else {
        return 'Скоро';
      }
    } catch (e) {
      return isoString;
    }
  }

  async checkNow() {
    if (!this._hass || !this.config.entity) {
      return;
    }

    const button = this.shadowRoot.querySelector('.check-button');
    if (button) {
      button.classList.add('loading');
      button.innerHTML = '<ha-icon icon="mdi:loading"></ha-icon><span>Проверка...</span>';
    }

    try {
      await this._hass.callService('bulgarian_utility_outage_checker', 'check_now', {
        entity_id: this.config.entity
      });
      
      // Wait a bit for the update
      setTimeout(() => {
        this.render();
      }, 2000);
    } catch (error) {
      console.error('Error calling check_now service:', error);
      alert('Грешка при извикване на услугата. Моля, проверете логовете.');
    }
  }
}

customElements.define('bulgarian-utility-outage-card', BulgarianUtilityOutageCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: 'bulgarian-utility-outage-card',
  name: 'Bulgarian Utility Outage Card',
  description: 'Карта за проверка на аварии на ток',
  preview: false,
  documentationURL: 'https://github.com/reminchev/bulgarian-utility-outage-checker-integration',
});

console.info(
  '%c BULGARIAN-UTILITY-OUTAGE-CARD %c Version 1.0.0 ',
  'color: white; background: #00bcd4; font-weight: 700;',
  'color: white; background: #00796b; font-weight: 700;',
);
