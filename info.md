# Bulgarian Utility Outage Checker Integration

Check for planned and unplanned utility outages in Bulgaria from ERM West directly in Home Assistant.

## Installation

1. Install via HACS (add custom repository)
2. Restart Home Assistant
3. Go to Settings → Devices & Services → Add Integration
4. Search for "Bulgarian Utility Outage Checker"
5. Enter your identifier (subscriber number, location, or street)

## Configuration

- **Identifier**: Your subscriber number, location (София, Перник), or street address
- **Check Interval**: How often to check for outages (1-1440 minutes, default 60)

## Entities Created

- **Sensor**: Shows current outage status
- **Binary Sensor**: ON when outage detected (for automations)

## Attributes

Both entities include:
- `outage_type`: Type of outage (Планирана/Непланирана авария)
- `last_check`: Last check timestamp
- `details`: List of outage details

Perfect for automations and notifications!
