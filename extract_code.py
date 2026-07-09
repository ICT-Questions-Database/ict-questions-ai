import sys
from pathlib import Path

IGNORE_DIRS = {".venv", "__pycache__", ".git", ".idea", "venv", "env", "node_modules", "dist", "build"}

def should_ignore(file_path: Path) -> bool:
    for part in file_path.parts:
        if part in IGNORE_DIRS or part.startswith(".") and part != ".":
            return True
    return False

def compile_py_to_txt(source_dir: str = ".", output_filename: str = "compiled_code.txt") -> None:
    source = Path(source_dir).resolve()
    if not source.is_dir():
        print(f"Erro: {source} não é um diretório válido.")
        sys.exit(1)

    all_py = list(source.rglob("*.py"))
    py_files = [f for f in all_py if not should_ignore(f)]

    if not py_files:
        print("Nenhum arquivo .py encontrado.")
        return

    print(f"Encontrados {len(py_files)} arquivos .py.")
    with open(output_filename, "w", encoding="utf-8") as out:
        for py_file in sorted(py_files):
            relative_path = py_file.relative_to(source)
            out.write(f"\n\n{'='*80}\n")
            out.write(f"FILE: {relative_path}\n")
            out.write(f"{'='*80}\n\n")
            try:
                content = py_file.read_text(encoding="utf-8")
                out.write(content)
            except Exception as e:
                out.write(f"Erro ao ler arquivo: {e}\n")
    print(f"Compilação concluída. Arquivo gerado: {output_filename}")

if __name__ == "__main__":
    compile_py_to_txt()