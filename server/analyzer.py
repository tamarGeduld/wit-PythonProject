import os
import re
import tempfile
import zipfile
import ast
from datetime import datetime
from db import analysis_collection


def analyze_zip(zip_bytes: bytes, save_to_db: bool = True):
    with tempfile.TemporaryDirectory() as predicament:
        zip_path = os.path.join(predicament, "project.zip")

        with open(zip_path, "wb") as f:
            f.write(zip_bytes)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(predicament)

        results = {}
        total_issues = 0

        for root, dirs, files in os.walk(predicament):
            for filename in files:
                if filename.endswith(".py"):
                    file_path = os.path.join(root, filename)
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    tree = ast.parse(content)

                    func_warnings, func_lengths = check_if_func_too_long(file_path)
                    file_too_long = check_if_file_too_long(file_path)
                    unused_vars = check_unused_variables(file_path)
                    docstrings = check_missing_docstrings(file_path)
                    non_english = check_non_english_variables(tree)

                    total_issues += (
                        len(func_warnings)
                        + len(file_too_long)
                        + len(unused_vars)
                        + len(docstrings)
                        + len(non_english)
                    )

                    results[filename] = {
                        "long_functions": func_warnings,
                        "function_lengths": func_lengths,
                        "file_too_long": file_too_long,
                        "unused_variables": unused_vars,
                        "missing_docstrings": docstrings,
                        "non_english_variable_names": non_english,
                    }

        if save_to_db:
            analysis_collection.insert_one({
                "timestamp": datetime.now(),
                "issues": total_issues
            })

    return results

def check_if_func_too_long(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        source = f.read()

    tree = ast.parse(source)
    warnings = []
    lengths = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            start_line = node.lineno
            end_line = max([getattr(n, 'lineno', start_line) for n in ast.walk(node)])
            length = end_line - start_line + 1
            if length > 20:
                warnings.append({
                    "type": "long_function",
                    "message": f"Function '{node.name}' is too long: {length} lines",
                    "line": start_line
                })
            lengths.append(length)

    return warnings, lengths

def check_if_file_too_long(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    if len(lines) > 200:
        return [{
            "type": "long_file",
            "message": f"Warning: File is too long ({len(lines)} lines). Limit is 200 lines.",
            "line": None
        }]
    else:
        return []


def check_unused_variables(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)
    assigned_vars = set()
    used_vars = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    assigned_vars.add((target.id, target.lineno))
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            used_vars.add(node.id)

    unused_vars = [(var, line) for (var, line) in assigned_vars if var not in used_vars]

    return [{
        "type": "unused_variable",
        "message": f"Variable '{var}' is assigned but never used.",
        "line": line
    } for var, line in unused_vars]

def check_missing_docstrings(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)
    warnings = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if ast.get_docstring(node) is None:
                warnings.append({
                    "type": "missing_docstring",
                    "message": f"Function '{node.name}' is missing a docstring.",
                    "line": node.lineno
                })

    return warnings


def check_non_english_variables(tree):
    warnings = []
    non_latin_pattern = re.compile(r'[^\x00-\x7F]')

    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            if non_latin_pattern.search(node.id):
                warnings.append({
                    "type": "non_english_variable",
                    "message": f"Variable name '{node.id}' contains non-English characters.",
                    "line": node.lineno
                })

    return warnings

