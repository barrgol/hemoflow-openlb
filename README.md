# hemoflow-openlb

The fork is based on the [hemoflow](https://github.com/gzavo/hemoflow) project - a Lattice-Boltzmann Method (LBM) framework for blood flow simulations based on [Palabos](https://gitlab.com/unigespc/palabos). The main goal of this repository is to port existing Palabos implementation to [OpenLB](https://gitlab.com/openlb) and extend it with support for GPU-based execution.

Initial starting point for refactoring has been tagged as [start-point-for-openlb-port-2026-11](https://github.com/barrgol/hemoflow-openlb/releases/tag/start-point-for-openlb-port-2026-11) (commit hash *`4d5fdf0bf7070aab0b6e0abde5e41927218a3984`*).

## Known issues (before porting to OpenLB)

**Preprocessor**:

- [ ] There is no "easy" way for switching between the two methods for detecting inlets/outlets. Switching relies on commenting/uncommenting certain code sections.

- [ ] Both methods for openings detection require specific geometry setup (either all openings located on boundary surfaces or all openings parallel to the normal planes).

- [ ] Labelling the openings relies on hardcoded `paint_dic` variable in `detectOpenings.py`, requiring explicit visual validation of the voxelization results.

**Simulation code:**

- [ ] Simulation output is based on the inefficient and not actively supported `XDMF` format (see [VTK HDF Reader](https://www.kitware.com/vtk-hdf-reader/) article at Kitware's website)

- [ ] Correctness of inlet/outlet labels relies on hardcoded constants in `globals.h` which are not cross-validated with voxelization output. This means that, if the opening IDs assigned at the pre-processing step don't match the expectations, a change might be required in both the preprocessor and `globals.h`.

- [ ] Switching between Direct Numerical Simulation (DNS) and LES-based simulation requires commenting/uncommenting multiple code sections in `hemoFlow.cpp`.

- [ ] (*Unverified*) Parallel-CPU code is potentially (very) inefficient. Notes from the previous developer suggest that all voxels are read to each MPI thread, leading to massive memory overhead.

- [ ] (*Unverified*) Max. geometry velocity calculated at snapshots doesn't match the values expected at the inlets, possibly indicating faulty logic around the flow rate scale functions.
