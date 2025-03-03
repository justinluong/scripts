# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "nbformat",
#     "pathspec>=0.12.1",
#     "typer",
# ]
# ///

import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Annotated

import nbformat
import pathspec
import typer

EXCLUDE_PATTERNS = [
    "*.ipynb",
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    "__pycache__",
    "venv",
    ".venv",
    "node_modules",
    ".vscode",
    ".venv",
    ".env",
    ".ruff_cache",
    "uv.lock",
    "*-llm.txt",
    ".nx",
    "*.py.lock",
    "package-lock.json",
]


@dataclass(order=True)
class FileInfo:
    line_count: int
    path: Path
    content: str = field(default="", compare=False)

    def __str__(self) -> str:
        return f"{self.path} ({self.line_count} lines)"


def get_default_output_path(root_dir: Path) -> Path:
    """Return default output file path based on the root directory name."""
    return root_dir / f"{root_dir.resolve().name}-llm.txt"


def clean_notebook_content(content: str) -> str:
    """Clean notebook content by removing cell outputs and execution counts."""
    try:
        nb = nbformat.reads(content, as_version=4)
        for cell in nb.cells:
            # Remove cell outputs
            if "outputs" in cell:
                cell.outputs = []
            # Remove execution count
            if "execution_count" in cell:
                cell.execution_count = None
            # Remove cell metadata
            cell.metadata = {}
        # Remove notebook metadata
        nb.metadata = {}
        return nbformat.writes(nb)
    except Exception as e:
        typer.echo(f"Warning: Failed to clean notebook content: {e}", err=True)
        return ""


def read_file_content(file_path: Path) -> str:
    """Read and potentially clean file content based on file type."""
    try:
        content = file_path.read_text(encoding="utf-8")
        if file_path.suffix == ".ipynb":
            return clean_notebook_content(content)
        return content
    except (UnicodeDecodeError, PermissionError, OSError) as e:
        typer.echo(f"Failed to read {file_path}: {e}", err=True)
        return ""


def get_ignore_spec() -> pathspec.PathSpec:
    spec = pathspec.PathSpec.from_lines("gitwildmatch", EXCLUDE_PATTERNS)
    return spec


def collect_files(root_dir: Path) -> list[FileInfo]:
    files = []
    ignore_spec = get_ignore_spec()

    for path in root_dir.rglob("*"):
        if ignore_spec.match_file(str(path)):
            continue
        if not path.is_file():
            continue
        try:
            content = read_file_content(path)
            line_count = len(content.splitlines()) if content else 0
            if line_count > 0:
                files.append(
                    FileInfo(line_count=line_count, path=path, content=content)
                )
        except Exception as e:
            typer.echo(f"Warning: Couldn't process {path}: {e}", err=True)
    return sorted(files, reverse=True)


def write_output_file(files: list[FileInfo], output_path: Path, root_dir: Path) -> None:
    files = sorted(files, key=lambda file_info: file_info.path)
    with output_path.open("w", encoding="utf-8") as out:
        out.write("<files>\n")
        for file_info in files:
            relative_path = file_info.path.relative_to(root_dir)
            content = read_file_content(file_info.path)
            if content:
                file_block = (
                    f"<file>\n"
                    f"  <path>{relative_path}</path>\n"
                    f"  <content>\n{textwrap.indent(content, '    ')}\n"
                    f"  </content>\n"
                    f"</file>\n"
                )
                out.write(textwrap.indent(file_block, "  "))
        out.write("</files>")


def main(
    directory: str = ".",
    output: str | None = None,
    dry: Annotated[
        bool, typer.Option(help="Lists the files that will be included.")
    ] = False,
) -> None:
    root_dir = Path(directory)
    if not root_dir.is_dir():
        typer.echo(f"{root_dir} is not a directory")
        raise typer.Exit(code=1)

    if output is None:
        output = get_default_output_path(root_dir)

    files = collect_files(root_dir)
    total_lines = sum(file_info.line_count for file_info in files)

    if dry:
        typer.echo("Dry run, listing files that would be included:\n")
        for file_info in files:
            typer.echo(file_info)
        typer.echo(f"\nTotal lines: {total_lines}")
        typer.echo(f"Total files: {len(files)}")
        typer.echo(f"Output file: {output}")
        return
    else:
        typer.echo(f"Writing {len(files)} files with {total_lines} lines to {output}")
        write_output_file(files, Path(output), root_dir)


if __name__ == "__main__":
    typer.run(main)
