#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /              Automatic
#           \__   |__/  |__/  |___| \__             Annotation
#              \  |     |     |   |    \             of
#           ___/  |     |     |   | ___/              Speech
#
#
#                           http://www.sppas.org/
#
# ---------------------------------------------------------------------------
#            Laboratoire Parole et Langage, Aix-en-Provence, France
#                   Copyright (C) 2011-2016  Brigitte Bigi
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
# File: basedialog.py
# ---------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi"""
__copyright__ = """Copyright (C) 2011-2016  Brigitte Bigi"""

# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------
import sys
import os.path
sys.path.append(  os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) )

import wx
from basedialog import spBaseDialog

from wxgui.sp_icons import APP_ICON
from wxgui.sp_icons import MESSAGE_ICON
from wxgui.sp_consts import MAIN_FONTSIZE

# ----------------------------------------------------------------------------

class spBaseMessageDialog( spBaseDialog ):

    def __init__(self, parent, preferences, headermsg, contentmsg):
        """
        Constructor.

        @param parent is the parent wx object.
        @param preferences (Preferences)
        @param filename (str) the file to display in this frame.

        """
        spBaseDialog.__init__(self, parent, preferences, title=" - Message")
        wx.GetApp().SetAppName( "question" )

        titlebox   = self.CreateTitle(MESSAGE_ICON,headermsg)
        contentbox = self._create_content(contentmsg)
        buttonbox  = self._create_buttons()

        self.LayoutComponents( titlebox,
                               contentbox,
                               buttonbox )

    def _create_content(self,message):
        txt = wx.TextCtrl(self, value=message, style=wx.TE_READONLY|wx.TE_MULTILINE|wx.NO_BORDER)
        font = wx.Font(MAIN_FONTSIZE, wx.FONTFAMILY_TELETYPE, wx.NORMAL, wx.NORMAL)
        txt.SetFont(font)
        txt.SetForegroundColour( self.preferences.GetValue('M_FG_COLOUR') )
        txt.SetBackgroundColour( self.preferences.GetValue('M_BG_COLOUR') )
        txt.SetMinSize((300,-1))
        return txt

    def _create_buttons(self):
        raise NotImplementedError

# ---------------------------------------------------------------------------

class YesNoQuestion( spBaseMessageDialog ):
    def __init__(self, parent, preferences, contentmsg):
        spBaseMessageDialog.__init__(self, parent, preferences, "Question", contentmsg)

    def _create_buttons(self):
        yes = self.CreateYesButton()
        no  = self.CreateNoButton()
        self.Bind( wx.EVT_BUTTON, self._on_no,  no,  wx.ID_NO  )
        self.Bind( wx.EVT_BUTTON, self._on_yes, yes, wx.ID_YES )
        return self.CreateButtonBox( [no],[yes] )

    def _on_no(self, evt):
        self.SetReturnCode( wx.ID_NO )
        self.Destroy()

    def _on_yes(self, evt):
        self.SetReturnCode( wx.ID_YES )
        self.Destroy()

# ---------------------------------------------------------------------------

class Information( spBaseMessageDialog ):
    def __init__(self, parent, preferences, contentmsg):
        spBaseMessageDialog.__init__(self, parent, preferences, "Information", contentmsg)

    def _create_buttons(self):
        yes = self.CreateYesButton()
        self.SetAffirmativeId( wx.ID_YES )
        return self.CreateButtonBox( [],[yes] )

# ---------------------------------------------------------------------------

def ShowYesNoQuestion(parent, preferences, contentmsg):
    dlg = YesNoQuestion( parent, preferences, contentmsg )
    return dlg.ShowModal()

# ---------------------------------------------------------------------------

def ShowInformation(parent, preferences, contentmsg):
    dlg = Information( parent, preferences, contentmsg )
    return dlg.ShowModal()

# ---------------------------------------------------------------------------

def DemoBaseDialog(parent, preferences=None):
    def _on_yesno(evt):
        res = ShowYesNoQuestion( frame, preferences, "This is the message to show.")
        if res == wx.ID_YES:
            ShowInformation( frame, preferences, "You clicked the ""Yes"" button")
        elif res == wx.ID_NO:
            ShowInformation( frame, preferences, "You clicked the ""No"" button")
        else:
            print "there's a bug! return value is %s"%res

    def _on_info(evt):
        ShowInformation( frame, preferences, "This is an information message.")

    frame = spBaseDialog(parent, preferences)
    title = frame.CreateTitle(APP_ICON,"Message dialogs demonstration")
    btninfo   = frame.CreateButton(MESSAGE_ICON,"Test 1", "This is a tooltip!", btnid=wx.NewId())
    btnyesno  = frame.CreateButton(MESSAGE_ICON,"Test 2", "This is a tooltip!", btnid=wx.NewId())

    btnclose  = frame.CreateCloseButton()
    btnbox    = frame.CreateButtonBox( [btninfo,btnyesno],[btnclose] )

    frame.LayoutComponents( title, wx.Panel(frame, -1, size=(320,200)), btnbox )

    btninfo.Bind( wx.EVT_BUTTON, _on_info )
    btnyesno.Bind( wx.EVT_BUTTON, _on_yesno )

    frame.ShowModal()
    frame.Destroy()

# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app = wx.PySimpleApp()
    DemoBaseDialog(None)
    app.MainLoop()

# ---------------------------------------------------------------------------
