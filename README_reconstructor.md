# JSON Reconstructor Tool

A Python script that reverses DeepDiff operations by reconstructing a modified JSON file from an original file and a diff export.

## Features

- **Complete Reconstruction**: Reconstructs modified JSON files from diff exports
- **Multiple Change Types**: Handles all DeepDiff change types (additions, deletions, changes, type changes, array modifications)
- **Optional Target File**: Can use a target file to extract values for additions
- **Robust Error Handling**: Handles file operations and JSON parsing errors gracefully
- **Command-Line Interface**: Easy to use from the command line with proper argument validation
- **Detailed Logging**: Shows progress and warnings during reconstruction

## Usage

### Basic Usage (Limited Reconstruction)
```bash
python json_reconstructor.py <original_file.json> <diff_file.json> <output_file.json>
```

### Complete Reconstruction (Recommended)
```bash
python json_reconstructor.py <original_file.json> <diff_file.json> <output_file.json> <target_file.json>
```

### Arguments

- **original_file.json**: The original, unmodified JSON file
- **diff_file.json**: The JSON file containing the DeepDiff export (from json_diff.py)
- **output_file.json**: The output file for the reconstructed JSON
- **target_file.json**: (Optional) The target file for extracting addition values

## Examples

```bash
# Basic reconstruction (may be incomplete for additions)
python json_reconstructor.py sample1.json diff_export.json reconstructed.json

# Complete reconstruction with target file
python json_reconstructor.py sample1.json diff_export.json reconstructed.json sample2.json

# Reconstruct Zuora workflow
python json_reconstructor.py zuora_workflow1.json diff_export.json reconstructed_workflow.json zuora_workflow2.json
```

## Supported Change Types

### ✅ Fully Supported (with or without target file)
- **Value Changes**: Updates existing values with new values
- **Type Changes**: Changes data types (string to number, etc.)
- **Dictionary Removals**: Removes keys from objects
- **Array Modifications**: Adds/removes items from arrays

### ⚠️ Limited Support (requires target file)
- **Dictionary Additions**: Adds new keys to objects
  - Without target file: Shows warning, skips addition
  - With target file: Extracts values from target and adds them

## How It Works

1. **Load Files**: Reads the original JSON file and the diff export
2. **Create Working Copy**: Makes a deep copy of the original data
3. **Apply Changes**: Iterates through diff changes and applies them:
   - Removes items first (to avoid path conflicts)
   - Updates existing values
   - Changes data types
   - Modifies arrays
   - Adds new items (if target file provided)
4. **Save Result**: Writes the reconstructed JSON to the output file

## Example Workflow

```bash
# 1. Compare two JSON files and generate diff
python json_diff.py original.json modified.json

# 2. Reconstruct the modified file from original and diff
python json_reconstructor.py original.json diff_export.json reconstructed.json modified.json

# 3. Verify reconstruction is correct
python json_diff.py reconstructed.json modified.json
# Should show: "No differences found. The JSON files are identical."
```

## Limitations

1. **Dictionary Additions**: Without a target file, new keys cannot be added because the diff export only contains paths, not values
2. **Complex Paths**: Very deeply nested structures might have path parsing limitations
3. **Array Order**: Array modifications preserve order but may not handle all edge cases

## Error Handling

The script includes robust error handling for:
- **File not found**: Clear error messages with file paths
- **Invalid JSON**: Shows line and column information for parsing errors
- **Permission errors**: Indicates when files cannot be read/written
- **Path navigation errors**: Warns about issues accessing specific paths
- **Missing diff structure**: Validates that the diff file has the expected format

## Output

The script provides detailed console output showing:
- Files being processed
- Types of changes being applied
- Progress for each change type
- Warnings for any issues encountered
- Success confirmation

## Use Cases

- **Version Control**: Reconstruct previous versions from diffs
- **Configuration Management**: Apply configuration changes to base templates
- **Data Migration**: Transform data structures using diff-based changes
- **Testing**: Verify that diff exports can be properly reconstructed
- **Backup Recovery**: Reconstruct files from change logs

## Dependencies

- Python 3.6+
- Standard library only (json, copy, sys, os, typing)

## Integration with JSON Diff Tool

This reconstructor is designed to work seamlessly with the `json_diff.py` script:

1. Use `json_diff.py` to compare files and generate diff exports
2. Use `json_reconstructor.py` to reverse the diff and reconstruct files
3. Both tools use the same diff export format for compatibility

## License

This script is provided as-is for educational and practical use.
