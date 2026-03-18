import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

def calculator(operation: str, a: float, b: float = None) -> str:
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
    
    if unit.lower() == "fahrenheit":
        temp = (temp * 9/5) + 32
        unit_symbol = "°F"
    else:
        unit_symbol = "°C"
    
    return f"Weather in {city.title()}: {temp}{unit_symbol}, {weather['condition']}, Humidity: {weather['humidity']}%"


def get_current_time(timezone: str = "UTC") -> str:
    now = datetime.utcnow()
    
    formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
    
    return f"Current time in {timezone}: {formatted_time}"


def web_search(query: str) -> str:
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
    
    for key, value in MOCK_SEARCHES.items():
        if key in query_lower:
            return f"Search results for '{query}':\n{value}"
    
    return f"Search results for '{query}':\nNo specific information found in mock database. In a real implementation, this would search the web using APIs like Google Search or Bing."


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

all_tools = types.Tool(
    function_declarations=[
        calculator_declaration,
        weather_declaration,
        time_declaration,
        search_declaration
    ]
)


class ToolAgent:
    
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
        
        self.tools = all_tools
        
        self.tool_functions = {
            "calculator": calculator,
            "get_weather": get_weather,
            "get_current_time": get_current_time,
            "web_search": web_search
        }
        
        self.conversation_history = []
        
        self.max_iterations = 5
    
    def execute_tool(self, tool_name: str, arguments: dict) -> str:
        if tool_name not in self.tool_functions:
            return f"Error: Unknown tool '{tool_name}'"
        
        tool_function = self.tool_functions[tool_name]
        
        try:
            result = tool_function(**arguments)
            return result
        
        except TypeError as e:
            return f"Error: Invalid parameters for {tool_name}: {str(e)}"
        
        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"
    
    def run(self, user_query: str) -> str:
        print(f"\n{'='*60}")
        print(f"🤔 User Query: {user_query}")
        print(f"{'='*60}\n")
        
        self.conversation_history.append({
            "role": "user",
            "parts": [{"text": user_query}]
        })
        
        for iteration in range(self.max_iterations):
            print(f"[Iteration {iteration + 1}/{self.max_iterations}]")
            
            try:
                response = self.client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=self.conversation_history,
                    config=types.GenerateContentConfig(
                        tools=[self.tools]
                    )
                )
                
                if not response.candidates or not response.candidates[0].content.parts:
                    print("⚠️ No response from AI")
                    return "Error: No response from AI"
                
                first_part = response.candidates[0].content.parts[0]
                
                if hasattr(first_part, 'function_call') and first_part.function_call:
                    function_call = first_part.function_call
                    tool_name = function_call.name
                    tool_args = dict(function_call.args)
                    
                    print(f"🔧 Tool Call: {tool_name}")
                    print(f"📋 Arguments: {json.dumps(tool_args, indent=2)}")
                    
                    result = self.execute_tool(tool_name, tool_args)
                    
                    print(f"✅ Result: {result}\n")
                    
                    self.conversation_history.append({
                        "role": "model",
                        "parts": [{"function_call": function_call}]
                    })
                    
                    self.conversation_history.append({
                        "role": "function",
                        "parts": [{
                            "function_response": {
                                "name": tool_name,
                                "response": {"result": result}
                            }
                        }]
                    })
                    
                    continue
                
                else:
                    final_answer = first_part.text if hasattr(first_part, 'text') else str(first_part)
                    
                    print(f"💡 Final Answer: {final_answer}\n")
                    
                    self.conversation_history.append({
                        "role": "model",
                        "parts": [{"text": final_answer}]
                    })
                    
                    return final_answer
            
            except Exception as e:
                print(f"❌ Error in iteration {iteration + 1}: {str(e)}\n")
                return f"Error: {str(e)}"
        
        print("⚠️ Reached maximum iterations without final answer")
        return "I apologize, but I couldn't complete the task within the iteration limit. Please try rephrasing your question."
    
    def reset(self):
        self.conversation_history = []
        print("🔄 Conversation history cleared\n")


def main():
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
    
    agent = ToolAgent()
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if not user_input:
                continue
            
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
            
            answer = agent.run(user_input)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    main()