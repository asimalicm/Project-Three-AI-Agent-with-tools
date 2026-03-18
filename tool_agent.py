"""
PROJECT 3: AI Agent with Tools (Function Calling)

This agent can autonomously use tools to accomplish tasks using the ReAct pattern:
- Reason: Think about what to do
- Act: Call a tool
- Observe: See the result
- Repeat until the task is complete

Key concepts demonstrated:
1. Function calling / tool use
2. ReAct pattern implementation
3. Multi-step reasoning
4. Tool schema definitions
5. Agent loop with iteration limits
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

# ============================================================================
# TOOL IMPLEMENTATIONS
# ============================================================================
# These are the actual Python functions that do the work.
# The AI doesn't execute these - it just tells us WHICH one to run and with WHAT parameters.

def calculator(operation: str, a: float, b: float = None) -> str:
    """
    Performs mathematical calculations
    
    Why this exists: AI models can make arithmetic errors. A calculator tool
    ensures 100% accurate math.
    
    Args:
        operation: One of "add", "subtract", "multiply", "divide", "power", "sqrt"
        a: First number (or only number for sqrt)
        b: Second number (not needed for sqrt)
    
    Returns:
        String with the calculation result
    """
    try:
        if operation == "add":
            result = a + b
        elif operation == "subtract":
            result = a - b
        elif operation == "multiply":
            result = a * b
        elif operation == "divide":
            if b == 0:
                return "Error: Cannot divide by zero"
            result = a / b
        elif operation == "power":
            result = a ** b
        elif operation == "sqrt":
            if a < 0:
                return "Error: Cannot take square root of negative number"
            result = a ** 0.5
        else:
            return f"Error: Unknown operation '{operation}'"
        
        return f"{result}"
    
    except Exception as e:
        return f"Error in calculation: {str(e)}"


def get_weather(city: str, unit: str = "celsius") -> str:
    """
    Get current weather for a city (mocked with hardcoded data)
    
    Why mocked: Real weather APIs cost money or have rate limits.
    For learning, mock data works perfectly.
    
    Args:
        city: Name of the city (e.g., "London", "Tokyo")
        unit: "celsius" or "fahrenheit"
    
    Returns:
        Weather information as formatted string
    """
    # Mock weather database
    MOCK_WEATHER = {
        "london": {"temp": 15, "condition": "Rainy", "humidity": 80},
        "tokyo": {"temp": 22, "condition": "Sunny", "humidity": 60},
        "new york": {"temp": 18, "condition": "Cloudy", "humidity": 65},
        "paris": {"temp": 20, "condition": "Partly cloudy", "humidity": 55},
        "sydney": {"temp": 25, "condition": "Sunny", "humidity": 50},
        "delhi": {"temp": 35, "condition": "Hot and sunny", "humidity": 40},
        "mumbai": {"temp": 30, "condition": "Humid", "humidity": 85},
        "bangalore": {"temp": 24, "condition": "Pleasant", "humidity": 60},
        "kolkata": {"temp": 32, "condition": "Hot", "humidity": 70},
    }
    
    city_lower = city.lower()
    
    if city_lower not in MOCK_WEATHER:
        return f"Error: Weather data not available for '{city}'"
    
    weather = MOCK_WEATHER[city_lower]
    temp = weather["temp"]
    
    # Convert to Fahrenheit if requested
    if unit.lower() == "fahrenheit":
        temp = (temp * 9/5) + 32
        unit_symbol = "°F"
    else:
        unit_symbol = "°C"
    
    return f"Weather in {city.title()}: {temp}{unit_symbol}, {weather['condition']}, Humidity: {weather['humidity']}%"


def get_current_time(timezone: str = "UTC") -> str:
    """
    Get current date and time in specified timezone
    
    Note: For simplicity, this just returns UTC time with the timezone label.
    In production, you'd use pytz for real timezone conversion.
    
    Args:
        timezone: Timezone string (e.g., "UTC", "America/New_York", "Asia/Tokyo")
    
    Returns:
        Current time formatted as string
    """
    now = datetime.utcnow()
    
    # Format: "2024-03-17 14:30:45 UTC"
    formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
    
    return f"Current time in {timezone}: {formatted_time}"


def web_search(query: str) -> str:
    """
    Search the web for information (mocked with hardcoded responses)
    
    Why mocked: Real search APIs (Google, Bing) require API keys and cost money.
    For learning, mock responses demonstrate the concept.
    
    Args:
        query: Search query string
    
    Returns:
        Mock search results as string
    """
    # Mock search database
    MOCK_SEARCHES = {
        "python": "Python is a high-level, interpreted programming language known for its readability and versatility. Created by Guido van Rossum in 1991, it's widely used in web development, data science, AI, and automation.",
        "ai": "Artificial Intelligence (AI) refers to machine intelligence that can perform tasks requiring human-like cognition, including learning, reasoning, and problem-solving. Modern AI uses techniques like machine learning and neural networks.",
        "weather": "Weather information varies by location. Use the weather tool for specific city weather data.",
        "gemini": "Gemini is Google's family of large language models, designed for multimodal understanding and generation. It can process text, images, and other data types.",
        "javascript": "JavaScript is a high-level programming language primarily used for web development. It enables interactive web pages and is an essential part of web applications.",
        "react": "React is a popular JavaScript library for building user interfaces, maintained by Meta (Facebook). It uses a component-based architecture and virtual DOM for efficient rendering.",
        "machine learning": "Machine learning is a subset of AI that enables systems to learn and improve from experience without explicit programming. It uses algorithms to identify patterns in data.",
        "blockchain": "Blockchain is a distributed ledger technology that maintains a secure, decentralized record of transactions. It's the foundation of cryptocurrencies like Bitcoin.",
    }
    
    query_lower = query.lower()
    
    # Check if we have a direct match
    for key, value in MOCK_SEARCHES.items():
        if key in query_lower:
            return f"Search results for '{query}':\n{value}"
    
    # Default response if no match
    return f"Search results for '{query}':\nNo specific information found in mock database. In a real implementation, this would search the web using APIs like Google Search or Bing."


# ============================================================================
# TOOL SCHEMA DEFINITIONS
# ============================================================================
# These describe the tools to the AI so it knows WHEN and HOW to use them.

# Calculator Tool Schema
calculator_declaration = types.FunctionDeclaration(
    name="calculator",
    description="Performs precise mathematical calculations. Use this when the user asks math questions or needs numerical computation. Supports: add, subtract, multiply, divide, power (a^b), and sqrt (square root of a).",
    parameters={
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "enum": ["add", "subtract", "multiply", "divide", "power", "sqrt"],
                "description": "The mathematical operation to perform"
            },
            "a": {
                "type": "number",
                "description": "First number (or the only number for sqrt operation)"
            },
            "b": {
                "type": "number",
                "description": "Second number (not required for sqrt)"
            }
        },
        "required": ["operation", "a"]
    }
)

# Weather Tool Schema
weather_declaration = types.FunctionDeclaration(
    name="get_weather",
    description="Get current weather information for a city. Use this when user asks about weather, temperature, conditions, or forecast. Returns temperature, condition, and humidity. Available cities: London, Tokyo, New York, Paris, Sydney, Delhi, Mumbai, Bangalore, Kolkata.",
    parameters={
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "Name of the city (e.g., 'London', 'Tokyo', 'Paris')"
            },
            "unit": {
                "type": "string",
                "enum": ["celsius", "fahrenheit"],
                "description": "Temperature unit (default: celsius)"
            }
        },
        "required": ["city"]
    }
)

# Time Tool Schema
time_declaration = types.FunctionDeclaration(
    name="get_current_time",
    description="Get the current date and time in any timezone. Use when user asks 'what time is it', 'current time', or mentions a specific timezone.",
    parameters={
        "type": "object",
        "properties": {
            "timezone": {
                "type": "string",
                "description": "Timezone string (e.g., 'UTC', 'America/New_York', 'Asia/Tokyo'). Default is UTC."
            }
        },
        "required": []
    }
)

# Search Tool Schema
search_declaration = types.FunctionDeclaration(
    name="web_search",
    description="Search the web for current information, facts, or answers not in your training data. Use when you need external information or user asks to 'search' or 'look up' something.",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query string"
            }
        },
        "required": ["query"]
    }
)

# Combine all tools into a single Tool object
all_tools = types.Tool(
    function_declarations=[
        calculator_declaration,
        weather_declaration,
        time_declaration,
        search_declaration
    ]
)


# ============================================================================
# TOOL AGENT CLASS
# ============================================================================

class ToolAgent:
    """
    AI Agent that can use tools to accomplish tasks using the ReAct pattern
    
    The ReAct pattern:
    1. Reason: AI thinks about what to do
    2. Act: AI decides to call a tool (or give final answer)
    3. Observe: We execute the tool and show the result to AI
    4. Repeat: Loop until AI gives final answer
    
    Key insight: The AI doesn't execute tools. It just tells us WHAT to execute.
    We do the actual execution and feed results back.
    """
    
    def __init__(self):
        """
        Initialize the agent with Gemini client and tools
        """
        # Initialize Gemini client
        self.client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
        
        # Store available tools
        self.tools = all_tools
        
        # Map tool names to actual functions
        # This is how we route tool calls to the right Python function
        self.tool_functions = {
            "calculator": calculator,
            "get_weather": get_weather,
            "get_current_time": get_current_time,
            "web_search": web_search
        }
        
        # Conversation history (needed because AI is stateless)
        self.conversation_history = []
        
        # Max iterations to prevent infinite loops
        self.max_iterations = 5
    
    def execute_tool(self, tool_name: str, arguments: dict) -> str:
        """
        Execute a tool function with given arguments
        
        This is where we actually RUN the tool that the AI requested.
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Dictionary of tool parameters
            
        Returns:
            String result from the tool
        """
        # Check if tool exists
        if tool_name not in self.tool_functions:
            return f"Error: Unknown tool '{tool_name}'"
        
        # Get the actual Python function
        tool_function = self.tool_functions[tool_name]
        
        try:
            # Call the function with the arguments
            # **arguments unpacks the dict into keyword arguments
            result = tool_function(**arguments)
            return result
        
        except TypeError as e:
            # This happens if AI provided wrong parameters
            return f"Error: Invalid parameters for {tool_name}: {str(e)}"
        
        except Exception as e:
            # Catch any other errors
            return f"Error executing {tool_name}: {str(e)}"
    
    def run(self, user_query: str) -> str:
        """
        Main agent loop - implements the ReAct pattern
        
        Process:
        1. Add user query to conversation
        2. Loop (max 5 times):
            a. Send conversation + tools to AI
            b. Check if AI wants to call a tool
            c. If yes: execute tool, add result, loop again
            d. If no: AI gave final answer, return it
        3. If we hit max iterations, return what we have
        
        Args:
            user_query: The user's question or request
            
        Returns:
            Final answer string
        """
        print(f"\n{'='*60}")
        print(f"🤔 User Query: {user_query}")
        print(f"{'='*60}\n")
        
        # Add user query to conversation history
        self.conversation_history.append({
            "role": "user",
            "parts": [{"text": user_query}]
        })
        
        # ReAct loop
        for iteration in range(self.max_iterations):
            print(f"[Iteration {iteration + 1}/{self.max_iterations}]")
            
            try:
                # Send conversation to AI with tools
                response = self.client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=self.conversation_history,
                    config=types.GenerateContentConfig(
                        tools=[self.tools]
                    )
                )
                
                # Check if response has parts
                if not response.candidates or not response.candidates[0].content.parts:
                    print("⚠️ No response from AI")
                    return "Error: No response from AI"
                
                # Get the first part of the response
                first_part = response.candidates[0].content.parts[0]
                
                # Check if AI wants to call a function
                if hasattr(first_part, 'function_call') and first_part.function_call:
                    # AI WANTS TO USE A TOOL
                    function_call = first_part.function_call
                    tool_name = function_call.name
                    tool_args = dict(function_call.args)
                    
                    print(f"🔧 Tool Call: {tool_name}")
                    print(f"📋 Arguments: {json.dumps(tool_args, indent=2)}")
                    
                    # Execute the tool
                    result = self.execute_tool(tool_name, tool_args)
                    
                    print(f"✅ Result: {result}\n")
                    
                    # Add AI's tool call to conversation
                    self.conversation_history.append({
                        "role": "model",
                        "parts": [{"function_call": function_call}]
                    })
                    
                    # Add tool result to conversation
                    self.conversation_history.append({
                        "role": "function",
                        "parts": [{
                            "function_response": {
                                "name": tool_name,
                                "response": {"result": result}
                            }
                        }]
                    })
                    
                    # Loop continues - AI will see the result and decide what to do next
                    continue
                
                else:
                    # AI GAVE FINAL ANSWER (no tool call)
                    final_answer = first_part.text if hasattr(first_part, 'text') else str(first_part)
                    
                    print(f"💡 Final Answer: {final_answer}\n")
                    
                    # Add AI's response to history
                    self.conversation_history.append({
                        "role": "model",
                        "parts": [{"text": final_answer}]
                    })
                    
                    return final_answer
            
            except Exception as e:
                print(f"❌ Error in iteration {iteration + 1}: {str(e)}\n")
                return f"Error: {str(e)}"
        
        # If we get here, we hit max iterations
        print("⚠️ Reached maximum iterations without final answer")
        return "I apologize, but I couldn't complete the task within the iteration limit. Please try rephrasing your question."
    
    def reset(self):
        """Reset conversation history"""
        self.conversation_history = []
        print("🔄 Conversation history cleared\n")


# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    """
    Main loop for the tool agent CLI
    """
    print("="*60)
    print("AI AGENT WITH TOOLS (ReAct Pattern)")
    print("="*60)
    print("\nAvailable Tools:")
    print("  🧮 Calculator - Perform math operations")
    print("  🌤️  Weather - Get current weather for cities")
    print("  🕐 Time - Get current time in any timezone")
    print("  🔍 Search - Search the web (mock)")
    print("\nCommands:")
    print("  /tools - List available tools")
    print("  /reset - Clear conversation history")
    print("  /quit  - Exit")
    print("\nType your question or request:")
    
    # Create agent
    agent = ToolAgent()
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() in ['/quit', '/exit', '/q']:
                print("\n👋 Goodbye!")
                break
            
            if user_input.lower() == '/tools':
                print("\n📋 Available Tools:")
                print("  1. calculator - Math operations (add, subtract, multiply, divide, power, sqrt)")
                print("  2. get_weather - Weather for cities (London, Tokyo, New York, Paris, Sydney, etc.)")
                print("  3. get_current_time - Current time in any timezone")
                print("  4. web_search - Search for information")
                continue
            
            if user_input.lower() == '/reset':
                agent.reset()
                continue
            
            # Process the query with the agent
            answer = agent.run(user_input)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    main()