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


def export_diff_to_json(diff: DeepDiff, file1_path: str, file2_path: str) -> None:
    """
    Export the diff object to a JSON file for programmatic access.
    
    Args:
        diff (DeepDiff): The DeepDiff object containing all differences
        file1_path (str): Path to the first JSON file
        file2_path (str): Path to the second JSON file
    """
    # Create a structured diff export object
    diff_export = {
        "metadata": {
            "comparison_timestamp": datetime.now().isoformat(),
            "file1": file1_path,
            "file2": file2_path,
            "has_differences": bool(diff)
        },
        "differences": {}
    }
    
    # Convert DeepDiff object to a serializable format
    if diff:
        # Create a clean, serializable representation of the diff
        diff_export["differences"] = {}
        
        # Handle dictionary item additions
        if 'dictionary_item_added' in diff:
            diff_export["differences"]["dictionary_item_added"] = list(diff['dictionary_item_added'])
            
        # Handle dictionary item removals
        if 'dictionary_item_removed' in diff:
            diff_export["differences"]["dictionary_item_removed"] = list(diff['dictionary_item_removed'])
            
        # Handle value changes
        if 'values_changed' in diff:
            diff_export["differences"]["values_changed"] = {}
            for path, change_info in diff['values_changed'].items():
                diff_export["differences"]["values_changed"][path] = {
                    "old_value": change_info['old_value'],
                    "new_value": change_info['new_value']
                }
                
        # Handle type changes
        if 'type_changes' in diff:
            diff_export["differences"]["type_changes"] = {}
            for path, change_info in diff['type_changes'].items():
                diff_export["differences"]["type_changes"][path] = {
                    "old_value": change_info['old_value'],
                    "new_value": change_info['new_value'],
                    "old_type": str(type(change_info['old_value']).__name__),
                    "new_type": str(type(change_info['new_value']).__name__)
                }
                
        # Handle iterable item additions
        if 'iterable_item_added' in diff:
            diff_export["differences"]["iterable_item_added"] = {}
            for path, value in diff['iterable_item_added'].items():
                diff_export["differences"]["iterable_item_added"][path] = value
                
        # Handle iterable item removals
        if 'iterable_item_removed' in diff:
            diff_export["differences"]["iterable_item_removed"] = {}
            for path, value in diff['iterable_item_removed'].items():
                diff_export["differences"]["iterable_item_removed"][path] = value
        
        # Add summary statistics
        diff_export["summary"] = {
            "total_changes": 0,
            "additions": 0,
            "deletions": 0,
            "changes": 0,
            "type_changes": 0,
            "array_additions": 0,
            "array_deletions": 0
        }
        
        # Count different types of changes
        diff_dict = diff_export["differences"]
        
        if 'dictionary_item_added' in diff_dict:
            diff_export["summary"]["additions"] = len(diff_dict['dictionary_item_added'])
            diff_export["summary"]["total_changes"] += diff_export["summary"]["additions"]
            
        if 'dictionary_item_removed' in diff_dict:
            diff_export["summary"]["deletions"] = len(diff_dict['dictionary_item_removed'])
            diff_export["summary"]["total_changes"] += diff_export["summary"]["deletions"]
            
        if 'values_changed' in diff_dict:
            diff_export["summary"]["changes"] = len(diff_dict['values_changed'])
            diff_export["summary"]["total_changes"] += diff_export["summary"]["changes"]
            
        if 'type_changes' in diff_dict:
            diff_export["summary"]["type_changes"] = len(diff_dict['type_changes'])
            diff_export["summary"]["total_changes"] += diff_export["summary"]["type_changes"]
            
        if 'iterable_item_added' in diff_dict:
            diff_export["summary"]["array_additions"] = len(diff_dict['iterable_item_added'])
            diff_export["summary"]["total_changes"] += diff_export["summary"]["array_additions"]
            
        if 'iterable_item_removed' in diff_dict:
            diff_export["summary"]["array_deletions"] = len(diff_dict['iterable_item_removed'])
            diff_export["summary"]["total_changes"] += diff_export["summary"]["array_deletions"]
    
    # Write to JSON file
    output_file = "diff_export.json"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(diff_export, f, indent=2, ensure_ascii=False)
        print(f"📄 Diff exported to: {output_file}")
    except Exception as e:
        print(f"⚠️  Warning: Could not export diff to JSON file: {e}")


