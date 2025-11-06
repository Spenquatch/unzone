#!/usr/bin/env python3
"""
Script to find and delete all Zone.Identifier files in the current directory
and all subdirectories.

Zone.Identifier files are created by Windows when files are downloaded from
the internet or transferred from other zones.
"""

import argparse
import logging
import os
import sys
from pathlib import Path
import json

__version__ = "0.1.0"
ZONE_IDENTIFIER_SUFFIX = "Zone.Identifier"

# Determine config location based on platform
if sys.platform == "win32":
    # Windows: use AppData/Local
    CONFIG_DIR = Path(os.getenv("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "unzone"
else:
    # Linux/Mac: use XDG config directory
    CONFIG_DIR = Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config")) / "unzone"

CONFIG_FILE = CONFIG_DIR / "config.json"

# Setup logging
logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(levelname)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def find_zone_identifier_files(start_path, recursive=False):
    """
    Find all files ending with 'Zone.Identifier' starting from start_path.

    Args:
        start_path: Directory to start searching from
        recursive: If True, search subdirectories recursively

    Returns:
        List of file paths
    """
    found_files = []

    if recursive:
        logger.info(f"Scanning directory recursively: {os.path.abspath(start_path)}")
        for root, _, files in os.walk(start_path):
            for filename in files:
                if filename.endswith(ZONE_IDENTIFIER_SUFFIX):
                    filepath = os.path.join(root, filename)
                    found_files.append(filepath)
                    logger.debug(f"Found: {filepath}")
    else:
        logger.info(f"Scanning directory (non-recursive): {os.path.abspath(start_path)}")
        try:
            for filename in os.listdir(start_path):
                filepath = os.path.join(start_path, filename)
                if os.path.isfile(filepath) and filename.endswith(ZONE_IDENTIFIER_SUFFIX):
                    found_files.append(filepath)
                    logger.debug(f"Found: {filepath}")
        except OSError as e:
            logger.error(f"Error reading directory: {e}")

    return found_files


def load_config():
    """
    Load configuration from config file.

    Returns:
        dict: Configuration dictionary with default values if file doesn't exist
    """
    default_config = {
        "auto_delete": False,  # Whether to skip confirmation by default
    }

    if not CONFIG_FILE.exists():
        return default_config

    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            # Merge with defaults in case new config options are added
            return {**default_config, **config}
    except (json.JSONDecodeError, IOError) as e:
        logger.warning(f"Error reading config file: {e}. Using defaults.")
        return default_config


def save_config(config):
    """
    Save configuration to config file.

    Args:
        config: Configuration dictionary to save
    """
    try:
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info(f"Configuration saved to {CONFIG_FILE}")
    except IOError as e:
        logger.error(f"Error saving config file: {e}")


def configure_interactive(first_run=False):
    """
    Interactive configuration setup.

    Args:
        first_run: If True, shows a welcome message for first-time users
    """
    if first_run:
        print("\n" + "=" * 60)
        print("Welcome to unzone!")
        print("=" * 60)
        print("\nLooks like this is your first time running unzone.")
        print("Let's set up your preferences (you can change these anytime")
        print("by running: unzone --configure)\n")
    else:
        print("\n" + "=" * 60)
        print("unzone - Configuration")
        print("=" * 60)
        print("\nYou can configure the default behavior of this tool.")
        print("These settings will be saved and used for future runs.\n")

    print("How it works:")
    print("  • If you choose 'Yes': Files are deleted automatically")
    print("    (use --confirm flag to force a prompt when needed)")
    print("  • If you choose 'No': You'll be asked before each deletion")
    print("    (use --force flag to skip the prompt when needed)")
    print("\n  Note: Command-line flags always override this setting\n")

    config = load_config()

    try:
        response = input("Always delete without asking for confirmation? [y/N]: ")
        config["auto_delete"] = response.lower() == 'y'

        save_config(config)

        print("\nConfiguration complete!")
        if config["auto_delete"]:
            print("  → Files will be deleted automatically without prompting")
        else:
            print("  → You will be asked for confirmation before deletion")

        if first_run:
            print("\n" + "=" * 60 + "\n")

        return config

    except (KeyboardInterrupt, EOFError):
        print("\n\nConfiguration cancelled.")
        if first_run:
            print("Using default: Ask for confirmation before deletion")
            default_config = {"auto_delete": False}
            save_config(default_config)
            return default_config
        else:
            sys.exit(0)


def delete_files(files):
    """
    Delete the specified files.

    Args:
        files: List of file paths to delete

    Returns:
        Tuple of (deleted_count, error_count)
    """
    deleted_count = 0
    error_count = 0

    for filepath in files:
        try:
            os.remove(filepath)
            logger.info(f"✓ Deleted: {filepath}")
            deleted_count += 1
        except PermissionError:
            error_count += 1
            logger.error(f"Permission denied: {filepath}")
        except OSError as e:
            error_count += 1
            logger.error(f"Error deleting {filepath}: {e}")

    return deleted_count, error_count


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description=f"Find and delete '{ZONE_IDENTIFIER_SUFFIX}' files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Scan current directory only
  %(prog)s -r                 # Scan current directory and subdirectories
  %(prog)s /path/to/folder    # Scan specific directory
  %(prog)s -r ~/Downloads     # Recursively scan Downloads
  %(prog)s --force            # Skip confirmation prompt
  %(prog)s --configure        # Change default settings

Configuration:
  Config file location: ~/.config/unzone/config.json (Linux/Mac)
                        %LOCALAPPDATA%/unzone/config.json (Windows)
  Use --configure to set whether confirmation is required by default
        """
    )

    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Directory to scan (defaults to current directory)'
    )
    parser.add_argument(
        '--recursive', '-r',
        action='store_true',
        help='Scan subdirectories recursively'
    )
    parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='Skip confirmation prompt and delete immediately'
    )
    parser.add_argument(
        '--confirm', '-c',
        action='store_true',
        help='Always ask for confirmation (overrides config setting)'
    )
    parser.add_argument(
        '--configure',
        action='store_true',
        help='Configure default behavior (saved globally)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed information during processing'
    )
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )

    args = parser.parse_args()

    # Handle configuration mode
    if args.configure:
        configure_interactive()
        sys.exit(0)

    # Set logging level based on verbose flag
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Check if this is the first run (no config exists)
    is_first_run = not CONFIG_FILE.exists()

    # If first run, run interactive config
    if is_first_run:
        config = configure_interactive(first_run=True)
    else:
        config = load_config()

    # Validate path
    if not os.path.exists(args.path):
        logger.error(f"Path '{args.path}' does not exist")
        sys.exit(1)

    if not os.path.isdir(args.path):
        logger.error(f"Path '{args.path}' is not a directory")
        sys.exit(1)

    # Find all Zone.Identifier files
    found_files = find_zone_identifier_files(args.path, recursive=args.recursive)

    if not found_files:
        logger.info(f"No files ending with '{ZONE_IDENTIFIER_SUFFIX}' found")
        sys.exit(0)

    logger.info(f"Found {len(found_files)} file(s) ending with '{ZONE_IDENTIFIER_SUFFIX}'")

    # Determine whether to ask for confirmation
    # Priority: --force (skip) > --confirm (ask) > config setting
    should_confirm = True
    if args.force:
        should_confirm = False
    elif args.confirm:
        should_confirm = True
    else:
        # Use config setting (auto_delete = True means skip confirmation)
        should_confirm = not config.get("auto_delete", False)

    # Confirmation prompt
    if should_confirm:
        try:
            response = input(f"\nProceed with deleting {len(found_files)} file(s)? [y/N]: ")
            if response.lower() != 'y':
                logger.info("Deletion cancelled by user")
                sys.exit(0)
        except (KeyboardInterrupt, EOFError):
            logger.info("\nDeletion cancelled by user")
            sys.exit(0)

    # Delete files
    logger.info("-" * 60)
    deleted_count, error_count = delete_files(found_files)
    logger.info("-" * 60)

    # Print summary
    logger.info("\nSummary:")
    logger.info(f"  Successfully deleted: {deleted_count} file(s)")

    if error_count > 0:
        logger.warning(f"  Errors encountered: {error_count}")
        sys.exit(1)
    else:
        logger.info("  All operations completed successfully")
        sys.exit(0)


if __name__ == '__main__':
    main()
