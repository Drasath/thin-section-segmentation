import json

from modifiers import *

def load(data: str):

    json_data = json.loads(data)
    value = json.loads(json_data['values'])
    modifier = value['modifier']
    parameters = value['parameters']

    modifiers[modifier](parameters)

    children = json_data['children']

    return image, segments, settings 

if __name__ == '__main__': 
    with open('data.json', 'r') as f:
        json_data = f.read()

    image, segments, settings = load(json_data)
    print(image)
    print(segments)
    print(settings)