# SESM3037 — Turbine Blade Design for a 16 MW Offshore Wind Turbine

## Project Overview

This repository contains the aerodynamic design and performance analysis code
for a 16 MW offshore wind turbine blade, developed as part of the SESM3037
Group Design Coursework at the University of Southampton.

Blade Element Momentum (BEM) theory is implemented with empirical corrections
and used to design, verify, and analyse turbine blade performance across a
range of operating conditions.

---

## Repository Structure

```
📁 root/
├── Task1-BEM_Calculation.ipynb                                # Task 1: BEM implementation + 0.5 MW verification
├── Task2-BEM_Task2_CLEAN.ipynb  ├──     Task2 clean           # Task 2: 16 MW blade aerodynamic design
|                                 └──     Task2 better plot     # Task 2: better plot
|
├── Task5-Task5_Wind_Conditions.ipynb                          # Task 5: Performance & control analysis
├── Reference Turbine ├──RISOA1A18LiftDragCharacteristics.csv  # Reference aerofoil polars
|                     └──RISO-A1-A18 Profile...csv             # Reference blade geometry (0.5 MW)
|          
└── README.md
└── Excel to Solidworks
```
<img width="910" height="278" alt="3d" src="https://github.com/user-attachments/assets/ad25def0-599b-40c6-9a28-66dae6f40f81" />


---

## Tasks Covered

| Task | Description | Notebook |
|------|-------------|----------|
| **1c** | Initial sizing via 1D Actuator Disc Model (Betz limit) | `BEM_Calculation.ipynb` |
| **1d** | BEM implementation: empirical thrust + tip loss factor | `BEM_Calculation.ipynb` |
| **1e** | Code verification against 0.5 MW RISO A1-A18 reference blade | `BEM_Calculation.ipynb` |
| **2a–d** | Aerodynamic blade design: chord, twist, aerofoil selection, iteration | `BEM_Task2_CLEAN.ipynb` |
| **5a** | BEM sweep: 50%–200% nominal wind speed at fixed pitch angles | `Task5_Wind_Conditions.ipynb` |
| **5b** | Operation envelope: pitch regulation schedule & power–speed map | `Task5_Wind_Conditions.ipynb` |
| **5c** | Mechanical loads at 200% nominal wind (flapwise/edgewise BM + root stress) | `Task5_Wind_Conditions.ipynb` |
| **5d** | Discussion: adapting blade for onshore 8 MW half-power variant | `Task5_Wind_Conditions.ipynb` |

---

## Key Parameters

### Turbine Specification

| Parameter               | Value        | Basis                       |
|-------------------------|--------------|-----------------------------|
| Rated Power             | 16 MW        | Group design choice         |
| Nominal Wind Speed V₀   | 11 m/s       | Group design choice         |
| Tip Speed Ratio (TSR)   | 8            | Group design choice         |
| Number of Blades        | 3            | Industry standard           |
| Air Density ρ           | 1.225 kg/m³  | Standard sea-level atmosphere |

### Task 1 — Initial Sizing (1D Actuator Disc, Betz Limit)

| Parameter               | Value        | Formula                          |
|-------------------------|--------------|----------------------------------|
| Betz CP limit           | 0.5926       | CP = 16/27, at axial induction a = 1/3 |
| Swept Area A            | 33,119 m²    | A = P / (½ρV₀³ · CP)            |
| Estimated Blade Radius R | 102.7 m     | R = √(A / π)                    |
| Angular Velocity Ω      | 0.857 rad/s  | Ω = TSR · V₀ / R                |
| Rotor Speed             | 8.18 RPM     | RPM = Ω · 60 / 2π               |

### Task 2 — Final Blade Design (After Aerodynamic Iteration)

| Parameter               | Value        | Notes                            |
|-------------------------|--------------|----------------------------------|
| Blade Radius R          | 120.4 m      | Includes root section            |
| Angular Velocity Ω      | 0.731 rad/s  | Ω = TSR · V₀ / R                |
| Rotor Speed             | 6.98 RPM     | RPM = Ω · 60 / 2π               |
| No. of Blade Elements   | ≥ 18         | Per coursework requirement       |
| Reference Blade         | RISO A1-A18  | 0.5 MW, used for scaling         |

### Task 5 — Wind Condition Analysis

| Parameter               | Value        | Notes                            |
|-------------------------|--------------|----------------------------------|
| Wind Speed Range (5a)   | 5.5–22 m/s   | 50%–200% of V₀ = 11 m/s         |
| Pitch Angles Swept (5a) | 0°–20°       | Fixed pitch, 6 angles            |
| High-Wind Load Case (5c)| 22 m/s       | 200% nominal, flapwise + edgewise BM |
| Control Strategy        | Pitch regulation | θₚ increased above rated wind to hold 16 MW |

---

## BEM Extensions Implemented

- **Empirical thrust correction** — applied when axial induction factor a > 0.4
- **Prandtl tip loss factor** — accounts for finite blade number
- **Glauert optimal rotor** — used as reference for chord/twist initial guess

---

## How to Run

### Requirements

```bash
pip install numpy pandas matplotlib scipy
```

### File Path Configuration

⚠️ Update the file paths in **Cell 2** of each notebook before running:

```python
BASE_DIR     = r"YOUR_LOCAL_PATH"
CLD_FOLDER   = r"YOUR_CLD_FOLDER_PATH"
REF_GEOM_CSV = os.path.join(BASE_DIR, "RISO-A1-A18 Profile for 500kW Reference Turbine Blade.csv")
```

### Execution Order

Run all cells **top-to-bottom** in each notebook. Each notebook is self-contained.

---

## Authors & Contributions

| Member | Contribution |
|--------|-------------|
| LO TZU SHENG and Zhang Zhiming | Task 1: BEM implementation & verification |
| LO TZU SHENG and Zhang Zhiming | Task 2: Aerodynamic blade design |
| LO TZU SHENG and Zhang Zhiming | Task 5: Wind condition & control analysis |
| Zhi Xi Tang | Excel to .txt to Solidworks |

---

## Academic Context

- **Module:** SESM3037 — Aerodynamics and Structural Mechanics of Wind Turbine Blades  
- **Institution:** University of Southampton  
- **Presentation:** Friday 15 May 2026, 14:00–16:00 (Done)
