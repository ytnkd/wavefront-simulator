# matplotlibをColabで安定して表示するためにinlineモードへ設定する
import matplotlib
matplotlib.use("Agg")
import base64

# 数値計算のためにNumPyを読み込む
import numpy as np

# グラフ描画のためにmatplotlibを読み込む
import matplotlib.pyplot as plt

# 円や矢印を描くための部品を読み込む
from matplotlib.patches import Circle, FancyArrowPatch

# 7色カラーマップを作るためにLinearSegmentedColormapを読み込む
from matplotlib.colors import LinearSegmentedColormap

# 文字に縁取りを付けるためにpath effectsを読み込む
import matplotlib.patheffects as pe

# 階乗計算のためにfactorialを読み込む
from math import factorial

# 高速畳み込みのためにfftconvolveを読み込む
from scipy.signal import fftconvolve

# UI作成のためにipywidgetsを読み込む
import ipywidgets as widgets

# UI表示と出力クリアのためにdisplayとclear_outputを読み込む
from IPython.display import display, clear_output

# 画像をメモリ上で扱うためにioを読み込む
import io

# RGBA画像をPNGに変換するためにPILのImageを読み込む
from PIL import Image

# 3Dグラフ描画のためにAxes3Dを読み込む
from mpl_toolkits.mplot3d import Axes3D

# 分数表示を作るためにFractionを読み込む
from fractions import Fraction


# Colabでipywidgetsを使いやすくするための処理を試す
try:
    # Colab専用の出力機能を読み込む
    from google.colab import output

    # Colabでカスタムwidgetを有効にする
    output.enable_custom_widget_manager()

# Colab以外では何もしない
except Exception:
    # エラーを無視する
    pass


# Matplotlibのフォントを英語用に設定する
plt.rcParams["font.family"] = "sans-serif"

# 英語フォント候補を設定する
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Liberation Sans"]

# マイナス記号の文字化けを防ぐ
plt.rcParams["axes.unicode_minus"] = False

# 数式フォントを見やすく設定する
plt.rcParams["mathtext.fontset"] = "stix"

# 数式の標準体裁を設定する
plt.rcParams["mathtext.default"] = "regular"


# ZernikeラベルをASCII形式で返す関数を定義する
def z_label(n, m):
    # 文字化けしないZernike表記を返す
    return f"Z({int(n)},{int(m)})"


# Zernikeラベルを数式風に返す関数を定義する
def z_label_math(n, m):
    # 数式風Zernike表記を返す
    return rf"$Z_{{{int(n)}}}^{{{int(m)}}}$"


# 波面表示の色ルール説明を返す関数を定義する
def wavefront_color_note():
    # 波面が進んでいるところを暖色、遅れているところを寒色と説明する
    return "Red to dark blue = advanced to delayed wavefront"


# 波面表示用7色カラーマップ名を返す関数を定義する
def get_wavefront_cmap_name():
    # 7色カラーマップの説明名を返す
    return "custom 7-color map"


# 波面表示用7色カラーマップを返す関数を定義する
def get_wavefront_cmap():
    # 低値から高値へ並ぶ7色を定義する
    colors = [
        "#D7191C",  # red
        "#F39C12",  # orange
        "#F4E04D",  # yellow
        "#2ECC71",  # green
        "#4FC3F7",  # light blue
        "#0050FF",  # blue
        "#08306B",  # dark blue
    ]

    # 7色カラーマップを返す
    return LinearSegmentedColormap.from_list("wavefront7", colors, N=256)


# Zernikeモード行を作る関数を定義する
def build_mode_rows(n_max=6):
    # 行リストを作る
    rows = []

    # nを0からn_maxまで順番に処理する
    for n in range(n_max + 1):
        # その次数のモード行を作る
        row = []

        # mを-nからnまで2刻みで作る
        for m in range(-n, n + 1, 2):
            # モードを行へ追加する
            row.append((n, m))

        # 行をリストへ追加する
        rows.append(row)

    # 行リストを返す
    return rows


# 添付図に近いj番号対応表を作る関数を定義する
def build_j_map():
    # j番号辞書を返す
    return {
        (0, 0): 1,
        (1, 1): 2,
        (1, -1): 3,
        (2, 0): 4,
        (2, 2): 5,
        (2, -2): 6,
        (3, 1): 7,
        (3, -1): 8,
        (4, 0): 9,
        (3, 3): 10,
        (3, -3): 11,
        (4, 2): 12,
        (4, -2): 13,
        (5, 1): 14,
        (5, -1): 15,
        (6, 0): 16,
        (4, 4): 17,
        (4, -4): 18,
        (5, 3): 19,
        (5, -3): 20,
        (6, 2): 21,
        (6, -2): 22,
        (5, 5): 26,
        (5, -5): 27,
        (6, 4): 28,
        (6, -4): 29,
        (6, 6): 37,
        (6, -6): 38,
    }


# 教育用の英語説明を作る関数を定義する
def build_mode_info():
    # モード説明辞書を返す
    return {
        (0, 0): "Piston: the whole wavefront shifts equally",
        (1, -1): "Tilt Y: image moves up or down",
        (1, 1): "Tilt X: image moves left or right",
        (2, -2): "Astigmatism 45 deg: blur along one diagonal axis",
        (2, 0): "Defocus: myopia-like or hyperopia-like blur",
        (2, 2): "Astigmatism 0/90 deg: blur along horizontal/vertical axis",
        (3, -3): "Trefoil: three-fold distortion",
        (3, -1): "Coma Y: comet-like vertical smear",
        (3, 1): "Coma X: comet-like horizontal smear",
        (3, 3): "Trefoil: three-fold distortion",
        (4, -4): "Tetrafoil: four-fold pattern",
        (4, -2): "Secondary astigmatism",
        (4, 0): "Spherical aberration: center and edge focus differently",
        (4, 2): "Secondary astigmatism",
        (4, 4): "Tetrafoil: four-fold pattern",
        (5, -5): "Pentafoil: five-fold pattern",
        (5, -3): "Secondary trefoil",
        (5, -1): "Fifth-order coma Y",
        (5, 1): "Fifth-order coma X",
        (5, 3): "Secondary trefoil",
        (5, 5): "Pentafoil: five-fold pattern",
        (6, -6): "Hexafoil: six-fold pattern",
        (6, -4): "Sixth-order tetrafoil",
        (6, -2): "Sixth-order astigmatism",
        (6, 0): "Secondary spherical aberration",
        (6, 2): "Sixth-order astigmatism",
        (6, 4): "Sixth-order tetrafoil",
        (6, 6): "Hexafoil: six-fold pattern",
    }


# プリセットを作る関数を定義する
def build_presets():
    # 教育用プリセット辞書を返す
    return {
        "No aberration": {},
        "Myopia": {(2, 0): -1.5},
        "Hyperopia": {(2, 0): 1.5},
        "Nuclear cataract": {(4, 0): 0.8},
        "Cortical cataract": {(4, 0): -0.8},
        "Astigmatism": {(2, 2): 1.0},
        "Keratoconus": {(3, -1): +0.65, (2, 2): +0.30, (4, 0): +0.10},
        "Post-LASIK": {(4, 0): +0.40, (3, 1): +0.15},
        "Double vision": {(3, 1): +0.70, (2, 0): +0.15},
        "Triple vision": {(3, 3): +0.45, (4, 0): +0.22},
        "Sixth-order example": {(6, 0): +0.18, (6, 2): +0.14, (6, 6): +0.16},
    }


# モードごとの初期値を返す関数を定義する
def default_value_for_mode(mode):
    # nとmを取り出す
    n, m = mode

    # Defocusの初期値を返す
    if (n, m) == (2, 0):
        return 0.30

    # Spherical aberrationの初期値を返す
    if (n, m) == (4, 0):
        return 0.20

    # Secondary spherical aberrationの初期値を返す
    if (n, m) == (6, 0):
        return 0.18

    # Comaの初期値を返す
    if (n, m) in [(3, -1), (3, 1), (5, -1), (5, 1)]:
        return 0.30

    # Trefoilの初期値を返す
    if (n, m) in [(3, -3), (3, 3), (5, -3), (5, 3)]:
        return 0.35

    # その他の初期値を返す
    return 0.20


# 瞳孔座標を作る関数を定義する
def make_pupil_coordinates(N=512, pad_factor=2):
    # 正規化座標を作る
    coords = np.linspace(-pad_factor, pad_factor, N)

    # 2次元座標を作る
    xx, yy = np.meshgrid(coords, coords)

    # 半径rhoを計算する
    rho = np.sqrt(xx**2 + yy**2)

    # 角度thetaを計算する
    theta = np.arctan2(yy, xx)

    # 瞳孔内マスクを作る
    pupil = rho <= 1.0

    # rhoを1以下へ丸める
    rho_clipped = np.clip(rho, 0.0, 1.0)

    # 座標を返す
    return xx, yy, rho_clipped, theta, pupil


