# GitHub Copilot Coding Agent Setup

This document describes the GitHub Copilot coding agent configuration for the Syntari repository.

## Overview

The Syntari repository is configured to work seamlessly with GitHub Copilot coding agent, following the best practices outlined in GitHub's documentation. This setup enables efficient AI-assisted development while maintaining code quality, security, and project conventions.

## Configuration Files

### 1. `copilot-instructions.md`

**Purpose**: Provides comprehensive context about the Syntari codebase to GitHub Copilot.

**Location**: `.github/copilot-instructions.md`

**Contents**:
- **Project Overview**: Description of Syntari as an AI-integrated, type-safe programming language
- **Technology Stack**: Python 3.8+, pytest, Black, flake8, mypy
- **Code Style Guidelines**: PEP 8 with 100-character lines, naming conventions, import organization
- **Project Structure**: Directory layout and component descriptions
- **Development Best Practices**: Testing requirements, code quality checks, security considerations
- **Syntari-Specific Details**: File extensions, key components, core modules
- **Common Patterns**: Error handling, AST nodes, visitor pattern
- **Helpful Commands**: Development, testing, building, running commands
- **Documentation Links**: References to key documentation files
- **Priority Areas**: Current development focuses
- **License Information**: Proprietary software notice

**Benefits**:
- More accurate and contextually relevant code suggestions
- Consistent coding style across AI-generated code
- Better understanding of Syntari-specific patterns and idioms
- Improved security awareness in generated code
- Faster onboarding for new contributors using Copilot

### 2. `copilot-setup-steps.yaml`

**Purpose**: Defines automated setup steps for the GitHub Copilot coding agent environment.

**Location**: `.github/copilot-setup-steps.yaml`

**Contents**:
- **Installation Steps**: Python dependencies, development tools
- **Verification Steps**: Module imports, test execution
- **Environment Variables**: PYTHONPATH configuration
- **Environment Metadata**: Python version, tools used
- **Notes**: Additional context for the agent

**Benefits**:
- Automated environment preparation in the agent's isolated workspace
- Consistent setup across all Copilot coding agent tasks
- Ensures dependencies are properly installed before work begins
- Validates environment is working before making changes

## How It Works

When a GitHub Copilot coding agent is assigned to work on an issue:

1. **Environment Setup**: The agent executes the steps defined in `copilot-setup-steps.yaml`
   - Installs Python dependencies via `pip install -e .`
   - Installs development tools (pytest, black, flake8, mypy)
   - Verifies core modules can be imported
   - Runs tests to ensure environment is working

2. **Context Loading**: The agent reads `copilot-instructions.md` to understand:
   - Project structure and conventions
   - Code style requirements
   - Testing and quality standards
   - Common patterns and best practices
   - Security considerations

3. **Task Execution**: The agent works on the assigned issue using:
   - The established coding patterns
   - Appropriate testing practices
   - Required code quality standards
   - Security best practices

4. **Quality Assurance**: The agent validates changes by:
   - Running tests (`pytest tests/`)
   - Formatting code (`black src/ tests/`)
   - Linting code (`flake8 src/ tests/`)
   - Ensuring changes follow project conventions

## Best Practices for Using Copilot Coding Agent

### Good Task Types
- ✅ Bug fixes with clear reproduction steps
- ✅ Test coverage improvements
- ✅ Small, well-defined features
- ✅ Documentation updates
- ✅ Code refactoring
- ✅ Technical debt reduction
- ✅ Configuration updates

### Task Definition Guidelines
- Be specific about the problem and acceptance criteria
- Reference specific files or components when possible
- Provide context about why the change is needed
- Include examples of expected behavior
- Link to relevant documentation or specifications

### Review Process
- Review all Copilot-generated PRs carefully
- Provide feedback via PR comments mentioning @copilot
- Verify that tests pass and coverage is maintained
- Check that code follows project conventions
- Ensure security considerations are addressed

## Maintenance

### Updating Instructions

When making significant changes to the codebase that affect conventions or patterns:

1. Update `copilot-instructions.md` to reflect the changes
2. Add new examples or patterns as they emerge
3. Update priority areas to reflect current development focus
4. Keep documentation links current

### Updating Setup Steps

When dependencies or setup process changes:

1. Update `copilot-setup-steps.yaml` with new steps
2. Test the setup in a clean environment
3. Ensure all required tools are included
4. Document any environment variables needed

## Verification

To verify the Copilot configuration is working:

1. **Check Files Exist**:
   ```bash
   ls -l .github/copilot-instructions.md
   ls -l .github/copilot-setup-steps.yaml
   ```

2. **Validate YAML Syntax**:
   ```bash
   python3 -c "import yaml; yaml.safe_load(open('.github/copilot-setup-steps.yaml'))"
   ```

3. **Test Setup Steps Manually**:
   ```bash
   pip install -e .
   pytest tests/ -v
   ```

4. **Verify Instructions Are Current**:
   - Read through `copilot-instructions.md`
   - Ensure all commands work as documented
   - Verify all documentation links are valid

## Resources

- [GitHub Copilot Best Practices](https://docs.github.com/en/copilot/tutorials/coding-agent/get-the-best-results)
- [Onboarding GitHub Copilot Coding Agent](https://github.blog/ai-and-ml/github-copilot/onboarding-your-ai-peer-programmer-setting-up-github-copilot-coding-agent-for-success/)
- [GitHub Copilot Coding Agent 101](https://github.blog/ai-and-ml/github-copilot/github-copilot-coding-agent-101-getting-started-with-agentic-workflows-on-github/)
- [Syntari Contributing Guide](../CONTRIBUTING.md)
- [Syntari Getting Started](../GETTING_STARTED.md)

## Support

For questions or issues with the Copilot configuration:
- Open an issue with the label `copilot-configuration`
- Contact the maintainers at legal@deuos.io

---

© 2025 DeuOS, LLC. All Rights Reserved.
