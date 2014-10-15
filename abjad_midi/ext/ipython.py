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

sound_font = None
midi_bank = 'gs'


def load_sound_font(new_sound_font, new_midi_bank):
    '''Save location of argument sound_font and its type.

    Type can be either 'gs', 'gm', 'xg', or 'mma'.
    '''
    global sound_font
    global midi_bank

    if os.path.isfile(new_sound_font):
        sound_font = new_sound_font
    else:
        message = 'The specified sound_font {} (relative to {}) '
        message += 'is either inaccessible or does not exist.'
        message = message.format(new_sound_font, os.getcwd())
        print(message)
    valid_midi_banks = ('gs', 'gm', 'xg', 'mma')
    if new_midi_bank in valid_midi_banks:
        midi_bank = new_midi_bank
    else:
        message = 'The MIDI bank must be either be one of {!s}'
        message = message.format(valid_midi_banks)
        print(message)


def get_b64_from_file(file_name):
    '''Read the base64 representation of a file and encode for HTML.
    '''
    import base64
    import sys
    with open(file_name, 'rb') as file_pointer:
        data = file_pointer.read()
        if sys.version_info[0] == 2:
            return base64.b64encode(data).decode('utf-8')
        else:
            return base64.b64encode(data)


def play(expr):
    '''Render `expr` as Vorbis audio and display it in the IPythpn notebook
    as an <audio> tag.

    This function requires `fluidsynth` and `ffmpeg` to convert MIDI into an
    audio recording.
    '''

    global sound_font
    global midi_bank

    from abjad.tools import systemtools, topleveltools
    assert '__illustrate__' in dir(expr)

    if not sound_font:
        message = 'sound_font is not specified, please call '
        message += "'load_sound_font(sound_font, midi_bank)\'"
        print(message)
        return

    tmpdir = tempfile.mkdtemp()
    agent = topleveltools.persist(expr)
    result = agent.as_midi(os.path.join(tmpdir, 'out.mid'))
    midi_file_path, format_time, render_time = result

    ogg_file_path = os.path.join(tmpdir, 'out.ogg')
    mp3_file_path = os.path.join(tmpdir, 'out.mp3')

    # OGG rendering

    fluidsynth_command = (
        'fluidsynth'
        '-T oga'
        '-nli'
        '-r 44200'
        '-o synth.midi-bank-select={}'.format(midi_bank),
        '-F',
        ogg_file_path,
        sound_font,
        midi_file_path,
        )
    fluidsynth_command = ' '.join(fluidsynth_command)
    print(fluidsynth_command)
    result = systemtools.IOManager.spawn_subprocess(fluidsynth_command)
    if result == 0:
        encoded_audio = get_b64_from_file(ogg_file_path)
        audio_tag = '<audio controls type="audio/ogg" '
        audio_tag += 'src="data:audio/ogg;base64,{}">'
        audio_tag = audio_tag.format(encoded_audio)
        display_html(audio_tag, raw=True)
    else:
        message = 'fluidsynth failed to render MIDI as OGG, result: {!i}'
        message = message.format(result)
        print(message)
        return

    # MP3 Rendering

    ffmpeg_command = 'ffmpeg -i {} {}'.format(ogg_file_path, mp3_file_path)
    print(ffmpeg_command)
    result = systemtools.IOManager.spawn_subprocess(ffmpeg_command)
    if result == 0:
        encoded_audio = get_b64_from_file(mp3_file_path)
        audio_tag = '<audio controls type="audio/mpeg" '
        audio_tag += 'src="data:audio/mpeg;base64,{}">'
        audio_tag = audio_tag.format(encoded_audio)
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