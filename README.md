# Bulgarian Utility Outage Checker Integration

<p align="center">
  <img src="https://raw.githubusercontent.com/reminchev/bulgarian_utility_outage_checker/main/example/logo.png" alt="Bulgarian Utility Outage Checker" width="200"/>
</p>

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
![Version](https://img.shields.io/github/v/release/reminchev/bulgarian-utility-outage-checker-integration)
![Downloads](https://img.shields.io/github/downloads/reminchev/bulgarian-utility-outage-checker-integration/total)

_Home Assistant custom integration for checking planned and unplanned utility outages in Bulgaria._

**Currently supports:**
- **ERM West** (ЕРМ Запад) - Electricity distribution company

## Features / Възможности

- 🔌 **Device Integration** - Creates a device with sensors / Създава устройство със сензори
- 🎨 **UI Configuration** - No YAML needed! / Без нужда от YAML конфигурация
- 📊 **Two Sensors** - Status sensor and binary sensor / Статус сензор и binary sensor
- ⏱️ **Configurable interval** - From 1 minute to 24 hours / Конфигурируем интервал
- 🔍 **Custom identifiers** - Subscriber number, location, or street / Поддръжка на идентификатори
- 🌐 **Bilingual** - Bulgarian and English / Двуезичен интерфейс (БГ/EN)
- 🔔 **Automation ready** - Binary sensor for triggers / Готов за автоматизации
- 🏠 **All HA types** - Works on Core, Container, and OS / Работи на всички типове инсталации

## Installation / Инсталация

### HACS (Recommended / Препоръчително)

1. Open **HACS** in Home Assistant
2. Click on **Integrations**
3. Click the **⋮** (three dots) in top right corner
4. Select **Custom repositories**
5. Add this URL: `https://github.com/reminchev/bulgarian-utility-outage-checker-integration`
6. Category: **Integration**
7. Click **Add**
8. Click **Install** on the Bulgarian Utility Outage Checker card
9. **Restart Home Assistant**

### Manual Installation / Ръчна инсталация

1. Copy the `custom_components/bulgarian_utility_outage_checker` folder to your `config/custom_components/` directory
2. Restart Home Assistant

## Configuration / Конфигурация

### Step 1: Add Integration / Стъпка 1: Добавяне на интеграцията

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "**Bulgarian Utility Outage Checker**"
4. Enter your **identifier**:
   - Subscriber number / Номер на абонат: `12345678`
   - Location / Населено място: `София`, `Перник`, `Враца`
   - Street / Улица: `София, ул. Витоша`
   - Address / Адрес: `София, ул. Витоша 25`
5. (Optional) Set **check interval** (default: 60 minutes)
6. Click **Submit**

### Step 2: View Device / Стъпка 2: Преглед на устройството

The integration automatically creates:
- **Device**: `Bulgarian Utility Outage Checker - {your_identifier}`
- **Sensor**: `sensor.bulgarian_utility_outage_checker_{id}_status` - Shows current status
- **Binary Sensor**: `binary_sensor.bulgarian_utility_outage_checker_{id}_outage` - ON when outage detected

## Dashboard Cards / Карти за таблото

### Цветна карта с бутон за проверка (Препоръчително!)

```yaml
type: vertical-stack
cards:
  - type: entity
    entity: binary_sensor.bulgarian_utility_outage_checker_xxx_outage
    name: Статус на електрозахранването
    icon: mdi:transmission-tower
    state_color: true
  - type: button
    name: Провери сега
    icon: mdi:refresh
    tap_action:
      action: call-service
      service: bulgarian_utility_outage_checker.check_now
      service_data:
        entity_id: binary_sensor.bulgarian_utility_outage_checker_xxx_outage
    hold_action:
      action: none
```

### Simple Card / Проста карта

```yaml
type: entities
title: Статус на Електрозахранването
entities:
  - entity: sensor.bulgarian_utility_outage_checker_xxx_status
    name: Статус
  - entity: binary_sensor.bulgarian_utility_outage_checker_xxx_outage
    name: Авария
```

### Detailed Card / Детайлна карта

```yaml
type: entities
title: 🔌 ЕРМ Запад - Мониторинг
entities:
  - entity: binary_sensor.bulgarian_utility_outage_checker_xxx_outage
    name: Статус на електрозахранването
    secondary_info: last-changed
  - type: attribute
    entity: binary_sensor.bulgarian_utility_outage_checker_xxx_outage
    attribute: outage_type
    name: Тип на аварията
  - type: attribute
    entity: binary_sensor.bulgarian_utility_outage_checker_xxx_outage
    attribute: last_check
    name: Последна проверка
  - type: button
    name: Провери сега
    icon: mdi:refresh
    tap_action:
      action: call-service
      service: bulgarian_utility_outage_checker.check_now
      service_data:
        entity_id: binary_sensor.bulgarian_utility_outage_checker_xxx_outage
```

### Conditional Alert Card / Карта за предупреждения

```yaml
type: conditional
conditions:
  - condition: state
    entity: binary_sensor.bulgarian_utility_outage_checker_xxx_outage
    state: 'on'
card:
  type: markdown
  content: >
    ## ⚠️ АВАРИЯ НА ЕЛЕКТРОЗАХРАНВАНЕТО!

    **Тип:** {{ state_attr('binary_sensor.bulgarian_utility_outage_checker_xxx_outage', 'outage_type') }}

    **Последна проверка:** {{ state_attr('binary_sensor.bulgarian_utility_outage_checker_xxx_outage', 'last_check') }}
```

## Automations / Автоматизации

### Send Notification on Outage / Нотификация при авария

```yaml
automation:
  - alias: "Power Outage Alert"
    trigger:
      - platform: state
        entity_id: binary_sensor.bulgarian_utility_outage_checker_xxx_outage
        to: "on"
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "⚠️ Авария на тока!"
          message: >
            {{ state_attr('binary_sensor.bulgarian_utility_outage_checker_xxx_outage', 'outage_type') }}
```

## Configuration Options / Опции за конфигурация

After installation, you can change settings:
1. Go to **Settings** → **Devices & Services**
2. Find **Bulgarian Utility Outage Checker**
3. Click **Configure**
4. Adjust **check interval**

## Troubleshooting / Отстраняване на проблеми

### Integration not found / Интеграцията не се намира
- Ensure `custom_components` folder exists in config directory
- Restart Home Assistant after installation
- Check logs for errors

### Sensors not updating / Сензорите не се обновяват
- Check your identifier is correct for ERM West system
- Verify internet connection
- Check Home Assistant logs for errors
- ERM West website may be temporarily down

### Device offline / Устройството е offline
- Integration needs internet access to `info.ermzapad.bg`
- Check firewall settings
- Verify Home Assistant can access external websites

## Support / Поддръжка

For issues and questions:
- GitHub Issues: https://github.com/reminchev/bulgarian-utility-outage-checker-integration/issues
- Home Assistant Community: https://community.home-assistant.io/

## Credits / Благодарности

Based on the original [Bulgarian Utility Outage Checker Add-on](https://github.com/reminchev/bulgarian_utility_outage_checker)

## License

MIT License - See LICENSE file for details
