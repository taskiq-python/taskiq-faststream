# Development

After cloning the project, you'll need to set up the development environment. Here are the guidelines on how to do this.

## Virtual Environment with `venv`

Create a virtual environment in a directory using Python's `venv` module:

```bash
python -m venv venv
```

That will create a `./venv/` directory with Python binaries, allowing you to install packages in an isolated environment.

## Activate the Environment

Activate the new environment with:

```bash
source ./venv/bin/activate
```

Ensure you have the latest pip version in your virtual environment:

```bash
python -m pip install --upgrade pip
```

## Installing Dependencies

After activating the virtual environment as described above, run:

```bash
pip install -e ".[dev]"
```

This will install all the dependencies and your local project in your virtual environment.

### Using Your local Project

If you create a Python file that imports and uses **taskiq_faststream**, and run it with the Python from your local environment, it will use your local **taskiq_faststream** source code.

Whenever you update your local **taskiq_faststream** source code, it will automatically use the latest version when you run your Python file again. This is because it is installed with `-e`.

This way, you don't have to "install" your local version to be able to test every change.

## Running Tests

### Pytest

To run tests with your current FastStream application and Python environment, use:

```bash
pytest tests
# or
./scripts/test.sh
# with coverage output
./scripts/test-cov.sh
```
