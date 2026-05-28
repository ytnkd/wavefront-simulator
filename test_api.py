import urllib.request
import json

reqData = {
    "coeffs": {"(2, 0)": 1.5},
    "pupil_mm": 5.0,
    "wavelength_nm": 555,
    "landolt_diameter_arcmin": 20.0,
    "contrast": 1.0,
    "gap_direction_deg": 0,
    "N": 512,
    "pad_factor": 2,
    "lenslet_n": 13
}

try:
    req = urllib.request.Request(
        'http://127.0.0.1:8001/api/simulate',
        data=json.dumps(reqData).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req) as res:
        print("Status:", res.status)
        data = json.loads(res.read().decode('utf-8'))
        print("Success! Vision images count:", len(data.get("vision_images_base64", [])))
except Exception as e:
    print("Exception:", e)
