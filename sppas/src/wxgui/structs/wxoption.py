# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /              the automatic
#           \__   |__/  |__/  |___| \__             annotation and
#              \  |     |     |   |    \             analysis
#           ___/  |     |     |   | ___/              of speech
#
#
#                           http://www.sppas.org/
#
# ---------------------------------------------------------------------------
#            Laboratoire Parole et Langage, Aix-en-Provence, France
#                   Copyright (C) 2011-2017  Brigitte Bigi
#
#                   This banner notice must not be removed
# ---------------------------------------------------------------------------
# Use of this software is governed by the GNU Public License, version 3.
#
# SPPAS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SPPAS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SPPAS. If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------
# File: src.wxgui.structs.wxoption.py
# ----------------------------------------------------------------------------

import wx

from sppas.src.structs.baseoption import sppasBaseOption

# ----------------------------------------------------------------------------


class sppasWxOption(sppasBaseOption):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    @summary:      Extend Option class to wx data types.

    New supported types are: wx.Size, wx.Colour, wx.Font and
    wx.ALIGN_something.

    """
    def __init__(self, option_type, option_value, option_text=""):
        """
        Creates a sppasWxOption() instance.

        option_type is a string; one of:
            boolean, int, float, string, wx.colour, wx.size, wx.font, wx.align

        """
        sppasBaseOption.__init__(self, option_type, option_value)
        self.set_text(option_text)

    # ------------------------------------------------------------------------
    # Getters
    # ------------------------------------------------------------------------

    def get_value(self):
        """
        Return the typed-value.
        Override the sppasBaseOption.get_value().

        """
        v = sppasBaseOption.get_value(self)
        if v is not None:
            return v

        if self._type == 'wx.size':
            #(w,h) = self._value
            #return wx.Size(w,h)
            return int(self._value)

        if self._type == 'wx.colour':
            if self._value is None:
                return None
            (r, g, b) = self._value
            return wx.Colour(r, g, b)

        if self._type == 'wx.font':
            (size, family, style, weight, u, face, enc) = self._value
            font = wx.Font(size, family, style, weight, u, face, enc)
            return font

        if self._type == 'wx.align':
            if self._value.lower() == 'left':
                return wx.ALIGN_LEFT
            if self._value.lower() == 'right':
                return wx.ALIGN_RIGHT
            return wx.ALIGN_CENTRE

        raise TypeError('Unknown option type %s' % self._type)

    # ------------------------------------------------------------------------
    # Setters
    # ------------------------------------------------------------------------

    def set_type(self, option_type):
        """ Set a new type. """

        option_type = option_type.lower()
        if option_type.startswith("wx"):
            self._type = option_type
        else:
            sppasBaseOption.set_type(self, option_type)

    # ------------------------------------------------------------------------

    def set_value(self, value):
        """
        Set a new value.
        Override the sppasBaseOption.set_value().

        """
        if self._type == 'wx.font':
            if isinstance(value,wx.Font):
                size   = value.GetPointSize()
                family = value.GetFamily()
                style  = value.GetStyle()
                weight = value.GetWeight()
                underline = value.GetUnderlined()
                face = value.GetFaceName()
                encoding = value.GetEncoding()
                self._value = (size, family, style, weight, underline, face, encoding)
            else:
                self._value = value

        elif self._type == 'wx.size':
            if isinstance(value,wx.Size):
                (w,h) = value
                self._value = (w, h)
            else:
                self._value = value

        elif self._type == 'wx.colour':
            if isinstance(value,wx.Colour):
                (r,g,b) = value
                self._value = (r, g, b)
            else:
                self._value = value

        elif self._type == 'wx.align':
            if value == wx.ALIGN_LEFT or value == 'left':
                self._value = 'left'
            elif value == wx.ALIGN_RIGHT or value == 'right':
                self._value = 'right'
            else:
                self._value = 'centre'

        else:
            self._value = value

    # ------------------------------------------------------------------------
