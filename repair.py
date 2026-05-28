import re

with open('backend/simulator.py', 'r') as f:
    content = f.read()

with open('01_Wavefront_simulator_code.txt', 'r') as f:
    orig = f.read()

# Extract generate_report from orig
start_idx = orig.find('def generate_report(')
end_idx = orig.find('def plot_zernike_map_with_thumbnail_style(', start_idx)
if end_idx == -1:
    end_idx = orig.find('def ', start_idx + 10)
    
orig_func = orig[start_idx:end_idx]

# Extract generate_report from content
start_idx2 = content.find('def generate_report(')
end_idx2 = content.find('def make_mode_map_image(', start_idx2)
if end_idx2 == -1:
    end_idx2 = len(content)

# Replace the broken function with the original one
new_content = content[:start_idx2] + orig_func + content[end_idx2:]

# Now apply the user's color changes and fixes
# 1. mtf_1d plot to red: 'b-' -> 'r-'
new_content = new_content.replace('ax40.plot(freq_cpd, mtf_x, lw=2)', "ax40.plot(freq_cpd, mtf_x, 'r-', lw=2)")

# 2. Fix Piston (Z0,0) to be green in thumbnails
thumb_fix = """
    # 瞳孔内を正規化する
    if mode == (0, 0):
        # Piston is constant, make it 0 (Green)
        norm = np.where(pupil, 0.0, np.nan)
    else:
        norm = np.where(pupil, W / vmax, np.nan)
"""
new_content = new_content.replace('    norm = np.where(pupil, W / vmax, np.nan)', thumb_fix.strip())

# 3. Fix Piston to be green in the report mode map
report_fix = """
    # Wavefront表示用配列を作る (Pistonを引いて平均を緑にする)
    mean_total = np.mean(W_total[pupil_total]) if np.any(pupil_total) else 0.0
    W_total_plot = np.where(pupil_total, W_total - mean_total, np.nan)
    
    mean_lower = np.mean(W_lower[pupil_lower]) if np.any(pupil_lower) else 0.0
    W_lower_plot = np.where(pupil_lower, W_lower - mean_lower, np.nan)
    
    mean_higher = np.mean(W_higher[pupil_higher]) if np.any(pupil_higher) else 0.0
    W_higher_plot = np.where(pupil_higher, W_higher - mean_higher, np.nan)
"""
new_content = new_content.replace(
    '    W_total_plot = np.where(pupil_total, W_total, np.nan)\n'
    '    W_lower_plot = np.where(pupil_lower, W_lower, np.nan)\n'
    '    W_higher_plot = np.where(pupil_higher, W_higher, np.nan)', 
    report_fix.strip()
)

with open('backend/simulator.py', 'w') as f:
    f.write(new_content)
print("Repaired!")
