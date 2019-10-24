These are some new-user-friendly, slightly more detailed explanations of some key Remodel flags. If you know how to use a flag that's not here, please add it with a short description of what it is and how to use it. You can see all the possible Rosetta flags and options [here on RosettaCommons](https://www.rosettacommons.org/docs/latest/full-options-list), or in your Rosetta build directory at `/main/source/src/basic/options/options_rosetta.py`.

*-use_blueprint_sequence*. Bias backbone fragment sampling towards fragments that match the sequence defined in blueprint column 2.  
*-symmetry_definition [filename]*. Allow you to pass a sym def file to build symmetric structures.  
in backbone sampling, all ff terms that involve sequence are turned off  
van der Waals, clashing,,  
radius of gyration, packing,  
Ramachandran probability terms are used to specifically address chain geometry (scaled down to 1/10)  
loop closure done with random chain breaks, then CCD or KIC; only models with closed chains are passed on to design  
*-use_clusters*. Remodel stores structures it has generated; this clusters them into unique conformations for localized sampling after large fragment-based moves.  
*-dr_cycles [int]*. number of design and refinement cycles, default 3  
*-bypass_fragments*. skip fragment insertion steps in design/refinement  
*-build_disulf*. Disulfides are built from mobile to stationary regions. Combine with DM_start DM_stop in the blueprint to designate a mobile region from which to construct disulfides. Stationary regions can be defined by either DS_start DS_stop or -disulf_landing_range [int,int].  
*-match_rt_limit*. set a limit to searching realistic disulfide geometries (if too low, may not find any matches)  
*-insert_segment_from_pdb [filename]*. insert pdb fragment (trimmed to only contain insertion residues) into blueprint where designated ‘I’. Be sure to include linker residues to allow connection.  
*-bypass_closure*. turn off chain closure (which is hard for some cases where chain length is unsure) and instead grow chains to closure.  
*-swap_refine_confirm_protocols*. Use KIC instead of CCD for refinement  
*-remodel:design:no_design*. Skip designing sequence onto the backbone. For de novo at least, doesn’t add too much time on.  
*-no_jumps*. sample degrees of freedom for flexible linker between two rigid bodies. What that means: To join two chains in a chainbreak, you can freeze the chains in space (this is called creating a jump) and build the loop with standard loop modeling/closure methods. Or you can allow the chains to move with respect to each other (no_jumps), which allows solutions where the other end moves (this is more like a docking-type procedure). Think of trying to build a bridge vs lasso a cow.  
*-ex1 -ex2*. have to do with rotamer sampling. They slow down refinement a lot.  
*-linmem_ig [int, default 10]*. instantiates the linear memory interaction graph. Is more efficient with memory (prevents crashes) but slows down the trajectory  
*-helical_radius [angstrom] _rise [angstrom] _omega [rad]*. Parameters dictating repeat structures. Radius is the distance between centroids of repeats.  
*-remodel:RemodelLoopMover:cyclic_peptide*.  
*-remodel:cstfilter [int]*. Don’t return structures that have atompair_cst scores higher than this number.  
*-constraints:cst_file [filename]*. Traditional/old method of defining constraints. (not enzdes)  
*-constraints:cst_fa_weight [float]*. Scorefunction weight for atompair csts. >1000 usually leads to unnatural structures.  
*-relax:constrain_relax_to_start_coords*. Constrains relax to starting coordinates (doesn't allow backbone to move). In the past I (Alex) have used this in conjunction with `-score:set_weights coordinate_constraint 4.0`  
*-soft_rep_design*. Lessens repulsion scorefunction terms during design to allow bigger sidechains to be sampled in the core.  
*-core_cutoff [int usu 16 or so]*. The minimum number of neighbors a residue must have to be considered a hydrophobic core residue.  
*-boundary_cutoff [int usu 15 or so]*. The maximum number of neighbors a residue can have to be considered a solvent exposed residue.  
**`-score:set_weights [scorefxn term] [float]`**. Change the weights for the Rosetta energy function for your sampling run. You will need to choose which energy term and the new weight, for example `-score:set_weights hbond_lr_bb 2.0 pro_close 0.0`. See a list of [scorefxn energy terms](https://www.rosettacommons.org/docs/latest/rosetta_basics/scoring/score-types).  

**Relax/refinement related flags**  
The use_pose_relax and use_cart_relax flags are the primary flags in charge of the refinement step. See the Refinement section in [Remodel Overview](https://github.com/ProteinDesignLab/protein-design-tutorials/blob/master/remodel/remodel_overview.md) to get a deeper explanation of how these interact with each other.  
*-remodel:use_pose_relax*. Pose relax varies torsional angles. This is the one most commonly used when we want to do refinement.  
*-remodel:use_cart_relax*. Cartesian relax varies all the Cartesian degrees of freedom - eg bond lengths and angles.  
*-remodel:free_relax*. Constraint-free relax (run pose or cart relax on the whole structure, regardless of secondary structure assignment).  
*-remodel:quick_and_dirty*. Skip iterative design and refinement cycles after centroid building; rebuild backbones without finetuning for sequences using CCD or KIC. This saves a lot of time (more than skipping sequence design)  
