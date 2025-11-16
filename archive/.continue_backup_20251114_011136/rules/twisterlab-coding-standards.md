---
globs: "**/*.py"
description: Python and FastAPI coding standards for TwisterLab development
alwaysApply: true
---

# TwisterLab Coding Standards

## Python Best Practices

### Type Hints (PEP 484)

- **Mandatory**: All functions, methods, and classes must have complete type hints
- Use `typing` module imports for complex types
- Example: `def execute(self, task: str, context: Dict[str, Any] = None) -> Any:`

### Docstrings

- **Required**: Google-style docstrings for all public functions and classes
- Include description, parameters, return types, and exceptions

```python
def execute_task(self, task_id: str) -> bool:
    """Execute a specific task by ID.

    Args:
        task_id: Unique identifier for the task

    Returns:
        True if execution successful, False otherwise

    Raises:
        TaskNotFoundError: If task_id doesn't exist
    """
```

### Async/Await Patterns

- **Preferred**: Use async functions for I/O operations and agent execution
- All agent `execute()` methods must be async
- Use `httpx` for async HTTP requests instead of `requests`

### Error Handling

- Use structured logging with `structlog` instead of print statements
- Catch specific exceptions, not bare `Exception`
- Log errors with context for debugging

## FastAPI Development

### API Structure

- Routes organized by domain in `agents/api/routes_*.py`
- Automatic OpenAPI docs available at `/docs`
- Use dependency injection for shared services

### Request/Response Models

- Define Pydantic models for all API inputs/outputs
- Use proper validation with field constraints
- Include example data in schema documentation

## Agent Development

### Agent Inheritance

- All agents must inherit from `TwisterAgent` in `agents/base.py`
- Implement required abstract methods
- Follow the standard constructor pattern with name, display_name, description, etc.

### Swarm Communication

- Use `SwarmMessenger` for inter-agent communication via Redis pub/pub
- Implement proper message serialization/deserialization
- Handle message timeouts and retries

## Testing Standards

### Test Coverage

- **Minimum 80% coverage** enforced
- Use `pytest` with shared fixtures in `tests/conftest.py`
- Write integration tests for end-to-end flows

### Test Organization

- Test files named `test_{component}.py`
- Use descriptive test names and docstrings
- Mock external services for unit tests

## Code Quality Tools

### Linting and Formatting

- **ruff**: Primary linter with fast performance
- **black**: Code formatting (line length 88)
- **mypy**: Static type checking

### Pre-commit Hooks

- All quality checks run automatically
- No commits allowed with failing checks

## Database Access

### Async SQLAlchemy

- Use async sessions from `agents/database/services.py`
- Implement business logic in service layer
- Avoid raw SQL in application code

### Connection Management

- Proper connection pooling
- Transaction management for data consistency
- Error handling for connection failures

## Logging Standards

### Structured Logging

- Use `structlog` for JSON-formatted logs
- Include relevant context in log messages
- Different log levels for different environments

### Log Levels

- `DEBUG`: Detailed debugging information
- `INFO`: General operational messages
- `WARNING`: Warning conditions
- `ERROR`: Error conditions
- `CRITICAL`: Critical errors requiring immediate attention

## Security Considerations

### Input Validation

- Validate all user inputs
- Sanitize data before processing
- Use parameterized queries for database operations

### Authentication/Authorization

- Implement proper auth mechanisms
- Use role-based access control where needed
- Secure sensitive configuration with environment variables

# TwisterLab Coding Standards

## Python Best Practices

### Type Hints (PEP 484)
- **Mandatory**: All functions, methods, and classes must have complete type hints
- Use `typing` module imports for complex types
- Example: `def execute(self, task: str, context: Dict[str, Any] = None) -> Any:`

### Docstrings
- **Required**: Google-style docstrings for all public functions and classes
- Include description, parameters, return types, and exceptions
- Example:
  ```python
  def execute_task(self, task_id: str) -> bool:
      """Execute a specific task by ID.

      Args:
          task_id: Unique identifier for the task

      Returns:
          True if execution successful, False otherwise

      Raises:
          TaskNotFoundError: If task_id doesn't exist
      """
  ```

### Async/Await Patterns
- **Preferred**: Use async functions for I/O operations and agent execution
- All agent `execute()` methods must be async
- Use `httpx` for async HTTP requests instead of `requests`

### Error Handling
- Use structured logging with `structlog` instead of print statements
- Catch specific exceptions, not bare `Exception`
- Log errors with context for debugging

## FastAPI Development

### API Structure
- Routes organized by domain in `agents/api/routes_*.py`
- Automatic OpenAPI docs available at `/docs`
- Use dependency injection for shared services

### Request/Response Models
- Define Pydantic models for all API inputs/outputs
- Use proper validation with field constraints
- Include example data in schema documentation

## Agent Development

### Agent Inheritance
- All agents must inherit from `TwisterAgent` in `agents/base.py`
- Implement required abstract methods
- Follow the standard constructor pattern with name, display_name, description, etc.

### Swarm Communication
- Use `SwarmMessenger` for inter-agent communication via Redis pub/sub
- Implement proper message serialization/deserialization
- Handle message timeouts and retries

## Testing Standards

### Test Coverage
- **Minimum 80% coverage** enforced
- Use `pytest` with shared fixtures in `tests/conftest.py`
- Write integration tests for end-to-end flows

### Test Organization
- Test files named `test_{component}.py`
- Use descriptive test names and docstrings
- Mock external services for unit tests

## Code Quality Tools

### Linting and Formatting
- **ruff**: Primary linter with fast performance
- **black**: Code formatting (line length 88)
- **mypy**: Static type checking

### Pre-commit Hooks
- All quality checks run automatically
- No commits allowed with failing checks

## Database Access

### Async SQLAlchemy
- Use async sessions from `agents/database/services.py`
- Implement business logic in service layer
- Avoid raw SQL in application code

### Connection Management
- Proper connection pooling
- Transaction management for data consistency
- Error handling for connection failures

## Logging Standards

### Structured Logging
- Use `structlog` for JSON-formatted logs
- Include relevant context in log messages
- Different log levels for different environments

### Log Levels
- `DEBUG`: Detailed debugging information
- `INFO`: General operational messages
- `WARNING`: Warning conditions
- `ERROR`: Error conditions
- `CRITICAL`: Critical errors requiring immediate attention

## Security Considerations

### Input Validation
- Validate all user inputs
- Sanitize data before processing
- Use parameterized queries for database operations

### Authentication/Authorization
- Implement proper auth mechanisms
- Use role-based access control where needed
- Secure sensitive configuration with environment variables
