import os
import yaml


def load_prompt(filename, context: str = ""):
    """Load a prompt from a YAML file."""
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    prompt_path = os.path.join(script_dir, "prompts", filename)

    try:
        with open(prompt_path, "r") as file:
            prompt_data = yaml.safe_load(file)
            instructions = prompt_data.get("instructions", "")

            if context:
                instructions = instructions.format(context=context)

            return instructions
    except (FileNotFoundError, yaml.YAMLError) as e:
        print(f"Error loading prompt file {filename}: {e}")
        return ""
