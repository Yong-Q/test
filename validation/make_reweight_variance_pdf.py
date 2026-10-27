#!/usr/bin/env python3
"""生成《重加权因子方差与 ESS》推导报告（中文 PDF）。

内容：重要性采样的权重、估计量方差、Kish ESS、权重二阶矩与累积量展开、
Gaussian 近似、广延性导致的指数衰减，以及本项目四组数据的数值量化。
"""
import json
import unicodedata
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.backends.backend_pdf import PdfPages

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
OUT = REPO / "docs" / "REWEIGHT_VARIANCE_DATA_2026-10-27.pdf"
FONT = Path("/workspace/group/shared/bza/.fonts/NotoSansSC.ttf")
if FONT.exists():
    font_manager.fontManager.addfont(str(FONT))
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Noto Sans SC", "DejaVu Sans"],
    "axes.unicode_minus": False,
    "font.size": 10,
    "savefig.dpi": 300,
})
PAGE = (8.5, 11)
GREY = "#4D4D4D"
BLUE = "#0072B2"
ORANGE = "#D55E00"


def cjk_wrap(text, width=96):
    lines, cur, w = [], "", 0
    for ch in text:
        cw = 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
        if w + cw > width and cur:
            lines.append(cur)
            cur, w = "", 0
        cur += ch
        w += cw
    if cur:
        lines.append(cur)
    return lines


def page_title(fig, title, y=0.95):
    fig.text(0.07, y, title, fontsize=15, fontweight="bold", ha="left")
    return y - 0.045


def para(fig, y, text, fontsize=9.2, width=96, leading=0.0185):
    for line in cjk_wrap(text, width):
        fig.text(0.07, y, line, fontsize=fontsize, ha="left")
        y -= leading
    return y - 0.010


def eq(fig, y, text, fontsize=11.5, x=0.12):
    fig.text(x, y, text, fontsize=fontsize, ha="left", color=BLUE)
    return y - 0.032


def head(fig, y, text):
    fig.text(0.07, y, text, fontsize=11, fontweight="bold", ha="left")
    return y - 0.026


# ---------------------------------------------------------------- data
def load():
    ess96 = json.loads((REPO / "validation/results/ess_student_2026-10-27/"
                        "ess_student_vs_polar.json").read_text())
    ess1152 = json.loads((REPO / "validation/results/ess_student_2026-10-27/"
                         "ess_student_1152.json").read_text())
    rows = [
        ("OFF23 → POLAR, 1,152 原子", 501, 13.76, 2.35, 0.596),
        ("学生 → POLAR, 1,152 原子", 501, 8.02, 1.19, 0.915),
        ("学生 → POLAR, 96 原子", 19, 1.87, 8.43, None),
        ("学生 → POLAR, 气相 336 帧", 336, 0.16, 329.5, None),
    ]
    out = []
    for name, n, sb, neff, top1 in rows:
        cv2 = n / neff - 1.0
        import math
        gauss = math.exp(-sb * sb)
        out.append((name, n, sb, cv2, neff / n, top1, gauss))
    return out


rows = load()

