#!/usr/bin/env python2
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

    scripts.tierfilter.py
    ~~~~~~~~~~~~~~~~~~~~~~~

    ... a script to filter labels of a tier of an annotated file.

"""
import sys
import os.path
from argparse import ArgumentParser
import functools
import operator

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

import sppas.src.annotationdata.aio
from sppas.src.annotationdata.filter.predicate import Sel
from sppas.src.annotationdata.transcription import Transcription
from sppas.src.annotationdata.transcription import Tier

# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

modeshelp = "Pattern search mode, in:"
modeshelp += " 0 = EXACT:      the label of the tier strictly corresponds to the pattern,\n"
modeshelp += ' 1 = CONTAINS:   the label of the tier contains the given pattern,\n'
modeshelp += ' 2 = STARTSWITH: the label of the tier starts with the given pattern,\n'
modeshelp += ' 3 = ENDSWITH:   the label of the tier ends with the given pattern.\n'
modeshelp += ' 4 = REGEXP'

parser = ArgumentParser(usage="%s -i file -o file [options]" % os.path.basename(PROGRAM),
                        description="... a script to filter labels of a tier of an annotated file.")

parser.add_argument("-i",
                    metavar="file",
                    required=True,
                    help='Input annotated file file name')

parser.add_argument("-t",
                    metavar="value",
                    default=1,
                    type=int,
                    help='Tier number (default: 1)')

parser.add_argument("-o",
                    metavar="file",
                    required=True,
                    help='Output file name')

parser.add_argument("-n",
                    metavar="str",
                    default="filtered",
                    help='Output tier name')

parser.add_argument("-p",
                    metavar="pattern",
                    required=True,
                    action="append",
                    help='One pattern to find (as many -p options as needed)')

parser.add_argument("-m", metavar="value", type=int, help=modeshelp)

parser.add_argument("--reverse",
                    action='store_true',
                    help="Reverse the result")

parser.add_argument("--no-case-sensitive",
                    dest="nocasesensitive",
                    action='store_true')

parser.add_argument("--no-merge",
                    dest="nomerge",
                    action='store_true',
                    help="Keep only the first pattern in the result")

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------

tieridx = args.t-1
fileinput = args.i
fileoutput = args.o
nameoutput = args.n
patterns = args.p
options = ["CASE_SENSITIVE", "MERGE"]
mode = args.m

if args.reverse:
    options.append("REVERSE")
if args.nocasesensitive:
    if "CASE_SENSITIVE" in options:
        options.remove("CASE_SENSITIVE")
if args.nomerge:
    if "MERGE" in options:
        options.remove("MERGE")

search_mode = (0, 1, 2, 3, 4)
for m in mode:
    if m not in search_mode:
        print("Unknown search mode : {}".format(m))
        sys.exit(1)

trs = sppas.src.annotationdata.aio.read(fileinput)

if tieridx < 0 or tieridx > trs.GetSize():
    print('Error: Bad tier number.\n')
    sys.exit(1)

tier = trs[tieridx]
if not mode:
    mode.append(0)

d = {0: 'exact', 1: 'contains', 2: 'startswith', 3: 'endswith', 4: 'regexp'}
prefix = "" if "CASE_SENSITIVE" in options else "i"
bools = [Sel(**{prefix + d[key]: p}) for key in mode for p in patterns]
pred = functools.reduce(operator.or_, bools)
pred = ~pred if "REVERSE" in options else pred

filtered_annotations = filter(pred, tier)
if not filtered_annotations:
    print("NO RESULT")
    sys.exit(0)

filteredtier = Tier(tier.Name)
for a in filtered_annotations:
    filteredtier.Add(a)

if fileoutput is None:
    for a in filteredtier:
        print(a)
else:
    trs = Transcription()
    trs.Add(filteredtier)
    sppas.src.annotationdata.aio.write(fileoutput, trs)
