import unittest
from build_training_copies import patched_target, input_parts


class TrainingCopiesTests(unittest.TestCase):
    def test_patch_does_not_mutate_original_and_requires_exact_old_value(self):
        original={'atomic':[{'key':'k','value':'old'}]}
        repair={'path':['atomic',0,'value'],'old':'old','value':'new'}
        fixed=patched_target(original,[repair])
        self.assertEqual(original['atomic'][0]['value'],'old')
        self.assertEqual(fixed['atomic'][0]['value'],'new')
        with self.assertRaisesRegex(ValueError,'precondition'):
            patched_target(fixed,[repair])

    def test_repair_propagates_to_later_input(self):
        formats={'memory':'Memory {session_number} ({timestamp}):\n{lines}','empty_memory':'empty'}
        before=[{'kind':'narrative','session':1,'date':'2026-01-01','text':'old'}]
        after=[{**before[0],'text':'corrected'}]
        a=input_parts(before,'new session',formats); b=input_parts(after,'new session',formats)
        self.assertNotEqual(a[0],b[0]); self.assertEqual(a[-1],b[-1])


if __name__=='__main__':
    unittest.main()
