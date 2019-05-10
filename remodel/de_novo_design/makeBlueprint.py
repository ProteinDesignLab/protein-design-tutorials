# Title: 		makeBlueprint.py
# Author:		Raphael Eguchi
# Modified:		171219 Raphael Eguchi
# Description:	Generates a blueprint given a pdb.
# Usage: 		python makeBlueprint.py mystructure.pdb

from Bio.PDB import *
import os
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))
input_dir = dir_path + '/' + sys.argv[1]
output_dir = dir_path + '/' + sys.argv[1][:-4] + ".bp"

parser = PDBParser()
ppb = PPBuilder()  # convert Structure object to polypeptide object.
output = open(output_dir, 'w')
handle = open(input_dir, 'r')
structure = parser.get_structure('TIM10', handle)
seq = ""

for pp in ppb.build_peptides(structure):  # converts each chain to peptide object.
    seq += str(pp.get_sequence()) # dumps all chains into a single file.

print len(seq)
print seq

for i in range(0,len(seq)):
    if (i == len(seq) - 1):
        line = str(i+1) + ' ' + seq[i] + ' ' + "."
    else:
        line = str(i+1) + ' ' + seq[i] + ' ' + "." + "\n"
    output.write(line)
output.close()
