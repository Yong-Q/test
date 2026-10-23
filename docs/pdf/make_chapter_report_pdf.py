#!/usr/bin/env python3
"""Chapter-style teacher report: Chapter 1 theory, Chapter 2 experiments."""
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
    fig.text(0.08, 0.945, title, fontsize=15, fontweight="bold", fontproperties=CN)
    fig.lines.append(plt.Line2D([0.08, 0.92], [0.925, 0.925], transform=fig.transFigure,
                                color="#888888", linewidth=0.8))
    return fig


def text(fig, y, s, size=10.2, color="#222222", weight="normal"):
    fig.text(0.08, y, s, fontsize=size, color=color, fontweight=weight,
             fontproperties=CN, va="top", wrap=True)


def eq(fig, y, s, size=12.5):
    fig.text(0.5, y, s, ha="center", va="top", fontsize=size, fontproperties=CN)


def image(fig, path, y0, h=0.30):
    ax = fig.add_axes([0.10, y0, 0.80, h]); ax.imshow(plt.imread(path)); ax.axis("off")


def save(fig, pdf):
    pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)


def main():
    out = HERE.parent / "reports" / "RESEARCH_REPORT.pdf"
    with PdfPages(out) as pdf:
        # title / abstract
        fig = page("MACE-OFF → MACE-POLAR：c1/c2 重加权的理论与实验")
        text(fig, 0.885, "Technical report · 2026-10-23 · for review", 11, "#333333", "bold")
        text(fig, 0.84,
             "本报告第一章给出重加权、ESS、c1、c2 与 Ornstein–Zernike 的推导；"
             "第二章给出 96 原子与 1,152 原子水体系的实测结果、问题与结论。", 10.5)
        text(fig, 0.74, "摘要", 12, "#333333", "bold")
        text(fig, 0.70,
             "重加权公式与 OZ 反演在数学上是正确的（解析验证误差 4.9×10^-13）；"
             "但实际相空间重叠不足：96 原子 ESS 10.1%（marginal），1,152 原子 ESS=1（collapse）。"
             "1 ns MACE-OFF 轨迹不能解决这个问题。", 10.5)
        text(fig, 0.56, "给老师的判断点", 12, "#333333", "bold")
        text(fig, 0.52,
             "• 是否接受直接 MACE-POLAR 采样（100 ps–1 ns）作为 c2/c1 参照？\n"
             "• 是否为 1,000+ 原子投入 ΔV 代理势（能量+力）？\n"
             "• 非均匀 c1(r) 是否走“外场密度剖面 + Euler–Lagrange”，还是 PRL 式多密度泛函？", 10)
        text(fig, 0.34,
             "代码与数据：https://github.com/Yong-Q/test", 9.5)
        save(fig, pdf)

        # Chapter 1
        fig = page("第一章 理论：重加权、ESS 与直接相关函数")
        text(fig, 0.885, "1.1 两个 Boltzmann 系综", 11.5, "#333333", "bold")
        eq(fig, 0.84, r"$p_A(x)=\frac{e^{-\beta V_A(x)}}{Z_A},\qquad p_B(x)=\frac{e^{-\beta V_B(x)}}{Z_B}$")
        text(fig, 0.76, "一体密度算符与密度：", 10)
        eq(fig, 0.72, r"$\hat\rho(\mathbf{r})=\sum_i\delta(\mathbf{r}-\mathbf{r}_i),\qquad \rho_A(\mathbf{r})=\langle\hat\rho(\mathbf{r})\rangle_A$")
        eq(fig, 0.64, r"$\int\rho_A(\mathbf{r})d\mathbf{r}=\int\rho_B(\mathbf{r})d\mathbf{r}=N$")
        text(fig, 0.56, r"A 的样本来自 $p_A$，目标是估计 B 的系综量；密度是系综平均，不是单帧量。", 9.8)
        text(fig, 0.46, "1.2 重要性采样（重加权）", 11.5, "#333333", "bold")
        eq(fig, 0.415, r"$\langle O\rangle_B=\int O p_B=\int O\frac{p_B}{p_A}p_A=\frac{\langle O e^{-\beta(V_B-V_A)}\rangle_A}{\langle e^{-\beta(V_B-V_A)}\rangle_A}$", 11.5)
        text(fig, 0.32, "权重与配分函数比：", 10)
        eq(fig, 0.285, r"$w_i=e^{-\beta[V_B(x_i)-V_A(x_i)]},\qquad \frac{Z_B}{Z_A}=\langle e^{-\beta(V_B-V_A)}\rangle_A$")
        text(fig, 0.19, r"常数偏移 $V_B=V_A+\Delta E$ 在归一化权重里消掉；只有逐帧涨落进入 ESS。", 9.8)
        save(fig, pdf)

        fig = page("第一章 理论：c1、c2 与 OZ")
        text(fig, 0.885, "1.3 直接相关函数", 11.5, "#333333", "bold")
        eq(fig, 0.84, r"$c_1(\mathbf{r};[\rho])=-\beta\frac{\delta F_{\rm exc}[\rho]}{\delta\rho(\mathbf{r})}$")
        eq(fig, 0.75, r"$c_2(\mathbf{r},\mathbf{r}';[\rho])=\frac{\delta c_1(\mathbf{r})}{\delta\rho(\mathbf{r}')}=-\beta\frac{\delta^2F_{\rm exc}}{\delta\rho(\mathbf{r})\delta\rho(\mathbf{r}')}$")
        text(fig, 0.65, "均匀体相：c1 是常数，c2 只依赖距离：", 10)
        eq(fig, 0.61, r"$c_{1,\rm ex}=-\beta\mu_{\rm ex},\qquad c_2(\mathbf{r},\mathbf{r}')=c_2(|\mathbf{r}-\mathbf{r}'|)$")
        text(fig, 0.52, "1.4 Ornstein–Zernike", 11.5, "#333333", "bold")
        eq(fig, 0.475, r"$h(r)=g(r)-1,\qquad h(k)=4\pi\int r^2h(r)\frac{\sin kr}{kr}dr$")
        eq(fig, 0.37, r"$c_2(k)=\frac{h(k)}{1+\rho h(k)},\qquad c_2(r)=\frac{1}{2\pi^2}\int k^2c_2(k)\frac{\sin kr}{kr}dk$")
        text(fig, 0.26, "1.5 非均匀 c1：外场下中心化", 11.5, "#333333", "bold")
        eq(fig, 0.215, r"$c_1(\mathbf{r})=\ln[\Lambda^3\rho(\mathbf{r})]-\beta\mu+\beta V_{\rm ext}(\mathbf{r})$")
        text(fig, 0.13, r"减掉空间平均即可去掉 $-\beta\mu$；不需要 Widom。", 9.8)
        save(fig, pdf)

        fig = page("第一章 理论：ESS 与尺寸限制")
        text(fig, 0.885, "1.6 有效样本数", 11.5, "#333333", "bold")
        eq(fig, 0.84, r"$\mathrm{ESS}=\frac{(\sum_iw_i)^2}{\sum_iw_i^2}\in[1,N],\qquad \sigma_\beta=\mathrm{std}(\beta\Delta V)$")
        eq(fig, 0.73, r"$\frac{\mathrm{ESS}}{N}\sim e^{-\sigma_\beta^2}$")
        text(fig, 0.63, "1.7 为什么 N 一大就崩", 11.5, "#333333", "bold")
        eq(fig, 0.585, r"$\Delta V=\sum_{i=1}^{N}\delta v_i$")
        text(fig, 0.50,
             "即使每原子只差 1 meV：96 原子总差 0.096 eV（βΔV≈3.7）；"
             "1,152 原子总差 1.15 eV（βΔV≈44）。指数权重把广延差异放大成数量级差异。", 9.8)
        text(fig, 0.40,
             "高维相空间的重叠随 N 指数下降；增加帧数只增加样本，不改变每帧权重的方差。", 9.8)
        text(fig, 0.30, "1.8 与 PRL/PNAS 的关系", 11.5, "#333333", "bold")
        text(fig, 0.265,
             "PRL：用 bulk g(r) 训练 c2 matching；外势只在预测/验证。\n"
             "PNAS：用非均匀密度剖面学习 c1；c2 由 autodiff。\n"
             "两者都不是“单条均相轨迹直接重加权”。", 9.8)
        save(fig, pdf)

        # Chapter 2
        fig = page("第二章 实验：体系、结果与问题")
        text(fig, 0.885, "2.1 体系与设置", 11.5, "#333333", "bold")
        text(fig, 0.845,
             "水，96 原子（32 H2O）与 1,152 原子（384 H2O）；密度 0.02 molecules/Å³；300 K；0.5 fs。\n"
             "源：原始 MACE-OFF23 medium（Symmetrix FP32 引擎）；目标：MACE-POLAR-1-M（FP64 单点）。", 9.8)
        text(fig, 0.74, "2.2 96 原子：重加权诊断", 11.5, "#333333", "bold")
        image(fig, ROOT / "examples/water96/reweight/reweight_diagnostics.png", 0.38, 0.33)
        text(fig, 0.34,
             "36 帧：ΔE 偏移 416.62 meV/atom，涨落 1.166 meV/atom，σβ=3.89，ESS=3.63/36=10.1%。"
             "slope/intercept=0.9452/−3606.84 eV，R²=0.9866，残差 1.03 meV/atom。", 9.3)
        text(fig, 0.22, "2.3 96 原子：重加权 c2 vs 直接 POLAR c2", 11.5, "#333333", "bold")
        text(fig, 0.185,
             "81 帧：ESS=2.09/81=2.6%；直接 POLAR vs OFF 的 c2 RMS=116；"
             "直接 POLAR vs 重加权 RMS=121，最大差 529。重加权没有改善一致性，"
             "但 ESS 太低，这是噪声对噪声。", 9.3)
        save(fig, pdf)

        fig = page("第二章 实验：重加权 c2 与直接 POLAR 的对照")
        image(fig, ROOT / "validation/results/forcefield_c1c2_water96/reweight_vs_direct/reweight_vs_direct.png", 0.50, 0.36)
        text(fig, 0.46,
             "81 帧：σβ=3.31，ESS=2.09/81=2.6%。直接 POLAR vs OFF 的 c2 RMS=115.8；"
             "直接 POLAR vs 重加权的 RMS=121.0，最大差 528.7。", 9.6)
        text(fig, 0.36,
             "重加权没有把曲线拉近，反而略差；但 ESS 只有 2.6%，加权 c2 实际由约 2 帧决定，"
             "直接 POLAR 轨迹也只有 10 ps。这个比较是噪声对噪声，不能证明公式错误，"
             "只说明当前数据不足以验证。", 9.8)
        text(fig, 0.22,
             "要得到有意义的对照：同一盒子、至少 100 ps 的 POLAR 轨迹；"
             "并在 ESS≥10% 的体系上比较。", 9.8, "#111111", "bold")
        save(fig, pdf)

        fig = page("第二章 实验：1,152 原子实时 ESS")
        text(fig, 0.885, "2.4 实时监控结果（逐帧 MACE-POLAR 单点）", 11.5, "#333333", "bold")
        text(fig, 0.845,
             "step 0      ΔE/atom=410.254  σβ=0.00    ESS=1/1\n"
             "step 2000   ΔE/atom=414.291  σβ=127.21  ESS=1/2\n"
             "step 4000   ΔE/atom=414.857  σβ=111.87  ESS=1/3\n"
             "step 6000   ΔE/atom=415.245  σβ=102.74  ESS=1/4\n"
             "step 8000   ΔE/atom=415.837  σβ=98.98   ESS=1/5\n"
             "step 10000  ΔE/atom=415.806  σβ=93.83   ESS=1/6", 9.2)
        text(fig, 0.61, "verdict: collapse", 14, "#B00020", "bold")
        text(fig, 0.55,
             "1,000 帧、10,000 帧都不会改变 ESS；这条 1,152 原子、1 ns 的直接重加权路线已停止。", 9.8)
        image(fig, ROOT / "docs/reports/figures/ess_scaling.png", 0.20, 0.30)
        text(fig, 0.16,
             "左：σβ 随 N 增大；右：ESS 绝对值。1,152 原子已 collapse。", 9.2)
        save(fig, pdf)

        fig = page("第二章 实验：已验证与未验证")
        text(fig, 0.885, "2.5 已严谨验证", 11.5, "#333333", "bold")
        text(fig, 0.845,
             "OZ 反演：光滑解析 c(r) 误差 4.9×10^-13；Percus–Yevick 硬球平滑段 2.1×10^-13；"
             "理想气体 c2=0；12 项单元测试通过。", 9.8)
        image(fig, ROOT / "docs/results/harmonic_validation.png", 0.48, 0.30)
        text(fig, 0.42, "2.6 尚未验证", 11.5, "#333333", "bold")
        text(fig, 0.385,
             "• 96 原子/10 ps 的 c2 定量形状；\n"
             "• c1 的 Widom 插入误差（仅 50/100 被接受）；\n"
             "• 两力场真实结构差；\n"
             "• 1,000+ 原子的可用 c1/c2。", 9.8)
        text(fig, 0.27, "2.7 结论", 11.5, "#333333", "bold")
        text(fig, 0.235,
             "公式正确、流程走通；失败的是 1,000+ 原子上的直接重加权。"
             "下一步：直接 POLAR 采样、ΔV 代理势，或 PRL 式多密度泛函。", 10, "#111111", "bold")
        save(fig, pdf)

        fig = page("References")
        text(fig, 0.885,
             "[1] J. Dijkman et al., Learning Neural Free-Energy Functionals with Pair-Correlation Matching,\n"
             "    Phys. Rev. Lett. 134, 056103 (2025). DOI: 10.1103/PhysRevLett.134.056103.\n\n"
             "[2] A. T. Bui, S. J. Cox, A unified machine-learning framework for ab initio multiscale\n"
             "    modeling of liquids, PNAS 123, e2610049123 (2026). DOI: 10.1073/pnas.2610049123.\n\n"
             "[3] R. W. Zwanzig, J. Chem. Phys. 22, 1420 (1954).\n"
             "[4] G. M. Torrie, J. P. Valleau, J. Comput. Phys. 23, 187 (1977).\n"
             "[5] A. M. Ferrenberg, R. H. Swendsen, Phys. Rev. Lett. 63, 1195 (1989).\n"
             "[6] C. H. Bennett, J. Comput. Phys. 22, 245 (1976).\n"
             "[7] M. R. Shirts, J. D. Chodera, J. Chem. Phys. 129, 124105 (2008).", 9.2)
        text(fig, 0.35,
             "代码与数据：https://github.com/Yong-Q/test\n"
             "sampling/direct_correlation.py; sampling/off_polar.py; scripts/monitor_ess.py", 9)
        save(fig, pdf)
    print(out)


if __name__ == "__main__":
    main()
