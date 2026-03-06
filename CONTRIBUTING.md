# Contributing to Whisperbox

Thanks for your interest. Here's how to get started.

## Setup

```bash
git clone https://github.com/PeterTechDev/whisperbox.git
cd whisperbox

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -e ".[dev]"
```

Requires: Python 3.10+, FFmpeg, NVIDIA GPU (optional)

## Making Changes

```bash
# Create a branch
git checkout -b feat/your-feature

# Run linting
ruff check src/
black src/

# Run tests
pytest tests/ -v
```

## Pull Requests

- Keep PRs focused — one change per PR
- Add tests for new functionality when possible
- Follow existing code style (black + ruff)
- Update the README if you're adding a feature

## Reporting Bugs

Use the [bug report template](https://github.com/PeterTechDev/whisperbox/issues/new?template=bug_report.md). Include your OS, Python version, GPU info, and the full error output.

## Questions

Open a [GitHub Discussion](https://github.com/PeterTechDev/whisperbox/discussions) for questions and ideas.
