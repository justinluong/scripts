# to-doc

A command-line utility to collect files from a directory into a single document for LLM context.

## Usage

```
to-doc [DIRECTORY] [OPTIONS]
```

Options:
- `--output TEXT`: Custom output file path
- `--dry`: Lists files that would be included without creating output

If no output path is specified, it uses the directory name to create `{directory-name}-llm.txt`.

## Customization

Create a `.ignore` file in the same directory as `to_doc.py` to specify patterns for files to exclude.