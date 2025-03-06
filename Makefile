# Thank you @Earthly https://www.youtube.com/watch?v=w2UeLF7EEwk
# Can be adapted to pipenv, and poetry
# Other languages coming soon especially R and Julia

# .ONESHELL tells make to run each recipe line in a single shell
.ONESHELL:

# .DEFAULT_GOAL tells make which target to run when no target is specified
.DEFAULT_GOAL := all

# Specify python location in virtual environment
# Specify pip location in virtual environment
PYTHON := .venv/bin/python3
PIP := .venv/bin/pip3
DOCKER_IMAGE_NAME := open-interp
DOCKER_IMAGE_VERSION := v0.0.0
DOCKER_IMAGE_TAG := $(DOCKER_IMAGE_NAME):$(DOCKER_IMAGE_VERSION)

#-----------------------------------------------------------------
# Package Manager Detection
#-----------------------------------------------------------------

# Detect available package managers
DETECT_PIPENV := $(shell which pipenv)
DETECT_POETRY := $(shell which poetry)
DETECT_UV     := $(shell which uv)

# Set flags (1: available, 0: not available)
ifeq ($(DETECT_PIPENV),)
  HAS_PIPENV := 0
else
  HAS_PIPENV := 1
endif

ifeq ($(DETECT_POETRY),)
  HAS_POETRY := 0
else
  HAS_POETRY := 1
endif

ifeq ($(DETECT_UV),)
  HAS_UV := 0
else
  HAS_UV := 1
endif

#-----------------------------------------------------------------
# Default Package Manager Selection (priority: uv > pipenv > poetry)
#-----------------------------------------------------------------

ifeq ($(HAS_UV),1)
  PACKAGE_MANAGER := uv
else ifeq ($(HAS_PIPENV),1)
  PACKAGE_MANAGER := pipenv
else ifeq ($(HAS_POETRY),1)
  PACKAGE_MANAGER := poetry
else
  $(error No supported package manager found (pipenv, poetry, or uv))
endif

#-----------------------------------------------------------------
# Set Commands Based on the Package Manager
#-----------------------------------------------------------------

ifeq ($(PACKAGE_MANAGER),pipenv)
  INSTALL_COMMAND := pipenv install --dev
  RUN_COMMAND     := pipenv run
else ifeq ($(PACKAGE_MANAGER),poetry)
  INSTALL_COMMAND := poetry install
  RUN_COMMAND     := poetry run
else ifeq ($(PACKAGE_MANAGER),uv)
  INSTALL_COMMAND := uv pip install -e . -r requirements-dev.txt
  RUN_COMMAND     := python  # or python3, depending on your setup
endif

detect:
    @echo "Pipenv detected: $(HAS_PIPENV)"
    @echo "Poetry detected: $(HAS_POETRY)"
    @echo "UV detected: $(HAS_UV)"
	@echo "Package manager selected: $(PACKAGE_MANAGER)"


venv/bin/activate: requirements.txt
	# create virtual environment
	python3 -m venv .venv
	# make command executable
	chmod +x .venv/bin/activate
	# activate virtual environment
	. .venv/bin/activate
  
activate:
	# activate virtual environment
	. .venv/bin/activate

install: venv/bin/activate requirements.txt # prerequisite
	# install commands
	$(PIP) --no-cache-dir install --upgrade pip &&\
		$(PIP) --no-cache-dir install -r requirements.txt
    
docstring: activate
	# format docstring
	pyment -w -o numpydoc *.py
  
format: activate 
	# format code
	black *.py #utils/*.py testing/*.py
  
clean:
	# clean directory of cache
	rm -rf __pycache__ &&\
	rm -rf utils/__pycache__ &&\
	rm -rf testing/__pycache__ &&\
	rm -rf .pytest_cache &&\
	rm -rf .venv
  
lint: activate install format
	# flake8 or #pylint
	pylint --disable=R,C --errors-only *.py #utils/*.py testing/*.py

