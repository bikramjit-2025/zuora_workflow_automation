#!/usr/bin/env python3
"""
JSON File Comparison Tool

This script compares two JSON files and reports differences in a clear,
human-readable format. It categorizes differences into additions, deletions,
and changes.

Author: AI Assistant
Dependencies: deepdiff (install with: pip install deepdiff)
"""

import json
import sys
import os
import re
from typing import Dict, Any, List, Tuple
from deepdiff import DeepDiff
from deepdiff.diff import DiffLevel
from datetime import datetime


def print_usage() -> None:
    """
    Print usage information for the script.
    """
    print("Usage: python json_diff.py <file1.json> <file2.json>")
    print("\nDescription:")
    print("  Compare two JSON files and report differences in a structured format.")
    print("\nExample:")
    print("  python json_diff.py sample1.json sample2.json")
    print("\nDependencies:")
    print("  pip install deepdiff")


def remove_excluded_fields(data: Dict[str, Any], excluded_fields: List[str]) -> Dict[str, Any]:
    """
    Recursively remove specified fields from JSON data.
    
    Args:
        data: The JSON data to process
        excluded_fields: List of field names to remove
        
    Returns:
        Dict[str, Any]: JSON data with excluded fields removed
    """
    if isinstance(data, dict):
        return {
            k: remove_excluded_fields(v, excluded_fields)
            for k, v in data.items()
            if k not in excluded_fields
        }
    elif isinstance(data, list):
        return [remove_excluded_fields(item, excluded_fields) for item in data]
    else:
        return data


def restore_excluded_fields(value: Any, path: str, original_data: Dict[str, Any], excluded_fields: List[str]) -> Any:
    """
    Restore excluded fields from original data into the value.
    
    Args:
        value: The current value (potentially missing excluded fields)
        path: The path to the value in the JSON structure
        original_data: The original JSON data with all fields
        excluded_fields: List of field names that were excluded
        
    Returns:
        Any: The value with excluded fields restored
    """
    if not isinstance(value, dict) or not original_data:
        return value
    
    # Parse the path to get the location in original data
    try:
        # Convert path like "root['tasks'][0]" to access original data
        path_parts = path.replace("root", "").strip("[]")
        if not path_parts:
            return value
            
        # Navigate to the location in original data
        current = original_data
        for part in path_parts.split("]["):
            part = part.strip("'\"")
            if part.isdigit():
                current = current[int(part)]
            else:
                current = current[part]
        
        # If current is a dict, restore excluded fields
        if isinstance(current, dict):
            restored_value = value.copy()
            for field in excluded_fields:
                if field in current:
                    restored_value[field] = current[field]
            return restored_value
            
    except (KeyError, IndexError, ValueError):
        # If path parsing fails, return original value
        pass
    
    return value


