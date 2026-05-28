import re

with open('backend/simulator.py', 'r') as f:
    content = f.read()

presets_orig = """
    return {
        "No aberration": {},
        "Myopia (Nearsightedness)": {(2, 0): 1.5},
        "Hyperopia (Farsightedness)": {(2, 0): -1.5},
        "Nuclear Cataract (核白内障)": {(4, 0): 0.8},
        "Cortical Cataract (皮質白内障)": {(4, 0): -0.8},
        "Astigmatism (WTR)": {(2, 2): 1.0},
"""

presets_new = """
    return {
        "No aberration": {},
        "Myopia": {(2, 0): 1.5},
        "Hyperopia": {(2, 0): -1.5},
        "核白内障": {(4, 0): 0.8},
        "皮質白内障": {(4, 0): -0.8},
        "Astigmatism": {(2, 2): 1.0},
"""

content = content.replace(presets_orig.strip(), presets_new.strip())

with open('backend/simulator.py', 'w') as f:
    f.write(content)
print("Presets fixed!")
