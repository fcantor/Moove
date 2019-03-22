#!/usr/bin/env python3
'''Module for FileStorage'''
import json
import os

list_count = 0;

def save(dict):
        """ Serialized objects into __file_path """
        with open("file.json", mode='w', encoding='utf-8') as f:
            json.dump(dict, f)

def deserialize():
    """ Deserialized json into python objects if file is found """
    try:
        with open("file.json", "r", encoding="utf-8") as f:
            obj = json.load(f)
        return (obj)
    except FileNotFoundError:
        pass