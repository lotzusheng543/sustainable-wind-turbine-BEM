import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Folder containing COORDS00 to COORDS49
COORD_DIR = Path(r"C:\Users\Ming\Desktop\Airfoil-Coords-CLD\COORDS")

TARGET_AIRFOILS = [42, 0, 11, 23, 32, 49]


def read_coord_file(file_path):
    """Read COORDS file safely and skip non-numeric lines."""
    coords = []

    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            parts = line.replace(",", " ").split()

            try:
                x_val = float(parts[0])
                y_val = float(parts[1])
                coords.append([x_val, y_val])
            except:
                continue

    data = np.array(coords)

    if data.shape[0] == 0:
        raise ValueError(f"No numeric coordinate data found in {file_path}")

    return data


def find_coord_file(airfoil_id):
    possible_files = [
        COORD_DIR / f"COORDS{airfoil_id:02d}",
        COORD_DIR / f"COORDS{airfoil_id:02d}.txt",
        COORD_DIR / f"COORD{airfoil_id:02d}",
        COORD_DIR / f"COORD{airfoil_id:02d}.txt",
    ]

    for p in possible_files:
        if p.exists():
            return p

    raise FileNotFoundError(f"Could not find coordinate file for COORD{airfoil_id:02d}")


# 1) Four separate subplots
fig, axes = plt.subplots(1, 4, figsize=(14, 3.5))

for ax, airfoil_id in zip(axes, TARGET_AIRFOILS):
    file_path = find_coord_file(airfoil_id)
    data = read_coord_file(file_path)

    x = data[:, 0]
    y = data[:, 1]

    ax.plot(x, y, linewidth=2)
    ax.set_title(f"COORD{airfoil_id:02d}")
    ax.axis("equal")
    ax.grid(True, alpha=0.3)
    ax.set_xlabel("x/c")
    ax.set_ylabel("y/c")

plt.suptitle("Selected Aerofoil Shapes: COORD09, COORD12, COORD32 and COORD42")
plt.tight_layout()

output_path_1 = Path(r"C:\Users\Ming\Desktop\selected_airfoil_shapes_09_12_32_42.png")
plt.savefig(output_path_1, dpi=300, bbox_inches="tight")

print(f"Figure saved to: {output_path_1}")
plt.show()


# 2) Overlay comparison
plt.figure(figsize=(8, 4.5))

for airfoil_id in TARGET_AIRFOILS:
    file_path = find_coord_file(airfoil_id)
    data = read_coord_file(file_path)

    x = data[:, 0]
    y = data[:, 1]

    plt.plot(x, y, linewidth=2, label=f"COORD{airfoil_id:02d}")

plt.xlabel("x/c")
plt.ylabel("y/c")
plt.title("Overlay Comparison of Selected Aerofoil Shapes")
plt.axis("equal")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

output_path_2 = Path(r"C:\Users\Ming\Desktop\selected_airfoil_shapes_overlay_09_12_32_42.png")
plt.savefig(output_path_2, dpi=300, bbox_inches="tight")

print(f"Figure saved to: {output_path_2}")
plt.show()