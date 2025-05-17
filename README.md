# CodevAI: Programming Assistant with AI Thinking

<div align="center">
  <img src="https://raw.githubusercontent.com/Bogdan11212/CodevAI/main/logo.png" alt="CodevAI Logo" width="250">
  
  <p>
    <strong>An AI-powered programming assistant that explains its thought process</strong>
  </p>
  
  <p>
    <a href="#features">Features</a> •
    <a href="#demo">Demo</a> •
    <a href="#api-documentation">API</a> •
    <a href="#installation">Installation</a> •
    <a href="#usage">Usage</a> •
    <a href="#architecture">Architecture</a> •
    <a href="#contributing">Contributing</a> •
    <a href="#license">License</a>
  </p>
  
  <p>
    <a href="https://github.com/Bogdan11212/CodevAI/blob/main/LICENSE">
      <img src="https://img.shields.io/github/license/Bogdan11212/CodevAI?style=flat-square" alt="License">
    </a>
    <a href="https://github.com/Bogdan11212/CodevAI/stargazers">
      <img src="https://img.shields.io/github/stars/Bogdan11212/CodevAI?style=flat-square" alt="Stars">
    </a>
    <a href="https://github.com/Bogdan11212/CodevAI/network/members">
      <img src="https://img.shields.io/github/forks/Bogdan11212/CodevAI?style=flat-square" alt="Forks">
    </a>
    <a href="https://github.com/Bogdan11212/CodevAI/issues">
      <img src="https://img.shields.io/github/issues/Bogdan11212/CodevAI?style=flat-square" alt="Issues">
    </a>
  </p>
</div>

## Introduction

CodevAI is a powerful programming assistant that not only generates code but also provides insights into its thinking process. It's designed to help developers understand the reasoning behind code suggestions, offering a more educational experience than traditional code completion tools.

The system leverages advanced AI models via Cloudflare AI Workers to provide intelligent assistance across multiple programming languages, with continuous learning capabilities that improve over time based on user feedback.

## Features

- **AI Thinking Process**: See how the AI approaches problems, reasons through solutions, and explains its thought process
- **Code Completion**: Get intelligent code suggestions across multiple programming languages
- **Error Detection**: Identify and fix errors with detailed correction suggestions
- **Interactive Editor**: Edit code with real-time AI assistance and syntax highlighting
- **Web Search Integration**: Search for programming solutions and incorporate examples
- **Continuous Learning**: System learns from feedback to improve suggestions over time
- **Language Support**: Python, JavaScript, Java, C++, and Go

## Demo

Visit our [live demo](https://codevai.example.com/demo) to experience CodevAI's capabilities without creating an account.

The demo showcases:
- AI thinking visualization
- Code completion
- Error detection
- Interactive coding

## API Documentation

CodevAI provides a RESTful API for integration into your development workflow.

### Base URL
```
https://api.codevai.example.com/v1
```

### Authentication
API requests require an API key passed in the header:
```
Authorization: Bearer your_api_key
```

### Key Endpoints

#### AI Thinking
```http
POST /ai-thinking
Content-Type: application/json

{
  "prompt": "Write a function to find the GCD of two numbers",
  "language": "python",
  "max_thoughts": 5
}
```

#### Code Completion
```http
POST /code-completion
Content-Type: application/json

{
  "code": "def fibonacci(n):",
  "language": "python",
  "max_tokens": 100
}
```

#### Error Checking
```http
POST /error-check
Content-Type: application/json

{
  "code": "def fibonacci(n):\n    if n <= 0:\n        return 0\n    elif n == 1\n        return 1\n    else:\n        return fibonacci(n-1) + fibonacci(n-2)",
  "language": "python"
}
```

#### Language Detection
```http
POST /detect-language
Content-Type: application/json

{
  "code": "function factorial(n) {\n  if (n === 0 || n === 1) {\n    return 1;\n  }\n  return n * factorial(n - 1);\n}"
}
```

#### Web Search
```http
POST /web-search
Content-Type: application/json

{
  "query": "Python recursive sorting",
  "language": "python"
}
```

#### Web Content
```http
POST /web-content
Content-Type: application/json

{
  "url": "https://example.com/python-tutorial"
}
```

## Installation

### Prerequisites
- Python 3.8+
- Flask
- SQLAlchemy
- Cloudflare API access (for AI Workers)

### Setup

1. Clone the repository
```bash
git clone https://github.com/Bogdan11212/CodevAI.git
cd CodevAI
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your Cloudflare credentials and other settings
```

4. Initialize the database
```bash
flask db init
flask db migrate
flask db upgrade
```

5. Start the server
```bash
flask run
```

## Usage

### Web Interface

Once installed, access the web interface at `http://localhost:5000` with the following sections:

- **Home**: Overview of CodevAI's capabilities
- **AI Thinking**: Visualize AI thought processes
- **Code Generator**: Generate code with continuous learning
- **Interactive Editor**: Code with real-time AI assistance
- **Demo**: Try all features without an account
- **Documentation**: Comprehensive API documentation

### Programmatic Usage

Using the Python client:

```python
from codevai import CodevAIClient

client = CodevAIClient(api_key="your_api_key")

# Get AI thinking for a coding problem
response = client.ai_thinking(
    prompt="Write a function to sort a list using quicksort", 
    language="python"
)

# Print the thought process and solution
for thought in response["thoughts"]:
    print(f"Thought: {thought}")
print(f"\nSolution:\n{response['solution']}")
```

## Architecture

CodevAI follows a modular architecture with several key components:

### Core Components

1. **Brain**
   - `ai_processor.py`: Main processing logic
   - `cloudflare_ai.py`: Integration with Cloudflare AI
   - `thinking_patterns.py`: Templates for AI thinking
   - `web_access.py`: Internet data access for learning

2. **API**
   - RESTful endpoints for different functionalities
   - Authentication and rate limiting
   - Request validation and processing

3. **Models**
   - Database models for storing examples, feedback, etc.
   - Versioning system for tracking AI improvements

4. **Web Interface**
   - Interactive demos
   - Documentation
   - Code editor with real-time suggestions

### Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLAlchemy with SQLite
- **AI Processing**: Cloudflare AI Workers
- **Frontend**: Bootstrap, Modern JS, Monaco Editor
- **Authentication**: Flask-Login

## Contributing

We welcome contributions from the community! See [CONTRIBUTING.md](https://github.com/Bogdan11212/CodevAI/blob/main/CONTRIBUTING.md) for guidelines.

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/Bogdan11212/CodevAI/blob/main/LICENSE) file for details.

## Acknowledgements

- [Cloudflare AI Workers](https://developers.cloudflare.com/workers-ai/) for providing the AI capabilities
- [Flask](https://flask.palletsprojects.com/) for the web framework
- All contributors who have helped shape this project

---

<div align="center">
  <p>Made with ❤️ by the CodevAI Team</p>
  <p>
    <a href="https://github.com/Bogdan11212">GitHub</a> •
    <a href="https://twitter.com/Bogdan11212">Twitter</a>
  </p>
</div>