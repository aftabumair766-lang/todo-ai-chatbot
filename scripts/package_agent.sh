#!/bin/bash
# Package Agent for Reuse
# Creates a standalone Python package from your agent

set -e

echo "🎁 Packaging Todo Agent for Reuse..."
echo ""

# Configuration
PACKAGE_NAME="todo-agent"
VERSION="1.0.0"
AUTHOR="Your Name"
EMAIL="your.email@example.com"
DESCRIPTION="Reusable AI agent for natural language task management"

# Create package directory
PACKAGE_DIR="dist/$PACKAGE_NAME"
mkdir -p "$PACKAGE_DIR/todo_agent"

echo "📦 Copying agent files..."
cp backend/agents/base_agent.py "$PACKAGE_DIR/todo_agent/"
cp backend/agents/todo_agent.py "$PACKAGE_DIR/todo_agent/"
touch "$PACKAGE_DIR/todo_agent/__init__.py"

# Create setup.py
echo "📝 Creating setup.py..."
cat > "$PACKAGE_DIR/setup.py" << EOF
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="$PACKAGE_NAME",
    version="$VERSION",
    author="$AUTHOR",
    author_email="$EMAIL",
    description="$DESCRIPTION",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/$PACKAGE_NAME",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.11",
    install_requires=[
        "openai>=1.12.0",
        "sqlalchemy>=2.0.0",
        "pydantic>=2.5.0",
    ],
)
EOF

# Create README.md
echo "📖 Creating README.md..."
cat > "$PACKAGE_DIR/README.md" << 'EOF'
# Todo Agent - Reusable AI Agent

A production-ready AI agent for natural language task management, built with OpenAI GPT-4 and function calling.

## Features

- ✅ Natural language understanding
- 🔧 5 built-in task management tools
- 👋 Greeting detection
- 📝 Input validation
- 🎨 Emoji confirmations
- 🔒 Row-level security
- 🚀 100% stateless design

## Installation

```bash
pip install todo-agent
```

## Quick Start

```python
from todo_agent import run_todo_agent

# Use the agent
result = await run_todo_agent(
    user_id="user_123",
    message="Add a task to buy groceries",
    conversation_history=[],
    db=db_session
)

print(result["response"])  # "✅ Task added: Buy groceries"
```

## Generic Base Agent

For other domains, use the BaseAgent:

```python
from todo_agent.base_agent import BaseAgent

# Define your tools
tools = [...]

# Create agent
agent = BaseAgent(
    api_key="sk-...",
    tools=tools,
    tool_handlers={...}
)

# Use it
result = await agent.process_message(
    user_message="Your message",
    user_id="user_id",
    conversation_history=[],
    db=db
)
```

## Tools Included

1. **add_task** - Create new tasks
2. **list_tasks** - List tasks with filtering
3. **complete_task** - Mark tasks complete
4. **delete_task** - Delete tasks
5. **update_task** - Update task details

## Configuration

Set your OpenAI API key:

```bash
export OPENAI_API_KEY="sk-..."
```

## Examples

See [AGENT_USAGE_EXAMPLES.md](docs/AGENT_USAGE_EXAMPLES.md) for:
- E-commerce agent
- Calendar agent
- Support ticket agent
- Healthcare agent

## License

MIT License
EOF

# Create __init__.py
cat > "$PACKAGE_DIR/todo_agent/__init__.py" << 'EOF'
"""
Todo Agent - Reusable AI Agent for Task Management

Usage:
    from todo_agent import run_todo_agent
    from todo_agent.base_agent import BaseAgent
"""

from todo_agent.todo_agent import run_todo_agent
from todo_agent.base_agent import BaseAgent

__version__ = "1.0.0"
__all__ = ["run_todo_agent", "BaseAgent"]
EOF

# Create MANIFEST.in
cat > "$PACKAGE_DIR/MANIFEST.in" << 'EOF'
include README.md
include LICENSE
EOF

# Create LICENSE
cat > "$PACKAGE_DIR/LICENSE" << 'EOF'
MIT License

Copyright (c) 2025 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF

echo "✅ Package created at: $PACKAGE_DIR"
echo ""
echo "📋 Next steps:"
echo "   1. cd $PACKAGE_DIR"
echo "   2. Edit setup.py with your details"
echo "   3. python setup.py sdist bdist_wheel"
echo "   4. pip install twine"
echo "   5. twine upload dist/*"
echo ""
echo "🎉 Your agent is ready to share!"
