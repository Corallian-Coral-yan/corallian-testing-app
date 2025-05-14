import json
import os

CONFIG_PATH = "config.json"

default_config = {
    "image_folder": "resources",
    "output_folder": "output"
}

if not os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "w") as f:
        json.dump(default_config, f, indent=2)

with open(CONFIG_PATH) as f:
    cfg = json.load(f)

IMAGE_FOLDER = cfg.get("image_folder", "resources")
OUTPUT_FOLDER = cfg.get("output_folder", "output")

# Make sure folders exist
os.makedirs(IMAGE_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
