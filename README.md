# K-Systems File Extraction Tool

A comprehensive utility for searching and packaging K-Systems related files into timestamped archives with manifests and checksums.

## Features

- **Smart Search**: Finds files matching 55+ K-Systems related keywords
- **Safe Operation**: Non-destructive, read-only with dry-run mode
- **Comprehensive Output**: Timestamped tar.gz archives with SHA-256 checksums and JSON manifests
- **Configurable**: Custom keywords, directories, and file size limits
- **Cross-Platform**: Works on Linux, macOS, and Windows

## Quick Start

```bash
# Dry run to see what would be extracted
python3 extract_k_systems.py --target /path/to/search --dry-run

# Extract files to a custom output directory
python3 extract_k_systems.py --target /path/to/search --out ./my-export

# Use custom keywords file
python3 extract_k_systems.py --target /path/to/search --keywords-file my-keywords.txt

# Show all options
python3 extract_k_systems.py --help
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--target` / `-t` | Directory to search | `$HOME` |
| `--out` / `-o` | Output folder for archives | `./k-systems-export` |
| `--keywords-file` / `-k` | Custom keywords file (one per line) | Built-in list |
| `--max-file-size` | Maximum file size in bytes | 5GB |
| `--dry-run` | Test mode - scan only, don't copy files | Off |
| `--no-confirm` | Skip confirmation prompts | Off |

## Output

The tool creates:
- Timestamped `tar.gz` archive containing matched files
- SHA-256 checksum file (`.sha256`)
- JSON manifest with file metadata
- JSON summary with extraction statistics

## License

MIT License

---

*Repository: Juanita-Marie — Dedicated to my mother with love* ❤️