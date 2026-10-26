import os
from dotenv import load_dotenv
from openai import OpenAI
import argparse

load_dotenv()
api_key = os.environ.get("OPENROUTER_API_KEY")

if api_key == None:
    raise RuntimeError("Runtime error")

client = OpenAI(
    base_url = "https://openrouter.ai/api/v1",
    api_key=api_key,
)

parser = argparse.ArgumentParser(description="Chatbot")
parser.add_argument("user_prompt", type=str, help="User prompt")
parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

args = parser.parse_args()

messages = [
    {"role": "user", "content": args.user_prompt},
    ]

def generate_content(client, messages):
    response = client.chat.completions.create(
        model="openrouter/free",
        messages=messages
    )
    return response

response = generate_content(client, messages)

if response.usage is not None:
    if args.verbose:
        print(f"User prompt: {args.user_prompt}")
        print(f"Prompt tokens: {response.usage.prompt_tokens}")
        print(f"Response tokens: {response.usage.completion_tokens}")
else:
    raise RuntimeError("Error: La API no devolvió información sobre el uso de tokens (response.usage es None).")

print(response.choices[0].message.content)
