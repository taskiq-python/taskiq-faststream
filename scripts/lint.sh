#!/bin/bash

echo "Running pyup_dirs..."
pyup_dirs --py38-plus --recursive taskiq_faststream tests

echo "Running ruff..."
ruff taskiq_faststream tests --fix

echo "Running black..."
black taskiq_faststream tests

echo "Running mypy..."
mypy taskiq_faststream
