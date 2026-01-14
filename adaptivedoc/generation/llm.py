# adaptivedoc/generation/llm.py

from unsloth import FastLanguageModel
import torch
import re
from typing import List, Optional

MODEL_NAME = "Qwen/Qwen2.5-Coder-7B-Instruct"

class LLMGenerator:
    def __init__(self):
        self.model, self.tokenizer = FastLanguageModel.from_pretrained(
            MODEL_NAME,
            max_seq_length=4096,
            load_in_4bit=True,
            dtype=torch.float16,
        )
        FastLanguageModel.for_inference(self.model)

    # =========================
    # Prompt construction
    # =========================

    def _build_messages(
        self,
        code: str,
        dependency_docs: Optional[List[str]] = None,
        style_examples: Optional[List[str]] = None,
    ) -> List[dict]:
        """
        Теперь мы строим не строку, а список сообщений для Chat Template.
        """
        
        examples_block = ""
        if style_examples:
            examples_block = "\n\nStyle examples:\n" + "\n\n".join(style_examples[:2])

        deps_block = ""
        if dependency_docs:
            deps_block = "\n\nContext dependencies:\n" + "\n\n".join(dependency_docs[:2])

        system_content = f"""You are a professional Python documentation generator.
Your task is to generate a NumPy-style docstring BODY for the provided code.

STRICT RULES:
- Return ONLY plain text.
- DO NOT use markdown code blocks (```).
- DO NOT repeat the function signature.
- Start directly with a short summary sentence.
- Follow NumPy format EXACTLY.

Format:
<Short summary sentence>

Parameters
----------
name : type
    Description

Returns
-------
type
    Description
"""

        user_content = f"""
{examples_block}
{deps_block}

Python code to document:
{code}

Generate ONLY the docstring body now:
"""
        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content.strip()}
        ]

    # =========================
    # Generation
    # =========================

    def generate_docstring(
        self,
        code: str,
        dependency_docs: Optional[List[str]] = None,
        style_examples: Optional[List[str]] = None,
    ) -> str:
        messages = self._build_messages(code, dependency_docs, style_examples)

        prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        inputs = self.tokenizer(prompt, return_tensors="pt").to("cuda")

        outputs = self.model.generate(
            **inputs,
            max_new_tokens=512, 
            temperature=0.2,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id 
        )

        generated_tokens = outputs[0][len(inputs['input_ids'][0]):]
        doc = self.tokenizer.decode(generated_tokens, skip_special_tokens=True)

        return self._clean_output(doc)

    # =========================
    # Cleanup
    # =========================

    def _clean_output(self, text: str) -> str:
        text = text.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines)
        
        text = text.replace('"""', "").strip()
        return text

    @staticmethod
    def looks_like_numpy(doc: str) -> bool:
        if not doc:
            return False
        if "Parameters" in doc or "Returns" in doc:
            return True
        return False