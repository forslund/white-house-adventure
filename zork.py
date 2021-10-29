import os
from os.path import exists, join
import requests
import subprocess
import time
import zipfile

from mycroft.util.log import LOG


class ZorkInterpreter:
    def __init__(self, interpreter, data, save_file):
        self.interpreter = interpreter
        self.data = data
        self.save_file = save_file

        LOG.info('Starting Zork')
        # Start zork using frotz
        self.zork = subprocess.Popen([self.interpreter, self.data],
                                     stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE)
        time.sleep(0.1)  # Allow to load
        self.clear_until_prompt()  # Clear initial startup messages
        # Load default savegame
        if exists(self.save_file):
            LOG.info('Loading save game')
            self.restore(join(self.save_file))

    def save(self):
        """Save the game state."""
        self.cmd('save')
        time.sleep(0.5)
        self.clear_until_prompt(':')
        self.cmd(self.save_file)  # Accept default savegame
        time.sleep(0.5)
        # Check if game returns Ok or query to overwrite
        while True:
            char = self.zork.stdout.read(1)
            time.sleep(0.01)
            if char == b'.':  # Ok. (everything is done)
                break  # The save is complete
            if char == b'?':  # Indicates an overwrite query
                self.cmd('y')  # reply yes

        time.sleep(0.5)
        self.clear_until_prompt()

    def delete_save(self):
        if exists(self.save_file):
            os.remove(self.save_file)
            return True
        return False

    def restore(self, filename):
        """Restore saved game."""
        self.cmd('restore')
        time.sleep(0.5)
        self.clear_until_prompt(':')
        self.cmd(filename)  # Accept default savegame
        time.sleep(0.5)
        self.clear_until_prompt()

    def clear_until_prompt(self, prompt='>'):
        """Clear all received characters until the standard prompt."""
        # Clear all data with title etecetera
        LOG.debug('Prompt is {}'.format(prompt))
        char = self.zork.stdout.read(1).decode()
        while char != prompt:
            time.sleep(0.001)
            char = self.zork.stdout.read(1).decode()

    def cmd(self, action):
        """Write a command to the interpreter."""
        self.zork.stdin.write(action.encode() + b'\n')
        self.zork.stdin.flush()

    def read(self):
        """Read from zork interpreter process.

        Returns:
            (tuple) Room name, description.
        """
        # read Room name
        output = ""
        output += self.zork.stdout.read(1).decode()
        while not output or output[-1] != '\n':
            output += self.zork.stdout.read(1).decode()

        room = output.split('Score')[0].strip()

        # Read room info
        output = ""
        output += self.zork.stdout.read(1).decode()
        while output[-1] != '>':
            output += self.zork.stdout.read(1).decode()

        #room = room.replace('\n', '')
        #output = output[:len(room) + 1] + ". " + output[len(room) + 1:]
        #output = output.replace('\n', '')
        # Return room name and description removing the prompt
        return (room, output[:-1])


def install_zork_data(destination_dir):
    """Install the zork data files in destination."""
    zork_data_dir = join(destination_dir, 'zork')
    try:
        os.mkdir(zork_data_dir)
    except FileExistsError:
        pass

    r = requests.get('http://www.infocom-if.org/downloads/zork1.zip',
                     stream=True)
    download_path = '/tmp/zork_data.zip'
    with open(download_path, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=1024):
            fd.write(chunk)

    with zipfile.ZipFile(download_path, 'r') as zip_ref:
        zip_ref.extractall(zork_data_dir)