# Zernike動径多項式を計算する関数を定義する
def zernike_radial(n, m, rho):
    # mの絶対値を取得する
    m_abs = abs(int(m))

    # nを整数にする
    n = int(n)

    # 偶奇条件を満たさない場合は0を返す
    if (n - m_abs) % 2 != 0:
        return np.zeros_like(rho)

    # 動径成分を0で初期化する
    R = np.zeros_like(rho, dtype=float)

    # 最大sを計算する
    max_s = (n - m_abs) // 2

    # sを順番に処理する
    for s in range(max_s + 1):
        # 係数を計算する
        c = ((-1) ** s) * factorial(n - s) / (
            factorial(s)
            * factorial((n + m_abs) // 2 - s)
            * factorial((n - m_abs) // 2 - s)
        )

        # 動径成分へ加算する
        R = R + c * rho ** (n - 2 * s)

    # 動径成分を返す
    return R


# 正規化Zernikeモードを計算する関数を定義する
def zernike_mode(n, m, rho, theta):
    # nを整数にする
    n = int(n)

    # mを整数にする
    m = int(m)

    # 動径成分を計算する
    R = zernike_radial(n, m, rho)

    # mが正ならcos型を返す
    if m > 0:
        return np.sqrt(2 * (n + 1)) * R * np.cos(m * theta)

    # mが負ならsin型を返す
    if m < 0:
        return np.sqrt(2 * (n + 1)) * R * np.sin(abs(m) * theta)

    # mが0なら円対称型を返す
    return np.sqrt(n + 1) * R


# Zernike係数から波面収差を作る関数を定義する
def make_wavefront(coeffs, N=512, pad_factor=2):
    # 瞳孔座標を作る
    xx, yy, rho, theta, pupil = make_pupil_coordinates(N=N, pad_factor=pad_factor)

    # 波面を0で初期化する
    W = np.zeros((N, N), dtype=float)

    # 各Zernike成分を加算する
    for (n, m), value in coeffs.items():
        W = W + value * zernike_mode(n, m, rho, theta)

    # 瞳孔外を0にする
    W[~pupil] = 0.0

    # 波面と瞳孔を返す
    return W, pupil


# 指定次数範囲の係数を抽出する関数を定義する
def extract_coeffs_by_order(coeffs, min_order=None, max_order=None):
    # 出力辞書を作る
    out = {}

    # 各モードを確認する
    for (n, m), value in coeffs.items():
        # 最小次数条件を判定する
        if min_order is not None and n < min_order:
            continue

        # 最大次数条件を判定する
        if max_order is not None and n > max_order:
            continue

        # 条件を満たす係数を保存する
        out[(n, m)] = value

    # 抽出結果を返す
    return out


# 分数をASCIIに変換する関数を定義する
def fraction_to_ascii(frac):
    # 分母が1なら整数を返す
    if frac.denominator == 1:
        return str(frac.numerator)

    # 分数文字列を返す
    return f"{frac.numerator}/{frac.denominator}"


# rhoのべき乗を文字列へ変換する関数を定義する
def rho_power_to_ascii(power):
    # 0乗なら1を返す
    if power == 0:
        return "1"

    # 1乗ならrhoを返す
    if power == 1:
        return "rho"

    # 2乗以上ならrho^nを返す
    return f"rho^{power}"


# 動径多項式の式を文字列で返す関数を定義する
def radial_formula_ascii(n, m):
    # nを整数にする
    n = int(n)

    # |m|を取得する
    m_abs = abs(int(m))

    # 偶奇条件を満たさない場合は0を返す
    if (n - m_abs) % 2 != 0:
        return "0"

    # 項リストを作る
    terms = []

    # 最大sを計算する
    max_s = (n - m_abs) // 2

    # sを順番に処理する
    for s in range(max_s + 1):
        # 分子を計算する
        numerator = ((-1) ** s) * factorial(n - s)

        # 分母を計算する
        denominator = (
            factorial(s)
            * factorial((n + m_abs) // 2 - s)
            * factorial((n - m_abs) // 2 - s)
        )

        # 分数係数を作る
        coeff = Fraction(numerator, denominator)

        # rhoの次数を計算する
        power = n - 2 * s

        # rho部分を文字列化する
        rho_part = rho_power_to_ascii(power)

        # 符号を決める
        sign = "-" if coeff < 0 else "+"

        # 絶対値を取る
        abs_coeff = abs(coeff)

        # 係数文字列を作る
        coeff_text = fraction_to_ascii(abs_coeff)

        # 定数項の場合
        if rho_part == "1":
            term_core = coeff_text
        elif abs_coeff == 1:
            term_core = rho_part
        else:
            term_core = f"{coeff_text}*{rho_part}"

        # 項を追加する
        terms.append((sign, term_core))

    # 項が空なら0を返す
    if len(terms) == 0:
        return "0"

    # 式文字列を作る
    formula = ""

    # 項を結合する
    for i, (sign, core) in enumerate(terms):
        if i == 0 and sign == "+":
            formula += core
        elif i == 0 and sign == "-":
            formula += f"-{core}"
        else:
            formula += f" {sign} {core}"

    # 式を返す
    return formula


# Zernike式を文字列で返す関数を定義する
def zernike_formula_ascii(n, m):
    # nを整数にする
    n = int(n)

    # mを整数にする
    m = int(m)

    # 動径多項式を作る
    R_text = radial_formula_ascii(n, abs(m))

    # mが正ならcos型の式を返す
    if m > 0:
        return f"{z_label(n, m)}(rho,theta) = sqrt({2 * (n + 1)}) * ({R_text}) * cos({m}*theta)"

    # mが負ならsin型の式を返す
    if m < 0:
        return f"{z_label(n, m)}(rho,theta) = sqrt({2 * (n + 1)}) * ({R_text}) * sin({abs(m)}*theta)"

    # m=0なら円対称型を返す
    return f"{z_label(n, m)}(rho,theta) = sqrt({n + 1}) * ({R_text})"


# 選択した式一覧を返す関数を定義する
def selected_formula_lines(coeffs, j_map=None, max_modes=None):
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
            "n": n,
            "label": z_label(n, m),
            "coeff": value,
            "formula_z": zernike_formula_ascii(n, m)
        })
    return result



# 瞳孔関数を作る関数を定義する
def make_pupil_function(coeffs, pupil_mm=5.0, wavelength_nm=555, N=512, pad_factor=2):
    # 波面を作る
    W, pupil = make_wavefront(coeffs, N=N, pad_factor=pad_factor)

    # 波長をumへ変換する
    wavelength_um = wavelength_nm / 1000.0

    # 位相を計算する
    phase = 2.0 * np.pi * W / wavelength_um

    # 複素瞳関数を作る
    pupil_function = pupil.astype(float) * np.exp(1j * phase)

    # 1ピクセルあたりのradを計算する
    rad_per_px = (wavelength_nm * 1e-9) / (pupil_mm * 1e-3 * pad_factor)

    # arcminへ変換する
    arcmin_per_px = np.degrees(rad_per_px) * 60.0

    # 結果を返す
    return pupil_function, W, pupil, phase, arcmin_per_px


# PSFを計算する関数を定義する
def make_psf(coeffs, pupil_mm=5.0, wavelength_nm=555, N=512, pad_factor=2):
    # 瞳孔関数を作る
    pupil_function, W, pupil, phase, arcmin_per_px = make_pupil_function(
        coeffs=coeffs,
        pupil_mm=pupil_mm,
        wavelength_nm=wavelength_nm,
        N=N,
        pad_factor=pad_factor,
    )

    # フーリエ変換を計算する
    field = np.fft.fftshift(np.fft.fft2(np.fft.ifftshift(pupil_function)))

    # PSFを計算する
    psf = np.abs(field) ** 2

    # PSFを正規化する
    psf = psf / np.sum(psf)

    # 結果を返す
    return psf, W, pupil, phase, pupil_function, arcmin_per_px


# ランドルト環を作る関数を定義する
def make_landolt_c(N=512, arcmin_per_px=0.1, diameter_arcmin=20.0, gap_direction_deg=0, contrast=1.0):
    # 白背景を作る
    img = np.ones((N, N), dtype=float)

    # x座標をarcmin単位で作る
    coords_x = (np.arange(N) - N / 2.0) * arcmin_per_px

    # y座標をarcmin単位で作る
    coords_y = (N / 2.0 - np.arange(N)) * arcmin_per_px

    # 2次元座標を作る
    xx, yy = np.meshgrid(coords_x, coords_y)

    # 半径を計算する
    rr = np.sqrt(xx**2 + yy**2)

    # 外半径を作る
    outer_radius = diameter_arcmin / 2.0

    # 線幅を作る
    stroke = diameter_arcmin / 5.0

    # 内半径を作る
    inner_radius = outer_radius - stroke

    # 円環マスクを作る
    ring_mask = (rr >= inner_radius) & (rr <= outer_radius)

    # 切れ目方向をradへ変換する
    phi = np.deg2rad(gap_direction_deg)

    # 切れ目方向座標を作る
    u = xx * np.cos(phi) + yy * np.sin(phi)

    # 切れ目直交座標を作る
    v = -xx * np.sin(phi) + yy * np.cos(phi)

    # 切れ目マスクを作る
    gap_mask = (u > 0) & (np.abs(v) <= stroke / 2.0) & (rr <= outer_radius)

    # 円環の切れ目以外を黒くする
    img[ring_mask & (~gap_mask)] = 1.0 - contrast

    # 画像を返す
    return img


# PSF中心を切り出す関数を定義する
def crop_psf(psf, arcmin_per_px, crop_radius_arcmin=60.0):
    # サイズを取得する
    N = psf.shape[0]

    # 中心を計算する
    c = N // 2

    # 切り出し半径をpxにする
    r = int(np.ceil(crop_radius_arcmin / arcmin_per_px))

    # 範囲外を避ける
    r = min(r, c - 1)

    # 中心を切り出す
    kernel = psf[c - r : c + r + 1, c - r : c + r + 1].copy()

    # 正規化する
    kernel = kernel / np.sum(kernel)

    # カーネルを返す
    return kernel


# PSFで画像をぼかす関数を定義する
def blur_image_with_psf(img, psf, arcmin_per_px, crop_radius_arcmin=60.0):
    # PSFカーネルを作る
    kernel = crop_psf(psf, arcmin_per_px, crop_radius_arcmin=crop_radius_arcmin)

    # 黒成分に変換する
    dark = 1.0 - img

    # 黒成分を畳み込む
    blurred_dark = fftconvolve(dark, kernel, mode="same")

    # 白背景に戻す
    blurred = 1.0 - blurred_dark

    # 0から1へ丸める
    blurred = np.clip(blurred, 0.0, 1.0)

    # ぼかし後画像を返す
    return blurred


# 波面RMSの詳細を計算する関数を定義する
def wavefront_rms_details(W, pupil, label="Wavefront"):
    # 瞳孔内の値を取り出す
    values = W[pupil]

    # 値が無ければ0を返す
    if values.size == 0:
        return {
            "label": label,
            "n_points": 0,
            "mean_before": 0.0,
            "mean_square": 0.0,
            "rms": 0.0,
            "formula": "RMS = sqrt(mean((W - mean(W))^2))",
        }

    # 平均値を計算する
    mean_before = float(np.mean(values))

    # ピストン成分を除く
    centered = values - mean_before

    # 二乗平均を計算する
    mean_square = float(np.mean(centered**2))

    # RMSを計算する
    rms = float(np.sqrt(mean_square))

    # 詳細を返す
    return {
        "label": label,
        "n_points": int(values.size),
        "mean_before": mean_before,
        "mean_square": mean_square,
        "rms": rms,
        "formula": "RMS = sqrt(mean((W - mean(W))^2))",
    }


# RMS説明行を作る関数を定義する
def build_rms_lines(total_info, lower_info, higher_info):
    # 行リストを作る
    lines = []

    # 見出しを追加する
    lines.append("RMS Calculation")
    lines.append("------------------------------")
    lines.append(total_info["formula"])
    lines.append("")

    # 各情報を順に追加する
    for info in [total_info, lower_info, higher_info]:
        lines.append(f"{info['label']}")
        lines.append(f"  Pupil points      : {info['n_points']}")
        lines.append(f"  Mean before cent. : {info['mean_before']:+.6f} um")
        lines.append(f"  Mean square       : {info['mean_square']:.6f} um^2")
        lines.append(f"  RMS               : {info['rms']:.3f} um")
        lines.append("")

    # 行を返す
    return lines


# ガウシアンスポットを描く関数を定義する
def draw_gaussian_spot(image, x0, y0, sigma_px=2.0, amplitude=1.0):
    # 描画半径を計算する
    radius = int(np.ceil(4.0 * sigma_px))

    # x最小を計算する
    x_min = max(0, int(np.floor(x0)) - radius)

    # x最大を計算する
    x_max = min(image.shape[1] - 1, int(np.floor(x0)) + radius)

    # y最小を計算する
    y_min = max(0, int(np.floor(y0)) - radius)

    # y最大を計算する
    y_max = min(image.shape[0] - 1, int(np.floor(y0)) + radius)

    # 範囲が不正なら戻る
    if x_max < x_min or y_max < y_min:
        return image

    # 局所座標を作る
    yy, xx = np.mgrid[y_min : y_max + 1, x_min : x_max + 1]

    # ガウシアンを作る
    spot = amplitude * np.exp(-((xx - x0) ** 2 + (yy - y0) ** 2) / (2.0 * sigma_px**2))

    # 画像へ加える
    image[y_min : y_max + 1, x_min : x_max + 1] += spot

    # 更新画像を返す
    return image


# 簡易Hartmann-Shack解析を作る関数を定義する
def make_hartmann_shack_analysis(coeffs, pupil_mm=5.0, N=512, pad_factor=2, lenslet_n=13, sensor_size=360, spot_sigma_px=2.2, spot_shift_gain=16000.0):
    # 波面を作る
    W, pupil = make_wavefront(coeffs, N=N, pad_factor=pad_factor)

    # 座標を作る
    xx, yy, rho, theta, pupil2 = make_pupil_coordinates(N=N, pad_factor=pad_factor)

    # 正規化座標の間隔を計算する
    step_norm = (2.0 * pad_factor) / (N - 1)

    # 波面勾配を計算する
    dW_dy_norm, dW_dx_norm = np.gradient(W, step_norm, step_norm)

    # 瞳孔半径をumへ変換する
    pupil_radius_um = (pupil_mm / 2.0) * 1000.0

    # x方向傾斜を計算する
    slope_x = dW_dx_norm / pupil_radius_um

    # y方向傾斜を計算する
    slope_y = dW_dy_norm / pupil_radius_um

    # 瞳孔外をNaNにする
    slope_x[~pupil] = np.nan
    slope_y[~pupil] = np.nan

    # 実スポット画像を0で初期化する
    sensor = np.zeros((sensor_size, sensor_size), dtype=float)

    # 参照スポット画像を0で初期化する
    reference = np.zeros((sensor_size, sensor_size), dtype=float)

    # 解析結果の記録リストを作る
    spot_records = []

    # レンズレット中心を作る
    centers_norm = np.linspace(-0.86, 0.86, lenslet_n)

    # レンズレット間隔を計算する
    cell_pitch_norm = centers_norm[1] - centers_norm[0] if lenslet_n > 1 else 2.0

    # センサー余白を設定する
    margin_px = 36

    # センサー上のスポット位置を作る
    centers_sensor = np.linspace(margin_px, sensor_size - margin_px, lenslet_n)

    # y方向に回す
    for iy, cy in enumerate(centers_norm):
        # x方向に回す
        for ix, cx in enumerate(centers_norm):
            # 瞳孔外ならスキップする
            if cx**2 + cy**2 > 0.95**2:
                continue

            # レンズレット領域を作る
            cell_mask = pupil & (np.abs(xx - cx) <= cell_pitch_norm / 2.0) & (np.abs(yy - cy) <= cell_pitch_norm / 2.0)

            # 有効画素が少なければスキップする
            if np.count_nonzero(cell_mask) < 5:
                continue

            # x方向平均傾斜を求める
            mean_sx = float(np.nanmean(slope_x[cell_mask]))

            # y方向平均傾斜を求める
            mean_sy = float(np.nanmean(slope_y[cell_mask]))

            # 基準x位置を決める
            x_ref = centers_sensor[ix]

            # 基準y位置を決める
            y_ref = centers_sensor[lenslet_n - 1 - iy]

            # x方向移動量を計算する
            dx = spot_shift_gain * mean_sx

            # y方向移動量を計算する
            dy = -spot_shift_gain * mean_sy

            # 実スポットxを作る
            x_spot = x_ref + dx

            # 実スポットyを作る
            y_spot = y_ref + dy

            # 参照スポットを描く
            reference = draw_gaussian_spot(reference, x_ref, y_ref, sigma_px=spot_sigma_px, amplitude=0.45)

            # 実スポットを描く
            sensor = draw_gaussian_spot(sensor, x_spot, y_spot, sigma_px=spot_sigma_px, amplitude=1.0)

            # 記録へ追加する
            spot_records.append({
                "x_ref": x_ref,
                "y_ref": y_ref,
                "dx": dx,
                "dy": dy,
                "x_spot": x_spot,
                "y_spot": y_spot,
                "mean_sx": mean_sx,
                "mean_sy": mean_sy,
            })

    # 参照スポットを正規化する
    if reference.max() > 0:
        reference = reference / reference.max()

    # 実スポットを正規化する
    if sensor.max() > 0:
        sensor = sensor / sensor.max()

    # 画像と解析結果を返す
    return sensor, reference, spot_records


# MTFを計算する関数を定義する
def compute_mtf(psf, arcmin_per_px):
    # OTFを計算する
    otf = np.fft.fftshift(np.fft.fft2(np.fft.ifftshift(psf)))

    # MTFを求める
    mtf2d = np.abs(otf)

    # MTFを正規化する
    mtf2d = mtf2d / np.max(mtf2d)

    # 中心を取得する
    c = mtf2d.shape[0] // 2

    # x方向断面を取る
    mtf_x = mtf2d[c, c:]

    # 周波数軸を作る
    freq_full = np.fft.fftshift(np.fft.fftfreq(psf.shape[1], d=arcmin_per_px / 60.0))

    # 正の周波数軸を作る
    freq_cpd = freq_full[c:]

    # 周波数軸とMTFを返す
    return freq_cpd, mtf_x, otf, mtf2d, freq_full


# PSFの水平断面を作る関数を定義する
def compute_psf_profile(psf, arcmin_per_px):
    # 中心を取得する
    c = psf.shape[0] // 2

    # x軸をarcminで作る
    x_arcmin = (np.arange(psf.shape[1]) - c) * arcmin_per_px

    # 水平断面を取得する
    profile = psf[c, :].copy()

    # 最大値で正規化する
    if np.max(profile) > 0:
        profile = profile / np.max(profile)

    # 結果を返す
    return x_arcmin, profile


# 中心付近を切り出す関数を定義する
def crop_image_by_physical_limit(arr, step, limit):
    # 中心を取得する
    c = arr.shape[0] // 2

    # 切り出し半径を計算する
    r = int(np.ceil(limit / step))

    # 範囲外を防ぐ
    r = min(r, c - 1)

    # 配列を切り出す
    cropped = arr[c - r : c + r + 1, c - r : c + r + 1]

    # 軸を作る
    axis_values = (np.arange(-r, r + 1)) * step

    # 切り出し結果を返す
    return cropped, axis_values


# 周波数軸で2次元配列を切り出す関数を定義する
def crop_2d_by_frequency_limit(arr, freq_axis, limit):
    # 指定周波数内のマスクを作る
    mask = np.abs(freq_axis) <= limit

    # 切り出し配列を作る
    cropped = arr[np.ix_(mask, mask)]

    # 切り出し軸を作る
    cropped_axis = freq_axis[mask]

    # 結果を返す
    return cropped, cropped_axis


# 3Dサーフェスを描く関数を定義する
def plot_surface_3d(ax, x_values, y_values, z_values, title, xlabel, ylabel, zlabel, elev=28, azim=-60, color=None):
    # 2次元格子を作る
    xx, yy = np.meshgrid(x_values, y_values)

    # サーフェスを描く
    ax.plot_surface(xx, yy, z_values, rstride=1, cstride=1, linewidth=0, antialiased=True, color=color)

    # タイトルを設定する
    ax.set_title(title)

    # 軸ラベルを設定する
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_zlabel(zlabel)

    # 視点を設定する
    ax.view_init(elev=elev, azim=azim)


# サムネイルを作る関数を定義する
def make_mode_thumbnail(mode, size=140, cmap=None):
    # カラーマップ未指定なら波面用を使う
    if cmap is None:
        cmap = get_wavefront_cmap()

    # nとmを取り出す
    n, m = mode

    # x座標を作る
    x = np.linspace(-1.0, 1.0, size)

    # y座標を作る
    y = np.linspace(-1.0, 1.0, size)

    # 2次元座標を作る
    xx, yy = np.meshgrid(x, y)

    # 半径を計算する
    rho = np.sqrt(xx**2 + yy**2)

    # 角度を計算する
    theta = np.arctan2(yy, xx)

    # 瞳孔マスクを作る
    pupil = rho <= 1.0

    # Zernikeを計算する
    Z = zernike_mode(n, m, np.clip(rho, 0.0, 1.0), theta)

    # 瞳孔外をNaNにする
    Z[~pupil] = np.nan

    # 最大絶対値を取得する
    vmax = max(np.nanmax(np.abs(Z)), 1e-12)

    # 0から1へ正規化する
    if n == 0 and m == 0:
        norm = np.full_like(Z, 0.5) # Force green (middle)
    else:
        norm = (Z + vmax) / (2.0 * vmax)

    # RGBA画像を作る
    rgba = cmap(np.nan_to_num(norm, nan=1.0))

    # 瞳孔外を透明にする
    rgba[~pupil, 3] = 0.0

    # RGBAを返す
    return rgba


# RGBA画像をPNGバイト列にする関数を定義する
def rgba_to_png_bytes(rgba):
    # 0から255の整数へ変換する
    arr = (np.clip(rgba, 0.0, 1.0) * 255).astype(np.uint8)

    # PIL画像にする
    img = Image.fromarray(arr, mode="RGBA")

    # バッファを作る
    buffer = io.BytesIO()

    # PNGとして保存する
    img.save(buffer, format="PNG")

    # PNGバイト列を返す
    return buffer.getvalue()


# 光路の説明図を描く関数を定義する
def draw_eye_light_step(ax, mode="input"):
    # 描画範囲を設定する
    ax.set_xlim(-3.6, 3.6)
    ax.set_ylim(-2.8, 2.8)
    ax.set_aspect("equal")
    ax.axis("off")

    # 眼球本体の塗りを描く
    eye_fill = Circle((0.3, 0.0), 2.0, facecolor="white", edgecolor="none", zorder=2)
    ax.add_patch(eye_fill)

    # 角膜様のふくらみを少し右へ移動して描く
    cornea = Circle((-1.45, 0.0), 0.85, facecolor="white", edgecolor="black", linewidth=2.0, zorder=3)
    ax.add_patch(cornea)

    # 黄斑の位置を示す点を少し右へ移動して描く
    macula_x = 2.18
    macula_y = 0.0
    ax.plot(macula_x, macula_y, marker="o", markersize=9, color="orange", zorder=4)
    ax.text(1.00, -1.95, "Reflection from macula", fontsize=9, color="darkorange")

    # 眼球本体の縁を最前面に描く
    eye_outline = Circle((0.3, 0.0), 2.0, facecolor="none", edgecolor="black", linewidth=2.0, zorder=6)
    ax.add_patch(eye_outline)

    # 測定光入力の場合の図を描く
    if mode == "input":
        ax.add_patch(FancyArrowPatch((-3.0, 0.0), (-1.9, 0.0), arrowstyle="-|>", mutation_scale=18, linewidth=3, color="green", zorder=5))
        ax.text(-3.15, 0.35, "Measurement light", fontsize=10, color="green")
        ax.text(-0.6, -2.25, "Input beam enters the eye", fontsize=10)

    # 反射戻り光の場合の図を描く
    if mode == "return":
        ax.add_patch(FancyArrowPatch((-1.9, 0.35), (1.75, 0.35), arrowstyle="-|>", mutation_scale=18, linewidth=3, color="green", zorder=5))
        ax.add_patch(FancyArrowPatch((1.75, -0.35), (-2.9, -0.35), arrowstyle="-|>", mutation_scale=18, linewidth=3, color="deepskyblue", zorder=5))
        ax.text(-2.95, 0.75, "Incident beam", fontsize=9, color="green")
        ax.text(-2.95, -0.95, "Returned reflected light", fontsize=9, color="deepskyblue")
        ax.text(-0.85, -2.25, "Retinal reflection returns", fontsize=10)


# 局所波面傾斜図を描く関数を定義する
def plot_local_slope_map(ax, spot_records, sensor_size=360):
    # 背景を黒にする
    ax.set_facecolor("black")

    # 記録がなければ終了する
    if len(spot_records) == 0:
        ax.text(0.5, 0.5, "No valid slope vectors", color="white", ha="center", va="center", transform=ax.transAxes)
        ax.set_xticks([])
        ax.set_yticks([])
        return

    # 参照点座標を作る
    x_ref = np.array([r["x_ref"] for r in spot_records])

    # 参照点座標を作る
    y_ref = np.array([r["y_ref"] for r in spot_records])

    # 矢印成分を作る
    dx = np.array([r["dx"] for r in spot_records])

    # 矢印成分を作る
    dy = np.array([r["dy"] for r in spot_records])

    # 参照点を描く
    ax.scatter(x_ref, y_ref, s=10, c="white")

    # 傾斜ベクトルを描く
    ax.quiver(x_ref, y_ref, dx, dy, angles="xy", scale_units="xy", scale=1, color="cyan", width=0.003)

    # タイトルを設定する
    ax.set_title("5. Local wavefront slope from spot shifts")

    # 軸ラベルを設定する
    ax.set_xlabel("sensor x [px]")
    ax.set_ylabel("sensor y [px]")

    # 範囲を設定する
    ax.set_xlim(0, sensor_size)
    ax.set_ylim(sensor_size, 0)


# 総合レポートを描く関数を定義する
def plot_wavefront_simulator_report(title, coeffs, pupil_mm=5.0, wavelength_nm=555, landolt_diameter_arcmin=20.0, gap_direction_deg=0, contrast=1.0, N=512, pad_factor=2, lenslet_n=13):
    # 波面カラーマップを作る
    wavefront_cmap = get_wavefront_cmap().copy()

    # NaNを透明にする
    wavefront_cmap.set_bad((1, 1, 1, 0))

    # Total PSFと波面を作る
    psf, W_total, pupil_total, phase_total, pupil_function, arcmin_per_px = make_psf(
        coeffs=coeffs,
        pupil_mm=pupil_mm,
        wavelength_nm=wavelength_nm,
        N=N,
        pad_factor=pad_factor,
    )

    # Lower order係数を抽出する
    lower_coeffs = extract_coeffs_by_order(coeffs, max_order=2)

    # Higher order係数を抽出する
    higher_coeffs = extract_coeffs_by_order(coeffs, min_order=3)

    # Lower order波面を作る
    W_lower, pupil_lower = make_wavefront(lower_coeffs, N=N, pad_factor=pad_factor)

    # Higher order波面を作る
    W_higher, pupil_higher = make_wavefront(higher_coeffs, N=N, pad_factor=pad_factor)

    # ランドルト環を作る
    landolt = make_landolt_c(
        N=N,
        arcmin_per_px=arcmin_per_px,
        diameter_arcmin=landolt_diameter_arcmin,
        gap_direction_deg=gap_direction_deg,
        contrast=contrast,
    )

    # ぼかし後ランドルト環を作る
    blurred = blur_image_with_psf(landolt, psf, arcmin_per_px=arcmin_per_px, crop_radius_arcmin=60.0)

    # Hartmann-Shack解析を作る
    hartmann_img, hartmann_ref, spot_records = make_hartmann_shack_analysis(
        coeffs=coeffs,
        pupil_mm=pupil_mm,
        N=N,
        pad_factor=pad_factor,
        lenslet_n=lenslet_n,
    )

    # MTFとOTFを計算する
    freq_cpd, mtf_x, otf, mtf2d, freq_full = compute_mtf(psf, arcmin_per_px)

    # PSF断面を計算する
    psf_x_arcmin, psf_profile = compute_psf_profile(psf, arcmin_per_px)

    # j番号辞書を作る
    j_map = build_j_map()

    # Total RMSを計算する
    total_info = wavefront_rms_details(W_total, pupil_total, label="Total")

    # Lower RMSを計算する
    lower_info = wavefront_rms_details(W_lower, pupil_lower, label="Lower order")

    # Higher RMSを計算する
    higher_info = wavefront_rms_details(W_higher, pupil_higher, label="Higher order")

    # RMS説明行を作る
    rms_lines = build_rms_lines(total_info, lower_info, higher_info)

    # Wavefront表示用配列を作る
# Wavefront表示用配列を作る (Pistonを引いて平均を緑にする)
    mean_total = np.mean(W_total[pupil_total]) if np.any(pupil_total) else 0.0
    W_total_plot = np.where(pupil_total, W_total - mean_total, np.nan)
    
    mean_lower = np.mean(W_lower[pupil_lower]) if np.any(pupil_lower) else 0.0
    W_lower_plot = np.where(pupil_lower, W_lower - mean_lower, np.nan)
    
    mean_higher = np.mean(W_higher[pupil_higher]) if np.any(pupil_higher) else 0.0
    W_higher_plot = np.where(pupil_higher, W_higher - mean_higher, np.nan)

    # 瞳孔関数の位相表示を作る
    pupil_function_phase = np.where(pupil_total, np.angle(pupil_function), np.nan)

    # 表示範囲を作る
    vmax_total = max(np.nanmax(np.abs(W_total_plot)), 1e-6)
    vmax_lower = max(np.nanmax(np.abs(W_lower_plot)), 1e-6)
    vmax_higher = max(np.nanmax(np.abs(W_higher_plot)), 1e-6)

    # PSF対数表示を作る
    psf_log = np.log10(psf / psf.max() + 1e-8)

    # OTF絶対値を正規化する
    otf_abs = np.abs(otf)
    otf_abs = otf_abs / np.max(otf_abs)
    otf_abs_log = np.log10(otf_abs + 1e-8)

    # arcmin表示範囲を作る
    extent_arcmin = [-(N / 2) * arcmin_per_px, (N / 2) * arcmin_per_px, -(N / 2) * arcmin_per_px, (N / 2) * arcmin_per_px]

    # PSF 3D用に中心付近を切り出す
    psf_crop, psf_axis_arcmin = crop_image_by_physical_limit(psf / psf.max(), arcmin_per_px, limit=20.0)

    # OTF表示用に周波数中心付近を切り出す
    otf_crop, otf_axis = crop_2d_by_frequency_limit(otf_abs_log, freq_full, limit=100.0)

    # MTF 3D用に周波数中心付近を切り出す
    mtf_crop, mtf_axis = crop_2d_by_frequency_limit(mtf2d, freq_full, limit=100.0)

    # 図を作る
    fig = plt.figure(figsize=(24, 28))
    gs = fig.add_gridspec(5, 4)

    # 全体タイトルを付ける
    fig.suptitle(title, fontsize=18)

    # 軸を作る
    ax00 = fig.add_subplot(gs[0, 0])
    ax01 = fig.add_subplot(gs[0, 1])
    ax02 = fig.add_subplot(gs[0, 2])
    ax03 = fig.add_subplot(gs[0, 3])
    ax10 = fig.add_subplot(gs[1, 0])
    ax11 = fig.add_subplot(gs[1, 1])
    ax12 = fig.add_subplot(gs[1, 2])
    ax13 = fig.add_subplot(gs[1, 3])
    ax20 = fig.add_subplot(gs[2, 0])
    ax21 = fig.add_subplot(gs[2, 1])
    ax22 = fig.add_subplot(gs[2, 2])
    ax23 = fig.add_subplot(gs[2, 3])
    ax30 = fig.add_subplot(gs[3, 0])
    ax31 = fig.add_subplot(gs[3, 1])
    ax32 = fig.add_subplot(gs[3, 2], projection="3d")
    ax33 = fig.add_subplot(gs[3, 3])
    ax40 = fig.add_subplot(gs[4, 0])
    ax41 = fig.add_subplot(gs[4, 1], projection="3d")
    ax42 = fig.add_subplot(gs[4, 2])
    ax43 = fig.add_subplot(gs[4, 3])

    # 1. 入射光説明を表示する
    draw_eye_light_step(ax00, mode="input")
    ax00.set_title("1. Input measurement light into the eye")

    # 2. 戻り光説明を表示する
    draw_eye_light_step(ax01, mode="return")
    ax01.set_title("2. Receive returned light reflected from retina")

    # 3. Hartmann referenceを表示する
    ax02.imshow(hartmann_ref, cmap="gray", vmin=0.0, vmax=1.0)
    ax02.set_title("3. Split light into many spots with Hartmann-Shack lenslets")
    ax02.set_xlabel("sensor x [px]")
    ax02.set_ylabel("sensor y [px]")

    # 4. Hartmann-Shack像を表示する
    ax03.imshow(hartmann_img, cmap="gray", vmin=0.0, vmax=1.0)
    ax03.set_title("4. Capture spot image with CCD / image sensor")
    ax03.set_xlabel("sensor x [px]")
    ax03.set_ylabel("sensor y [px]")

    # 5. 局所波面傾斜を表示する
    plot_local_slope_map(ax10, spot_records, sensor_size=hartmann_img.shape[0])

    # 6. 再構成波面を表示する
    im6 = ax11.imshow(W_total_plot, cmap=wavefront_cmap, vmin=-vmax_total, vmax=vmax_total)
    ax11.set_title("6. Reconstruct wavefront shape from local slopes")
    ax11.axis("off")
    cbar6 = plt.colorbar(im6, ax=ax11, fraction=0.046)
    cbar6.set_label("Wavefront [um]")

    # 7. Zernike分解説明を表示する
    ax12.axis("off")
    step7_lines = [
        "7. Decompose reconstructed wavefront",
        "   into Zernike polynomials",
        "",
        "Selected coefficients",
        "------------------------------",
    ]
    if len(coeffs) == 0:
        step7_lines.append("None")
    else:
        for mode in sorted(coeffs):
            n, m = mode
            j = j_map.get(mode, "-")
            step7_lines.append(f"j{j:>2} {z_label(n, m):>8} = {coeffs[mode]:+.2f} um")
    step7_lines.append("")
    step7_lines.append("Example formulae")
    step7_lines.append("------------------------------")
    step7_lines.extend(selected_formula_lines(coeffs, j_map=j_map, max_modes=2))
    ax12.text(0.0, 1.0, "\n".join(step7_lines), va="top", ha="left", family="monospace", fontsize=9)

    # RMS計算過程を表示する
    ax13.axis("off")
    ax13.text(0.0, 1.0, "\n".join(rms_lines), va="top", ha="left", family="monospace", fontsize=9)

    # 8a. Totalを表示する
    im8a = ax20.imshow(W_total_plot, cmap=wavefront_cmap, vmin=-vmax_total, vmax=vmax_total)
    ax20.set_title("8a. Wavefront map: Total")
    ax20.axis("off")
    cbar8a = plt.colorbar(im8a, ax=ax20, fraction=0.046)
    cbar8a.set_label("Advanced (+) / Delayed (-) [um]")

    # 8b. Lower orderを表示する
    im8b = ax21.imshow(W_lower_plot, cmap=wavefront_cmap, vmin=-vmax_lower, vmax=vmax_lower)
    ax21.set_title("8b. Wavefront map: Lower Order Aberration")
    ax21.axis("off")
    cbar8b = plt.colorbar(im8b, ax=ax21, fraction=0.046)
    cbar8b.set_label("Advanced (+) / Delayed (-) [um]")

    # 8c. Higher orderを表示する
    im8c = ax22.imshow(W_higher_plot, cmap=wavefront_cmap, vmin=-vmax_higher, vmax=vmax_higher)
    ax22.set_title("8c. Wavefront map: Higher Order Aberration")
    ax22.axis("off")
    cbar8c = plt.colorbar(im8c, ax=ax22, fraction=0.046)
    cbar8c.set_label("Advanced (+) / Delayed (-) [um]")

    # 9. 瞳孔関数を表示する
    im9 = ax23.imshow(pupil_function_phase, cmap="twilight", vmin=-np.pi, vmax=np.pi)
    ax23.set_title("9. Build the pupil function from pupil diameter, wavelength, and Zernike coefficients")
    ax23.axis("off")
    cbar9 = plt.colorbar(im9, ax=ax23, fraction=0.046)
    cbar9.set_label("Pupil function phase [rad]")

    # 10. PSFを表示する
    ax30.imshow(psf_log, cmap="gray", extent=extent_arcmin, origin="upper")
    ax30.set_title("10. Compute PSF by Fourier transform of pupil function")
    ax30.set_xlim(-20, 20)
    ax30.set_ylim(-20, 20)
    ax30.set_xlabel("arcmin")
    ax30.set_ylabel("arcmin")

    # 10b. PSF断面グラフを表示する
    ax31.plot(psf_x_arcmin, psf_profile, lw=2)
    ax31.set_title("10b. PSF horizontal profile")
    ax31.set_xlabel("arcmin")
    ax31.set_ylabel("Normalized intensity")
    ax31.set_xlim(-20, 20)
    ax31.grid(True, alpha=0.3)

    # 10c. PSF 3Dグラフを表示する
    plot_surface_3d(
        ax32,
        psf_axis_arcmin,
        psf_axis_arcmin,
        psf_crop,
        title="10c. PSF 3D surface",
        xlabel="arcmin",
        ylabel="arcmin",
        zlabel="Normalized intensity",
    )

    # 11. OTFを表示する
    ax33.imshow(otf_crop, cmap="gray", extent=[otf_axis[0], otf_axis[-1], otf_axis[0], otf_axis[-1]], origin="lower")
    ax33.set_title("11. OTF magnitude")
    ax33.set_xlabel("Spatial frequency x [cycles/deg]")
    ax33.set_ylabel("Spatial frequency y [cycles/deg]")
    ax33.set_xlim(-100, 100)
    ax33.set_ylim(-100, 100)

    # 11b. MTFを表示する
    ax40.plot(freq_cpd, mtf_x, 'r-', lw=2)
    ax40.set_title("11b. MTF from |OTF|")
    ax40.set_xlabel("Spatial frequency [cycles/deg]")
    ax40.set_ylabel("Modulation")
    ax40.set_ylim(0.0, 1.05)
    ax40.set_xlim(0.0, 100.0)
    ax40.grid(True, alpha=0.3)

    # 11c. MTF 3Dグラフを表示する
    plot_surface_3d(
        ax41,
        mtf_axis,
        mtf_axis,
        mtf_crop,
        title="11c. MTF 3D surface",
        xlabel="Spatial frequency x [cycles/deg]",
        ylabel="Spatial frequency y [cycles/deg]",
        zlabel="Modulation",
        color="red",
    )

    # 12. 元のランドルト環を表示する
    ax42.imshow(landolt, cmap="gray", vmin=0.0, vmax=1.0, extent=extent_arcmin, origin="upper")
    ax42.set_title("12. Convolve target image with PSF")
    ax42.set_xlim(-landolt_diameter_arcmin, landolt_diameter_arcmin)
    ax42.set_ylim(-landolt_diameter_arcmin, landolt_diameter_arcmin)
    ax42.set_xlabel("arcmin")
    ax42.set_ylabel("arcmin")

    # 13. シミュレーション後の網膜像を表示する
    ax43.imshow(blurred, cmap="gray", vmin=0.0, vmax=1.0, extent=extent_arcmin, origin="upper")
    ax43.set_title("13. Generate simulated Landolt C image")
    ax43.set_xlim(-landolt_diameter_arcmin, landolt_diameter_arcmin)
    ax43.set_ylim(-landolt_diameter_arcmin, landolt_diameter_arcmin)
    ax43.set_xlabel("arcmin")
    ax43.set_ylabel("arcmin")

    # レイアウトを整える
    plt.tight_layout(rect=[0.0, 0.0, 1.0, 0.97])

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
        "rms_higher": higher_info,
        "psf": psf,
        "arcmin_per_px": arcmin_per_px
    }


# 添付図風のWavefront Mode Mapを描く関数を定義する
def triangular_positions(n_max=6, dx=1.70, dy=1.55):
    # 座標辞書を作る
    pos = {}

    # nを順番に処理する
    for n in range(n_max + 1):
        # m一覧を作る
        m_list = list(range(-n, n + 1, 2))

        # xインデックスを作る
        x_index = np.arange(len(m_list)) - (len(m_list) - 1) / 2.0

        # y座標を作る
        y = (n_max - n) * dy

        # 各mを処理する
        for i, m in enumerate(m_list):
            # x座標を作る
            x = x_index[i] * dx

            # 辞書へ保存する
            pos[(n, m)] = (x, y)

    # 座標辞書を返す
    return pos


# 添付図風のWavefront Mode Mapを描く関数を定義する
def plot_wavefront_mode_map(coeffs, n_max=6, show_all=True, show_coeff_value=True, mode_size=240):
    # カラーマップを作る
    cmap = get_wavefront_cmap().copy()

    # NaNを透明にする
    cmap.set_bad((1, 1, 1, 0))

    # 三角配置座標を作る
    pos = triangular_positions(n_max=n_max, dx=1.70, dy=1.55)

    # 背景色を決める
    bg_color = "#e8e8e8"

    # 図を作る
    fig, ax = plt.subplots(figsize=(13, 13))

    # 背景色を設定する
    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)

    # 全モードリストを作る
    all_modes = []
    for n in range(n_max + 1):
        for m in range(-n, n + 1, 2):
            all_modes.append((n, m))

    # 表示対象を決める
    if show_all:
        modes_to_draw = all_modes
    else:
        modes_to_draw = sorted(coeffs.keys())

    # 表示対象がなければメッセージを出す
    if len(modes_to_draw) == 0:
        ax.text(0.5, 0.5, "No Zernike mode selected", ha="center", va="center", fontsize=18, transform=ax.transAxes)
        ax.axis("off")
        plt.show()
        return

    # 各モードを描く
    for mode in modes_to_draw:
        n, m = mode
        cx, cy = pos[(n, m)]
        selected = mode in coeffs

        # 選択中なら係数つき画像を作る
        if selected:
            coeff = coeffs[mode]
            Zimg = zernike_mode(n, m, *make_pupil_coordinates(N=mode_size, pad_factor=1)[2:4])
            Zimg = coeff * Zimg
        else:
            Zimg = zernike_mode(n, m, *make_pupil_coordinates(N=mode_size, pad_factor=1)[2:4])

        # 円外をNaNにするためのマスクを作る
        _, _, rho_tmp, theta_tmp, pupil_tmp = make_pupil_coordinates(N=mode_size, pad_factor=1)
        Zimg[~pupil_tmp] = np.nan
        if n == 0 and m == 0:
            Zimg[pupil_tmp] = 0.0

        # 表示スケールを決める
        vmax = max(np.nanmax(np.abs(Zimg)), 1e-9)

        # 円半径を決める
        r = 0.60

        # 表示範囲を決める
        extent = [cx - r, cx + r, cy - r, cy + r]

        # 濃さを決める
        alpha_value = 1.0 if selected else 0.28

        # 画像を表示する
        ax.imshow(
            np.ma.masked_invalid(Zimg),
            cmap=cmap,
            vmin=-vmax,
            vmax=vmax,
            extent=extent,
            origin="lower",
            interpolation="bilinear",
            alpha=alpha_value,
            zorder=2,
        )

        # 外枠色を決める
        edge_color = "black" if selected else "#888888"

        # 外枠太さを決める
        line_width = 2.2 if selected else 1.0

        # 円枠を描く
        circle = Circle((cx, cy), r, facecolor="none", edgecolor=edge_color, linewidth=line_width, zorder=3)
        ax.add_patch(circle)

        # j番号を取得する
        j = build_j_map().get(mode, "-")

        # 数式ラベルを作る
        label = z_label_math(n, m)

        # 数式ラベルを描く
        ax.text(
            cx + 0.16,
            cy - 0.47,
            label,
            fontsize=25,
            color="white",
            ha="left",
            va="center",
            zorder=4,
            path_effects=[pe.withStroke(linewidth=2.4, foreground="black")],
        )

        # 選択中なら係数を表示する
        if selected and show_coeff_value:
            coeff_text = f"{coeffs[mode]:+.2f} um"
            ax.text(cx, cy - 0.88, coeff_text, fontsize=10, color="black", ha="center", va="center", zorder=4)

        # j番号を描く
        ax.text(cx, cy + 0.84, f"j={j}", fontsize=10, color="black", ha="center", va="center", zorder=4)

    # x座標リストを作る
    xs = [p[0] for p in pos.values()]

    # y座標リストを作る
    ys = [p[1] for p in pos.values()]

    # タイトルを付ける
    ax.set_title("Wavefront Mode Map (up to 6th order)", fontsize=20, pad=18)

    # 色の意味を注記する
    ax.text(0.02, 0.98, wavefront_color_note(), transform=ax.transAxes, ha="left", va="top", fontsize=12)

    # x範囲を設定する
    ax.set_xlim(min(xs) - 1.3, max(xs) + 1.3)

    # y範囲を設定する
    ax.set_ylim(min(ys) - 1.4, max(ys) + 1.2)

    # 軸を消す
    ax.axis("off")

    # レイアウトを整える
    plt.tight_layout()

    # 図を保存して返す
    import io
    import base64
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", transparent=True)
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


