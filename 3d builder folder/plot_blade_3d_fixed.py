from pathlib import Path
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# =========================
# USER SETTINGS
# =========================
BASE_DIR = Path(__file__).resolve().parent   # put this .py in Airfoil-Coords-CLD
COORDS_DIR = BASE_DIR / "COORDS"
OUTPUT_PNG = BASE_DIR / "blade_3d_fixed.png"

N_POINTS_SURFACE = 160        # points per upper/lower surface
TWIST_SIGN = -1               # if blade twists the wrong way, change to +1
SECTION_LINE_EVERY = 1        # draw every section outline
SURFACE_ALPHA = 0.95

# =========================
# HELPERS
# =========================
def find_geometry_csv(base_dir: Path) -> Path:
    preferred = [
        base_dir / "task2_final_geometry_19airfoils.csv",
        base_dir / "task2_final_geometry_19airfoils.csv.csv",
    ]
    for p in preferred:
        if p.exists():
            return p

    candidates = sorted(base_dir.glob("*.csv"))
    if not candidates:
        raise FileNotFoundError(f"No CSV file found in {base_dir}")

    # Pick the first CSV that contains the needed columns
    for p in candidates:
        try:
            df = pd.read_csv(p)
            cols = [c.strip().lower() for c in df.columns]
            needed = [
                any(x in cols for x in ["r", "r_m", "radius", "span", "spanwise_r"]),
                any(x in cols for x in ["chord", "chord_m", "c"]),
                any(x in cols for x in ["twist", "twist_deg", "beta", "twist_degree"]),
                any(x in cols for x in ["airfoil", "foil", "profile"]),
            ]
            if all(needed):
                return p
        except Exception:
            pass

    # Fall back to first CSV if nothing matched
    return candidates[0]


