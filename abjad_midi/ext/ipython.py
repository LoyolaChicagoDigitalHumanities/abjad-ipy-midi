# -*- coding: utf-8 -*-
'''Abjad-IPython: MIDI Playback
  ----------------------------

  Integrates audio renderings of Abjad MIDI files into IPython
  notebooks using fluidsynth.

  This patch requires fluidsynth to be in your $PATH. If you do not
  have fluidsynth installed, it is likely available in your platform's
  package manager:

    $ brew install fluidsynth
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

def play(expr):
    '''Renders Abjad expression as Vorbis audio, then displays it in the notebook
    as an <audio> tag. This method uses fluidsynth to convert MIDI into an audio
    recording.

    Keyword arguments:
      expr -- Abjad expression to be rendered
    '''

    global font
    global bank

    from base64 import b64encode
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

    fluid_cmd = 'fluidsynth -T oga -nli -r 44200 -o synth.midi-bank-select=%s -F %s %s %s' % (bank, ogg_tmpfile, font, midi_file_path)
    result = systemtools.IOManager.spawn_subprocess(fluid_cmd)
    if result != 0:
        print('Fluidsynth failed to render MIDI as OGG, result: %i' % (result))
        return

    ffmpeg_cmd = 'ffmpeg -i %s %s' % (ogg_tmpfile, mp3_tmpfile)
    result = systemtools.IOManager.spawn_subprocess(ffmpeg_cmd)
    if result == 0:
        with open(mp3_tmpfile, "rb") as audiofile:
           audio_data = audiofile.read()
           audio_encoded = b64encode(audio_data)
           audio_tag = '<audio controls type="audio/mpeg" src="data:audio/mpeg;base64,{0}">'.format(audio_encoded)
           display_html(audio_tag, raw=True)
    else:
        print('ffmpeg failed to render mp3, result: %i' % (result))

def load_ipython_extension(ipython):
    import abjad
    from abjad.tools import topleveltools
    abjad.play = play
    topleveltools.play = play
    ipython.push({'play': play})
    ipython.push({'loadSoundFont': loadSoundFont})

