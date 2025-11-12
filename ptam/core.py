import os
import hashlib
import re

def _escape_content(content):
    """
    Escapes special characters ('(', ')', '\\') in file content to prevent
    parsing errors.
    """
    return content.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')

def _unescape_content(content):
    """
    Un-escapes special characters in file content during extraction.
    """
    return content.replace('\\)', ')').replace('\\(', '(').replace('\\\\', '\\')

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

def archive(source_directory, output_ptam_file):
    """
    Archives a source directory into a human-readable .ptam file.
    """
    archive_parts = []
    source_directory = os.path.abspath(source_directory)

    paths_to_process = []
    for dirpath, dirnames, filenames in os.walk(source_directory, topdown=True):
        paths_to_process.append((dirpath, dirnames, filenames))

    paths_to_process.sort(key=lambda x: x[0].count(os.sep))

    for dirpath, dirnames, filenames in paths_to_process:
        dirnames.sort()
        filenames.sort()

        relative_path = os.path.relpath(dirpath, source_directory)
        display_path = "/" if relative_path == "." else "/" + relative_path.replace("\\", "/") + "/"

        archive_parts.append(f"[path:{display_path}]")

        # Unambiguous format: All directories end with a single '/'
        for dirname in dirnames:
            archive_parts.append(f"{dirname}/")

        for filename in filenames:
            full_path = os.path.join(dirpath, filename)

            # Unambiguous format: Empty files end with '//'
            if os.path.getsize(full_path) == 0:
                archive_parts.append(f"{filename}//")
                continue

            is_text = True
            content = ""
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if '\0' in content[:1024]:
                    is_text = False
            except (UnicodeDecodeError, IOError):
                is_text = False

            if is_text:
                escaped_content = _escape_content(content)
                archive_parts.append(f"{filename}")
                archive_parts.append(f"({escaped_content})")
            else:
                file_hash = _get_file_hash(full_path)
                archive_parts.append(f"{filename} (skipped_binary:sha256:{file_hash})")

        if dirnames or filenames:
            archive_parts.append("")

    with open(output_ptam_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(archive_parts).strip() + "\n")

def extract(ptam_file, output_directory):
    """
    Extracts a .ptam archive to a specified directory.
    """
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    with open(ptam_file, 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()

    current_dir = ""
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        if line.startswith("[path:"):
            path_match = re.match(r'\[path:(.*?)\]', line)
            if path_match:
                current_path_str = path_match.group(1)
                if current_path_str == "/":
                    current_dir = output_directory
                else:
                    parts = current_path_str.strip('/').split('/')
                    current_dir = os.path.join(output_directory, *parts)

                if not os.path.exists(current_dir):
                    os.makedirs(current_dir)
            i += 1
            continue

        # Unambiguous parsing logic
        if line.endswith("//"): # Empty file
            name = line[:-2]
            path = os.path.join(current_dir, name)
            open(path, 'w').close()
            i += 1
        elif line.endswith("/"): # Directory
            name = line[:-1]
            path = os.path.join(current_dir, name)
            if not os.path.exists(path):
                os.makedirs(path)
            i += 1
        elif "(skipped_binary:" in line:
            i += 1
        else: # File with content
            filename = line
            filepath = os.path.join(current_dir, filename)
            i += 1
            if i < len(lines) and lines[i].strip().startswith("("):
                content_line = lines[i].strip()
                if content_line.startswith("(") and content_line.endswith(")"):
                    content = content_line[1:-1]
                    unescaped_content = _unescape_content(content)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(unescaped_content)
                i += 1
            else:
                open(filepath, 'w').close()
