import requests
import os
import json


def entity_resolve(entity):
    url = "http://113.54.135.70:9001/entity_resolve"
    data = {'entity': entity}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers= headers, data = json.dumps(data)).json()
    entity = response['entity']
    return entity
    



if __name__ == '__main__':
    entity_resolve()