"""Tests for the VMware client."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from vmware_fusion_mcp.vmware_client import VMwareClient


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
            "http://localhost:8697/fusionsvc/vms"
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
            "http://localhost:8697/fusionsvc/vms/vm1"
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
        mock_client.post.return_value = mock_response

        client = VMwareClient()
        async with client:
            result = await client.power_vm("vm1", "on")

        assert result == {"status": "success"}
        mock_client.post.assert_called_once_with(
            "http://localhost:8697/fusionsvc/vms/vm1/on"
        )


@pytest.mark.asyncio
async def test_vmware_client_power_vm_invalid_action():
    """Test power_vm with invalid action."""
    client = VMwareClient()

    with pytest.raises(ValueError, match="Invalid action 'invalid'"):
        async with client:
            await client.power_vm("vm1", "invalid")


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
