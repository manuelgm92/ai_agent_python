import os
from config import MAX_CHARS

def get_file_content(working_directory:str, file_path:str) -> str:
    
    try:
        # 1. Obtener la ruta absoluta del working_directory
        absolute_path = os.path.abspath(working_directory)
        
        # 2. Construir y normalizar la ruta completa del directorio destino
        target_dir = os.path.join(absolute_path, file_path)
        target_dir = os.path.normpath(target_dir)
        
        # 3. Validar que la ruta esté dentro del directorio de trabajo permitido
        if os.path.commonpath([absolute_path, target_dir]) != absolute_path:
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

        # 4. Comprobar si no es un archivo
        if not os.path.isfile(target_dir):
            return f'Error: File not found or is not a regular file: "{file_path}"'
        
        with open(target_dir, "r") as f:
            file_content_string = f.read(MAX_CHARS)
            if f.read(1):
                file_content_string += f'[...File "{target_dir}" truncated at {MAX_CHARS} characters]'
            return file_content_string
        
    except Exception as error:
        return f"Error: {error}"

schema_get_file_content = {
    "type": "function",
    "function": {
        "name": "get_file_content",
        "description": "Read the contents of a file at a specified path relative to the working directory",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {  # <--- Cambiado de 'directory' a 'file_path'
                    "type": "string",
                    "description": "The path to the file to read, relative to the working directory",
                },
            },
            "required": ["file_path"],
        },
    },
}