# De novo design with Remodel
Created Dec 2018 by Alex Chu. Last updated 181228 AEC  

This is a step by step tutorial to de novo protein design using Rosetta fragment sampling in RosettaRemodel. This tutorial assumes some basic knowledge of how RosettaRemodel works, i.e. some of what is discussed in `remodel_overview.md`. If some of the terms or concepts in here aren't familiar to you yet, you should begin there.

### Backbone design
De novo design in this framework begins by specifying a protein backbone, i.e. folded secondary structures, onto which sequences can be designed. To start, you'll need a stub PDB of alanine or some other residue:
```
Alanine
```
and a blueprint specifying the fold you want. In this tutorial, let's build a simple 2x2 Rossmann fold. Then our blueprint would look like this:
```
1 A L
0 x H
0 x H
0 x H
0 x H
0 x H
0 x H
0 x H
0 x L
0 x L
0 x L
0 x E
0 x E
0 x E
0 x E
0 x E
```
Let's save these files as `ala.pdb` and `de_novo.bp`. Now, let's specify some of the arguments we want Remodel to take, and save these in a file called `flags`:
```
-s ala.pdb
-remodel:blueprint de_novo.bp
-jd2:no_output
-overwrite
-remodel:design:no_design
-remodel:quick_and_dirty
-num_trajectory 10
-save_top 5
```
`-overwrite` means that any old files with the same names as the output files will be overwritten. `-remodel:design:no_design` and `-remodel:quick_and_dirty` let us skip the design and refinement stages, respectively. `-num_trajectory 10` means that we want to run 10 Monte Carlo trajectories, and `-save_top 5` means to save and output only the top 5 scoring results by Rosetta energy. Here, we are running 10 trajectories, which is probably not enough . The number of trajectories you need to run will scale with the difficulty of your problem. For most sampling problems in this tutorial, we might somewhere on the order of 1e1 to 1e3 trajectories. Proteins that are larger or harder to design might involve adding one or two orders of magnitude to that. You can change the number of trajectories sampled with `-num_trajectory [int]`, or since this problem is easily parallelized, run the same command on several processors.

With these starting arguments, and all of the above files in the same directory, we can begin a sampling run:  
`/path/to/remodel.linuxgccrelease @flags`  
If you add the path to your Rosetta executables to your `.bash_profile`, you can simply run  
`remodel.linuxgccrelease @flags`  



### Sequence design

### Final validation
