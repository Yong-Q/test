#!/usr/bin/env python3
"""Teacher-facing research report PDF (research-tech-report style)."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.font_manager import FontProperties, fontManager

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FONT = Path("/workspace/group/shared/bza/symmetrix-polar/.tmp_fonts/NotoSansCJKsc-Regular.otf")
fontManager.addfont(str(FONT)); CN = FontProperties(fname=str(FONT))
plt.rcParams["mathtext.fontset"] = "dejavusans"
plt.rcParams["font.family"] = CN.get_name()
W, H = 8.27, 11.69


def page(title):
    fig = plt.figure(figsize=(W, H)); fig.patch.set_facecolor("white")
    fig.text(0.08, 0.945, title, fontsize=16, fontweight="bold", fontproperties=CN)
    fig.lines.append(plt.Line2D([0.08, 0.92], [0.925, 0.925], transform=fig.transFigure,
                                color="#888888", linewidth=0.8))
    return fig


def text(fig, y, s, size=10.5, color="#222222", weight="normal"):
    fig.text(0.08, y, s, fontsize=size, color=color, fontweight=weight,
             fontproperties=CN, va="top", wrap=True)


def eq(fig, y, s, size=13):
    fig.text(0.5, y, s, ha="center", va="top", fontsize=size, fontproperties=CN)


def image(fig, path, y0, h=0.32):
    ax = fig.add_axes([0.10, y0, 0.80, h]); ax.imshow(plt.imread(path)); ax.axis("off")


def save(fig, pdf):
    pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)


def main():
    out = HERE.parents[1] / "docs/reports/RESEARCH_REPORT.pdf"
    with PdfPages(out) as pdf:
        fig = page("MACE-OFF → MACE-POLAR：c1/c2 重加权的可行性")
        text(fig, 0.885, "给老师的审阅稿 · 2026-10-23", 12, "#333333", "bold")
        text(fig, 0.84,
             "问题：能否用便宜的 MACE-OFF 轨迹，加上逐帧 MACE-POLAR 单点能量，"
             "通过 Boltzmann 重加权得到 MACE-POLAR 的 c1 和 c2？", 10.5)
        text(fig, 0.76, "结论", 12, "#333333", "bold")
        text(fig, 0.72,
             "重加权公式和 Ornstein–Zernike 反演本身是正确的（解析验证误差 5×10^-13）；"
             "但实际相空间重叠失败：96 原子 ESS 10.1%（marginal），1,152 原子 ESS=1（collapse）。"
             "1 ns MACE-OFF 轨迹不能解决这个问题。", 10.5)
        text(fig, 0.60, "关键数字", 12, "#333333", "bold")
        text(fig, 0.565,
             "• 能量偏移：416.62 meV/atom（常数，归一化后消掉）。\n"
             "• 96 原子：σβ=3.89，ESS=3.63/36=10.1%，重加权 c2 与直接 POLAR c2 的 RMS=121。\n"
             "• 1,152 原子：σβ=93.8，ESS=1.0/6，实时判定 collapse。\n"
             "• bulk 水两力场力 MAE：104.7 meV/Å。", 10)
        text(fig, 0.38, "建议", 12, "#333333", "bold")
        text(fig, 0.345,
             "1,000+ 原子不要用直接重加权；改用直接 MACE-POLAR 采样、ΔV 代理势，"
             "或 PRL 式的多密度 c2 泛函。", 10.5)
        save(fig, pdf)

        fig = page("1. 方法：重加权与直接相关函数")
        text(fig, 0.885, "从 A（MACE-OFF）的样本估计 B（MACE-POLAR）的系综平均：", 10)
        eq(fig, 0.84, r"$\langle O\rangle_B=\frac{\langle O\,e^{-\beta(V_B-V_A)}\rangle_A}{\langle e^{-\beta(V_B-V_A)}\rangle_A},\qquad w_i=e^{-\beta\Delta V_i}$")
        text(fig, 0.76, "c1 / c2 是自由能泛函的导数，不是线性拟合系数：", 10)
        eq(fig, 0.715, r"$c_1=-\beta\frac{\delta F_{\rm exc}}{\delta\rho},\qquad c_2=\frac{\delta c_1}{\delta\rho}=-\beta\frac{\delta^2F_{\rm exc}}{\delta\rho\delta\rho'}$")
        text(fig, 0.62, "均匀体相：c1 是常数，c2 由 g(r) 经 OZ 得到：", 10)
        eq(fig, 0.575, r"$c_2(k)=\frac{h(k)}{1+\rho h(k)},\qquad h(r)=g(r)-1$")
        text(fig, 0.49, "ESS 是有效样本数：", 10)
        eq(fig, 0.45, r"$\mathrm{ESS}=\frac{(\sum_i w_i)^2}{\sum_i w_i^2}\in[1,N]$")
        text(fig, 0.37,
             "常数偏移在权重里消掉；真正决定 ESS 的是 ΔV 的涨落。\n"
             "c2 是结构量；c1 在均匀体相是常数，非均匀时需要密度剖面+目标外场。", 9.8)
        text(fig, 0.25,
             "参考：Dijkman et al., PRL 134, 056103 (2025)；Bui & Cox, PNAS 123, e2610049123 (2026)。", 9)
        save(fig, pdf)

        fig = page("2. 为什么大体系 ESS 会塌缩")
        image(fig, ROOT / "docs/reports/figures/ess_scaling.png", 0.46, 0.38)
        text(fig, 0.40,
             "96 原子：σβ=3.89，ESS=3.63/36=10.1%；1,152 原子实时监控：σβ=93.8，ESS=1。"
             "阈值 σβ≈3、ESS≈10 已越过。", 9.8)
        text(fig, 0.30, "原因是广延量 + 指数权重 + 高维重叠：", 10, "#333333", "bold")
        eq(fig, 0.265, r"$\Delta V=\sum_{i=1}^{N}\delta v_i,\qquad \frac{\mathrm{ESS}}{N}\sim e^{-\sigma_\beta^2}$")
        text(fig, 0.19,
             "每原子 1 meV 的差异，在 1,152 原子上就是 1.15 eV；300 K 下 βΔV≈44。\n"
             "增加帧数只增加样本，不改变每帧权重的方差。", 9.8)
        save(fig, pdf)

        fig = page("3. 96 原子：重加权诊断与 c2 对比")
        image(fig, ROOT / "docs/reports/figures/reweight_diagnostics.png", 0.48, 0.36)
        text(fig, 0.44,
             "36 帧：ΔE 偏移 416.6 meV/atom，涨落 1.166 meV/atom，σβ=3.89，ESS=3.63（10.1%）。"
             "线性 slope/intercept=0.9452/−3606.84 eV，R²=0.9866，残差 1.03 meV/atom。", 9.5)
        image(fig, ROOT / "docs/reports/figures/reweight_vs_direct.png", 0.10, 0.30)
        text(fig, 0.065,
             "81 帧对比：重加权 vs 直接 POLAR c2 的 RMS=121，最大差 529；直接 POLAR vs OFF 的 RMS=116。"
             "重加权没有改善一致性——但 ESS 只有 2.6%，这是噪声对噪声，不能据此否定公式。", 9.3)
        save(fig, pdf)

        fig = page("4. 1,152 原子：实时 ESS 判死")
        text(fig, 0.885, "实时监控逐帧 MACE-POLAR 单点，输出 σβ 与 ESS：", 10)
        text(fig, 0.845,
             "step 0      ΔE/atom=410.254  σβ=0.00    ESS=1/1\n"
             "step 2000   ΔE/atom=414.291  σβ=127.21  ESS=1/2\n"
             "step 4000   ΔE/atom=414.857  σβ=111.87  ESS=1/3\n"
             "step 6000   ΔE/atom=415.245  σβ=102.74  ESS=1/4\n"
             "step 8000   ΔE/atom=415.837  σβ=98.98   ESS=1/5\n"
             "step 10000  ΔE/atom=415.806  σβ=93.83   ESS=1/6", 9.2)
        text(fig, 0.60, "verdict: collapse", 14, "#B00020", "bold")
        text(fig, 0.54,
             "ESS 由体系尺寸和两个势的差异决定；1,000 帧、10,000 帧都不会改变。\n"
             "这条 1,152 原子的 1 ns 直接重加权路线已停止，不再消耗机时。", 10)
        text(fig, 0.40, "同一批帧上还发现的两个物理问题：", 10, "#333333", "bold")
        text(fig, 0.365,
             "• 0.02 molecules/Å³ 在 300 K 接近水的两相区，不是稳定单相液体；\n"
             "• 盒子 Lx=23.4 Å 只有约 7.4σ，小于 PRL 的 L=10σ。", 9.8)
        text(fig, 0.27,
             "即使换成 0.0334（1 g/cm³）的稳定液体，1,152 原子的 σβ 仍会随 N 增长，"
             "直接重加权大概率仍是 ESS≈1。", 9.8)
        save(fig, pdf)

        fig = page("5. 已严谨验证与尚未验证")
        text(fig, 0.885, "已严谨验证：", 11, "#333333", "bold")
        text(fig, 0.845,
             "• 光滑解析 c(r) 的 OZ 反演：最大误差 4.9×10^-13；\n"
             "• Percus–Yevick 硬球平滑段：2.1×10^-13；\n"
             "• 理想气体 c2=0；12 项单元测试通过；\n"
             "• 重加权恒等式、ESS、线性拟合的代数关系与实现一致。", 10)
        image(fig, ROOT / "docs/reports/figures/harmonic_validation.png", 0.44, 0.30)
        text(fig, 0.38, "尚未验证：", 11, "#333333", "bold")
        text(fig, 0.345,
             "• 96 原子/10 ps 的 c2 不是定量结果（噪声/有限尺寸）；\n"
             "• c1 的 Widom 插入方差大，只有 50/100 次插入被接受；\n"
             "• 两力场 c2 的真实结构差尚未测出；\n"
             "• 1,000+ 原子的 c1/c2 没有可用的重加权结果。", 9.8)
        save(fig, pdf)

        fig = page("6. 问题、限制与建议")
        text(fig, 0.885, "当前实验的问题", 11, "#333333", "bold")
        text(fig, 0.85,
             "1. 96 原子盒子 L=11.7 Å < 2r_cut=12 Å；0.02 密度在 300 K 是两相区。\n"
             "2. 10 ps 轨迹的 g(r) 噪声大，c2 摆动到 −293~1337。\n"
             "3. c1 绝对值被能量参考主导；Widom 接受率低。\n"
             "4. 1,152 原子 σβ≈94，ESS=1；更多帧无效。\n"
             "5. 在 OFF 帧上重算 POLAR 能量不会改变 g(r)。", 9.6)
        text(fig, 0.61, "建议的下一步", 11, "#333333", "bold")
        text(fig, 0.575,
             "• 要 MACE-POLAR 的 c2：直接跑 POLAR 100 ps（1,152 原子约 8.3 h），"
             "或用 ΔV 代理势跑 MD。\n"
             "• 要 c1(r)：在外场下跑非均匀 POLAR 轨迹，用 Euler–Lagrange 反解；"
             "均相轨迹只能给 c1 常数。\n"
             "• 要 PRL 式泛函：跑多个密度的 bulk c2，训练 c2-matching 泛函，"
             "而不是单条轨迹重加权。\n"
             "• 重加权本身：只在 ≤96 原子、势差更小的情况下作为方法验证。", 9.6)
        text(fig, 0.28, "一句话", 12, "#333333", "bold")
        text(fig, 0.24,
             "公式正确，流程也已走通；失败的是“用直接重加权把 1,000+ 原子的 MACE-OFF "
             "变成 MACE-POLAR”这个具体方案。", 10.5, "#111111", "bold")
        save(fig, pdf)

        fig = page("References")
        text(fig, 0.885,
             "[1] J. Dijkman, M. Dijkstra, R. van Roij, M. Welling, J.-W. van de Meent, B. Ensing,\n"
             "    Learning Neural Free-Energy Functionals with Pair-Correlation Matching,\n"
             "    Phys. Rev. Lett. 134, 056103 (2025). DOI: 10.1103/PhysRevLett.134.056103.\n\n"
             "[2] A. T. Bui, S. J. Cox,\n"
             "    A unified machine-learning framework for ab initio multiscale modeling of liquids,\n"
             "    PNAS 123, e2610049123 (2026). DOI: 10.1073/pnas.2610049123.\n\n"
             "[3] R. W. Zwanzig, J. Chem. Phys. 22, 1420 (1954).\n"
             "[4] G. M. Torrie, J. P. Valleau, J. Comput. Phys. 23, 187 (1977).\n"
             "[5] A. M. Ferrenberg, R. H. Swendsen, Phys. Rev. Lett. 63, 1195 (1989).\n"
             "[6] C. H. Bennett, J. Comput. Phys. 22, 245 (1976).\n"
             "[7] M. R. Shirts, J. D. Chodera, J. Chem. Phys. 129, 124105 (2008).\n"
             "[8] J.-P. Hansen, I. R. McDonald, Theory of Simple Liquids.", 9.2)
        text(fig, 0.35,
             "代码与数据：https://github.com/Yong-Q/test\n"
             "sampling/direct_correlation.py; sampling/off_polar.py; scripts/monitor_ess.py", 9)
        save(fig, pdf)
    print(out)


if __name__ == "__main__":
    main()
