"""
    ..
        ---------------------------------------------------------------------
         ___   __    __    __    ___
        /     |  \  |  \  |  \  /              the automatic
        \__   |__/  |__/  |___| \__             annotation and
           \  |     |     |   |    \             analysis
        ___/  |     |     |   | ___/              of speech

        http://www.sppas.org/

        Use of this software is governed by the GNU Public License, version 3.

        SPPAS is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        SPPAS is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with SPPAS. If not, see <http://www.gnu.org/licenses/>.

        This banner notice must not be removed.

        ---------------------------------------------------------------------

    src.annotations.annotationsexc.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Exceptions for annotations package.

"""
from . import t

# -----------------------------------------------------------------------

SECT_CFG_FILE_ERROR = ":ERROR 4014: "
OPTION_KEY_ERROR = ":ERROR 1010: "
EMPTY_INPUT_ERROR = ":ERROR 1020: "
NO_INPUT_ERROR = ":ERROR 1030: "
BAD_INPUT_ERROR = ":ERROR 1040: "
SIZE_INPUT_ERROR = ":ERROR 1050: "
NO_DIR_ERROR = ":ERROR 1210: "
EMPTY_DIR_ERROR = ":ERROR 1220: "

# -----------------------------------------------------------------------


class AnnotationSectionConfigFileError(ValueError):
    """ :ERROR 4014: Missing section {section_name} in the configuration file. """

    def __init__(self, section_name):
        self.parameter = SECT_CFG_FILE_ERROR + (t.gettext(SECT_CFG_FILE_ERROR)).format(section_name=section_name)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class AnnotationOptionError(KeyError):
    """ :ERROR 1010: Unknown option with key {key}. """

    def __init__(self, key):
        self.parameter = OPTION_KEY_ERROR + (t.gettext(OPTION_KEY_ERROR)).format(key=key)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class EmptyInputError(IOError):
    """ :ERROR 1020: Empty input tier {name}. """

    def __init__(self, name):
        self.parameter = EMPTY_INPUT_ERROR + (t.gettext(EMPTY_INPUT_ERROR)).format(name=name)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class NoInputError(IOError):
    """ :ERROR 1030: Missing input tier. Please read the documentation. """

    def __init__(self):
        self.parameter = NO_INPUT_ERROR + t.gettext(NO_INPUT_ERROR)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class BadInputError(TypeError):
    """ :ERROR 1040: Bad input tier type. Expected time-aligned intervals. """

    def __init__(self):
        self.parameter = BAD_INPUT_ERROR + t.gettext(BAD_INPUT_ERROR)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class SizeInputsError(IOError):
    """ :ERROR 1050: Inconsistency between the number of intervals of the input tiers. Got: {:d} and {:d}. """

    def __init__(self, number1, number2):
        self.parameter = SIZE_INPUT_ERROR + (t.gettext(SIZE_INPUT_ERROR)).format(number1, number2)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class NoDirectoryError(IOError):
    """ :ERROR 1210: The directory {dirname} does not exist. """

    def __init__(self, dirname):
        self.parameter = NO_DIR_ERROR + (t.gettext(NO_DIR_ERROR)).format(dirname=dirname)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class EmptyDirectoryError(IOError):
    """ :ERROR 1220: The directory {dirname} does not contain relevant data. """

    def __init__(self, dirname):
        self.parameter = EMPTY_DIR_ERROR + (t.gettext(EMPTY_DIR_ERROR)).format(dirname=dirname)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------

