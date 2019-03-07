# protein-design-tutorials
This is a collection for all of the tutorials/resources for learning to use Rosetta and the other computational methods we use in our work. Please feel free to edit and update if you see old or incorrect info, even if you are new to the lab (sometimes new people bring the best insights on what is needed!) Note: Most of the documents in this repository are written in Markdown - [here is a quick guide](https://guides.github.com/features/mastering-markdown/) if you are new to it.

## Contents
[intro_to_sherlock.md](https://github.com/ProteinDesignLab/protein-design-tutorials/blob/master/intro_to_sherlock.md) - A quick-start guide for lab members new to or just getting started on Sherlock.

### Remodel
We've assembled some cheat sheets, references, and tutorials for learning to use RosettaRemodel as a command line executable here in this repo. They're not meant to replace the documentation kept at RosettaCommons, which is already very well developed, some of which we have linked to below. The goal here is to just help you get started in the lab ASAP.  

**In this repository**  
[remodel_overview.md](https://github.com/ProteinDesignLab/protein-design-tutorials/blob/master/remodel/remodel_overview.md) - An introduction to RosettaRemodel, how it works, and some basic knowledge that will be useful in learning to use it. **Start here if you are new to to Remodel!**  
[remodel_flags.md](https://github.com/ProteinDesignLab/protein-design-tutorials/blob/master/remodel/remodel_flags.md) - A newbie-friendly list of the most commonly used flags in RosettaRemodel.   
[remodel_bugs.md](https://github.com/ProteinDesignLab/protein-design-tutorials/blob/master/remodel/remodel_bugs.md) - A kind of Stack Overflow for RosettaRemodel. Adding bugs and fixes to this list will hopefully save everyone time in the long run!   
[de_novo_design/](https://github.com/ProteinDesignLab/protein-design-tutorials/tree/master/remodel/de_novo_design) - A step-by-step tutorial for de novo protein design using Rosetta fragment sampling.   

**External Resources**  
[RosettaRemodel Docs](https://www.rosettacommons.org/docs/latest/application_documentation/design/rosettaremodel)  
[Old Remodel Docs & Tutorial](https://www.rosettacommons.org/manuals/archive/rosetta3.4_user_guide/d1/d8c/remodel.html)  
[Rosetta 3 Forums](https://www.rosettacommons.org/forums/rosetta-3)  
[Remodel Flags & Options](https://www.rosettacommons.org/docs/latest/full-options-list)  
[General Remodel Tutorial](https://www.rosettacommons.org/docs/latest/application_documentation/design/Remodel)  
[Stanford Rosetta Workshop](http://2016.rosetta.ninja/day-3/rosettaremodel-basic-tutorial)  
[Loop Modeling Tutorial](https://www.rosettacommons.org/demos/latest/tutorials/loop_modeling/loop_modeling)  
[Disulfide Design Tutorial](https://www.rosettacommons.org/docs/latest/application_documentation/design/rosettaremodel#algorithm_disulfide-design)  

### Pyrosetta 
The Pyrosetta tutorial illustrates methods to manipulate pdb files, quickly extract and parse energy information, and contains a full representative example of docking two proteins in Pyrosetta. 

Key concepts include:
1. the Pose object (a pose contains various methods to extract protein info. including ".pdb_info()")
2. Movers (anything that manipulate a pose, you can identify movers by the ".apply()" method)
3. Movemaps (create MoveMap() objects to specify conditions for minimization)
4. TaskFactory (create TaskFactory() objects to specify conditions for packing)
5. FastRelax (use your specified minimization and packing constraints to run repeated iterations with FastDesign())
6. ResidueSelector (select particular residues to specify for packing or other applications with Movers in the residue_selector class)

as well as much more!

To download Pyrosetta make sure to use a conda environment to create an isolated virtual environment (i.e. install Anaconda3 https://www.anaconda.com/download/). Then go into terminal:
1. 'conda install anaconda-client'
2. 'anaconda login'
3. sign into account ( i.e. for Baker lab: Username: bakerlab, Password: BakerG00d)
3. 'conda env create -f pyrosetta-packages.yml'
4. In the ~/.bashrc and ~/.profile files, comment out any lines with `export PYTHONPATH=...`
5. `source ~/.bashrc` or `source ~/.profile'
6. `conda activate pyrosetta-packages`

note: you can find pyrosetta-packages.yml in the PyRosetta folder

