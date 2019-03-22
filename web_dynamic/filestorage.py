#!/usr/bin/env python3
'''Module for FileStorage'''
import json
import os

list_count = 0;

def save(dict):
        """ Serialized objects into __file_path """
        with open('file.json', mode='a', encoding='utf-8') as file:
            json.dump(dict, file)

def deserialize():
    """ Deserialized json into python objects if file is found """
    try:
        with open("file.json", "r", encoding="utf-8") as handle:
            data = [json.loads(line) for line in handle]
        return (data)
    except FileNotFoundError:
        pass