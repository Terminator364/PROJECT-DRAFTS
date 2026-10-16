import json, tempfile, unittest
from pathlib import Path
from journal_tool import append,inspect,JournalError

def event(i=1):return {'id':f'E{i:04d}','date':'2026-10-16','origin':'user','type':'USER_FEEDBACK',
                        'summary':'Tester la continuité','evidence':[], 'confidence':'EXPLICIT', 'supersedes':None}

class JournalTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.p=Path(self.tmp.name)/'journal.jsonl'
    def tearDown(self):self.tmp.cleanup()
    def test_empty(self):self.assertEqual(inspect(self.p),[])
    def test_append(self):append(self.p,event());self.assertEqual(len(inspect(self.p)),1)
    def test_chain(self):
        append(self.p,event());append(self.p,event(2));x=inspect(self.p)
        self.assertEqual(x[0]['digest'],x[1]['previous_digest'])
    def test_duplicate(self):
        append(self.p,event())
        with self.assertRaises(JournalError):append(self.p,event())
    def test_tamper(self):
        append(self.p,event());x=self.p.read_text().replace('Tester la continuité','Contenu réécrit')
        self.p.write_text(x)
        with self.assertRaises(JournalError):inspect(self.p)
    def test_swap_lines(self):
        append(self.p,event());append(self.p,event(2));self.p.write_text('\n'.join(reversed(self.p.read_text().splitlines()))+'\n')
        with self.assertRaises(JournalError):inspect(self.p)
    def test_bad_schema(self):
        e=event();e['hidden']=1
        with self.assertRaises(JournalError):append(self.p,e)
    def test_bad_type(self):
        e=event();e['type']='AUTOPROMOTION'
        with self.assertRaises(JournalError):append(self.p,e)
    def test_bad_json(self):
        self.p.write_text('badjson\n')
        with self.assertRaises(JournalError):inspect(self.p)
    def test_no_fabricated_external_timestamp_proof(self):
        append(self.p,event());self.assertNotIn('trusted_timestamp',inspect(self.p)[0])

if __name__=='__main__':unittest.main()
