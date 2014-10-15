# -*- coding: utf-8 -*-
'''
Abjad-IPython: MIDI Playback
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
# Global (module) variables set by load_sound_font() only
#

font = None
bank = 'gs'


def load_sound_font(soundfont, midibank):
    '''Save location of argument SoundFont and its type.

    Type can be either 'gs', 'gm', 'xg', or 'mma'.
    '''
    global font
    global bank

    if os.path.isfile(soundfont):
        font = soundfont
    else:
        message = 'The specified SoundFont {} (relative to {}) '
        message += 'is either inaccessible or does not exist.'
        message = message.format(soundfont, os.getcwd())
        print(message)
    allowed_banks = ('gs', 'gm', 'xg', 'mma')
    if midibank in allowed_banks:
        bank = midibank
    else:
        message = 'The MIDI Bank must be either be one of {!s}'
        message = message.format(allowed_banks)
        print(message)


def get_b64_from_file(filename):
    '''Read the base64 representation of a file and encode for HTML.
    '''
    import base64
    with open(filename, "rb") as infile:
        data = infile.read()
        if type(data) != type(''):
            return base64.b64encode(data).decode('utf-8')
        else:
            return base64.b64encode(data)


def play(expr):
    '''Render `expr` as Vorbis audio and display it in the IPythpn notebook
    as an <audio> tag.

    This function requires `fluidsynth` and `ffmpeg` to convert MIDI into an
    audio recording.
    '''

    global font
    global bank

    from abjad.tools import systemtools, topleveltools
    assert '__illustrate__' in dir(expr)

    if not font:
        message = 'Soundfont is not specified, please call '
        message += "'loadSoundFount(soundfont, midibank)\'"
        print(message)
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
        message = 'fluidsynth failed to render MIDI as OGG, result: {!i}'
        message = message.format(result)
        print(message)
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
        message = 'ffmpeg failed to render OGG as MP3, result: {!i}'
        message = message.format(result)
        print(message)


def load_ipython_extension(ipython):
    import abjad
    from abjad.tools import topleveltools
    abjad.play = play
    topleveltools.play = play
    ipython.push({'play': play})
    ipython.push({'load_sound_font': load_sound_font})