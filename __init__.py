from mycroft.skills.core import MycroftSkill, intent_handler
from mycroft.util.log import LOG
from adapt.intent import IntentBuilder

import time
import subprocess
import os
from os.path import join, exists
import sys


def save(zork, filename):
    """
        Save game state.
    """
    cmd(zork, 'save')
    time.sleep(0.5)
    clear_until_prompt(zork, ':')
    cmd(zork, filename) # Accept default savegame
    time.sleep(0.5)
    # Check if game returns Ok or query to overwrite
    while True:
        char = zork.stdout.read(1)
        if char == '.':  # Ok. (everything is done)
            break  # The save is complete
        if char == '?':  # Indicates an overwrite query
            cmd(zork, 'y')  # reply yes

    time.sleep(0.5)
    clear_until_prompt(zork)


def restore(zork, filename):
    """
        Restore saved game.
    """
    cmd(zork, 'restore')
    time.sleep(0.5)
    clear_until_prompt(zork, ':')
    cmd(zork, filename)  # Accept default savegame
    time.sleep(0.5)
    clear_until_prompt(zork)

def clear_until_prompt(zork, prompt=None):
    """ Clear all received characters until the standard prompt. """
    # Clear all data with title etecetera
    prompt = prompt or '>'
    char = zork.stdout.read(1)
    while char != prompt:
        char = zork.stdout.read(1)

def cmd(zork, action):
    """ Write a command to the interpreter. """
    zork.stdin.write(action + '\n')

def zork_read(zork):
    """
        Read from zork interpreter process.

        Returns tuple with Room name and description.
    """
    # read Room name
    output = ""
    output += zork.stdout.read(1)
    while output[-1] != '\n':
        output += zork.stdout.read(1)

    room = output.split('Score')[0].strip()

    # Read room info
    output = ""
    output += zork.stdout.read(1)
    while output[-1] != '>':
        output += zork.stdout.read(1)

    # Return room name and description removing the prompt
    return (room, output[:-1])

class ZorkSkill(MycroftSkill):
    def __init__(self):
        super(ZorkSkill, self).__init__()
        self.room = None
        self.playing = False
        self.zork = None

        self.interpreter = join(self._dir, 'frotz/dfrotz')
        self.data = join(self._dir, 'zork/DATA/ZORK1.DAT')
        self.save_file = join(self.file_system.path, 'save.qzl')

    @intent_handler(IntentBuilder('PlayZork').require('Play').require('Zork'))
    def play_zork(self, Message):
        """
            Starts zork and activates the converse part where the actual game
            is played.
        """
        if not self.zork:
            # Start zork using frotz
            self.zork = subprocess.Popen([self.interpreter, self.data],
                                         stdin=subprocess.PIPE,
                                         stdout=subprocess.PIPE)
            time.sleep(0.1)  # Allow to load
            clear_until_prompt(self.zork) # Clear initial startup messages
            # Load default savegame
            if exists(self.save_file):
                restore(self.zork, join(self.save_file))
        # Issue look command to get initial description
        cmd(self.zork, 'look')
        self.room, description = zork_read(self.zork)
        self.speak(description, expect_response=True)
        self.playing = True

    def leave_zork(self):
        self.speak_dialog('LeavingZork')
        self.playing = False
        save(self.zork, self.save_file)
        LOG.info('SAVE COMPLETE!')

    def converse(self, utterance, lang):
        """
            Pass sentence on to the frotz zork interpreter. The commands
            "quit" and "exit" will immediately exit the game.
        """
        if utterance:
            utterance = utterance[0]
            if self.playing:
                if "quit" in utterance or utterance == "exit":
                    self.leave_zork()
                    return True
                else:
                    # Send utterance to zork interpreter and then speak response
                    cmd(self.zork, utterance)
                    self.room, description = zork_read(self.zork)
                    if description != "":
                        self.speak(description, expect_response=True)
                        return True
        return False

    @intent_handler(IntentBuilder('DeleteSave').require('Delete')
                    .require('Zork').require('Save'))
    def delete_save(self, Message):
        if exists(self.save_file):
            os.remove(self.save_file)
            self.speak_dialog('SaveDeleted')
        else:
            self.speak_dialog('NoSave')

    def stop(self, message=None):
        """
            Stop playing
        """
        if self.playing:
            self.leave_zork()


def create_skill():
    return ZorkSkill()