# 教育用アプリクラスを定義する
class ZernikeTeachingApp:
    # 初期化関数を定義する
    def __init__(self, n_max=6):
        # 最大次数を保存する
        self.n_max = n_max

        # モード行を作る
        self.mode_rows = build_mode_rows(n_max=self.n_max)

        # j番号辞書を作る
        self.j_map = build_j_map()

        # 説明辞書を作る
        self.mode_info = build_mode_info()

        # プリセット辞書を作る
        self.presets = build_presets()

        # 選択中モード集合を作る
        self.selected_modes = set()

        # スライダー辞書を作る
        self.slider_dict = {}

        # ボタン辞書を作る
        self.button_dict = {}

        # 更新中フラグを作る
        self.updating_buttons = False

        # ウィジェットを作る
        self.build_widgets()

        # モードグリッドを作る
        self.mode_grid = self.build_mode_grid()

        # 選択表示を更新する
        self.refresh_selected_text()

        # スライダー欄を更新する
        self.refresh_sliders()

    # 基本ウィジェットを作る関数を定義する
    def build_widgets(self):
        # ヘッダーを作る
        self.header_html = widgets.HTML("<h3>Wavefront Simulator</h3>")

        # 説明文を作る
        self.help_html = widgets.HTML(
            "1) Click one or more Zernike modes or use the preset buttons.<br>"
            "2) Adjust coefficients with sliders.<br>"
            "3) Click <b>Run Simulation</b> to see the 13-step process from Hartmann-Shack spots to simulated Landolt C.<br>"
            "4) Wavefront maps are shown as Total, Lower Order Aberration, and Higher Order Aberration.<br>"
            f"5) Color map: {wavefront_color_note()}."
        )

        # 選択表示欄を作る
        self.selected_html = widgets.HTML("<b>Selected:</b> none")

        # スライダー欄を作る
        self.sliders_box = widgets.VBox([])

        # 瞳孔径スライダーを作る
        self.pupil_slider = widgets.FloatSlider(
            value=5.0,
            min=2.0,
            max=7.0,
            step=0.1,
            description="Pupil mm",
            continuous_update=False,
            layout=widgets.Layout(width="360px"),
        )

        # 波長スライダーを作る
        self.wavelength_slider = widgets.IntSlider(
            value=555,
            min=450,
            max=650,
            step=5,
            description="Wavelength",
            continuous_update=False,
            layout=widgets.Layout(width="360px"),
        )

        # ランドルト環サイズスライダーを作る
        self.landolt_size_slider = widgets.FloatSlider(
            value=20.0,
            min=5.0,
            max=60.0,
            step=1.0,
            description="Size arcmin",
            continuous_update=False,
            layout=widgets.Layout(width="360px"),
        )

        # コントラストスライダーを作る
        self.contrast_slider = widgets.FloatSlider(
            value=1.0,
            min=0.05,
            max=1.0,
            step=0.05,
            description="Contrast",
            continuous_update=False,
            layout=widgets.Layout(width="360px"),
        )

        # 切れ目方向ドロップダウンを作る
        self.gap_dropdown = widgets.Dropdown(
            options=[
                ("Right: 0 deg", 0),
                ("Up: 90 deg", 90),
                ("Left: 180 deg", 180),
                ("Down: 270 deg", 270),
            ],
            value=0,
            description="Gap",
            layout=widgets.Layout(width="220px"),
        )

        # 計算グリッドサイズ選択を作る
        self.N_dropdown = widgets.Dropdown(
            options=[256, 512, 768, 1024],
            value=512,
            description="Grid size",
            layout=widgets.Layout(width="220px"),
        )

        # Padding倍率スライダーを作る
        self.pad_factor_slider = widgets.IntSlider(
            value=2,
            min=2,
            max=4,
            step=1,
            description="Padding",
            continuous_update=False,
            layout=widgets.Layout(width="280px"),
        )

        # レンズレット数スライダーを作る
        self.lenslet_slider = widgets.IntSlider(
            value=13,
            min=7,
            max=21,
            step=2,
            description="Lenslets",
            continuous_update=False,
            layout=widgets.Layout(width="280px"),
        )

        # 実行ボタンを作る
        self.run_button = widgets.Button(
            description="Run Simulation",
            button_style="primary",
            layout=widgets.Layout(width="220px", height="46px"),
        )

        # クリアボタンを作る
        self.clear_button = widgets.Button(
            description="Clear Selection",
            button_style="danger",
            layout=widgets.Layout(width="180px"),
        )

        # 出力欄を作る
        self.output_area = widgets.Output()

        # 実行ボタンに処理を登録する
        self.run_button.on_click(self.run_simulation)

        # クリアボタンに処理を登録する
        self.clear_button.on_click(self.clear_selection)

        # プリセットボタン辞書を作る
        self.preset_buttons = {}

        # プリセット名を順番に処理する
        for name in self.presets.keys():
            btn = widgets.Button(
                description=name,
                button_style="info",
                layout=widgets.Layout(width="170px"),
            )
            btn.on_click(lambda b, name=name: self.apply_named_preset(name))
            self.preset_buttons[name] = btn

    # 1つのモードカードを作る関数を定義する
    def make_mode_card(self, mode):
        # nとmを取り出す
        n, m = mode

        # j番号を取得する
        j = self.j_map.get(mode, "-")

        # サムネイル画像を作る
        rgba = make_mode_thumbnail(mode, size=140, cmap=get_wavefront_cmap())

        # PNGバイト列に変換する
        png_bytes = rgba_to_png_bytes(rgba)

        # 画像ウィジェットを作る
        image_widget = widgets.Image(
            value=png_bytes,
            format="png",
            layout=widgets.Layout(width="84px", height="84px"),
        )

        # ボタン表示文字列を作る
        button_text = f"j={j} {z_label(n, m)}"

        # トグルボタンを作る
        button = widgets.ToggleButton(
            value=False,
            description=button_text,
            tooltip=self.mode_info.get(mode, ""),
            layout=widgets.Layout(width="126px", height="42px"),
        )

        # 変化時の処理を登録する
        button.observe(lambda change, mode=mode: self.on_mode_button_change(mode, change), names="value")

        # 辞書へ保存する
        self.button_dict[mode] = button

        # カードを作る
        card = widgets.VBox([image_widget, button], layout=widgets.Layout(align_items="center", width="132px"))

        # カードを返す
        return card

    # モードグリッドを作る関数を定義する
    def build_mode_grid(self):
        # 行ウィジェットリストを作る
        row_widgets = []

        # 各行を順番に作る
        for row in self.mode_rows:
            cards = [self.make_mode_card(mode) for mode in row]
            hbox = widgets.HBox(cards, layout=widgets.Layout(justify_content="center", width="1250px"))
            row_widgets.append(hbox)

        # 全体縦並びを作る
        grid = widgets.VBox(row_widgets)

        # グリッドを返す
        return grid

    # モードボタン変化時の処理を定義する
    def on_mode_button_change(self, mode, change):
        # 更新中なら何もしない
        if self.updating_buttons:
            return

        # ONなら選択集合へ追加する
        if change["new"]:
            self.selected_modes.add(mode)
        else:
            self.selected_modes.discard(mode)

        # スライダーが無ければ作る
        if mode not in self.slider_dict:
            self.slider_dict[mode] = self.make_mode_slider(mode)

        # ボタン色を更新する
        self.update_button_styles()

        # 選択表示を更新する
        self.refresh_selected_text()

        # スライダー欄を更新する
        self.refresh_sliders()

    # ボタン色を更新する関数を定義する
    def update_button_styles(self):
        # 全ボタンを順番に確認する
        for mode, button in self.button_dict.items():
            if mode in self.selected_modes:
                button.button_style = "success"
            else:
                button.button_style = ""

    # モードごとのスライダーを作る関数を定義する
    def make_mode_slider(self, mode, value=None):
        # 値が無ければ初期値を使う
        if value is None:
            value = default_value_for_mode(mode)

        # nとmを取り出す
        n, m = mode

        # j番号を取得する
        j = self.j_map.get(mode, "-")

        # ラベルを作る
        label = f"j{j} {z_label(n, m)}"

        # スライダーを作る
        slider = widgets.FloatSlider(
            value=value,
            min=-1.00,
            max=1.00,
            step=0.01,
            description=label,
            readout=True,
            readout_format="+.2f",
            continuous_update=False,
            layout=widgets.Layout(width="680px"),
        )

        # 値が変化したら表示を更新する
        slider.observe(lambda change: self.refresh_selected_text(), names="value")

        # スライダーを返す
        return slider

    # 選択表示を更新する関数を定義する
    def refresh_selected_text(self):
        # 選択が無い場合
        if len(self.selected_modes) == 0:
            self.selected_html.value = "<b>Selected:</b> none"
            return

        # 行リストを作る
        lines = []

        # 選択モードを順番に処理する
        for mode in sorted(self.selected_modes):
            n, m = mode
            j = self.j_map.get(mode, "-")
            value = self.slider_dict[mode].value
            info = self.mode_info.get(mode, "")
            lines.append(f"j{j} / {z_label(n, m)} : {value:+.2f} um | {info}")

        # HTMLを更新する
        self.selected_html.value = "<b>Selected:</b><br>" + "<br>".join(lines)

    # スライダー欄を更新する関数を定義する
    def refresh_sliders(self):
        # 子要素リストを作る
        children = []

        # 選択モードを順番に処理する
        for mode in sorted(self.selected_modes):
            if mode not in self.slider_dict:
                self.slider_dict[mode] = self.make_mode_slider(mode)
            n, m = mode
            j = self.j_map.get(mode, "-")
            info = self.mode_info.get(mode, "")
            html = widgets.HTML(f"<b>j{j} / {z_label(n, m)}</b>: {info}")
            one_box = widgets.VBox([html, self.slider_dict[mode]])
            children.append(one_box)

        # スライダー欄へ反映する
        self.sliders_box.children = tuple(children)

    # 現在の係数辞書を返す関数を定義する
    def current_coeffs(self):
        # 出力辞書を作る
        coeffs = {}

        # 選択モードを順番に処理する
        for mode in sorted(self.selected_modes):
            value = self.slider_dict[mode].value
            if abs(value) > 1e-12:
                coeffs[mode] = value

        # 辞書を返す
        return coeffs

    # 名前でプリセットを適用する関数を定義する
    def apply_named_preset(self, name):
        # プリセット係数を取得する
        preset_coeffs = self.presets[name]

        # 更新中フラグを立てる
        self.updating_buttons = True

        # 選択を空にする
        self.selected_modes.clear()

        # 全ボタンをOFFにする
        for button in self.button_dict.values():
            button.value = False

        # プリセット内容を順番に適用する
        for mode, value in preset_coeffs.items():
            self.selected_modes.add(mode)
            if mode not in self.slider_dict:
                self.slider_dict[mode] = self.make_mode_slider(mode, value=value)
            self.slider_dict[mode].value = value
            if mode in self.button_dict:
                self.button_dict[mode].value = True

        # 更新中フラグを下ろす
        self.updating_buttons = False

        # 表示を更新する
        self.update_button_styles()
        self.refresh_selected_text()
        self.refresh_sliders()

    # 選択をクリアする関数を定義する
    def clear_selection(self, _=None):
        # 更新中フラグを立てる
        self.updating_buttons = True

        # 選択を空にする
        self.selected_modes.clear()

        # 全ボタンをOFFにする
        for button in self.button_dict.values():
            button.value = False

        # 更新中フラグを下ろす
        self.updating_buttons = False

        # 表示を更新する
        self.update_button_styles()
        self.refresh_selected_text()
        self.refresh_sliders()

    # 処理手順の説明行を返す関数を定義する
    def process_lines(self):
        # 手順リストを返す
        return [
            "Process",
            "--------------------------------",
            "1. Input measurement light into the eye",
            "2. Receive returned light reflected from retina",
            "3. Split the light into many small spots with the Hartmann-Shack lenslet array",
            "4. Capture the spot image with a CCD / image sensor",
            "5. Calculate local wavefront slopes from spot displacements",
            "6. Reconstruct wavefront shape from local wavefront slopes",
            "7. Decompose the reconstructed wavefront into Zernike polynomials",
            "8. Create Total / Lower Order / Higher Order wavefront maps",
            "9. Build the pupil function from pupil diameter, wavelength, and Zernike coefficients",
            "10. Compute the PSF by Fourier transform of the pupil function",
            "11. Compute the OTF by Fourier transform of the PSF, then take |OTF| to obtain the MTF",
            "12. Convolve the target image with the PSF",
            "13. Generate the simulated image such as a Landolt C",
        ]

    # シミュレーション実行関数を定義する
    def run_simulation(self, _=None):
        # 現在の係数辞書を取得する
        coeffs = self.current_coeffs()

        # タイトルを作る
        title = "Wavefront Simulator"

        # 出力欄へ表示する
        with self.output_area:
            clear_output(wait=True)

            # 見出しを表示する
            print(title)
            print("=" * len(title))
            print("")

            # 手順を表示する
            for line in self.process_lines():
                print(line)
            print("")

            # 選択係数を表示する
            print("Selected Zernike coefficients")
            print("--------------------------------")
            print(f"Maximum order : {self.n_max}")
            print(f"Color map     : {get_wavefront_cmap_name()}")
            print(f"Color meaning : {wavefront_color_note()}")
            print("")
            if len(coeffs) == 0:
                print("None (diffraction-limited example)")
            else:
                for mode in sorted(coeffs):
                    n, m = mode
                    j = self.j_map.get(mode, "-")
                    value = coeffs[mode]
                    info = self.mode_info.get(mode, "")
                    print(f"j{j:>2} / {z_label(n, m)} = {value:+.2f} um | {info}")
            print("")

            # 計算式見出しを表示する
            print("Selected Zernike formulae")
            print("--------------------------------")
            for line in selected_formula_lines(coeffs, j_map=self.j_map, max_modes=None):
                print(line)
            print("")

            # メインレポートを表示する
            result = plot_wavefront_simulator_report(
                title=title,
                coeffs=coeffs,
                pupil_mm=self.pupil_slider.value,
                wavelength_nm=self.wavelength_slider.value,
                landolt_diameter_arcmin=self.landolt_size_slider.value,
                gap_direction_deg=self.gap_dropdown.value,
                contrast=self.contrast_slider.value,
                N=self.N_dropdown.value,
                pad_factor=self.pad_factor_slider.value,
                lenslet_n=self.lenslet_slider.value,
            )

            # RMS結果を表示する
            print("RMS summary")
            print("--------------------------------")
            print(f"Total RMS       : {result['rms_total']['rms']:.3f} um")
            print(f"Lower order RMS : {result['rms_lower']['rms']:.3f} um")
            print(f"Higher order RMS: {result['rms_higher']['rms']:.3f} um")
            print("")

            # Mode mapも表示する
            plot_wavefront_mode_map(
                coeffs=coeffs,
                n_max=self.n_max,
                show_all=True,
                show_coeff_value=True,
                mode_size=220,
            )

    # UI全体を表示する関数を定義する
    def show(self):
        # プリセット行を作る
        preset_row_1 = widgets.HBox([
            self.preset_buttons["No aberration"],
            self.preset_buttons["Hyperopia"],
            self.preset_buttons["Myopia"],
            self.preset_buttons["Astigmatism"],
        ])

        # プリセット行を作る
        preset_row_2 = widgets.HBox([
            self.preset_buttons["Keratoconus"],
            self.preset_buttons["Post-LASIK"],
            self.preset_buttons["Double vision"],
            self.preset_buttons["Triple vision"],
        ])

        # プリセット行を作る
        preset_row_3 = widgets.HBox([
            self.preset_buttons["Sixth-order example"],
            self.clear_button,
        ])

        # 設定1行目を作る
        settings_row_1 = widgets.HBox([self.pupil_slider, self.wavelength_slider])

        # 設定2行目を作る
        settings_row_2 = widgets.HBox([self.landolt_size_slider, self.contrast_slider])

        # 設定3行目を作る
        settings_row_3 = widgets.HBox([self.gap_dropdown, self.N_dropdown, self.pad_factor_slider, self.lenslet_slider])

        # UI全体を作る
        ui = widgets.VBox([
            self.header_html,
            self.help_html,
            widgets.HTML("<h4>Zernike Mode Selection (up to 6th order)</h4>"),
            self.mode_grid,
            widgets.HTML("<h4>Quick Presets</h4>"),
            preset_row_1,
            preset_row_2,
            preset_row_3,
            self.selected_html,
            self.sliders_box,
            widgets.HTML("<h4>Simulation Settings</h4>"),
            settings_row_1,
            settings_row_2,
            settings_row_3,
            self.run_button,
            self.output_area,
        ])

        # UIを表示する
        display(ui)


