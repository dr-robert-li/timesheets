#!/usr/bin/env python3
"""
Initialization helper script for Timing to Clockify sync.
Sets up the .env file with Clockify API key and default project.
"""

import os
import sys

ENV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")


def load_env():
    """Load existing .env file into a dictionary."""
    env_vars = {}
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip()
    return env_vars


def save_env(env_vars):
    """Save environment variables to .env file."""
    with open(ENV_FILE, "w", encoding="utf-8") as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")
    print(f"\nConfiguration saved to {ENV_FILE}")


def prompt_api_key(env_vars):
    """Prompt user for Clockify API key."""
    existing_key = env_vars.get("CLOCKIFY_API_KEY", "")

    if existing_key:
        masked_key = existing_key[:8] + "..." + existing_key[-4:] if len(existing_key) > 12 else "****"
        print(f"\nExisting Clockify API key found: {masked_key}")
        overwrite = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if overwrite != "y":
            print("Keeping existing API key.")
            return existing_key

    print("\nEnter your Clockify API key.")
    print("(You can find this at: https://app.clockify.me/user/preferences#advanced)")
    new_key = input("API Key: ").strip()

    if not new_key:
        if existing_key:
            print("No key entered. Keeping existing key.")
            return existing_key
        else:
            print("Error: API key is required.")
            sys.exit(1)

    return new_key


def prompt_default_project(env_vars):
    """Prompt user for default Clockify project name."""
    existing_project = env_vars.get("CLOCKIFY_DEFAULT_PROJECT", "")

    print(f"\nDefault Clockify Project for time entries.")
    if existing_project:
        print(f"Current default: {existing_project}")
        new_project = input(f"Enter new project name (or press Enter to keep '{existing_project}'): ").strip()
        if not new_project:
            return existing_project
        return new_project
    else:
        new_project = input("Enter default project name (e.g., 'GTM Engineering'): ").strip()
        if not new_project:
            print("No project entered. Using 'GTM Engineering' as default.")
            return "GTM Engineering"
        return new_project


def main():
    print("=" * 50)
    print("Timing to Clockify Sync - Configuration Setup")
    print("=" * 50)

    # Load existing config
    env_vars = load_env()

    # Prompt for API key
    env_vars["CLOCKIFY_API_KEY"] = prompt_api_key(env_vars)

    # Prompt for default project
    env_vars["CLOCKIFY_DEFAULT_PROJECT"] = prompt_default_project(env_vars)

    # Save configuration
    save_env(env_vars)

    print("\nConfiguration complete!")
    print(f"  API Key: {env_vars['CLOCKIFY_API_KEY'][:8]}...{env_vars['CLOCKIFY_API_KEY'][-4:]}")
    print(f"  Default Project: {env_vars['CLOCKIFY_DEFAULT_PROJECT']}")
    print("\nYou can now run: python3 sync_timing.py")


if __name__ == "__main__":
    main()
