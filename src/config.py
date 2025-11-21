import json

def load_config():
    with open("config.json") as f:
        return json.load(f)

config = load_config()


if __name__ == "__main__":
    print(config)