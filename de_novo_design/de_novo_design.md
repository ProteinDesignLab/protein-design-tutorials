# De novo design with RosettaRemodel
Created Dec 2018 by Alex Chu. Last updated 181228 AEC  

This is a step by step tutorial to de novo protein design in RosettaRemodel. There are other methods for de novo design, such as parametric geometry sampling as in [this paper](), but this tutorial is an introduction to de novo design with Rosetta fragment sampling. This tutorial assumes some basic knowledge of how RosettaRemodel works, i.e. some of what is discussed in `remodel_overview.md`. If some of the terms or concepts in here aren't familiar to you yet, you should begin there.

### 1. Backbone design
De novo design in this framework begins by specifying a protein backbone, i.e. folded secondary structures, onto which sequences can be designed. To start, you'll need a stub PDB of alanine or some other residue:
```
ATOM      1  N   ALA     1      -0.575  -9.347   5.191  1.00  0.00           N  
ATOM      2  CA  ALA     1       0.101  -8.053   5.191  1.00  0.00           C  
ATOM      3  C   ALA     1       1.601  -8.227   5.191  1.00  0.00           C  
ATOM      4  O   ALA     1       2.132  -9.344   5.180  1.00  0.00           O  
ATOM      5  CB  ALA     1      -0.407  -7.261   6.408  1.00  0.00           C  
ATOM      6  H   ALA     1      -0.029 -10.279   5.191  1.00  0.00           H  
ATOM      7  HA  ALA     1      -0.167  -7.514   4.263  1.00  0.00           H  
ATOM      8 1HB  ALA     1      -1.503  -7.111   6.372  1.00  0.00           H  
ATOM      9 2HB  ALA     1      -0.183  -7.775   7.363  1.00  0.00           H  
ATOM     10 3HB  ALA     1       0.049  -6.256   6.465  1.00  0.00           H  
END
```
and a blueprint specifying the fold you want. In this tutorial, let's build the fourfold repeat TIM barrel from [Huang et al.](https://www.nature.com/articles/nchembio.1966). Then our blueprint would look like this:
```
1 A L
0 x E
0 x E
0 x E
0 x E
0 x E
0 x L
0 x L
0 x L
0 x H
0 x H
0 x H
0 x H
0 x H
0 x H
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
0 x L
0 x L
0 x L
0 x H
0 x H
0 x H
0 x H
0 x H
0 x H
0 x H
0 x H
0 x H
0 x H
0 x H
0 x L
0 x L
```
Let's save these files as `ala.pdb` and `de_novo.bp`. Now, let's specify some of the arguments we want Remodel to take, and save these in a file called `flags`:
```
-s ala.pdb
-remodel:blueprint de_novo.bp
-jd2:no_output
-overwrite
-remodel:design:no_design
-remodel:quick_and_dirty
-use_clusters false
-rg 2.0
-hb_lrbb 2.0
-hb_srbb 0.0
-vdw 1.0
-cenpack 1.0
-cbeta 1.0
-num_trajectory 10
-save_top 5
```
`-overwrite` means that any old files with the same names as the output files will be overwritten.  
`-remodel:design:no_design` and `-remodel:quick_and_dirty` let us skip the design and refinement stages, respectively.  
`-rg 2.0`, `-hb_lrbb 2.0`, and the four other listed flags with float arguments are derived from the supplementary material of the Huang et al. paper; they tune term weights for the Rosetta scorefunction.  
`-num_trajectory 10` means that we want to run 10 Monte Carlo trajectories, and `-save_top 5` means to save and output only the top 5 scoring results by Rosetta energy.  

With these starting arguments, and all of the above files in the same directory, we can begin a sampling run:  
`/path/to/remodel.linuxgccrelease @flags`  
Replace `/path/to` with the path to the directory where your Rosetta executables are. If you add the path to your Rosetta executables to your bash profile, you can simply run  
`remodel.linuxgccrelease @flags`  

When the run is finished, you should have five new files in your directory, named `1.pdb`, `2.pdb`, and so on. These are your results! Open them in PyMOL and see which ones fit your target fold the best. With our current run, you should look for structures that form a quarter-TIM-barrel: a beta-alpha-beta-alpha structure. If you add the line `-repeat_structure 4` to the flags file, it will try to build a full fourfold repeat TIM barrel.  

- Note: Since these are Monte Carlo solutions, you aren't guaranteed that any of these solutions are correct - if so, keep sampling until you get some that are. In this example flags file, we are running 10 trajectories, which is probably not enough - you should probably run and save about ten times that in practice. The number of trajectories you need to run will scale with the difficulty of your problem. For most sampling problems in this tutorial, we might need somewhere on the order of 1e1 to 1e3 trajectories. Proteins that are larger or harder to design might involve adding one or two orders of magnitude to that. You can change the number of trajectories sampled with `-num_trajectory [int]`, or since this problem is easily parallelized, run the same command several times on several processors.  

This stage can be the hardest part of de novo design. Often getting your trajectories to converge to a structure that both fits what you have envisioned and satisfies physical and chemical principles for stably folding protein structures can be very difficult. See this [thread on RosettaCommons](https://www.rosettacommons.org/node/10002) for some more discussion about why actually de novo designing a protein can be much more complicated than simply following this protocol.  

### 2. Sequence design

### 3. Final validation
