# JSON Diff Tool

A Python script to compare two JSON files and report differences in a clear, human-readable format.

## Features

- **Comprehensive Comparison**: Uses the `deepdiff` library for accurate deep comparison of JSON structures
- **Structured Output**: Clearly categorizes differences into additions, deletions, and changes
- **JSON Export**: Automatically exports diff results to `diff_export.json` for programmatic access
- **Robust Error Handling**: Handles file not found, permission errors, and malformed JSON gracefully
- **Command-Line Interface**: Easy to use from the command line with proper argument validation
- **Detailed Comments**: Well-documented code with comprehensive comments explaining the logic

## Installation

1. Install the required dependency:
```bash
pip install deepdiff
```

Or install from the requirements file:
```bash
pip install -r requirements.txt
```

## Usage

```bash
python json_diff.py <file1.json> <file2.json>
```

### Examples

```bash
# Compare two JSON files
python json_diff.py sample1.json sample2.json

# Compare with identical files
python json_diff.py sample1.json sample1.json
```

## Output Format

The script provides a structured output that categorizes differences:

### 🟢 ADDITIONS
Keys or values that exist in the second file but not in the first file.

### 🔴 DELETIONS  
Keys or values that exist in the first file but have been removed in the second file.

### 🟡 CHANGES
Keys that have different values between the two files, showing both old and new values.

### 🔄 TYPE CHANGES
Keys that have the same name but different data types between the files.

### 🟢 ARRAY ADDITIONS
Items that have been added to arrays/lists.

### 🔴 ARRAY DELETIONS
Items that have been removed from arrays/lists.

## JSON Export

The script automatically exports the diff results to `diff_export.json` in the project directory. This file is refreshed on each run and contains:

- **Metadata**: Timestamp, file paths, and whether differences were found
- **Differences**: Structured representation of all changes found
- **Summary**: Count of different types of changes

### Export Structure

```json
{
  "metadata": {
    "comparison_timestamp": "2024-01-20T14:45:00Z",
    "file1": "sample1.json",
    "file2": "sample2.json",
    "has_differences": true
  },
  "differences": {
    "dictionary_item_added": ["root['new_field']"],
    "values_changed": {
      "root['existing_field']": {
        "old_value": "old_value",
        "new_value": "new_value"
      }
    }
  },
  "summary": {
    "total_changes": 2,
    "additions": 1,
    "deletions": 0,
    "changes": 1,
    "type_changes": 0,
    "array_additions": 0,
    "array_deletions": 0
  }
}
```

## Error Handling

The script includes robust error handling for:

- **Incorrect number of arguments**: Shows usage information
- **File not found**: Clear error message with file path
- **Permission errors**: Indicates when files cannot be read
- **Invalid JSON**: Shows line and column information for JSON parsing errors
- **Unexpected errors**: Catches and reports any other issues

## Sample Files

The repository includes sample JSON files for testing:

- `sample1.json`: Basic JSON structure with user information
- `sample2.json`: Modified version with additions and changes
- `malformed.json`: Example of invalid JSON for testing error handling

## Example Output

```
🔍 Comparing JSON files:
   File 1: sample1.json
   File 2: sample2.json

================================================================================
📊 JSON COMPARISON RESULTS
================================================================================

🟢 ADDITIONS (present in second file, missing in first):
------------------------------------------------------------
  • ['department']
  • ['skills']
  • ['address']['country']

🟡 CHANGES (different values for the same key):
------------------------------------------------------------
  • ['age']
    Old: 30
    New: 31

  • ['hobbies'][2]
    Old: 'cooking'
    New: 'hiking'

================================================================================
📈 SUMMARY: 5 total changes found
================================================================================
```

## Dependencies

- Python 3.6+
- deepdiff >= 6.0.0

## License

This script is provided as-is for educational and practical use.
