import json

def txt_to_json(txt_file, json_file):
    data = {}
    with open(txt_file, 'r') as f:
        for line in f:
            elements = line.split()
            key = elements[0]
            values = {elements[i].capitalize(): int(elements[i+1]) for i in range(1, len(elements), 2)}
            data[key] = values
            some_test = 123

    with open(json_file, 'w') as f:
        json.dump(data, f, indent=4)

# Użyj funkcji
txt_to_json('input.txt', 'output.json')