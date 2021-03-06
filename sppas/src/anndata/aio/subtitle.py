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

    src.anndata.aio.subtitle.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import codecs
import datetime

import sppas
from .basetrs import sppasBaseIO
from ..anndataexc import AnnDataTypeError
from ..anndataexc import AioMultiTiersError
from ..annotation import sppasAnnotation
from ..annlocation.location import sppasLocation
from ..annlocation.point import sppasPoint
from ..annlocation.interval import sppasInterval

from .aioutils import serialize_labels
from .aioutils import format_labels

# ---------------------------------------------------------------------------


class sppasBaseSubtitles(sppasBaseIO):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      SPPAS base class for subtitle formats.

    """
    def __init__(self, name=None):
        """ Initialize a new sppasBaseSubtitles instance.

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
        self._accept_overlaps = False

    # -----------------------------------------------------------------------

    @staticmethod
    def _parse_time(time_string):
        """ Convert a time in "%H:%M:%S,%m" format into seconds. """

        time_string = time_string.strip()
        dt = (datetime.datetime.strptime(time_string, '%H:%M:%S,%f') -
              datetime.datetime.strptime('', ''))
        return dt.total_seconds()

    # -----------------------------------------------------------------------

    @staticmethod
    def _format_time(second_count):
        """ Convert a time in seconds into "%H:%M:%S" format. """

        dt = datetime.datetime.utcfromtimestamp(second_count)
        return dt.strftime('%H:%M:%S,%f')[:-3]

    # -----------------------------------------------------------------------

    @staticmethod
    def make_point(midpoint):
        """ In subtitles, the localization is a time value, so a float. """

        try:
            midpoint = float(midpoint)
        except ValueError:
            raise AnnDataTypeError(midpoint, "float")
        return sppasPoint(midpoint, radius=0.02)

    # -----------------------------------------------------------------------

    @staticmethod
    def _format_text(text):
        """ Remove HTML tags, etc. """

        text = text.replace('<b>', '')
        text = text.replace('<B>', '')
        text = text.replace('</b>', '')
        text = text.replace('</B>', '')

        text = text.replace('<i>', '')
        text = text.replace('<I>', '')
        text = text.replace('</i>', '')
        text = text.replace('</I>', '')

        text = text.replace('<u>', '')
        text = text.replace('<U>', '')
        text = text.replace('</u>', '')
        text = text.replace('</U>', '')

        text = text.replace('<font>', '')
        text = text.replace('<FONT>', '')
        text = text.replace('</font>', '')
        text = text.replace('</FONT>', '')

        text = text.replace('[br]', '\n')

        return text

    # -----------------------------------------------------------------------

    @staticmethod
    def _serialize_location(ann):
        """ Extract location to serialize the timestamps. """

        if ann.location_is_point() is False:
            begin = sppasBaseSubtitles._format_time(
                ann.get_lowest_localization().get_midpoint())
            end = sppasBaseSubtitles._format_time(
                ann.get_highest_localization().get_midpoint())

        else:
            # SubRip does not support point based annotation
            # so we'll make a 1 second subtitle
            begin = sppasBaseSubtitles._format_time(
                ann.get_lowest_localization().get_midpoint())
            end = sppasBaseSubtitles._format_time(
                ann.get_highest_localization().get_midpoint() + 1.)

        return '{:s} --> {:s}\n'.format(begin, end)


# ---------------------------------------------------------------------------


