from os import system, name, path, environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

from mutagen.mp3 import MP3
import pygame
from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit import HTML
from prompt_toolkit.completion import WordCompleter
import sys


# Auto completer
completer = WordCompleter(['play',
                           'exit',
                           'resume',
                           'pause',
                           'stop',
                           'clear',
                           'restart',
                           'length',
                           'vol',
                           'setvol',
                           'progress',
                           'status'],
                          ignore_case=True)

# Input session
session = PromptSession(completer=completer)

# Clearing the terminal window depending on platform
def clear():
    if name == "nt":
        system('cls')
    else:
        system('clear')

# Start Pygame
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.mixer.init()
pygame.init()
clear()

# Class for mp3 files using pygame.mixer.music
class MP3Player:
    def __init__(self, file):
        self.file = file

    def play(self):
        pygame.mixer.music.load(self.file)
        pygame.mixer.music.play()

    def stop(self):
        pygame.mixer.music.stop()

    def unpause(self):
        pygame.mixer.music.unpause()

    def pause(self):
        pygame.mixer.music.pause()

    def get_music_length(self):
        return round(MP3(self.file).info.length)

    def get_pos(self):
        return pygame.mixer.music.get_pos()

    def restart(self):
        pygame.mixer.music.rewind()

    def get_volume(self):
        return pygame.mixer.music.get_volume()

    def set_volume(self, volume):
        pygame.mixer.music.set_volume(float(volume))

    def queue(self, file):
        pygame.mixer.music.queue(file)

# Class for parsing and executing user input
class Terminal:
    def __init__(self) -> None:
        # MP3 Player
        self.player = None
        self.help = lambda: 'https://github.com/TheLegendBeacon/pymusic-player/blob/3f38001e40d00e613f57813cf26c0e022a243432/README.md'
        self.playing = False
        self.paused = False
        self.volume = 1.0

        # All functions required for operation
        self.functions = {
            'exit': sys.exit,
            'play': self.play,
            'resume': self.resume,
            'pause': self.pause,
            'stop': self.stop,
            'restart': self.restart,
            'progress': self.progress,
            'clear': self.clear,
            'length': self.length,
            'vol': self.vol,
            'setvol': self.set_volume,
            'status': self.status,
            'help': self.help
        }

    def clear(self):
        clear()

    # Status function - Shows essential info
    def status(self):
        if self.playing:
            return f"Playing: {self.player.file}, Paused: {self.paused}\n{self.progress()}"
        else:
            return "Not playing anything."

    # Toolbar
    def toolbar_string(self):
        return f'''<b>[play]</b> play <b>[stop]</b> stop  <b>[pause]</b> pause <b>[exit]</b> exit <b>[resume]</b> resume <b>[clear]</b> clear <b>|</b> volume: {int(self.volume*100)}%'''

    # Starts playing the mp3
    def play(self, filepath):
        if path.isfile(filepath):
            if self.playing:
                self.stop()

            filepath = filepath.replace("\\", "/")
            self.player = MP3Player(filepath)
            self.player.play()
            self.player.set_volume(self.volume)
            self.playing = True
            self.paused = False
            return "Started playing."
        else:
            return "Error: File Not Found."


    # Stops playing the mp3
    def stop(self):
        if self.playing:
            self.player.stop()
            self.playing = False
            self.paused = False
            return "Stopped."
        else:
            return "Nothing is playing right now."

    # Pause the mp3
    def pause(self):
        if self.playing:
            if self.paused:
                return "You are already paused."
            else:
                self.player.pause()
                self.paused = True
                return "Paused the track."
        else:
            return "You are not playing anything."

    # Resumes playing the mp3
    def resume(self):
        if self.playing:
            if self.paused:
                self.player.unpause()
                self.paused = False
                return "Successfully resumed."
            else:
                return "You are already playing."
        else:
            return "Nothing is playing right now."

    # Restarts playing the mp3 from the beginning
    def restart(self):
        if self.playing:
            self.player.restart()
            return "Restarted the track."
        else:
            return "Nothing is playing right now."

    # returns the length of the mp3
    def length(self):
        if self.playing:
            seclength = self.player.get_music_length()
            minlength, seclength = seclength // 60, seclength % 60
            hourlength, minlength = minlength // 60, minlength % 60

            if hourlength == 0:
                return f"{minlength} minutes and {seclength} seconds"
            else:
                return f"{hourlength} hours, {minlength} minutes and {seclength} seconds"
        else:
            return "Nothing is playing right now."

    # returns the volume of the mp3
    def vol(self):
        return f"{str(int(self.volume*100))}%"

    # Sets the volume of the mp3
    def set_volume(self, volume):
        volume = volume.replace("%", '')
        if int(float(volume)) > 100 and int(float(volume)) > 0:
            return r"You need a value between 0% and 100%."
        else: 
            self.volume = int(float(volume)) / 100
            pygame.mixer.music.set_volume(self.volume)
            return f"Set volume to {int(100*self.volume)}%"

    # Returns a progress bar
    def progress(self):
        if self.playing:
            progressBar = ['-' for x in range(50)]
            length = self.player.get_music_length()
            pos = self.player.get_pos() // 1000
            ratio = round(pos / length * 50)
            for x in range(ratio):
                progressBar[x] = "█"
            return f"\n|{''.join(progressBar)}| {pos}/{length} seconds, {length-pos} sec ETA\n"
        else:
            return "You are not playing anything."

    # Parses user input and runs it
    def parse(self, inp):

        inWords = inp.split()
        if not inWords:
            return " "
        if len(inWords) > 2:
            inWords = [inWords[0], " ".join(inWords[1:])]

        inWords[0] = inWords[0].lower()
        keywords = [
            'play',
            'exit',
            'resume',
            'pause',
            'stop',
            'clear',
            'restart',
            'length',
            'vol',
            'setvol',
            'progress',
            'status',
            'help']

        if inWords[0] in keywords:
            if len(inWords) == 1:
                if inWords[0] == 'exit':
                    sys.exit()
                else:
                    try:
                        result = self.functions[inWords[0]]()
                        return result
                    except BaseException:
                        return f"Invalid Syntax: {inp}"
            else:
                try:
                    result = self.functions[inWords[0]](inWords[1])
                    return result
                except BaseException:
                    return f"Invalid Syntax: {inp}"

        else:
            return f"Invalid Syntax: {inp}: Not a valid keyword."


kb = KeyBindings()
terminal = Terminal()

# Short Cuts
@kb.add('c-u')
def _(*args):
    if terminal.paused:
        terminal.resume()
    else:
        terminal.pause()


@kb.add('c-x')
def _(*args):
    terminal.stop()


@kb.add('c-r')
def _(*args):
    terminal.restart()


@kb.add('c-up')
def _(*args):
    terminal.set_volume(str(terminal.volume * 100 + 10))


@kb.add('c-down')
def _(*args):
    terminal.set_volume(str(terminal.volume * 100 - 10))

# Main function
while True:
    try:
        inp = session.prompt(
            "\n❯ ",
            bottom_toolbar=HTML(
                terminal.toolbar_string()),
            key_bindings=kb)
        output = terminal.parse(inp)
        output = [output if output is not None else " "][0]
        print(output)
    except (KeyboardInterrupt, EOFError):
        print("\nThanks For Using!")
        sys.exit()
    except BaseException:
        print("There was an error.")
        sys.exit()
