"""Constants for the Bulgarian Utility Outage Checker integration."""
from datetime import timedelta

DOMAIN = "bulgarian_utility_outage_checker"

# Configuration
CONF_IDENTIFIER = "identifier"
CONF_CHECK_INTERVAL = "check_interval"

# Defaults
DEFAULT_CHECK_INTERVAL = 60  # minutes
DEFAULT_NAME = "Bulgarian Utility Outage Checker"

# Update interval
UPDATE_INTERVAL = timedelta(minutes=DEFAULT_CHECK_INTERVAL)

# ERM West website
ERM_WEST_URL = "https://info.ermzapad.bg/webint/vok/avplan.php"

# Attributes
ATTR_IDENTIFIER = "identifier"
ATTR_OUTAGE_TYPE = "outage_type"
ATTR_HAS_OUTAGE = "has_outage"
ATTR_DETAILS = "details"
ATTR_LAST_CHECK = "last_check"
ATTR_TIMESTAMP = "timestamp"

# Outage types
OUTAGE_TYPE_PLANNED = "Планирана авария"
OUTAGE_TYPE_UNPLANNED = "Непланирана авария"
OUTAGE_TYPE_BOTH = "Планирана и непланирана авария"
OUTAGE_TYPE_NONE = "Няма текуща авария"
OUTAGE_TYPE_UNKNOWN = "Unknown"
