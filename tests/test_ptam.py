import os
import shutil
import unittest
import filecmp
from ptam.core import archive

class TestPtamArchive(unittest.TestCase):

    SAMPLE_DIR = "tests/sample_data"
    OUTPUT_DIR = "test_output"
    EXPECTED_NORMAL_PTAM = "tests/expected_normal.ptam"
    EXPECTED_TOKENIZED_PTAM = "tests/expected_tokenized.ptam"

    def tearDown(self):
        """Clean up generated directories and files after each test."""
        if os.path.exists(self.OUTPUT_DIR):
            shutil.rmtree(self.OUTPUT_DIR)

    def test_archive_creation_normal(self):
        """Verify that the generated archive matches the expected normal archive."""
        generated_ptam = os.path.join(self.OUTPUT_DIR, "generated_normal.ptam")
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)

        archive(self.SAMPLE_DIR, generated_ptam, use_tokenization=False)

        self.assertTrue(filecmp.cmp(generated_ptam, self.EXPECTED_NORMAL_PTAM),
                        "Generated normal archive does not match the expected one.")

    def test_archive_creation_tokenized(self):
        """Verify that the generated archive matches the expected tokenized archive."""
        generated_ptam = os.path.join(self.OUTPUT_DIR, "generated_tokenized.ptam")
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)

        archive(self.SAMPLE_DIR, generated_ptam, use_tokenization=True)

        self.assertTrue(filecmp.cmp(generated_ptam, self.EXPECTED_TOKENIZED_PTAM),
                        "Generated tokenized archive does not match the expected one.")

if __name__ == '__main__':
    unittest.main()
