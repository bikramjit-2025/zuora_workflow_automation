#!/usr/bin/env python3
"""
JSON Reconstructor Tool

This script reverses a DeepDiff operation by taking an original JSON file and a diff export
to reconstruct the modified JSON file. It applies all the changes from the diff to create
the target version.

Author: AI Assistant
Dependencies: None (uses only standard library)
"""

import json
import copy
import sys
import os
from typing import Dict, Any, List, Union


def print_usage() -> None:
    """
    Print usage information for the script.
    """
    print("Usage: python json_reconstructor.py <original_file.json> <diff_file.json> <output_file.json> [target_file.json]")
    print("\nDescription:")
    print("  Reconstruct a modified JSON file from an original file and a diff export.")
    print("\nArguments:")
    print("  original_file.json  - The original, unmodified JSON file")
    print("  diff_file.json      - The JSON file containing the DeepDiff export")
    print("  output_file.json    - The output file for the reconstructed JSON")
    print("  target_file.json    - (Optional) The target file for extracting addition values")
    print("\nExamples:")
    print("  python json_reconstructor.py sample1.json diff_export.json reconstructed.json")
    print("  python json_reconstructor.py sample1.json diff_export.json reconstructed.json sample2.json")


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


def parse_path(path: str) -> List[Union[str, int]]:
    """
    Parse a DeepDiff path string into a list of keys/indices for navigation.
    
    Args:
        path (str): Path string like "root['key']['subkey'][0]"
        
    Returns:
        List[Union[str, int]]: List of keys and indices for navigation
    """
    # Remove 'root' prefix if present
    if path.startswith("root"):
        path = path[4:]  # Remove 'root'
    
    # Handle empty path (root only)
    if not path:
        return []
    
    # Parse the path using a simple approach
    import re
    
    # Find all ['key'] and [index] patterns
    pattern = r"\[([^\]]+)\]"
    matches = re.findall(pattern, path)
    
    result = []
    for match in matches:
        # Try to convert to integer (for array indices)
        try:
            result.append(int(match))
        except ValueError:
            # Remove quotes if present
            if match.startswith("'") and match.endswith("'"):
                result.append(match[1:-1])
            elif match.startswith('"') and match.endswith('"'):
                result.append(match[1:-1])
            else:
                result.append(match)
    
    return result


def navigate_to_path(data: Dict[str, Any], path: List[Union[str, int]]) -> Any:
    """
    Navigate to a specific path in the data structure.
    
    Args:
        data: The data structure to navigate
        path: List of keys/indices to follow
        
    Returns:
        The value at the specified path
        
    Raises:
        KeyError: If the path doesn't exist
        IndexError: If an array index is out of bounds
    """
    current = data
    for key in path:
        if isinstance(current, dict):
            current = current[key]
        elif isinstance(current, list):
            current = current[key]
        else:
            raise KeyError(f"Cannot navigate to key '{key}' in non-container type")
    return current


def set_value_at_path(data: Dict[str, Any], path: List[Union[str, int]], value: Any) -> None:
    """
    Set a value at a specific path in the data structure.
    
    Args:
        data: The data structure to modify
        path: List of keys/indices to follow
        value: The value to set
    """
    current = data
    # Navigate to the parent of the target
    for key in path[:-1]:
        if isinstance(current, dict):
            if key not in current:
                # Create intermediate dictionaries as needed
                current[key] = {}
            current = current[key]
        elif isinstance(current, list):
            # Ensure list is large enough
            while len(current) <= key:
                current.append(None)
            current = current[key]
        else:
            raise KeyError(f"Cannot navigate to key '{key}' in non-container type")
    
    # Set the final value
    final_key = path[-1]
    if isinstance(current, dict):
        current[final_key] = value
    elif isinstance(current, list):
        # Ensure list is large enough
        while len(current) <= final_key:
            current.append(None)
        current[final_key] = value
    else:
        raise KeyError(f"Cannot set value in non-container type")


