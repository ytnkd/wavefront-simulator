import re

with open('backend/simulator.py', 'r') as f:
    content = f.read()

bad_return_block = """
    # 表示する
    plt.show()
"""

good_return_block = """
    # 図を保存して返す
    import io
    import base64
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", transparent=True)
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode("utf-8")
"""

content = content.replace(bad_return_block.strip(), good_return_block.strip())

with open('backend/simulator.py', 'w') as f:
    f.write(content)
print("Return2 fixed!")
