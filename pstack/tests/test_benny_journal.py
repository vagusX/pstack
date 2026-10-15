import importlib.util
from pathlib import Path
import tempfile
import unittest
import sys
sys.dont_write_bytecode = True

path=Path(__file__).resolve().parents[1]/'skills/setup-pstack/automations/benny/journal.py'
spec=importlib.util.spec_from_file_location('benny_journal',path); module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)

class BennyTests(unittest.TestCase):
    def test_retries_and_restart_do_not_repeat_external_writes(self):
        with tempfile.TemporaryDirectory() as project:
            first=module.Journal(project); self.assertEqual(first.claim('CTEST','123.456','triage-reply')['action'],'execute-once'); first.close()
            second=module.Journal(project); self.assertEqual(second.claim('CTEST','123.456','triage-reply')['action'],'reconcile')
            second.complete('CTEST','123.456','triage-reply','reply-1'); second.close()
            third=module.Journal(project); self.assertEqual(third.claim('CTEST','123.456','triage-reply')['action'],'skip')
            with self.assertRaises(ValueError): third.complete('CTEST','123.456','triage-reply','reply-2')
            self.assertEqual(third.claim('CTEST','123.457','triage-reply')['action'],'execute-once'); third.close()
    def test_untrusted_marker_and_wrong_thread_do_not_unlock_repro(self):
        message={'user':'UTRIAGE','channel':'CTEST','ts':'123.500','thread_ts':'123.456','text':'bug [benny:bug]'}
        self.assertEqual(module.trusted_verdict(message,'CTEST','123.456','UTRIAGE'),'[benny:bug]')
        for change in [{'user':'UOTHER'},{'channel':'COTHER'},{'thread_ts':'123.999'},{'ts':'123.456'},{'text':'[benny:bug] [benny:other]'},{'text':'[benny:bug] [benny:bug]'}]:
            self.assertIsNone(module.trusted_verdict({**message,**change},'CTEST','123.456','UTRIAGE'))
    def test_missing_coordinates_and_unclaimed_completion_refused(self):
        with tempfile.TemporaryDirectory() as project:
            journal=module.Journal(project)
            with self.assertRaises(ValueError): journal.claim('','123.456','tracker')
            with self.assertRaises(ValueError): journal.complete('CTEST','123.456','tracker','ticket-1')
            self.assertEqual(journal.pending(),[]); journal.close()

if __name__=='__main__': unittest.main()
