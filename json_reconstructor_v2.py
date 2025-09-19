#!/usr/bin/env python3
"""
JSON Reconstructor Script

This script reverses a DeepDiff operation to reconstruct a modified JSON file.
It takes a source JSON file, a DeepDiff export, and an exclusion list to create
a new JSON file with the changes applied while respecting exclusions.

Usage:
    python json_reconstructor.py <target_data.json> <diff_export.json> <exclusion_list.json>

Author: Generated for Zuora Workflow Automation
"""

import json
import sys
import re
import copy
import argparse
from typing import Any, Dict, List, Union, Set
from pathlib import Path

class JSONReconstructor:
    """Handles the reconstruction of JSON files from DeepDiff exports."""
    
    def __init__(self, target_data: Dict, diff_export: Dict, exclusion_list: Dict):
        """
        Initialize the reconstructor with the required data.
        
        Args:
            target_data: The original JSON data
            diff_export: The DeepDiff export containing changes
            exclusion_list: The exclusion list with paths to ignore
        """
        self.target_data = copy.deepcopy(target_data)
        self.diff_export = diff_export
        self.exclusion_list = exclusion_list
        self.excluded_paths = set(exclusion_list.get('excluded_paths', []))
        self.excluded_regex_paths = exclusion_list.get('excluded_regex_paths', [])
        
    def is_path_excluded(self, path: str) -> bool:
        """
        Check if a path should be excluded from reconstruction.
        
        Args:
            path: The path to check
            
        Returns:
            True if the path should be excluded, False otherwise
        """
        # Check exact path matches
        if path in self.excluded_paths:
            return True
            
        # Check if any parent path is excluded (for task-level changes)
        for excluded_path in self.excluded_paths:
            if path.startswith(excluded_path + '[') or path.startswith(excluded_path + '.'):
                return True
            
        # Check regex pattern matches
        for regex_pattern in self.excluded_regex_paths:
            try:
                if re.search(regex_pattern, path):
                    return True
            except re.error:
                # If regex is invalid, skip it
                continue
                
        return False
    
    def parse_path(self, path: str) -> List[Union[str, int]]:
        """
        Parse a DeepDiff path string into a list of keys/indices.
        
        Args:
            path: The path string (e.g., "root['tasks'][0]['name']")
            
        Returns:
            List of keys and indices to navigate the JSON structure
        """
        # Remove 'root' prefix and parse the path
        if path.startswith("root"):
            path = path[4:]  # Remove 'root'
        
        # Parse the path using regex to handle both string keys and numeric indices
        pattern = r"\[([^\]]+)\]"
        matches = re.findall(pattern, path)
        
        result = []
        for match in matches:
            # Check if it's a numeric index (including negative numbers)
            if match.lstrip('-').isdigit():
                result.append(int(match))
            else:
                # Remove quotes and add the key
                key = match.strip("'\"")
                result.append(key)
        
        return result
    
    def get_nested_value(self, data: Dict, path_keys: List[Union[str, int]]) -> Any:
        """
        Get a value from nested data structure using path keys.
        
        Args:
            data: The data structure to navigate
            path_keys: List of keys/indices to navigate
            
        Returns:
            The value at the specified path
        """
        current = data
        for key in path_keys:
            if isinstance(current, dict):
                current = current[key]
            elif isinstance(current, list):
                current = current[key]
            else:
                raise ValueError(f"Cannot navigate to key {key} in {type(current)}")
        return current
    
    def set_nested_value(self, data: Dict, path_keys: List[Union[str, int]], value: Any) -> None:
        """
        Set a value in nested data structure using path keys.
        
        Args:
            data: The data structure to modify
            path_keys: List of keys/indices to navigate
            value: The value to set
        """
        current = data
        for key in path_keys[:-1]:
            if isinstance(current, dict):
                if key not in current:
                    current[key] = {}
                current = current[key]
            elif isinstance(current, list):
                while len(current) <= key:
                    current.append({})
                current = current[key]
            else:
                raise ValueError(f"Cannot navigate to key {key} in {type(current)}")
        
        # Set the final value
        final_key = path_keys[-1]
        if isinstance(current, dict):
            current[final_key] = value
        elif isinstance(current, list):
            while len(current) <= final_key:
                current.append(None)
            current[final_key] = value
        else:
            raise ValueError(f"Cannot set value at key {final_key} in {type(current)}")
    
    def apply_values_changed(self, changes: List[Dict]) -> None:
        """
        Apply values_changed modifications to the reconstructed data.
        
        Args:
            changes: List of value change objects from DeepDiff
        """
        for change in changes:
            path = change['path']
            
            if self.is_path_excluded(path):
                print(f"Skipping excluded path: {path}")
                continue
            
            try:
                path_keys = self.parse_path(path)
                new_value = change['new_value']
                
                # Check if this is an object-level change that might have excluded fields
                if self.is_object_level_change(path) and self.has_excluded_object_fields():
                    new_value = self.apply_selective_object_update(path, new_value)
                
                self.set_nested_value(self.target_data, path_keys, new_value)
                print(f"Applied values_changed: {path}")
            except Exception as e:
                print(f"Error applying values_changed for {path}: {e}")
    
    def apply_dictionary_item_added(self, changes: List[Dict]) -> None:
        """
        Apply dictionary_item_added modifications to the reconstructed data.
        
        Args:
            changes: List of dictionary item addition objects from DeepDiff
        """
        for change in changes:
            path = change['path']
            
            if self.is_path_excluded(path):
                print(f"Skipping excluded path: {path}")
                continue
            
            try:
                path_keys = self.parse_path(path)
                new_value = change.get('new_value', change.get('value'))
                self.set_nested_value(self.target_data, path_keys, new_value)
                print(f"Applied dictionary_item_added: {path}")
            except Exception as e:
                print(f"Error applying dictionary_item_added for {path}: {e}")
    
    def apply_dictionary_item_removed(self, changes: List[Dict]) -> None:
        """
        Apply dictionary_item_removed modifications to the reconstructed data.
        
        Args:
            changes: List of dictionary item removal objects from DeepDiff
        """
        for change in changes:
            path = change['path']
            
            if self.is_path_excluded(path):
                print(f"Skipping excluded path: {path}")
                continue
            
            try:
                path_keys = self.parse_path(path)
                parent_keys = path_keys[:-1]
                key_to_remove = path_keys[-1]
                
                parent = self.get_nested_value(self.target_data, parent_keys)
                if isinstance(parent, dict):
                    del parent[key_to_remove]
                elif isinstance(parent, list):
                    parent.pop(key_to_remove)
                
                print(f"Applied dictionary_item_removed: {path}")
            except Exception as e:
                print(f"Error applying dictionary_item_removed for {path}: {e}")
    
    def apply_iterable_item_added(self, changes: List[Dict]) -> None:
        """
        Apply iterable_item_added modifications to the reconstructed data.
        
        Args:
            changes: List of iterable item addition objects from DeepDiff
        """
        for change in changes:
            path = change['path']
            
            if self.is_path_excluded(path):
                print(f"Skipping excluded path: {path}")
                continue
            
            try:
                path_keys = self.parse_path(path)
                new_value = change['value']
                self.set_nested_value(self.target_data, path_keys, new_value)
                print(f"Applied iterable_item_added: {path}")
            except Exception as e:
                print(f"Error applying iterable_item_added for {path}: {e}")
    
    def apply_iterable_item_removed(self, changes: List[Dict]) -> None:
        """
        Apply iterable_item_removed modifications to the reconstructed data.
        
        Args:
            changes: List of iterable item removal objects from DeepDiff
        """
        for change in changes:
            path = change['path']
            
            if self.is_path_excluded(path):
                print(f"Skipping excluded path: {path}")
                continue
            
            try:
                path_keys = self.parse_path(path)
                parent_keys = path_keys[:-1]
                index_to_remove = path_keys[-1]
                
                parent = self.get_nested_value(self.target_data, parent_keys)
                if isinstance(parent, list):
                    parent.pop(index_to_remove)
                
                print(f"Applied iterable_item_removed: {path}")
            except Exception as e:
                print(f"Error applying iterable_item_removed for {path}: {e}")
    
    def reconstruct(self) -> Dict:
        """
        Reconstruct the JSON by applying all changes from the DeepDiff export.
        
        Returns:
            The reconstructed JSON data
        """
        differences = self.diff_export.get('differences', {})
        
        # Apply different types of changes
        if 'values_changed' in differences:
            self.apply_values_changed(differences['values_changed'])
        
        if 'dictionary_item_added' in differences:
            self.apply_dictionary_item_added(differences['dictionary_item_added'])
        
        if 'dictionary_item_removed' in differences:
            self.apply_dictionary_item_removed(differences['dictionary_item_removed'])
        
        if 'iterable_item_added' in differences:
            self.apply_iterable_item_added(differences['iterable_item_added'])
        
        if 'iterable_item_removed' in differences:
            self.apply_iterable_item_removed(differences['iterable_item_removed'])
        
        return self.target_data
    
    def is_object_level_change(self, path: str) -> bool:
        """
        Check if the path represents an object-level change (entire object replacement).
        
        Args:
            path: The path to check
            
        Returns:
            True if this is an object-level change, False otherwise
        """
        # Match patterns like root['key'][index] or root['key']['subkey'][index]
        # This detects when entire objects are being replaced
        return re.match(r"root\[[^\]]+\]\[\d+\]$", path) is not None
    
    def has_excluded_object_fields(self) -> bool:
        """
        Check if there are any regex patterns that exclude object fields.
        
        Returns:
            True if there are object field exclusions, False otherwise
        """
        # Check if any regex pattern targets specific fields within objects
        for regex_pattern in self.excluded_regex_paths:
            # Look for patterns that match field-level exclusions like root['key'][index]['field']
            # Check if the pattern contains both [digit] and ['field'] structure
            if "\\[\\d+\\]\\[" in regex_pattern and "\\]" in regex_pattern:
                return True
        return False
    
    def apply_selective_object_update(self, path: str, new_value: Dict) -> Dict:
        """
        Apply selective updates to an object, preserving excluded fields.
        
        Args:
            path: The path of the object being updated
            new_value: The new object value
            
        Returns:
            The selectively updated object value
        """
        # Get the current object value
        path_keys = self.parse_path(path)
        current_value = self.get_nested_value(self.target_data, path_keys)
        
        # Create a copy of the new value
        updated_value = copy.deepcopy(new_value)
        
        # Check each field in the new value against exclusion patterns
        for field_name, field_value in new_value.items():
            field_path = f"{path}['{field_name}']"
            
            # Check if this field should be excluded
            for regex_pattern in self.excluded_regex_paths:
                try:
                    if re.search(regex_pattern, field_path):
                        # Preserve the original field value
                        if isinstance(current_value, dict) and field_name in current_value:
                            updated_value[field_name] = current_value[field_name]
                            print(f"Preserved excluded field: {field_path}")
                        break
                except re.error:
                    continue
        
        return updated_value


