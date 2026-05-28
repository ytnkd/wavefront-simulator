import re

with open('backend/simulator.py', 'r') as f:
    content = f.read()

with open('01_Wavefront_simulator_code.txt', 'r') as f:
    orig = f.read()

start_idx_orig = orig.find('def plot_wavefront_simulator_report(')
end_idx_orig = orig.find('def plot_zernike_map_with_thumbnail_style', start_idx_orig)
orig_func = orig[start_idx_orig:end_idx_orig]

start_idx_curr = content.find('def plot_wavefront_simulator_report(')
end_idx_curr = content.find('def make_mode_map_image', start_idx_curr)
if end_idx_curr == -1: end_idx_curr = len(content)

new_content = content[:start_idx_curr] + orig_func + "\n" + content[end_idx_curr:]

new_content = new_content.replace("ax40.plot(freq_cpd, mtf_x, lw=2)", "ax40.plot(freq_cpd, mtf_x, 'r-', lw=2)")

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
print("Restored!")
