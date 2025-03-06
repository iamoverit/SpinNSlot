# Contributing to SpinNSlot

Thank you for wanting to contribute to SpinNSlot! We appreciate your interest in helping us build a seamless time slot booking platform.

## Setting Up

### Prerequisites

- Docker installed on your system
- Python 3.8+
- PostgreSQL database (optional, but recommended)

### Fork the Repository

1. Fork this repository: https://github.com/iamoverit/SpinNSlot.git
2. Clone it to your local machine:
```bash
git clone git@github.com:yourusername/spinnslot.git
cd spinnslot
```

### Install Dependencies

Use Poetry for dependency management:

```bash
poetry install
```

This will also create a virtual environment in the `venv` directory.

## Development Workflow

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and test them locally:
   ```bash
   poetry run pytest src/web/tests.py  # Example test command
   ```

3. Commit your changes with a clear commit message following our [commit message guidelines](#commit-message-guidelines).

4. Push the branch to your forked repository.

5. Create a Pull Request from your feature branch to the main branch of this repository.

## Code Quality

- Follow PEP 8 style guidelines.
- Write clean, maintainable code.
- Add appropriate comments and documentation.
- Use type hints where possible.

### Linting & Testing

We use several tools to ensure code quality:

1. Run tests with:
   ```bash
   poetry run pytest --cov src/web/ -v
   ```

2. Check linting with flake8:
   ```bash
   poetry run flake8 src/
   ```

3. Check type hints with mypy:
   ```bash
   poetry run mypy src/
   ```

## Security Considerations

- Avoid hardcoding sensitive information.
- Use environment variables for configuration.
- Follow secure coding practices.

## Pull Request Process

1. All changes must be covered by tests.
2. Ensure your branch is up-to-date with the main branch before creating a PR.
3. Provide a clear description of what your changes do.
4. Include any relevant documentation updates.

### Commit Message Guidelines

Follow these conventions for commit messages:
- Use imperative mood (e.g., "add" instead of "added").
- Keep subject line under 72 characters.
- Capitalize the first letter of each sentence in the body.
- Separate type, scope, and subject with a slash (e.g., `feat/database: add new query optimization`).

Example:
```
feat/views: implement tournament details view
fix/models: correct customer model validation
docs/config: update environment variables documentation
```

## Reporting Issues

Please report any bugs or issues you encounter in the [Issues section](https://github.com/iamoverit/SpinNSlot/issues) of this repository.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

Thank you for your contribution!
