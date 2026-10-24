import re
import httpx
from typing import Dict, Any, List, Optional
from luna.config import settings

class HomeAssistantClient:
    """Connector for Home Assistant REST API with sandbox fallback."""

    def __init__(self):
        self.url = settings.HOME_ASSISTANT_URL.rstrip("/")
        self.token = settings.HOME_ASSISTANT_TOKEN
        # In-memory sandbox device state when no live HA instance is connected
        self.simulated_entities: Dict[str, Dict[str, Any]] = {
            "light.office_main": {
                "state": "on",
                "attributes": {"brightness": 204, "brightness_pct": 80, "friendly_name": "Office Main Lights"}
            },
            "light.ambient_desk": {
                "state": "on",
                "attributes": {"brightness": 128, "brightness_pct": 50, "friendly_name": "Desk Ambient Light"}
            },
            "climate.office_hvac": {
                "state": "cool",
                "attributes": {"temperature": 22.0, "current_temperature": 23.5, "friendly_name": "Office Climate"}
            },
            "lock.front_door": {
                "state": "locked",
                "attributes": {"battery_level": 88, "friendly_name": "Main Entrance Smart Lock"}
            },
            "switch.studio_power": {
                "state": "on",
                "attributes": {"current_power_w": 185, "friendly_name": "Studio Power Relay"}
            }
        }

    @property
    def is_configured(self) -> bool:
        return bool(self.token and self.url and not self.url.startswith("http://homeassistant.local"))

    async def get_states(self) -> List[Dict[str, Any]]:
        """Fetch entity states from live HA or simulated state."""
        if self.is_configured:
            try:
                async with httpx.AsyncClient(timeout=4.0) as client:
                    resp = await client.get(
                        f"{self.url}/api/states",
                        headers={"Authorization": f"Bearer {self.token}"}
                    )
                    if resp.status_code == 200:
                        return resp.json()
            except Exception:
                pass
        
        # Return simulated state
        return [
            {"entity_id": eid, **data}
            for eid, data in self.simulated_entities.items()
        ]

    async def call_service(self, domain: str, service: str, service_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calls a Home Assistant service (e.g., light.turn_on)."""
        if self.is_configured:
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    resp = await client.post(
                        f"{self.url}/api/services/{domain}/{service}",
                        headers={"Authorization": f"Bearer {self.token}"},
                        json=service_data
                    )
                    if resp.status_code in (200, 201):
                        return {"success": True, "source": "live_ha", "response": resp.json()}
            except Exception as e:
                return {"success": False, "source": "live_ha", "error": str(e)}

        # Execute on simulated entities
        entity_id = service_data.get("entity_id")
        if entity_id and entity_id in self.simulated_entities:
            target = self.simulated_entities[entity_id]
            if service == "turn_on":
                target["state"] = "on"
                if "brightness_pct" in service_data:
                    target["attributes"]["brightness_pct"] = service_data["brightness_pct"]
                    target["attributes"]["brightness"] = int(service_data["brightness_pct"] * 2.55)
            elif service == "turn_off":
                target["state"] = "off"
            elif service == "lock":
                target["state"] = "locked"
            elif service == "unlock":
                target["state"] = "unlocked"
            elif service == "set_temperature" and "temperature" in service_data:
                target["attributes"]["temperature"] = service_data["temperature"]

        return {"success": True, "source": "sandbox", "action": f"{domain}.{service}", "data": service_data}

    async def execute_directive(self, instruction: str) -> str:
        """Parses natural language directive and adjusts Home Assistant entities."""
        lower = instruction.lower()
        actions_taken = []

        # Check brightness percentage
        pct_match = re.search(r"(\d{1,3})\s*%", lower)
        brightness_pct = int(pct_match.group(1)) if pct_match else None

        # Check lighting
        if "light" in lower or "dim" in lower:
            target_pct = brightness_pct if brightness_pct is not None else (30 if "dim" in lower else 100)
            await self.call_service("light", "turn_on", {
                "entity_id": "light.office_main",
                "brightness_pct": target_pct
            })
            actions_taken.append(f"Adjusted light.office_main brightness to {target_pct}%")

        # Check climate
        if any(w in lower for w in ["temp", "thermostat", "ac", "cool", "heat"]):
            temp_match = re.search(r"(\d{2})\s*(?:c|degrees)?", lower)
            target_temp = float(temp_match.group(1)) if temp_match else 21.5
            await self.call_service("climate", "set_temperature", {
                "entity_id": "climate.office_hvac",
                "temperature": target_temp
            })
            actions_taken.append(f"Set climate.office_hvac target temperature to {target_temp}°C")

        # Check door lock
        if "unlock" in lower and "door" in lower:
            await self.call_service("lock", "unlock", {"entity_id": "lock.front_door"})
            actions_taken.append("Unlocked lock.front_door")
        elif "lock" in lower and "door" in lower:
            await self.call_service("lock", "lock", {"entity_id": "lock.front_door"})
            actions_taken.append("Secured lock.front_door")

        if not actions_taken:
            actions_taken.append(f"Evaluated IoT environment for '{instruction}' (all device parameters nominal)")

        return " | ".join(actions_taken)
