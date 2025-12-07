# cart002_engineering.py
"""
Cart 002: Engineering Module
Comprehensive engineering toolkit for the mongoose.os BMX system.

Features:
- Structural: beam stress/deflection, column buckling, shaft torsion
- Fluids: hydrostatic pressure, Reynolds number, Darcy-Weisbach head loss
- Thermo: thermal expansion, heat transfer (conduction/convection), TEG estimate
- Electrical: Ohm’s law, RC/LC time constants, power calculations
- Units: simple unit helpers and conversions
- Solver: parameter sweep and optimization stubs
- CLI: run calculators via arguments; export results to JSON
- Logging to JSONL for provenance
"""

import sys
import os
import json
import math
from typing import Dict, Any, List

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT, "data")
LOGS_DIR = os.path.join(ROOT, "logs")
OUT_DIR = os.path.join(ROOT, "artifacts")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)

AUDIT = os.path.join(LOGS_DIR, "engineering_audit.jsonl")

def audit(entry: Dict[str, Any]):
    entry = dict(entry)
    entry["t"] = __import__("time").strftime("%Y-%m-%dT%H:%M:%S", __import__("time").gmtime())
    with open(AUDIT, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

# ---------- Units ----------
class Units:
    @staticmethod
    def mm_to_m(mm): return mm / 1000.0
    @staticmethod
    def cm2_to_m2(cm2): return cm2 / 10000.0
    @staticmethod
    def N_to_kN(N): return N / 1000.0
    @staticmethod
    def C_to_K(C): return C + 273.15

# ---------- Structural ----------
def beam_bending_stress(M: float, c: float, I: float) -> float:
    """sigma = M*c/I"""
    return M * c / I

def beam_deflection_uniform_load(w: float, L: float, E: float, I: float) -> float:
    """delta = (5 w L^4) / (384 E I)"""
    return (5.0 * w * (L**4)) / (384.0 * E * I)

def euler_buckling_load(E: float, I: float, K: float, L: float) -> float:
    """Pcr = (pi^2 E I) / (K L)^2"""
    return (math.pi**2 * E * I) / ((K * L)**2)

def shaft_torsion_theta(T: float, L: float, J: float, G: float) -> float:
    """theta = T L / (J G)"""
    return (T * L) / (J * G)

# ---------- Fluids ----------
def hydrostatic_pressure(rho: float, h: float, g: float = 9.81) -> float:
    return rho * g * h

def reynolds_number(rho: float, v: float, D: float, mu: float) -> float:
    return (rho * v * D) / mu

def darcy_head_loss(f: float, L: float, D: float, v: float, g: float = 9.81) -> float:
    return f * (L / D) * (v**2) / (2 * g)

# ---------- Thermo ----------
def thermal_expansion(L0: float, alpha: float, dT: float) -> float:
    return L0 * alpha * dT

def conduction_heat_flux(k: float, A: float, dT: float, dx: float) -> float:
    return k * A * dT / dx

def convection_heat_flux(h: float, A: float, dT: float) -> float:
    return h * A * dT

def teg_power_estimate(dT: float, seebeck: float, internal_R: float, load_R: float) -> float:
    """
    Simplified TEG: V = S * dT; I = V / (Rint + Rload); P = I^2 * Rload
    """
    V = seebeck * dT
    I = V / (internal_R + load_R)
    return (I**2) * load_R

# ---------- Electrical ----------
def ohms_law(V: float = None, I: float = None, R: float = None) -> Dict[str, float]:
    if V is None: V = I * R
    if I is None: I = V / R
    if R is None: R = V / I
    return {"V": V, "I": I, "R": R}

def rc_time_constant(R: float, C: float) -> float:
    return R * C

def lc_resonant_freq(L: float, C: float) -> float:
    return 1.0 / (2.0 * math.pi * math.sqrt(L * C))

# ---------- Solver ----------
def sweep(func, param_name: str, values: List[float], fixed_kwargs: Dict[str, Any]) -> List[Dict[str, Any]]:
    out = []
    for v in values:
        kwargs = dict(fixed_kwargs)
        kwargs[param_name] = v
        try:
            res = func(**kwargs)
        except Exception as e:
            res = f"error:{e}"
        out.append({"param": param_name, "value": v, "result": res})
    return out

# ---------- CLI ----------
def example_bundle() -> Dict[str, Any]:
    """Run a bundle of calculations to demonstrate capabilities."""
    E_steel = 200e9
    I_beam = 8.1e-6
    L = 2.0
    w = 1500.0
    c = 0.05

    beam_sigma = beam_bending_stress(M=w*L, c=c, I=I_beam)
    beam_delta = beam_deflection_uniform_load(w=w, L=L, E=E_steel, I=I_beam)
    buckling = euler_buckling_load(E=E_steel, I=I_beam, K=1.0, L=L)

    rho = 998.0
    v = 1.5
    D = 0.05
    mu = 1e-3
    Re = reynolds_number(rho=rho, v=v, D=D, mu=mu)
    head = darcy_head_loss(f=0.02, L=50.0, D=D, v=v)

    alpha = 12e-6
    dT = 60.0
    deltaL = thermal_expansion(L0=1.0, alpha=alpha, dT=dT)
    q_cond = conduction_heat_flux(k=205.0, A=0.01, dT=40.0, dx=0.02)
    q_conv = convection_heat_flux(h=25.0, A=0.01, dT=30.0)
    P_teg = teg_power_estimate(dT=100.0, seebeck=0.2e-3, internal_R=2.0, load_R=4.0)

    ohm = ohms_law(V=12.0, I=None, R=6.0)
    tau_rc = rc_time_constant(R=1000.0, C=1e-6)
    f_lc = lc_resonant_freq(L=10e-3, C=100e-9)

    return {
        "structural": {"beam_stress": beam_sigma, "beam_deflection": beam_delta, "buckling_load": buckling},
        "fluids": {"Re": Re, "head_loss": head},
        "thermo": {"deltaL": deltaL, "q_cond": q_cond, "q_conv": q_conv, "P_teg": P_teg},
        "electrical": {"ohms": ohm, "tau_rc": tau_rc, "f_lc": f_lc}
    }

def save_artifact(name: str, obj: Dict[str, Any]) -> str:
    path = os.path.join(OUT_DIR, f"{name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
    return path

def main():
    args = sys.argv[1:]
    if not args:
        print("Engineering: running example bundle...")
        result = example_bundle()
        audit({"action": "bundle"})
        path = save_artifact("engineering_bundle", result)
        print(json.dumps(result, indent=2))
        print(f"Saved: {path}")
        return

    # Minimal CLI dispatcher
    cmd = args[0]
    audit({"action": "cli", "cmd": cmd})
    if cmd == "beam":
        M = float(args[1]); c = float(args[2]); I = float(args[3])
        res = {"sigma": beam_bending_stress(M, c, I)}
        print(json.dumps(res, indent=2))
    elif cmd == "fluid":
        rho = float(args[1]); h = float(args[2])
        res = {"p": hydrostatic_pressure(rho, h)}
        print(json.dumps(res, indent=2))
    elif cmd == "reynolds":
        rho = float(args[1]); v = float(args[2]); D = float(args[3]); mu = float(args[4])
        res = {"Re": reynolds_number(rho, v, D, mu)}
        print(json.dumps(res, indent=2))
    elif cmd == "teg":
        dT = float(args[1]); S = float(args[2]); Rint = float(args[3]); Rload = float(args[4])
        res = {"P": teg_power_estimate(dT, S, Rint, Rload)}
        print(json.dumps(res, indent=2))
    elif cmd == "sweep":
        # Example: sweep teg over dT values
        values = [20, 40, 60, 80, 100]
        fixed = {"seebeck": 0.2e-3, "internal_R": 2.0, "load_R": 4.0}
        rows = sweep(lambda dT, seebeck, internal_R, load_R: teg_power_estimate(dT, seebeck, internal_R, load_R), "dT", values, fixed)
        path = save_artifact("teg_sweep", {"rows": rows})
        print(json.dumps({"rows": rows}, indent=2)); print(f"Saved: {path}")
    else:
        print("Unknown command. Try: beam | fluid | reynolds | teg | sweep")

if __name__ == "__main__":
    main()