def load_json_file(file_path: str) -> Dict:
    """
    Load and parse a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Parsed JSON data
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json_file(data: Dict, file_path: str) -> None:
    """
    Save data to a JSON file with proper formatting.
    
    Args:
        data: The data to save
        file_path: Path where to save the file
    """
    path = Path(file_path)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def main():
    """Main function to handle command line arguments and orchestrate reconstruction."""
    parser = argparse.ArgumentParser(
        description="Reconstruct a JSON file from DeepDiff export while respecting exclusions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python json_reconstructor.py original.json diff_export.json exclusion.json
    python json_reconstructor.py sample1.json diff_export.json exclusion.json -o reconstructed.json
        """
    )
    
    parser.add_argument('target_data', help='Path to the target JSON file')
    parser.add_argument('diff_export', help='Path to the DeepDiff export JSON file')
    parser.add_argument('exclusion_list', help='Path to the exclusion list JSON file')
    parser.add_argument('-o', '--output', default='reconstructed.json',
                       help='Output file path (default: reconstructed.json)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose output')
    
    args = parser.parse_args()
    
    try:
        # Load input files
        print("Loading input files...")
        target_data = load_json_file(args.target_data)
        diff_export = load_json_file(args.diff_export)
        exclusion_list = load_json_file(args.exclusion_list)
        
        if args.verbose:
            print(f"Target data keys: {list(target_data.keys())}")
            print(f"Diff export keys: {list(diff_export.keys())}")
            print(f"Exclusion list: {exclusion_list}")
        
        # Create reconstructor and apply changes
        print("Reconstructing JSON...")
        reconstructor = JSONReconstructor(target_data, diff_export, exclusion_list)
        reconstructed_data = reconstructor.reconstruct()
        
        # Save the reconstructed data
        print(f"Saving reconstructed data to {args.output}...")
        save_json_file(reconstructed_data, args.output)
        
        print(f"✅ Successfully reconstructed JSON file: {args.output}")
        
        # Print summary
        differences = diff_export.get('differences', {})
        total_changes = sum(len(changes) for changes in differences.values() if isinstance(changes, list))
        print(f"📊 Applied {total_changes} changes from DeepDiff export")
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()