"""VMware Fusion MCP Server implementation."""

import asyncio
from typing import Any, Dict, Optional
from contextlib import asynccontextmanager

from mcp.server import Server
from mcp.types import (
    Tool,
    TextContent,
    CallToolResult,
    ListToolsResult,
)
from pydantic import BaseModel, Field

from .vmware_client import VMwareClient


class VMwareToolParams(BaseModel):
    """Base parameters for VMware tools."""

    pass


class ListVMsParams(VMwareToolParams):
    """Parameters for list_vms tool."""

    pass


class GetVMInfoParams(VMwareToolParams):
    """Parameters for get_vm_info tool."""

    vm_id: str = Field(description="The ID of the VM to get information about")


class PowerVMParams(VMwareToolParams):
    """Parameters for power_vm tool."""

    vm_id: str = Field(description="The ID of the VM to control")
    action: str = Field(
        description="Power action (on, off, suspend, pause, unpause, reset)"
    )


# Global VMware client instance
vmware_client: Optional[VMwareClient] = None


@asynccontextmanager
async def get_vmware_client():
    """Get or create VMware client instance."""
    global vmware_client
    if vmware_client is None:
        vmware_client = VMwareClient()
    async with vmware_client:
        yield vmware_client


# Create the MCP server
server: Server = Server("vmware-fusion-mcp", version="0.1.0")


@server.list_tools()
async def handle_list_tools() -> ListToolsResult:
    """List available VMware Fusion tools."""
    return ListToolsResult(
        tools=[
            Tool(
                name="list_vms",
                description="List all VMs in VMware Fusion",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            ),
            Tool(
                name="get_vm_info",
                description="Get detailed information about a specific VM",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "vm_id": {
                            "type": "string",
                            "description": "VM ID to get info about",
                        }
                    },
                    "required": ["vm_id"],
                },
            ),
            Tool(
                name="power_vm",
                description="Perform a power action on a VM",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "vm_id": {
                            "type": "string",
                            "description": "The ID of the VM to control",
                        },
                        "action": {
                            "type": "string",
                            "enum": [
                                "on",
                                "off",
                                "suspend",
                                "pause",
                                "unpause",
                                "reset",
                            ],
                            "description": "Power action to perform",
                        },
                    },
                    "required": ["vm_id", "action"],
                },
            ),
        ]
    )


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: Dict[str, Any]
) -> CallToolResult:
    """Handle tool calls."""
    try:
        if name == "list_vms":
            return await handle_list_vms()
        elif name == "get_vm_info":
            params = GetVMInfoParams(**arguments)
            return await handle_get_vm_info(params.vm_id)
        elif name == "power_vm":
            power_params = PowerVMParams(**arguments)
            return await handle_power_vm(
                power_params.vm_id, power_params.action
            )
        else:
            raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: {str(e)}")],
            isError=True,
        )


async def handle_list_vms() -> CallToolResult:
    """Handle list_vms tool call."""
    async with get_vmware_client() as client:
        vms = await client.list_vms()

        # Format the VM list as a readable table
        if not vms:
            content = "No VMs found in VMware Fusion."
        else:
            lines = ["VMware Fusion VMs:", "=" * 50]
            for vm in vms:
                vm_id = vm.get("id", "Unknown")
                vm_path = vm.get("path", "Unknown")
                lines.append(f"ID: {vm_id}")
                lines.append(f"Path: {vm_path}")
                lines.append("-" * 30)
            content = "\n".join(lines)

        return CallToolResult(
            content=[TextContent(type="text", text=content)],
            structuredContent={"vms": vms} if vms else {"vms": []},
        )


async def handle_get_vm_info(vm_id: str) -> CallToolResult:
    """Handle get_vm_info tool call."""
    async with get_vmware_client() as client:
        vm_info = await client.get_vm_info(vm_id)

        # Format VM information
        lines = [f"VM Information for ID: {vm_id}", "=" * 50]

        for key, value in vm_info.items():
            if isinstance(value, dict):
                lines.append(f"{key.title()}:")
                for sub_key, sub_value in value.items():
                    lines.append(f"  {sub_key}: {sub_value}")
            else:
                lines.append(f"{key.title()}: {value}")

        content = "\n".join(lines)

        return CallToolResult(
            content=[TextContent(type="text", text=content)],
            structuredContent=vm_info,
        )


async def handle_power_vm(vm_id: str, action: str) -> CallToolResult:
    """Handle power_vm tool call."""
    async with get_vmware_client() as client:
        result = await client.power_vm(vm_id, action)

        content = f"Successfully performed '{action}' action on VM {vm_id}"
        if result.get("status"):
            content += f" - Status: {result['status']}"

        return CallToolResult(
            content=[TextContent(type="text", text=content)],
            structuredContent=result,
        )


async def main():
    """Main entry point for the server."""
    # Run the server using stdio transport
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, write_stream, server.create_initialization_options()
        )


def cli_main():
    """CLI entry point that runs the async main function."""
    asyncio.run(main())


if __name__ == "__main__":
    cli_main()
