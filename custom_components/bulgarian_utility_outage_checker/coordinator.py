"""Data update coordinator for Bulgarian Utility Outage Checker."""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
import logging

import aiohttp
import async_timeout
from bs4 import BeautifulSoup

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_CHECK_INTERVAL,
    CONF_IDENTIFIER,
    DEFAULT_CHECK_INTERVAL,
    DOMAIN,
    ERM_WEST_URL,
    OUTAGE_TYPE_BOTH,
    OUTAGE_TYPE_NONE,
    OUTAGE_TYPE_PLANNED,
    OUTAGE_TYPE_UNPLANNED,
)

_LOGGER = logging.getLogger(__name__)


class BulgarianUtilityOutageCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Bulgarian utility outage data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.identifier = entry.data[CONF_IDENTIFIER]
        self.entry = entry
        
        # Get check interval from options or data
        check_interval = entry.options.get(
            CONF_CHECK_INTERVAL,
            entry.data.get(CONF_CHECK_INTERVAL, DEFAULT_CHECK_INTERVAL)
        )
        
        self._check_interval = check_interval
        update_interval = timedelta(minutes=check_interval)
        
        _LOGGER.info(
            "Initializing coordinator for %s with update interval of %d minutes",
            self.identifier,
            check_interval,
        )

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{self.identifier}",
            update_interval=update_interval,
        )
    
    @property
    def check_interval(self) -> int:
        """Return the check interval in minutes."""
        return self._check_interval

    async def _async_update_data(self) -> dict:
        """Fetch data from ERM West website."""
        _LOGGER.debug(
            "Starting data update for %s (interval: %d min)",
            self.identifier,
            self._check_interval,
        )
        try:
            async with async_timeout.timeout(30):
                data = await self._fetch_outage_data()
                _LOGGER.info(
                    "Successfully updated data for %s: has_outage=%s",
                    self.identifier,
                    data.get("has_outage", "unknown"),
                )
                return data
        except asyncio.TimeoutError as err:
            _LOGGER.error("Timeout communicating with ERM West for %s: %s", self.identifier, err)
            raise UpdateFailed(f"Timeout communicating with ERM West: {err}") from err
        except Exception as err:
            _LOGGER.error("Error communicating with ERM West for %s: %s", self.identifier, err)
            raise UpdateFailed(f"Error communicating with ERM West: {err}") from err

    async def _fetch_outage_data(self) -> dict:
        """Fetch and parse outage data."""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        params = {
            "submit": "Търсене",
            "key": self.identifier,
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(
                ERM_WEST_URL, 
                params=params, 
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=20)
            ) as response:
                if response.status != 200:
                    raise UpdateFailed(f"HTTP error {response.status}")
                
                html = await response.text()
                return await self.hass.async_add_executor_job(
                    self._parse_html, html
                )

    def _parse_html(self, html: str) -> dict:
        """Parse HTML response."""
        soup = BeautifulSoup(html, "lxml")
        
        # По подразбиране предполагаме, че има проблем
        result = {
            "identifier": self.identifier,
            "timestamp": datetime.now().isoformat(),
            "has_outage": True,
            "outage_type": OUTAGE_TYPE_UNPLANNED,
            "details": [],
            "last_check": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        # Проверка за съобщение "няма регистрирано прекъсване"
        no_outage_messages = soup.find_all(
            string=lambda text: text and (
                "няма регистрирано" in text.lower() or
                "няма планирано" in text.lower() or
                "няма непланирано" in text.lower() or
                "не са регистрирани" in text.lower()
            )
        )
        
        if no_outage_messages:
            # Ако има съобщение "няма регистрирано", значи всичко е ОК
            result["has_outage"] = False
            result["outage_type"] = OUTAGE_TYPE_NONE
        else:
            # Ако няма такова съобщение, има авария
            # Определяме типа на аварията
            
            # Проверка за непланирани аварии
            unplanned_markers = soup.find_all(
                string=lambda text: text and "непланиран" in text.lower()
            )
            
            # Проверка за планирани аварии
            planned_markers = soup.find_all(
                string=lambda text: text and "планиран" in text.lower() and "непланиран" not in text.lower()
            )
            
            if unplanned_markers and planned_markers:
                result["outage_type"] = OUTAGE_TYPE_BOTH
            elif planned_markers:
                result["outage_type"] = OUTAGE_TYPE_PLANNED
            else:
                result["outage_type"] = OUTAGE_TYPE_UNPLANNED
            
            # Извличане на детайли за аварията
            tables = soup.find_all("table")
            for table in tables:
                rows = table.find_all("tr")
                for row in rows:
                    cells = row.find_all(["td", "th"])
                    if len(cells) > 0:
                        row_text = " ".join([cell.get_text(strip=True) for cell in cells])
                        if row_text and len(row_text) > 5:  # Игнорираме празни редове
                            result["details"].append(row_text)

        _LOGGER.debug(
            "Fetched data for %s: has_outage=%s, type=%s, no_outage_msg=%s",
            self.identifier,
            result["has_outage"],
            result["outage_type"],
            len(no_outage_messages) > 0,
        )

        return result
