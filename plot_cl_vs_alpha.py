import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

CLD_DIR = Path(r"C:\Users\Ming\Desktop\Airfoil-Coords-CLD\CLD")

def read_cld_file(file_path):
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

plt.figure(figsize=(12, 7))

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

    plt.plot(alpha, cl, linewidth=1.0, alpha=0.65)

plt.xlabel("Angle of attack, α [deg]")
plt.ylabel("Lift coefficient, CL")
plt.title("CL vs Angle of Attack for All 50 Aerofoils (-10° to 20°)")
plt.grid(True, alpha=0.3)
plt.xlim(-10, 20)

output_path = Path(r"C:\Users\Ming\Desktop\cl_vs_alpha_all_50_airfoils_zoom_-10_to_20.png")
plt.savefig(output_path, dpi=300, bbox_inches="tight")

print(f"Figure saved to: {output_path}")
plt.show()