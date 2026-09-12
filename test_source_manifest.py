import unittest

from adaption_memory.source_manifest import RUNTIME_SOURCE_PATHS, source_hashes


class SourceManifestTests(unittest.TestCase):
    def test_one_manifest_drives_hashing_and_packaging(self):
        hashes = source_hashes()
        self.assertEqual(tuple(hashes), RUNTIME_SOURCE_PATHS)
        self.assertTrue(all(len(value) == 64 for value in hashes.values()))
        self.assertIn("adaption_memory/evaluation/pipeline.py", RUNTIME_SOURCE_PATHS)
        self.assertIn("adaption_memory/execution/vllm_worker.py", RUNTIME_SOURCE_PATHS)


if __name__ == "__main__":
    unittest.main()
