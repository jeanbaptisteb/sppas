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

    src.anndata.tests.test_aio_annotationpro
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Test the reader of SPPAS for AnnotationPro files.

"""
import unittest
import os.path
import xml.etree.cElementTree as ET

from ..aio.annotationpro import sppasANTX
from ..annlocation.point import sppasPoint
from ..tier import sppasTier
from ..media import sppasMedia
from ..annlabel.tag import sppasTag
from ..annlocation.interval import sppasInterval
from ..annlabel.label import sppasLabel
from ..annlocation.location import sppasLocation

# ---------------------------------------------------------------------------

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------------------


class TestANTX(unittest.TestCase):
    """
    Test reader of Audacity project files.

    """
    def test_detect(self):
        """ Test the file format detection method. """

        for filename in os.listdir(DATA):
            f = os.path.join(DATA, filename)
            if filename.endswith('.antx'):
                self.assertTrue(sppasANTX.detect(f))
            else:
                self.assertFalse(sppasANTX.detect(f))

    # -----------------------------------------------------------------------

    def test_members(self):
        txt = sppasANTX()
        self.assertTrue(txt.multi_tiers_support())
        self.assertTrue(txt.no_tiers_support())
        self.assertTrue(txt.metadata_support())
        self.assertFalse(txt.ctrl_vocab_support())
        self.assertTrue(txt.media_support())
        self.assertFalse(txt.hierarchy_support())
        self.assertFalse(txt.point_support())
        self.assertTrue(txt.interval_support())
        self.assertFalse(txt.disjoint_support())
        self.assertFalse(txt.alternative_localization_support())
        self.assertFalse(txt.alternative_tag_support())
        self.assertFalse(txt.radius_support())
        self.assertTrue(txt.gaps_support())
        self.assertFalse(txt.overlaps_support())

    # -----------------------------------------------------------------------

    def test_make_point(self):
        """ Convert data into the appropriate digit type, or not. """

        self.assertEqual(sppasPoint(3., 0.005), sppasANTX.make_point("132300"))
        with self.assertRaises(TypeError):
            sppasANTX.make_point("3a")
        with self.assertRaises(TypeError):
            sppasANTX.make_point("3.")

    # -----------------------------------------------------------------------

    def test_configuration(self):
        """ 'Configuration' <-> metadata. """

        root = ET.Element('AnnotationSystemDataSet')
        root.set('xmlns', 'http://tempuri.org/AnnotationSystemDataSet.xsd')
        antx = sppasANTX()

        # Format antx: from antx.metadata (or default value) to 'Configuration
        antx._format_configuration(root)

        # Parse the tree: from 'Configuration' to antx.metadata
        for child in root.iter('Configuration'):
            antx._parse_configuration(child)

        # so, test the result!
        self.assertEqual(antx.get_meta("Version"), "5")
        self.assertEqual(antx.get_meta("file_version"), "1")
        self.assertEqual(antx.get_meta("media_sample_rate"), "44100")

    # -----------------------------------------------------------------------

    def test_audiofile(self):
        """ 'AudioFile' <-> sppasMedia. """

        root = ET.Element('AnnotationSystemDataSet')
        root.set('xmlns', 'http://tempuri.org/AnnotationSystemDataSet.xsd')
        antx = sppasANTX()
        media = sppasMedia("filename.wav")

        # Format antx: from sppasMedia() to 'AudioFile'
        sppasANTX._format_media(root, media)

        # Parse the tree: from 'AudioFile' to antx.media
        for child in root.iter('AudioFile'):
            antx._parse_audiofile(child)

        self.assertEqual(len(antx.get_media_list()), 1)
        antx_media = antx.get_media_list()[0]
        self.assertEqual(antx_media, media)
        self.assertEqual(antx_media.get_meta('media_sample_rate'), '44100')
        self.assertEqual(antx_media.get_meta('Name'), 'NoName')
        self.assertEqual(antx_media.get_meta('Current'), 'false')

    # -----------------------------------------------------------------------

    def test_layer(self):
        """ 'Layer' <-> sppasTier. """

        root = ET.Element('AnnotationSystemDataSet')
        root.set('xmlns', 'http://tempuri.org/AnnotationSystemDataSet.xsd')
        antx = sppasANTX()
        tier1 = sppasTier()
        tier2 = sppasTier()

        # Format antx: from sppasTier() to 'Layer'
        sppasANTX._format_tier(root, tier1)
        sppasANTX._format_tier(root, tier2)

        # Parse the tree: from 'Layer' to antx.tier
        for child in root.iter('Layer'):
            antx._parse_layer(child)

        self.assertEqual(len(antx), 2)
        self.assertEqual(antx[0].get_name(), tier1.get_name())
        self.assertEqual(antx[0].get_meta('id'), tier1.get_meta('id'))
        self.assertEqual(antx[1].get_name(), tier2.get_name())
        self.assertEqual(antx[1].get_meta('id'), tier2.get_meta('id'))

        elt_layer = {'CoordinateControlStyle': "0",
                     'IsLocked': "false",
                     'ShowOnSpectrogram': "false",
                     'ShowAsChart': "false",
                     'ChartMinimum': "-50",
                     'ChartMaximum': "50",
                     'ShowBoundaries': "true",
                     'IncludeInFrequency': "true",
                     'Parameter1Name': "Parameter 1",
                     'Parameter2Name': "Parameter 2",
                     'Parameter3Name': "Parameter 3",
                     'IsVisible': "true", 'FontSize': "10",
                     "tier_is_closed": "false",
                     "tier_height": "70",
                     "tier_is_selected": "false",
                     }
        for key in elt_layer:
            self.assertEqual(antx[0].get_meta(key), elt_layer[key])
            self.assertEqual(antx[1].get_meta(key), elt_layer[key])

    # -----------------------------------------------------------------------

    def test_segment(self):
        """ 'Segment' <-> sppasAnnotation. """

        root = ET.Element('AnnotationSystemDataSet')
        root.set('xmlns', 'http://tempuri.org/AnnotationSystemDataSet.xsd')
        antx = sppasANTX()
        pass

    # -----------------------------------------------------------------------
