import unittest

from qwen_gpu_sizing import RATE, RESERVE, TIMEOUT, left_pad, trim_output


class SizingTests(unittest.TestCase):
    def test_left_padding_and_mask(self):
        self.assertEqual(left_pad([[1, 2], [3]], 9), ([[1, 2], [9, 3]], [[1, 1], [0, 1]]))

    def test_eos_does_not_count_batch_padding(self):
        self.assertEqual(trim_output([4, 8, 9, 9], [8, 9]), ([4, 8], 'stop'))
        self.assertEqual(trim_output([4, 5], [9]), ([4, 5], 'length'))

    def test_budget(self):
        self.assertLessEqual(TIMEOUT * RATE + RESERVE, 2)


if __name__ == '__main__':
    unittest.main()