with PdfPages(OUT) as pdf:
    # ---------------- page 1 ----------------
    fig = plt.figure(figsize=PAGE)
    y = 0.90
    fig.text(0.07, y, "重加权因子方差与 ESS：四组数据量化", fontsize=18,
             fontweight="bold")
    y -= 0.035
    fig.text(0.07, y, "数据附录：从权重二阶矩推导 ESS，并量化本项目的四组数据",
             fontsize=11, color=GREY)
    y -= 0.020
    fig.text(0.07, y, "2026 年 10 月 27 日 · OFF/POLAR 重加权审计",
             fontsize=9, color=GREY)
    y -= 0.045

    y = head(fig, y, "摘要")
    y = para(fig, y, "重加权把源系综 q 的样本按 w = exp(−βΔU) 加权成目标系综 p。"
             "权重越不均匀，估计量方差越大；ESS 是权重相对方差的直接函数。"
             "本项目四组数据的权重相对标准差分别为 14.6（OFF→POLAR，1,152 原子）、"
             "20.5（学生→POLAR，1,152 原子）、1.12（96 原子）和 0.14（气相），"
             "对应 ESS 0.47 %、0.24 %、44 % 和 98 %。生产尺寸的失败不是程序错误，"
             "而是权重方差随原子数增长的结果。")

    y = head(fig, y, "符号")
    y = para(fig, y, "q：源分布（OFF23 或学生采样的系综）；p：目标分布（POLAR）；"
             "U_s、U_t：源/目标势能；ΔU = U_t − U_s；β = 1/(k_B T)；"
             "N：帧数；w：未归一化权重；w_norm：归一化权重；"
             "σ_β = Std(βΔU)；CV_w = Std(w)/E[w]。")

    y = head(fig, y, "1  重要性采样与权重")
    y = para(fig, y, "在同一温度、粒子数、体积和约束下，目标分布与源分布满足")
    y = eq(fig, y, r"$p(x)=q(x)\,e^{-\beta\Delta U(x)}/Z,\qquad Z=\langle e^{-\beta\Delta U}\rangle_q$")
    y = para(fig, y, "任意观测量 A 的目标平均为")
    y = eq(fig, y, r"$\langle A\rangle_p=\frac{\langle A\,w\rangle_q}{\langle w\rangle_q},"
                    r"\qquad w=e^{-\beta\Delta U}$")
    y = para(fig, y, "用 q 的 N 个样本做自归一化估计：")
    y = eq(fig, y, r"$\hat A=\sum_i \tilde w_i A_i,\qquad "
                    r"\tilde w_i=w_i/\sum_j w_j$")
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)

    # ---------------- page 2 ----------------
    fig = plt.figure(figsize=PAGE)
    y = 0.95
    y = head(fig, y, "2  估计量方差与 ESS")
    y = para(fig, y, "对自归一化估计做 delta 展开（N 较大时）：")
    y = eq(fig, y, r"$\mathrm{Var}(\hat A)\approx\frac{1}{N}\,"
                    r"\frac{\mathrm{Var}_q\left(w(A-\langle A\rangle_p)\right)}"
                    r"{\langle w\rangle_q^2}$")
    y = para(fig, y, "取 A = 1，得到归一化常数的方差")
    y = eq(fig, y, r"$\mathrm{Var}(\hat 1)\approx\frac{1}{N}\,"
                    r"\frac{\mathrm{Var}_q(w)}{\langle w\rangle_q^2}"
                    r"=\frac{\mathrm{CV}_w^2}{N}$")
    y = para(fig, y, "其中 CV_w 是权重的变异系数：")
    y = eq(fig, y, r"$\mathrm{CV}_w^2=\frac{\mathrm{Var}_q(w)}{\langle w\rangle_q^2}"
                    r"=\frac{\langle w^2\rangle_q}{\langle w\rangle_q^2}-1$")
    y = para(fig, y, "若直接从 p 抽 N_eff 个独立样本，均值的方差是 Var_p(A)/N_eff；"
             "令它与上式相等，得到 Kish 有效样本量")
    y = eq(fig, y, r"$N_{\mathrm{eff}}=\frac{N}{1+\mathrm{CV}_w^2}"
                    r"=\frac{1}{\sum_i\tilde w_i^2}$")
    y = para(fig, y, "这就是 ESS 的定义：它只由权重的相对方差决定，与 A 无关。"
             "CV_w = 0 时 N_eff = N；CV_w = 1 时 N_eff = N/2；"
             "CV_w = 20 时 N_eff ≈ N/400。")
    y = head(fig, y, "3  权重二阶矩的累积量展开")
    y = para(fig, y, "把 ΔU 写成均值 μ 与中心矩 δ = ΔU − μ，κ_n 为 δ 的 n 阶累积量：")
    y = eq(fig, y, r"$\langle e^{-\beta\Delta U}\rangle=e^{-\beta\mu}"
                    r"\exp\left(\sum_{n\geq2}\frac{(-\beta)^n}{n!}\kappa_n\right)$")
    y = eq(fig, y, r"$\langle e^{-2\beta\Delta U}\rangle=e^{-2\beta\mu}"
                    r"\exp\left(\sum_{n\geq2}\frac{(-2\beta)^n}{n!}\kappa_n\right)$")
    y = para(fig, y, "两式相除：")
    y = eq(fig, y, r"$1+\mathrm{CV}_w^2=\exp\left(\sum_{n\geq2}"
                    r"\frac{(-2\beta)^n-2(-\beta)^n}{n!}\kappa_n\right)$")
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)

    # ---------------- page 3 ----------------
    fig = plt.figure(figsize=PAGE)
    y = 0.95
    y = head(fig, y, "4  Gaussian 近似")
    y = para(fig, y, "若 ΔU 近似 Gaussian（n ≥ 3 的累积量为 0），只剩 n = 2 项：")
    y = eq(fig, y, r"$1+\mathrm{CV}_w^2=e^{\beta^2\mathrm{Var}(\Delta U)}"
                    r"=e^{\sigma_\beta^2}$")
    y = eq(fig, y, r"$\mathrm{CV}_w=\sqrt{e^{\sigma_\beta^2}-1},"
                    r"\qquad \frac{N_{\mathrm{eff}}}{N}=e^{-\sigma_\beta^2}$")
    y = para(fig, y, "也就是说，Gaussian 权重下 ESS 随 σ_β 的平方指数衰减："
             "σ_β = 1 时 37 %，2 时 1.8 %，3 时 0.012 %，8 时约 1e-28。"
             "这就是为什么 1,152 原子的重加权必然塌缩。")

    y = head(fig, y, "5  广延性与尺寸效应")
    y = para(fig, y, "ΔU 是广延量。若每原子能量误差 δu_i 独立、方差为 v，则")
    y = eq(fig, y, r"$\mathrm{Var}(\Delta U)=Nv\;\Rightarrow\;"
                    r"\sigma_\beta^2=\beta^2Nv,\qquad "
                    r"\frac{N_{\mathrm{eff}}}{N}\approx e^{-\beta^2Nv}$")
    y = para(fig, y, "若误差是相干的（例如整体密度/参考能漂移），"
             "Var(ΔU) = N²v_c，衰减更快：")
    y = eq(fig, y, r"$\frac{N_{\mathrm{eff}}}{N}\approx e^{-\beta^2N^2v_c}$")
    y = para(fig, y, "在局域贡献近似独立或短程相关成立时，两种情况下 ESS 都随 N 指数下降。"
             "把 96 原子的 σ_β=1.87 按 "
             "√N 外推到 1,152 原子，得到 σ_β≈6.5，与实测 8.0 同量级；"
             "按相干外推则更大。")

    y = head(fig, y, "6  独立的样本量判据（Chatterjee–Diaconis）")
    y = para(fig, y, "除方差/ESS 外，原始论文还给出：准确估计所需样本量约为 "
             "n ~ exp(KL(ν‖μ))，KL 是目标相对源的 KL 散度。")
    y = eq(fig, y, r"$n\sim e^{D(\nu\|\mu)},\qquad "
                    r"D(\nu\|\mu)=\frac{s^2}{2}\ \mathrm{(Gaussian)}$")
    y = para(fig, y, "当前 s=13.7616，s²/2=94.69，即 n~1.3e41；501 帧远小于该尺度。"
             "两条判据（ESS 的 χ² 与样本量的 KL）独立指向同一结论。")

    y = head(fig, y, "7  本项目四组数据的量化")
    lines = [
        ("体系", "N", "σ_β", "CV_w²", "CV_w", "ESS/N", "Gaussian ESS/N"),
    ]
    for name, n, sb, cv2, frac, top1, gauss in rows:
        lines.append((name, f"{n}", f"{sb:.2f}", f"{cv2:.1f}",
                      f"{cv2**0.5:.2f}", f"{frac*100:.1f}%",
                      f"{gauss:.1e}"))
    y -= 0.012
    colx = [0.07, 0.40, 0.48, 0.57, 0.66, 0.75, 0.84]
    for j, (c, x) in enumerate(zip(lines[0], colx)):
        fig.text(x, y, c, fontsize=8.6, fontweight="bold", color=GREY)
    y -= 0.022
    for row in lines[1:]:
        for c, x in zip(row, colx):
            fig.text(x, y, c, fontsize=8.4)
        y -= 0.020
    y -= 0.010
    y = para(fig, y, "CV_w = 权重相对标准差：1,152 原子是 14.6（OFF）和 20.5（学生），"
             "96 原子 1.12，气相 0.14。按 ESS = N/(1+CV_w²) 反推与上表一致。")
    y = para(fig, y, "Gaussian 预测在 σ_β 大时严重偏离实测：学生 1,152 原子"
             "Gaussian 给 1e-28，实测 0.24 %；说明 ΔU 分布不是 Gaussian，"
             "而是“多数帧接近均值、少数帧极端”的重尾分布。σ_β 只反映对数权重的"
             "整体宽度，ESS 由最大几个权重决定，两者不能互相替代。")
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)

    # ---------------- page 4 ----------------
    fig = plt.figure(figsize=PAGE)
    y = 0.95
    y = head(fig, y, "8  权重集中度")
    y = para(fig, y, "对 1,152 原子数据直接统计归一化权重：")
    y = para(fig, y, "OFF→POLAR：最大单帧 59.6 %，前 3 帧 93.2 %，前 5 帧 99.1 %。")
    y = para(fig, y, "学生→POLAR：最大单帧 91.5 %，前 5 帧 98.1 %，第 277 帧的 "
             "βΔU 比均值低 22.9（ΔU 低约 0.59 eV）。")
    y = para(fig, y, "学生整体 σ_β 更小（8.0 对 13.8），但它的权重更集中，"
             "因为 1,152 原子帧是 OFF23 采的、对学生是分布外；单帧离群即可让 ESS 更低。"
             "这说明 ESS 不是 σ_β 的单调函数，必须同时报告最大权重和前 k 帧占比。")

    y = head(fig, y, "9  估计量的偏差")
    y = para(fig, y, "自归一化估计的偏差是 O(1/N_eff)。N_eff ≈ 1 时，"
             "任何重加权平均实际上由一帧决定，偏差与统计误差同量级，结果没有意义。"
             "因此不能用“加权后的曲线看起来平滑”判断可用性，必须看 N_eff、"
             "最大权重和分块误差。")

    y = head(fig, y, "10  实用诊断")
    y = para(fig, y, "1) 报告 σ_β、CV_w、N_eff、最大单帧权重和前 3/5 帧占比；"
             "2) 按时间块重算权重与观测量，给出分块误差；"
             "3) ESS ≥ 10 % 只作启发式门槛，最终看观测量与独立目标轨迹的偏差；"
             "4) 生产尺寸不要用一步重加权：直接学生采样，或采样 λ 中间势后用 "
             "BAR/MBAR 合并相邻状态。")

    y = head(fig, y, "11  结论")
    y = para(fig, y, "权重方差是重加权可行性的核心量：1,152 原子时 CV_w ≈ 15–21，"
             "ESS 只剩 0.2–0.5 %；96 原子 CV_w ≈ 1.1，ESS ≈ 44 %；"
             "气相 CV_w ≈ 0.14，ESS ≈ 98 %。ESS 随 N 指数衰减，"
             "因此“换个更准的模型”只能把 σ_β 从 13.8 降到 8.0，"
             "不能把生产尺寸的一步重加权救回来。")
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)

    # ---------------- page 5: references ----------------
    fig = plt.figure(figsize=PAGE)
    y = 0.95
    y = head(fig, y, "参考文献")
    refs = [
        "Kish, L. Survey Sampling. Wiley, New York, 1965. "
        "（ESS = (Σw)²/Σw² 的原始来源；专著，无 DOI）",
        "Kong, A.; Liu, J. S.; Wong, W. H. Sequential imputations and "
        "Bayesian missing data problems. J. Am. Stat. Assoc. 89, 278–288 "
        "(1994). DOI: 10.1080/01621459.1994.10476469",
        "Chatterjee, S.; Diaconis, P. The sample size required in importance "
        "sampling. Ann. Appl. Probab. 28, 1099–1135 (2018). "
        "DOI: 10.1214/17-AAP1326",
        "Shirts, M. R.; Chodera, J. D. Statistically optimal analysis of "
        "samples from multiple equilibrium states. J. Chem. Phys. 129, "
        "124105 (2008). DOI: 10.1063/1.2978177",
        "Herzog, et al. Assessing the accuracy of machine learning "
        "thermodynamic perturbation theory: DFT and beyond. J. Chem. Theory "
        "Comput. 18, 1382–1394 (2022). DOI: 10.1021/acs.jctc.1c01034",
        "Hilpert, J.; Kresse, G. Accurate thermophysical properties of water "
        "using machine-learned potentials. J. Chem. Phys. 164, 194504 "
        "(2026). DOI: 10.1063/5.0325444",
    ]
    for i, r in enumerate(refs, 1):
        y = para(fig, y, f"[{i}] {r}", fontsize=9.0, width=94)
        y -= 0.006
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)

print("wrote", OUT)
