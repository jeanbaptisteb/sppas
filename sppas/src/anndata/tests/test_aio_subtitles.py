# -*- coding:utf-8 -*-

import unittest
import os.path

from ..aio.subtitle import sppasBaseSubtitles
from ..aio.subtitle import sppasSubRip
from ..aio.subtitle import sppasSubViewer

from ..annlocation.interval import sppasInterval
from ..annlocation.point import sppasPoint
from ..annlabel.label import sppasTag
from ..annlabel.label import sppasLabel
from ..annotation import sppasAnnotation
from ..annlocation.location import sppasLocation

# ---------------------------------------------------------------------------

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------------------


class TestBaseSubtitle(unittest.TestCase):
    """
    Base text is mainly made of utility methods.

    """
    def test_members(self):
        txt = sppasBaseSubtitles()
        self.assertFalse(txt.multi_tiers_support())
        self.assertTrue(txt.no_tiers_support())
        self.assertFalse(txt.metadata_support())
        self.assertFalse(txt.ctrl_vocab_support())
        self.assertFalse(txt.media_support())
        self.assertFalse(txt.hierarchy_support())
        self.assertFalse(txt.point_support())
        self.assertTrue(txt.interval_support())
        self.assertFalse(txt.disjoint_support())
        self.assertFalse(txt.alternative_localization_support())
        self.assertFalse(txt.alternative_tag_support())
        self.assertFalse(txt.radius_support())
        self.assertTrue(txt.gaps_support())
        self.assertFalse(txt.overlaps_support())

    # -----------------------------------------------------------------

    def test_make_point(self):
        """ Convert data into the appropriate digit type, or not. """

        self.assertEqual(sppasPoint(3., 0.02), sppasBaseSubtitles.make_point("3.0"))
        self.assertEqual(sppasPoint(3., 0.02), sppasBaseSubtitles.make_point("3."))
        self.assertEqual(sppasPoint(3), sppasBaseSubtitles.make_point("3"))
        with self.assertRaises(TypeError):
            sppasBaseSubtitles.make_point("3a")

    # -----------------------------------------------------------------

    def test_serialize_location(self):
        """ Test location -> timestamps. """

        a1 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(3.5))))
        self.assertEqual(sppasSubRip._serialize_location(a1),
                         "00:00:01,000 --> 00:00:03,500\n")

        a2 = sppasAnnotation(sppasLocation(sppasPoint(1.)))
        self.assertEqual(sppasSubRip._serialize_location(a2),
                         "00:00:01,000 --> 00:00:02,000\n")

        a1 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1), sppasPoint(3))))
        self.assertEqual(sppasSubRip._serialize_location(a1),
                         "00:00:01,000 --> 00:00:03,000\n")

        a2 = sppasAnnotation(sppasLocation(sppasPoint(1)))
        self.assertEqual(sppasSubRip._serialize_location(a2),
                         "00:00:01,000 --> 00:00:02,000\n")

# ---------------------------------------------------------------------


class TestSubRip(unittest.TestCase):
    """
    Represents a SubRip reader/writer.

    """
    def test_read(self):
        """ Test of reading a SRT sample file. """

        txt = sppasSubRip()
        txt.read(os.path.join(DATA, "sample.srt"))
        self.assertEqual(len(txt), 1)
        self.assertEqual(len(txt[0]), 4)
        self.assertEqual(sppasPoint(0.), txt[0].get_first_point())
        self.assertEqual(sppasPoint(15.), txt[0].get_last_point())
        self.assertTrue(txt[0][2].is_meta_key('position_pixel_X1'))

        # multi-lines: 2 sppasLabel() created in the same annotation
        self.assertEqual(len(txt[0][1].get_labels()), 2)
        self.assertFalse("<i>" in txt[0][1].get_labels()[0].get_best().get_content())
        self.assertTrue("une classe" in txt[0][1].get_labels()[0].get_best().get_content())
        self.assertTrue("bien vu" in txt[0][1].get_labels()[1].get_best().get_content())

    # -----------------------------------------------------------------

    def test_serialize_metadata(self):
        """ Test metadata -> position. """

        a1 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(3.5))))
        self.assertEqual(sppasSubRip._serialize_metadata(a1), "")
        a1.set_meta("position_pixel_X1", "10")
        a1.set_meta("position_pixel_Y1", "20")
        self.assertEqual(sppasSubRip._serialize_metadata(a1), "")
        a1.set_meta("position_pixel_X2", "100")
        a1.set_meta("position_pixel_Y2", "200")
        self.assertEqual(sppasSubRip._serialize_metadata(a1), "X1:10 Y1:20 X2:100 Y2:200\n")

# ---------------------------------------------------------------------


class TestSubViewer(unittest.TestCase):
    """
    Represents a SubViewer reader/writer.

    """
    def test_read(self):
        """ Test of reading a SUB sample file. """

        txt = sppasSubViewer()
        txt.read(os.path.join(DATA, "sample.sub"))
        self.assertEqual(txt.get_meta('annotator_name'), "FK")

        self.assertEqual(1, len(txt))
        self.assertEqual(6, len(txt[0]))
        self.assertEqual(sppasPoint(22.5), txt[0].get_first_point())
        self.assertEqual(sppasPoint(34.80), txt[0].get_last_point())
        self.assertFalse("[br]" in txt[0][0].get_labels()[0].get_best().get_content())
        self.assertTrue("Lorem ipsum dolor sit amet" in txt[0][0].get_labels()[0].get_best().get_content())
        self.assertTrue("consectetur adipiscing elit" in txt[0][0].get_labels()[1].get_best().get_content())

        self.assertTrue("Lorem ipsum dolor sit amet" in txt[0][0].get_labels()[0].get_best().get_content())
        self.assertTrue("consectetur adipiscing elit" in txt[0][0].get_labels()[1].get_best().get_content())

    # -----------------------------------------------------------------

    def test_serialize_header(self):
        """ Test metadata -> header. """

        txt = sppasSubViewer()
        header = txt._serialize_header()
        self.assertEqual(len(header.split('\n')), 14)
