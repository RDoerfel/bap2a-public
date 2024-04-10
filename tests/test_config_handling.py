from src import config_handler
import json
import pytest
import os
import tempfile
import yaml 

TEST_NAME_JSON = 'test_file.json'
TEST_NAME_YAML = 'test_file.yml'
TEST_DICT = {'PATHS':{'Test1':1, 'Test2':2}}

def setup_module():
    with open(TEST_NAME_JSON, 'w') as f:
        json.dump(TEST_DICT, f, indent=4)
    with open(TEST_NAME_YAML, 'w') as f:
        yaml.dump(TEST_DICT, f, indent=4)
    

def teardown_module():
    os.remove(TEST_NAME_JSON)
    os.remove(TEST_NAME_YAML)

def test_read_json():
    json = config_handler.read_json(TEST_NAME_JSON)
    assert json['PATHS']['Test1'] == 1
    assert json['PATHS']['Test2'] == 2

def test_write_json():
    config_handler.write_json(TEST_NAME_JSON, {'Test3':3})
    json = config_handler.read_json(TEST_NAME_JSON)
    assert json['Test3'] == 3

def test_read_yaml():
    yaml_dict = config_handler.read_yaml(TEST_NAME_YAML)
    assert yaml_dict['PATHS']['Test1'] == 1
    assert yaml_dict['PATHS']['Test2'] == 2

def test_write_yaml():
    config_handler.write_yaml(TEST_NAME_YAML, {'Test3':3})
    yaml_dict = config_handler.read_yaml(TEST_NAME_YAML)
    assert yaml_dict['Test3'] == 3

def test_set_entry():
    test_dict = {'Test1':1, 'Test2':2}    
    config_handler.set_entry(test_dict, 'Test4', 4)
    assert test_dict['Test1'] == 1
    assert test_dict['Test2'] == 2
    assert test_dict['Test4'] == 4

def test_get_entry():
    test_dict = {'Test1':1, 'Test2':2}
    assert config_handler.get_entry(test_dict, 'Test1') == 1
    assert config_handler.get_entry(test_dict, 'Test2') == 2

def test_get_entry_error():
    test_dict = {'Test1':1, 'Test2':2}
    with pytest.raises(KeyError):
        config_handler.get_entry(test_dict, 'Test3')



    