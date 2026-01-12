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
    OUTAGE_TYPE_UNKNOWN,
)

_LOGGER = logging.getLogger(__name__)


class BulgarianUtilityOutageCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Bulgarian utility outage data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.identifier = entry.data[CONF_IDENTIFIER]
        
        # Get check interval from options or data
        check_interval = entry.options.get(
            CONF_CHECK_INTERVAL,
            entry.data.get(CONF_CHECK_INTERVAL, DEFAULT_CHECK_INTERVAL)
        )
        
        update_interval = timedelta(minutes=check_interval)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )

    async def _async_update_data(self) -> dict:
        """Fetch data from ERM West website."""
        try:
            async with async_timeout.timeout(30):
                return await self._fetch_outage_data()
        except asyncio.TimeoutError as err:
            raise UpdateFailed(f"Timeout communicating with ERM West: {err}") from err
        except Exception as err:
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
        
        result = {
            "identifier": self.identifier,
            "timestamp": datetime.now().isoformat(),
            "has_outage": False,
            "outage_type": OUTAGE_TYPE_NONE,
            "details": [],
            "last_check": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        # Check for unplanned outages (red markers)
        red_markers = soup.find_all(
            string=lambda text: text and "Непланирани прекъсвания" in text
        )
        if red_markers:
            result["has_outage"] = True
            result["outage_type"] = OUTAGE_TYPE_UNPLANNED

        # Check for planned outages (green markers)
        green_markers = soup.find_all(
            string=lambda text: text and "Планирани прекъсвания" in text
        )
        if green_markers:
            result["has_outage"] = True
            if result["outage_type"] != OUTAGE_TYPE_NONE:
                result["outage_type"] = OUTAGE_TYPE_BOTH
            else:
                result["outage_type"] = OUTAGE_TYPE_PLANNED

        # Extract outage details
        tables = soup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all(["td", "th"])
                if len(cells) > 0:
                    row_text = " ".join([cell.get_text(strip=True) for cell in cells])
                    if row_text and self.identifier.lower() in row_text.lower():
                        result["details"].append(row_text)

        # Check for "no results" message
        if not result["details"]:
            no_results = soup.find_all(
                string=lambda text: text and ("Няма" in text or "няма" in text)
            )
            if no_results:
                result["has_outage"] = False
                result["outage_type"] = OUTAGE_TYPE_NONE

        _LOGGER.debug(
            "Fetched data for %s: has_outage=%s, type=%s",
            self.identifier,
            result["has_outage"],
            result["outage_type"],
        )

        return result
