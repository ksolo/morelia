# Base image with Python and build tools
FROM python:3.11-slim AS base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    clang \
    llvm \
    lld \
    libclang-dev \
    clang-tools \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*


# Set working directory
WORKDIR /app

# Install uv for dependency management
RUN pip install --upgrade pip uv

# Install project dependencies
COPY . .
RUN uv sync

# Copy source code

# Default command
CMD ["python", "-m", "morelia"]