class sppasSubRip(sppasBaseSubtitles):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      SPPAS reader/writer for SRT format.

    The SubRip text file format (SRT) is used by the SubRip program to save
    subtitles ripped from video files or DVDs.
    It is free software, released under the GNU GPL.

    Each subtitle is represented as a group of lines. Subtitles are separated
    subtitles by a blank line.

        - first line of a subtitle is an index (starting from 1);
        - the second line is a timestamp interval,
          in the format %H:%M:%S,%m and the start and end of the range separated by -->;
        - optionally: a specific positioning by pixels, in the form X1:number Y1:number X2:number Y2:number;
        - the third line is the label. The HTML <b>, <i>, <u>, and <font> tags are allowed.

    """
    def __init__(self, name=None):
        """ Initialize a new sppasSubRip instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__

        sppasBaseSubtitles.__init__(self, name)
        self.default_extension = "srt"

    # -----------------------------------------------------------------------

    def read(self, filename):
        """ Read a SRT file and fill the Transcription.

        :param filename: (str)

        """
        with codecs.open(filename, 'r', sppas.encoding) as fp:

            tier = self.create_tier('Trans-SubRip')
            line = fp.next()
            lines = list()

            # Ignore an optional header (or blank lines)
            while sppasBaseIO.is_number(line.strip()[0:1]) is False:
                line = fp.next()

            # Content of the file
            try:
                while True:
                    lines = list()
                    while line.strip() != '':
                        lines.append(line.strip())
                        line = fp.next()
                    a = sppasSubRip._parse_subtitle(lines)
                    if a is not None:
                        tier.append(a)
                    line = fp.next()
            except StopIteration:
                a = sppasSubRip._parse_subtitle(lines)
                if a is not None:
                    tier.append(a)

            fp.close()

    # -----------------------------------------------------------------------

    @staticmethod
    def _parse_subtitle(lines):
        """ Parse a single subtitle.

        The subtitle can be written on several lines. In this case, one sppasLabel()
        is created for each line.

        :param lines: (list) the lines of a subtitle (index, timestamps, label)

        """
        if len(lines) < 3:
            return None

        # time stamps
        start, stop = map(sppasBaseSubtitles._parse_time, lines[1].split('-->'))
        time = sppasInterval(sppasBaseSubtitles.make_point(start),
                             sppasBaseSubtitles.make_point(stop))

        # create the annotation without label
        a = sppasAnnotation(sppasLocation(time))

        # optional position (in pixels), saved as metadata of the annotation
        if 'X1' in lines[2] and 'Y1' in lines[2]:
            # parse position: X1:number Y1:number X2:number Y2:number
            positions = lines[2].split(" ")
            for position in positions:
                coord, value = position.split(':')
                a.set_meta("position_pixel_"+coord, value)
            lines.pop(2)

        # labels
        text = ""
        for line in lines[2:]:
            text += sppasBaseSubtitles._format_text(line) + "\n"
        labels = format_labels(text.rstrip(), separator="\n")
        if len(labels) > 0:
            a.set_labels(labels)

        return a

    # -----------------------------------------------------------------------

    def write(self, filename):
        """ Write a transcription into a file.

        :param filename: (str)

        """
        if len(self) != 1:
            raise AioMultiTiersError("SubRip")

        with codecs.open(filename, 'w', sppas.encoding, buffering=8096) as fp:

            if self.is_empty() is False:
                number = 1
                last = len(self[0])
                for ann in self[0]:

                    text = serialize_labels(ann.get_labels(),
                                            separator="\n",
                                            empty="",
                                            alt=True)

                    # no label defined, or empty label -> no subtitle!
                    if len(text) == 0:
                        continue

                    subtitle = ""
                    # first line: the number of the annotation
                    subtitle += str(number) + "\n"
                    # 2nd line: the timestamps
                    subtitle += sppasBaseSubtitles._serialize_location(ann)
                    # 3rd line: optionally the position on screen
                    subtitle += sppasSubRip._serialize_metadata(ann)
                    # the text
                    subtitle += text + "\n"
                    if number < last:
                        # a blank line
                        subtitle += "\n"

                    # next!
                    fp.write(subtitle)
                    number += 1

            fp.close()

    # -----------------------------------------------------------------------

    @staticmethod
    def _serialize_metadata(ann):
        """ Extract metadata to serialize the position on screen. """

        text = ""
        if ann.is_meta_key("position_pixel_X1"):
            x1 = ann.get_meta("position_pixel_X1")
            if ann.is_meta_key("position_pixel_Y1"):
                y1 = ann.get_meta("position_pixel_Y1")
                if ann.is_meta_key("position_pixel_X2"):
                    x2 = ann.get_meta("position_pixel_X2")
                    if ann.is_meta_key("position_pixel_Y2"):
                        y2 = ann.get_meta("position_pixel_Y2")
                        text += "X1:{:s} Y1:{:s} X2:{:s} Y2:{:s}\n" \
                                "".format(x1, y1, x2, y2)
        return text

# ---------------------------------------------------------------------------


