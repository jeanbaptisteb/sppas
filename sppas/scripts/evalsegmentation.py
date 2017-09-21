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

    scripts.evalsegmentation.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    ... a script to evaluate a segmentation vs a reference segmentation.

    It estimates the Unit Boundary Positioning Accuracy and generates an
    R script to draw a boxplot of the evaluation.

"""
import sys
import os
import codecs
import os.path
from argparse import ArgumentParser
import subprocess

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas.src.calculus.scoring.ubpa import ubpa
from sppas.src.annotationdata.transcription import Transcription
import sppas.src.annotationdata.aio

# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------

vowels = ["a","e","i","i:","o","u","y","A","E","I","M","O","Q","U","V","Y","a~","A~", "E~", "e~","i~","o~","O~","O:",
          "u~","U~","eu","EU","{","}","@","1","2","3","6","7","8","9","&","3:r","OI","@U","eI","ai","aI","au","aU",
          "aj","aw","ei","ew","ia","ie","io","ja","je","jo","ju","oj","ou","ua","uo","wa","we","wi","wo","ya","ye","yu"]
consonants = ["b","b_<","c","d","d`","f","g","g_<","h","j","k","l","l`","m","n","n`","p","q","r","r`","r\\", "rr",
              "s","s`","t","t`","v","w","x","z","z`","B","C","D","F","G","H","J","K","L","M","N","R","S","T","W","X","Z",
              "4","5","?","ts","tS","dz","dZ","tK","kp","Nm","rr","ss","ts_h","k_h","p_h","t_h","ts_hs","tss"]

# ----------------------------------------------------------------------------
# Functions
# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------
# Functions to manage input annotated files


def get_tier(filename, tier_idx):
    """ Returns the tier of the given index in an annotated file.

    :param filename: Name of the annotated file
    :param tier_idx: Index of the tier to get
    :returns: Tier or None

    """
    try:
        trs_input = sppas.src.annotationdata.aio.read(filename)
    except Exception:
        return None
    if tier_idx < 0 or tier_idx >= trs_input.GetSize():
        return None

    return trs_input[tier_idx]


def get_tiers(ref_filename, hyp_filename, ref_idx=0, hyp_idx=0):
    """ Returns a reference and an hypothesis tier from annotated files.

    :param ref_filename: Name of the annotated file with the reference
    :param hyp_filename: Name of the annotated file with the hypothesis
    :param ref_idx: (int)
    :param hyp_idx: (int)

    :returns: a tuple with Tier or None for both ref and hyp

    """
    ref_tier = get_tier(ref_filename, ref_idx)
    hyp_tier = get_tier(hyp_filename, hyp_idx)

    return ref_tier, hyp_tier

# ----------------------------------------------------------------------------
# Function to draw the evaluation as BoxPlots (using an R script)


def test_R():
    """ Test if Rscript is available as a command of the system. """

    try:
        NULL = open(os.devnull, "w")
        subprocess.call(['Rscript'], stdout=NULL, stderr=subprocess.STDOUT)
    except OSError:
        return False
    return True


def exec_Rscript(filenamed, filenames, filenamee, rscriptname, pdffilename):
    """ Write the R script to draw boxplots from the given files, then
    execute it, and delete it.

    :param pdffilename: the file with the result.

    """
    with codecs.open(rscriptname, "w", "utf8") as fp:
        fp.write("#!/usr/bin/env Rscript \n")
        fp.write("# Title: Boxplot for phoneme alignments evaluation \n")
        fp.write("\n")
        fp.write("args <- commandArgs(trailingOnly = TRUE) \n")
        fp.write("\n")
        fp.write("# Get datasets \n")
        fp.write('dataD <- read.csv("%s",header=TRUE,sep=",") \n' % filenamed)
        fp.write('dataPS <- read.csv("%s",header=TRUE,sep=",") \n' % filenames)
        fp.write('dataPE <- read.csv("%s",header=TRUE,sep=",") \n' % filenamee)
        fp.write("\n")
        fp.write("# Define Output file \n")
        fp.write('pdf(file="%s", paper="a4") \n'%pdffilename)
        fp.write("\n")
        fp.write("# Control plotting style \n")
        fp.write("par(mfrow=c(3,1))    # only one line and one column \n")
        fp.write("par(cex.lab=1.2)     # controls the font size of the axis title \n")
        fp.write("par(cex.axis=1.2)    # controls the font size of the axis labels \n")
        fp.write("par(cex.main=1.6)    # controls the font size of the title \n")
        fp.write("\n")
        fp.write("# Then, plot: \n")
        fp.write("boxplot(dataD$DeltaD~dataD$PhoneD, \n")
        fp.write('   main="Delta Duration",             # graphic title \n')
        fp.write('   ylab="T(automatic) - T(manual)",   # y axis title \n')
        fp.write('   #range=0,                          # use min and max for the whisker \n')
        fp.write('   outline = FALSE,                   # REMOVE OUTLIERS \n')
        fp.write('   border="blue", \n')
        fp.write('   ylim=c(-0.05,0.05), \n')
        fp.write('   col="pink") \n')
        fp.write("   abline(0,0) \n")
        fp.write("\n")
        fp.write('boxplot(dataPS$DeltaS~dataPS$PhoneS, \n')
        fp.write('   main="Delta Start Position", \n')
        fp.write('   ylab="T(automatic) - T(manual)", \n')
        fp.write('   outline = FALSE, \n')
        fp.write('   border = "blue", \n')
        fp.write('   ylim=c(-0.05,0.05), \n')
        fp.write('   col = "pink") \n')
        fp.write('   abline(0,0) \n')
        fp.write("\n")
        fp.write('boxplot(dataPE$DeltaE~dataPE$PhoneE, \n')
        fp.write('   main="Delta End Position", \n')
        fp.write('   ylab="T(automatic) - T(manual)", \n')
        fp.write('   outline = FALSE,  \n')
        fp.write('   border="blue", \n')
        fp.write('   ylim=c(-0.05,0.05), \n')
        fp.write('   col="pink") \n')
        fp.write('abline(0,0) \n')
        fp.write('graphics.off() \n')
        fp.write("\n")

    command = "Rscript "+rscriptname
    try:
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()
        line = p.communicate()
    except OSError as e:
        os.remove(rscriptname)
        return e

    os.remove(rscriptname)
    if retval != 0:
        return line

    return ""


def boxplot(deltaposB, deltaposE, deltaposD, extras, outname, vector, name):
    """ Create a PDF file with boxplots, but selecting only a subset of phonemes.

    :param vector: the list of phonemes

    """
    filenamed = outname+"-delta-duration-"+name+".csv"
    filenames = outname+"-delta-position-start-"+name+".csv"
    filenamee = outname+"-delta-position-end-"+name+".csv"

    fpb = codecs.open(filenames, "w", 'utf8')
    fpe = codecs.open(filenamee, "w", 'utf8')
    fpd = codecs.open(filenamed, "w", 'utf8')
    fpb.write("PhoneS,DeltaS\n")
    fpe.write("PhoneE,DeltaE\n")
    fpd.write("PhoneD,DeltaD\n")
    for i, extra in enumerate(extras):
        etiquette = extra[0]
        tag = extra[2]
        if etiquette in vector:
            if tag != 0:
                fpb.write("%s,%f\n" % (etiquette, deltaposB[i]))
            if tag != -1:
                fpe.write("%s,%f\n" % (etiquette, deltaposE[i]))
            fpd.write("%s,%f\n" % (etiquette, deltadur[i]))
    fpb.close()
    fpe.close()
    fpd.close()

    message = exec_Rscript(filenamed, filenames, filenamee, outname+".R", outname+"-delta-"+name+".pdf")

    os.remove(filenamed)
    os.remove(filenames)
    os.remove(filenamee)
    return message


# ----------------------------------------------------------------------------
# Main program
# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------
# Verify and extract args:

parser = ArgumentParser(usage="%s -fr ref -fh hyp [options]" % os.path.basename(PROGRAM), 
                        description="... a script to compare two segmentation boundaries, "
                                    "in the scope of evaluating an hypothesis vs a reference.")

parser.add_argument("-fr",
                    metavar="file",
                    required=True,
                    help='Input annotated file/directory name of the reference.')

parser.add_argument("-fh",
                    metavar="file",
                    required=True,
                    help='Input annotated file/directory name of the hypothesis.')

parser.add_argument("-tr",
                    metavar="file",
                    type=int,
                    default=1,
                    required=False,
                    help='Tier number of the reference (default=1).')

parser.add_argument("-th",
                    metavar="file",
                    type=int,
                    default=1,
                    required=False,
                    help='Tier number of the hypothesis (default=1).')

parser.add_argument("-o",
                    metavar="path",
                    required=False,
                    help='Path for the output files.')

parser.add_argument("--quiet",
                    action='store_true',
                    help="Disable the verbosity.")

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------
# Global variables

idxreftier = args.tr - 1
idxhyptier = args.th - 1
files = []      # List of tuples: (reffilename, hypfilename)
deltadur = []   # Duration of each phoneme
deltaposB = []  # Position of the beginning boundary of each phoneme
deltaposE = []  # Position of the end boundary of each phoneme
deltaposM = []  # Position of the center of each phoneme
extras = []     # List of tuples: (evaluated phoneme,hypothesis file names, a tag)

# ----------------------------------------------------------------------------
# Prepare file names to be analyzed, as a list of tuples (ref,hyp)

outpath = None
if args.o:
    outpath = args.o
    if not os.path.exists(outpath):
        os.mkdir(outpath)

if os.path.isfile(args.fh) and os.path.isfile(args.fr):
    hypfilename, extension = os.path.splitext(args.fh)
    outbasename = os.path.basename(hypfilename)
    if outpath is None:
        outpath = os.path.dirname(hypfilename)
    outname = os.path.join(outpath, outbasename)

    files.append((os.path.basename(args.fr), os.path.basename(args.fh)))
    refdir = os.path.dirname(args.fr)
    hypdir = os.path.dirname(args.fh)

elif os.path.isdir(args.fh) and os.path.isdir(args.fr):
    if outpath is None:
        outpath = args.fh
    outname = os.path.join(outpath, "phones")

    refdir = args.fr
    hypdir = args.fh

    reffiles = []
    hypfiles = []
    for fr in os.listdir(args.fr):
        if os.path.isfile(os.path.join(refdir, fr)):
            reffiles.append(fr)
    for fh in os.listdir(args.fh):
        if os.path.isfile(os.path.join(hypdir, fh)):
            hypfiles.append(os.path.basename(fh))

    for fr in reffiles:
        basefr, extfr = os.path.splitext(fr)
        if not extfr.lower() in sppas.src.annotationdata.aio.extensions:
            continue
        for fh in hypfiles:
            basefh, extfh = os.path.splitext(fh)
            if not extfh.lower() in sppas.src.annotationdata.aio.extensions:
                continue
            if fh.startswith(basefr):
                files.append((fr, fh))

else:
    print("Both reference and hypothesis must be of the same type: file or directory.")
    sys.exit(1)

if not args.quiet:
    print("Results will be stored in: {}".format(outname))

# ----------------------------------------------------------------------------
# Evaluate the delta from the hypothesis to the reference
# Delta = T(hyp) - T(ref)

for f in files:

    fr = os.path.join(refdir, f[0])
    fh = os.path.join(hypdir, f[1])
    reftier, hyptier = get_tiers(fr, fh, idxreftier, idxhyptier)
    if reftier is None or hyptier is None:
        print("[ INFO ] No aligned phonemes found in tiers. Nothing to do. ")
        continue
    if reftier.GetSize() != hyptier.GetSize():
        print("[ ERROR ] Hypothesis: {} -> {} vs Reference: {} -> {} phonemes.".format(f[1], hyptier.GetSize(), f[0], reftier.GetSize()))
        continue
    if not args.quiet:
        print("[ OK ] Hypothesis: {} vs Reference: {} -> {} phonemes.".format(f[1], f[0], reftier.GetSize()))

    # ----------------------------------------------------------------------------
    # Compare boundaries and durations of annotations.

    i = 0
    imax = reftier.GetSize()-1

    for rann, hann in zip(reftier, hyptier):
        etiquette = rann.GetLabel().GetValue()
        if etiquette == "#":
            continue
        # begin
        rb = rann.GetLocation().GetBegin().GetValue()
        hb = hann.GetLocation().GetBegin().GetValue()
        deltab = hb-rb
        # end
        re = rann.GetLocation().GetEnd().GetValue()
        he = hann.GetLocation().GetEnd().GetValue()
        deltae = he-re
        # middle
        rm = rb + (re-rb)/2.
        hm = hb + (he-hb)/2.
        deltam = hm-rm
        # duration
        rd = rann.GetLocation().GetDuration().GetValue()
        hd = hann.GetLocation().GetDuration().GetValue()
        deltad = hd-rd

        tag = 1
        if i == 0:
            tag = 0
        elif i == imax:
            tag = -1

        # Add new values into vectors, to evaluate the accuracy
        deltaposB.append(deltab)
        deltaposE.append(deltae)
        deltaposM.append(deltam)
        deltadur.append(deltad)
        extras.append((etiquette, fh, tag))

        i += 1

# ----------------------------------------------------------------------------
# Save delta values into output files

fpb = codecs.open(os.path.join(outname)+"-delta-position-start.txt", "w", 'utf8')
fpe = codecs.open(os.path.join(outname)+"-delta-position-end.txt", "w", 'utf8')
fpm = codecs.open(os.path.join(outname)+"-delta-position-middle.txt", "w", 'utf8')
fpd = codecs.open(os.path.join(outname)+"-delta-duration.txt",  "w", 'utf8')

fpb.write("Phone Delta Filename\n")
fpe.write("Phone Delta Filename\n")
fpm.write("Phone Delta Filename\n")
fpd.write("Phone Delta Filename\n")

for i, extra in enumerate(extras):
    etiquette = extra[0]
    filename = extra[1]
    tag = extra[2]
    if tag != 0:
        fpb.write("%s %f %s\n" % (etiquette, deltaposB[i], filename))
    if tag != -1:
        fpe.write("%s %f %s\n" % (etiquette, deltaposE[i], filename))
    fpm.write("%s %f %s\n" % (etiquette, deltaposM[i], filename))
    fpd.write("%s %f %s\n" % (etiquette, deltadur[i], filename))

fpb.close()
fpe.close()
fpm.close()
fpd.close()

# ----------------------------------------------------------------------------
# Estimates the Unit Boundary Positioning Accuracy

if not args.quiet:
    ubpa(deltaposB, "Start boundary", sys.stdout)

with open(outname+"-eval-position-start.txt", "w") as fp:
    ubpa(deltaposB, "Start boundary position", fp)
with open(outname+"-eval-position-end.txt", "w") as fp:
    ubpa(deltaposE, "End boundary position", fp)
with open(outname+"-eval-position-middle.txt", "w") as fp:
        ubpa(deltaposM, "Middle boundary position", fp)

with open(outname+"-eval-duration.txt") as fp:
    ubpa(deltadur, "Duration", fp)

# ----------------------------------------------------------------------------
# Draw BoxPlots of the accuracy via an R script

if test_R() is False:
    sys.exit(0)

message = boxplot(deltaposB, deltaposE, deltadur, extras, outname, vowels, "vowels")
if len(message) > 0 and not args.quiet:
    print("{:s}".format(message))

message = boxplot(deltaposB, deltaposE, deltadur, extras, outname, consonants, "consonants")
if len(message) > 0 and not args.quiet:
    print("{:s}".format(message))

others = []
for extra in extras:
    etiquette = extra[0]
    if not (etiquette in vowels or etiquette in consonants or etiquette in others):
        others.append(etiquette)

if len(others) > 0:
    message = boxplot(deltaposB, deltaposE, deltadur, extras, outname, others, "others")
    if len(message) > 0 and not args.quiet:
        print("{:s}".format(message))
