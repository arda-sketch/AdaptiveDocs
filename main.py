# main.py

import os
import argparse
from tqdm import tqdm

from adaptivedoc.parser.python_ast import parse_repo
from adaptivedoc.generation.llm import LLMGenerator
from adaptivedoc.graph.dependency import build_dependency_graph
from adaptivedoc.graph.order import topological_order
# Импортируем втсавку
from adaptivedoc.parser.injector import inject_docstrings_to_code

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("repo_path", type=str)
    args = parser.parse_args()
    
    repo_path = args.repo_path
    output_file = os.path.join("docs", "generated_docstrings.md")
    # Файл песочницы
    sandbox_file = os.path.join("experiments", "sandbox.py")

    print(f"[INFO] Parsing: {repo_path}")
    items = parse_repo(repo_path)
    item_map = {f"{i.module}.{i.name}": i for i in items}
    print(f"[INFO] Found {len(items)} items")

    graph = build_dependency_graph(repo_path)
    order = topological_order(graph)

    execution_order = [node for node in order if node in item_map]
    visited = set(execution_order)
    for name in item_map:
        if name not in visited:
            execution_order.append(name)

    print("[INFO] Loading LLM...")
    generator = LLMGenerator()
    docstore = {} 
    
    md_lines = ["# Generated Documentation\n"]

    for func_name in tqdm(execution_order, desc="Generating"):
        item = item_map[func_name]
        
        context_docs = []
        if graph.has_node(func_name):
            deps = list(graph.predecessors(func_name))
            for dep in deps:
                if dep in docstore:
                    context_docs.append(f"Function `{dep}`:\n{docstore[dep]}")

        if item.docstring:
            docstore[func_name] = item.docstring
            continue

        doc = generator.generate_docstring(
            code=item.code,
            dependency_docs=context_docs
        )
        docstore[func_name] = doc
        
        md_lines.append(f"## {func_name}")
        md_lines.append("```python")
        md_lines.append(item.signature)
        md_lines.append('"""')
        md_lines.append(doc)
        md_lines.append('"""')
        md_lines.append("```\n")

    # Сохраняем Markdown отчет
    os.makedirs("docs", exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    print(f"[DONE] Markdown report saved to {output_file}")

    # ==========================================
    # SANDBOX INJECTION TEST
    # ==========================================
    print("\n[TEST] Creating sandbox file for injection test...")
    os.makedirs("experiments", exist_ok=True)

    # 1. Собираем весь код из test_repo в одну строку
    full_source_code = ""
    simple_name_to_doc = {}

    for func_name in execution_order:
        item = item_map[func_name]
        full_source_code += f"# From {item.module}\n"
        full_source_code += item.code + "\n\n"
        
        # Инжектор работает по node.name.value (короткое имя).
        short_name = func_name.split(".")[-1]
        if func_name in docstore:
            simple_name_to_doc[short_name] = docstore[func_name]

    # 2. Применяем инъекцию
    print("[TEST] Injecting docstrings into sandbox code...")
    injected_code = inject_docstrings_to_code(full_source_code, simple_name_to_doc)

    # 3. Записываем результат
    with open(sandbox_file, "w", encoding="utf-8") as f:
        f.write(injected_code)

    print(f"[DONE] Sandbox file created: {sandbox_file}")
    print("Check this file to see the code with injected docstrings!")

if __name__ == "__main__":
    main()