# Contributing to CodevAI

Thank you for considering contributing to CodevAI! This document outlines the guidelines for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](https://github.com/Bogdan11212/CodevAI/blob/main/CODE_OF_CONDUCT.md).

## How Can I Contribute?

### Reporting Bugs

- Ensure the bug was not already reported by searching on GitHub under [Issues](https://github.com/Bogdan11212/CodevAI/issues)
- If you're unable to find an open issue addressing the problem, [open a new one](https://github.com/Bogdan11212/CodevAI/issues/new)
- Include a clear title and description
- Add as much relevant information as possible, including a code sample or an executable test case demonstrating the expected behavior

### Suggesting Enhancements

- Open a new issue with a clear title and detailed description
- Provide specific examples and explain why this enhancement would be useful
- Include any relevant screenshots or mockups if applicable

### Pull Requests

1. Fork the repository
2. Create a new branch: `git checkout -b feature/amazing-feature`
3. Make your changes and commit them with clear commit messages
4. Push to the branch: `git push origin feature/amazing-feature`
5. Submit a pull request

## Development Process

### Setting Up the Development Environment

1. Clone your fork of the repository
   ```bash
   git clone https://github.com/YourUsername/CodevAI.git
   cd CodevAI
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables
   ```bash
   cp .env.example .env
   # Edit .env with your Cloudflare credentials
   ```

4. Run the development server
   ```bash
   flask run
   ```

### Code Style

- Follow PEP 8 guidelines for Python code
- Use consistent indentation (4 spaces)
- Include docstrings for all functions, classes, and modules
- Write clear, readable code with descriptive variable names

### Testing

- Write tests for all new features or bug fixes
- Ensure all tests pass before submitting a pull request
- Run tests using the following command:
  ```bash
  pytest
  ```

## Documentation

Good documentation is essential for the success of the project. Please follow these guidelines:

- Update the README.md with details of changes to the interface
- Update the API documentation for any endpoint changes
- Document new features, especially in the brain/ and api/ directories
- Comment your code, especially complex algorithms or non-obvious behavior

## Review Process

- All submissions require review
- Maintainers will review your PR and may suggest changes
- Once approved, maintainers will merge your PR
- Be responsive to feedback and be prepared to make requested changes

## Acknowledgements

Your contributions are always welcome and appreciated. We will acknowledge all contributors in our README.md file.

Thank you for helping improve CodevAI!