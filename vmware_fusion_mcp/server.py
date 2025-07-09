"""VMware Fusion MCP Server implementation."""

from fastmcp import FastMCP
from .vmware_client import VMwareClient
from typing import Dict, Any
import os

mcp: FastMCP = FastMCP("VMware Fusion MCP Server")

# Helper to get credentials from environment
VMREST_USER = os.environ.get("VMREST_USER", "")
VMREST_PASS = os.environ.get("VMREST_PASS", "")


async def _list_vms_impl() -> Dict[str, Any]:
    """List all VMs in VMware Fusion."""
    async with VMwareClient(username=VMREST_USER, password=VMREST_PASS) as client:
        vms = await client.list_vms()
        return {"vms": vms}  # type: ignore[no-any-return]


@mcp.tool
async def list_vms() -> Dict[str, Any]:
    """List all VMs in VMware Fusion."""
    return await _list_vms_impl()


async def _get_vm_info_impl(vm_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific VM."""
    async with VMwareClient(username=VMREST_USER, password=VMREST_PASS) as client:
        info = await client.get_vm_info(vm_id)
        return info  # type: ignore[no-any-return]


@mcp.tool
async def get_vm_info(vm_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific VM."""
    return await _get_vm_info_impl(vm_id)


async def _power_vm_impl(vm_id: str, action: str) -> Dict[str, Any]:
    """Perform a power action on a VM. Valid actions are 'on', 'off', 'shutdown', 'suspend', 'pause', 'unpause'."""
    async with VMwareClient(username=VMREST_USER, password=VMREST_PASS) as client:
        result = await client.power_vm(vm_id, action)
        return result  # type: ignore[no-any-return]


@mcp.tool
async def power_vm(vm_id: str, action: str) -> Dict[str, Any]:
    """Perform a power action on a VM. Valid actions are 'on', 'off', 'shutdown', 'suspend', 'pause', 'unpause'."""
    return await _power_vm_impl(vm_id, action)


async def _get_vm_power_state_impl(vm_id: str) -> Dict[str, Any]:
    """Get the power state of a specific VM."""
    async with VMwareClient(username=VMREST_USER, password=VMREST_PASS) as client:
        state = await client.get_vm_power_state(vm_id)
        return state  # type: ignore[no-any-return]


@mcp.tool
async def get_vm_power_state(vm_id: str) -> Dict[str, Any]:
    """Get the power state of a specific VM."""
    return await _get_vm_power_state_impl(vm_id)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
