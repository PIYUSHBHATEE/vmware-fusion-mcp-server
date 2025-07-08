.PHONY: env run test lint fmt clean help

# Default target
help:
	@echo "Available targets:"
	@echo "  env    - Create/activate virtual environment and install dependencies"
	@echo "  run    - Start the MCP server"
	@echo "  test   - Run unit tests"
	@echo "  lint   - Run flake8 linting"
	@echo "  fmt    - Format code with black"
	@echo "  clean  - Clean up temporary files and caches"
	@echo "  help   - Show this help message"

# Create virtual environment and install dependencies
env:
	@echo "Setting up environment with uv..."
	uv sync
	@echo "Environment ready! Activate with: source .venv/bin/activate"

# Start the MCP server
run:
	@echo "Starting VMware Fusion MCP Server..."
	uv run python -m vmware_fusion_mcp.server

# Run tests
test:
	@echo "Running tests..."
	uv run pytest tests/ -v

# Run linting
lint:
	@echo "Running flake8..."
	uv run flake8 vmware_fusion_mcp/ tests/
	@echo "Running mypy..."
	uv run mypy vmware_fusion_mcp/

# Format code
fmt:
	@echo "Formatting code with black..."
	uv run black vmware_fusion_mcp/ tests/

# Clean up
clean:
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleanup complete!"

# Install for development
dev: env
	@echo "Installing development dependencies..."
	uv sync --dev

# Run the server with debug output
debug:
	@echo "Starting VMware Fusion MCP Server in debug mode..."
	uv run python -m vmware_fusion_mcp.server --debug