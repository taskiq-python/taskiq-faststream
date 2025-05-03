#!/bin/bash

echo "Running ruff..."
ruff check taskiq_faststream tests --fix

echo "Running ruff formatter..."
ruff format taskiq_faststream tests

echo "Running mypy..."
mypy taskiq_faststream
