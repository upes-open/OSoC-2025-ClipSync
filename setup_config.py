import json

def get_input(prompt, default=None, validator=None):
    while True:
        user_input = input(f"{prompt}" + (f" [{default}]" if default else "") + ": ")
        if not user_input and default is not None:
            return default
        if validator and not validator(user_input):
            print("❌ Invalid input. Try again.")
            continue
        return user_input

def main():
    print("\n🔧 ClipSync Config Setup\n")

    config = {}
    config["server_ip"] = get_input("Enter server IP", "127.0.0.1")
    config["port"] = int(get_input("Enter port", "5000", lambda x: x.isdigit()))
    config["mode"] = get_input("Enter mode (one-way/bidirectional)", "one-way", lambda x: x in ["one-way", "bidirectional"])

    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)

    print("\n✅ Configuration saved to config.json\n")

if __name__ == "__main__":
    main()
