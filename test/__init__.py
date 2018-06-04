from unittest.mock import patch, MagicMock
from test.integrationtests.skills.skill_tester import SkillTest

def test_runner(skill, example, emitter, loader):
    # Get the skill object from the skill path
    s = [s for s in loader.skills if s and s.root_dir == skill][0]
    s.save_file = 'dummy'
    with patch(s.__module__ + '.exists') as m:
        m.return_value = False
        return SkillTest(skill, example, emitter).run(loader)