# 教育用アプリを作る
# app = ZernikeTeachingApp(n_max=6)

# 教育用アプリを表示する
# app.show()

# ====================================================
# Vision Simulation Code
# ====================================================
import os
from PIL import Image
import base64
import io

# Global cache for the 4 images
vision_simulation_images = []

def load_vision_images():
    global vision_simulation_images
    if len(vision_simulation_images) > 0:
        return
    
    # Path is relative to the backend directory, so go up one level
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_names = ["02.png", "03.png", "04.png", "05.png"]
    
    for fname in file_names:
        path = os.path.join(base_dir, fname)
        if os.path.exists(path):
            try:
                img = Image.open(path).convert('RGB')
                # Removed aggressive 400px resize to keep high quality
                arr = np.array(img, dtype=float) / 255.0
                vision_simulation_images.append(arr)
            except Exception as e:
                print(f"Error loading {fname}: {e}")

import scipy.ndimage

def get_vision_simulation_base64(psf, arcmin_per_px, crop_radius_arcmin=60.0):
    load_vision_images()
    kernel = crop_psf(psf, arcmin_per_px, crop_radius_arcmin=crop_radius_arcmin)
    
    # Scale kernel so it matches a realistic FOV (e.g. 20 degrees for a 1000px image)
    photo_arcmin_per_px = 1.2
    scale_factor = arcmin_per_px / photo_arcmin_per_px
    if scale_factor < 1.0:
        kernel = scipy.ndimage.zoom(kernel, scale_factor, order=1)
        k_sum = kernel.sum()
        if k_sum > 1e-9:
            kernel /= k_sum
        else:
            kernel = np.array([[1.0]])

    results = []
    for arr in vision_simulation_images:
        blurred = np.zeros_like(arr)
        for c in range(3):
            blurred[:, :, c] = fftconvolve(arr[:, :, c], kernel, mode="same")
        
        blurred = np.clip(blurred, 0.0, 1.0)
        img_out = Image.fromarray((blurred * 255).astype(np.uint8), mode='RGB')
        buf = io.BytesIO()
        img_out.save(buf, format="JPEG", quality=85)
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        results.append(b64)
    return results
