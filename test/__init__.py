from unittest.mock import patch, MagicMock
from test.integrationtests.skills.skill_tester import SkillTest
import time


class mock_subprocess():
    def __init__(self):
        self.data = b'\n.:>'
        self.pos = 0
        self.stdout = self
        self.stdin = MagicMock()

    def read(self, size=1):
        ret = self.data[self.pos:self.pos + 1]
        self.pos = (self.pos + 1) % len(self.data)
        return ret


@patch('subprocess.Popen')
def test_runner(skill, example, emitter, loader, popen):
    popen.return_value = mock_subprocess()
    # Get the skill object from the skill path
    s = [s for s in loader.skills if s and s.root_dir == skill][0]
    s.save_file = 'dummy'
    with patch(s.__module__ + '.exists') as m:
        m.return_value = False
        return SkillTest(skill, example, emitter).run(loader)
