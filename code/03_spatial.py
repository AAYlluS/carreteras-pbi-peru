"""Step 3: spatial diagnostics (Table 4) and spatial-error IV model (Table 5).

Table 4: Moran's I and Lagrange multiplier tests on the residuals of the OLS
growth regression with controls and department fixed effects, on the 1,191
districts that define the contiguity matrix W.

Table 5: spatial-error model with road density instrumented by the log distance
to the Inca road, estimated by generalised spatial two-stage least squares
(GS2SLS) on the 1,141-district estimation sample, using the rows and columns
of W that belong to it.

The estimators are implemented in numpy from the published formulas:

[SP-spregress]  Stata Spatial Autoregressive Models Reference Manual, spregress
                and spivregress, "Methods and formulas: GS2SLS estimator".
[SP-moran]      Stata manual, estat moran, "Methods and formulas".
[DEP2013]       Drukker, Egger & Prucha (2013), Econometric Reviews 32: 686-733
                (two-step GS2SLS/GMM with endogenous regressors; homoskedastic
                Psi matrix and joint VCE of delta and rho).
[DPR2013]       Drukker, Prucha & Raciborski (2013), Stata Journal 13(2): 287-301.
[ADKP2010]      Arraiz, Drukker, Kelejian & Prucha (2010), J. Regional Science 50:
                592-614 (step sequence 1a/1b/2a/2b; initial GMM with identity weight).
[Anselin1988/1996] Anselin (1988), Anselin, Bera, Florax & Yoon (1996): LM-error,
                LM-lag and their robust versions; Cliff-Ord Moran's I for regression
                residuals.

Run from the repository root:  python code/03_spatial.py
Deterministic: no random numbers; the GMM objective is a quartic in rho and is
minimised exactly through the real roots of its derivative.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import L1, L2, RAW, TABLES, load_analysis, stata_encode  # noqa: E402

CONTROLS = ["Edu_2007", "Agro", "MYPE", "Minero", "Urbano"]
ENDOG = "Densidad_Total"
INSTR = "ln_dist_inca"


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
def load_samples() -> dict:
    """Build the 1,191-district W sample and the 1,141-district estimation sample.

    W sample: districts not excluded (Drop != "Si") with complete data on L1,
    sorted by Id; W.dta is the first-order contiguity matrix of these districts
    (spectral normalisation). The estimation sample additionally requires
    complete data on L2; it uses the corresponding rows and columns of W,
    without re-normalisation.
    """
    d = load_analysis("main")
    d = d[d["Drop"] != "Si"].dropna(subset=L1).sort_values("Id").reset_index(drop=True)
    W = pd.read_stata(RAW / "W.dta").to_numpy(dtype=float)
    if W.shape != (len(d), len(d)):
        raise ValueError(f"W is {W.shape}, sample has {len(d)} rows")
    d = transform(d)
    keep = d[L2].notna().all(axis=1).to_numpy()
    d2 = d[keep].reset_index(drop=True)
    d2["dpto"] = stata_encode(d2["dpto_nombre"])
    d["dpto"] = stata_encode(d["dpto_nombre"])
    return {"d1191": d, "W1191": W, "d1141": d2, "W1141": W[np.ix_(keep, keep)]}


def transform(d: pd.DataFrame) -> pd.DataFrame:
    """Variable transformations used by the Table 4/5 models."""
    d = d.copy()
    d["Urbano"] = np.log(d["Urbano"])
    # MYPE in logs; districts with zero or missing MYPE get ln(1e-6).
    m = d["MYPE"].where(d["MYPE"] > 0)
    d["MYPE"] = np.log(m).fillna(np.log(0.000001))
    return d


def design(d: pd.DataFrame, fe: bool = True, controls=CONTROLS):
    """Return y, exogenous X (controls, i.dpto dummies with base 1, constant last),
    endogenous regressor and excluded instrument, plus column names."""
    cols = list(controls)
    X = d[cols].to_numpy(float)
    names = cols[:]
    if fe:
        lev = sorted(d["dpto"].unique())
        D = np.column_stack([(d["dpto"] == k).to_numpy(float) for k in lev[1:]])
        X = np.column_stack([X, D])
        names += [f"{k}.dpto" for k in lev[1:]]
    X = np.column_stack([X, np.ones(len(d))])
    names.append("_cons")
    return (d["Tasa"].to_numpy(float), X, d[[ENDOG]].to_numpy(float),
            d[[INSTR]].to_numpy(float), names)


# ---------------------------------------------------------------------------
# Linear-algebra helpers
# ---------------------------------------------------------------------------
def independent_columns(A: np.ndarray, tol: float = 1e-9) -> np.ndarray:
    """Keep the linearly independent columns of A, scanning left to right
    (a column collinear with earlier ones is dropped).
    [SP-spregress]: "H1 contains the linearly independent columns in ...".
    """
    Q = np.zeros((A.shape[0], 0))
    keep = []
    for j in range(A.shape[1]):
        a = A[:, j]
        nrm = np.linalg.norm(a)
        if nrm == 0:
            continue
        r = a - Q @ (Q.T @ a)
        r = r - Q @ (Q.T @ r)  # re-orthogonalise for stability
        if np.linalg.norm(r) / nrm > tol:
            Q = np.column_stack([Q, r / np.linalg.norm(r)])
            keep.append(j)
    return A[:, keep]


def tsls(y, Z, H):
    """2SLS: delta = (Zhat'Zhat)^-1 Zhat'y, Zhat = P_H Z ([SP-spregress], eq. for
    the 2SLS estimator of delta)."""
    HtH_inv = np.linalg.pinv(H.T @ H)
    Zhat = H @ (HtH_inv @ (H.T @ Z))
    return np.linalg.solve(Zhat.T @ Zhat, Zhat.T @ y)


def a1_matrix(M, kind: str):
    """First GMM moment matrix.

    'het'    : A1 = M'M - diag(M'M)  ([SP-spregress] "B = M'M - diag(M'M)";
               [ADKP2010]). Stata documents this single form.
    'hom_sc' : A1 = {1+[tr(M'M)/n]^2}^-1 [M'M - tr(M'M)/n I]  ([DPR2013], sppack
               homoskedastic case; also spreg's A1='hom_sc').
    """
    n = M.shape[0]
    MtM = M.T @ M
    if kind == "het":
        return MtM - np.diag(np.diag(MtM))
    t = np.trace(MtM) / n
    A = MtM - t * np.eye(n)
    return A / (1.0 + t ** 2) if kind == "hom_sc" else A


def gmm_moments(u, M, As):
    """Sample moments g(rho) = gamma - Gamma [rho, rho^2]' for eps = u - rho*M u,
    using E[eps' A_r eps]/n = 0 ([DEP2013] eqs. for the GM estimator of rho;
    [SP-spregress] "GMM estimator of rho based on 2SLS residuals")."""
    n = len(u)
    ub = M @ u
    gam = np.array([u @ A @ u for A in As]) / n
    Gam = np.array([[u @ (A + A.T) @ ub, -(ub @ A @ ub)] for A in As]) / n
    return gam, Gam


def gmm_rho(gam, Gam, Ups, bounds=(-0.99999, 0.99999)):
    """argmin_rho (gam - Gam[rho,rho^2]')' Ups (gam - Gam[rho,rho^2]').
    The objective is a quartic in rho; take the global minimum over the
    admissible interval |rho|<1 ([DEP2013] assume |rho|<1) exactly."""
    c0, c1, c2 = gam, -Gam[:, 0], -Gam[:, 1]  # r(rho) = c0 + c1 rho + c2 rho^2
    q = lambda a, b: float(a @ Ups @ b)
    poly = np.array([q(c2, c2), 2 * q(c1, c2), q(c1, c1) + 2 * q(c0, c2),
                     2 * q(c0, c1), q(c0, c0)])  # descending powers
    crit = np.roots(np.polyder(poly))
    cand = [bounds[0], bounds[1]] + [r.real for r in crit
                                     if abs(r.imag) < 1e-10 and bounds[0] < r.real < bounds[1]]
    vals = [np.polyval(poly, r) for r in cand]
    return float(cand[int(np.argmin(vals))])


def psi_hom(eps, As, H, P, Ztil, rho_unused=None):
    """Homoskedastic VC matrix of the moments and its delta-rho block,
    [DEP2013] (homoskedastic case), with a_r = H P alpha_r and
    alpha_r = -n^-1 Ztil'(A_r + A_r') eps:
      psi_rs = sig^4/(2n) tr[(A_r+A_r')(A_s+A_s')] + sig^2/n a_r'a_s
               + (mu4-3 sig^4)/n vecD(A_r)'vecD(A_s)
               + mu3/n [a_r'vecD(A_s) + a_s'vecD(A_r)]
      psi_dr  = sig^2/n H'a_r + mu3/n H'vecD(A_r)
    """
    n = len(eps)
    s2 = eps @ eps / n
    mu3 = np.sum(eps ** 3) / n
    mu4 = np.sum(eps ** 4) / n
    S = len(As)
    a = [H @ (P @ (-(Ztil.T @ ((A + A.T) @ eps)) / n)) for A in As]
    vd = [np.diag(A) for A in As]
    Psi = np.empty((S, S))
    for r in range(S):
        for s in range(S):
            Psi[r, s] = (s2 ** 2 / (2 * n) * np.trace((As[r] + As[r].T) @ (As[s] + As[s].T))
                         + s2 / n * a[r] @ a[s]
                         + (mu4 - 3 * s2 ** 2) / n * vd[r] @ vd[s]
                         + mu3 / n * (a[r] @ vd[s] + a[s] @ vd[r]))
    Psi_dr = np.column_stack([s2 / n * H.T @ a[r] + mu3 / n * H.T @ vd[r] for r in range(S)])
    return Psi, Psi_dr, s2


def p_matrix(H, Ztil):
    """P = (H'H/n)^-1 (H'Z/n) [(Z'H/n)(H'H/n)^-1(H'Z/n)]^-1 ([DEP2013])."""
    n = H.shape[0]
    Qhh_inv = np.linalg.pinv(H.T @ H / n)
    Qhz = H.T @ Ztil / n
    return Qhh_inv @ Qhz @ np.linalg.inv(Qhz.T @ Qhh_inv @ Qhz)


# ---------------------------------------------------------------------------
# GS2SLS for the spatial-error model with an endogenous regressor
# ---------------------------------------------------------------------------
def build_instruments(X, q, M, scheme: str = "stata", impower: int = 2):
    """Instrument matrices for step 1 (H1) and step 2 (H2).

    'stata' : [SP-spregress] H1 = indep. cols of [X*, W1 X*, ..., W^q X*], where
              W1 is the set of matrices applied to the DEPENDENT variable. The
              model has errorlag(W) only, so W1 is empty and H1 = [X*] with X* =
              (exogenous regressors incl. constant and dummies, excluded
              instrument) ([SP] spivregress: instruments are added to X*).
              H2 = indep. cols of [H1, M H1] ([SP-spregress] "GS2SLS estimator").
    'sppack': [DPR2013]/[DEP2013] style: H = [X*, M X*, ..., M^q X*] (powers of
              the weighting matrix, impower default 2) used in both steps.
    'sppack_h2': H1 as 'sppack'; H2 = [H1, M H1] (Stata's step-2 rule applied
              on top of the power instruments).
    'none'  : H = [X*] in both steps (spreg default, no spatial instruments).
    """
    Xs = np.column_stack([X, q])
    if scheme in ("stata", "none"):
        H1 = independent_columns(Xs)
    else:
        blocks, B = [Xs], Xs
        for _ in range(impower):
            B = M @ B
            blocks.append(B)
        H1 = independent_columns(np.column_stack(blocks))
    if scheme in ("stata", "sppack_h2"):
        H2 = independent_columns(np.column_stack([H1, M @ H1]))
    else:
        H2 = H1
    return H1, H2


def gs2sls_sem_iv(y, X, Yend, q, M, scheme="stata", a1="het", impower=2,
                  vce_at="initial"):
    """GS2SLS for y = [Yend, X] delta + u, u = rho M u + eps (homoskedastic),
    i.e. Stata `spivregress y X (Yend = q), gs2sls errorlag(M)`.

    Steps ([SP-spregress] "GS2SLS estimator"; [ADKP2010]; [DEP2013]):
      1a  2SLS of y on Z=[Yend, X] with H1                  -> delta~, u~
      1b  GMM for rho from u~, weighting matrix I             -> rho~
      2a  2SLS of (I-rho~M)y on (I-rho~M)Z with H2             -> delta^, u^
      2b  efficient GMM for rho from u^, weight Psi^-1 (hom.,
          evaluated at rho~ and u^)                             -> rho^
      VCE joint Omega of (delta^, rho^) from [DEP2013], homoskedastic case
          (see the comment on the evaluation point below).
    Returns a dict with coefficient vector (Yend, X..., rho) and std. errors.
    """
    n = len(y)
    Z = np.column_stack([Yend, X])
    H1, H2 = build_instruments(X, q, M, scheme, impower)
    As = [a1_matrix(M, a1), M]  # [SP-spregress]: moments with B (=A1) and A = M
    # 1a
    d1 = tsls(y, Z, H1)
    u1 = y - Z @ d1
    # 1b
    gam, Gam = gmm_moments(u1, M, As)
    rho1 = gmm_rho(gam, Gam, np.eye(2))
    # 2a  spatial Cochrane-Orcutt transform
    ys, Zs = y - rho1 * (M @ y), Z - rho1 * (M @ Z)
    d2 = tsls(ys, Zs, H2)
    u2 = y - Z @ d2
    # 2b  efficient GMM, Psi evaluated at rho~ with GS2SLS residuals
    eps = u2 - rho1 * (M @ u2)
    P = p_matrix(H2, Zs)
    Psi, _, _ = psi_hom(eps, As, H2, P, Zs)
    gam, Gam = gmm_moments(u2, M, As)
    rho2 = gmm_rho(gam, Gam, np.linalg.inv(Psi))
    # VCE: joint Omega of (delta^, rho^), homoskedastic case ([DEP2013]).
    # Evaluation point: the delta-block and Psi use the step-2a quantities
    # actually used in the GS2SLS regression, Z~ = (I - rho~ M)Z and
    # eps = (I - rho~ M)u^ (i.e. sigma2 is the step-2a 2SLS residual variance);
    # J = Gamma [1, 2 rho^]' uses the final rho^. Both evaluation points are
    # consistent and the manuals leave this implicit; vce_at="final" gives the
    # spreg / Anselin (2011) convention.
    r_v = rho1 if vce_at == "initial" else rho2
    Zt = Z - r_v * (M @ Z)
    eps = u2 - r_v * (M @ u2)
    P = p_matrix(H2, Zt)
    Psi, Psi_dr, s2 = psi_hom(eps, As, H2, P, Zt)
    gam, Gam = gmm_moments(u2, M, As)
    J = Gam @ np.array([1.0, 2 * rho2])
    Pinv = np.linalg.inv(Psi)
    o_rr = 1.0 / (J @ Pinv @ J)
    Psi_dd = s2 * H2.T @ H2 / n
    O_dd = P.T @ Psi_dd @ P
    O_dr = P.T @ Psi_dr @ Pinv @ J * o_rr
    k = Z.shape[1]
    Om = np.zeros((k + 1, k + 1))
    Om[:k, :k], Om[:k, k], Om[k, :k], Om[k, k] = O_dd, O_dr, O_dr, o_rr
    V = Om / n
    b = np.append(d2, rho2)
    return {"b": b, "se": np.sqrt(np.diag(V)), "V": V, "rho_initial": rho1,
            "delta_2sls": d1, "n": n, "H1_cols": H1.shape[1], "H2_cols": H2.shape[1],
            "sigma2": s2}


# ---------------------------------------------------------------------------
# Diagnostics after OLS
# ---------------------------------------------------------------------------
def ols(y, X):
    b = np.linalg.lstsq(X, y, rcond=None)[0]
    return b, y - X @ b


def estat_moran(y, X, W):
    """Stata `regress y X` then `estat moran, errorlag(W)` ([SP-moran]):
    I = u'Wu / (sig2 [tr{(W'+W)W}]^1/2), sig2 = u'u/n, chi2(1) = I^2
    (Kelejian & Prucha 2001)."""
    _, u = ols(y, X)
    n = len(u)
    s2 = u @ u / n
    I = (u @ W @ u) / (s2 * np.sqrt(np.trace((W.T + W) @ W)))
    chi2 = I ** 2
    return {"I_KP": I, "chi2": chi2, "p": stats.chi2.sf(chi2, 1)}


def spatdiag(y, X, W):
    """Spatial diagnostics of OLS residuals following [Anselin1988/1996]
    (as reported by the Stata command `spatdiag`); residuals e, sig2 = e'e/N:
      Moran's I = (N/S0) e'We/e'e, standardised with the Cliff-Ord moments
        E[I] = (N/S0) tr(MW)/(N-k),
        V[I] = (N/S0)^2 [tr(MWMW') + tr((MW)^2) + tr(MW)^2]/((N-k)(N-k+2)) - E[I]^2
      T = tr(W'W + WW); NJ = [(WXb)'M(WXb) + T sig2]/sig2
      LM-error = (e'We/sig2)^2 / T
      LM-lag   = (e'Wy/sig2)^2 / NJ
      robust LM-error = (e'We/sig2 - T/NJ e'Wy/sig2)^2 / (T - T^2/NJ)
      robust LM-lag   = (e'Wy/sig2 - e'We/sig2)^2 / (NJ - T)
    """
    n, k = X.shape
    b, e = ols(y, X)
    s2 = e @ e / n
    S0 = W.sum()
    XtX_inv = np.linalg.inv(X.T @ X)
    Mx = np.eye(n) - X @ XtX_inv @ X.T
    MW = Mx @ W
    I = n / S0 * (e @ W @ e) / (e @ e)
    EI = n / S0 * np.trace(MW) / (n - k)
    VI = (n / S0) ** 2 * (np.trace(MW @ Mx @ W.T) + np.trace(MW @ MW) + np.trace(MW) ** 2) \
        / ((n - k) * (n - k + 2)) - EI ** 2
    z = (I - EI) / np.sqrt(VI)
    T = np.trace(W.T @ W + W @ W)
    WXb = W @ (X @ b)
    NJ = (WXb @ Mx @ WXb + T * s2) / s2
    eWe, eWy = (e @ W @ e) / s2, (e @ W @ y) / s2
    out = {"moran_I": I, "moran_EI": EI, "moran_z": z,
           "lm_error": eWe ** 2 / T,
           "rlm_error": (eWe - T / NJ * eWy) ** 2 / (T - T ** 2 / NJ),
           "lm_lag": eWy ** 2 / NJ,
           "rlm_lag": (eWy - eWe) ** 2 / (NJ - T)}
    out["moran_p"] = 2 * stats.norm.sf(abs(z))
    for key in ("lm_error", "rlm_error", "lm_lag", "rlm_lag"):
        out[key + "_p"] = stats.chi2.sf(out[key], 1)
    return out


def check_with_pysal(y, X, W):
    """Independent check with spreg.OLS(spat_diag, moran) and esda.Moran."""
    import warnings

    import esda
    import libpysal
    import scipy.sparse as sp
    import spreg
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        w = libpysal.weights.WSP(sp.csr_matrix(W)).to_W(silence_warnings=True)
        w.transform = "O"
        r = spreg.OLS(y[:, None], X[:, :-1], w=w, spat_diag=True, moran=True)
        e = r.u.ravel()
        m = esda.Moran(e, w, transformation="O", permutations=0)
    return {"spreg_moran_I": r.moran_res[0], "spreg_moran_z": r.moran_res[1],
            "spreg_lm_error": r.lm_error[0], "spreg_lm_lag": r.lm_lag[0],
            "spreg_rlm_error": r.rlm_error[0], "spreg_rlm_lag": r.rlm_lag[0],
            "esda_moran_I": m.I}


# ---------------------------------------------------------------------------
# Tables
# ---------------------------------------------------------------------------
def run_table4(S) -> pd.DataFrame:
    """OLS of growth on road density, controls and department dummies on the
    1,191-district W sample; spatial diagnostics of the residuals."""
    d, W = S["d1191"], S["W1191"]
    y, X, Yend, _, _ = design(d, fe=True)
    Xf = np.column_stack([Yend, X])
    em = estat_moran(y, Xf, W)
    sd = spatdiag(y, Xf, W)
    ck = check_with_pysal(y, Xf, W)
    row = {"N": len(y), "k": Xf.shape[1],
           "moran_I": sd["moran_I"], "moran_z": sd["moran_z"], "moran_p": sd["moran_p"],
           "lm_error": sd["lm_error"], "lm_error_p": sd["lm_error_p"],
           "rlm_error": sd["rlm_error"], "rlm_error_p": sd["rlm_error_p"],
           "lm_lag": sd["lm_lag"], "lm_lag_p": sd["lm_lag_p"],
           "rlm_lag": sd["rlm_lag"], "rlm_lag_p": sd["rlm_lag_p"],
           "kp_moran_chi2": em["chi2"], "kp_moran_p": em["p"]}
    row.update({f"check_{k}": v for k, v in ck.items()})
    return pd.DataFrame([row])


def run_table5(S) -> pd.DataFrame:
    d, W = S["d1141"], S["W1141"]
    y, X, Yend, q, names = design(d, fe=True)
    names = [ENDOG] + names + ["lambda"]
    r = gs2sls_sem_iv(y, X, Yend, q, W)
    return pd.DataFrame({"variable": names, "coef": r["b"], "se": r["se"], "N": r["n"]})


def write_tables(t4, t5):
    TABLES.mkdir(parents=True, exist_ok=True)
    t4.to_csv(TABLES / "table4_spatial_tests.csv", index=False, float_format="%.6g")
    a = t4.iloc[0]
    md = ["# Table 4: tests for spatial dependence in the OLS residuals\n",
          f"OLS of growth on road density, controls and department fixed effects; N = {int(a.N)}. "
          "W = first-order contiguity matrix, spectral normalisation. Moran z, LM and robust LM "
          "follow Anselin (1988) and Anselin et al. (1996); KP chi2 is the Kelejian-Prucha "
          "version of the Moran test. The check_* columns of the CSV repeat the statistics "
          "with spreg/esda.\n",
          "| Test | Statistic | p-value |", "|---|---|---|",
          f"| Moran's I (z) | {a.moran_I:.3f} ({a.moran_z:.2f}) | {a.moran_p:.3f} |",
          f"| LM error | {a.lm_error:.2f} | {a.lm_error_p:.3f} |",
          f"| Robust LM error | {a.rlm_error:.2f} | {a.rlm_error_p:.3f} |",
          f"| LM lag | {a.lm_lag:.2f} | {a.lm_lag_p:.3f} |",
          f"| Robust LM lag | {a.rlm_lag:.3f} | {a.rlm_lag_p:.3f} |",
          f"| Moran, Kelejian-Prucha chi2(1) | {a.kp_moran_chi2:.2f} | {a.kp_moran_p:.3f} |"]
    (TABLES / "table4_spatial_tests.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    t5.to_csv(TABLES / "table5_spatial_iv.csv", index=False, float_format="%.6g")
    key = [ENDOG] + CONTROLS + ["_cons", "lambda"]
    md = ["# Table 5: spatial-error model, road density instrumented (GS2SLS)\n",
          "Growth on road density, Edu_2007, Agro, ln MYPE, Minero, ln Urbano and department "
          "fixed effects; road density instrumented with ln distance to the Inca road; "
          "spatial-error term with W. lambda = spatial error parameter.\n",
          "| variable | coef | se |", "|---|---|---|"]
    for _, r in t5[t5.variable.isin(key)].iterrows():
        md.append(f"| {r.variable} | {r.coef:.4g} | {r.se:.4g} |")
    md.append(f"\nN = {int(t5.N.iloc[0])}")
    (TABLES / "table5_spatial_iv.md").write_text("\n".join(md) + "\n", encoding="utf-8")


def main():
    S = load_samples()
    t4 = run_table4(S)
    t5 = run_table5(S)
    write_tables(t4, t5)
    with pd.option_context("display.width", 250, "display.max_columns", 30):
        print(t4.round(3).T.to_string())
        print(t5[~t5.variable.str.endswith(".dpto")].round(5).to_string(index=False))


if __name__ == "__main__":
    main()
