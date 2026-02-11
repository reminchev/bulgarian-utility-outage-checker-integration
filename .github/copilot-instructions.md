# Bulgarian Utility Outage Checker - AI Coding Agent Instructions

## Architecture Overview

This is a **Home Assistant custom integration** that monitors utility outages in Bulgaria by scraping the ERM West website. The codebase follows Home Assistant's integration patterns with a coordinator-based data fetching architecture.

### Key Components

- **Coordinator** (`coordinator.py`): Central data fetcher using `DataUpdateCoordinator`. Scrapes `info.ermzapad.bg` with BeautifulSoup, manages update intervals (1-1440 minutes)
- **Sensors** (`sensor.py`): Three sensors - status, last check timestamp, next check timestamp (uses `last_update_success_time`)
- **Binary Sensor** (`binary_sensor.py`): Problem detection sensor with `device_class=PROBLEM`, returns `True` when outage detected
- **Config Flow** (`config_flow.py`): Two-step UI configuration (provider → identifier), creates unique_id from both
- **Custom Card** (`www/bulgarian-utility-outage-card.js`): Lovelace card with instant check button, auto-registers via `hass.http.register_static_path`
- **Service** (`__init__.py`): `check_now` service triggers `coordinator.async_request_refresh()`

### Data Flow

```
Web Scraping → HTML Parsing → Coordinator Data → Multiple Sensors Update
```

**Critical scraping logic** (INVERSE of typical - no message means outage exists):
```python
# If "няма регистрирано" message found → NO outage (OK)
# If message NOT found → OUTAGE detected
no_outage_messages = soup.find_all(string=lambda text: text and "няма регистрирано" in text.lower())
result["has_outage"] = not bool(no_outage_messages)  # Inverse logic!
```

## Conventions & Patterns

### Entity Naming
- **Always Bulgarian for entity names**: `_attr_name = "Статус"`, `"Последна проверка"`, `"Следваща проверка"`
- **English for unique_ids**: `f"{entry.entry_id}_status"`, `_outage`, `_last_check`, `_next_check`
- Entity IDs follow pattern: `sensor.bulgarian_utility_outage_checker_{entry_id}_{suffix}`

### Device Grouping
All entities share the same `DeviceInfo` to group under one device:
```python
DeviceInfo(
    identifiers={(DOMAIN, entry.entry_id)},
    name=f"Bulgarian Utility Outage Checker - {self._identifier}",
    manufacturer="ERM West",
    model="Outage Checker",
)
```

### Bilingual Support
- Translations in `translations/bg.json` and `en.json`
- Config flow uses translation keys with bilingual data field descriptions
- Documentation (README.md) uses dual language headers: `## Features / Възможности`

### Web Scraping Requirements
Always include User-Agent header to avoid blocking:
```python
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
params = {"submit": "Търсене", "key": self.identifier}
```

## Development Workflows

### Testing Changes
1. Copy `custom_components/bulgarian_utility_outage_checker/` to HA config
2. Restart Home Assistant
3. Check logs: `Settings → System → Logs` or `homeassistant.log`
4. Test service: Developer Tools → Services → `bulgarian_utility_outage_checker.check_now`

### Adding New Sensors
1. Create sensor class extending `CoordinatorEntity[BulgarianUtilityOutageCoordinator], SensorEntity`
2. Add to `async_add_entities()` list in platform's `async_setup_entry`
3. Use shared `DeviceInfo` for grouping
4. Access coordinator data via `self.coordinator.data.get("key")`

### Custom Card Development
- Card auto-registers at `/local/community/bulgarian_utility_outage_checker/`
- Static path registration in `__init__.py`: `hass.http.register_static_path()`
- Card definition: `customElements.define('bulgarian-utility-outage-card', BulgarianUtilityOutageCard)`
- Service call pattern: `hass.callService('bulgarian_utility_outage_checker', 'check_now', {entity_id: ...})`

## Critical Files

- **`coordinator.py`**: Core web scraping logic, inverse detection pattern (lines 120-145)
- **`const.py`**: All constants including URLs, attribute names, outage types
- **`__init__.py`**: Service registration, static file serving, entry setup
- **`manifest.json`**: Version, dependencies (beautifulsoup4>=4.12.0, lxml>=4.9.0)
- **`services.yaml`**: Service definitions with Bulgarian names/descriptions

## Common Pitfalls

1. **Inverse logic**: Empty search results mean outage EXISTS (not the opposite)
2. **Entry ID vs Identifier**: `entry.entry_id` (HA-generated UUID) ≠ `entry.data[CONF_IDENTIFIER]` (user input)
3. **Options vs Data**: Check interval in `entry.options` OR `entry.data` (options override)
4. **Async executor**: BeautifulSoup parsing runs in executor: `await hass.async_add_executor_job(self._parse_html, html)`
5. **Update listener**: Register `entry.add_update_listener(update_listener)` for options changes to trigger reload

## Integration Points

- **Home Assistant Core**: Uses standard coordinator, config_entries, sensor/binary_sensor platforms
- **External**: ERM West website (`https://info.ermzapad.bg/webint/vok/avplan.php`)
- **Frontend**: Custom Lovelace card requires `customElements.define()` and `window.customCards.push()`
- **HACS**: Installable via custom repository, uses `hacs.json` for metadata

## Version Management

Update three places when releasing:
1. `manifest.json` → `"version": "X.Y.Z"`
2. `README.md` → Version badges and changelog
3. Create GitHub release tag matching version

## Examples from Codebase

**Coordinator pattern with configurable interval:**
```python
check_interval = entry.options.get(CONF_CHECK_INTERVAL, entry.data.get(CONF_CHECK_INTERVAL, DEFAULT_CHECK_INTERVAL))
update_interval = timedelta(minutes=check_interval)
super().__init__(hass, _LOGGER, name=f"{DOMAIN}_{self.identifier}", update_interval=update_interval)
```

**Service registration with entity_id parameter:**
```python
SERVICE_CHECK_NOW_SCHEMA = vol.Schema({vol.Required("entity_id"): cv.entity_ids})
hass.services.async_register(DOMAIN, SERVICE_CHECK_NOW, async_check_now, schema=SERVICE_CHECK_NOW_SCHEMA)
```

**Next check sensor using timestamp device class:**
```python
_attr_device_class = "timestamp"
next_update = self.coordinator.last_update_success_time + timedelta(minutes=self.coordinator.check_interval)
return next_update.isoformat()  # Returns ISO 8601 format for timestamp sensors
```
