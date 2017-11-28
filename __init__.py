from mycroft.skills.core import MycroftSkill, intent_handler
from adapt.intent import IntentBuilder

import time
import subprocess
from os.path import join
import sys


def clear_until_prompt(zork):
    # Clear all data with title etecetera
    char = zork.stdout.read(1)
    while char != '>':
        char = zork.stdout.read(1)

def cmd(zork, action):
    zork.stdin.write(action + '\n')

def zork_read(zork):
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


    @intent_handler(IntentBuilder('PlayZork').require('Play').require('Zork'))
    def play_zork(self, Message):
        if not self.zork:
            self.zork = subprocess.Popen([self.interpreter, self.data],
                                         stdin=subprocess.PIPE,
                                         stdout=subprocess.PIPE)
            time.sleep(0.5)
            clear_until_prompt(self.zork)

        cmd(self.zork, 'look')
        self.room, description = zork_read(self.zork)
        self.speak(description, expect_response=True)
        self.playing = True

    def converse(self, utterance, lang):
        utterance = utterance[0]
        if self.playing:
            if "quit" in utterance or utterance == "exit":
                self.speak("Leaving the mysterious kingdom of Zork")
                self.playing = False
                return True
            else:
                cmd(self.zork, utterance)
                self.room, description = zork_read(self.zork)
                if description != "":
                    self.speak(description, expect_response=True)
                    return True
        return False

    def stop(self, message):
        self.playing = False


def create_skill():
    return ZorkSkill()
