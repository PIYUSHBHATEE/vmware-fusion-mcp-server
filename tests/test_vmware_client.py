"""Tests for the VMware client."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx
import os

from vmware_fusion_mcp.vmware_client import VMwareClient

# --------------------
# Mock-based unit tests
# --------------------


@pytest.mark.asyncio
async def test_vmware_client_init():
    """Test VMwareClient initialization."""
    client = VMwareClient("http://localhost:8697", "user", "pass")
    assert client.base_url == "http://localhost:8697"
    assert client.username == "user"
    assert client.password == "pass"


@pytest.mark.asyncio
async def test_vmware_client_list_vms_success():
    """Test successful list_vms call."""
    with patch(
        "vmware_fusion_mcp.vmware_client.httpx.AsyncClient"
    ) as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"id": "vm1", "path": "/path/to/vm1.vmx"}
        ]
        mock_response.raise_for_status.return_value = None
        mock_client.get.return_value = mock_response
        client = VMwareClient()
        async with client:
            result = await client.list_vms()
        assert result == [{"id": "vm1", "path": "/path/to/vm1.vmx"}]
        mock_client.get.assert_called_once_with(
            "http://localhost:8697/api/vms",
            headers=client._auth_header,
        )


@pytest.mark.asyncio
async def test_vmware_client_get_vm_info_success():
    """Test successful get_vm_info call."""
    with patch(
        "vmware_fusion_mcp.vmware_client.httpx.AsyncClient"
    ) as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": "vm1", "cpu": {"cores": 2}}
        mock_response.raise_for_status.return_value = None
        mock_client.get.return_value = mock_response
        client = VMwareClient()
        async with client:
            result = await client.get_vm_info("vm1")
        assert result == {"id": "vm1", "cpu": {"cores": 2}}
        mock_client.get.assert_called_once_with(
            "http://localhost:8697/api/vms/vm1",
            headers=client._auth_header,
            params=None,
        )


@pytest.mark.asyncio
async def test_vmware_client_power_vm_success():
    """Test successful power_vm call."""
    with patch(
        "vmware_fusion_mcp.vmware_client.httpx.AsyncClient"
    ) as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "success"}
        mock_response.content = b'{"status": "success"}'
        mock_response.raise_for_status.return_value = None
        mock_client.put.return_value = mock_response
        client = VMwareClient()
        async with client:
            result = await client.power_vm("vm1", "on")
        assert result == {"status": "success"}
        expected_headers = client._auth_header.copy()
        expected_headers["Content-Type"] = (
            "application/vnd.vmware.vmw.rest-v1+json"
        )
        mock_client.put.assert_called_once_with(
            "http://localhost:8697/api/vms/vm1/power",
            headers=expected_headers,
            params=None,
            content=b"on",
        )


@pytest.mark.asyncio
async def test_vmware_client_power_vm_invalid_action():
    """Test power_vm with invalid action."""
    client = VMwareClient()
    with pytest.raises(ValueError, match="Invalid action 'invalid'"):
        async with client:
            await client.power_vm("vm1", "invalid")


@pytest.mark.asyncio
async def test_vmware_client_get_vm_power_state_success():
    """Test successful get_vm_power_state call."""
    with patch(
        "vmware_fusion_mcp.vmware_client.httpx.AsyncClient"
    ) as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.json.return_value = {"powerState": "poweredOn"}
        mock_response.raise_for_status.return_value = None
        mock_client.get.return_value = mock_response
        client = VMwareClient()
        async with client:
            result = await client.get_vm_power_state("vm1")
        assert result == {"powerState": "poweredOn"}
        mock_client.get.assert_called_once_with(
            "http://localhost:8697/api/vms/vm1/power",
            headers=client._auth_header,
            params=None,
        )


@pytest.mark.asyncio
async def test_vmware_client_connection_error():
    """Test connection error handling."""
    with patch(
        "vmware_fusion_mcp.vmware_client.httpx.AsyncClient"
    ) as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_client.get.side_effect = httpx.RequestError("Connection failed")
        client = VMwareClient()
        with pytest.raises(
            Exception, match="Failed to connect to VMware Fusion API"
        ):
            async with client:
                await client.list_vms()


@pytest.mark.asyncio
async def test_vmware_client_http_error():
    """Test HTTP error handling."""
    with patch(
        "vmware_fusion_mcp.vmware_client.httpx.AsyncClient"
    ) as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_client.get.side_effect = httpx.HTTPStatusError(
            "Server error", request=MagicMock(), response=mock_response
        )
        client = VMwareClient()
        with pytest.raises(Exception, match="VMware Fusion API error: 500"):
            async with client:
                await client.list_vms()


# --------------------
# Integration tests
# --------------------

REAL_ENV_SKIP = not all(
    os.environ.get(k) for k in ["VMREST_USER", "VMREST_PASS"]
)


@pytest.mark.asyncio
@pytest.mark.skipif(
    REAL_ENV_SKIP,
    reason="VMREST_USER and VMREST_PASS must be set for real server tests.",
)
async def test_vmware_client_list_vms_real():
    """Integration: Test list_vms against real vmrest server."""
    url = os.environ.get("VMREST_URL", "http://localhost:8697")
    client = VMwareClient(
        url, os.environ["VMREST_USER"], os.environ["VMREST_PASS"]
    )
    async with client:
        vms = await client.list_vms()
    assert isinstance(vms, list)
    if vms:
        assert "id" in vms[0]


@pytest.mark.asyncio
@pytest.mark.skipif(
    REAL_ENV_SKIP,
    reason="VMREST_USER and VMREST_PASS must be set for real server tests.",
)
async def test_vmware_client_get_vm_info_real():
    """Integration: Test get_vm_info against real vmrest server."""
    url = os.environ.get("VMREST_URL", "http://localhost:8697")
    client = VMwareClient(
        url, os.environ["VMREST_USER"], os.environ["VMREST_PASS"]
    )
    async with client:
        vms = await client.list_vms()
        if not vms:
            pytest.skip("No VMs available on real server.")
        vm_id = vms[0]["id"]
        vm_password = os.environ.get("VMREST_VM_PASSWORD")
        try:
            info = await client.get_vm_info(vm_id, vm_password=vm_password)
        except Exception as e:
            msg = str(e)
            if (
                "please provide password" in msg.lower()
                or "encrypted" in msg.lower()
            ):
                pytest.skip(
                    "VM is encrypted and VMREST_VM_PASSWORD is not set or "
                    "incorrect."
                )
            raise
    assert isinstance(info, dict)
    assert info.get("id") == vm_id


@pytest.mark.asyncio
@pytest.mark.skipif(
    REAL_ENV_SKIP,
    reason="VMREST_USER and VMREST_PASS must be set for real server tests.",
)
async def test_vmware_client_power_vm_real():
    """Integration: Test power_vm (no-op) against real vmrest server."""
    url = os.environ.get("VMREST_URL", "http://localhost:8697")
    client = VMwareClient(
        url, os.environ["VMREST_USER"], os.environ["VMREST_PASS"]
    )
    async with client:
        vms = await client.list_vms()
        if not vms:
            pytest.skip("No VMs available on real server.")
        vm_id = vms[0]["id"]
        vm_password = os.environ.get("VMREST_VM_PASSWORD")
        try:
            result = await client.power_vm(
                vm_id, "pause", vm_password=vm_password
            )
        except Exception as e:
            msg = str(e)
            if (
                "please provide password" in msg.lower()
                or "encrypted" in msg.lower()
            ):
                pytest.skip(
                    "VM is encrypted and VMREST_VM_PASSWORD is not set or "
                    "incorrect."
                )
            raise
        assert isinstance(result, dict)


@pytest.mark.asyncio
@pytest.mark.skipif(
    REAL_ENV_SKIP,
    reason="VMREST_USER and VMREST_PASS must be set for real server tests.",
)
async def test_vmware_client_get_vm_power_state_real():
    """Integration: Test get_vm_power_state against real vmrest server."""
    url = os.environ.get("VMREST_URL", "http://localhost:8697")
    client = VMwareClient(
        url, os.environ["VMREST_USER"], os.environ["VMREST_PASS"]
    )
    async with client:
        vms = await client.list_vms()
        if not vms:
            pytest.skip("No VMs available on real server.")
        vm_id = vms[0]["id"]
        vm_password = os.environ.get("VMREST_VM_PASSWORD")
        try:
            state = await client.get_vm_power_state(
                vm_id, vm_password=vm_password
            )
        except Exception as e:
            msg = str(e)
            if (
                "please provide password" in msg.lower()
                or "encrypted" in msg.lower()
            ):
                pytest.skip(
                    "VM is encrypted and VMREST_VM_PASSWORD is not set or "
                    "incorrect."
                )
            raise
    assert isinstance(state, dict)
    # Accept both 'powerState' and 'power_state' keys for robustness
    assert any(k in state for k in ("powerState", "power_state"))
