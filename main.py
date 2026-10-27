import os
from dotenv import load_dotenv
from openai import OpenAI
import argparse
from prompts import system_prompt
from call_function import available_functions, call_function
import json

# 1. Cargar las variables de entorno desde el archivo .env
load_dotenv()

# 2. Inicializar el cliente conectándolo a OpenRouter (o proveedor compatible)
# Obtiene el valor de OPENROUTER_API_KEY; devuelve None si la variable no existe
api_key = os.environ.get("OPENROUTER_API_KEY")

# Comprueba si la clave no se encontró (nota: lo idiomático en Python es "is None")
if api_key is None:
    raise RuntimeError("Runtime error")

# Crea el cliente de OpenAI
client = OpenAI(
    # Redirige las peticiones a OpenRouter en lugar de a los servidores de OpenAI y Pasa la clave de API para autenticarse
    base_url = "https://openrouter.ai/api/v1",
    api_key=api_key, 
)

# Crea el analizador de argumentos de línea de comandos, con una descripción del programa
parser = argparse.ArgumentParser(description="Chatbot")

# Define un argumento posicional obligatorio: el texto (prompt) que escribe el usuario
parser.add_argument("user_prompt", type=str, help="User prompt")

# Define una opción opcional --verbose; al ser store_true vale True si se incluye y False si no
parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

# Lee y procesa los argumentos recibidos en la terminal, guardándolos en el objeto args
args = parser.parse_args()

# Crea el historial de la conversación: una lista de mensajes con su rol y contenido
messages = [
    # Mensaje de sistema: define el comportamiento/instrucciones generales del modelo
    {"role": "system", "content": system_prompt},
    # Mensaje del usuario: la pregunta o petición recibida por línea de comandos   
    {"role": "user", "content": args.user_prompt},
    ]

# Define una función que encapsula la llamada al modelo
def generate_content(client, messages):
    # Envía la conversación al endpoint de chat completions y guarda la respuesta
    response = client.chat.completions.create(
        # Modelo a usar: el enrutador de modelos gratuitos de OpenRouter
        model="openrouter/free",
        # Historial de mensajes que el modelo debe procesar
        messages=messages,
        # Lista de herramientas (funciones) que el modelo puede decidir invocar
        tools=available_functions,
    )
    # Devuelve el objeto de respuesta completo
    return response

# Llama a la función anterior y almacena la respuesta del modelo
response = generate_content(client, messages)

# Verifica si la API devolvió datos de uso (consumo de tokens).
if response.usage is not None:
    # Solo muestra la información si el usuario activó --verbose
    if args.verbose:
        # Muestra el prompt original del usuario
        print(f"User prompt: {args.user_prompt}")
        # Muestra cuántos tokens consumió la entrada (prompt)
        print(f"Prompt tokens: {response.usage.prompt_tokens}")
        # Muestra cuántos tokens generó el modelo en su respuesta
        print(f"Response tokens: {response.usage.completion_tokens}")
# Si usage es None (la API no informó del consumo)
else:
    # Lanza un error indicando que falta la información de tokens
    raise RuntimeError("Error: La API no devolvió información sobre el uso de tokens (response.usage es None).")

# Extrae el mensaje del modelo: toma la primera opción (choices[0]) de la respuesta
message = response.choices[0].message

# Si el modelo pidió ejecutar una o más herramientas (la lista no es vacía ni None)
if message.tool_calls:
    # Recorre cada llamada a herramienta solicitada por el modelo
    for tool_call in message.tool_calls:
        # Llamar a nuestra función encargada y asignar el resultado
        # Ejecuta la herramienta pedida; verbose controla si imprime información adicional
        result_message = call_function(tool_call, verbose=args.verbose)
        
        # Validar que el contenido devuelto no esté vacío
        # Si el diccionario no tiene "content" o está vacío, se considera un fallo
        if not result_message.get("content"):
            # Lanza un error indicando el id de la llamada que falló
            raise RuntimeError(f"Error: Tool message content is empty for tool call {tool_call.id}")
            
        # Si estamos en modo verbose, imprimir el resultado de la función
        if args.verbose:
            # Muestra el contenido devuelto por la herramienta, precedido de una flecha
            print(f"-> {result_message['content']}")
            
        # Código comentado (desactivado), conservado como referencia:
        # function_args = json.loads(tool_call.function.arguments or "{}")  # convertiría los argumentos JSON de la llamada en un diccionario
        # print(f"Calling function: {tool_call.function.name}({function_args})")  # mostraría el nombre de la función y sus argumentos
# Si no hubo llamadas a herramientas pero el modelo devolvió texto
elif message.content:
    # Imprime la respuesta de texto del modelo
    print(message.content)
# Si no hay ni herramientas ni texto
else:
    # Informa de que el modelo no devolvió nada útil
    print("El modelo no devolvió contenido ni llamadas a funciones.")

