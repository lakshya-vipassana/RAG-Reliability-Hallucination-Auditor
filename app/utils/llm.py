import subprocess

MODEL_NAME = "llama3"  # or mistral

def llm(prompt: str) -> str:
    """
    Simple, auditable local LLM call using Ollama.
    No streaming. No magic.
    """
    result = subprocess.run(
        ["ollama", "run", MODEL_NAME],
        input=prompt,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr)

    return result.stdout.strip()
