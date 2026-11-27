# hemoflow-openlb

The fork is based on the [hemoflow](https://github.com/gzavo/hemoflow) project - a Lattice-Boltzmann Method (LBM) framework for blood flow simulations based on [Palabos](https://gitlab.com/unigespc/palabos). The main goal of this repository is to port existing Palabos implementation to [OpenLB](https://gitlab.com/openlb) and extend it with support for GPU-based execution.

Initial starting point for refactoring has been tagged as [start-point-for-openlb-port-2026-11](https://github.com/barrgol/hemoflow-openlb/releases/tag/start-point-for-openlb-port-2026-11) (commit hash *`4d5fdf0bf7070aab0b6e0abde5e41927218a3984`*).

## Project Requirements: OpenLB port

The following section summarizes existing `hemoflow` features at the initial stage of the Palabos-to-OpenLB refactoring (see previous section for commit details). This feature list serves to ensure full compatibility of current Palabos-based implementation with the future OpenLB-based port as well as a helper guideline throughout the development process.

The list utilizes the [MoSCoW method](https://en.wikipedia.org/wiki/MoSCoW_method) for task prioritization:

- **MUST have**'s form a minimal baseline for a functional, but not fully-complete OpenLB port

- **SHOULD have**'s form a framework for a "planned" final outcome of the refactoring, including full compatibility with key features from the previous implementation

- **COULD have**'s describe the "nice-to-have" features that are not part of the current implementation and/or are not strictly necessary for a fully-functional port

### MUST have's

**I/O data:**

- [ ] The user must be able to specify **geometry & inlet/outlet** input file(s) that will define the simulation domain (currently separate `.h5` geometry flag and `.npz` openings data)

- [ ] The program must be able to save result at the **final simulation step** as output snapshot

- [ ] The program must be able to calculate & save data on **local velocity** (X, Y, Z directions) in the output snapshot

**Simulation parameters:**

- [ ] The user must be able to specify **(Inlet) Reynolds number** $\text{Re}$, **(Inlet) Average Velocity** $\text{u}_{\text{avg}}$, **Lattice Relaxation Time** $\tau_{\text{LB}}$, **Kinematic Viscosity** $\eta$ and **Fluid Density** $\rho$ as simulation parameters

- [ ] The user must be able to specify **intended simulation length** $T_{sim}$ (in seconds)

**Inlet/outlet boundaries:**

- [ ] The program must be able to impose **constant-pressure boundary condition** on all geometry outlets

- [ ] The program must be able to **apply the exact same custom boundaries** for the openings (inlets) as the original implementation, including rotating the Poiseuille flow and scaling it by a variable factor

- [ ] The program must be able to read **flow rate data** (currently separate `.txt` files) and use it to **scale the flow rate** on all geometry inlets

**Simulation dynamics:**

- [ ] The program must (be able to) **exclude empty nodes** from active simulation domain

- [ ] The program must (be able to) **impose bounce-back boundaries** on wall nodes

- [ ] The program must support **simulation dynamics** based purely on BGK collision operator (equivalent to Palabos' `BGKDynamics`)

- [ ] The program must be able to **perform warm-up iterations** to allow "regular" flow to develop at the inlet/outlet extensions

**Logging:**

- [ ] The program must log the **basic simulation parameters** before the simulation starts (**grid dimensions** $N_{X}, N_{Y}, N_{Z}$, **lattice step** $\Delta x$, **time step** $\Delta t$, **relaxation frequency** $\omega$, **Average Lattice Velocity** $\text{u}_{\text{avg LB}}$, **(Inlet) Reynolds number** $\text{Re}$, **(Inlet) Average Velocity** $\text{u}_{\text{avg}}$)

- [ ] The program must log **basic, descriptive message** at each major step (e.g. "Initializing lattice...", "Defining wall dynamics...", "Reading the openings..." etc.)

- [ ] The program must log **change in energy** $\Delta E$ and **execution time** $T_{exec}$ at user-specified stat intervals

- [ ] The program must log **at which step** it saves the output snapshot and **how long it took** to save the particular snapshot

**CPU/GPU-execution support:**

- [ ] The program must support **single-threaded CPU** execution

- [ ] The program must support **single-GPU parallel** execution

### SHOULD have's

**I/O data:**

- [ ] The program should be able to include in the output snapshot **all currently-supported quantities** (**shear stress** $\sigma$, **velocity** $u$, **density** $\rho$) as well as **metadata** (MPI rank, grid spacing)

**Simulation parameters:**

- [ ] The user should be able to provide **saving frequency** $f_{save}$ (in seconds) as an intended simulation time between each output snapshot

- [ ] The user should be able to specify all modifiable simulation parameters using a **separate config file** (e.g. `.xml`) to avoid direct modifications to the code logic

**Simulation dynamics:**

- [ ] The program should support **simulation dynamics** based on LES turbulence model (equivalent to Palabos' `SmagorinskyRegularizedDynamics`) including custom **Smagorinsky parameter** $C_{S}$

**Divergence checking:**

- [ ] The program should **automatically check for divergence** and terminate the simulation in case of detecting it

- [ ] The program should log **if the simulation diverged** and the **simulation step** at which the divergence occured

**Checkpointing:**

- [ ] The program should be able to **save simulation checkpoints** (not to be confused with full output snapshots) at a user-specified frequency $f_{cp}$ to avoid needing to restart the entire run in case of a crash

- [ ] The program should be able to **(re)start simulation from a checkpointed state** if the user chooses to do so

**Logging:**

- [ ] The user should be able to specify a **log file** as the target location for all output logs, instead of the terminal

**CPU/GPU-execution support:**

- [ ] The program should support **multi-threaded CPU** execution

- [ ] The program should support **multiple-GPU parallel** execution

### COULD have's

**I/O data:**

- [ ] The program could write **output data** using a dedicated OpenLB/external `HDF` writer, rather than a custom `XDMF` parser code

- [ ] The program could allow **geometry voxelization** from within the main OpenLB pipeline itself (the preprocessor would be partially or fully merged with `.cpp` code)

**Inlet/Outlet boundaries:**

- [ ] The program could allow specifiying **different types of inlet/outlet BCs** through the config file

**Simulation dynamics:**

- [ ] The program could support logic for geometries with implanted **medical stent (flow diverter)**

- [ ] The program could support logic for **porous vessel walls**, including input porosity data

## How to use it?

### Setting up the project

**[WIP]**: This section is a work-in-progress and will be expanded in the future. At the time of writing, none of the actual simulation logic is implemented yet.

`hemoflow-openlb` uses [OpenLB 1.9.0](https://gitlab.com/openlb/release/-/tree/1.9.0) as a git submodule. Cloning projects that use git submodules by default results in an empty submodule folder, without any of the actual files.

To clone the repository **and** fetch the submodule contents run:

```
git clone --recurse-submodules https://github.com/barrgol/hemoflow-openlb.git
```

or equivalent, split into two commands:

```
git clone https://github.com/barrgol/hemoflow-openlb.git
git submodule update --init
```

The OpenLB submodule should contain version 1.9.0 independently of what's the current most-recent OpenLB release. Run:

```
git submodule status
```

and verify that the output is equal to:

```
145cd54810b468f4b6fd3ed86b10644264841578 openlb (1.9.0)
```

which is the commit hash of OpenLB release 1.9.0.

### Dependencies

- (*) **NVIDIA CUDA 12**: release 12.4.x or newer, but no later than 12.9.x

(*) OpenLB developers claim that version 1.9.0 supports CUDA 12.4+, but our local test runs with CUDA 13.3 failed, seemingly due to a change in CUDA's header structure introduced with CUDA 13. Local test runs were confirmed to work with CUDA 12.9.

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
