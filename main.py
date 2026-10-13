"""
Interactive Command Line Interface for Google ADK EE Agent
"""
import sys
import asyncio
from dotenv import load_dotenv

# Ensure UTF-8 output encoding for Windows Command Prompt (supports Ω, µ, τ symbols)
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from agent import ee_agent

load_dotenv()

async def run_agent(runner, user_prompt: str, user_id: str = "user", session_id: str = "s1"):
    content = types.Content(role="user", parts=[types.Part.from_text(text=user_prompt)])
    response_text = ""
    
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        if hasattr(event, "content") and event.content:
            for part in event.content.parts:
                if hasattr(part, "text") and part.text:
                    response_text += part.text
    return response_text

async def main_async():
    print("=" * 60)
    print("  EE Circuit Analysis ADK Agent (MCP-Driven)")
    print("=" * 60)
    print("Type your circuit query below (or 'quit' to exit).\n")

    session_service = InMemorySessionService()
    await session_service.create_session(app_name="ee_app", user_id="user", session_id="s1")
    runner = Runner(app_name="ee_app", agent=ee_agent, session_service=session_service)

    sample_prompts = [
        "I have an RC low-pass filter with R = 4.7k ohms and C = 100nF. What is the cutoff frequency and time constant?",
        "I calculated a target resistor value of 4.73 kOhms. What is the nearest real-world E24 resistor and percentage error?",
        "Analyze a transfer function with numerator [1000] and denominator [1, 1000]. What is the maximum gain and cutoff frequency?",
        "Find the resonance frequency and Q factor for a series RLC circuit with R=10 ohms, L=1mH, and C=1uF."
    ]

    print("Sample Prompts to try:")
    for i, prompt in enumerate(sample_prompts, 1):
        print(f"  {i}. {prompt}")
    print("-" * 60)

    while True:
        try:
            user_prompt = input("\nEE-Agent > ").strip()
            if not user_prompt:
                continue
            if user_prompt.lower() in ["quit", "exit", "q"]:
                print("Exiting EE Agent. Goodbye!")
                break
            
            print("\n[Processing with Google ADK Agent...]")
            response = await run_agent(runner, user_prompt)
            print("\n[Agent Response]:")
            print(response if response else "[Completed]")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\n[Error running agent]: {e}")

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
