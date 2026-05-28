import re

with open('backend/simulator.py', 'r') as f:
    content = f.read()

start_idx = content.find('def plot_wavefront_simulator_report(')
end_idx = content.find('def plot_wavefront_mode_map(', start_idx)

func_content = content[start_idx:end_idx]

# Replace plt.show() and the return dictionary inside func_content
new_func_content = re.sub(
    r'# 図を表示する\s+plt\.show\(\)\s+# 結果を返す\s+return \{.*?\}',
    """# 図を保存して返す
    import io
    import base64
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    return {
        "report_img_base64": base64.b64encode(buf.getvalue()).decode("utf-8"),
        "rms_total": total_info,
        "rms_lower": lower_info,
        "rms_higher": higher_info
    }""",
    func_content,
    flags=re.DOTALL
)

new_content = content[:start_idx] + new_func_content + content[end_idx:]

with open('backend/simulator.py', 'w') as f:
    f.write(new_content)

print("Report return fixed!")
