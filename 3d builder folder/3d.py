import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# ============================================================
# Folder setup
# ============================================================
BASE_DIR = Path(__file__).resolve().parent
COORDS_DIR = BASE_DIR / "COORDS"
OUT_PNG = BASE_DIR / "blade_surface_from_table.png"

# ============================================================
# Blade data from your table
# ============================================================
# Element, r [m], airfoil, chord [m], twist [deg]
blade_data = [
    (1,  26.90, "COORD42", 5.80, 0.00),
    (2,  31.90, "COORD00", 9.50, 16.75),
    (3,  37.10, "COORD03", 9.22, 13.81),
    (4,  42.31, "COORD08", 8.91, 11.13),
    (5,  47.51, "COORD48", 8.60, 8.72),
    (6,  52.72, "COORD02", 8.27, 6.83),
    (7,  57.93, "COORD29", 7.94, 5.58),
    (8,  63.13, "COORD39", 7.62, 4.73),
    (9,  68.34, "COORD45", 7.28, 3.98),
    (10, 73.54, "COORD49", 6.94, 3.23),
    (11, 78.75, "COORD01", 6.58, 2.72),
    (12, 83.96, "COORD09", 6.23, 2.22),
    (13, 89.16, "COORD05", 5.86, 1.67),
    (14, 94.37, "COORD25", 5.48, 1.12),
    (15, 99.58, "COORD30", 5.10, 0.64),
    (16, 104.78, "COORD06", 4.68, 0.30),
    (17, 109.99, "COORD11", 4.14, 0.14),
    (18, 115.19, "COORD32", 3.31, 0.06),
    (19, 120.40, "COORD23", 1.57, 0.02),
]

N_POINTS = 220


# ============================================================
# Helper functions
# ============================================================
def load_airfoil_coords(name):
    """
    Load airfoil coordinates.
    Supports COORDxx / COORDSxx file names.
    """
    name = str(name).strip().upper()
    num = int(name.replace("COORDS", "").replace("COORD", ""))

    candidates = [
        COORDS_DIR / f"COORD{num:02d}",
        COORDS_DIR / f"COORD{num:02d}.txt",
        COORDS_DIR / f"COORDS{num:02d}",
        COORDS_DIR / f"COORDS{num:02d}.txt",
    ]

    file_path = None
    for p in candidates:
        if p.exists():
            file_path = p
            break

    if file_path is None:
        print("Tried:")
        for p in candidates:
            print(" -", p)
        raise FileNotFoundError(f"Cannot find coordinate file for {name}")

    pts = []
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = line.replace(",", " ").split()
            nums = []

            for item in parts:
                try:
                    nums.append(float(item))
                except:
                    pass

            if len(nums) >= 2:
                pts.append([nums[0], nums[1]])

    pts = np.array(pts, dtype=float)

    if len(pts) < 5:
        raise ValueError(f"Not enough valid coordinate points in {file_path}")

    # Remove consecutive duplicate points
    keep = [True]
    for i in range(1, len(pts)):
        keep.append(np.linalg.norm(pts[i] - pts[i - 1]) > 1e-12)
    pts = pts[np.array(keep)]

    # Close curve
    if np.linalg.norm(pts[0] - pts[-1]) > 1e-8:
        pts = np.vstack([pts, pts[0]])

    return pts


def resample_closed_curve(pts, n=N_POINTS):
    """
    Resample closed airfoil curve by arc length.
    """
    d = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    s = np.concatenate([[0.0], np.cumsum(d)])
    total = s[-1]

    if total <= 0:
        raise ValueError("Invalid airfoil curve length.")

    s_new = np.linspace(0, total, n, endpoint=False)

    x_new = np.interp(s_new, s, pts[:, 0])
    y_new = np.interp(s_new, s, pts[:, 1])

    return np.column_stack([x_new, y_new])


