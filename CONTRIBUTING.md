# Contributing to TwisterLab

Thank you for your interest in contributing to TwisterLab! We welcome contributions from the community.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Pull Request Process](#pull-request-process)
- [Reporting Issues](#reporting-issues)
- [Documentation](#documentation)

## 🤝 Code of Conduct

This project follows our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold this code.

## 🚀 Getting Started

1. **Fork** the repository on GitHub
2. **Clone** your fork locally
3. **Create** a feature branch
4. **Make** your changes
5. **Test** your changes
6. **Submit** a pull request

## 🛠️ Development Setup

### Prerequisites

- Python 3.8+
- Git
- Docker (optional, for full stack testing)

### Local Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/twisterlab.git
cd twisterlab

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/
```

### Docker Setup (Full Stack)

```bash
# Start all services
docker-compose up -d

# Run tests in container
docker-compose exec api pytest tests/

# View logs
docker-compose logs -f api
```

## 💡 How to Contribute

### Types of Contributions

- **🐛 Bug fixes**: Fix issues in the codebase
- **✨ Features**: Add new functionality
- **📚 Documentation**: Improve docs, guides, examples
- **🧪 Tests**: Add or improve test coverage
- **🔧 Tools**: Development tools, CI/CD improvements

### Contribution Guidelines

#### Code Style

- Follow [PEP 8](https://pep8.org/) style guidelines
- Use [Black](https://black.readthedocs.io/) for code formatting
- Use [isort](https://pycqa.github.io/isort/) for import sorting
- Add type hints where possible
- Write docstrings for all public functions/classes

#### Commit Messages

Use clear, descriptive commit messages:

```
feat: add TwisterLang compression algorithm
fix: resolve sync checksum validation bug
docs: update API reference for new endpoints
test: add integration tests for agent communication
```

#### Testing

- Write tests for all new features
- Ensure all tests pass before submitting PR
- Aim for >85% code coverage
- Test both unit and integration scenarios

## 🔄 Pull Request Process

1. **Create a branch** from `develop` (not `main`)
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the guidelines above

3. **Run the full test suite**
   ```bash
   pytest tests/ --cov=agents --cov=core --cov-report=html
   ```

4. **Update documentation** if needed

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: description of your changes"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Target branch: `develop`
   - Fill out the PR template
   - Request review from maintainers

8. **Address review feedback**
   - Make requested changes
   - Update tests if needed
   - Rebase if necessary

9. **Merge** (maintainers only)
   - Squash merge to keep history clean
   - Delete feature branch after merge

## 🐛 Reporting Issues

### Bug Reports

Use the [bug report template](https://github.com/youneselfakir0/twisterlab/issues/new?template=bug_report.md) and include:

- **Description**: Clear description of the issue
- **Steps to reproduce**: Step-by-step instructions
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Environment**: Python version, OS, etc.
- **Logs**: Error messages, stack traces
- **Screenshots**: If applicable

### Feature Requests

Use the [feature request template](https://github.com/youneselfakir0/twisterlab/issues/new?template=feature_request.md) and include:

- **Problem**: What problem are you trying to solve?
- **Solution**: Describe your proposed solution
- **Alternatives**: Any alternative solutions considered
- **Use case**: How would this feature be used?

## 📚 Documentation

### Building Docs

```bash
# Install docs dependencies
pip install mkdocs mkdocs-material

# Serve docs locally
mkdocs serve

# Build docs
mkdocs build
```

### Documentation Guidelines

- Write in clear, simple English
- Include code examples where helpful
- Keep screenshots up to date
- Test all instructions on a clean environment

## 🎯 Areas for Contribution

### High Priority

- [ ] **TwisterLang Protocol**: Extend vocabulary, improve compression
- [ ] **Agent Framework**: New agent types, improved coordination
- [ ] **Testing**: More comprehensive test coverage
- [ ] **Documentation**: Complete API docs, tutorials

### Medium Priority

- [ ] **Performance**: Optimize message processing, reduce latency
- [ ] **Security**: Additional validation, encryption options
- [ ] **Monitoring**: Better observability, alerting
- [ ] **UI/UX**: Improve OpenWebUI integration

### Future Ideas

- [ ] **Multi-language support**: Localized vocabularies
- [ ] **Plugin system**: Extensible agent capabilities
- [ ] **Cloud deployment**: Azure/AWS/GCP templates
- [ ] **Mobile app**: Companion mobile application

## 🙏 Recognition

Contributors will be:
- Listed in `CONTRIBUTORS.md`
- Mentioned in release notes
- Invited to join the core team (for significant contributions)

## 📞 Getting Help

- **Discussions**: [GitHub Discussions](https://github.com/youneselfakir0/twisterlab/discussions)
- **Issues**: [GitHub Issues](https://github.com/youneselfakir0/twisterlab/issues)
- **Email**: youneselfakir@outlook.com

Thank you for contributing to TwisterLab! 🚀