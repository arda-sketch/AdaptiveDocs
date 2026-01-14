# adaptivedoc/parser/python_ast.py

import ast
import os
from dataclasses import dataclass
from typing import List


@dataclass
class CodeItem:
    name: str
    type: str  # "function" | "class"
    module: str
    signature: str
    code: str
    docstring: str | None
    filepath: str


def _path_to_module(repo_root: str, file_path: str) -> str:
    rel_path = os.path.relpath(file_path, repo_root)
    rel_path = rel_path.replace(os.sep, ".")
    return rel_path[:-3]  # remove .py


def _annotation_to_str(node: ast.AST | None) -> str | None:
    if node is None:
        return None
    try:
        return ast.unparse(node)
    except Exception:
        return None


def _build_signature(node: ast.AST) -> str:
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return node.name

    args = []

    for arg in node.args.args:
        ann = _annotation_to_str(arg.annotation)
        args.append(f"{arg.arg}: {ann}" if ann else arg.arg)

    if node.args.vararg:
        args.append(f"*{node.args.vararg.arg}")

    for arg in node.args.kwonlyargs:
        ann = _annotation_to_str(arg.annotation)
        args.append(f"{arg.arg}: {ann}" if ann else arg.arg)

    if node.args.kwarg:
        args.append(f"**{node.args.kwarg.arg}")

    ret = _annotation_to_str(node.returns)
    ret_part = f" -> {ret}" if ret else ""

    return f"{node.name}({', '.join(args)}){ret_part}"


def parse_python_file(path: str, repo_root: str) -> List[CodeItem]:
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)
    items: List[CodeItem] = []

    module_name = _path_to_module(repo_root, path)

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            doc = ast.get_docstring(node)
            code = ast.get_source_segment(source, node)
            signature = _build_signature(node)

            items.append(
                CodeItem(
                    name=node.name,
                    type="class" if isinstance(node, ast.ClassDef) else "function",
                    module=module_name,
                    signature=signature,
                    code=code,
                    docstring=doc,
                    filepath=path,
                )
            )

    return items


def parse_repo(repo_path: str) -> List[CodeItem]:
    results: List[CodeItem] = []

    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                results.extend(parse_python_file(full_path, repo_path))

    return results
