# Примерни Lovelace карти за Bulgarian Utility Outage Checker

## Цветна карта с бутон (Препоръчително!)

Тази карта показва статуса в цвят (червена при авария, зелена при OK) и има бутон за незабавна проверка.

```yaml
type: vertical-stack
cards:
  - type: entity
    entity: binary_sensor.bulgarian_utility_outage_checker_xxx_status
    name: Електрозахранване
    icon: mdi:transmission-tower
    state_color: true
  - type: button
    name: Провери сега
    icon: mdi:refresh
    tap_action:
      action: call-service
      service: bulgarian_utility_outage_checker.check_now
      service_data:
        entity_id: binary_sensor.bulgarian_utility_outage_checker_xxx_status
```

**Как да използвам:**
1. Замени `xxx` с твоя entry_id (виж в Developer Tools > States)
2. Копирай кода в Lovelace редактор
3. Натисни бутона "Провери сега" за незабавна проверка
4. Картата ще бъде:
   - 🔴 **Червена** с икона ⚠️ когато има авария ("Има авария")
   - 🟢 **Зелена** с икона ✓ когато всичко е OK ("ОК")

## Карта с детайли

```yaml
type: entities
title: 🔌 ЕРМ Запад - Детайли
entities:
  - entity: binary_sensor.bulgarian_utility_outage_checker_xxx_status
    name: Статус
    secondary_info: last-changed
  - type: attribute
    entity: binary_sensor.bulgarian_utility_outage_checker_xxx_status
    attribute: outage_type
    name: Тип на аварията
  - type: attribute
    entity: binary_sensor.bulgarian_utility_outage_checker_xxx_status
    attribute: last_check
    name: Последна проверка
  - type: button
    name: Провери сега
    icon: mdi:refresh
    tap_action:
      action: call-service
      service: bulgarian_utility_outage_checker.check_now
      service_data:
        entity_id: binary_sensor.bulgarian_utility_outage_checker_xxx_status
```

## Карта само за авария (показва се само при проблем)

```yaml
type: conditional
conditions:
  - condition: state
    entity: binary_sensor.bulgarian_utility_outage_checker_xxx_status
    state: 'on'
card:
  type: markdown
  content: |
    ## ⚠️ АВАРИЯ!
    
    **Тип:** {{ state_attr('binary_sensor.bulgarian_utility_outage_checker_xxx_status', 'outage_type') }}
    
    **Проверено:** {{ state_attr('binary_sensor.bulgarian_utility_outage_checker_xxx_status', 'last_check') }}
```

## Автоматизация за известяване

```yaml
automation:
  - alias: "Известие при авария на тока"
    trigger:
      - platform: state
        entity_id: binary_sensor.bulgarian_utility_outage_checker_xxx_status
        from: 'off'
        to: 'on'
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "⚠️ Авария на електрозахранването!"
          message: >
            Открита е {{ state_attr('binary_sensor.bulgarian_utility_outage_checker_xxx_status', 'outage_type') }}
```
