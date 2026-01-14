import ast
import os
import networkx as nx
import builtins
from typing import Dict, Set, List


BUILTINS = set(dir(builtins))


class FunctionCollector(ast.NodeVisitor):
    """
    Собирает все функции и методы проекта.
    """
    def __init__(self, module: str):
        self.module = module
        self.functions: Set[str] = set()

    def visit_FunctionDef(self, node):
        self.functions.add(f"{self.module}.{node.name}")

    def visit_AsyncFunctionDef(self, node):
        self.functions.add(f"{self.module}.{node.name}")


class DependencyVisitor(ast.NodeVisitor):
    """
    Собирает зависимости внутри одной функции.
    """
    def __init__(self, module: str, known_functions: Dict[str, str]):
        self.module = module
        self.known_functions = known_functions
        self.current_function = None
        self.dependencies: Dict[str, Set[str]] = {}

    def visit_FunctionDef(self, node):
        self.current_function = f"{self.module}.{node.name}"
        self.dependencies.setdefault(self.current_function, set())
        self.generic_visit(node)
        self.current_function = None

    def visit_Call(self, node):
        if not self.current_function:
            return

        func_name = None

        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        if func_name and func_name not in BUILTINS:
            if func_name in self.known_functions:
                self.dependencies[self.current_function].add(
                    self.known_functions[func_name]
                )

        self.generic_visit(node)


def discover_functions(repo_path: str) -> Dict[str, str]:
    """
    Возвращает mapping: short_name -> full_name
    """
    functions = {}

    for root, _, files in os.walk(repo_path):
        for file in files:
            if not file.endswith(".py"):
                continue

            path = os.path.join(root, file)
            module = os.path.relpath(path, repo_path).replace(os.sep, ".")[:-3]

            with open(path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())

            collector = FunctionCollector(module)
            collector.visit(tree)

            for full_name in collector.functions:
                short = full_name.split(".")[-1]
                functions[short] = full_name

    return functions


def build_dependency_graph(repo_path: str) -> nx.DiGraph:
    graph = nx.DiGraph()

    known_functions = discover_functions(repo_path)

    for full_name in known_functions.values():
        graph.add_node(full_name)

    for root, _, files in os.walk(repo_path):
        for file in files:
            if not file.endswith(".py"):
                continue

            path = os.path.join(root, file)
            module = os.path.relpath(path, repo_path).replace(os.sep, ".")[:-3]

            with open(path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())

            visitor = DependencyVisitor(module, known_functions)
            visitor.visit(tree)

            for src, deps in visitor.dependencies.items():
                for dep in deps:
                    graph.add_edge(dep, src)

    return graph
