# Multi-Agent Workflow Orchestration - Interview Task

A Python framework for orchestrating multi-step AI workflows with parallelization, state management, and error handling.

## Features

- **DAG-based workflow execution** with dependency resolution
- **Parallel step execution** for independent tasks
- **State management** with persistence and resumability
- **Error handling** with retry logic and exponential backoff
- **Progress tracking** with real-time updates
- **Mock LLM** for testing without API keys

## Quick Start

### Prerequisites

- Python 3.12+
- Poetry 2.2.1+

### Setup

```bash
# Install dependencies
poetry install

# Run example workflow
poetry run python examples/run_workflow.py

# Run tests
./test.sh

# Check types
./check_types.sh

# Lint code
./lint.sh
```

## Project Structure

```
src/
├── workflow/           # Core workflow engine
│   ├── workflow__types.py       # Type definitions
│   ├── workflow__executor.py   # Workflow orchestration
│   └── workflow__state.py      # State management
├── steps/             # Workflow step implementations
│   ├── step__base.py           # Base step class
│   ├── research__step.py       # Research step
│   ├── blog_post__step.py      # Blog post generation
│   └── ...
├── llm/               # LLM client and mocks
│   ├── llm__client.py          # LLM interface
│   └── llm__mock.py            # Mock LLM for testing
└── utils/             # Shared utilities
```

## Workflow Visualization

The example content generation workflow:

```
                    ┌─────────────┐
                    │  Research   │  (Step 1)
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  Blog Post  │  (Step 2)
                    └──────┬──────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
    ┌────▼────┐      ┌─────▼─────┐     ┌─────▼─────┐
    │LinkedIn │      │  Twitter  │     │   Email   │  (Steps 3-6, Parallel)
    └────┬────┘      └─────┬─────┘     └─────┬─────┘
         │                 │                 │
         │           ┌─────▼─────┐           │
         │           │   Meta    │           │
         │           └─────┬─────┘           │
         │                 │                 │
         └─────────────────┼─────────────────┘
                           │
                    ┌──────▼──────┐
                    │Quality Check│  (Step 7)
                    └──────┬──────┘
                           │
                    ┌──────▼───────┐
                    │Format/Publish│ (Step 8)
                    └──────────────┘
```

## Example Usage

```python
from src.workflow.workflow__executor import WorkflowExecutor
from src.workflow.workflow__state import InMemoryStateStore
from src.steps.research__step import ResearchStep
from src.steps.blog_post__step import BlogPostStep
from src.llm.llm__mock import MockLLMClient

# Create workflow steps
steps = [
    ResearchStep(name="research", llm_client=mock_llm),
    BlogPostStep(name="blog_post", depends_on=["research"], llm_client=mock_llm),
]

# Execute workflow
executor = WorkflowExecutor(state_store=InMemoryStateStore())
state = await executor.execute_workflow(
    workflow_id="content_gen_1",
    steps=steps,
    input_data={"topic": "AI in Healthcare"}
)
```

## Testing

```bash
# Run all tests
./test.sh

# Run specific test
poetry run pytest -vv src/workflow/workflow__executor__spec.py

# Run with coverage
poetry run pytest --cov=src --cov-report=html
```

## Code Quality

```bash
# Fix linting issues
./lint_fix.sh

# Check types
./check_types.sh

# Run pre-commit hooks
poetry run pre-commit run --all-files
```

## Interview Task

This repository is designed for a 1-hour interview task. Candidates should:

1. Review the existing architecture
2. Implement missing components
3. Discuss design decisions and tradeoffs
4. Demonstrate understanding of async patterns, error handling, and scalability

See the task description in the repository root for detailed requirements.
