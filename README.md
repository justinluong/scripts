# Justin's Scripts

A collection of useful CLI scripts designed to be run with UV with minimal setup.

# Instructions

1. Install UV.

https://docs.astral.sh/uv/getting-started/installation/

2. Add alias to your interactive non-login shell configuration file.

```.zshrc
to-doc() {
  uv run /<absolute-path>/scripts/to-doc/to_doc.py "$@"
}
```

