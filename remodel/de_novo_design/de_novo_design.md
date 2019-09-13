# De novo design with RosettaRemodel
Created Dec 2018 by Alex Chu.  

This is a step by step tutorial to de novo protein design with fragment sampling in RosettaRemodel. You should get to experience many of the main functionalities of Remodel in the course of this tutorial:
- backbone design
- sequence design
- remodel and redesign one of the loops
- build in a disulfide  

The tutorial should be fairly modular, so you can skip to any of the sections if you don't think some of them are as useful to you. If you run into bugs or have questions about some of the flags, [these lab documents](https://github.com/ProteinDesignLab/protein-design-tutorials/tree/master/remodel) may or may not be helpful. You can also refer to the main Remodel docs at [https://www.rosettacommons.org/docs/latest/application_documentation/design/Remodel](https://www.rosettacommons.org/docs/latest/application_documentation/design/Remodel) and [https://www.rosettacommons.org/docs/latest/application_documentation/design/rosettaremodel](https://www.rosettacommons.org/docs/latest/application_documentation/design/rosettaremodel).

## 0. Prerequisites
- You should be familiar with basic Linux stuff like `mv`, `cd`, vim, and stuff like that. [Linux Tutorial](https://ryanstutorials.net/linuxtutorial/)
- Be able to look at protein structures in PyMOL (or similar program).
- You should have a working build of RosettaRemodel, so that you can run the `remodel.linuxgccrelease` executables (or similar looking ones). 
  - If you have access to Sherlock, the Stanford HPC cluster, and have been added to the `possu` group, then the executables should be in `$PI_HOME/working_build/190322_standard/Rosetta/main/source/bin/`.
  - If you have Sherlock access but are not in `possu`, then use the command `ml rosetta` to load the Sherlock installation. Then you can use the Remodel executable by simply typing `remodel.default.linuxgccrelease` (you can tab-complete this).
  - If this didn't make any sense to you, you should read the [Slurm/Sherlock tutorial](https://github.com/ProteinDesignLab/protein-design-tutorials/blob/master/intro_to_sherlock.md).
- This tutorial relies on some basic knowledge of how RosettaRemodel works, i.e. some of what is discussed in [Remodel Overview](https://github.com/ProteinDesignLab/protein-design-tutorials/blob/master/remodel/remodel_overview.md). If some of the terms or concepts in here aren't familiar to you yet, you can refer to that document.

## 1. Design a backbone for the TIM barrel
In this tutorial, let's build the fourfold repeat TIM barrel from [Huang et al](https://www.nature.com/articles/nchembio.1966). De novo design in this framework begins by specifying a protein backbone, i.e. folded secondary structures, onto which sequences can be designed.  

![de novo TIM barrel](/images/timb.png)

To start, you'll need:
- a stub PDB of alanine or some other residue just as a starting point for Remodel, which we've provided in `ala.pdb`
- a blueprint specifying the fold you want, which we've provided in `de_novo.bp`.   

You should open the blueprint in vim or with `cat de_novo.bp` to see how the secondary structures are set up. The blueprint specifies the fold of one-fourth of the TIM barrel, which is a beta-alpha-beta-alpha motif. Using flags we'll pass to Remodel, we'll instruct Remodel to 1) build this b-a-b-a motif, and then 2) repeat this 4 times to make the full TIM barrel. We've already worked out what the correct strand, helix, and loop lengths should be for you. Now, let's specify all the Rosetta flags, and save these in a file called `flags`:
```
-s ala.pdb
-remodel:blueprint de_novo.bp
-jd2:no_output
-overwrite
-remodel:design:no_design
-remodel:quick_and_dirty
-use_clusters false
-repeat_structure 4
-rg 2.0
-hb_lrbb 2.0
-hb_srbb 0.0
-vdw 1.0
-cenpack 1.0
-cbeta 1.0
-num_trajectory 10
-save_top 5
```
`jd2:no_output` suppresses output from the standard Rosetta job distributor in favor of the Remodel-specific output.  
`-overwrite` means that any old files with the same names as the output files will be overwritten.  
`-remodel:design:no_design` and `-remodel:quick_and_dirty` let us skip the design and refinement stages, respectively.  
`-repeat_structure 4` indicates that Rosetta should repeat the input four times. Here, since the input blueprint specifies just one of the four repeats (beta-alpha)-2; this flag completes the other three repeats.  
`-rg 2.0`, `-hb_lrbb 2.0`, and the four other listed flags with float arguments are derived from the supplementary material of the Huang et al. paper; they tune term weights for the Rosetta scorefunction.  
`-num_trajectory 10` means that we want to run 10 Monte Carlo trajectories, and `-save_top 5` means to save and output only the top 5 scoring results by Rosetta energy.  

