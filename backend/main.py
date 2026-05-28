from fastapi import FastAPI, Response
from pydantic import BaseModel
from typing import Dict, Any
from fastapi.middleware.cors import CORSMiddleware
import simulator
import ast

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SimulationRequest(BaseModel):
    coeffs: Dict[str, float]
    pupil_mm: float = 4.0
    wavelength_nm: int = 555
    landolt_diameter_arcmin: float = 20.0
    gap_direction_deg: int = 0
    contrast: float = 1.0
    N: int = 512
    pad_factor: int = 2
    lenslet_n: int = 13

@app.get("/api/presets")
def get_presets():
    presets = simulator.build_presets()
    j_map = simulator.build_j_map()
    
    # Convert keys to string for JSON serialization
    str_presets = {}
    for name, coeffs in presets.items():
        str_coeffs = {str(k): v for k, v in coeffs.items()}
        str_presets[name] = str_coeffs

    return {
        "presets": str_presets,
        "mode_info": {str(k): v for k, v in simulator.build_mode_info().items()},
        "j_map": {str(k): v for k, v in j_map.items()},
        "n_max": 6
    }

@app.get("/api/thumbnail/{n}/{m}")
def get_thumbnail(n: int, m: int):
    mode = (n, m)
    rgba = simulator.make_mode_thumbnail(mode, size=140)
    png_bytes = simulator.rgba_to_png_bytes(rgba)
    return Response(content=png_bytes, media_type="image/png")

@app.post("/api/simulate")
def run_simulation(req: SimulationRequest):
    # Convert coeffs keys from string "(n, m)" back to tuple (n, m)
    coeffs_tuple = {}
    for k, v in req.coeffs.items():
        try:
            mode = ast.literal_eval(k)
            coeffs_tuple[mode] = v
        except Exception:
            pass

    # Generate main report
    result = simulator.plot_wavefront_simulator_report(
        title="Wavefront Simulator",
        coeffs=coeffs_tuple,
        pupil_mm=req.pupil_mm,
        wavelength_nm=req.wavelength_nm,
        landolt_diameter_arcmin=req.landolt_diameter_arcmin,
        gap_direction_deg=req.gap_direction_deg,
        contrast=req.contrast,
        N=req.N,
        pad_factor=req.pad_factor,
        lenslet_n=req.lenslet_n,
    )

    # Generate mode map
    mode_map_b64 = simulator.plot_wavefront_mode_map(
        coeffs=coeffs_tuple,
        n_max=6,
        show_all=True,
        show_coeff_value=True,
        mode_size=220,
    )

    j_map = simulator.build_j_map()
    formulae = simulator.selected_formula_lines(coeffs_tuple, j_map=j_map, max_modes=None)
    active_modes = simulator.get_active_modes_info(coeffs_tuple, j_map=j_map)
    
    # Generate vision simulation images
    vision_b64 = simulator.get_vision_simulation_base64(
        result["psf"], 
        result["arcmin_per_px"], 
        crop_radius_arcmin=60.0
    )

    return {
        "report_img_base64": result.get("report_img_base64"),
        "mode_map_img_base64": mode_map_b64,
        "vision_images_base64": vision_b64,
        "rms_total": result["rms_total"],
        "rms_lower": result["rms_lower"],
        "rms_higher": result["rms_higher"],
        "formulae": formulae,
        "active_modes": active_modes,
    }
