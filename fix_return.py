import re

with open('backend/simulator.py', 'r') as f:
    content = f.read()

bad_return_block = """
    # 図を表示する
    plt.show()

    # 結果を返す
    return {
        "psf": psf,
        "wavefront_total": W_total,
        "wavefront_lower": W_lower,
        "wavefront_higher": W_higher,
        "pupil_function": pupil_function,
        "otf": otf,
        "mtf2d": mtf2d,
        "landolt_original": landolt,
        "landolt_simulated": blurred,
        "hartmann_image": hartmann_img,
        "hartmann_reference": hartmann_ref,
        "arcmin_per_px": arcmin_per_px,
    }
"""

good_return_block = """
    # 図を保存して返す
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
    }
"""

content = content.replace(bad_return_block.strip(), good_return_block.strip())

with open('backend/simulator.py', 'w') as f:
    f.write(content)
print("Return fixed!")
