# Remodel Overview
Created Dec 2018 by Alex Chu. Last updated 190509 AEC

## Introduction & a quick summary of this document
This is an overview of the key concepts underlying RosettaRemodel. 
- The [Rosetta software suite](https://www.rosettacommons.org/docs/latest/Home) is a massive library of programs that do all kinds of things with protein structure modeling. It was first developed in [the David Baker lab](https://www.bakerlab.org/). 
- RosettaRemodel is just one app/executable in that library; it's one of the main apps in that framework for protein design.
- It combines backbone design (specifying the overall fold); sequence design (packing sidechains onto the backbone); and refinement (wiggling your structure to get it to settle into a more realistic conformation).
- In many of these steps, what's running under the hood is called the Metropolis-Hastings algorithm. This is a type of Monte Carlo algorithm, which is a fancy name for random sampling algorithms.
- This is meant to complement the main documentation at [https://www.rosettacommons.org/docs/latest/application_documentation/design/Remodel](https://www.rosettacommons.org/docs/latest/application_documentation/design/Remodel) and [https://www.rosettacommons.org/docs/latest/application_documentation/design/rosettaremodel](https://www.rosettacommons.org/docs/latest/application_documentation/design/rosettaremodel).

## The Remodel workflow

Remodel basically combines three main functions from Rosetta into a single app. These are backbone remodeling, sequence design, and relax/minimization. At any point, you might be using anywhere from one to all three of these functions in a single job. 

### Backbone remodeling
Backbone remodeling refers to altering the secondary structure (SS), or phi-psi torsional angles of the peptide backbone. Varying these phi-psi angles is what lets you define a segment of residues as an alpha helix, or a beta strand, or a loop. Remodel does this by fragment sampling: taking out the part of your protein you are trying to remodel, randomly taking protein "fragments," or small segments of native proteins structures from the PDB, and trying to stick them into your structure. If they stick nicely*, then it keeps it there. If it doesn't, it tries again. If you have a discontinuity in the backbone (called a chainbreak), say if you are remodeling a chunk in the middle of your protein, it will try to close this break with fragment sampling and closure algorithms like CCD or KIC.

At this stage, the amino acid sequence (sidechains) are not super important. If you only use this function of Remodel, you might be surprised to see that your output structure is all valines; this is because Rosetta doesn't explicitly model all the sidechains in backbone mode. To make it computationally easier, it replaces all the sidechains with blobs, or "centroids," that are supposed to resemble the "average" sidechain. At output time, these centroids are saved to PDBs as valines.  

*See the Monte Carlo section

![Protein torsional angles](/images/phi_psi_torsional_diagram.jpg)

### Sequence design
Sequence design is the second stage that involves placing sidechains once you have a defined backbone. The sequence space of a protein from a design perspective is enormous: It is (length of protein) ^ (20 amino acids) ^ (chi1 rotamer angle values) ^ (chi2 rotamer value angles) ^ ...as many rotamer angles as you need. Since it's impossible to try out every sequence in this space, Rosetta uses Monte Carlo random sampling to pick the best sidechains and rotamers. The Rosetta "packer" does this by randomly picking an amino acid position, randomly picking a sidechain to go there, randomly picking the rotamer, or orientation, of that sidechain, and then if it this all looks good*, then it keeps it. Otherwise it discards this random sample and starts again. It does this a million times until every position has a sidechain that fits pretty well.  

*See the Monte Carlo section

### Refinement
Relax (also called refinement or minimization) is a final energy minimization step that is carried out once you have a complete structure (backbone + sidechains). It's like when you scoop flour into a cup and shake it around a little to make sure any air pockets collapse and extra stuff falls away, so it all fits together nicely.

### Workflow & subway map
At the end of the day, you actually use Remodel by running the executable `remodel.linuxgccrelease` in Terminal (with maybe some variations in the exact command if you don't use Linux) and giving it a structure and a number of arguments. These arguments/flags/options tell Remodel what you want it to do to your structure. An actual command might look like this:
```
remodel.default.linuxgccrelease -in:file:s MyProtein.pdb -blueprint MyBlueprint.bp -use_pose_relax
```

Here is a "subway map" for Remodel. It shows the workflow for the three functions/modes just discussed, and some of the common flags that might be used at each step. It might look a little complex, but we'll try to walk through the main ideas here.  

- First you provide your input PDB structure and blueprint, and maybe some constraint or symmetry definition files. 
- Next it enters backbone stage, where it does fragment sampling and loop closure, and which should give you a complete backbone (you can skip this step with `-bypass_fragments` or `-bypass_closure`). 
- Next, if you have asked it to `-build_disulf`, it will try to design disulfide bridges. 
- Then it proceeds to design stage (you can skip this with `-remodel:design:no_design`). This is where you decide if design is guided by your blueprint, by the neighbors each residue has, or its buried surface area. 
- Then it proceeds to the relax stage, where you can choose what kind of relax algorithm (e.g. `-use_pose_relax` or `-use_cart_relax`) you want to run on the structure.
- Remodel then repeats the previous two steps by default 3 times, which you can change using `-remodel:dr_cycles [int]`, and saves the output files. Then you can open these and look at them in PyMOL!

![Remodel Subway Map](/images/RemodelSubwayMap.png)

## Monte Carlo and the Rosetta energy function

How does Rosetta actually do backbone or sequence design? Nearly all of the hard computational work in Rosetta is done with a method called Monte Carlo sampling, which is basically just random sampling. The algorithm (specifically called the Metropolis-Hastings algorithm) works like this:

1. Initialize your system. (e.g., define your starting structure).
2. Score your current system. (e.g., energy of structure A is -400).
2. Perturb the system. (e.g., mutate position 58 to alanine to generate structure B).
3. Score the perturbed system. (e.g. energy of structure B is -450).
4. Calculate the acceptance probability, alpha = min(1, exp(-energyA - energyB)). (e.g., alpha = 1).
5. Keep the perturbation with probability alpha, i.e. if alpha = 1, keep B. If alpha = 0.5, flip a coin to see if you should keep A or B. Whichever one you keep becomes your current system.
6. Repeat steps 2-5 until you've converged on a good solution.

The basic idea is you just randomly stumble around on the energy landscape, roughly going downhill, until you aren't really moving anymore. (figure).

The key component to all of this working, for protein design, is how good you are at scoring and comparing your systems. If your scorefunction is bad, you might keep accepting perturbations that you think are good, but are actually not that good. In Rosetta, scoring is done with the [Rosetta energy function](https://pubs.acs.org/doi/abs/10.1021/acs.jctc.7b00125). It covers a lot of important things, like:
- Lennard-Jones attraction/repulsion
- Hydrogen bond energy
- Disulfide bridge energy
- Electrostatics  

It's pretty good, and allows us to design proteins to atomic accuracy. But it also is far from perfect, and doesn't exactly reflect what's going on in nature. For example, it doesn't handle solvent explicitly, or entropic considerations. This is why we can't design proteins to exact, perfect accuracy, and in some hard cases, we can be way off. One day, when we have a perfect scorefunctions, maybe we'll be able to perfect our protein design abilities!  

## Some notes about implementation
The blueprint tells Remodel what you want it to do to your structure. Here is a brief explanation of the blueprint syntax: [Blueprint syntax](https://www.rosettacommons.org/docs/latest/application_documentation/design/Remodel#blueprint)

TODO jd2:no_output. 