def standardize_airfoil(pts, n=N_POINTS):
    """
    Resample and align all airfoils to reduce loft twisting.
    Start at trailing edge, same direction.
    """
    pts = resample_closed_curve(pts, n=n)

    # Start near trailing edge = maximum x
    te_idx = np.argmax(pts[:, 0])
    pts = np.roll(pts, -te_idx, axis=0)

    # Ensure direction is broadly upper surface first
    check_n = max(5, n // 20)
    if np.mean(pts[1:1 + check_n, 1]) < 0:
        pts = pts[::-1]
        te_idx = np.argmax(pts[:, 0])
        pts = np.roll(pts, -te_idx, axis=0)

    return pts


def transform_section(coords, chord, twist_deg, r):
    """
    Transform 2D airfoil into 3D blade section.

    X = spanwise direction
    Y = chordwise direction
    Z = thickness direction

    Twist is applied about quarter-chord.
    """
    x = coords[:, 0]
    y = coords[:, 1]

    # If x range is not 0-1, normalise it
    x_min, x_max = np.min(x), np.max(x)
    if x_max - x_min > 1e-9:
        x = (x - x_min) / (x_max - x_min)

    # Scale by chord and rotate about quarter chord
    Y0 = (x - 0.25) * chord
    Z0 = y * chord

    theta = np.deg2rad(twist_deg)

    Y = Y0 * np.cos(theta) - Z0 * np.sin(theta)
    Z = Y0 * np.sin(theta) + Z0 * np.cos(theta)
    X = np.full_like(Y, r)

    return X, Y, Z


# ============================================================
# Build sections
# ============================================================
if not COORDS_DIR.exists():
    raise FileNotFoundError(f"COORDS folder not found: {COORDS_DIR}")

sections = []

print("\nBlade sections used:")
print(f"{'Elem':<5} {'r [m]':<8} {'Airfoil':<8} {'Chord [m]':<10} {'Twist [deg]':<10}")

for elem, r, foil, chord, twist in blade_data:
    raw = load_airfoil_coords(foil)
    coords = standardize_airfoil(raw, n=N_POINTS)
    X, Y, Z = transform_section(coords, chord, twist, r)

    sections.append({
        "elem": elem,
        "r": r,
        "foil": foil,
        "chord": chord,
        "twist": twist,
        "X": X,
        "Y": Y,
        "Z": Z,
    })

    print(f"{elem:<5} {r:<8.2f} {foil:<8} {chord:<10.2f} {twist:<10.2f}")


# ============================================================
# Plot CAD-like surface
# ============================================================
fig = plt.figure(figsize=(15, 8))
ax = fig.add_subplot(111, projection="3d")

surface_color = "#aeb7c6"

# Surface between sections
for i in range(len(sections) - 1):
    s1 = sections[i]
    s2 = sections[i + 1]

    Xsurf = np.vstack([s1["X"], s2["X"]])
    Ysurf = np.vstack([s1["Y"], s2["Y"]])
    Zsurf = np.vstack([s1["Z"], s2["Z"]])

    ax.plot_surface(
        Xsurf,
        Ysurf,
        Zsurf,
        color=surface_color,
        edgecolor="none",
        linewidth=0,
        antialiased=True,
        shade=True,
        alpha=0.98,
    )

# Root and tip cap
for sec in [sections[0], sections[-1]]:
    verts = [list(zip(sec["X"], sec["Y"], sec["Z"]))]
    cap = Poly3DCollection(
        verts,
        facecolor=surface_color,
        edgecolor="black",
        linewidth=0.4,
        alpha=0.98,
    )
    ax.add_collection3d(cap)

# Leading and trailing edge guide curves
te_idx = 0
le_idx = N_POINTS // 2

te_curve = np.array([[s["X"][te_idx], s["Y"][te_idx], s["Z"][te_idx]] for s in sections])
le_curve = np.array([[s["X"][le_idx], s["Y"][le_idx], s["Z"][le_idx]] for s in sections])

ax.plot(le_curve[:, 0], le_curve[:, 1], le_curve[:, 2], color="black", linewidth=1.1)
ax.plot(te_curve[:, 0], te_curve[:, 1], te_curve[:, 2], color="dimgray", linewidth=1.0)

# ============================================================
# View settings
# ============================================================
allX = np.concatenate([s["X"] for s in sections])
allY = np.concatenate([s["Y"] for s in sections])
allZ = np.concatenate([s["Z"] for s in sections])

ax.set_xlim(allX.min(), allX.max())
ax.set_ylim(allY.min(), allY.max())
ax.set_zlim(allZ.min(), allZ.max())

xrange = allX.max() - allX.min()
yrange = allY.max() - allY.min()
zrange = allZ.max() - allZ.min()

# Make it visually long and CAD-like
ax.set_box_aspect((xrange, yrange * 1.05, zrange * 1.05))

# Try this view first
ax.view_init(elev=18, azim=-120)

ax.set_title("CAD-like 3D Surface of 16 MW Blade", fontsize=16, pad=18)
ax.set_xlabel("Spanwise direction r [m]", labelpad=10)
ax.set_ylabel("Chordwise direction [m]", labelpad=10)
ax.set_zlabel("Thickness direction [m]", labelpad=10)

ax.grid(True, alpha=0.25)

plt.tight_layout()
plt.savefig(OUT_PNG, dpi=300, bbox_inches="tight")
plt.show()

print(f"\nFigure saved to:\n{OUT_PNG}")