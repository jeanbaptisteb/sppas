# -*- coding: UTF-8 -*-
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

    src.anndata.aio.htk.py
    ~~~~~~~~~~~~~~~~~~~~~~~


"""
import codecs

from sppas import encoding

from ..anndataexc import AioError
from ..anndataexc import AioEncodingError
from ..anndataexc import AioMultiTiersError
from ..anndataexc import AioLocationTypeError
from ..annlocation.location import sppasLocation
from ..annlocation.point import sppasPoint
from ..annlocation.interval import sppasInterval
from ..annlabel.label import sppasLabel
from ..annlabel.tag import sppasTag

from .basetrs import sppasBaseIO

# ----------------------------------------------------------------------------

# time values are in multiples of 100ns
TIME_UNIT = pow(10, -7)

# ----------------------------------------------------------------------------


class sppasBaseHTK(sppasBaseIO):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      SPPAS HTK files reader and writer.

    """
    def __init__(self, name=None):
        """ Initialize a new sppasMLF instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        sppasBaseIO.__init__(self, name)

        self._accept_multi_tiers = False
        self._accept_no_tiers = True
        self._accept_metadata = False
        self._accept_ctrl_vocab = False
        self._accept_media = False
        self._accept_hierarchy = False
        self._accept_point = False
        self._accept_interval = True
        self._accept_disjoint = False
        self._accept_alt_localization = False
        self._accept_alt_tag = False
        self._accept_radius = False
        self._accept_gaps = True
        self._accept_overlaps = False  # to be verified

    # ----------------------------------------------------------------------------

    @staticmethod
    def make_point(time_string):
        """ Convert data into the appropriate sppasPoint().
        No radius if data is an integer. A default radius of 0.001 if data is a
        float.

        :param time_string: (str) a time in HTK format
        :returns: sppasPoint().

        """
        v = float(TIME_UNIT) * float(time_string)
        return sppasPoint(v, radius=0.005)

    # ------------------------------------------------------------------------

    @staticmethod
    def _format_time(second_count):
        """ Convert a time in seconds into HTK format. """

        return int(1. / TIME_UNIT * float(second_count))

    # -----------------------------------------------------------------

    @staticmethod
    def _serialize_annotation(ann):
        """ Convert an annotation into a line for HTK lab of mlf files.

        :param ann: (sppasAnnotation)
        :returns: (str)

        """
        # no label defined, or empty label
        if ann.get_best_tag().is_empty():
            return ""
        if ann.get_location().is_point():
            raise AioLocationTypeError('HTK Label', 'points')

        tag_content = ann.get_best_tag().get_content()
        begin = sppasBaseHTK._format_time(ann.get_lowest_localization().get_midpoint())
        end = sppasBaseHTK._format_time(ann.get_highest_localization().get_midpoint())

        if ' ' not in tag_content:
            location = "{:d} {:d}".format(begin, end)
        else:
            # one "token" at a line, and only begin at first
            location = "{:d}".format(begin)
            tag_content = tag_content.replace(' ', '\n')

        return "{:s} {:s}\n".format(location, tag_content)

# ----------------------------------------------------------------------------


class sppasLab(sppasBaseHTK):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      SPPAS LAB reader and writer.

    Each line of a HTK label file contains the actual label optionally
    preceded by start and end times, and optionally followed by a match score.

    [<start> <end>] <<name> [<score>]> [";" <comment>]

    Multiple alternatives are written as a sequence of separate label
    lists separated by three slashes (///).

    Examples:
        - simple transcription:

            0000000 3600000 ice
            3600000 8200000 cream

        - alternative labels:

            0000000 2200000 I
            2200000 8200000 scream
            ///
            0000000 3600000 ice
            3600000 8200000 cream
            ///
            0000000 3600000 eyes
            3600000 8200000 cream

    *************  Only simple transcription is implemented yet.  ***********

    """
    @staticmethod
    def detect(filename):
        """ Check whether a file is of HTK-Lab format or not.

        :param filename: (str) Name of the file to check.
        :returns: (bool)

        """
        try:
            with codecs.open(filename, 'r', encoding) as fp:
                line = fp.readline()
                fp.close()
        except IOError:
            return False
        except UnicodeDecodeError:
            return False

        # the first line contains at least 2 columns
        tab = line.split()
        if len(tab) < 2:
            return False
        # First column is the start time: an integer
        try:
            int(line[0])
        except ValueError:
            return False

        return line[0].isdigit()

    # -----------------------------------------------------------------

    def __init__(self, name=None):
        """ Initialize a new sppasLab instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        sppasBaseHTK.__init__(self, name)

    # ------------------------------------------------------------------------

    def read(self, filename):
        """ Read a transcription from a file.

        :param filename:

        """
        try:
            with codecs.open(filename, 'r', encoding) as fp:
                lines = fp.readlines()
                fp.close()
        except IOError:
            raise AioError(filename)
        except UnicodeDecodeError:
            raise AioEncodingError(filename, "")

        tier = self.create_tier('Trans-MLF')
        label = ""
        prev_end = sppasBaseHTK.make_point(0)

        for line in lines:
            line = line.strip().split()

            has_begin = len(line) > 0 and line[0].isdigit()
            has_end = len(line) > 1 and line[1].isdigit()

            if has_begin and has_end:
                if len(label) > 0:
                    time = sppasInterval(prev_end, sppasBaseHTK.make_point(line[0]))
                    tier.create_annotation(sppasLocation(time), sppasLabel(sppasTag(label)))

                time = sppasInterval(sppasBaseHTK.make_point(line[0]),
                                     sppasBaseHTK.make_point(line[1]))

                label = line[2]
                score = None
                if len(line) > 3:
                    try:
                        score = float(line[3])
                    except ValueError:
                        # todo: auxiliary labels or comment
                        pass

                tier.create_annotation(sppasLocation(time), sppasLabel(sppasTag(label), score))
                label = ""
                prev_end = sppasBaseHTK.make_point(line[1])

            elif has_begin:
                label = label + " " + " ".join(line[1])
                # todo: auxiliary labels or comment

            else:
                label = label + " " + " ".join(line)

    # ------------------------------------------------------------------------

    def write(self, filename):
        """ Write a transcription into a file.

        :param filename: (str)

        """
        if len(self) != 1:
            raise AioMultiTiersError("HTK Label")

        with codecs.open(filename, 'w', encoding, buffering=8096) as fp:

            if self.is_empty() is False:
                for ann in self[0]:
                    if ann.get_best_tag().is_empty() is False:
                        fp.write(sppasBaseHTK._serialize_annotation(ann))

            fp.close()