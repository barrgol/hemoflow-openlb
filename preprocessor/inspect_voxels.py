#!/usr/bin/env python3
"""
inspect_voxels.py - sanity-check and visualize voxelization output
(e.g. voxelsops.npz and voxelsgf.h5) with numpy + matplotlib.
--------

What the file does:
--------
  1. loads geometry flag (.h5) and openings data (.npz) calculated by main.py.
  2. prints out basic info about each data field stored in these files,
     for easier inspection by a user who's new to the repository.
  3. reports loaded domain dimensions to the terminal.
  4. reports per-label (empty, fluid, wall) voxel count for the 3D voxelized volume.
  5. opens an interactive 3D overview of the voxelized volume.

Example usage:
--------
  python3 inspect_voxels.py -ops output/voxelsops.npz -gf output/voxelsgf.h5

Requirements: numpy, matplotlib, and h5py for .h5 files.
"""
import argparse
import h5py

import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.family'] = 'sans-serif'

from constants import const
CONSTANTS = const()
ONAMES = {
    CONSTANTS.INLET_IVC: "IVC",
    CONSTANTS.INLET_SVC: "SVC",
    CONSTANTS.INLET_LHV: "LHV",
    CONSTANTS.INLET_MHV: "MHV",
    CONSTANTS.INLET_RHV: "RHV",
    CONSTANTS.OUTLET_LPA: "LPA",
    CONSTANTS.OUTLET_RPA: "RPA",
    CONSTANTS.OUTLET_SIDE_P: "RPA side branch (P)",
    CONSTANTS.OUTLET_SIDE_V: "RPA side branch (V)"
}

# --- Loading input --------------------------------------------------------
def load_h5(path):
    "Loads HDF5 file and returns retrieved arrays as a dictionary."
    arrays = {}
    if path.endswith((".h5", ".hdf5")):
        with h5py.File(path, "r") as f:
            def visit(name, obj):
                if isinstance(obj, h5py.Dataset):
                    arrays[name] = obj[()]

            f.visititems(visit)
    else:
        raise ValueError(f"Unsupported file type: {path}. Supported types: .h5, .hdf5")

    return arrays

def load_npz(path):
    "Loads NumPy data archive file and returns retrieved arrays as a dictionary."
    arrays = {}
    if path.endswith(".npz"):
        with np.load(path, allow_pickle=True) as f:
            for k in f.files:
                arrays[k] = f[k]
    else:
        raise ValueError(f"Unsupported file type: {path}. Supported types: .npz")

    return arrays

def describe_file(path, arrays):
    """Print a summary of the arrays and attributes in a file at path."""
    print(f"\n{'=' * 50}\n{path}\n{'=' * 50}")
    for k, a in arrays.items():
        a = np.asarray(a)
        desc = f"{k}:\n\tshape={a.shape}\n\tdtype={a.dtype}"
        if a.ndim == 0 or a.size == 0:
            desc += f"\n\tvalue={a.tolist()}"
        elif np.issubdtype(a.dtype, np.number):
            desc += f"\n\tmin={a.min()} max={a.max()}"
        print("  " + desc)
    print(f"{'=' * 50}\n")

# --- Parsing data --------------------------------------------------------
def label_report(volume, voxel_names):
    """Counts voxels of each type (empty, wall, fluid) and prints out the results to terminal."""
    print(f"  {'label':<16}{'voxels':>16}{'%total':>16}")
    total = volume.size
    for id, name in voxel_names.items():
        count = np.count_nonzero(volume == id)
        frac = np.round(100*count/total, 2)
        print(f"  {str(id) + " (" + name + ")":<16}{count:>16}{frac:>16}")

def parse_openings(opsData):
    """Parses data from *ops.npz and returns output as dict, sorted by opening's index."""
    openings = []
    centers = np.atleast_2d(opsData["openingCenter"])
    for i, c in enumerate(centers):
        o = {"center": c.astype(float)}
        for key, name in (("openingIndex", "index"), 
                          ("openingRadius", "radius"),
                          ("openingNormalizedQRatio", "q"), 
                          ("openingTangent", "tangent")):
            o[name] = opsData[key][i]
        openings.append(o)

    openings = sorted(openings, key=lambda o : o["index"])
    return openings

