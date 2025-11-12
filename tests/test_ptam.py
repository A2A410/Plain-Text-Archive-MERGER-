import os
import shutil
import unittest
from ptam.core import archive, extract

class TestPtam(unittest.TestCase):

    def setUp(self):
        """Set up a test directory structure for each test."""
        self.test_dir = "test_archive"
        self.output_dir = "test_extract"
        self.ptam_file = "test.ptam"

        # Clean up any previous runs
        self._cleanup()

        os.makedirs(os.path.join(self.test_dir, "folder1", "subfolder1"))
        os.makedirs(os.path.join(self.test_dir, "folder2")) # Empty folder

        with open(os.path.join(self.test_dir, "root_file.txt"), "w") as f:
            f.write("hello world")

        with open(os.path.join(self.test_dir, "folder1", "file1.txt"), "w") as f:
            f.write("this is (file1)")

        with open(os.path.join(self.test_dir, "folder1", "subfolder1", "empty_file.txt"), "w") as f:
            pass

        with open(os.path.join(self.test_dir, "folder1", "binary.data"), "wb") as f:
            f.write(b"\x01\x02\x03\x00\x04")

    def tearDown(self):
        """Clean up test files and directories after each test."""
        self._cleanup()

    def _cleanup(self):
        """Helper to remove test directories and files."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        if os.path.exists(self.ptam_file):
            os.remove(self.ptam_file)

    def test_archive_and_extract_no_tokenization(self):
        """Test the full archive and extract process without tokenization."""
        archive(self.test_dir, self.ptam_file, use_tokenization=False)
        self.assertTrue(os.path.exists(self.ptam_file))

        extract(self.ptam_file, self.output_dir)
        self.assertTrue(os.path.exists(self.output_dir))

        # Verify extracted structure and content
        self.assertTrue(os.path.isdir(os.path.join(self.output_dir, "folder2")))
        root_file_path = os.path.join(self.output_dir, "root_file.txt")
        with open(root_file_path, "r") as f:
            self.assertEqual(f.read(), "hello world")
        empty_file_path = os.path.join(self.output_dir, "folder1", "subfolder1", "empty_file.txt")
        self.assertTrue(os.path.isfile(empty_file_path))
        self.assertEqual(os.path.getsize(empty_file_path), 0)
        self.assertFalse(os.path.exists(os.path.join(self.output_dir, "folder1", "binary.data")))

    def test_new_archive_format_headers(self):
        """Verify the new header format in the .ptam file."""
        archive(self.test_dir, self.ptam_file)
        with open(self.ptam_file, 'r') as f:
            content = f.read()

        self.assertIn("[header]", content)
        self.assertIn("# PTAM Archive v1.1", content)
        self.assertIn("# tokenization: false", content)
        self.assertIn("# media_references: true", content)
        self.assertIn("[structure]", content)
        self.assertIn("/folder1/subfolder1/", content)
        self.assertNotIn("[tokens]", content)
        self.assertTrue(content.strip().endswith("[g-end]"))

    def test_tokenization_feature(self):
        """Test the tokenization and de-tokenization process."""
        # Create a file with words that should be tokenized
        repeat_word_one = "wonderful" # 9 letters
        repeat_word_two = "another"   # 7 letters
        content_to_tokenize = (f"{repeat_word_one} " * 5) + (f"{repeat_word_two} " * 5)
        with open(os.path.join(self.test_dir, "tokenize_me.txt"), "w") as f:
            f.write(content_to_tokenize)

        # 1. Archive with tokenization enabled
        archive(self.test_dir, self.ptam_file, use_tokenization=True)

        # 2. Verify the .ptam file content
        with open(self.ptam_file, 'r') as f:
            archive_content = f.read()

        self.assertIn("# tokenization: true", archive_content)
        self.assertIn("[tokens]", archive_content)
        # Word order is deterministic, 'another' comes before 'wonderful'
        self.assertIn('$01="another"', archive_content)
        self.assertIn('$02="wonderful"', archive_content)
        # Check if content is tokenized
        self.assertIn("($02 $02 $02 $02 $02 $01 $01 $01 $01 $01 )", archive_content)

        # 3. Extract the archive
        extract(self.ptam_file, self.output_dir)

        # 4. Verify the extracted file is correctly de-tokenized
        extracted_file_path = os.path.join(self.output_dir, "tokenize_me.txt")
        self.assertTrue(os.path.isfile(extracted_file_path))
        with open(extracted_file_path, "r") as f:
            self.assertEqual(f.read(), content_to_tokenize)

    def test_backward_compatibility_extract(self):
        """Ensure extract can read old-format archives without headers."""
        # Create a fake old-format archive
        old_format_content = """
[path:/]
my_file.txt
(hello from the past)
empty_dir/
"""
        with open(self.ptam_file, "w") as f:
            f.write(old_format_content)

        extract(self.ptam_file, self.output_dir)

        # Verify extraction
        self.assertTrue(os.path.isdir(os.path.join(self.output_dir, "empty_dir")))
        old_file_path = os.path.join(self.output_dir, "my_file.txt")
        self.assertTrue(os.path.isfile(old_file_path))
        with open(old_file_path, "r") as f:
            self.assertEqual(f.read(), "hello from the past")


if __name__ == '__main__':
    unittest.main()
