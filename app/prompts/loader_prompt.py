from pathlib import Path

# 读取指定的prompt内容
def load_prompt(name: str) -> str:
    prompt_path = Path(__file__).parents[2] / "prompts" / f"{name}.prompt"
    prompt_text = prompt_path.read_text(encoding="utf-8")
    return prompt_text

if __name__ == "__main__":
    prompt_path = Path(__file__).parents[2]
    # d:\VScodeProjects\Agent_Learning\个人项目实战\E-commerce
    print(prompt_path)
