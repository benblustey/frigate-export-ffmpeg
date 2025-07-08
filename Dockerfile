# --- Builder Stage (to cache dependencies if needed later) ---
FROM python:3.12-alpine AS builder

# Prevent interactive prompts
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# Install build deps (optional if wheels are prebuilt)
RUN apk add --no-cache gcc musl-dev libffi-dev

WORKDIR /app

# If you use a requirements.txt
COPY requirements.txt .

RUN pip install --prefix=/install -r requirements.txt

# --- Final Stage ---
FROM python:3.12-alpine

LABEL maintainer="admin@henhousesolutions.com" \
    version="1.1.0"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install only runtime deps
RUN apk add --no-cache libffi

# Copy Python deps from builder stage
COPY --from=builder /install /usr/local

WORKDIR /app

COPY . .

CMD ["python", "api_call_upload.py"]
