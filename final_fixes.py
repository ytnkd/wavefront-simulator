import re

with open('backend/simulator.py', 'r') as f:
    content = f.read()

# Fix 1: plot_wavefront_mode_map Piston Green
bad_block1 = """
        # 円外をNaNにするためのマスクを作る
        _, _, rho_tmp, theta_tmp, pupil_tmp = make_pupil_coordinates(N=mode_size, pad_factor=1)
        Zimg[~pupil_tmp] = np.nan

        # 表示スケールを決める
"""
good_block1 = """
        # 円外をNaNにするためのマスクを作る
        _, _, rho_tmp, theta_tmp, pupil_tmp = make_pupil_coordinates(N=mode_size, pad_factor=1)
        Zimg[~pupil_tmp] = np.nan
        if n == 0 and m == 0:
            Zimg[pupil_tmp] = 0.0

        # 表示スケールを決める
"""
content = content.replace(bad_block1.strip("\n"), good_block1.strip("\n"))

# Fix 2: plot_surface_3d color
bad_block2_1 = """def plot_surface_3d(ax, x_values, y_values, z_values, title, xlabel, ylabel, zlabel, elev=28, azim=-60):
    # 2次元格子を作る
    xx, yy = np.meshgrid(x_values, y_values)

    # サーフェスを描く
    ax.plot_surface(xx, yy, z_values, rstride=1, cstride=1, linewidth=0, antialiased=True)"""
good_block2_1 = """def plot_surface_3d(ax, x_values, y_values, z_values, title, xlabel, ylabel, zlabel, elev=28, azim=-60, color=None):
    # 2次元格子を作る
    xx, yy = np.meshgrid(x_values, y_values)

    # サーフェスを描く
    ax.plot_surface(xx, yy, z_values, rstride=1, cstride=1, linewidth=0, antialiased=True, color=color)"""
content = content.replace(bad_block2_1, good_block2_1)

bad_block2_2 = """plot_surface_3d(ax41, mtf_axis, mtf_axis, mtf_crop, "11c. MTF 3D surface", "Freq x [cpd]", "Freq y [cpd]", "MTF", elev=28, azim=-60)"""
good_block2_2 = """plot_surface_3d(ax41, mtf_axis, mtf_axis, mtf_crop, "11c. MTF 3D surface", "Freq x [cpd]", "Freq y [cpd]", "MTF", elev=28, azim=-60, color='red')"""
content = content.replace(bad_block2_2, good_block2_2)

# Fix 3: English labels
bad_block3 = """
    return {
        "No aberration": {},
        "Myopia": {(2, 0): 1.5},
        "Hyperopia": {(2, 0): -1.5},
        "核白内障": {(4, 0): 0.8},
        "皮質白内障": {(4, 0): -0.8},
        "Astigmatism": {(2, 2): 1.0},
"""
good_block3 = """
    return {
        "No aberration": {},
        "Myopia": {(2, 0): 1.5},
        "Hyperopia": {(2, 0): -1.5},
        "Nuclear cataract": {(4, 0): 0.8},
        "Cortical cataract": {(4, 0): -0.8},
        "Astigmatism": {(2, 2): 1.0},
"""
content = content.replace(bad_block3.strip("\n"), good_block3.strip("\n"))

with open('backend/simulator.py', 'w') as f:
    f.write(content)

print("Applied 3 fixes!")
