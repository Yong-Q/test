# 密度、RDF和重加权估计器文献

2026-10-28整理；PDF均为公开作者稿或机构公开版本。逐项任务见[估计器 TODO](../../docs/TODO_ESTIMATOR_LITERATURE_2026-10-28.md)。

| PDF | 文献信息 | 主要用途 |
|---|---|---|
| [de_las_heras_2018_force_density.pdf](de_las_heras_2018_force_density.pdf) | de las Heras & Schmidt, *Better than Counting: Density Profiles from Force Sampling*, Phys. Rev. Lett. 120, 218001 (2018), [DOI 10.1103/PhysRevLett.120.218001](https://doi.org/10.1103/PhysRevLett.120.218001) | 力密度积分，一体密度；[arXiv v2](https://arxiv.org/abs/1711.00006) |
| [coles_2021_force_estimator_combination.pdf](coles_2021_force_estimator_combination.pdf) | Coles 等, *Reduced variance analysis of molecular dynamics simulations by linear combination of estimators*, J. Chem. Phys. 154, 191101 (2021), [DOI 10.1063/5.0053737](https://doi.org/10.1063/5.0053737) | 两种力辅助估计器的线性组合；[arXiv v2](https://arxiv.org/abs/2104.05038) |
| [patrone_2017_spectral_rdf.pdf](patrone_2017_spectral_rdf.pdf) | Patrone & Rosch, *Beyond histograms: efficiently estimating radial distribution functions via spectral Monte Carlo*, J. Chem. Phys. 146, 094107 (2017), [DOI 10.1063/1.4977516](https://doi.org/10.1063/1.4977516) | 用基函数估计 g(r)；[NIST全文](https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=920798) |
| [majumdar_2026_mlip_pmf_reweighting.pdf](majumdar_2026_mlip_pmf_reweighting.pdf) | Majumdar 等, *Reweighting free energy profiles between universal machine learning interatomic potentials for fast consensus building*, arXiv:2605.15630 (2026，预印本), [DOI 10.48550/arXiv.2605.15630](https://doi.org/10.48550/arXiv.2605.15630) | 不同机器学习势之间的反应坐标自由能重加权；[代码](https://github.com/sauradeep93/Reweighting-free-energies)，[Zenodo数据](https://zenodo.org/records/23046063) |

下载自各条链接指向的 arXiv 或 NIST 公开来源；未单独下载补充材料或模拟数据。个别作者稿本身包含附录。所有文件的标题与页数已从PDF核验，文件哈希见[清单](manifest.tsv)。2026论文在这里标为预印本；不能仅凭论文示例认证本项目结果。
