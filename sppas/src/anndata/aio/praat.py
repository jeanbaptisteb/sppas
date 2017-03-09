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

    src.anndata.aio.praat.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Praat - Doing phonetic with computers, is a GPL tool developed by:

        | Paul Boersma and David Weenink
        | Phonetic Sciences, University of Amsterdam
        | Spuistraat 210
        | 1012VT Amsterdam
        | The Netherlands

    See: http://www.fon.hum.uva.nl/praat/

"""
import codecs
import re

from sppas.src.sp_glob import encoding
from sppas.src.utils.makeunicode import b

from ..anndataexc import AioNoTiersError
from ..anndataexc import AioEmptyTierError
from ..annotation import sppasAnnotation
from ..annlocation.location import sppasLocation
from ..annlocation.point import sppasPoint
from ..annlocation.interval import sppasInterval
from ..annlabel.label import sppasLabel
from ..annlabel.tag import sppasTag

import aioutils
from .basetrs import sppasBaseIO

# ----------------------------------------------------------------------------


class sppasBasePraat(sppasBaseIO):
    """
    :author:       Brigitte Bigi, Jibril Saffi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Base class for readers and writers or Praat files.
    
    """
    @staticmethod
    def parse_int(line):
        """ Parse an integral value from a line of a Praat formatted file.

        :param line: (str)

        """
        try:
            sline = line.strip()
            val = sline[sline.rfind(' ') + 1:]
            return int(val)
        except:
            raise Exception(
                "could not parse int value on line: %s" %
                repr(line))

    # ----------------------------------------------------------------------------

    @staticmethod
    def parse_float(line):
        """ Parse a floating point value from a line of a Praat formatted file.
        We keep all the floating points in memory (even if it's totally un-relevant)
        to be able to restore exactly the original file.

        :param line: (str)

        """
        try:
            sline = line.strip()
            val = sline[sline.rfind(' ') + 1:]
            return float(val)
            #return round(float(val), 10)
        except:
            raise Exception("could not parse float value on line: %s" % repr(line))

    # ----------------------------------------------------------------------------

    @staticmethod
    def parse_string(iterator):
        """ Parse a string from one or more lines of a Praat formatted file.
        
        :param iterator: file pointer
        
        """
        first_line = iterator.next()
        if first_line.rstrip().endswith('"'):
            first_line = first_line.rstrip()
            return first_line[first_line.find('"') + 1:-1]
        else:
            first_line = first_line[first_line.find('"') + 1:]

        current_line = iterator.next()

        while not current_line.rstrip().endswith('"'):
            first_line += current_line
            current_line = iterator.next()

        current_line = current_line.rstrip()[:-1]
        first_line += current_line

        return first_line
    
    # -----------------------------------------------------------------

    @staticmethod
    def detect(filename, file_class):
        with codecs.open(filename, 'r', encoding) as it:
            file_type = sppasBasePraat.parse_string(it)
            object_class = sppasBasePraat.parse_string(it)
            return file_type == "ooTextFile" and object_class == file_class

    # -----------------------------------------------------------------

    def __init__(self, name=None):
        """ Initialize a new Praat instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        sppasBaseIO.__init__(self, name)

        self._accept_multi_tiers = True
        self._accept_no_tiers = False
        self._accept_metadata = False
        self._accept_ctrl_vocab = False
        self._accept_media = False
        self._accept_hierarchy = False
        self._accept_disjoint = False
        self._accept_alt_localization = False
        self._accept_alt_tag = False
        self._accept_radius = False
        self._accept_gaps = False
        self._accept_overlaps = False

# ----------------------------------------------------------------------------


class sppasTextGrid(sppasBasePraat):
    """
    :author:       Brigitte Bigi, Jibril Saffi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      SPPAS TextGrid reader and writer.

    TextGrid does not support alternatives labels nor locations. Only the ones
    with the best score are saved.
    TextGrid does not support controlled vocabularies.
    TextGrid does not support hierarchy.
    TextGrid does not support metadata.
    TextGrid does not support media assignment.
    TextGrid supports points and intervals. It does not support disjoint intervals.
    TextGrid does not support alternative tags (here called "text").
    TextGrid does not support radius.

    """
    @staticmethod
    def detect(filename):
        sppasBasePraat.parse_string(filename, "TextGrid")

    # -----------------------------------------------------------------

    @staticmethod
    def make_point(midpoint):
        return sppasPoint(midpoint, radius=0.0005)

    # -----------------------------------------------------------------

    def __init__(self, name=None):
        """ Initialize a new RawText instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        sppasBaseIO.__init__(self, name)

        self._accept_point = True
        self._accept_interval = True

    # -----------------------------------------------------------------

    def read(self, filename):
        """ Read a TextGrid file.

        :param filename: is the input file name, ending by ".TextGrid"

        """
        with codecs.open(filename, 'r', encoding) as it:
            try:
                for i in range(6):
                    it.next()

                # if the size isn't named, we must be in a short TextGrid file
                tier_count_line = it.next().strip()
                is_long = not tier_count_line.isdigit()
                tier_count = sppasBasePraat.parse_int(tier_count_line)

                if is_long:
                    it.next()

                for i in range(tier_count):
                    self.__read_tier(it, is_long)

            except StopIteration:
                pass
                # FIXME: we should probably warn the user
                #       that his file has invalid size values

    # -----------------------------------------------------------------

    def __read_tier(self, it, is_long):
        """ Reads a tier from the contents of a TextGrid file.
        Beware, this function will advance the iterator passed.

        :param it: An iterator to the contents of the file
             pointing where the tier starts.
        :param is_long: A boolean which is false if the TextGrid is in short form.

        """
        if is_long:
            it.next()

        tier_type = sppasBasePraat.parse_string(it)
        tier_name = sppasBasePraat.parse_string(it)

        tier = self.create_tier(tier_name)

        it.next()
        it.next()

        item_count = sppasBasePraat.parse_int(it.next())

        if tier_type == "IntervalTier":
            read_annotation = sppasTextGrid.__read_interval_annotation
        elif tier_type == "TextTier":
            read_annotation = sppasTextGrid.__read_point_annotation
        else:
            raise Exception("Tier type "+tier_type+" cannot be parsed.")

        for i in range(item_count):
            if is_long:
                it.next()
            read_annotation(it, tier)

    # -----------------------------------------------------------------

    @staticmethod
    def __read_point_annotation(it, tier):
        """ Read an annotation from an IntervalTier in the contents of a TextGrid file.
        Beware, this function will advance the iterator passed.

        :param it: an iterator to the contents of the file
             pointing where the annotation starts
        :param tier: the tier where we will add the read annotation

        """
        midpoint = sppasBasePraat.parse_float(it.next())
        tag_content = sppasBasePraat.parse_string(it)

        tier.add(sppasAnnotation(sppasLocation(sppasTextGrid.make_point(midpoint)),
                                 sppasLabel(sppasTag(tag_content))))

    # ------------------------------------------------------------------------

    @staticmethod
    def __read_interval_annotation(it, tier):
        """ Read an annotation from an IntervalTier in the contents of a TextGrid file
        Beware, this function will advance the iterator passed.

        :param it: an iterator to the contents of the file
             pointing where the annotation starts
        :param tier: the tier where we will add the read annotation

        """
        begin = sppasTextGrid.make_point(sppasBasePraat.parse_float(it.next()))
        end = sppasTextGrid.make_point(sppasBasePraat.parse_float(it.next()))
        interval = sppasInterval(begin, end)
        tag_content = sppasBasePraat.parse_string(it)
        tag_content = tag_content.replace('""', '"')  # praat double quotes.
        tier.add(sppasAnnotation(sppasLocation(interval),
                                 sppasLabel(sppasTag(tag_content))))

    # ------------------------------------------------------------------------

    def write(self, filename):
        """ Write a TextGrid file.

        :param filename: (str)

        """
        if self.is_empty():
            raise AioNoTiersError("TextGrid")

        try:
            min_point = min([tier.get_first_point() for tier in self._tiers if tier.is_empty() is False])
            max_point = max([tier.get_last_point() for tier in self._tiers if tier.is_empty() is False])
        except ValueError:
            raise AioEmptyTierError("TextGrid", ";".join([tier.get_name() for tier in self._tiers]))

        with codecs.open(filename, 'w', encoding, buffering=8096) as fp:
            fp.write((
                'File type = "ooTextFile"\n'
                'Object class = "TextGrid"\n'
                '\n'
                'xmin = {}\n'
                'xmax = {}\n'
                'tiers? <exists>\n'
                'size = {:d}\n'
                'item []:\n').format(
                    min_point.get_midpoint(),
                    max_point.get_midpoint(),
                    len(self._tiers)))

            for i, tier in enumerate(self._tiers):
                fp.write(self.__format_tier(tier, i))

    # ------------------------------------------------------------------------

    def __format_tier(self, tier, number):
        """ Format a tier from a transcription to the TextGrid format.

        :param number: The position of the tier in the list of all tiers.

        """
        min_point = min([t.get_first_point() for t in self._tiers if t.is_empty() is False])
        max_point = min([t.get_last_point() for t in self._tiers if t.is_empty() is False])

        # Fill empty tiers because TextGrid does not support empty tiers.
        if tier.is_empty():
            tier.append(sppasAnnotation(sppasLocation(sppasInterval(min_point, max_point))))

        if tier.is_interval() is True:
            tier = aioutils.fill_gaps(tier, min_point, max_point)
            tier = aioutils.merge_overlapping_annotations(tier)

        result = (
            '    item [{:d}]:\n'
            '        class = "{:s}"\n'
            '        name = "{:s}"\n'
            '        xmin = {}\n'
            '        xmax = {}\n'
            '        intervals: size = {:d}\n').format(
                number,
                'IntervalTier' if tier.is_interval() else 'TextTier',
                tier.get_name(),
                tier.get_first_point().get_midpoint(),
                tier.get_last_point().get_midpoint(),
                len(tier))

        if tier.is_interval():
            format_annotation = sppasTextGrid.__format_interval_annotation
        else:
            format_annotation = sppasTextGrid.__format_point_annotation

        for j, an in enumerate(tier):
            result += format_annotation(an, j)

        return result

    # ------------------------------------------------------------------------

    @staticmethod
    def __format_interval_annotation(annotation, number):
        """ Formats an annotation consisting of intervals to the TextGrid format.

        :param number: The position of the annotation in the list of all annotations.

        """
        text = b(annotation.get_label().get_best().get_content())
        if '"' in text:
            text = re.sub('([^"])["]([^"])', '\\1""\\2', text)
            text = re.sub('([^"])["]([^"])', '\\1""\\2', text)  # miss occurrences if 2 " are separated by only 1 character
            text = re.sub('([^"])["]$', '\\1""', text)  # miss occurrences if " is at the end of the label!
            text = re.sub('^["]([^"])', '""\\1', text)  # miss occurrences if " is at the beginning of the label!

        return (
            '        intervals [{:d}]:\n'
            '            xmin = {}\n'
            '            xmax = {}\n'
            '            text = "{:s}"\n').format(
                number,
                annotation.get_lowest_localization().get_midpoint(),
                annotation.get_highest_localization().get_midpoint(),
                text)

    # ------------------------------------------------------------------------

    @staticmethod
    def __format_point_annotation(annotation, number):
        """ Formats an annotation consisting of points to the TextGrid format.

        :param number: The position of the annotation in the list of all annotations.

        """
        text = annotation.get_label().get_best().get_content()
        return (
            '        points [{:d}]:\n'
            '            time = {}\n'
            '            mark = "{:s}"\n').format(
                number,
                annotation.get_lowest_localization().get_midpoint(),
                text)