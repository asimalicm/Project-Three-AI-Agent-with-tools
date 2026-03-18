# Project Three: AI Agent with Tools (Function Calling)

An autonomous AI agent that can use tools to accomplish tasks using the **ReAct pattern** (Reason → Act → Observe → Repeat).

## 🎯 What This Project Demonstrates

1. **Function Calling / Tool Use** - AI can call Python functions to accomplish tasks
2. **ReAct Pattern Implementation** - The agent reasons, acts, observes, and repeats until task completion
3. **Multi-step Reasoning** - Handles complex queries requiring multiple tool calls
4. **Tool Schema Definitions** - Proper definition of tools for the AI to understand
5. **Agent Loop with Iteration Limits** - Safe execution with maximum iteration controls

## 🛠️ Available Tools

The agent has access to four tools:

- **🧮 Calculator** - Performs precise mathematical operations (add, subtract, multiply, divide, power, sqrt)
- **🌤️ Weather** - Gets current weather for cities (mocked data for learning)
- **🕐 Time** - Gets current date/time in any timezone
- **🔍 Search** - Searches the web for information (mocked data for learning)

## 📋 Prerequisites

- Python 3.8 or higher
- A Gemini API key (free tier available at [Google AI Studio](https://ai.google.dev/gemini-api/docs/api-key))

## 🚀 Setup Instructions

### 1. Create Virtual Environment

Due to the colon in the directory name, we need to create the venv in /tmp:

```bash
cd /tmp && python -m venv ai_agent_venv && cd - && ln -s /tmp/ai_agent_venv .venv
```

### 2. Activate Virtual Environment

```bash
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install python-dotenv google-genai
```

### 4. Set Up API Key

Create a `.env` file in the project root:

```bash
GEMINI_API_KEY=your_api_key_here
```

Get your free API key from: https://ai.google.dev/gemini-api/docs/api-key

## 🎮 Usage

### Interactive Mode

Run the agent in interactive CLI mode:

```bash
source .venv/bin/activate
python tool_agent.py
```

Then type your queries:
- `What's 234 * 56?`
- `What's the weather in Tokyo?`
- `What time is it?`
- `Search for information about Python`

### Commands

- `/tools` - List available tools
- `/reset` - Clear conversation history
- `/quit` - Exit the program

### Running Tests

Quick test:
```bash
source .venv/bin/activate
python test_agent.py
```

Comprehensive test suite:
```bash
source .venv/bin/activate
python test_comprehensive.py
```

## 🧠 How It Works

### The ReAct Pattern

1. **Reason** - The AI thinks about what action to take
2. **Act** - The AI decides to call a tool (or give a final answer)
3. **Observe** - We execute the tool and show the result to the AI
4. **Repeat** - Loop continues until the AI provides a final answer

### Key Architecture Concepts

#### 1. Tool Declarations

Tools are defined using `types.FunctionDeclaration` with:
- Name and description
- Parameter schema (types, required fields, descriptions)
- Constraints (e.g., enum values for specific operations)

#### 2. Agent Loop

The agent maintains:
- **Conversation history** (since AI is stateless)
- **Tool registry** (maps tool names to Python functions)
- **Iteration limit** (prevents infinite loops)

#### 3. Tool Execution

When AI wants to use a tool:
1. AI sends a `function_call` with tool name and arguments
2. We execute the actual Python function
3. We send the result back as `function_response`
4. AI processes the result and continues or gives final answer

## 📝 Example Interactions

### Single-Step Query
```
You: What's 234 * 56?

[Iteration 1/5]
🔧 Tool Call: calculator
📋 Arguments: {"operation": "multiply", "a": 234, "b": 56}
✅ Result: 13104

[Iteration 2/5]
💡 Final Answer: 234 multiplied by 56 is 13104.
```

### Multi-Step Query
```
You: What's the weather in Delhi and convert to Fahrenheit?

[Iteration 1/5]
🔧 Tool Call: get_weather
📋 Arguments: {"city": "Delhi", "unit": "fahrenheit"}
✅ Result: Weather in Delhi: 95°F, Hot and sunny, Humidity: 40%

[Iteration 2/5]
💡 Final Answer: The weather in Delhi is 95°F (35°C), hot and sunny with 40% humidity.
```

## 🎓 Learning Notes

### Why Function Calling?

AI models can make mistakes with:
- **Math** - Arithmetic errors are common
- **Current data** - Models only know training data
- **Actions** - Can't actually perform tasks (send emails, API calls, etc.)

Function calling lets AI use tools for these tasks reliably.

### Why Mock Data?

Real APIs (weather, search) require:
- API keys and authentication
- Rate limits and costs
- Network dependencies

Mock data lets us learn the core concepts without these complications.

### Why the ReAct Pattern?

The ReAct pattern provides:
- **Transparency** - We see what the AI is thinking and doing
- **Control** - We execute the tools, not the AI
- **Iterative problem solving** - AI can use tool results to make better decisions

## 🔧 Customization

### Adding New Tools

1. Create the Python function
2. Define the tool schema using `types.FunctionDeclaration`
3. Add to `all_tools` list
4. Register in `tool_functions` dictionary

### Changing the Model

Edit line 385 in `tool_agent.py`:
```python
model='gemini-2.5-flash',  # Change to any available model
```

Available models include:
- `gemini-2.5-flash` (recommended - faster, good for most tasks)
- `gemini-2.5-pro` (more capable, slower, higher cost)

## ⚠️ Rate Limits

Free tier limits (per minute):
- **gemini-2.5-flash**: 5 requests/minute
- **gemini-2.0-flash**: 0 requests/minute (exhausted more quickly)

If you hit rate limits, wait 10-15 seconds and try again.

## 📚 Further Reading

- [Google Gen AI Python SDK Documentation](https://github.com/googleapis/python-genai)
- [Gemini API Function Calling Guide](https://ai.google.dev/gemini-api/docs/function-calling)
- [ReAct Pattern Paper](https://arxiv.org/abs/2210.03629)

## 🐛 Troubleshooting

### "No module named 'dotenv'"
```bash
source .venv/bin/activate
pip install python-dotenv google-genai
```

### "No API key was provided"
Make sure your `.env` file exists with:
```
GEMINI_API_KEY=your_actual_key_here
```

### "429 RESOURCE_EXHAUSTED"
You've hit the rate limit. Wait 10-15 seconds and try again, or upgrade your API plan.

## 📄 License

This is a learning project - feel free to use and modify as needed!
