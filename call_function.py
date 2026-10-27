from functions.get_files_info import schema_get_files_info, get_files_info
from functions.get_file_content import schema_get_file_content, get_file_content
from functions.write_file import schema_write_file, write_file
from functions.run_python_file import schema_run_python_file, run_python_file
import json
from collections.abc import Callable

# Lista de funciones disponibles par exportar a main.py
available_functions = [
    schema_get_files_info, schema_get_file_content,  schema_write_file, schema_run_python_file
]

# Diccionario de mapeo de nombre de función a función ejecutable de Python
function_map: dict[str, Callable[..., str]] = {
        "get_file_content": get_file_content,
        "get_files_info": get_files_info,
        "write_file": write_file,
        "run_python_file": run_python_file,
        }

def call_function(tool_call, verbose: bool = False) -> dict:
    function_name = tool_call.function.name
    function_args = json.loads(tool_call.function.arguments or "{}")

    if verbose:
        print(f" - Calling function: {function_name}({function_args})")
    else:
        print(f" - Calling function: {function_name}")
        
    if function_name not in function_map:
        return {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": f"Error: Unknown function: {function_name}",
        }
    
    # Inyectar el working_directory que el LLM desconoce
    function_args["working_directory"] = "../calculator"
    
    try:
        # Ejecutar la función pasando los argumentos desempaquetados
        result = function_map[function_name](**function_args)
    except Exception as error:
        result = f"Error: executing function {function_name}: {error}"

    # Retornar el mensaje de herramienta requerido por la API de OpenAI
    return {
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": result,
        }