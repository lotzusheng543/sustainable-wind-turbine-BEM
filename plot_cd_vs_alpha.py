import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# ===== folder path =====
CLD_DIR = Path(r"C:\Users\Ming\Desktop\Airfoil-Coords-CLD\CLD")

# ===== read one CLD file =====
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

    # sort by alpha
    data = data[np.argsort(data[:, 0])]
    return data


# ===== find CLD file =====
def find_cld_file(i):
    possible_files = [
        CLD_DIR / f"CLD{i:02d}",
        CLD_DIR / f"CLD{i:02d}.txt",
    ]

    for p in possible_files:
        if p.exists():
            return p

    raise FileNotFoundError(f"Could not find CLD file for CLD{i:02d}")


# ===== make symmetric CD curve =====
def make_symmetrised_cd_curve(alpha, cd, alpha_min=-20, alpha_max=20, step=1):
    # keep only needed range for interpolation stability
    mask = (alpha >= alpha_min) & (alpha <= alpha_max)
    alpha_use = alpha[mask]
    cd_use = cd[mask]

    if len(alpha_use) < 2:
        return None, None

    # positive side including zero
    alpha_pos = np.arange(0, alpha_max + step, step)

    cd_sym = []
    for a in alpha_pos:
        cd_plus = np.interp(a, alpha_use, cd_use)
        cd_minus = np.interp(-a, alpha_use, cd_use)
        cd_avg = 0.5 * (cd_plus + cd_minus)
        cd_sym.append(cd_avg)

    cd_sym = np.array(cd_sym)

    # mirror to negative side
    alpha_full = np.concatenate((-alpha_pos[:0:-1], alpha_pos))
    cd_full = np.concatenate((cd_sym[:0:-1], cd_sym))

    return alpha_full, cd_full


# ===== plot =====
plt.figure(figsize=(12, 7))

for i in range(50):
    file_path = find_cld_file(i)
    data = read_cld_file(file_path)

    alpha = data[:, 0]
    cd = data[:, 2]

    alpha_plot, cd_plot = make_symmetrised_cd_curve(alpha, cd, alpha_min=-20, alpha_max=20, step=1)

    if alpha_plot is None:
        continue

    plt.plot(alpha_plot, cd_plot, linewidth=1.0, alpha=0.75)

plt.xlabel("Angle of attack, α [deg]")
plt.ylabel("Drag coefficient, CD")
plt.title("Symmetrised CD vs Angle of Attack for All 50 Aerofoils")
plt.grid(True, alpha=0.3)

# 这个范围更像 lecture slide
plt.xlim(-20, 20)
plt.ylim(0, 0.25)

output_path = Path(r"C:\Users\Ming\Desktop\cd_vs_alpha_symmetrised_all_50.png")
plt.savefig(output_path, dpi=300, bbox_inches="tight")

print(f"Figure saved to: {output_path}")

plt.show()