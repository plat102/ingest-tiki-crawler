FROM python:3.12-slim

# Config Python env
# Send Python stdout&err to output
# Prevent generate bytecode file
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set workdir inside container
WORKDIR /app

# Install dependencies
RUN apt-get update  && apt-get install -y --no-install-recommends \
    gcc tini \
    && pip install poetry \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && poetry install --no-root --only main

# Copy the src \
COPY . .

# Run application (PID 1)
ENTRYPOINT ["/usr/bin/tini", "--"]
# Can pass arg
CMD ["python", "src/main.py"]
