# Contributing to Travel App

Thank you for your interest in contributing to the Travel App! This document provides guidelines and instructions to help you get started.

## Setting Up the Project

1. **Clone the Repository:**
   - Clone the project to your local machine using Git:
     ```
     git clone https://github.com/DeepBlockDeepak/RoadTripPlanner.git
     ```

2. **Install Dependencies:**
   - We use Poetry for dependency management. After cloning, navigate to the project directory and run:
     ```
     poetry install --no-root
     ```
   - This will install the necessary dependencies for the project.

## Code Quality and Standards

1. **Ruff for Linting:**
   - We use Ruff to maintain code quality. To run Ruff on all Python files in the project, use:
     ```
     poetry run ruff check src/
     ```
   - To automatically fix linting issues in all files, use:
     ```
     poetry run ruff check --fix src/
     ```

2. **Pre-commit Hooks:**
   - Our project uses pre-commit hooks for automated checks before each commit.
   - Set up pre-commit hooks by running:
     ```
     pre-commit install
     ```

3. **GitHub Actions:**
   - Code pushed to the repository is automatically linted using GitHub Actions with Ruff.
   - Ensure that your code passes all checks before pushing or creating a pull request.

## Contributing Changes

1. **Creating a Branch:**
   - For new features or fixes, create a new branch:
     ```
     git checkout -b feature/your-feature-name
     ```

2. **Making Changes:**
   - Make your changes and commit them with clear, concise commit messages.
   - Use the following command to stage and commit your changes:
     ```
     git add .
     git commit -m "A brief description of the change"
     ```

3. **Pushing Changes:**
   - Push your changes to the repository:
     ```
     git push origin feature/your-feature-name
     ```

4. **Creating a Pull Request:**
   - Go to the repository on GitHub and create a pull request for your branch.
   - Provide a clear description of your changes and any relevant issue numbers.

## Final Notes

- Ensure that your code adheres to the project's coding standards and passes all checks.
- When adding new dependencies, update `pyproject.toml` using `poetry add <dependency>`.
- Use `poetry update` to update dependencies and `poetry lock --no-update` to regenerate the lock file without updating dependencies.

Thank you for contributing to the Travel App project!
