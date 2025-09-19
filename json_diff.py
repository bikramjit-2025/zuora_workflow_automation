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
from typing import Dict, Any
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


def export_diff_to_json(diff, file1_path: str, file2_path: str) -> None:
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
        print(json.dumps(tree_dict, indent=4, sort_keys=True, ensure_ascii=False))
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
            ignore_order=True
        )
        
        # Get tree view representation
        tree_view = diff.tree
        
        # Display the results
        print_differences(tree_view)
        
        # Export diff to JSON file
        export_diff_to_json(tree_view, file1_path, file2_path)
        
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
