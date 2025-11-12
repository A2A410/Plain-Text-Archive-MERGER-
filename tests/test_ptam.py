import os
import shutil
import unittest
from ptam.core import archive, extract

class TestPtam(unittest.TestCase):

    def setUp(self):
        """Set up a test directory structure."""
        self.test_dir = "test_archive"
        self.output_dir = "test_extract"
        self.ptam_file = "test.ptam"

        # Clean up previous runs
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        if os.path.exists(self.ptam_file):
            os.remove(self.ptam_file)

        os.makedirs(os.path.join(self.test_dir, "folder1", "subfolder1"))
        os.makedirs(os.path.join(self.test_dir, "folder2")) # Empty folder

        with open(os.path.join(self.test_dir, "root_file.txt"), "w") as f:
            f.write("hello world")

        with open(os.path.join(self.test_dir, "folder1", "file1.txt"), "w") as f:
            f.write("this is (file1)")

        with open(os.path.join(self.test_dir, "folder1", "subfolder1", "empty_file.txt"), "w") as f:
            pass

        # Create a dummy binary file
        with open(os.path.join(self.test_dir, "folder1", "binary.data"), "wb") as f:
            f.write(b"\x01\x02\x03\x00\x04")

    def tearDown(self):
        """Clean up test files and directories."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        if os.path.exists(self.ptam_file):
            os.remove(self.ptam_file)

    def test_archive_and_extract(self):
        """Test the full archive and extract process."""
        # 1. Archive the test directory
        archive(self.test_dir, self.ptam_file)
        self.assertTrue(os.path.exists(self.ptam_file))

        # 2. Extract the archive
        extract(self.ptam_file, self.output_dir)
        self.assertTrue(os.path.exists(self.output_dir))

        # 3. Verify the extracted structure and content

        # Check directories
        self.assertTrue(os.path.isdir(os.path.join(self.output_dir, "folder1")))
        self.assertTrue(os.path.isdir(os.path.join(self.output_dir, "folder1", "subfolder1")))
        self.assertTrue(os.path.isdir(os.path.join(self.output_dir, "folder2")))
        self.assertEqual(len(os.listdir(os.path.join(self.output_dir, "folder2"))), 0) # folder2 should be empty

        # Check files and their content
        root_file_path = os.path.join(self.output_dir, "root_file.txt")
        self.assertTrue(os.path.isfile(root_file_path))
        with open(root_file_path, "r") as f:
            self.assertEqual(f.read(), "hello world")

        file1_path = os.path.join(self.output_dir, "folder1", "file1.txt")
        self.assertTrue(os.path.isfile(file1_path))
        with open(file1_path, "r") as f:
            self.assertEqual(f.read(), "this is (file1)")

        empty_file_path = os.path.join(self.output_dir, "folder1", "subfolder1", "empty_file.txt")
        self.assertTrue(os.path.isfile(empty_file_path))
        self.assertEqual(os.path.getsize(empty_file_path), 0)

        # Check that the binary file was not extracted
        binary_file_path = os.path.join(self.output_dir, "folder1", "binary.data")
        self.assertFalse(os.path.exists(binary_file_path))

    def test_ptam_file_content(self):
        """Verify the content of the .ptam file itself."""
        archive(self.test_dir, self.ptam_file)

        with open(self.ptam_file, 'r') as f:
            content = f.read()

        # These are simple checks, a more robust test might parse the file
        self.assertIn("[path:/]", content)
        self.assertIn("root_file.txt", content)
        self.assertIn("(hello world)", content)
        self.assertIn("file1.txt", content)
        self.assertIn("(this is \\(file1\\))", content) # Check escaping
        self.assertIn("empty_file.txt//", content)
        self.assertIn("folder2/", content) # Asserting the correct, unambiguous format
        self.assertIn("binary.data (skipped_binary:sha256:", content)

if __name__ == '__main__':
    unittest.main()
