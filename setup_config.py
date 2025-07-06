import os
import sys
import json
import base64
import ipaddress
import getpass
import logging
import platform
from typing import Any, Dict, Optional, Callable

CONFIG_PATH = os.path.join("shared", "config.json")

# Set up basic logging
logging.basicConfig(
    filename="setup_config.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s"
)

def is_valid_port(port: str) -> bool:
    """Check if the port is a valid integer between 1 and 65535."""
    return port.isdigit() and 1 <= int(port) <= 65535

def is_valid_ip(ip: str) -> bool:
    """Validate if the input string is a valid IP address."""
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def is_valid_base64(s: str) -> bool:
    """Check if the string is valid base64."""
    try:
        base64.b64decode(s, validate=True)
        return True
    except (base64.binascii.Error, ValueError):
        return False

def decoded_length(s: str) -> int:
    """Return the length of the decoded base64 string, or -1 if invalid."""
    try:
        return len(base64.b64decode(s, validate=True))
    except Exception:
        return -1

def prompt_field(
    prompt: str,
    validate_fn: Callable[[str], bool],
    error_msg: str,
    default: Optional[str] = None,
    is_secret: bool = False
) -> str:
    """Prompt the user for input, validate, and return the value."""
    while True:
        if default:
            msg = f"{prompt} [{default}]: "
        else:
            msg = f"{prompt}: "
        try:
            value = getpass.getpass(msg) if is_secret else input(msg)
        except KeyboardInterrupt:
            print("\n❌ Input cancelled by user. Exiting.")
            sys.exit(1)

        value = value.strip() or (default or "")
        if validate_fn(value):
            return value
        print(error_msg)

def load_existing_config(path: str) -> Optional[Dict[str, Any]]:
    """Load existing configuration from the given path, if available."""
    if os.path.isfile(path):
        try:
            with open(path, "r") as f:
                config = json.load(f)
            logging.info(f"Loaded existing config from {path}")
            return config
        except Exception as e:
            logging.error(f"Failed to load existing config: {e}")
    return None

def prompt_for_config(existing: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Prompt user for all config fields, using existing values as defaults."""
    print("🔧 Let's configure your peer node setup:\n")

    local_port = prompt_field(
        "Enter local port (1–65535)",
        is_valid_port,
        "❌ Invalid port. Please enter a number between 1 and 65535.",
        str(existing.get("local_port")) if existing and existing.get("local_port") else None
    )

    peer_ip = prompt_field(
        "Enter peer IP (e.g., 192.168.0.101)",
        is_valid_ip,
        "❌ Invalid IP address format.",
        existing.get("peer_ip") if existing and existing.get("peer_ip") else None
    )

    peer_port = prompt_field(
        "Enter peer port (1–65535)",
        is_valid_port,
        "❌ Invalid port. Please enter a number between 1 and 65535.",
        str(existing.get("peer_port")) if existing and existing.get("peer_port") else None
    )

    def valid_aes_key(s: str) -> bool:
        return is_valid_base64(s) and decoded_length(s) in (16, 24, 32)

    aes_key = prompt_field(
        "Enter AES key (base64-encoded, 16/24/32 bytes)",
        valid_aes_key,
        "❌ Invalid AES key. Must be base64-encoded and 16, 24, or 32 bytes after decoding.",
        existing.get("aes_key") if existing and existing.get("aes_key") else None,
        is_secret=True
    )

    def valid_iv(s: str) -> bool:
        return is_valid_base64(s) and decoded_length(s) == 16

    iv = prompt_field(
        "Enter IV (base64-encoded, 16 bytes)",
        valid_iv,
        "❌ Invalid IV. Must be base64-encoded and 16 bytes after decoding.",
        existing.get("iv") if existing and existing.get("iv") else None,
        is_secret=True
    )

    return {
        "local_port": int(local_port),
        "peer_ip": peer_ip,
        "peer_port": int(peer_port),
        "aes_key": aes_key,
        "iv": iv
    }

def save_config(config: Dict[str, Any], path: str = CONFIG_PATH) -> None:
    """Save the configuration to a JSON file, setting secure permissions."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        with open(path, "w") as f:
            json.dump(config, f, indent=4)

        # Set file permissions to owner read/write only (Unix)
        if platform.system() != "Windows":
            try:
                os.chmod(path, 0o600)
            except Exception as e:
                logging.warning(f"Could not set file permissions for {path}: {e}")
        else:
            logging.info("Running on Windows: skipping file permission setting")

        logging.info(f"Configuration saved successfully to {path}")
        print(f"\n✅ Configuration saved successfully to {path}")
    except Exception as e:
        logging.error(f"Failed to save configuration: {e}")
        print(f"\n❌ Failed to save configuration: {e}")
        print("See setup_config.log for details.")
        sys.exit(1)

def main() -> None:
    """Main entry point for the configuration script."""
    existing = load_existing_config(CONFIG_PATH)
    if existing:
        print(f"⚠️  Existing config found at {CONFIG_PATH}.")
        confirm = input("Overwrite? (y/N): ").strip().lower()
        if confirm != 'y':
            logging.info("User aborted configuration overwrite.")
            print("❌ Aborted.")
            sys.exit(0)

    config = prompt_for_config(existing)

    # Show preview without sensitive fields, but with key/IV lengths
    print("\n🔍 Preview of configuration:")
    safe_config = {}
    for k, v in config.items():
        if k == "aes_key":
            safe_config[k] = f"*** (base64, {decoded_length(v)} bytes)"
        elif k == "iv":
            safe_config[k] = f"*** (base64, {decoded_length(v)} bytes)"
        else:
            safe_config[k] = v
    print(json.dumps(safe_config, indent=4))

    confirm_save = input("💾 Save this configuration? (Y/n): ").strip().lower()
    if confirm_save == 'n':
        logging.info("User cancelled save after preview.")
        print("❌ Save cancelled.")
        sys.exit(0)

    save_config(config)

if __name__ == "__main__":
    main()
