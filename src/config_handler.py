#%%
import json
import yaml
#%%
def read_json(json_file):
    """
    Reads the paths from a json file.
    args:
        json_file: json file to read from
    returns: dictionary of paths
    """
    with open(json_file, 'r') as f:
        paths = json.load(f)
    return paths

def write_json(json_file, dict_to_write):
    """
    Writes the paths to a json file.
    args:
        json_file: json file to write to
        dict_to_write: dictionary to write
    """
    with open(json_file, 'w') as f:
        json.dump(dict_to_write, f, indent=4)

def read_yaml(yaml_file):
    """
    Reads the paths from a yaml file.
    args:
        yaml_file: yaml file to read from
    returns: dictionary of paths
    """
    with open(yaml_file, 'r') as f:
        paths = yaml.safe_load(f)
    return paths

def write_yaml(yaml_file, dict_to_write):
    """
    Writes the paths to a yaml file.
    args:
        yaml_file: yaml file to write to
        dict_to_write: dictionary to write
    """
    with open(yaml_file, 'w') as f:
        yaml.dump(dict_to_write, f, indent=4)
    

def set_entry(dictionary, key, value):
    """
    Adds a key-value pair to the dictionary.
    args:
        dictionary: dictionary
        key: key to add
        value: value to add
    returns: updated paths dictionary
    """
    dictionary[key] = value
    return dictionary

def get_entry(dictionary: dict, name: str) -> dict:
    """ 
    Returns the entry for the given name.
    args:
        config: dictionary to get entry from
        name: name of entry
    returns: entry for the given name
    """
    if name in dictionary:
        entry = dictionary[name]
    else:
        raise KeyError(f"Entry '{name}' not found in dictionary.")
    return entry