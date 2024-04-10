from src.paths import Paths
import os
import pytest
import json

TEST_FILE = 'test_json.json'

def setup_module():
    test_paths = {'PATHS':{'Test1':1, 'Test2':2}}
    with open(TEST_FILE, 'w') as f:
        json.dump(test_paths, f, indent=4)

def teardown_module():
    os.remove(TEST_FILE)

def test_paths_call():
    test_paths = Paths(TEST_FILE)
    assert test_paths('Test1') == 1
    assert test_paths('Test2') == 2

def test_paths_add_path():
    test_paths = Paths(TEST_FILE)
    test_paths.add_path('Test3', 3)
    assert test_paths('Test3') == 3
    assert test_paths('Test1') == 1
    assert test_paths('Test2') == 2

def test_paths_add_path_file():
    test_paths = Paths(TEST_FILE)
    test_paths.add_path('Test4', 4)

    with open(TEST_FILE, 'r') as f:
        test_paths_json = json.load(f)

    assert test_paths_json['PATHS']['Test1'] == 1
    assert test_paths_json['PATHS']['Test2'] == 2
    assert test_paths_json['PATHS']['Test3'] == 3
    assert test_paths_json['PATHS']['Test4'] == 4

