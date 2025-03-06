# Docker Setup for Open Interpreter with Ollama

This setup provides a containerized environment for running Open Interpreter with Ollama as the local LLM backend.

## Usage with Docker

1. Build and start the services:
```bash
docker-compose up -d
```

2. Attach to the interpreter container:
```bash
docker-compose exec interpreter bash
```

3. Use interpreter with mounted files:
```bash
interpreter --local
```

## Usage with Podman
1. Build and start the services:
```bash
podman-compose up -d
```

2. Attach to the interpreter container:
```bash
podman-compose exec interpreter bash
```

3. Use interpreter with mounted files:
```bash
interpreter --local
```

## Configuration

- Ollama service runs on port 11434
- Files in the current directory are mounted to `/files` in the interpreter container
- Ollama models are persisted in a named volume

## Models

The default model is `qwen2.5-coder:0.5b`. To use a different model, modify the MODEL environment variable in Dockerfile.ollama.

## Code Review Assistant

This container includes a code review assistant that provides feedback on code quality, architecture, and data engineering practices.

### Features

- Analyzes code for best practices and improvement suggestions
- Identifies architectural issues and performance concerns
- Evaluates data engineering and ML/AI implementations
- Saves reviews as markdown files for future reference

### Usage

Run the code review assistant with:

```bash
# From within the container
python /app/test.py -f /files/your_code_file.py

# Or review code from clipboard (when running on a host with GUI support)
python /app/test.py
```

### Requirements

- Requires only 531MB of VRAM when using small models like Qwen2.5-coder:0.5b
- Can also run entirely on CPU
- All dependencies are pre-installed in the Docker image