def find_column(df: pd.DataFrame, candidates):
    lower_map = {c.strip().lower(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in lower_map:
            return lower_map[cand.lower()]
    raise ValueError(f"Could not find any of these columns: {candidates}\nAvailable columns: {list(df.columns)}")


def normalise_airfoil_name(name) -> str:
    s = str(name).strip().upper()
    m = re.search(r"(\d+)", s)
    if m:
        n = int(m.group(1))
        return f"COORD{n:02d}"
    return s


def resolve_airfoil_file(airfoil_name: str, coords_dir: Path) -> Path:
    label = normalise_airfoil_name(airfoil_name)
    num = re.search(r"(\d+)", label)
    num2 = f"{int(num.group(1)):02d}" if num else ""

    candidates = [
        coords_dir / label,
        coords_dir / f"{label}.txt",
        coords_dir / f"{label}.dat",
        coords_dir / f"COORDS{num2}",
        coords_dir / f"COORDS{num2}.txt",
        coords_dir / f"COORDS{num2}.dat",
        coords_dir / f"COORD{num2}",
        coords_dir / f"COORD{num2}.txt",
        coords_dir / f"COORD{num2}.dat",
    ]

    for p in candidates:
        if p.exists():
            return p

    # loose search fallback
    hits = []
    for p in coords_dir.iterdir():
        stem = p.stem.upper()
        if num2 and num2 in stem and ("COORD" in stem or "COORDS" in stem):
            hits.append(p)
    if hits:
        return sorted(hits)[0]

    raise FileNotFoundError(f"Cannot find coordinate file for {airfoil_name} in {coords_dir}")


def read_airfoil_coords(file_path: Path) -> np.ndarray:
    pts = []
    text = file_path.read_text(encoding="utf-8", errors="ignore")
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        line = line.replace(",", " ")
        vals = []
        for tok in line.split():
            try:
                vals.append(float(tok))
            except ValueError:
                pass
        if len(vals) >= 2:
            pts.append([vals[0], vals[1]])

    arr = np.asarray(pts, dtype=float)
    if len(arr) < 10:
        raise ValueError(f"Not enough numeric coordinate points in {file_path}")

    # Remove repeated final point if present
    if np.allclose(arr[0], arr[-1], atol=1e-10):
        arr = arr[:-1]
    return arr


def split_upper_lower(coords: np.ndarray):
    """
    Convert a closed airfoil loop into two curves:
    upper: LE -> TE
    lower: LE -> TE
    Works even if the original file starts at an arbitrary point.
    """
    x_raw = coords[:, 0]
    y_raw = coords[:, 1]

    chord_raw = x_raw.max() - x_raw.min()
    if chord_raw <= 0:
        raise ValueError("Invalid airfoil chord length (xmax <= xmin)")

    # Normalise to x in [0,1], y scaled by the same chord length
    x = (x_raw - x_raw.min()) / chord_raw
    y = y_raw / chord_raw

    # Start sequence at leading edge
    i_le = int(np.argmin(x))
    x = np.roll(x, -i_le)
    y = np.roll(y, -i_le)

    # From LE, one path goes to TE, then the other path returns to LE
    i_te = int(np.argmax(x))
    side_a = np.column_stack([x[: i_te + 1], y[: i_te + 1]])  # LE -> TE

    side_b_te_to_le = np.column_stack([x[i_te:], y[i_te:]])
    side_b_te_to_le = np.vstack([side_b_te_to_le, [x[0], y[0]]])  # append exact LE
    side_b = side_b_te_to_le[::-1]  # LE -> TE

    # Decide which one is upper by average y
    if np.mean(side_a[:, 1]) >= np.mean(side_b[:, 1]):
        upper, lower = side_a, side_b
    else:
        upper, lower = side_b, side_a

    # Ensure both run from LE (x≈0) to TE (x≈1)
    if upper[0, 0] > upper[-1, 0]:
        upper = upper[::-1]
    if lower[0, 0] > lower[-1, 0]:
        lower = lower[::-1]

    return upper, lower


def resample_curve(curve: np.ndarray, n: int) -> np.ndarray:
    ds = np.sqrt(np.sum(np.diff(curve, axis=0) ** 2, axis=1))
    s = np.concatenate([[0.0], np.cumsum(ds)])
    if s[-1] == 0:
        return np.repeat(curve[:1], n, axis=0)
    s_new = np.linspace(0, s[-1], n)
    x_new = np.interp(s_new, s, curve[:, 0])
    y_new = np.interp(s_new, s, curve[:, 1])
    return np.column_stack([x_new, y_new])


def transform_section(curve_le_to_te: np.ndarray, chord: float, twist_deg: float, r: float, twist_sign: int = -1):
    """
    Input curve is in unit airfoil coords: x from LE->TE, y thickness.
    Scale by chord, shift so 25% chord is the pitch axis, then twist around the span axis.
    Returns Nx3 array: [spanwise r, chordwise, thickness]
    """
    x = curve_le_to_te[:, 0] * chord
    z = curve_le_to_te[:, 1] * chord

    # rotate about quarter-chord / pitch axis
    x = x - 0.25 * chord

    theta = np.deg2rad(twist_sign * twist_deg)
    y_chord = x * np.cos(theta) - z * np.sin(theta)
    z_thick = x * np.sin(theta) + z * np.cos(theta)
    x_span = np.full_like(y_chord, r)
    return np.column_stack([x_span, y_chord, z_thick])


def closed_loop_from_upper_lower(upper_xyz: np.ndarray, lower_xyz: np.ndarray) -> np.ndarray:
    # upper: LE->TE, lower: LE->TE
    # closed loop: upper LE->TE, then lower TE->LE
    return np.vstack([upper_xyz, lower_xyz[-2:0:-1]])


def set_axes_equal_3d(ax, X, Y, Z):
    x_min, x_max = np.nanmin(X), np.nanmax(X)
    y_min, y_max = np.nanmin(Y), np.nanmax(Y)
    z_min, z_max = np.nanmin(Z), np.nanmax(Z)

    x_mid = 0.5 * (x_min + x_max)
    y_mid = 0.5 * (y_min + y_max)
    z_mid = 0.5 * (z_min + z_max)

    max_range = max(x_max - x_min, y_max - y_min, z_max - z_min)
    half = 0.5 * max_range

    ax.set_xlim(x_mid - half, x_mid + half)
    ax.set_ylim(y_mid - half, y_mid + half)
    ax.set_zlim(z_mid - half, z_mid + half)

    try:
        ax.set_box_aspect((x_max - x_min, y_max - y_min, z_max - z_min))
    except Exception:
        pass


# =========================
# MAIN
# =========================
def main():
    if not COORDS_DIR.exists():
        raise FileNotFoundError(f"COORDS folder not found: {COORDS_DIR}")

    geom_csv = find_geometry_csv(BASE_DIR)
    print(f"Using geometry CSV: {geom_csv}")
    df = pd.read_csv(geom_csv)
    print("\nGeometry columns found:", list(df.columns))

    r_col = find_column(df, ["r", "r_m", "radius", "span", "spanwise_r"])
    chord_col = find_column(df, ["chord", "chord_m", "c"])
    twist_col = find_column(df, ["twist", "twist_deg", "beta", "twist_degree"])
    foil_col = find_column(df, ["airfoil", "foil", "profile"])

    geom = df[[r_col, chord_col, twist_col, foil_col]].copy()
    geom.columns = ["r", "chord", "twist", "airfoil"]
    geom = geom.sort_values("r").reset_index(drop=True)

    print("\nAirfoil order used:")
    for i, row in geom.iterrows():
        print(
            f"Section {i+1:02d}: r = {row['r']:.2f} m, chord = {row['chord']:.2f} m, "
            f"twist = {row['twist']:.2f} deg, airfoil = {row['airfoil']}"
        )

    upper_sections = []
    lower_sections = []

    for _, row in geom.iterrows():
        foil_name = row["airfoil"]
        coord_file = resolve_airfoil_file(foil_name, COORDS_DIR)
        raw = read_airfoil_coords(coord_file)
        upper, lower = split_upper_lower(raw)
        upper = resample_curve(upper, N_POINTS_SURFACE)
        lower = resample_curve(lower, N_POINTS_SURFACE)

        upper_xyz = transform_section(upper, row["chord"], row["twist"], row["r"], TWIST_SIGN)
        lower_xyz = transform_section(lower, row["chord"], row["twist"], row["r"], TWIST_SIGN)

        upper_sections.append(upper_xyz)
        lower_sections.append(lower_xyz)

    upper_sections = np.asarray(upper_sections)   # [n_sec, n_pts, 3]
    lower_sections = np.asarray(lower_sections)

    # arrays for plot_surface: [n_sec, n_pts]
    Xu, Yu, Zu = upper_sections[:, :, 0], upper_sections[:, :, 1], upper_sections[:, :, 2]
    Xl, Yl, Zl = lower_sections[:, :, 0], lower_sections[:, :, 1], lower_sections[:, :, 2]

    fig = plt.figure(figsize=(14, 8), dpi=160)
    ax = fig.add_subplot(111, projection="3d")

    blade_color = (0.73, 0.78, 0.86)   # CAD-like light grey-blue
    edge_color = (0.35, 0.37, 0.42)

    # upper and lower skin separately -> avoids the collapse caused by wrong closed-loop lofting
    ax.plot_surface(Xu, Yu, Zu, color=blade_color, alpha=SURFACE_ALPHA, linewidth=0, antialiased=True, shade=True)
    ax.plot_surface(Xl, Yl, Zl, color=blade_color, alpha=SURFACE_ALPHA, linewidth=0, antialiased=True, shade=True)

    # root cap and tip cap
    root_loop = closed_loop_from_upper_lower(upper_sections[0], lower_sections[0])
    tip_loop = closed_loop_from_upper_lower(upper_sections[-1], lower_sections[-1])
    ax.add_collection3d(Poly3DCollection([root_loop], facecolor=blade_color, edgecolor=edge_color, linewidth=0.4, alpha=SURFACE_ALPHA))
    ax.add_collection3d(Poly3DCollection([tip_loop], facecolor=blade_color, edgecolor=edge_color, linewidth=0.4, alpha=SURFACE_ALPHA))

    # section outlines
    for i in range(0, len(upper_sections), SECTION_LINE_EVERY):
        loop = closed_loop_from_upper_lower(upper_sections[i], lower_sections[i])
        ax.plot(loop[:, 0], loop[:, 1], loop[:, 2], color=edge_color, linewidth=0.4, alpha=0.7)

    # leading edge, trailing edge, quarter-chord axis
    LE = 0.5 * (upper_sections[:, 0, :] + lower_sections[:, 0, :])
    TE = 0.5 * (upper_sections[:, -1, :] + lower_sections[:, -1, :])
    pitch_axis = np.column_stack([geom["r"].to_numpy(), np.zeros(len(geom)), np.zeros(len(geom))])

    ax.plot(LE[:, 0], LE[:, 1], LE[:, 2], "k--", lw=1.0, label="Leading edge")
    ax.plot(TE[:, 0], TE[:, 1], TE[:, 2], color="gray", lw=1.0, label="Trailing edge")
    ax.plot(pitch_axis[:, 0], pitch_axis[:, 1], pitch_axis[:, 2], "r-.", lw=1.0, label="Quarter-chord / pitch axis")

    # cosmetics
    ax.set_title("3D Wind Turbine Blade (fixed upper/lower surface loft)", pad=16, fontsize=13)
    ax.set_xlabel("Spanwise direction r [m]", labelpad=12)
    ax.set_ylabel("Chordwise direction [m]", labelpad=12)
    ax.set_zlabel("Thickness direction [m]", labelpad=12)
    ax.legend(loc="upper left", fontsize=9)

    # CAD-like view. If you want the opposite side, try azim=-120 or azim=60.
    ax.view_init(elev=18, azim=-118)

    # Make axes less ugly
    allX = np.concatenate([Xu.ravel(), Xl.ravel()])
    allY = np.concatenate([Yu.ravel(), Yl.ravel()])
    allZ = np.concatenate([Zu.ravel(), Zl.ravel()])
    set_axes_equal_3d(ax, allX, allY, allZ)

    # Slight zoom-in by trimming blank margins around the blade
    x_min, x_max = np.min(allX), np.max(allX)
    y_min, y_max = np.min(allY), np.max(allY)
    z_min, z_max = np.min(allZ), np.max(allZ)
    ax.set_xlim(x_min - 2, x_max + 2)
    ax.set_ylim(y_min - 1.5, y_max + 1.5)
    ax.set_zlim(z_min - 1.5, z_max + 1.5)

    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUTPUT_PNG, bbox_inches="tight")
    print(f"\nSaved figure to: {OUTPUT_PNG}")
    plt.show()


if __name__ == "__main__":
    main()