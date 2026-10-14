"""stata_core -- minimal Stata-compatible estimation helpers for the employer re-run (n = 397).

clogit with two alternatives per choice set (the employer DCE: 2 options x 6 tasks per firm), cluster-robust
variance as Stata's `clogit ..., vce(cluster id)` (finite-sample factor G/(G-1)), delta method (`nlcom`) and
Wald tests (`test`). Written for MOM_presentation; the professor's do-files are the reference.
"""
import numpy as np
import pandas as pd
from math import erf, sqrt
from scipy import stats


class Fit:
    pass


def _prep(df, y, X, group):
    """Return per-choice-set arrays: dX (n_sets x k) = x_first - x_second, y_first, set index, first-row index."""
    d = df.sort_values([group], kind="mergesort")
    g = d[group].to_numpy()
    cnt = pd.Series(g).value_counts()
    assert (cnt == 2).all(), "clogit port assumes exactly two alternatives per choice set"
    d = d.reset_index(drop=True)
    first = d.index[d[group].ne(d[group].shift())].to_numpy()
    second = first + 1
    Xv = d[X].to_numpy(float)
    yv = d[y].to_numpy(float)
    assert np.allclose(yv[first] + yv[second], 1), "each choice set must have exactly one chosen option"
    dX = Xv[first] - Xv[second]
    y1 = yv[first]
    return d, first, dX, y1


def clogit(df, y, X, group, cluster, drop_constant=True):
    """Conditional logit, 2 alternatives per set. Returns Fit with b, V (cluster robust), se, ll, names, N, G."""
    d, first, dX, y1 = _prep(df, y, X, group)
    cl = d[cluster].to_numpy()[first]
    k = len(X)
    b = np.zeros(k)
    ll_old = -np.inf
    for it in range(100):
        eta = dX @ b
        p = 1 / (1 + np.exp(-eta))
        ll = np.sum(y1 * np.log(p) + (1 - y1) * np.log(1 - p))
        g = dX.T @ (y1 - p)
        H = -(dX * (p * (1 - p))[:, None]).T @ dX
        try:
            step = np.linalg.solve(H, -g)
        except np.linalg.LinAlgError:
            step = np.linalg.lstsq(H, -g, rcond=None)[0]
        b_new = b + step
        # simple step halving
        t = 1.0
        while True:
            eta2 = dX @ (b + t * step)
            p2 = 1 / (1 + np.exp(-eta2))
            ll2 = np.sum(y1 * np.log(np.clip(p2, 1e-300, 1)) + (1 - y1) * np.log(np.clip(1 - p2, 1e-300, 1)))
            if ll2 >= ll - 1e-12 or t < 1e-6:
                break
            t /= 2
        b = b + t * step
        if abs(ll2 - ll) < 1e-12 and np.max(np.abs(t * step)) < 1e-9:
            break
    eta = dX @ b
    p = 1 / (1 + np.exp(-eta))
    ll = np.sum(y1 * np.log(p) + (1 - y1) * np.log(1 - p))
    H = -(dX * (p * (1 - p))[:, None]).T @ dX
    Hinv = np.linalg.pinv(-H)
    scores = dX * (y1 - p)[:, None]
    codes, uniq = pd.factorize(cl)
    S = np.zeros((len(uniq), k))
    np.add.at(S, codes, scores)
    G = len(uniq)
    meat = S.T @ S
    V = (G / (G - 1)) * Hinv @ meat @ Hinv
    f = Fit()
    f.b, f.V, f.names, f.ll, f.N, f.G = b, V, list(X), ll, len(d), G
    f.se = np.sqrt(np.diag(V))
    f.idx = {n: i for i, n in enumerate(X)}
    f.nsets = len(first)
    f.rank = int(np.linalg.matrix_rank(dX))
    return f


def nlcom(fit, func, h=1e-6):
    """Delta method. func maps a dict name->coef to a scalar (or list). Returns (est, se) arrays."""
    b = fit.b
    def ev(bb):
        r = func({n: bb[i] for n, i in fit.idx.items()})
        return np.atleast_1d(np.asarray(r, float))
    est = ev(b)
    J = np.zeros((len(est), len(b)))
    for j in range(len(b)):
        step = h * max(1.0, abs(b[j]))
        bp, bm = b.copy(), b.copy()
        bp[j] += step
        bm[j] -= step
        J[:, j] = (ev(bp) - ev(bm)) / (2 * step)
    Vf = J @ fit.V @ J.T
    return est, np.sqrt(np.diag(Vf)), Vf


def wald(fit, R, r=None):
    """Wald chi2 test of R b = r. R: list of dicts {name: coef} or (m x k) array. Returns chi2, df, p."""
    if not isinstance(R, np.ndarray):
        M = np.zeros((len(R), len(fit.b)))
        for i, row in enumerate(R):
            for n, c in row.items():
                M[i, fit.idx[n]] = c
        R = M
    r = np.zeros(R.shape[0]) if r is None else np.asarray(r, float)
    diff = R @ fit.b - r
    W = float(diff @ np.linalg.solve(R @ fit.V @ R.T, diff))
    df = R.shape[0]
    return W, df, float(stats.chi2.sf(W, df))


def invlogit(x):
    return 1 / (1 + np.exp(-x))


def normal_cdf(x):
    return 0.5 * (1 + erf(x / sqrt(2)))


def wilson(k, n):
    z = stats.norm.ppf(0.975)
    p = k / n
    den = 1 + z ** 2 / n
    c = (p + z ** 2 / (2 * n)) / den
    h = z * np.sqrt(p * (1 - p) / n + z ** 2 / (4 * n ** 2)) / den
    return 100 * (c - h), 100 * (c + h)