With these starting arguments, and all of the above files in the same directory, we can begin a sampling run:  
```
[/path/to/]remodel.linuxgccrelease @flags
```  
Replace `[/path/to/]` with the path to the directory where your Rosetta executables are. If you add the path to your Rosetta executables to your bash profile, you can simply run  
```
remodel.linuxgccrelease @flags
```  

When the run is finished, you should have five new files in your directory, named `1.pdb`, `2.pdb`, and so on. These are your results! Open them in PyMOL and see which ones fit your target fold the best. Since we are only doing backbone design here, your sequence will be all valines (see [remodel_overview.md](https://github.com/ProteinDesignLab/protein-design-tutorials/blob/master/remodel_overview.md#backbone-remodeling) for an explanation of why). With our current run, you should look for structures that form a TIM-barrel like structure. If you don't see any, it could be due to a number of reasons. Perhaps your secondary structure lengths (we call this the topology) aren't correct - try different loop, strand, or helix lengths. (We've already worked out the topology for this design, so you don't need to worry about that.) Perhaps you aren't sampling deep enough - try it again and run it with more trajectories.  

A word about sampling. Since these are Monte Carlo solutions, you aren't guaranteed that any of these solutions are correct - if so, keep sampling until you get some that are. In this example flags file, we are running 10 trajectories, which is probably not enough - you should probably run and save about 10-100x that in practice. You can change the number of trajectories sampled with `-num_trajectory [int]`, or since this problem is easily parallelized, run the same command or job several times on several processors. On Sherlock, you can do this by setting the `#SBATCH --array=0-99` option in your sbatch file.  
- More generally, the number of trajectories you need to run will scale with the difficulty of your problem. 
- For most sampling problems in this tutorial, we might need somewhere on the order of 1e1 to 1e3 trajectories. 
- Proteins that are larger or harder to design might involve adding one or two orders of magnitude to that.
- Sometimes, it can be helpful to write a script that ranks your output structures on some metric (for example, maybe the distance between residue 1 and residue 184, which could indicate whether the structure forms a closed barrel). It's a little hacky, but this is protein design. The original TIM barrel involved fine-tuning a lot of the repeat-mode options in Rosetta to get the barrel to come together, but we won't go into how to do that here.  

Backbone design can be the hardest part of de novo design. It can be tricky figuring out what the correct topology is, or how much sampling you need. Often getting your trajectories to converge to a structure that both fits what you have envisioned and satisfies physical and chemical principles for stably folding protein structures can be very difficult. See this [thread on RosettaCommons](https://www.rosettacommons.org/node/10002) for some more discussion about why actually de novo designing a protein can be much more complicated than simply following this protocol. Please feel free to reach out to us in the lab if you'd like some guidance in this area.  

When selecting ideal backbone structures, you should look for 1) correct topology, as in whether the helices and strands are positioned correctly relative to each other, and 2) clean loops, as in loops where the backbone hydrogen bonds (C=O and N-H) are largely satisfied and the torsional angles are in permitted regions of Ramachandran space. 

## 2. Design a sequence that will fold into your backbone's structure
Once you have an ideal backbone structure, you can proceed to sequence design. If you weren't able to get a good peptide backbone for the de novo TIM barrel in Part 1, we have included one in the directory (`TIMbarrel_centroid_backbone.pdb`). For this tutorial, we will do simple automated sequence design, just so you can get a feel for how sequence design (sometimes just "design" for short) works in RosettaRemodel. If you want to learn how de novo sequence design is carried out in practice, see below*. There are many parallels.  

First, this time you'll generate your own blueprint using the provided python script.
```
python makeBlueprint.py TIMbarrel_centroid_backbone.pdb
```
In the blueprint, edit all the residues to be designed as `ALLAAxc`. If you are using vim, you can do this by typing `:%norm A ALLAAxc`. At this stage, we set the third column of the blueprint to "L" so that the protein relaxes smoothly. If you are using vim, you can do this by typing `:%s/\./L/g`. For the TIM barrel, the beginning of your blueprint might look like this:
```
1 A L ALLAAxc
2 V L ALLAAxc
3 V L ALLAAxc
4 V L ALLAAxc
5 V L ALLAAxc
6 V L ALLAAxc
7 V L ALLAAxc
8 V L ALLAAxc
...
```
To design the sequence, keep only the first 46 lines of the blueprint (one "quarter-barrel") and delete the rest; this specifies the same changes to be made to all four repeat segments. You can use the flags provided below. If you want to design the protein without repeating sequence, keep the whole blueprint but remove the `-repeat_structure 4` flag.
```
-s [your structure].pdb
-remodel:blueprint [your blueprint].bp
-jd2:no_output
-overwrite
-repeat_structure 4
-remodel:RemodelLoopMover:cyclic_peptide
-hb_lrbb 2.0 
-randomize_loops false
-bypass_fragments
-bypass_closure
-remodel:use_pose_relax
-remodel:dr_cycles 3
-soft_rep_design
-no_optH false
-ex1
-ex2
-linmem_ig 10
-num_trajectory 1
-save_top 1
```
`-remodel:use_pose_relax` defines the relax protocol that is used. Relax can be slow, so if you're in a hurry, replace this flag with `-remodel:quick_and_dirty`, which bypasses relax. `-remodel:dr_cycles 3` indicates that you want to go through three rounds of sequence Design and Refinement/Relax; you can also change this to 1 if you want to cut down on sampling time. `-soft_rep_design` temporarily reduces the repulsion term of the Rosetta scorefunction during design, which makes less difficult to place larger side chains in buried positions. `-no_optH false`, `-ex1`, and `-ex2` deal with rotamer sampling and typically included in Rosetta sequence design. You can leave out `-ex1` and `-ex2` if you want to cut down on sampling time. `-linmem_ig 10` helps reduce memory usage, but at the cost of increased sampling time, and can also be left out.  

Run a few trajectories, ~1e2, and see how your results look. If you restricted dr_cycles to 1, then you might find some packing defects or other flaws with the design. If you see sidechains that you think work quite well, you can lock them into your blueprint by changing `ALLAAxc` for that residue to `NATAA`, to keep the current residue, or `PIKAA RK`, for example, to restrict design to positively charged residues (Arg and Lys).  

## 3. Remodel one of the loops to insert or remove a helix
After finishing sequence design, you should have a pretty good initial model for a de novo designed protein! There are some more steps you can do for refining the structure and getting it as good as possible, but we won't go into those here. Instead, we'll try to build a new motif into one segment of the protein, an activity that should be of more general interest to protein engineers.  

Here, we'll insert a helix into the third beta-alpha turn (residues 53-55). To start with, we only have the TIM barrel structure (`TIMbarrel_inc_sequence.pdb`). We first need to generate a blueprint based on the starting structure:
```
python makeBlueprint.py TIMbarrel_inc_sequence.pdb
```
You can rename the output ".bp" file to something else if you want. Then let's edit the blueprint to insert a 6-residue helix, flanked by loops, into the third beta-alpha turn:
```
...
51 V .
52 D E NATAA
53 A L ALLAAxc
0 x H ALLAAxc
0 x H ALLAAxc
0 x H ALLAAxc
0 x H ALLAAxc
0 x H ALLAAxc
0 x H ALLAAxc
0 x L ALLAAxc
54 T L ALLAAxc
55 D L NATAA
56 V .
57 D .
...
```
Great. Then use these flags:
```
-s TIMbarrel_inc_sequence.pdb
-blueprint [your blueprint].bp
-jd2:no_output
-overwrite
-num_trajectory 10
-save_top 10 
-remodel:quick_and_dirty
```
Here, we used `quick_and_dirty` to skip the relax step, which can be very slow, since we want to quickly see if we can get good results. When the trajectories are done, take a look at your output structures.
- If they look okay, then you should run it again, but replace `-remodel:quick_and_dirty` with `-remodel:use_pose_relax`, so that your final designs are relaxed and a little more refined.
- If not, it could be one of two problems: your topology is wrong, or you're not sampling enough. You can try fixing both of these by trying different loop and helix lengths, and by running more trajectories.  

Here, we opted to do backbone design and sequence design in a single trajectory. If you'd like to make sure you have your backbone correct, then do sequence design, that's also a good approach sometimes. You could probably take both these approaches and see which one gives you better results. To do this, then add the `-remodel:design:no_design` flag to the initial run, and remove the `ALLAAxc` from the blueprint. Then, once you have a backbone you like, make a new blueprint for that structure, and add `ALLAAxc` to the positions you want to design sequence for. Run Remodel with the same flags, but remove `-remodel:design:no_design`. TODO split this into another section?  

Finally, let's say your starting structure included the helix, but you wanted to remove it. Then you could run the job with the same flags (you could also add in `-remodel:design:no_design`), but using this blueprint. Notice we just deleted residues 54-60. Remodel will delete those residues from your structure and rejoin the two end residues, but make sure you give it some flexibility to work with around the deletion by setting the neighboring residues to 'L' or 'E' or 'H'.
```
...
51 V .
52 D E
53 A L
61 T L
62 D L
63 V H
64 D .
...
```

## 4. Build a disulfide bridge in the core of the protein
TODO






## *Appendix. Iterative enrichment de novo sequence design
Here, we will outline the process for more manually-guided sequence design known as "iterative enrichment." This method allows us to overcome some of the randomness in the Monte Carlo design process by gradually "enriching" residues that are frequently picked at a position, in a lot of trajectories.  

First, this time you'll generate your own blueprint using the provided python script.
```
python makeBlueprint.py TIMbarrel_centroid_backbone.pdb
```
Next, in the blueprint, classify each residue as a core, boundary, or surface residue. Core residues are those which participate in hydrophobic packing. Surface residues are solvent-exposed. Boundary residues are the hardest to define and are basically those residues which are not obviously core or surface. In the blueprint, design core residues to APOLAR, surface residues to PIKAA A (postponing surface design until later), and boundary residues to ALLAAxc. For example, for the TIM barrel, the beginning of your blueprint might look like this:
```
1 A L PIKAA A
2 V L ALLAAxc
3 V L APOLAR
4 V L APOLAR
5 V L APOLAR
6 V L APOLAR
7 V L ALLAAxc
8 V L PIKAA A
...
```
You might have noticed that residues 2-6 were previously set as `E` but here are `L`. Here we want to relax the whole protein with `-use_pose_relax`, which only relaxes residues with a secondary structure assignment (SSA). To do this we need to give every residue a SSA by changing the third column from `.` to any of the assignment letters - `H`, `E`, `L`, or `D`. **It doesn't matter which one, since `-bypass_fragments` is turned on, so these assignments are not being used to determine fragment sampling - they only determine which residues are relaxed.** Here we've arbitrarily chosen `L`. You can read more about this in [Remodel Overview](https://github.com/ProteinDesignLab/protein-design-tutorials/blob/master/remodel/remodel_overview.md) under the Refinement section.  

You should use these flags:
```
-s [your structure].pdb
-remodel:blueprint [your blueprint].bp
-jd2:no_output
-overwrite
-repeat_structure 4
-remodel:RemodelLoopMover:cyclic_peptide
-hb_lrbb 2.0 
-randomize_loops false
-bypass_fragments
-bypass_closure
-remodel:use_pose_relax
-remodel:dr_cycles 3
-soft_rep_design
-no_optH false
-ex1
-ex2
-linmem_ig 10
-num_trajectory 1
-save_top 1
```
`-remodel:use_pose_relax` defines the relax protocol that is used. Relax can be slow, so if you're in a hurry, replace this flag with `-remodel:quick_and_dirty`, which bypasses relax which can be slow. `-remodel:dr_cycles 3` indicates that you want to go through three rounds of sequence Design and Refinement/Relax; you can also change this to 1 if you want to cut down on sampling time. `-soft_rep_design` temporarily reduces the repulsion term of the Rosetta scorefunction during design, which makes less difficult to place larger side chains in buried positions. `-no_optH false`, `-ex1`, and `-ex2` deal with rotamer sampling and typically included in Rosetta sequence design. You can leave out `-ex1` and `-ex2` if you want to cut down on sampling time. `-linmem_ig 10` helps reduce memory usage, but at the cost of increased sampling time, and can also be left out.  

Run a large number of trajectories, ~1e3, and generate a sequence logo from your output (imagine all your outputs as a multiple sequence alignment). There are a few ways to do this, but one is to gather your output structures into a directory, copy `get_sequence_from_pdb.py` from the `essentials_kit` repository, run it in the directory, and then use the output `sequence_list.txt` on a web server, e.g. [https://weblogo.berkeley.edu/logo.cgi](https://weblogo.berkeley.edu/logo.cgi), to generate it for you. Looking at this sequence logo will help you see which residues are selected more frequently at different positions, and perhaps more helpfully, not selected at all. This allows you to go back and "iteratively enrich" your sequences for the "right" residues. For example, if you generated this logo plot from using the blueprint above:  

![example sequence logo](/images/example_sequence_logo.png)  

you might go back and edit your blueprint like so:
```
1 A L PIKAA A
2 V L PIKAA IWV
3 V L PIKAA ILW
4 V L PIKAA IV
5 V L PIKAA IL
6 V L PIKAA LIV
7 V L PIKAA LWIV
8 V L PIKAA A
...
```
Run another thousand trajectories with this, and repeat the process, so that you begin to converge on a good sequence for packing the hydrophobic core.  

Once the core is designed, we can design the rest of the protein. Follow the same process to design the surface residues, which you set to PIKAA A in the previous step. Then manually go through your structure to look for weird behavior, especially in the boundary residues, and redesign them to fix them.  