# --- Visualization --------------------------------------------------------
def overview_3d(volume, title, openings=(), dx=None):
    """
    Creates a 3D scatterplot of wall and fluid voxels. Empty nodes are not shown.
    Also draws the openings as circles, with an arrow indicating whether it's inlet or outlet.
    """
    fig = plt.figure(figsize=(10, 9))
    ax = fig.add_subplot(projection="3d")
    ax.set_title(title, loc="center")
    
    pts = np.argwhere(volume == 1)
    ax.scatter(*pts.T, s=1.5, alpha=0.05, color='gray', label='Vessel walls', depthshade=False)

    pts = np.argwhere(volume == 2)
    ax.scatter(*pts.T, s=1.5, alpha=0.05, color='darkred', label='Fluid voxels', depthshade=False)
    
    for o in openings:
        """Draw the arrow indicating inlet/outlet."""
        c = o["center"]
        t = np.asarray(o.get("tangent", [0, 0, 1]), float)
        r = o["radius"] / dx
        ax.quiver(*c, *(t * 3 * r), color="black", linewidth=2)

        """Draw the circle of the opening radius in the plane normal to the tangent."""
        t = t / np.linalg.norm(t)
        u = np.cross(t, [1, 0, 0] if abs(t[0]) < 0.9 else [0, 1, 0])
        u /= np.linalg.norm(u)
        w = np.cross(t, u)
        phi = np.linspace(0, 2 * np.pi, 60)
        ring = c[:, None] + r * (np.outer(u, np.cos(phi)) + np.outer(w, np.sin(phi)))
        ax.plot(*ring, color="black", linewidth=2)
        ax.text(*(c + r), f"{ONAMES[o["index"]]}", fontsize=12, weight="bold")

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")

    ax.set_xlim(0, volume.shape[0] - 1)
    ax.set_ylim(0, volume.shape[1] - 1)
    ax.set_zlim(0, volume.shape[2] - 1)

    ax.set_box_aspect(volume.shape)
    leg = ax.legend(loc="upper left", fontsize=14, markerscale=3, bbox_to_anchor=(1.05, 1))
    fig.subplots_adjust(right=0.75)
    for h in leg.legend_handles:
        h.set_alpha(1)

    ax.view_init(elev=30, azim=-120, roll=0)

    """Locks camera roll & elevation, makes the interactive visualization much nicer to work with."""
    def lock_view(event):
        if event.inaxes is ax:
            ax.view_init(elev=30, azim=ax.azim, roll=0)
            fig.canvas.draw_idle()

    fig.canvas.mpl_connect("motion_notify_event", lock_view)

    return fig

# ------------------------------------------------------------------- main
def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("-gf", nargs=1, help="Provide a .h5 file with geometry flag data.")
    p.add_argument("-ops", nargs=1, help="Provide an .npz file with openings data.")
    args = p.parse_args()

    """Load input files (gf = geometry flag (.h5), ops = openings (.npz))"""
    gfData = load_h5(args.gf[0])
    opsData = load_npz(args.ops[0])

    paths = [args.gf[0], args.ops[0]]
    loaded = [gfData, opsData]

    """Prints into terminal basic info on loaded data fields for user's convenience."""
    for path, arrays in zip(paths, loaded):
        describe_file(path, arrays)

    """Parse & print grid dimensions (Nx, Ny, Nz) and lattice step size (dx)"""
    dims = tuple(int(opsData[k].item()) for k in ("Nx", "Ny", "Nz"))
    dx = float(opsData["dx"].ravel()[0])
    print(f"Grid dimensions from metadata: (Nx, Ny, Nz) = {dims}")
    print(f"Lattice step size dx ≈ {np.round(dx*1e3, 4)}mm (milimeters)")
    print(f"Corresponding domain size ≈ " +
          f"{int(dims[0]*dx*1e3)} x " +
          f"{int(dims[1]*dx*1e3)} x " + 
          f"{int(dims[2]*dx*1e3)} mm (milimeters)\n")

    """Parse & print loaded data on openings (inlets/outlets): centers & radii"""
    openings = parse_openings(opsData)

    for o in openings:
        print(f"Opening #{o["index"]} - {ONAMES[o["index"]]}:" +
              f"\n\tcenter = (X={o['center'][0]:.2f}, Y={o['center'][1]:.2f}, Z={o['center'][2]:.2f})" +
              f"\n\tradius = {o['radius'] / dx:.2f} voxels" +
              f"\n\tnormalizedQRatio ≈ {o['q']:.4f}" +
              f"\n\ttangent = {o['tangent']}"
        )

    """Reshape flattened geometry back to original dimensions (Nx, Ny, Nz)."""
    print(f"\nReshaping geometry data loaded from {args.gf[0]}: {gfData["geometryFlag"].shape} ---> {dims}")

    volume = gfData["geometryFlag"].reshape(dims)
    voxel_names = {0: "empty", 1: "wall", 2: "fluid"}

    """Report statistics on each label count (empty, wall, fluid)."""
    print(f"\n--- Label statistics for [{args.gf[0]}] ---")
    label_report(volume, voxel_names)

    """Create the interactive 3D scatter plot."""
    keep = []
    keep.append(overview_3d(volume, "Voxelized geometry", openings, dx))
    plt.show()

if __name__ == "__main__":
    main()