def remove_value_at_path(data: Dict[str, Any], path: List[Union[str, int]]) -> None:
    """
    Remove a value at a specific path in the data structure.
    
    Args:
        data: The data structure to modify
        path: List of keys/indices to follow
    """
    current = data
    # Navigate to the parent of the target
    for key in path[:-1]:
        if isinstance(current, dict):
            current = current[key]
        elif isinstance(current, list):
            current = current[key]
        else:
            raise KeyError(f"Cannot navigate to key '{key}' in non-container type")
    
    # Remove the final value
    final_key = path[-1]
    if isinstance(current, dict):
        if final_key in current:
            del current[final_key]
    elif isinstance(current, list):
        if 0 <= final_key < len(current):
            del current[final_key]
    else:
        raise KeyError(f"Cannot remove value from non-container type")


def apply_dictionary_item_added(data: Dict[str, Any], additions: List[str], target_data: Dict[str, Any] = None) -> None:
    """
    Apply dictionary item additions to the data.
    
    Args:
        data: The data structure to modify
        additions: List of paths that were added
        target_data: Optional target data to extract values from
    """
    print("🟢 Applying dictionary item additions...")
    for path_str in additions:
        try:
            if target_data:
                # Extract the value from the target data
                path = parse_path(path_str)
                value = navigate_to_path(target_data, path)
                set_value_at_path(data, path, value)
                print(f"  • Added: {path_str}")
            else:
                print(f"  ⚠️  Warning: Cannot add {path_str} without target data")
        except Exception as e:
            print(f"  ⚠️  Warning: Could not apply addition at {path_str}: {e}")


def apply_dictionary_item_removed(data: Dict[str, Any], removals: List[str]) -> None:
    """
    Apply dictionary item removals to the data.
    
    Args:
        data: The data structure to modify
        removals: List of paths that were removed
    """
    print("🔴 Applying dictionary item removals...")
    for path_str in removals:
        try:
            path = parse_path(path_str)
            remove_value_at_path(data, path)
            print(f"  • Removed: {path_str}")
        except Exception as e:
            print(f"  ⚠️  Warning: Could not remove item at {path_str}: {e}")


def apply_values_changed(data: Dict[str, Any], changes: Dict[str, Dict[str, Any]]) -> None:
    """
    Apply value changes to the data.
    
    Args:
        data: The data structure to modify
        changes: Dictionary of path -> {old_value, new_value}
    """
    print("🟡 Applying value changes...")
    for path_str, change_info in changes.items():
        try:
            path = parse_path(path_str)
            new_value = change_info['new_value']
            set_value_at_path(data, path, new_value)
            print(f"  • Changed: {path_str}")
        except Exception as e:
            print(f"  ⚠️  Warning: Could not change value at {path_str}: {e}")


def apply_type_changes(data: Dict[str, Any], type_changes: Dict[str, Dict[str, Any]]) -> None:
    """
    Apply type changes to the data.
    
    Args:
        data: The data structure to modify
        type_changes: Dictionary of path -> {old_value, new_value, old_type, new_type}
    """
    print("🔄 Applying type changes...")
    for path_str, change_info in type_changes.items():
        try:
            path = parse_path(path_str)
            new_value = change_info['new_value']
            set_value_at_path(data, path, new_value)
            print(f"  • Type changed: {path_str} ({change_info.get('old_type', 'unknown')} -> {change_info.get('new_type', 'unknown')})")
        except Exception as e:
            print(f"  ⚠️  Warning: Could not apply type change at {path_str}: {e}")


def apply_iterable_changes(data: Dict[str, Any], additions: Dict[str, Any], removals: Dict[str, Any]) -> None:
    """
    Apply iterable (array) changes to the data.
    
    Args:
        data: The data structure to modify
        additions: Dictionary of path -> value for array additions
        removals: Dictionary of path -> value for array removals
    """
    print("🟢 Applying array additions...")
    for path_str, value in additions.items():
        try:
            path = parse_path(path_str)
            # For array additions, we need to append to the list
            current = navigate_to_path(data, path[:-1])
            if isinstance(current, list):
                current.append(value)
                print(f"  • Added to array: {path_str}")
            else:
                print(f"  ⚠️  Warning: Path {path_str} does not point to a list")
        except Exception as e:
            print(f"  ⚠️  Warning: Could not add to array at {path_str}: {e}")
    
    print("🔴 Applying array removals...")
    for path_str, value in removals.items():
        try:
            path = parse_path(path_str)
            # For array removals, we need to remove from the list
            current = navigate_to_path(data, path[:-1])
            if isinstance(current, list) and value in current:
                current.remove(value)
                print(f"  • Removed from array: {path_str}")
            else:
                print(f"  ⚠️  Warning: Could not remove from array at {path_str}")
        except Exception as e:
            print(f"  ⚠️  Warning: Could not remove from array at {path_str}: {e}")