setup_readme:  ## Create a README.md
	@if [ ! -f README.md ]; then \
		echo "# Project Name\n\
Description of the project.\n\n\
## Installation\n\
- Step 1\n\
- Step 2\n\n\
## Usage\n\
Explain how to use the project here.\n\n\
## Contributing\n\
Explain how to contribute to the project.\n\n\
## License\n\
License information." > README.md; \
		echo "README.md created."; \
	else \
		echo "README.md already exists."; \
	fi
  
test: activate install format
	# test
	$(PYTHON) -m pytest testing/test_input_validation.py
  
run: activate install format lint
	# run application
  	# example $(PYTHON) app.py
	$(PYTHON) test.py
	
review-code:
	@echo "#### General Code Review Prompt ####"
	@echo "1. Code Quality:"
	@echo "   - Architecture patterns"
	@echo "   - Design principles (SOLID, DRY, KISS)"
	@echo "   - Code complexity"
	@echo "   - Documentation quality"

	@echo "2. Reliability:"
	@echo "   - Single and multiple points of failure"
	@echo "   - Failover strategies"
	@echo "   - Resource management"
	@echo "   - Thread safety"

	@echo "3. Performance:"
	@echo "   - Algorithmic efficiency"
	@echo "   - Memory usage"
	@echo "   - I/O operations"
	@echo "   - Caching strategy"

review-ds:
	@echo "#### Data Science Review Prompt ####"
	@echo "1. Data Pipeline:"
	@echo "   - Data validation"
	@echo "   - Preprocessing steps"
	@echo "   - Feature engineering"
	@echo "   - Data versioning"

	@echo "2. Model Development:"
	@echo "   - Algorithm selection"
	@echo "   - Hyperparameter management"
	@echo "   - Cross-validation"
	@echo "   - Model persistence"

	@echo "3. Production Readiness:"
	@echo "   - Scalability"
	@echo "   - Monitoring setup"
	@echo "   - A/B testing capability"
	@echo "   - Model deployment pipeline"

docker_build: Dockerfile
	# build container
	#docker build -t plot-timeseries-app:v0 .
	# podman build -t plot-timeseries-app:v0 .
  
docker_run_test: Dockerfile
	# linting Dockerfile
	# podman run --rm -i hadolint/hadolint < Dockerfile
	docker run --rm -i hadolint/hadolint < Dockerfile
	
docker_clean: 
	# remove dangling images, containers, volumes and networks
	# podman system prune -a
	docker system prune -a
  
docker_run: Dockerfile docker_build
	# run docker
	# # podman run -e ENDPOINT_URL -e SECRET_KEY -e SPACES_ID -e SPACES_NAME plot-timeseries-app:v0
	# docker run -e ENDPOINT_URL -e SECRET_KEY -e SPACES_ID -e SPACES_NAME plot-timeseries-app:v0

docker_push: docker_build
  # push to registry
  # docker tag <my-image> registry.digitalocean.com/<my-registry>/<my-image>
  # docker push registry.digitalocean.com/<my-registry>/<my-image> 
  # podman tag <my-image> registry.digitalocean.com/<my-registry>/<my-image>
  # podman push registry.digitalocean.com/<my-registry>/<my-image> 
 
 help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@echo "  detect          Detect package managers"
	@echo "  activate        Activate virtual environment"
	@echo "  install         Install dependencies"
	@echo "  docstring       Format docstrings"
	@echo "  format          Format code"
	@echo "  clean           Clean directory of cache"
	@echo "  lint            Lint code"
	@echo "  test            Run tests"
	@echo "  run             Run application"
	@echo "  setup_readme    Create a README.md"
	@echo "  review-code     Code review prompt"
	@echo "  review-ds       Data Science review prompt"
	@echo "  docker-build    Build Docker image $(DOCKER_IMAGE_TAG)"
	@echo "  docker_run_test Lint Dockerfile"
	@echo "  docker_clean    Remove dangling images, containers, volumes, and networks"
	@echo "  docker_run      Run Docker container"
	@echo "  docker_push     Push Docker container to registry"
	@echo "  help            Show this help message"
 
# .PHONY tells make that these targets do not represent actual files
.PHONY: activate format clean lint test build run docker_build docker_run docker_push docker_clean docker_run_test
  
all: install format lint test run docker_build docker_run docker_push