"""VMware Fusion REST API client."""

import httpx
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class VMInfo:
    """VM information from Fusion API."""

    id: str
    path: str
    cpu: Dict[str, Any]
    memory: Dict[str, Any]


class VMwareClient:
    """Client for VMware Fusion REST API."""

    def __init__(
        self,
        base_url: str = "http://localhost:8697",
        username: str = "",
        password: str = "",
    ):
        """Initialize the VMware client.

        Args:
            base_url: Base URL for the Fusion REST API
            username: Username for authentication (if required)
            password: Password for authentication (if required)
        """
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self._client = httpx.AsyncClient()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._client.aclose()

    async def list_vms(self) -> List[Dict[str, Any]]:
        """List all VMs.

        Returns:
            List of VM dictionaries with basic information
        """
        try:
            response = await self._client.get(f"{self.base_url}/fusionsvc/vms")
            response.raise_for_status()
            result: List[Dict[str, Any]] = response.json()
            return result
        except httpx.RequestError as e:
            raise Exception(f"Failed to connect to VMware Fusion API: {e}")
        except httpx.HTTPStatusError as e:
            raise Exception(
                f"VMware Fusion API error: {e.response.status_code} - "
                f"{e.response.text}"
            )

    async def get_vm_info(self, vm_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific VM.

        Args:
            vm_id: The ID of the VM

        Returns:
            Dictionary with detailed VM information
        """
        try:
            response = await self._client.get(
                f"{self.base_url}/fusionsvc/vms/{vm_id}"
            )
            response.raise_for_status()
            result: Dict[str, Any] = response.json()
            return result
        except httpx.RequestError as e:
            raise Exception(f"Failed to connect to VMware Fusion API: {e}")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise Exception(f"VM with ID '{vm_id}' not found")
            raise Exception(
                f"VMware Fusion API error: {e.response.status_code} - "
                f"{e.response.text}"
            )

    async def power_vm(self, vm_id: str, action: str) -> Dict[str, Any]:
        """Perform a power action on a VM.

        Args:
            vm_id: The ID of the VM
            action: Power action (on, off, suspend, pause, unpause, reset)

        Returns:
            Dictionary with the result of the power action
        """
        valid_actions = ["on", "off", "suspend", "pause", "unpause", "reset"]
        if action not in valid_actions:
            raise ValueError(
                f"Invalid action '{action}'. Valid actions: {valid_actions}"
            )

        try:
            response = await self._client.post(
                f"{self.base_url}/fusionsvc/vms/{vm_id}/{action}"
            )
            response.raise_for_status()
            return (
                response.json()
                if response.content
                else {"status": "success", "action": action}
            )
        except httpx.RequestError as e:
            raise Exception(f"Failed to connect to VMware Fusion API: {e}")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise Exception(f"VM with ID '{vm_id}' not found")
            raise Exception(
                f"VMware Fusion API error: {e.response.status_code} - "
                f"{e.response.text}"
            )
