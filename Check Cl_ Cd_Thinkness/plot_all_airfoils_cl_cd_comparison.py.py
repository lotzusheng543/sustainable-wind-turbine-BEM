import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Folder containing CLD00 to CLD49
CLD_DIR = Path(r"C:\Users\Ming\Desktop\Airfoil-Coords-CLD\CLD")


TARGET_AIRFOILS = list(range(0, 50))

# Angle of attack range: 0° to 20°
ALPHA_RANGE = np.arange(0.0, 20.01, 1.0)  # 0, 1, 2, ..., 20 deg


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

    data = data[np.argsort(data[:, 0])]
    return data


def find_cld_file(airfoil_id):
    possible_files = [
        CLD_DIR / f"CLD{airfoil_id:02d}",
        CLD_DIR / f"CLD{airfoil_id:02d}.txt",
    ]

    for p in possible_files:
        if p.exists():
            return p

    raise FileNotFoundError(f"Could not find CLD file for CLD{airfoil_id:02d}")


all_rows = []

plt.figure(figsize=(10, 6))

for airfoil_id in TARGET_AIRFOILS:
    file_path = find_cld_file(airfoil_id)
    data = read_cld_file(file_path)

    alpha_data = data[:, 0]
    cl_data = data[:, 1]
    cd_data = data[:, 2]

    # Interpolate CL and CD from 0 to 20 degrees
    cl_interp = np.interp(ALPHA_RANGE, alpha_data, cl_data)
    cd_interp = np.interp(ALPHA_RANGE, alpha_data, cd_data)
    cl_cd_interp = cl_interp / cd_interp

    for a, cl, cd, clcd in zip(ALPHA_RANGE, cl_interp, cd_interp, cl_cd_interp):
        all_rows.append({
            "Airfoil": f"COORD{airfoil_id:02d}",
            "AoA [deg]": a,
            "CL": cl,
            "CD": cd,
            "CL/CD": clcd
        })

    # Plot CL/CD over 0–20 degrees
    plt.plot(
        ALPHA_RANGE,
        cl_cd_interp,
        marker="o",
        linewidth=2,
        label=f"COORD{airfoil_id:02d}"
    )


# Save table
df = pd.DataFrame(all_rows)

print("\nCL, CD and CL/CD from 0° to 20°")
print("=" * 70)
print(df.to_string(index=False, formatters={
    "AoA [deg]": "{:.1f}".format,
    "CL": "{:.4f}".format,
    "CD": "{:.5f}".format,
    "CL/CD": "{:.2f}".format
}))

csv_path = Path(r"C:\Users\Ming\Desktop\all_airfoils_cl_cd_0to20.csv")
df.to_csv(csv_path, index=False)

print(f"\nCSV saved to: {csv_path}")


# Plot formatting
plt.xlabel("Angle of attack, α [deg]")
plt.ylabel("CL/CD")
plt.title("CL/CD Comparison for All Airfoils, α = 0° to 20°")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

fig_path = Path(r"C:\Users\Ming\Desktop\all_airfoils_clcd_0to20.png")
plt.savefig(fig_path, dpi=300, bbox_inches="tight")

print(f"Figure saved to: {fig_path}")

plt.show()