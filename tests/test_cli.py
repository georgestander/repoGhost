import os
import pytest
from repoGhost.cli import valid_source_file, calculate_file_hash, scan_repo

def test_valid_source_file():
    assert valid_source_file("test.py") == True
    assert valid_source_file("test.pyc") == False
    assert valid_source_file(".git/config") == False

def test_calculate_file_hash(tmp_path):
    # Create a temporary file
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")
    
    # Calculate hash
    file_hash = calculate_file_hash(str(test_file))
    assert isinstance(file_hash, str)
    assert len(file_hash) > 0

def test_scan_repo(tmp_path):
    # Create test files
    (tmp_path / "test.py").write_text("print('hello')")
    (tmp_path / "test.txt").write_text("hello")
    os.makedirs(tmp_path / "__pycache__")
    (tmp_path / "__pycache__" / "test.pyc").write_text("cache")
    
    # Scan repo
    files = scan_repo(str(tmp_path))
    assert len(files) == 1
    assert str(files[0]).endswith("test.py")
