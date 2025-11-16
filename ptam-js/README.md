# Plain Text Archive Merger (.ptam) for JavaScript

A JavaScript library for creating `.ptam` archives. This format is designed to be human-readable and allows multiple files and directories to be merged into a single text file.

This library is a direct port of the original Python `ptam` library, with the addition of a `virtualFiles` feature for adding in-memory content to the archive.

## Features

- **Human-Readable Format:** The `.ptam` format is plain text, making it easy to read and debug.
- **Directory Structure:** Preserves the full directory structure of the source.
- **Binary File Handling:** References binary files by name and SHA-256 hash instead of storing their content.
- **Word Tokenization (Optional):** Reduces archive size by replacing frequently used words with short tokens.
- **Virtual Files:** Add files to the archive directly from memory, without needing to write them to disk first.

## API Reference

The library exposes a single main function: `archive`.

---

### `archive(sourceDirectory, outputPtamFile, [options])`

Creates a `.ptam` archive from a source directory and/or virtual files.

- **`sourceDirectory` (string | null):** The path to the directory you want to archive. Can be `null` if you are only using virtual files.
- **`outputPtamFile` (string):** The path where the `.ptam` file will be saved.
- **`options` (object, optional):**
    - **`useTokenization` (boolean, optional):** If `true`, the function will enable word tokenization. Defaults to `false`.
    - **`virtualFiles` (object | string[], optional):** In-memory files to add to the archive. See examples below.

## Usage Example

### Archiving a Directory

```javascript
const { archive } = require('./src/index');

archive('./my_project', 'my_project.ptam').then(() => {
    console.log('Archiving complete!');
});
```

### Using Virtual Files

You can add files to the archive from memory using the `virtualFiles` option.

#### With an Object (specifying file paths)

```javascript
const { archive } = require('./src/index');

const virtualFiles = {
    'docs/manual.txt': 'This is the manual.',
    'main.txt': 'This is the main file.'
};

archive(null, 'virtual_files.ptam', { virtualFiles }).then(() => {
    console.log('Archiving complete!');
});
```

#### With an Array (random file names)

```javascript
const { archive } = require('./src/index');

const virtualFiles = [
    'This is the first file.',
    'This is the second file.'
];

archive(null, 'random_files.ptam', { virtualFiles }).then(() => {
    console.log('Archiving complete!');
});
```
