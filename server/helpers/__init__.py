"""
Helpers for 102shows
(c) 2016 Simon Leiner
licensed under the GNU Public License, version 2

Helpful functions that are used throughout 102shows
"""

__all__ = ['color', 'exceptions', 'mqtt', 'preprocessors', 'verify']


def get_logo(filename: str ='../logo') -> str:
    """\
    Returns the colored 102shows logo. It is read from :file:`/path/to/102shows/logo`

    :param filename: You can specify another logo source file, if you want.

    :return: The logo as a multiline string. The colors are included as escape characters.
    """
    with open(filename, encoding='unicode_escape') as file:
        contents = file.read()
    return contents.rstrip().rstrip()  # return without newline at the end


def get_version(filename: str ='../version') -> str:
    """\
    Returns the current 102shows version as a string that is read from a special version file

    :param filename: Name of the version file. If no name is supplied, the standard file
        ``/path/to/102shows/version`` will be used

    :return: version string (as in the file))
    """
    with open(filename) as file:
        contents = file.read()
    return contents.rstrip().rstrip()  # return without newline at the end
