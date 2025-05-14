import json
import os


def save_annotations(output_path, annotations):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(annotations, f, indent=2)
    print(f"✅ Annotations saved to {output_path}")


def load_annotations(annotation_path):
    if not os.path.exists(annotation_path):
        return []
    with open(annotation_path, "r") as f:
        return json.load(f)
