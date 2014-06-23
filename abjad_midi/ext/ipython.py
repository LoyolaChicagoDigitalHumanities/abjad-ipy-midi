# -*- coding: utf-8 -*-
'''Abjad-IPython: MIDI Playback
  ----------------------------

  Integrates audio renderings of Abjad MIDI files into IPython
  notebooks using fluidsynth.

  This patch requires fluidsynth to be in your $PATH. If you do not
  have fluidsynth installed, it is likely available in your platform's
  package manager:

  OS X
    $ brew install fluidsynth --with-libsndfile
    $ port install fluidsynth

  Linux
    $ apt-get install fluidsynth

'''

import os
import os.path
import tempfile
from IPython.core.display import display_html

# 
# Global (module) variables set by loadSoundFont() only
#

font=None
bank='gs'

def loadSoundFont(soundfont, midibank):
    '''Saves location of argument SoundFont and its type. Type can be
    either 'gs', 'gm', 'xg', or 'mma'.
    '''
    global font
    global bank

    if os.path.isfile(soundfont):
        font = soundfont
    else: 
        print('The specified SoundFont %s (relative to %s) is either inaccessible or does not exist.' % (soundfont, os.getcwd()))
    allowed_banks = ['gs', 'gm', 'xg', 'mma']
    if midibank in allowed_banks: 
        bank = midibank
    else:
        print("The MIDI Bank must be either be one of %s" % (str(allowed_banks)))


def get_b64_from_file(filename):
    '''This allows us to reliably read (and encode for HTML) the base64 representation of a file in Python 2 or 3.
    Python 2 uses 'str' when reading a binary file entirely. Python 3 uses 'bytes'.
    '''
    import base64
    with open(filename, "rb") as infile:
        data = infile.read()
        if type(data) != type(''):
            return base64.b64encode(data).decode('utf-8')
        else:
            return base64.b64encode(data)

def play(expr):
    '''Renders Abjad expression as Vorbis audio, then displays it in the notebook
    as an <audio> tag. This method uses fluidsynth to convert MIDI into an audio
    recording.

    Keyword arguments:
      expr -- Abjad expression to be rendered
    '''

    global font
    global bank

    from abjad.tools import systemtools, topleveltools
    assert '__illustrate__' in dir(expr)

    if not font:
        print('Soundfont is not specified, please call \'loadSoundFount(soundfont, midibank)\'')
        return

    tmpdir = tempfile.mkdtemp()
    agent = topleveltools.persist(expr)
    result = agent.as_midi( os.path.join(tmpdir, 'out.mid'))
    midi_file_path, format_time, render_time = result 

    ogg_tmpfile = os.path.join(tmpdir, 'out.ogg')
    mp3_tmpfile = os.path.join(tmpdir, 'out.mp3')

    # TODO: Could make this user selectable.
    # OGG rendering
    fluid_cmd = 'fluidsynth -T oga -nli -r 44200 -o synth.midi-bank-select=%s -F %s %s %s' % (bank, ogg_tmpfile, font, midi_file_path)
    print(fluid_cmd)
    result = systemtools.IOManager.spawn_subprocess(fluid_cmd)
    if result == 0:
        audio_encoded = get_b64_from_file(ogg_tmpfile)
        audio_tag = '<audio controls type="audio/ogg" src="data:audio/ogg;base64,{0}">'.format(audio_encoded)
        display_html(audio_tag, raw=True)
    else:
        print('fluidsynth failed to render MIDI as OGG, result: %i' % (result))
        return

    # MP3 Rendering
    ffmpeg_cmd = 'ffmpeg -i %s %s' % (ogg_tmpfile, mp3_tmpfile)
    print(ffmpeg_cmd)
    result = systemtools.IOManager.spawn_subprocess(ffmpeg_cmd)
    if result == 0:
        audio_encoded = get_b64_from_file(mp3_tmpfile)
        audio_tag = '<audio controls type="audio/mpeg" src="data:audio/mpeg;base64,{0}">'.format(audio_encoded)
        display_html(audio_tag, raw=True)
    else:
        print('ffmpeg failed to render OGG as MP3, result: %i' % (result))

def load_ipython_extension(ipython):
    import abjad
    from abjad.tools import topleveltools
    abjad.play = play
    topleveltools.play = play
    ipython.push({'play': play})
    ipython.push({'loadSoundFont': loadSoundFont})

