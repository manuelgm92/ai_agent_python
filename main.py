import os
from dotenv import load_dotenv
from openai import OpenAI
import argparse
from prompts import system_prompt
from call_function import available_functions, call_function
import json

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
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": args.user_prompt},
    ]

def generate_content(client, messages):
    response = client.chat.completions.create(
        model="openrouter/free",
        messages=messages,
        tools=available_functions,
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

message = response.choices[0].message
if message.tool_calls:
    for tool_call in message.tool_calls:
        # Llamar a nuestra función encargada y asignar el resultado
        result_message = call_function(tool_call, verbose=args.verbose)
        
        # Validar que el contenido devuelto no esté vacío
        if not result_message.get("content"):
            raise RuntimeError(f"Error: Tool message content is empty for tool call {tool_call.id}")
            
        # Si estamos en modo verbose, imprimir el resultado de la función
        if args.verbose:
            print(f"-> {result_message['content']}")
            
        # function_args = json.loads(tool_call.function.arguments or "{}")
        # print(f"Calling function: {tool_call.function.name}({function_args})")
elif message.content:
    print(message.content)
else:
    print("El modelo no devolvió contenido ni llamadas a funciones.")