def print_differences(diff: DeepDiff) -> None:
    """
    Print the differences in a structured, human-readable format.
    
    Args:
        diff (DeepDiff): The DeepDiff object containing all differences
    """
    print("=" * 80)
    print("📊 JSON COMPARISON RESULTS")
    print("=" * 80)
    print(diff)
    print("=" * 80)
    # Check if there are any differences
    if not diff:
        print("✅ No differences found. The JSON files are identical.")
        return
    
    # Track total changes for summary
    total_changes = 0
    
    # Print additions (values added in the second file)
    if 'dictionary_item_added' in diff:
        print("\n🟢 ADDITIONS (present in second file, missing in first):")
        print("-" * 60)
        for path in diff['dictionary_item_added']:
            formatted_path = format_path(path)
            print(f"  • {formatted_path}")
            total_changes += 1
    
    # Print deletions (values removed from the first file)
    if 'dictionary_item_removed' in diff:
        print("\n🔴 DELETIONS (present in first file, missing in second):")
        print("-" * 60)
        for path in diff['dictionary_item_removed']:
            formatted_path = format_path(path)
            print(f"  • {formatted_path}")
            total_changes += 1
    
    # Print value changes
    if 'values_changed' in diff:
        print("\n🟡 CHANGES (different values for the same key):")
        print("-" * 60)
        for path, change_info in diff['values_changed'].items():
            formatted_path = format_path(path)
            old_value = change_info['old_value']
            new_value = change_info['new_value']
            
            # Format values for better readability
            old_str = json.dumps(old_value, indent=2) if isinstance(old_value, (dict, list)) else repr(old_value)
            new_str = json.dumps(new_value, indent=2) if isinstance(new_value, (dict, list)) else repr(new_value)
            
            print(f"  • {formatted_path}")
            print(f"    Old: {old_str}")
            print(f"    New: {new_str}")
            print()
            total_changes += 1
    
    # Print type changes
    if 'type_changes' in diff:
        print("\n🔄 TYPE CHANGES (same key, different data type):")
        print("-" * 60)
        for path, change_info in diff['type_changes'].items():
            formatted_path = format_path(path)
            old_value = change_info['old_value']
            new_value = change_info['new_value']
            old_type = type(old_value).__name__
            new_type = type(new_value).__name__
            print(f"  • {formatted_path}")
            print(f"    Old type: {old_type} ({repr(old_value)})")
            print(f"    New type: {new_type} ({repr(new_value)})")
            print()
            total_changes += 1
    
    # Print iterable changes (for lists/arrays)
    if 'iterable_item_added' in diff:
        print("\n🟢 ARRAY ADDITIONS (items added to arrays):")
        print("-" * 60)
        for path, value in diff['iterable_item_added'].items():
            formatted_path = format_path(path)
            value_str = json.dumps(value, indent=2) if isinstance(value, (dict, list)) else repr(value)
            print(f"  • {formatted_path}")
            print(f"    Added: {value_str}")
            print()
            total_changes += 1
    
    if 'iterable_item_removed' in diff:
        print("\n🔴 ARRAY DELETIONS (items removed from arrays):")
        print("-" * 60)
        for path, value in diff['iterable_item_removed'].items():
            formatted_path = format_path(path)
            value_str = json.dumps(value, indent=2) if isinstance(value, (dict, list)) else repr(value)
            print(f"  • {formatted_path}")
            print(f"    Removed: {value_str}")
            print()
            total_changes += 1
    
    # Print summary
    print("=" * 80)
    print(f"📈 SUMMARY: {total_changes} total changes found")
    print("=" * 80)


def compare_json_files(file1_path: str, file2_path: str) -> None:
    """
    Compare two JSON files and display the differences.
    
    Args:
        file1_path (str): Path to the first JSON file
        file2_path (str): Path to the second JSON file
    """
    print(f"🔍 Comparing JSON files:")
    print(f"   File 1: {file1_path}")
    print(f"   File 2: {file2_path}")
    print()
    
    # Load both JSON files
    try:
        json1 = load_json_file(file1_path)
        json2 = load_json_file(file2_path)
    except Exception:
        # Error handling is done in load_json_file
        return
    
    # Perform the comparison using deepdiff
    try:
        diff = DeepDiff(
            json1, 
            json2, 
            ignore_order=True,  # Ignore order in lists for cleaner output
            exclude_paths=set()  # No paths to exclude
        )
        
        # Display the results
        print_differences(diff)
        
        # Export diff to JSON file
        export_diff_to_json(diff, file1_path, file2_path)
        
    except Exception as e:
        print(f"❌ Error during comparison: {e}")
        sys.exit(1)


def main() -> None:
    """
    Main function to handle command-line arguments and initiate comparison.
    """
    # Check for correct number of arguments
    if len(sys.argv) != 3:
        print("❌ Error: Incorrect number of arguments.")
        print()
        print_usage()
        sys.exit(1)
    
    # Extract file paths
    file1_path = sys.argv[1]
    file2_path = sys.argv[2]
    
    # Validate that both arguments are provided
    if not file1_path or not file2_path:
        print("❌ Error: Both file paths must be provided.")
        print()
        print_usage()
        sys.exit(1)
    
    # Perform the comparison
    compare_json_files(file1_path, file2_path)


if __name__ == "__main__":
    main()
