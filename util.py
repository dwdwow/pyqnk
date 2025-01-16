import hashlib
import json


def get_instruction_discriminator(instruction_name: str, scope: str = "global"):
    preimage = f"{scope}:{instruction_name}"
    hash_bytes = hashlib.sha256(preimage.encode()).digest()
    discriminator = hash_bytes[:8]
    return discriminator


def create_discriminators(method_names: list[str], scope: str = "global") -> dict[str, dict[str, str]]:
    result = {"func_disc": {}, "disc_func": {}}
    for method_name in method_names:
        disc = get_instruction_discriminator(method_name, scope).hex()
        result["func_disc"][method_name] = disc
        result["disc_func"][disc] = method_name
    return result


def create_discriminators_json_locally():
    result = {}
    with open("prog_func.json", "r") as f:
        prog_func = json.load(f)
    for prog_name, info in prog_func.items():
        methods = info["methods"]
        num_bytes = info["num_bytes"]
        if num_bytes == 8: 
            discriminators = create_discriminators(methods)
        else:
            discriminators = {"func_disc": {}, "disc_func": {}}
            for method in methods:
                strs = method.split(" ")
                m = strs[0]
                d = strs[1]
                discriminators["func_disc"][m] = d
                discriminators["disc_func"][d] = m
        result[prog_name] = discriminators
    with open("discriminators.json", "w") as f:
        json.dump(result, f)


if __name__ == "__main__":
    create_discriminators_json_locally()