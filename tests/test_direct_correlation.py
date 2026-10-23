import numpy as np

from sampling.direct_correlation import c2_from_g


def test_ideal_gas_has_zero_c2():
    r = np.linspace(0.05, 8.0, 160)
    g = np.ones_like(r)
    _, c2r, _, c2k = c2_from_g(r, g, rho=0.02)
    assert np.max(np.abs(c2r)) < 1e-10
    assert np.max(np.abs(c2k)) < 1e-10


def test_c2_roundtrip_shape():
    r = np.linspace(0.05, 8.0, 160)
    g = 1.0 + 0.5 * np.exp(-((r - 2.8) / 0.4) ** 2)
    r2, c2r, k, c2k = c2_from_g(r, g, rho=0.02)
    assert r2.shape == c2r.shape == r.shape
    assert k.shape == c2k.shape
    assert np.isfinite(c2r).all()
    assert np.isfinite(c2k).all()
