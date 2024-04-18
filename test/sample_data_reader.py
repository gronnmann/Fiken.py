import json
import os


def get_sample_from_json(filename: str) -> dict:
    with open(os.path.join('test/sample_model_responses', f"{filename}.json"), 'r') as f:
        return json.load(f)