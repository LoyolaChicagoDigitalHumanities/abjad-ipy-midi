import os
import setuptools 

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

install_requires = [
    'Abjad >= 2.0',
    ]

    #packages=['abjad-midi'],
setuptools.setup(
    name = "abjad-ipython-midi",
    version = "1.0",
    author = "Griffin Moe",
    author_email = "me@griffinmoe.com",
    description = ("An IPython extension that uses Fluidsynth to render"
                   "Abjad expressions as audio files within iPy Notebooks."),
    license = "GPL",
    keywords = "ipython notebook abjad midi fluidsynth music lilypond",
    packages=setuptools.find_packages(exclude=('notebooks')),
    url = "https://github.com/ctsdh-luc-edu/abjad-ipython-midi",
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Scientific/Engineering",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)

