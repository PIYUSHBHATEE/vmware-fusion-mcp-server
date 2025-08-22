# Use Python 3.12 slim as base image for smaller size
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies directly with pip
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir fastmcp>=2.10.3 httpx>=0.28.1

# Copy source code
COPY vmware_fusion_mcp/ ./vmware_fusion_mcp/
COPY manifest.json ./

# Change ownership to appuser
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port (if needed for MCP communication)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["python", "-m", "vmware_fusion_mcp.server"]

# Labels for better maintainability
LABEL maintainer="Xiaodong Ye <yeahdongcn@gmail.com>" \
      version="0.1.5" \
      description="VMware Fusion MCP Server for managing VMs via REST API" \
      org.opencontainers.image.source="https://github.com/yeahdongcn/vmware-fusion-mcp-server"
