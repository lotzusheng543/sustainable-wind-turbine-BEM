import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Folder containing CLD00 to CLD49
CLD_DIR = Path(r"C:\Users\Ming\Desktop\Airfoil-Coords-CLD\CLD")

TARGET_ALPHA = 4.0  # representative operating angle of attack [deg]

def read_cld_file(file_path):
    """Read CLD file safely and skip non-numeric lines."""
    rows = []

    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            parts = line.replace(",", " ").split()

            try:
                alpha = float(parts[0])
                cl = float(parts[1])
                cd = float(parts[2])
                rows.append([alpha, cl, cd])
            except:
                continue

    data = np.array(rows)

    if data.shape[0] == 0:
        raise ValueError(f"No numeric CLD data found in {file_path}")

    # Sort by alpha for interpolation
    data = data[np.argsort(data[:, 0])]
    return data


airfoil_ids = []
cl_values = []
cd_values = []
clcd_values = []
status_list = []

for i in range(50):
    possible_files = [
        CLD_DIR / f"CLD{i:02d}",
        CLD_DIR / f"CLD{i:02d}.txt",
    ]

    file_path = None
    for p in possible_files:
        if p.exists():
            file_path = p
            break

    if file_path is None:
        raise FileNotFoundError(f"Could not find CLD file for CLD{i:02d}")

    data = read_cld_file(file_path)

    alpha = data[:, 0]
    cl = data[:, 1]
    cd = data[:, 2]

    # Interpolate CL and CD at target alpha
    cl_target = np.interp(TARGET_ALPHA, alpha, cl)
    cd_target = np.interp(TARGET_ALPHA, alpha, cd)

    if abs(cd_target) < 1e-8:
        clcd_target = np.nan
    else:
        clcd_target = cl_target / cd_target

    # Simple screening status
    if cd_target > 0.05 or clcd_target < 30:
        status = "Poor"
    elif cd_target > 0.02 or clcd_target < 60:
        status = "Weak"
    else:
        status = "Good"

    airfoil_ids.append(i)
    cl_values.append(cl_target)
    cd_values.append(cd_target)
    clcd_values.append(clcd_target)
    status_list.append(status)


# Print summary table
print(f"CL/CD comparison at alpha = {TARGET_ALPHA:.1f} deg")
print("=" * 70)
print(f"{'Airfoil':<10} {'CL':>8} {'CD':>10} {'CL/CD':>10} {'Status':>10}")
print("-" * 70)

for i, cl_t, cd_t, clcd_t, status in zip(
    airfoil_ids, cl_values, cd_values, clcd_values, status_list
):
    print(f"COORD{i:02d}   {cl_t:8.3f} {cd_t:10.4f} {clcd_t:10.1f} {status:>10}")


# Bar chart: CL/CD at alpha = 4 deg
plt.figure(figsize=(15, 6))

bars = plt.bar(airfoil_ids, clcd_values)

# Highlight poor / weak airfoils
for bar, status in zip(bars, status_list):
    if status == "Poor":
        bar.set_alpha(0.35)
    elif status == "Weak":
        bar.set_alpha(0.60)
    else:
        bar.set_alpha(0.95)

plt.xlabel("Aerofoil index")
plt.ylabel("CL/CD at α = 4°")
plt.title("Lift-to-Drag Ratio Comparison at α = 4°")
plt.grid(axis="y", alpha=0.3)
plt.xticks(range(0, 50, 2), [f"{i:02d}" for i in range(0, 50, 2)])

# Label clearly poor ones
for i, value, status in zip(airfoil_ids, clcd_values, status_list):
    if status == "Poor":
        plt.text(i, value + 2, f"{i:02d}", ha="center", fontsize=8)

plt.tight_layout()

output_path = Path(r"C:\Users\Ming\Desktop\clcd_at_4deg_all_50_airfoils.png")
plt.savefig(output_path, dpi=300, bbox_inches="tight")

print(f"\nFigure saved to: {output_path}")

plt.show()