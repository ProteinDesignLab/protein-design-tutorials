# import pyrosetta
from pyrosetta import *
init()

# additional imports
import random
import math

#######################################################################
# 0. Misc

# analyze a score file:
import pandas as pd
def parse_score_file(filename):
    score_file = open(filename).readlines()
    headers = score_file[1].split()[1:]  # isolate the column headers
    score_data = [line.split()[1:] for line in score_file[2:]]
    for scores in score_data:
        if len(scores) != len(headers):
            sys.exit('Error in input file at decoy ' + scores[-1] + '.')
    return headers, score_data

# (1) Select rows with CAPRI_rank=3.0
headers, score_data = parse_score_file('fixed_docking_score.sc')
df = pd.DataFrame(score_data, columns = headers, dtype=float)
#print(df.dtypes)
df_CAPRIsort = df.sort_values(by='CAPRI_rank',ascending=False)
list_CAPRIsort = []
for index, row in df_CAPRIsort.iterrows():
    if row['CAPRI_rank'] < 3:
        break
    list_CAPRIsort.append(row)
df_CAPRIsort = pd.DataFrame(list_CAPRIsort, columns = headers, dtype=float)

# (2) Sort rows by I_sc (interface score)
df_ISCsort = df_CAPRIsort.sort_values(by='I_sc')

# (3) print only the relevant metrics (CAPRI_rank, Fnat, I_sc)
subdf_ISCsort = df_ISCsort[['CAPRI_rank', 'Fnat', 'I_sc', 'description']]
print('relevant metrics and the description for high-quality models: ')
print(subdf_ISCsort)

# ask user for flags:
import argparse
# Ask user for:
# (a) variable number of terms (--terms)
# (b) variable number of weights (--weights)
parser = argparse.ArgumentParser(description="Change the default weights of selected score terms and display which terms were changed")
parser.add_argument("--terms", "-t", action="store", type=str, help="variable number of terms", nargs='+', required=True)
parser.add_argument("--weights", "-w", action="store", type=str, help="variable number of weights", nargs='+', required=True)
args = parser.parse_args()
terms = args.terms
weights = args.weights


#######################################################################
# 1. Structural Data

# import pdb
from pyrosetta.toolbox import pose_from_rcsb
ras = pose_from_rcsb("6Q21")

# what is residue 500?
print(ras.residue(500).name())

# what is chain and number of 500th residue?
print(ras.pdb_info().chain(500))
print(ras.pdb_info().number(500))

# convert between pose and pdb
print(ras.pdb_info().pose2pdb(25))
print(ras.pdb_info().pdb2pose('A',100))

# get phi/psi/chi of residue 5
print(ras.phi(5))
print(ras.psi(5))
print(ras.chi(1, 5))

# select particular atoms
# in a pdb -> order of atoms in residue 5 is N, CA, C
R5N = AtomID(1, 5)
R5CA = AtomID(2, 5)
R5C = AtomID(3, 5)

# use selected atoms to find bond lengths
print(ras.conformation().bond_length(R5N, R5CA))
print(ras.conformation().bond_length(R5CA, R5C))

# the N-Calpha-C bond angle?
print(ras.conformation().bond_angle(R5N, R5CA, R5C))

# Change the phi/psi/chi and bond length
ras.set_phi(5, -60)
ras.set_psi(5, -43)
ras.set_chi(1, 5, 180)
ras.conformation().set_bond_length(R5N, R5CA, 1.5)
ras.conformation().set_bond_angle(R5N, R5CA, R5C, 110./180.*3.14159)

# Make PyMOL listen to changes
# Go into pymol, and run the "run PyMOL-RosettaServer.py"
# now, instantiate the PyMOLMover and apply it to a pose
from pyrosetta import PyMOLMover
pymol = PyMOLMover()
pymol.apply(ras) # Apply the "apply" method to the pose after any change to see effect

#######################################################################
# 2. Scoring

# Define a score function
from pyrosetta.teaching import *
scorefxn = get_fa_scorefxn()

# you can set your own custom score function
scorefxn2 = ScoreFunction()
scorefxn2.set_weight(fa_atr, 1.0)
scorefxn2.set_weight(fa_rep, 1.0)

# show score
print(scorefxn(ras))

# break energy into individual pieces with show method
scorefxn.show(ras)

# you can get individual energy of a residue
print(ras.energies().show(24))

# The hydrogen score component are stored HBondSet object
from rosetta.core.scoring.hbonds import HBondSet
hbond_set = HBondSet(ras, True) # False for only bb-bb Hbonds

# use EMapVector() class to store energy data
# for instance, store contact independent two-body interaction energies
res_num1 = ras.pdb_info().pdb2pose('D', 102)
res_num2 = ras.pdb_info().pdb2pose('A', 108)
rsd1= ras.residue(res_num1)
rsd2 = ras.residue(res_num2)
emap = EMapVector()
scorefxn.eval_ci_2b(rsd1, rsd2, ras, emap)
print(emap[fa_atr])
print(emap[fa_rep])
print(emap[fa_sol])

#######################################################################
# 3. Folding

# create poly-A chain and set all peptide bonds to trans
deNovoPose = pose_from_sequence('A'*10, "fa_standard")
for res in range(1, deNovoPose.total_residue() + 1):
    deNovoPose.set_omega(res, 180)
pymol.apply(deNovoPose)

# create a score function to include Van der Wals and H-bonds only
score = ScoreFunction()
score.set_weight(fa_atr, 0.8)
score.set_weight(fa_rep, 0.44)
score.set_weight(hbond_sr_bb, 1.17)

