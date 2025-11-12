# PTAM Library Documentation

## Overview

The Plain Text Archive Merger (`.ptam`) is a Python library designed for creating human-readable, non-compressed archives. It is ideal for scenarios where file archives need to be easily inspected or modified with a standard text editor.

The library is designed to be simple, robust, and transparent. It supports nested directories, text files, and provides a mechanism for referencing binary files without including them in the archive. Version 1.1 introduces an optional word tokenization feature to reduce the size of archives containing repetitive text.

**Note:** This version of the library focuses exclusively on the archiving (merging) functionality. Extraction capabilities will be addressed in a future update.

## Features

- **Human-Readable Format:** The `.ptam` format is plain text, making it easy to read and debug.
- **Directory Structure:** Preserves the full directory structure of the source.
- **Binary File Handling:** References binary files by name and SHA-256 hash instead of storing their content, keeping the archive text-only.
- **Word Tokenization (Optional):** Reduces archive size by replacing frequently used words with short tokens (e.g., `$01`).

## API Reference

The library exposes a single main function: `archive`.

---

### `archive(source_directory, output_ptam_file, use_tokenization=False)`

Creates a `.ptam` archive from a source directory.

- **`source_directory` (str):** The path to the directory you want to archive.
- **`output_ptam_file` (str):** The path where the `.ptam` file will be saved.
- **`use_tokenization` (bool, optional):** If `True`, the function will enable word tokenization. Defaults to `False`.

**Tokenization Rules:** A word is tokenized if it contains 5 or more letters and appears 5 or more times across all text files in the archive.

## Usage Example

Here's a simple example of how to use the library:

```python
import os
from ptam import archive

# --- Create a dummy directory to archive ---
source_dir = "my_project"
os.makedirs(os.path.join(source_dir, "docs"), exist_ok=True)

with open(os.path.join(source_dir, "main.txt"), "w") as f:
    f.write("This is the main file. This file is important.")

# --- Archive the directory ---
archive(source_dir, "my_project.ptam")

# --- Archive with tokenization ---
archive(source_dir, "my_project_tokenized.ptam", use_tokenization=True)

print("Archiving complete!")
```

## The `.ptam` File Format

The `.ptam` format is section-based, using bracketed `[]` headers.

- **`[header]`:** Contains metadata about the archive, such as its version and whether tokenization is used.
- **`[structure]`:** An optional section that lists all the directory paths for faster extraction in future versions.
- **`[tokens]`:** An optional section that contains the word-to-token mapping if tokenization is enabled.
- **`[path:/...]`:** A section that lists the files and subdirectories within a specific path.
- **`[g-end]`:** A marker at the end of the file to signify a complete archive.
