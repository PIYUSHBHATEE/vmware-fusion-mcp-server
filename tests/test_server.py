"""Tests for the VMware Fusion MCP Server."""

import pytest
from unittest.mock import patch, AsyncMock
from vmware_fusion_mcp.server import (
    _list_vms_impl,
    _get_vm_info_impl,
    _power_vm_impl,
    _get_vm_power_state_impl,
    mcp,
)
from fastmcp import Client


@pytest.mark.asyncio
async def test_list_vms_tool():
    with patch("vmware_fusion_mcp.server.VMwareClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client.list_vms.return_value = [
            {"id": "vm1", "path": "/path/to/vm1"}
        ]
        result = await _list_vms_impl()
        assert "vms" in result
        assert result["vms"][0]["id"] == "vm1"


@pytest.mark.asyncio
async def test_get_vm_info_tool():
    with patch("vmware_fusion_mcp.server.VMwareClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client.get_vm_info.return_value = {"id": "vm1", "cpu": {}}
        result = await _get_vm_info_impl("vm1")
        assert result["id"] == "vm1"


@pytest.mark.asyncio
async def test_power_vm_tool():
    with patch("vmware_fusion_mcp.server.VMwareClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client.power_vm.return_value = {"status": "success"}
        result = await _power_vm_impl("vm1", "on")
        assert result["status"] == "success"


@pytest.mark.asyncio
async def test_get_vm_power_state_tool():
    with patch("vmware_fusion_mcp.server.VMwareClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client.get_vm_power_state.return_value = {"powerState": "on"}
        result = await _get_vm_power_state_impl("vm1")
        assert result["powerState"] == "on"


@pytest.mark.asyncio
async def test_fastmcp_client_tools():
    async with Client(mcp) as client:
        tools = await client.list_tools()
        tool_names = [t.name for t in tools]
        assert set(tool_names) >= {
            "list_vms",
            "get_vm_info",
            "power_vm",
            "get_vm_power_state",
        }
        # Test call_tool (mocked)
        with patch("vmware_fusion_mcp.server.VMwareClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client_cls.return_value.__aenter__.return_value = mock_client
            mock_client.list_vms.return_value = [{"id": "vm1"}]
            result = await client.call_tool("list_vms", {})
            assert "vms" in result.structured_content
