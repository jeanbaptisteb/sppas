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
# File: src.plugins
# ----------------------------------------------------------------------------

"""
@author:       Brigitte Bigi
@organization: Laboratoire Parole et Langage, Aix-en-Provence, France
@contact:      brigitte.bigi@gmail.com
@license:      GPL, v3
@copyright:    Copyright (C) 2011-2017  Brigitte Bigi
@summary:      Plugin manager for SPPAS.

plugins is a free and open source Python library to access and manage
external programs to plug into SPPAS.

This package requires:
 - the PYTHON_PATH variable that is defined in sp_glob
 - the Option class of structs.baseoption
 - the function get_files of utils.fileutils

"""
from cfgparser import sppasPluginConfigParser
from manager import sppasPluginsManager
from param import sppasPluginParam
from process import sppasPluginProcess

__all__ = [
    "sppasPluginsManager",
    "sppasPluginConfigParser",
    "sppasPluginParam",
    "sppasPluginProcess"
    ]