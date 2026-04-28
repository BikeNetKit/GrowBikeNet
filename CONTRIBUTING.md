# Contributing to BikeNetKit

First off, thank you for considering contributing to BikeNetKit! ❤️ It's
people like you that make BikeNetKit such a great toolkit.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

This project and everyone participating in it is governed by our
[Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are
expected to uphold this code.

## How Can I Contribute?

All types of contributions are encouraged and valued. See this page for different ways to help and details about how this project handles them. Please make sure to read the relevant section before making your contribution. It will make it a lot easier for us maintainers and smooth out the experience for all involved. The community looks forward to your contributions. 🎉

> And if you like the project, but just don't have time to contribute, that's fine. There are other easy ways to support the project and show your appreciation, which we would also be very happy about:
>
> - Star the project
> - Post on social media about it
> - Refer this project in your project's `README`
> - Mention the project at local meetups and tell your friends/colleagues

### 🐛 Reporting Bugs

Before creating bug reports, please check existing issues to avoid
duplicates. When you create a bug report, include as many details as
possible using our [bug report template](ISSUE_TEMPLATE/bug_report.md).

### 💡 Suggesting Features

Feature requests are welcome! Please use our
[feature request template](ISSUE_TEMPLATE/feature_request.md).

### 📝 Improving Documentation

Documentation improvements are always welcome! This includes:

- Fixing typos
- Adding examples
- Clarifying confusing sections

### 🔧 Submitting Code

Look for issues labeled `good first issue` or `help wanted` for
great places to start.

## Development setup

### Prerequisites

- Git
- pre-commit
- pytest

### Getting Started

```
# 1. Fork the repository on GitHub

# 2. Clone your fork locally
git clone https://github.com/YOUR_USERNAME/[project-name].git
cd [project-name]

# 3. Add upstream remote
git remote add upstream https://github.com/BikeNetKit/[project-name].git

# 4. Create a branch for your changes
git checkout -b feature/your-feature-name
```

## Pull Request Process

### Before Submitting

1. **Update your branch** with the latest upstream changes:
   ```
   git fetch upstream
   git rebase upstream/main
   ```
2. **Update documentation** if you've changed APIs or added features.

### Submitting

1. Push your branch to your fork:

   ```
   git push origin feature/your-feature-name
   ```

2. Open a Pull Request against the `main` branch.

3. Fill out the [PR template](PULL_REQUEST_TEMPLATE.md) completely.

4. Wait for review. We aim to respond within 7 days.

### PR Checklist

- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have updated the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix/feature works
- [ ] New and existing tests pass locally

### Code Style

- Use prettier and ruff for formatting via pre-commit ([config](pre-commit-config.yaml) included)
- Write self-documenting code with meaningful variable names

### Testing

- All new features must include tests
- Tests should be deterministic (no flaky tests)
- Tests will run automatically on GitHub when a pull request is created, this is not meant to replace testing while in development. Do not use GitHub as a testing environment.

---

Thank you for contributing! 🎉
