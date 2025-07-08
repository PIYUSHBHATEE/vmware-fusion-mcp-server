# VMware Fusion MCP Server

A Model Context Protocol (MCP) server for managing VMware Fusion virtual machines via the Fusion REST API.

## Overview

This MCP server provides tools to interact with VMware Fusion VMs through the built-in REST API service (`vmrest`). It implements three core MCP tools:

- `list_vms` - List all VMs in VMware Fusion
- `get_vm_info` - Get detailed information about a specific VM
- `power_vm` - Perform power actions on a VM (on, off, suspend, pause, unpause, reset)

## Prerequisites

- VMware Fusion Pro (with REST API support)
- Python 3.12 or later
- `uv` package manager (recommended) or `pip`

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yeahdongcn/vmware-fusion-mcp-server.git
cd vmware-fusion-mcp-server
```

2. Set up the environment and install dependencies:
```bash
make env
```

## VMware Fusion Setup

1. Enable the REST API in VMware Fusion Pro:
   - Go to VMware Fusion > Preferences > Advanced
   - Check "Enable REST API"
   - Note the API port (default: 8697)

2. Start the REST API service:
```bash
vmrest
```

The API will be available at `http://localhost:8697` by default.

## Usage

### As an MCP Server

Start the server:
```bash
make run
```

### Available Make Targets

- `make env` - Set up virtual environment and install dependencies
- `make run` - Start the MCP server
- `make test` - Run unit tests
- `make lint` - Run linting (flake8 + mypy)
- `make fmt` - Format code with black
- `make clean` - Clean up temporary files
- `make help` - Show available targets

### MCP Tools

#### list_vms
Lists all VMs in VMware Fusion.

**Parameters:** None

**Example response:**
```
VMware Fusion VMs:
==================================================
ID: vm1
Path: /path/to/vm1.vmx
------------------------------
ID: vm2
Path: /path/to/vm2.vmx
------------------------------
```

#### get_vm_info
Gets detailed information about a specific VM.

**Parameters:**
- `vm_id` (string): The ID of the VM

**Example:**
```json
{
  "vm_id": "vm1"
}
```

#### power_vm
Performs a power action on a VM.

**Parameters:**
- `vm_id` (string): The ID of the VM
- `action` (string): Power action - one of: "on", "off", "suspend", "pause", "unpause", "reset"

**Example:**
```json
{
  "vm_id": "vm1",
  "action": "on"
}
```

## Configuration

The server connects to VMware Fusion's REST API at `http://localhost:8697` by default. You can modify the connection settings in `vmware_fusion_mcp/vmware_client.py`.

## Development

### Running Tests

```bash
make test
```

### Code Formatting

```bash
make fmt
```

### Linting

```bash
make lint
```

## Architecture

- `vmware_fusion_mcp/server.py` - Main MCP server implementation
- `vmware_fusion_mcp/vmware_client.py` - VMware Fusion REST API client
- `tests/` - Unit tests

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting: `make test && make lint`
5. Submit a pull request