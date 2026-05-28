import re

with open('backend/simulator.py', 'r') as f:
    content = f.read()

bad_return = """    return {
        "report_img_base64": base64.b64encode(buf.getvalue()).decode("utf-8"),
        "rms_total": total_info,
        "rms_lower": lower_info,
        "rms_higher": higher_info
    }"""

good_return = """    return {
        "report_img_base64": base64.b64encode(buf.getvalue()).decode("utf-8"),
        "rms_total": total_info,
        "rms_lower": lower_info,
        "rms_higher": higher_info,
        "psf": psf,
        "arcmin_per_px": arcmin_per_px
    }"""

content = content.replace(bad_return, good_return)

with open('backend/simulator.py', 'w') as f:
    f.write(content)
print("Updated report return!")
