"""Test configuration for pytest."""

import pytest


@pytest.fixture
def mock_vmware_client():
    """Mock VMware client for testing."""
    from unittest.mock import AsyncMock

    client = AsyncMock()

    # Mock list_vms
    client.list_vms.return_value = [
        {"id": "vm1", "path": "/path/to/vm1.vmx"},
        {"id": "vm2", "path": "/path/to/vm2.vmx"},
    ]

    # Mock get_vm_info
    client.get_vm_info.return_value = {
        "id": "vm1",
        "path": "/path/to/vm1.vmx",
        "cpu": {"cores": 2, "threads": 4},
        "memory": {"size": "4GB"},
    }

    # Mock power_vm
    client.power_vm.return_value = {"status": "success", "action": "on"}

    return client
