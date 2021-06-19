from os.path import join

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill, intent_handler

from .zork import ZorkInterpreter


class ZorkSkill(MycroftSkill):
    def __init__(self):
        super(ZorkSkill, self).__init__()
        self.room = None
        self.playing = False
        self.zork = None

        self.interpreter = join(self.root_dir, 'frotz/dfrotz')
        self.data = join(self.root_dir, 'zork/DATA/ZORK1.DAT')
        self.save_file = join(self.file_system.path, 'save.qzl')

    @intent_handler(IntentBuilder('PlayZork').require('Play').require('Zork'))
    def play_zork(self, Message):
        """Starts zork and activates the converse part.

        Converse then handles the actual gameplay.
        """
        if not self.zork:
            self.zork = ZorkInterpreter(self.interpreter,
                                        self.data,
                                        self.save_file)
        # Issue look command to get initial description
        self.zork.cmd('look')
        self.room, description = self.zork.read()
        self.speak(description, expect_response=True)
        self.playing = True

    def leave_zork(self):
        self.speak_dialog('LeavingZork')
        self.playing = False
        self.zork.save()
        self.log.info('Zork savegame has been created')

    def converse(self, message):
        """Pass sentence on to the frotz zork interpreter.

        The commands "quit" and "exit" will immediately exit the game.
        """
        utterances = message.data['utterances']
        if utterances:
            utterance = utterances[0]
            if self.playing:
                if "quit" in utterance or utterance == "exit":
                    self.leave_zork()
                    return True
                else:
                    # Send utterance to zork interpreter and then
                    # speak response
                    self.zork.cmd(utterance)
                    self.room, description = self.zork.read()
                    if description != "":
                        self.speak(description, expect_response=True)
                        return True
        return False

    @intent_handler(IntentBuilder('DeleteSave').require('Delete')
                    .require('Zork').require('Save'))
    def delete_save(self, Message):
        if self.zork.delete_save():
            self.speak_dialog('SaveDeleted')
        else:
            self.speak_dialog('NoSave')

    def stop(self, message=None):
        """Stop playing."""
        if self.playing:
            self.leave_zork()


def create_skill():
    return ZorkSkill()