# Now, we can write a program that implements Monte Carlo algorithm
# to fold this pose
PHI = 0; PSI = 1; kT = 1.0 # constants
# subroutines/functions
def random_move(pose):
    res = random.randint(1, pose.total_residue()) # select random residue
    # select and set random torsion angle distributed around old angle
    if random.randint(PHI, PSI) == PHI:
        torsion = pose.phi(res)
        a = random.gauss(torsion, 25)
        pose.set_phi(res, a)
    else:
        torsion = pose.psi(res)
        a = random.gauss(torsion, 25)
        pose.set_psi(res, a)
# initialize pose objects
last_pose = Pose()
low_pose = Pose()
# initialize low score objects
low_pose.assign(deNovoPose)
low_score = score(deNovoPose)
# iterate 100x MonteCarlo sampling
for i in range(100):
    last_score = score(deNovoPose)
    last_pose.assign(deNovoPose)
    random_move(deNovoPose)
    new_score = score(deNovoPose)
    print( "Iteration:", i, "Score:", new_score, "Low Score:", low_score )
    deltaE = new_score - last_score
    # accept if new energy score is improved
    # reject or accept if new energy score is worse based on Metropolis criteria
    if deltaE > 0:
        P = math.exp(-deltaE/kT)  # probability of accepting move diminishes exponetially with increasing energy
        roll = random.uniform(0.0, 1.0)
        if roll >= P:
            deNovoPose.assign(last_pose)  # reject pose and reassign previous
            continue
    # if new pose is accepted, store lowest score and associated pose
    if new_score < low_score:
        low_score = new_score
        low_pose.assign(deNovoPose)
# output files
deNovoPose.dump_pdb("poly-A_final.pdb")
low_pose.dump_pdb("poly-A_low.pdb")

# you can convert from full atom to centroid
switch = SwitchResidueTypeSetMover("centroid")
switch.apply(ras)
switch2 = SwitchResidueTypeSetMover("fa_standard")
switch2.apply(ras)

# and you can apply fragement insertion to a pose
# with ClassicFragmentMover()
fragset = rosetta.core.fragment.ConstantLengthFragSet(3)
fragset.read_fragment_file("aat000_03_05.200_v1_3")
movemap = MoveMap() # a MoveMap() object specifies what can be moved
movemap.set_bb(True)
mover_3mer = rosetta.protocols.simple_moves.ClassicFragmentMover(fragset, movemap)
fragPose = Pose()
make_pose_from_sequence(fragPose, "RFPMMSTFKVLLCGAVLSRIDAGRFPMMSTFKVLLCGAVLSRIDAG", "centroid")
for res in range(1, fragPose.total_residue() + 1):
    fragPose.set_omega(res, 180)
mover_3mer.apply(fragPose)

#######################################################################
# 3. Refinement

# Create a small mover -> to perturb phi/psi by small angle
# Create a shear mover -> pertub phi or a random residue by a small angle, and psi of same residue by same angle of opposite sign
from rosetta.protocols.simple_moves import *
kT = 1.0 # constant
n_moves = 1 # constant
movemap = MoveMap()
movemap.set_bb(True) # allowing only movement of backbone
small_mover = SmallMover(movemap, kT, n_moves)
shear_mover = ShearMover(movemap, kT, n_moves)

# Adjust the maximum magnitude of perturbations
small_mover.angle_max("H", 10)
small_mover.angle_max("E", 10)
small_mover.angle_max("L", 10)

# Create a MinMover Object to minimize pose
from rosetta.protocols.minimization_packing import *
min_mover = MinMover()
mm4060 = MoveMap()
mm4060.set_bb_true_range(40, 60) # here we specify we can move backbone phi/psi/omega of residues 40-60
scorefxn = get_fa_scorefxn()
min_mover.movemap(mm4060)
min_mover.score_function(scorefxn)

# to see the movers in action, we can use a MonteCarlo object:
# after the pose is modified by a mover, we can tell
# MonteCarlo object to automatically accept or reject the new
# conformation, and update the internal counters (i.e.
# current pose, and lowest energy pose)
# if mc.boltzmann returns true, then it accepted, if it returns false, then it rejected
mc = MonteCarlo(ras, scorefxn, kT)
for i in range(1,2):
    # 1. small move pose
    small_mover.apply(ras)
    # 2. shear move pose
    shear_mover.apply(ras)
    # 3. minimize pose
    min_mover.apply(ras)
    # accept or reject new pose
    print(mc.boltzmann(ras))
mc.show_scores()

# Trial Movers combine a mover with a MonteCarlo object
# if you call a trial mover, it tries a move, and then
# accepts/rejects with the MonteCarlo object
trial_mover = TrialMover(small_mover, mc)
trial_mover.apply(ras)

# A sequence mover applies several movers in succession
seq_mover = SequenceMover()
seq_mover.add_mover(small_mover)
seq_mover.add_mover(shear_mover)
seq_mover.add_mover(min_mover)

# now we can create a trial mover based on this sequence mover
# and apply it 5x on a pose
trial_mover = TrialMover(seq_mover, mc)
for i in range(0,1):
    trial_mover.apply(ras)

# similarly, a repeat mover will apply its input Mover n times
n = 5
repeat_mover = RepeatMover(trial_mover, n)

# the entire Rosetta refinement protocol is available as a mover
from rosetta.protocols.relax import *
relax = ClassicRelax()
relax.set_scorefxn(scorefxn)
relax.apply(ras)