def reconstruct_json(original_file_path: str, diff_file_path: str, output_file_path: str, target_file_path: str = None) -> None:
    """
    Reconstruct a modified JSON file from an original file and a diff export.
    
    Args:
        original_file_path (str): Path to the original JSON file
        diff_file_path (str): Path to the diff export JSON file
        output_file_path (str): Path for the output reconstructed JSON file
        target_file_path (str, optional): Path to the target file for extracting addition values
    """
    print("🔧 JSON Reconstruction Tool")
    print("=" * 50)
    print(f"📁 Original file: {original_file_path}")
    print(f"📄 Diff file: {diff_file_path}")
    print(f"💾 Output file: {output_file_path}")
    if target_file_path:
        print(f"🎯 Target file: {target_file_path}")
    print()
    
    # Load the original data
    print("📖 Loading original JSON data...")
    original_data = load_json_file(original_file_path)
    
    # Load the diff data
    print("📖 Loading diff export data...")
    diff_data = load_json_file(diff_file_path)
    
    # Load target data if provided
    target_data = None
    if target_file_path:
        print("📖 Loading target JSON data...")
        target_data = load_json_file(target_file_path)
    
    # Validate diff structure
    if 'differences' not in diff_data:
        print("❌ Error: Invalid diff file structure. Missing 'differences' key.")
        sys.exit(1)
    
    # Create a deep copy of the original data
    print("📋 Creating working copy of original data...")
    working_data = copy.deepcopy(original_data)
    
    # Get the differences
    differences = diff_data['differences']
    
    # Check if there are any differences to apply
    if not differences:
        print("✅ No differences found. Original and target files are identical.")
        # Still save the copy
        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(working_data, f, indent=4, ensure_ascii=False)
        print(f"💾 Saved identical copy to: {output_file_path}")
        return
    
    print(f"🔍 Found {len(differences)} types of differences to apply...")
    print()
    
    # Apply dictionary item removals first (to avoid path issues)
    if 'dictionary_item_removed' in differences:
        apply_dictionary_item_removed(working_data, differences['dictionary_item_removed'])
        print()
    
    # Apply value changes
    if 'values_changed' in differences:
        apply_values_changed(working_data, differences['values_changed'])
        print()
    
    # Apply type changes
    if 'type_changes' in differences:
        apply_type_changes(working_data, differences['type_changes'])
        print()
    
    # Apply iterable changes
    if 'iterable_item_added' in differences or 'iterable_item_removed' in differences:
        additions = differences.get('iterable_item_added', {})
        removals = differences.get('iterable_item_removed', {})
        apply_iterable_changes(working_data, additions, removals)
        print()
    
    # Apply dictionary item additions last (to avoid path conflicts)
    if 'dictionary_item_added' in differences:
        apply_dictionary_item_added(working_data, differences['dictionary_item_added'], target_data)
        print()
    
    # Save the reconstructed data
    print("💾 Saving reconstructed JSON...")
    try:
        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(working_data, f, indent=4, ensure_ascii=False)
        print(f"✅ Successfully saved reconstructed JSON to: {output_file_path}")
    except Exception as e:
        print(f"❌ Error saving reconstructed JSON: {e}")
        sys.exit(1)
    
    print()
    print("🎉 Reconstruction complete!")


def main() -> None:
    """
    Main function to handle command-line arguments and initiate reconstruction.
    """
    # Check for correct number of arguments (3 required, 1 optional)
    if len(sys.argv) < 4 or len(sys.argv) > 5:
        print("❌ Error: Incorrect number of arguments.")
        print()
        print_usage()
        sys.exit(1)
    
    # Extract file paths
    original_file_path = sys.argv[1]
    diff_file_path = sys.argv[2]
    output_file_path = sys.argv[3]
    target_file_path = sys.argv[4] if len(sys.argv) == 5 else None
    
    # Validate that required arguments are provided
    if not all([original_file_path, diff_file_path, output_file_path]):
        print("❌ Error: All required file paths must be provided.")
        print()
        print_usage()
        sys.exit(1)
    
    # Perform the reconstruction
    reconstruct_json(original_file_path, diff_file_path, output_file_path, target_file_path)


if __name__ == '__main__':
    main()
