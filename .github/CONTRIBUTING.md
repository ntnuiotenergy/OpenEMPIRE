# Contributing to OpenEMPIRE

Thank you for your interest in contributing to OpenEMPIRE! We value the contributions of our community members and are excited to welcome you aboard. Whether you're fixing a bug, adding a new feature, or improving documentation, your help is appreciated. OpenEMPIRE is a community-driven project, and it's people like you that help make it great.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Please read it before contributing to ensure a welcoming and inclusive environment for everyone.

## Getting Started

### Fork and Clone the Repository

1. Fork the OpenEMPIRE repository on GitHub.
2. Clone your fork locally:
   ```bash
   git clone https://github.com/ntnuiotenergy/OpenEMPIRE.git
   ```
3. Set up your local development environment. Make sure you have Python 3.8 or newer installed.

### Set Up Your Development Environment

1. Navigate to the OpenEMPIRE directory:
    ```bash
    cd OpenEMPIRE
    ```
2. Create a conda environment:
    ```bash
    conda env create -f environment.yml
    ```
3. Activate the conda environment:
    ```bash
    conda activate empire_env
    ```

## Making changes 

### Implementing your changes
1. Create a new branch for your work
    ```bash
    git checkout -b my-branch
    ```
    See [this](https://dev.to/varbsan/a-simplified-convention-for-naming-branches-and-commits-in-git-il4) reference for our preferred naming convention of branches, e.g feature/my-feature-branch

2. Make your changes. Remember to keep your code clean and follow the [PEP 8](https://peps.python.org/pep-0008/) style guide for Python code. 

3. Run linting and code formatting with [Ruff](https://docs.astral.sh/ruff/):
    ```bash
    ruff .
    ```
    We also recommend the Ruff extension for [VS Code](https://github.com/astral-sh/ruff-vscode).

4. Strive to write tests for your changes. We use pytest for testing, so add your tests to the tests/ directory.

5. Run test to ensure your changes don't break existing functionality:
    ```bash
    pytest
    ```

6. If this is your first time contributing, add your name and email (optional) to the list of [contributors](../docs/source/contributors.rst).

6. Commit your changes with a clear and descriptive commit message.

## Submitting a pull request

1. Push your changes to your fork:
    ```bash
    git push origin my-feature
    ```

2. Go to the OpenEMPIRE repository on GitHub and click "New pull request".

3. Select your branch and fill out the pull request template with information about your changes.

4. Wait for a review from the project maintainers. Be open to feedback and willing to make adjustments to your contribution.

## Coding standards
- Follow the [PEP 8](https://peps.python.org/pep-0008/) style guide for Python code.
- Write clear, readable code and include comments where necessary.
- Ensure your code is well-tested with pytest.
