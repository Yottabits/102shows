# Lightshow Templates
# (c) 2016-2017 Simon Leiner, 2015 Martin Erzberger
# licensed under the GNU Public License, version 2

"""\
To make writing lightshows easy and convenient we introduced templates.
These provide the interfaces for the controller and generic functionalities.

*Basically: The templates are there so that lightshow modules just have to
worry about the LED animations, and not about the backgrounds of 102shows*
"""

__all__ = ['base', 'colorcycle']
