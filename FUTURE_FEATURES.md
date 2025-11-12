# Future Features & Project Roadmap

This document outlines the current feature set of the `.ptam` library and the planned direction for future development.

## Feature Checklist

### Version 1.1 (Current)
- **✓ Plain Text Merge:** The core functionality of archiving a directory into a single, human-readable text file is complete and stable.
- **✓ Values Compression:** Optional word tokenization for frequently used words is implemented.
- **✓ Header 2:** The archive format includes a robust header for metadata (`[header]`, `[structure]`, `[tokens]`).
- **✓ Basic Archive Structure:** The `[structure]` section in the header provides an index of the directory tree.

### Future Versions
- **✗ Extraction:** The `extract` functionality is planned but not yet implemented in a stable release.

## Development Notes

### The `extract` Function Bottleneck

The primary reason for excluding the `extract` function from the current release was a persistent and complex bug in the parsing logic. While the `archive` function works perfectly, the `extract` function failed to reliably parse the `.ptam` file, especially when handling the new header format and maintaining backward compatibility.

The core challenge was correctly identifying the boundary between the header sections (`[header]`, `[structure]`, `[tokens]`) and the start of the file content (`[path:/...]`). Several parsing strategies were attempted, but none were able to pass the test suite reliably.

### Locating the Hidden Code

The previous, non-functional implementation of the `extract` function has been removed from the current codebase to ensure the library is stable. However, its complete implementation can be found in the git history of the following file:
- **`ptam/core.py`**

Developers looking to implement the extraction feature in the future should review the history of this file to understand the previous attempts and the nature of the parsing bug.
