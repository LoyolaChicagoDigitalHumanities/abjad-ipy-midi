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
import tempfile
from IPython.core.display import display_html

font=None
bank='gs'

def loadSoundFont(soundfont, midibank):
    '''Saves location of argument SoundFont and its type. Type can be
    either 'gs', 'gm', 'xg', or 'mma'.
    '''
    global font

    if os.path.isfile(soundfont):
        font = soundfont
    else: 
        print('The specified SoundFont %s (relative to %s) is either inaccessible or does not exist.' % (soundfont, os.getcwd()))
    
    if(midibank == 'gs' or midibank == 'gm' or midibank == 'xg' or midibank == 'mma'): 
        bank = midibank
    else:
        print("The MIDI Bank must be either be 'gm', 'gs', 'xg', or 'mma'.")

def play(expr):
    '''Renders Abjad expression as Vorbis audio, then displays it in the notebook
    as an <audio> tag. This method uses fluidsynth to convert MIDI into an audio
    recording.

    Keyword arguments:
      expr -- Abjad expression to be rendered
    '''

    global font
    from base64 import b64encode
    from abjad.tools import systemtools, topleveltools
    assert '__illustrate__' in dir(expr)

    if font:
        tmpdir = tempfile.mkdtemp()
        agent = topleveltools.persist(expr)
        result = agent.as_midi(tmpdir + os.sep + 'out.mid')
        midi_file_path, format_time, render_time = result 

        tmpaudio = tmpdir + os.sep + 'out.ogg'
        cmd = 'fluidsynth -nli -r 48000 -o synth.cpu-cores=2 synth.midi-bank-select=%s -T oga -F %s %s %s' % (bank, tmpaudio, font, midi_file_path)
        result = systemtools.IOManager.spawn_subprocess(cmd)

        if result == 0:
            audio_file = open(tmpaudio, "rb").read()
            audio_encoded = b64encode(audio_file)
            audio_tag = '<audio controls type="audio/ogg" src="data:audio/ogg;base64,{0}">'.format(audio_encoded)
            display_html(audio_tag, raw=True)
        else:
            print('Fluidsynth failed to render MIDI, result: %i' % (result))
    else:
        print('Soundfont is not specified, please call \'loadSoundFount(soundfont, midibank)\'')

def load_ipython_extension(ipython):
    import abjad
    from abjad.tools import topleveltools
    abjad.play = play
    topleveltools.play = play
    ipython.push({'play': play})
    ipython.push({'loadSoundFont': loadSoundFont})

