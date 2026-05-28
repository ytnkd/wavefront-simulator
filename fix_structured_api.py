import re

with open('backend/simulator.py', 'r') as f:
    content = f.read()

# Add get_active_modes_info function
structured_func = """def selected_formula_lines(coeffs, j_map=None, max_modes=None):
    if j_map is None:
        j_map = build_j_map()
    lines = []
    if len(coeffs) == 0:
        lines.append("None")
        return lines
    modes = sorted(coeffs.keys())
    if max_modes is not None:
        modes = modes[:max_modes]
    for mode in modes:
        n, m = mode
        j = j_map.get(mode, "-")
        value = coeffs[mode]
        lines.append(f"j{j} {z_label(n, m)}   coefficient = {value:+.3f} um")
        lines.append(f"  {zernike_formula_ascii(n, m)}")
        lines.append(f"  W(rho,theta) += ({value:+.3f} um) * {z_label(n, m)}(rho,theta)")
        lines.append("")
    return lines

def get_active_modes_info(coeffs, j_map=None):
    if j_map is None:
        j_map = build_j_map()
    modes = sorted(coeffs.keys())
    result = []
    for mode in modes:
        n, m = mode
        j = j_map.get(mode, "-")
        value = coeffs[mode]
        result.append({
            "j": j,
            "label": z_label(n, m),
            "coeff": value,
            "formula_z": zernike_formula_ascii(n, m)
        })
    return result
"""

# replace selected_formula_lines block
content = re.sub(r'def selected_formula_lines\(.*?(?=\n#|\n\n\n|\Z)', structured_func, content, flags=re.DOTALL)

with open('backend/simulator.py', 'w') as f:
    f.write(content)
print("Updated simulator.py!")
