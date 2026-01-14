# adaptivedoc/parser/injector.py
import libcst as cst
from typing import Dict

class DocstringInserter(cst.CSTTransformer):
    """
    Трансформер LibCST, который находит функции по имени
    и вставляет/заменяет им Docstring.
    """
    def __init__(self, docstrings_map: Dict[str, str]):
        # docstrings_map: { "function_name": "Docstring text..." }
        self.docstrings_map = docstrings_map

    def leave_FunctionDef(
        self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef
    ) -> cst.CSTNode:
        
        func_name = original_node.name.value
        
        # Если для этой функции нет сгенерированной доки — пропускаем
        if func_name not in self.docstrings_map:
            return updated_node

        doc_text = self.docstrings_map[func_name]
        
        # Формируем строку в тройных кавычках
        # Важно: LibCST не добавляет отступы внутрь строки сам, 
        # но для docstring body это обычно не критично, если генератор выдал plain text.
        quoted_doc = f'"""\n{doc_text}\n"""'
        
        # Создаем узел выражения (Statement)
        doc_node = cst.SimpleStatementLine(
            body=[
                cst.Expr(
                    value=cst.SimpleString(quoted_doc)
                )
            ]
        )

        # Логика вставки:
        # Проверяем, есть ли уже docstring (первым выражением в теле)
        body_block = updated_node.body
        new_body_content = list(body_block.body)
        
        if len(new_body_content) > 0:
            first_stmt = new_body_content[0]
            # Является ли первая строка строкой-литералом?
            if isinstance(first_stmt, cst.SimpleStatementLine):
                if isinstance(first_stmt.body[0], cst.Expr):
                    if isinstance(first_stmt.body[0].value, cst.SimpleString):
                        # ДА, это докстринг. ЗАМЕНЯЕМ его.
                        new_body_content[0] = doc_node
                        return updated_node.with_changes(
                            body=body_block.with_changes(body=new_body_content)
                        )

        # НЕТ, докстринга не было. ВСТАВЛЯЕМ в начало.
        new_body_content.insert(0, doc_node)
        
        return updated_node.with_changes(
            body=body_block.with_changes(body=new_body_content)
        )

def inject_docstrings_to_code(source_code: str, docstrings_map: Dict[str, str]) -> str:
    """
    Принимает исходный код (строку), парсит его, вставляет доки и возвращает новый код.
    """
    try:
        tree = cst.parse_module(source_code)
        transformer = DocstringInserter(docstrings_map)
        modified_tree = tree.visit(transformer)
        return modified_tree.code
    except Exception as e:
        print(f"[ERROR in Injector] {e}")
        return source_code