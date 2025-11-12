import os
import hashlib
import re
from collections import Counter

def _escape_content(content):
    """
    Escapes special characters ('(', ')', '\\') in file content to prevent
    parsing errors.
    """
    return content.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')

def _get_file_hash(filepath):
    """
    Calculates the SHA-256 hash of a file, reading it in chunks to handle
    large files efficiently.
    """
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def archive(source_directory, output_ptam_file, use_tokenization=False):
    """
    Archives a source directory into a human-readable .ptam file.
    Optionally uses tokenization to reduce file size.
    """
    source_directory = os.path.abspath(source_directory)

    all_paths = []
    text_contents = {}
    has_media_references = False
    word_counts = Counter()

    for dirpath, dirnames, filenames in os.walk(source_directory, topdown=True):
        all_paths.append(dirpath)
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            if os.path.getsize(full_path) == 0:
                continue

            is_binary = False
            try:
                with open(full_path, 'rb') as f:
                    if b'\0' in f.read(1024):
                        is_binary = True
            except IOError:
                is_binary = True

            if is_binary:
                has_media_references = True
                continue

            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                text_contents[full_path] = content
                if use_tokenization:
                    words = re.findall(r'\b[a-zA-Z]{5,}\b', content)
                    word_counts.update(words)
            except (UnicodeDecodeError, IOError):
                has_media_references = True

    tokens = {}
    if use_tokenization:
        token_id = 1
        frequent_words = sorted([word for word, count in word_counts.items() if count >= 5])
        for word in frequent_words:
            tokens[word] = f'${token_id:02}'
            token_id += 1

    header_parts = ["[header]", "# PTAM Archive v1.1", f"# tokenization: {str(use_tokenization and bool(tokens)).lower()}", f"# media_references: {str(has_media_references).lower()}", ""]

    structure_parts = ["[structure]"]
    for path in sorted(all_paths):
        relative_path = os.path.relpath(path, source_directory)
        display_path = "/" if relative_path == "." else "/" + relative_path.replace("\\", "/") + "/"
        structure_parts.append(display_path)
    structure_parts.append("")

    tokens_parts = []
    if use_tokenization and tokens:
        tokens_parts.append("[tokens]")
        for word, token in sorted(tokens.items(), key=lambda item: int(item[1][1:])):
            tokens_parts.append(f'{token}="{word}"')
        tokens_parts.append("")

    archive_parts = []
    for dirpath, dirnames, filenames in sorted(os.walk(source_directory, topdown=True)):
        dirnames.sort()
        filenames.sort()

        relative_path = os.path.relpath(dirpath, source_directory)
        display_path = "/" if relative_path == "." else "/" + relative_path.replace("\\", "/") + "/"
        archive_parts.append(f"[path:{display_path}]")

        for dirname in dirnames:
            archive_parts.append(f"{dirname}/")

        for filename in filenames:
            full_path = os.path.join(dirpath, filename)

            if os.path.getsize(full_path) == 0:
                archive_parts.append(f"{filename}//")
                continue

            if full_path in text_contents:
                content = text_contents[full_path]
                if use_tokenization and tokens:
                    for word, token in tokens.items():
                        content = re.sub(r'\b' + re.escape(word) + r'\b', token, content)

                escaped_content = _escape_content(content)
                archive_parts.append(filename)
                archive_parts.append(f"({escaped_content})")
            else:
                file_hash = _get_file_hash(full_path)
                archive_parts.append(f"{filename} (skipped_binary:sha256:{file_hash})")

        if dirnames or filenames:
            archive_parts.append("")

    final_archive = "\n".join(header_parts) + "\n".join(structure_parts) + "\n".join(tokens_parts) + "\n".join(archive_parts)
    final_archive = final_archive.strip() + "\n[g-end]\n"

    with open(output_ptam_file, 'w', encoding='utf-8') as f:
        f.write(final_archive)
