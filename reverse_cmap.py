import re

with open('backend/simulator.py', 'r') as f:
    content = f.read()

# Reverse the custom colormap colors
orig_colors = """    colors = [
        "#08306B",  # dark blue
        "#0050FF",  # blue
        "#4FC3F7",  # light blue
        "#2ECC71",  # green
        "#F4E04D",  # yellow
        "#F39C12",  # orange
        "#D7191C",  # red
    ]"""

new_colors = """    colors = [
        "#D7191C",  # red
        "#F39C12",  # orange
        "#F4E04D",  # yellow
        "#2ECC71",  # green
        "#4FC3F7",  # light blue
        "#0050FF",  # blue
        "#08306B",  # dark blue
    ]"""

new_content = content.replace(orig_colors, new_colors)

with open('backend/simulator.py', 'w') as f:
    f.write(new_content)
print("Reversed!")