def load_json_file(file_path: str) -> Dict[str, Any]:
    """
    Load and parse a JSON file.
    
    Args:
        file_path (str): Path to the JSON file to load
        
    Returns:
        Dict[str, Any]: Parsed JSON data as a Python dictionary
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
        PermissionError: If the file cannot be read due to permissions
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Error: File '{file_path}' not found.")
        
        # Check if file is readable
        if not os.access(file_path, os.R_OK):
            raise PermissionError(f"Error: File '{file_path}' is not readable.")
        
        # Load and parse JSON
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data
            
    except FileNotFoundError as e:
        print(f"❌ {e}")
        sys.exit(1)
    except PermissionError as e:
        print(f"❌ {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in file '{file_path}' at line {e.lineno}, column {e.colno}: {e.msg}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error reading file '{file_path}': {e}")
        sys.exit(1)


def format_path(path: str) -> str:
    """
    Format a deepdiff path for better readability.
    
    Args:
        path (str): The path string from deepdiff
        
    Returns:
        str: Formatted path for display
    """
    # Remove 'root' prefix and format the path
    if path.startswith("root"):
        path = path[4:]  # Remove 'root'
    
    # Replace array indices with more readable format
    import re
    path = re.sub(r"\[(\d+)\]", r"[\1]", path)
    
    return path if path else "root"


def export_diff_to_json(diff, file1_path: str, file2_path: str, json1_original: Dict[str, Any] = None, json2_original: Dict[str, Any] = None) -> None:
    """
    Export the diff object to a JSON file for programmatic access.
    
    Args:
        diff: The DeepDiff object containing all differences (tuple for tree view)
        file1_path (str): Path to the first JSON file
        file2_path (str): Path to the second JSON file
    """
    # Create a structured diff export object
    diff_export = {
        "metadata": {
            "comparison_timestamp": datetime.now().isoformat(),
            "file1": file1_path,
            "file2": file2_path,
            "view_type": "tree"
        },
        "differences": {}
    }
    
    # Handle TreeResult object from DeepDiff tree view
    if hasattr(diff, '__iter__') and hasattr(diff, 'items'):
        # Set has_differences flag - check if there are any changes
        has_changes = any(len(changes) > 0 for changes in diff.values())
        diff_export["metadata"]["has_differences"] = has_changes
        
        # Convert TreeResult to a serializable format
        tree_dict = {}
        
        # Handle different types of changes in the tree
        for change_type, changes in diff.items():
            tree_dict[change_type] = []
            for change in changes:
                # Convert each change to a dictionary, handling NotPresent objects
                old_value = getattr(change, 't1', None)
                new_value = getattr(change, 't2', None)
                
                # Convert NotPresent objects to a string representation
                if hasattr(old_value, '__class__') and 'NotPresent' in str(type(old_value)):
                    old_value = "not present"
                if hasattr(new_value, '__class__') and 'NotPresent' in str(type(new_value)):
                    new_value = "not present"
                
                change_dict = {
                    "path": str(change.path()),
                    "old_value": old_value,
                    "new_value": new_value
                }
                tree_dict[change_type].append(change_dict)
        
        # Store the tree view structure
        diff_export["differences"] = tree_dict
        
        # Add summary statistics
        total_changes = sum(len(changes) for changes in tree_dict.values())
        diff_export["summary"] = {
            "total_changes": total_changes,
            "change_types": {change_type: len(changes) for change_type, changes in tree_dict.items()}
        }
        
    else:
        # Fallback for unexpected format
        diff_export["metadata"]["has_differences"] = False
        diff_export["differences"] = {"error": "Unexpected diff format"}
        diff_export["summary"] = {"total_changes": 0}
    
    # Write to JSON file
    output_file = "diff_export.json"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(diff_export, f, indent=2, ensure_ascii=False)
        print(f"📄 Diff exported to: {output_file}")
    except Exception as e:
        print(f"⚠️  Warning: Could not export diff to JSON file: {e}")


def print_differences(diff) -> None:
    """
    Print the differences in a structured, human-readable format.
    
    Args:
        diff: The DeepDiff object containing all differences (tuple for tree view)
    """
    print("=" * 80)
    print("📊 JSON COMPARISON RESULTS (TREE VIEW)")
    print("=" * 80)
    
    # Handle TreeResult object from DeepDiff tree view
    if hasattr(diff, '__iter__') and hasattr(diff, 'items'):
        # Check if there are any differences
        if not diff:
            print("✅ No differences found. The JSON files are identical.")
            return
        
        # Convert TreeResult to a serializable format
        tree_dict = {}
        
        # Handle different types of changes in the tree
        for change_type, changes in diff.items():
            tree_dict[change_type] = []
            for change in changes:
                # Convert each change to a dictionary, handling NotPresent objects
                old_value = getattr(change, 't1', None)
                new_value = getattr(change, 't2', None)
                
                # Convert NotPresent objects to a string representation
                if hasattr(old_value, '__class__') and 'NotPresent' in str(type(old_value)):
                    old_value = "not present"
                if hasattr(new_value, '__class__') and 'NotPresent' in str(type(new_value)):
                    new_value = "not present"
                
                change_dict = {
                    "path": str(change.path()),
                    "old_value": old_value,
                    "new_value": new_value
                }
                tree_dict[change_type].append(change_dict)
        
        # Display the tree structure
        print("\n🌳 TREE VIEW STRUCTURE:")
        print("-" * 60)
        #print(json.dumps(tree_dict, indent=4, sort_keys=True, ensure_ascii=False))
        print()
        
        # Calculate summary
        total_changes = sum(len(changes) for changes in tree_dict.values())
        
    else:
        # Fallback for unexpected format
        print("⚠️  Warning: Unexpected tree view format.")
        print(f"⚠️  Actual type: {type(diff)}")
        return
    
    # Print summary
    print("=" * 80)
    print(f"📈 SUMMARY: {total_changes} total changes found")
    print("=" * 80)

def print_excluded_regex(excluded_paths: dict,json1: dict) -> None:
    """
    Print the excluded regex paths.
    """
    regex_paths = excluded_paths['excluded_regex_paths']
    print(f"   Excluded regex paths: {regex_paths}")
    try:
        regex_patterns = [re.compile(pattern) for pattern in regex_paths]
        print(f"   Regex patterns: {regex_patterns}")
    except re.error as e:
        print(f"   ❌ Regex compilation error: {e}")

    for regex in regex_patterns:
        print(f"   Regex: {regex}")
        for item in json1:
            print(f"   Item before regex: {item}")
            if re.match(regex, item):
                print(f"   {item}")


def compare_json_files(file1_path: str, file2_path: str, exclusion_file_path: str) -> None:
    """
    Compare two JSON files and display the differences.
    
    Args:
        file1_path (str): Path to the first JSON file
        file2_path (str): Path to the second JSON file
    """
    print(f"🔍 Comparing JSON files:")
    print(f"   File 1: {file1_path}")
    print(f"   File 2: {file2_path}")
    print(f"   Exclusion file: {exclusion_file_path}")
    print()
    
    # Load both JSON files
    try:
        json1 = load_json_file(file1_path)
        json2 = load_json_file(file2_path)
        excluded_paths = load_json_file(exclusion_file_path)
        #print_excluded_regex(excluded_paths,json1);
        
        # Create copies for comparison while keeping originals intact
        excluded_fields = ['id','task_id','files','created_tags']
        json1_copy = remove_excluded_fields(json1, excluded_fields)
        json2_copy = remove_excluded_fields(json2, excluded_fields)
        
    except Exception:
        # Error handling is done in load_json_file
        return
    
    # Perform the comparison using deepdiff
    try:
        diff = DeepDiff(
            json1_copy, 
            json2_copy, 
            ignore_order=True,
            exclude_paths=excluded_paths["excluded_paths"],
            exclude_regex_paths=excluded_paths["excluded_regex_paths"],
        )  
        
        # Get tree view representation
        tree_view = diff.tree
        
        # Display the results
        print_differences(tree_view)
        
        # Export diff to JSON file
        export_diff_to_json(tree_view, file1_path, file2_path, json1, json2)
        
    except Exception as e:
        print(f"❌ Error during comparison: {e}")
        sys.exit(1)


def main() -> None:
    """
    Main function to handle command-line arguments and initiate comparison.
    """
    # Check for correct number of arguments
    if len(sys.argv) != 4:
        print("❌ Error: Incorrect number of arguments.")
        print()
        print_usage()
        sys.exit(1)
    
    # Extract file paths
    file1_path = sys.argv[1]
    file2_path = sys.argv[2]
    exclusion_file_path = sys.argv[3]
    
    # Validate that both arguments are provided
    if not file1_path or not file2_path or not exclusion_file_path: 
        print("❌ Error: All the three file paths must be provided.")
        print()
        print_usage()
        sys.exit(1)
    
    # Perform the comparison
    compare_json_files(file1_path, file2_path,exclusion_file_path)


if __name__ == "__main__":
    main()
