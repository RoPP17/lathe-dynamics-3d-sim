"""
Script de auditoría técnica y métricas cuantitativas del código fuente.
Calcula Líneas de Código (LOC), comentarios, líneas en blanco, clases, funciones y complejidad modular.
"""

import os
import ast
import json

def analyze_directory(base_dir):
    stats = {}
    total_files = 0
    total_loc = 0
    total_code = 0
    total_comment = 0
    total_blank = 0
    total_classes = 0
    total_functions = 0

    target_folders = ["physics", "simulation", "visualization", "ui", "config", "tests"]
    
    # Archivos raíz
    root_files = ["main.py", "generate_icon.py"]

    detailed_files = []

    for root, dirs, files in os.walk(base_dir):
        # Excluir carpetas temporales y de compilación
        dirs[:] = [d for d in dirs if d not in [".git", ".idea", "__pycache__", "build", "dist", ".pytest_cache", ".venv"]]
        
        for f in files:
            if not f.endswith(".py") or f == "analyze_codebase.py":
                continue
            
            fpath = os.path.join(root, f)
            relpath = os.path.relpath(fpath, base_dir)
            
            with open(fpath, "r", encoding="utf-8", errors="replace") as fp:
                content = fp.read()
                lines = content.splitlines()

            n_loc = len(lines)
            n_blank = 0
            n_comment = 0
            n_code = 0

            in_multiline = False
            for line in lines:
                sline = line.strip()
                if not sline:
                    n_blank += 1
                elif sline.startswith("#"):
                    n_comment += 1
                elif '"""' in sline or "'''" in sline:
                    n_comment += 1
                    # Comprobar si abre o cierra bloque multilínea
                    cnt = sline.count('"""') + sline.count("'''")
                    if cnt % 2 == 1:
                        in_multiline = not in_multiline
                elif in_multiline:
                    n_comment += 1
                else:
                    n_code += 1

            # Análisis AST para contar Clases y Funciones
            n_classes = 0
            n_funcs = 0
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        n_classes += 1
                    elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        n_funcs += 1
            except Exception:
                pass

            total_files += 1
            total_loc += n_loc
            total_code += n_code
            total_comment += n_comment
            total_blank += n_blank
            total_classes += n_classes
            total_functions += n_funcs

            # Determinar módulo
            parts = relpath.split(os.sep)
            module_name = parts[0] if len(parts) > 1 else "root"
            
            if module_name not in stats:
                stats[module_name] = {
                    "files": 0, "loc": 0, "code": 0, "comment": 0, "blank": 0,
                    "classes": 0, "functions": 0
                }
            
            stats[module_name]["files"] += 1
            stats[module_name]["loc"] += n_loc
            stats[module_name]["code"] += n_code
            stats[module_name]["comment"] += n_comment
            stats[module_name]["blank"] += n_blank
            stats[module_name]["classes"] += n_classes
            stats[module_name]["functions"] += n_funcs

            detailed_files.append({
                "path": relpath,
                "module": module_name,
                "loc": n_loc,
                "code": n_code,
                "comment": n_comment,
                "blank": n_blank,
                "classes": n_classes,
                "functions": n_funcs
            })

    report = {
        "summary": {
            "total_files": total_files,
            "total_loc": total_loc,
            "total_code": total_code,
            "total_comment": total_comment,
            "total_blank": total_blank,
            "total_classes": total_classes,
            "total_functions": total_functions,
            "comment_ratio_pct": round((total_comment / total_loc * 100) if total_loc else 0, 2)
        },
        "by_module": stats,
        "files": detailed_files
    }
    return report

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    res = analyze_directory(base_dir)
    print(json.dumps(res, indent=2))
