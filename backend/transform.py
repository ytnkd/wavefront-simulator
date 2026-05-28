import re

with open('01_Wavefront_simulator_code.txt', 'r') as f:
    lines = f.readlines()

# Filter out lines related to ipywidgets and PIL import if they cause issues, but PIL is fine.
# We will truncate everything from "class ZernikeTeachingApp:"
out_lines = []
for line in lines:
    if line.startswith('class ZernikeTeachingApp:'):
        break
    out_lines.append(line)

code = "".join(out_lines)

# Replace inline plotting with Agg and base64
code = code.replace('%matplotlib inline', 'import matplotlib\nmatplotlib.use("Agg")\nimport base64')

# Modify plot_wavefront_simulator_report to save and return base64
old_report_return = """    # レイアウトを整える
    plt.tight_layout(rect=[0.0, 0.0, 1.0, 0.97])

    # 図を表示する
    plt.show()

    # 結果を返す
    return {"""

new_report_return = """    # レイアウトを整える
    plt.tight_layout(rect=[0.0, 0.0, 1.0, 0.97])

    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100)
    plt.close(fig)
    report_img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')

    # 結果を返す
    return {
        "report_img_base64": report_img_base64,"""

code = code.replace(old_report_return, new_report_return)

# Modify plot_wavefront_mode_map to save and return base64
old_map_return = """    # レイアウトを整える
    plt.tight_layout()

    # 表示する
    plt.show()"""

new_map_return = """    # レイアウトを整える
    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100)
    plt.close(fig)
    map_img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return map_img_base64"""

code = code.replace(old_map_return, new_map_return)

# Fix empty figure bug in map when show_all=False and no mode is selected
old_map_empty = """    # 表示対象がなければメッセージを出す
    if len(modes_to_draw) == 0:
        ax.text(0.5, 0.5, "No Zernike mode selected", ha="center", va="center", fontsize=18, transform=ax.transAxes)
        ax.axis("off")
        plt.show()
        return"""

new_map_empty = """    # 表示対象がなければメッセージを出す
    if len(modes_to_draw) == 0:
        ax.text(0.5, 0.5, "No Zernike mode selected", ha="center", va="center", fontsize=18, transform=ax.transAxes)
        ax.axis("off")
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=100)
        plt.close(fig)
        return base64.b64encode(buf.getvalue()).decode('utf-8')"""

code = code.replace(old_map_empty, new_map_empty)

# Write to simulator.py
with open('backend/simulator.py', 'w') as f:
    f.write(code)

