# unzone

A simple, safe utility to find and delete `Zone.Identifier` files.

## What are Zone.Identifier files?

When files are downloaded from the internet or transferred from other security zones in Windows, the OS creates hidden `:Zone.Identifier` alternate data stream files. When these files are copied to Linux or Mac systems (or accessed via WSL), they appear as separate files with the suffix `:Zone.Identifier`.

This tool helps clean them up.

## Features

- ✅ **Safe by default** - Non-recursive by default, requires `-r` flag for subdirectories
- ✅ **Confirmation prompts** - Always asks for confirmation before deletion (configurable)
- ✅ **Configurable** - Set your preferred behavior globally
- ✅ **Cross-platform** - Works on Windows, Linux, and macOS
- ✅ **No dependencies** - Uses only Python standard library
- ✅ **Verbose mode** - See exactly what's being processed
- ✅ **Smart error handling** - Handles permission issues gracefully

## Installation

```bash
pip install unzone
```

## Usage

### Basic usage (interactive)
```bash
# Scan current directory only (non-recursive)
unzone

# Scan current directory and all subdirectories
unzone -r

# Scan specific directory (non-recursive)
unzone /path/to/directory

# Recursively scan specific directory
unzone -r /path/to/directory

# See detailed output
unzone --verbose
```

### Configuration
```bash
# Configure default behavior (one-time setup, runs first time you use unzone)
unzone --configure
```

This lets you choose whether to always ask for confirmation or auto-delete. Your choice is saved globally.

### Command-line flags

```bash
# Recursive scan
unzone -r
unzone --recursive

# Force deletion without confirmation (for scripts)
unzone --force

# Force confirmation prompt (override config when set to automatically delete)
unzone --confirm

# Verbose output
unzone --verbose

# Show version
unzone --version

# Show help
unzone --help
```

### Examples

```bash
# Clean current directory only
unzone

# Clean current directory and all subdirectories
unzone -r

# Clean Downloads folder (non-recursive)
unzone ~/Downloads

# Recursively clean Downloads folder
unzone -r ~/Downloads

# Automated cleanup in a script (recursive)
unzone -r ~/Downloads --force

# Override auto-delete config for this run
unzone ~/Downloads --confirm
```

## Configuration File

Configuration is stored at:
- **Linux/Mac**: `~/.config/unzone/config.json`
- **Windows**: `%LOCALAPPDATA%\unzone\config.json`

You can edit this file manually or use `unzone --configure`.

## How It Works

1. Scans the specified directory (use `-r` for recursive subdirectory scanning)
2. Finds all files ending with `Zone.Identifier`
3. Asks for confirmation (unless configured otherwise or `--force` is used)
4. Deletes the files and reports results

## Safety Features

- **Non-recursive by default** - Only scans the current directory unless `-r` is specified
- **Confirmation prompts** - Won't delete anything without your approval (by default)
- **Graceful error handling** - Continues processing even if some files can't be deleted
- **Clear reporting** - Shows exactly what was deleted and any errors
- **Targeted deletion** - Only removes files ending with `Zone.Identifier`

## License

MIT License - See LICENSE file for details

## Contributing

Issues and pull requests welcome at https://github.com/spenquatch/unzone
