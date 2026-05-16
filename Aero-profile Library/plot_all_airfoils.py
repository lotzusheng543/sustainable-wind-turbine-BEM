import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# =========================
# 1. Settings
# =========================

selected_airfoils = [f"COORDS{i:02d}" for i in range(00, 50)]

# Search from current project folder
base_folder = Path.cwd()

output_name = "selected_final_aerofoil_shapes.png"


# =========================
# 2. Find and load files
# =========================

def find_coord_file(base_folder, airfoil_name):
    """
    Recursively search all subfolders for a coordinate file.
    Accepts files such as:
    COORD42.txt, coord42.dat, COORD42, coord42_coords.csv, etc.
    """
    airfoil_upper = airfoil_name.upper()

    candidates = []

    for file in base_folder.rglob("*"):
        if file.is_file():
            stem_upper = file.stem.upper()
            name_upper = file.name.upper()

            # Match exact stem or filename containing COORDxx
            if stem_upper == airfoil_upper or airfoil_upper in name_upper:
                candidates.append(file)

    if not candidates:
        raise FileNotFoundError(f"Could not find coordinate file for {airfoil_name} under {base_folder}")

    # Prefer coordinate-looking files, not CLD files
    preferred = []
    for file in candidates:
        name = file.name.upper()
        if "CLD" not in name and "POLAR" not in name:
            preferred.append(file)

    if preferred:
        return preferred[0]
    else:
        return candidates[0]


def load_airfoil_coordinates(file_path):
    """
    Load x-y coordinates from file.
    Handles files with text headers.
    """
    try:
        data = np.loadtxt(file_path)
    except Exception:
        data = np.genfromtxt(file_path, skip_header=1)

    data = np.asarray(data)

    # Remove invalid rows
    if data.ndim == 1:
        raise ValueError(f"File {file_path} was not loaded as a two-column coordinate file.")

    data = data[~np.isnan(data).any(axis=1)]

    if data.shape[1] < 2:
        raise ValueError(f"File {file_path} does not contain at least two columns.")

    x = data[:, 0]
    y = data[:, 1]

    return x, y

# =========================
# 3. Plot selected aerofoils
# =========================

n_airfoils = len(selected_airfoils)
n_cols = 5
n_rows = int(np.ceil(n_airfoils / n_cols))

fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, 3 * n_rows))
axes = axes.flatten()

found_files = {}

for ax, airfoil_name in zip(axes, selected_airfoils):
    file_path = find_coord_file(base_folder, airfoil_name)
    found_files[airfoil_name] = file_path

    x, y = load_airfoil_coordinates(file_path)

    ax.plot(x, y, linewidth=2)
    ax.set_title(airfoil_name, fontsize=10)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")

# Hide unused subplot boxes
for ax in axes[len(selected_airfoils):]:
    ax.axis("off")

fig.suptitle(
    "All Aerofoil Sections in the Database",
    fontsize=18,
    fontweight="bold"
)

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig("all_aerofoil_shapes.png", dpi=300, bbox_inches="tight")
plt.show()

print(f"Saved figure as: all_aerofoil_shapes.png")
print("\nFiles used:")
for name, path in found_files.items():
    print(f"{name}: {path}")
