"""VMware Fusion REST API client."""

import httpx
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import base64


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
        # Prepare the Authorization header
        userpass = f"{self.username}:{self.password}"
        self._auth_header = {
            "Authorization": "Basic "
            + base64.b64encode(userpass.encode()).decode(),
            "Accept": "application/vnd.vmware.vmw.rest-v1+json",
        }

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
            response = await self._client.get(
                f"{self.base_url}/api/vms",
                headers=self._auth_header,
            )
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

    async def get_vm_info(
        self, vm_id: str, vm_password: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get detailed information about a specific VM.

        Args:
            vm_id: The ID of the VM
            vm_password: The password for the VM (if required)

        Returns:
            Dictionary with detailed VM information
        """
        try:
            url = f"{self.base_url}/api/vms/{vm_id}"
            params = {}
            if vm_password:
                params["vmPassword"] = vm_password
            response = await self._client.get(
                url,
                headers=self._auth_header,
                params=params or None,
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

    async def power_vm(
        self, vm_id: str, action: str, vm_password: Optional[str] = None
    ) -> Dict[str, Any]:
        """Perform a power action on a VM.

        Args:
            vm_id: The ID of the VM
            action: Power action (on, off, shutdown, suspend, pause, unpause)
            vm_password: The password for the VM (if required)

        Returns:
            Dictionary with the result of the power action
        """
        valid_actions = ["on", "off", "shutdown", "suspend", "pause", "unpause"]
        if action not in valid_actions:
            raise ValueError(
                f"Invalid action '{action}'. Valid actions: {valid_actions}"
            )

        try:
            url = f"{self.base_url}/api/vms/{vm_id}/power"
            params = {}
            if vm_password:
                params["vmPassword"] = vm_password
            headers = self._auth_header.copy()
            headers["Content-Type"] = "application/vnd.vmware.vmw.rest-v1+json"
            response = await self._client.put(
                url,
                headers=headers,
                params=params or None,
                content=action.encode(),
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

    async def get_vm_power_state(
        self, vm_id: str, vm_password: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get the power state of a specific VM.

        Args:
            vm_id: The ID of the VM
            vm_password: The password for the VM (if required)

        Returns:
            Dictionary with the VM's power state
        """
        try:
            url = f"{self.base_url}/api/vms/{vm_id}/power"
            params = {}
            if vm_password:
                params["vmPassword"] = vm_password
            response = await self._client.get(
                url,
                headers=self._auth_header,
                params=params or None,
            )
            response.raise_for_status()
            return response.json()  # type: ignore[no-any-return]
        except httpx.RequestError as e:
            raise Exception(f"Failed to connect to VMware Fusion API: {e}")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise Exception(f"VM with ID '{vm_id}' not found")
            raise Exception(
                f"VMware Fusion API error: {e.response.status_code} - "
                f"{e.response.text}"
            )