class sppasSubViewer(sppasBaseSubtitles):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      SPPAS reader/writer for SUB format.

    The SubViewer text file format (SUB) is used by the SubViewer program to
    save subtitles of videos.

    """
    def __init__(self, name=None):
        """ Initialize a new sppasBaseSubtitles instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__

        sppasBaseSubtitles.__init__(self, name)
        self.default_extension = "sub"

    # -----------------------------------------------------------------------

    def read(self, filename):
        """ Read a SUB file and fill the Transcription.

        :param filename: (str)

        """
        with codecs.open(filename, 'r', sppas.encoding) as fp:

            tier = self.create_tier('Trans-SubViewer')
            lines = list()
            line = fp.next()

            # Header
            while sppasBaseIO.is_number(line.strip()[0:1]) is False:
                lines.append(line.strip())
                line = fp.next()
            self._parse_header(lines)

            # Content of the file
            try:
                while True:
                    lines = list()
                    while line.strip() != '':
                        lines.append(line.strip())
                        line = fp.next()
                    a = sppasSubViewer._parse_subtitle(lines)
                    if a is not None:
                        tier.append(a)
                    line = fp.next()
            except StopIteration:
                a = sppasSubViewer._parse_subtitle(lines)
                if a is not None:
                    try:
                        tier.append(a)
                    except:
                        pass
            fp.close()

    # -----------------------------------------------------------------------

    def _parse_header(self, lines):
        """ Parse the header lines to get metadata.

        [INFORMATION]
        [TITLE]SubViewer file example
        [AUTHOR]FK
        [SOURCE]FK
        [PRG]gedit
        [FILEPATH]/extdata
        [DELAY]0
        [CD TRACK]0
        [COMMENT]
        [END INFORMATION]
        [SUBTITLE]
        [COLF]&HFFFFFF,[STYLE]bd,[SIZE]18,[FONT]Arial

        """
        for line in lines:
            if line.startswith('[TITLE]'):
                self.set_name(line[7:])
            elif line.startswith('[AUTHOR]'):
                self.set_meta('annotator_name', line[8:])
            elif line.startswith('[PRG]'):
                self.set_meta("prg_editor_name", line[4:])
            elif line.startswith('[FILEPATH]'):
                self.set_meta("file_path", line[:10])
            elif line.startswith('[DELAY]'):
                self.set_meta("media_shift_delay", line[:7])

    # -----------------------------------------------------------------------

    @staticmethod
    def _parse_subtitle(lines):
        """ Parse a single subtitle.

        :param lines: (list) the lines of a subtitle (index, timestamps, label)

        """
        if len(lines) < 2:
            return None

        # time stamps
        time_stamp = lines[0].replace(",", " ")
        time_stamp = time_stamp.replace(".", ",")
        start, stop = map(sppasBaseSubtitles._parse_time, time_stamp.split())
        time = sppasInterval(sppasBaseSubtitles.make_point(start),
                             sppasBaseSubtitles.make_point(stop))

        # labels
        text = ""
        for line in lines[1:]:
            text += sppasBaseSubtitles._format_text(line) + "\n"
        labels = format_labels(text.rstrip(), separator="\n")

        return sppasAnnotation(sppasLocation(time), labels)

    # -----------------------------------------------------------------------

    def write(self, filename):
        """ Write a transcription into a file.

        :param filename: (str)

        """
        if len(self) != 1:
            raise AioMultiTiersError("SubViewer")

        with codecs.open(filename, 'w', sppas.encoding, buffering=8096) as fp:

            fp.write(self._serialize_header())
            if self.is_empty() is False:
                for ann in self[0]:

                    text = serialize_labels(ann.get_labels(),
                                            separator="[br]",
                                            empty="",
                                            alt=True)

                    # no label defined, or empty label -> no subtitle!
                    if len(text) == 0:
                        continue

                    # the timestamps
                    subtitle = sppasBaseSubtitles._serialize_location(ann)
                    subtitle = subtitle.replace(",", ".")
                    subtitle = subtitle.replace(" --> ", ",")
                    # the text
                    subtitle += text + "\n"
                    # a blank line
                    subtitle += "\n"

                    # next!
                    fp.write(subtitle)

            fp.close()

    # -----------------------------------------------------------------------

    def _serialize_header(self):
        """ Convert metadata into an header.

        [INFORMATION]
        [TITLE]SubViewer file example
        [AUTHOR]FK
        [SOURCE]FK
        [PRG]gedit
        [FILEPATH]/extdata
        [DELAY]0
        [CD TRACK]0
        [COMMENT]
        [END INFORMATION]
        [SUBTITLE]
        [COLF]&HFFFFFF,[STYLE]bd,[SIZE]18,[FONT]Arial

        """
        header = "[INFORMATION]"
        header += "\n"
        header += "[TITLE]"
        header += self.get_name()
        header += "\n"
        header += "[AUTHOR]"
        if self.is_meta_key("annotator_name"):
            header += self.get_meta("annotator_name")
        header += "\n"
        header += "[SOURCE]"
        header += "\n"
        header += "[PRG]"
        header += "\n"
        header += "[FILEPATH]"
        header += "\n"
        header += "[DELAY]"
        header += "\n"
        header += "[CD TRACK]"
        header += "\n"
        header += "[COMMENT]"
        header += "\n"
        header += "[END INFORMATION]"
        header += "\n"
        header += "[SUBTITLE]"
        header += "\n"
        header += "[COLF]&HFFFFFF,[STYLE]bd,[SIZE]18,[FONT]Arial"
        header += "\n"
        header += "\n"

        return header
