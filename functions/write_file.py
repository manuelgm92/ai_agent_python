import os

def write_file(working_directory: str, file_path: str, content: str) -> str:
    """
    Escribe contenido en un archivo de forma segura dentro de un directorio de trabajo permitido.
    Crea las carpetas necesarias si no existen.
    """
    try:
        # 1. Convertir el directorio base a una ruta absoluta para evitar ambigüedades
        working_directory_absolute_path = os.path.abspath(working_directory)
        
        # 2. Combinar el directorio base con la ruta del archivo y normalizarla (limpia barras duplicadas, etc.)
        target_dir = os.path.join(working_directory_absolute_path, file_path)
        target_dir = os.path.normpath(target_dir)
        
        # 3. FILTRO DE SEGURIDAD: Validar que el archivo final esté DENTRO del directorio permitido
        # (Evita ataques de tipo 'Path Traversal' usando rutas como ../../etc/passwd)
        if os.path.commonpath([working_directory_absolute_path, target_dir]) != working_directory_absolute_path:
            return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
        
        # 4. VALIDACIÓN: Comprobar que la ruta destino no sea un directorio ya existente
        if os.path.isdir(target_dir):
            return f'Error: Cannot write to "{file_path}" as it is a directory'
        
        # 5. CREACIÓN DE CARPETAS: Obtiene el directorio padre del archivo y crea las carpetas que falten
        # (exist_ok=True evita que dé error si las carpetas ya existen)
        os.makedirs(os.path.dirname(target_dir), exist_ok=True)
        
        # 6. ESCRITURA: Abre el archivo en modo escritura ("w") y escribe el contenido
        with open(target_dir, "w") as f:
            f.write(content)
            
        # 7. Retornar mensaje de éxito con la cantidad de caracteres escritos
        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
        
    except Exception as error:
        return f"Error: {error}"
    
schema_write_file = {
    "type": "function",
    "function": {
        "name": "write_file",  # <--- Cambiado al nombre correcto de la función
        "description": "Writes text content to a file at a specified path relative to the working directory. Creates parent directories if they do not exist.",  # <--- Descripción adaptada
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The path to the file to write to, relative to the working directory",
                },
                "content": {
                    "type": "string",
                    "description": "The text content to write into the file",
                },
            },
            "required": ["file_path", "content"],  # <--- Ambos son obligatorios para escribir
        },
    },
}