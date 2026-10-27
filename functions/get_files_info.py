import os
# Este código sirve para explorar y listar de forma segura el contenido de 
# un directorio dentro de un espacio de trabajo permitido, 
# devolviendo un reporte detallado de cada archivo o carpeta que contiene.

def get_files_info(working_directory: str, directory: str = ".") -> str:
    try:
        # 1. Obtener la ruta absoluta del working_directory
        working_dir_abs = os.path.abspath(working_directory)
        
        # 2. Construir y normalizar la ruta completa del directorio destino
        target_dir = os.path.normpath(os.path.join(working_dir_abs, directory))
        
        # 3. Validar que la ruta esté dentro del directorio de trabajo permitido
        if os.path.commonpath([working_dir_abs, target_dir]) != working_dir_abs:
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
            
        # 4. Validar que efectivamente sea un directorio
        if not os.path.isdir(target_dir):
            return f'Error: "{directory}" is not a directory'
          
        result = []
        list_dir_or_files = os.listdir(target_dir)
        for dir_or_file in list_dir_or_files:
            full_path = os.path.join(target_dir, dir_or_file)
            result.append(f"  - {dir_or_file}: file_size={(os.path.getsize(full_path))} bytes, is_dir={os.path.isdir(full_path)}")
        
        result_final = "\n".join(result)
        # 5. Si todo es correcto, devolver mensaje de éxito
        return result_final
        
    except Exception as error:
        return f"Error: {error}"

schema_get_files_info = {
    "type": "function",
    "function": {
        "name": "get_files_info",
        "description": "Lists files in a specified directory relative to the working directory, providing file size and directory status",
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "Directory path to list files from, relative to the working directory (default is the working directory itself)",
                },
            },
        },
    },
}