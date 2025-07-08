"""Tests for the VMware Fusion MCP Server."""

import pytest
from unittest.mock import patch, AsyncMock

from vmware_fusion_mcp.server import (
    handle_list_vms,
    handle_get_vm_info,
    handle_power_vm,
    handle_list_tools,
    handle_call_tool,
)


@pytest.mark.asyncio
async def test_handle_list_tools():
    """Test that list_tools returns the expected tools."""
    result = await handle_list_tools()

    assert len(result.tools) == 3
    tool_names = [tool.name for tool in result.tools]
    assert "list_vms" in tool_names
    assert "get_vm_info" in tool_names
    assert "power_vm" in tool_names


@pytest.mark.asyncio
@patch("vmware_fusion_mcp.server.get_vmware_client")
async def test_handle_list_vms(mock_get_client, mock_vmware_client):
    """Test list_vms tool."""
    mock_get_client.return_value.__aenter__.return_value = mock_vmware_client

    result = await handle_list_vms()

    assert not result.isError
    assert "VMware Fusion VMs:" in result.content[0].text
    assert (
        result.structuredContent["vms"]
        == mock_vmware_client.list_vms.return_value
    )


@pytest.mark.asyncio
@patch("vmware_fusion_mcp.server.get_vmware_client")
async def test_handle_get_vm_info(mock_get_client, mock_vmware_client):
    """Test get_vm_info tool."""
    mock_get_client.return_value.__aenter__.return_value = mock_vmware_client

    result = await handle_get_vm_info("vm1")

    assert not result.isError
    assert "VM Information for ID: vm1" in result.content[0].text
    assert (
        result.structuredContent == mock_vmware_client.get_vm_info.return_value
    )


@pytest.mark.asyncio
@patch("vmware_fusion_mcp.server.get_vmware_client")
async def test_handle_power_vm(mock_get_client, mock_vmware_client):
    """Test power_vm tool."""
    mock_get_client.return_value.__aenter__.return_value = mock_vmware_client

    result = await handle_power_vm("vm1", "on")

    assert not result.isError
    assert (
        "Successfully performed 'on' action on VM vm1"
        in result.content[0].text
    )
    assert result.structuredContent == mock_vmware_client.power_vm.return_value


@pytest.mark.asyncio
async def test_handle_call_tool_list_vms():
    """Test call_tool with list_vms."""
    with patch("vmware_fusion_mcp.server.handle_list_vms") as mock_handle:
        mock_handle.return_value = AsyncMock()

        await handle_call_tool("list_vms", {})

        mock_handle.assert_called_once()


@pytest.mark.asyncio
async def test_handle_call_tool_get_vm_info():
    """Test call_tool with get_vm_info."""
    with patch("vmware_fusion_mcp.server.handle_get_vm_info") as mock_handle:
        mock_handle.return_value = AsyncMock()

        await handle_call_tool("get_vm_info", {"vm_id": "vm1"})

        mock_handle.assert_called_once_with("vm1")


@pytest.mark.asyncio
async def test_handle_call_tool_power_vm():
    """Test call_tool with power_vm."""
    with patch("vmware_fusion_mcp.server.handle_power_vm") as mock_handle:
        mock_handle.return_value = AsyncMock()

        await handle_call_tool("power_vm", {"vm_id": "vm1", "action": "on"})

        mock_handle.assert_called_once_with("vm1", "on")


@pytest.mark.asyncio
async def test_handle_call_tool_unknown():
    """Test call_tool with unknown tool."""
    result = await handle_call_tool("unknown_tool", {})

    assert result.isError
    assert "Unknown tool: unknown_tool" in result.content[0].text
