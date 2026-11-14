"""Step 6: build the working paper (HTML + PDF) from paper/working_paper/text.md.

Every table is generated here from the outputs in output/tables,
and every figure is taken from output/figures, so the paper cannot drift from
the code. The PDF is printed with headless Microsoft Edge (or Chrome); if no
browser is found, only the HTML is written.

Output: paper/working_paper/working_paper.html and working_paper.pdf
"""
import base64
import re
import subprocess
import tempfile
from pathlib import Path

import markdown
import numpy as np
import pandas as pd
from scipy import stats

from common import FIGURES, ROOT, TABLES, fmt, stars

WP = ROOT / "paper" / "working_paper"
BROWSERS = [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/microsoft-edge"]

EN = {"Densidad_Total": "Road density",
      "ln_dist_inca": "ln distance to Inca road",
      "ln_dist_kruskal": "ln distance to Kruskal network", "Edu_2007": "Education 2007 (share)",
      "Agro": "Agriculture 2007 (share)", "MYPE": "MYPEs 2007", "Minero": "Mining 2007 (0/1)",
      "Urbano": "ln urban population 2007", "const": "Constant", "_cons": "Constant",
      "lambda": "λ (spatial error)"}
NOTE_FE = ("Robust standard errors in parentheses (OLS: HC1; 2SLS: HC0). All regressions include "
           "department fixed effects. First-stage F: robust F statistic of the excluded instrument. "
           "*** p<0.01, ** p<0.05, * p<0.1.")


def cell(coef, se, p):
    return f"{fmt(coef)}{stars(p)}", f"({fmt(se)})"


def reg_table(csv, title, heads, order, note):
    df = pd.read_csv(TABLES / csv)
    cols = list(dict.fromkeys(df.column))
    get = lambda c, v, s: df[(df.column == c) & (df.variable == v) & (df.stat == s)]
    rows = []
    for v in order:
        if not any(len(get(c, v, "coef")) for c in cols):
            continue
        r1, r2 = [EN.get(v, v)], [""]
        for c in cols:
            b, s = get(c, v, "coef"), get(c, v, "se")
            if len(b):
                x, y = cell(b.value.iloc[0], s.value.iloc[0], b.p.iloc[0])
            else:
                x, y = "", ""
            r1.append(x); r2.append(y)
        rows += [r1, r2]
    rows.append(["Observations"] + [f"{int(get(c, 'model', 'n').value.iloc[0]):,}" for c in cols])
    rows.append(["R²"] + [f"{get(c, 'model', 'r2').value.iloc[0]:.3f}" for c in cols])
    if any(len(get(c, "model", "F")) for c in cols):
        rows.append(["First-stage F"] + [
            (f"{get(c, 'model', 'F').value.iloc[0]:.2f}{stars(get(c, 'model', 'F').p.iloc[0])}"
             if len(get(c, "model", "F")) else "") for c in cols])
    head = [""] + [f"({i + 1})<br>{h}" for i, h in enumerate(heads)]
    return html_table(title, head, rows, note)


def html_table(title, head, rows, note):
    h = "".join(f"<th>{x}</th>" for x in head)
    b = "".join("<tr>" + "".join(f"<td>{x}</td>" for x in r) + "</tr>" for r in rows)
    return (f'<div class="tbl"><p class="cap">{title}</p><table><thead><tr>{h}</tr></thead>'
            f"<tbody>{b}</tbody></table><p class=\"tnote\">{note}</p></div>")


def table1():
    t = pd.read_csv(TABLES / "table1.csv")
    lab = {"PIB2007": "GDP per capita 2007 (soles)", "Tasa": "Growth of GDP per capita 2007-18 (log points)",
           "Edu_2007": "Education (share)", "Agro": "Agriculture (share)", "MYPE": "MYPEs (number)",
           "Urbano_level": "Urban population", "Minero": "Mining (0/1)"}
    rows = []
    for _, r in t.iterrows():
        big = r.variable in ("PIB2007", "Urbano_level")
        f = (lambda x: f"{x:,.0f}") if big else (lambda x: f"{x:.3f}" if r.variable != "MYPE" else f"{x:.2f}")
        rows.append([lab[r.variable], f(r.within50km_mean), f(r.within50km_sd), f(r.study_mean), f(r.study_sd)])
    n_out, n_in = int(t.within50km_n.iloc[0]), int(t.study_n.iloc[0])
    rows.append(["Districts", f"{n_out:,}", "", f"{n_in:,}", ""])
    head = ["", "Near capitals<br>mean", "<br>s.d.", "Study sample<br>mean", "<br>s.d."]
    return html_table("Table 1. Descriptive statistics, 2007", head, rows,
                      "Near capitals: districts within about 50 km of a departmental capital, excluded from "
                      "the estimation sample. Study sample: estimation sample of Tables 2 and 3. GDP from "
                      "Seminario and Palomino (2022); other variables from the 2007 Census and the author's data.")


def table4():
    t = pd.read_csv(TABLES / "table4_spatial_tests.csv")
    a = t.iloc[0]
    chi = lambda x: stats.chi2.sf(x, 1)
    rows = [["Moran's I (z)", f"{a.moran_I:.3f} ({a.moran_z:.2f})", f"{2 * stats.norm.sf(abs(a.moran_z)):.3f}"],
            ["LM error", f"{a.lm_error:.2f}", f"{chi(a.lm_error):.3f}"],
            ["Robust LM error", f"{a.rlm_error:.2f}", f"{chi(a.rlm_error):.3f}"],
            ["LM lag", f"{a.lm_lag:.2f}", f"{chi(a.lm_lag):.3f}"],
            ["Robust LM lag", f"{a.rlm_lag:.3f}", f"{chi(a.rlm_lag):.3f}"]]
    return html_table("Table 4. Tests for spatial dependence in the OLS residuals", ["Test", "Statistic", "p-value"],
                      rows, f"Residuals of equation (1) estimated by OLS with controls and department fixed "
                      f"effects on the {int(a.N):,} districts that define the contiguity matrix. W: first-order "
                      f"contiguity, spectral normalisation. p-values of 0.000 are below 0.0005.")


def table5():
    t = pd.read_csv(TABLES / "table5_spatial_iv.csv")
    order = ["Densidad_Total", "Edu_2007", "Agro", "MYPE", "Minero", "Urbano", "_cons", "lambda"]
    rows = []
    for v in order:
        r = t[t.variable == v].iloc[0]
        p = 2 * stats.norm.sf(abs(r.coef / r.se))
        a, b = cell(r.coef, r.se, p)
        rows += [[EN.get(v, v) if v != "MYPE" else "ln MYPEs 2007", a], ["", b]]
    rows.append(["Observations", f"{int(t.N.iloc[0]):,}"])
    return html_table("Table 5. Spatial-error model, road density instrumented (2007-2018)", ["", "Growth"], rows,
                      "Generalised spatial two-stage least squares (spatial-error model); road density "
                      "instrumented with the log distance to the Inca road. MYPEs enter as ln(MYPEs), with "
                      "ln(10<sup>-6</sup>) for districts with none. Department fixed effects included. "
                      "Standard errors in parentheses. *** p<0.01, ** p<0.05, * p<0.1.")


def table6():
    t = pd.read_csv(TABLES / "inference_checks.csv").set_index("statistic")["value"]
    f3 = lambda x: f"{x:.3f}"
    ci = lambda lo, hi: f"[{t[lo]:.3f}, {t[hi]:.3f}]"
    rows = [["Reduced form: growth on ln distance to Inca road", f"{t.reduced_form_coef:.4f} ({t.reduced_form_se:.4f})", f"p = {t.reduced_form_p:.2f}"],
            ["2SLS estimate (Table 3, col. 4)", f"{f3(t.iv_coef)} ({f3(t.iv_se)})", ""],
            ["2SLS 95% confidence interval", ci("iv_ci95_low", "iv_ci95_high"),
             f"[{t['effect_1sd__iv_ci95_low']:.3f}, {t['effect_1sd__iv_ci95_high']:.3f}]"],
            ["Anderson-Rubin 95% confidence set", ci("ar_set95_low", "ar_set95_high"),
             f"[{t['effect_1sd__ar_set95_low']:.3f}, {t['effect_1sd__ar_set95_high']:.3f}]"],
            ["OLS estimate (Table 3, col. 2)", f"{f3(t.ols_coef)} {ci('ols_ci95_low', 'ols_ci95_high')}",
             f"{t['effect_1sd__ols_coef']:.3f}"],
            ["Wu-Hausman test of exogeneity", f"F = {t.wu_hausman_F:.2f}", f"p = {t.wu_hausman_p:.2f}"],
            ["2SLS with the stricter exclusion flag (N = 939)", f"{f3(t.iv_coef_drop_alt)} ({f3(t.iv_se_drop_alt)})", ""]]
    return html_table("Table 6. What the 2SLS estimate rules out", ["", "Estimate (s.e.) or interval", "Per 1 s.d. of density"],
                      rows, f"Specification of Table 3, column 4. Instrument: ln distance to the Inca road. One standard "
                      f"deviation of road density = {t.sd_density:.3f} km per km²; the last column multiplies the "
                      f"estimate or interval by it (log points of 2007-2018 growth; s.d. of growth = {t.sd_growth:.2f}). "
                      f"Anderson-Rubin set: heteroskedasticity-robust test inversion on a grid with step 0.001.")


def figure(name, caption, note):
    png = FIGURES / f"{name}.png"
    if not png.exists():
        return f'<p class="missing">[Figure {name} not available: run code/05_figures.py]</p>'
    b64 = base64.b64encode(png.read_bytes()).decode()
    return (f'<figure><p class="cap">{caption}</p><img src="data:image/png;base64,{b64}" alt="{caption}">'
            f'<figcaption>{note}</figcaption></figure>')


CSS = """
@page { size: A4; margin: 22mm 22mm 24mm 22mm; }
body { font-family: Cambria, Georgia, 'Times New Roman', serif; font-size: 11pt; line-height: 1.45;
       color: #111; background: #fff; max-width: 760px; margin: 0 auto; padding: 0 16px; }
h1 { font-size: 18pt; text-align: center; margin: 0.4em 0 0.2em; line-height: 1.25; }
.author, .date { text-align: center; margin: 0.1em 0; }
.date { color: #555; font-size: 10pt; margin-bottom: 1.2em; }
h2 { font-size: 13pt; margin: 1.4em 0 0.4em; }
h3 { font-size: 11.5pt; font-style: italic; font-weight: normal; margin: 1em 0 0.3em; }
p { text-align: justify; margin: 0.45em 0; }
.abstract, .note { font-size: 10pt; margin: 0.8em 2em; }
.note { border: 1px solid #bbb; padding: 0.4em 0.8em; background: #f6f6f6; }
.eq { text-align: center; margin: 0.8em 0; }
.tbl, figure { margin: 1.2em 0; page-break-inside: avoid; break-inside: avoid; }
.cap { font-weight: bold; text-align: left; margin-bottom: 0.3em; }
table { border-collapse: collapse; margin: 0 auto; font-size: 9.5pt; }
thead th { border-top: 1.5px solid #000; border-bottom: 1px solid #000; padding: 3px 10px; font-weight: normal; }
tbody tr:last-child td { border-bottom: 1.5px solid #000; }
td { padding: 1px 10px; text-align: center; }
td:first-child { text-align: left; }
.tnote, figcaption { font-size: 8.5pt; color: #333; text-align: justify; margin-top: 0.3em; }
img { width: 100%; max-width: 560px; display: block; margin: 0 auto; }
.footnote { font-size: 9pt; }
.thanks { font-size: 9pt; color: #444; text-align: center; margin: -0.8em 2em 1.2em; }
.missing { color: #a00; }
@media (max-width: 600px) { .abstract, .note { margin: 0.8em 0; } table { font-size: 8.5pt; } }
"""


def main() -> None:
    src = (WP / "text.md").read_text(encoding="utf-8")
    fm, body = re.match(r"---\n(.*?)\n---\n(.*)", src, re.S).groups()
    meta = dict(re.findall(r'(\w+): "(.*)"', fm))

    tables = {
        "table1": table1(),
        "table2": reg_table("table2.csv", "Table 2. First stage: road density on the candidate instruments",
                            ["Road density", "Road density"],
                            ["ln_dist_inca", "ln_dist_kruskal", "Edu_2007", "Agro", "MYPE", "Minero", "Urbano", "const"],
                            NOTE_FE),
        "table3": reg_table("table3.csv", "Table 3. Road density and growth of GDP per capita, 2007-2018",
                            ["OLS", "OLS", "2SLS", "2SLS"],
                            ["Densidad_Total", "Edu_2007", "Agro", "MYPE", "Minero", "Urbano", "const"],
                            NOTE_FE + " Columns 1 and 3 have one more district than columns 2 and 4 "
                                      "because MYPEs are missing for one district."),
        "table4": table4(),
        "table5": table5(),
        "table6": table6(),
    }
    # Placeholders are replaced after Markdown conversion; protect them first.
    keep = {}

    def stash(m):
        key = f"@@BLOCK{len(keep)}@@"
        kind, arg = m.group(1), m.group(2)
        if kind == "TABLE":
            keep[key] = tables[arg]
        else:
            name, cap, note = (arg.split("|") + ["", ""])[:3]
            keep[key] = figure(name, cap, note)
        return "\n\n" + key + "\n\n"

    body = re.sub(r"\{\{(TABLE|FIGURE):([^}]*)\}\}", stash, body)
    html_body = markdown.markdown(body, extensions=["footnotes", "md_in_html"])
    for k, v in keep.items():
        html_body = html_body.replace(f"<p>{k}</p>", v).replace(k, v)

    html = (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>{meta["title"]}</title><style>{CSS}</style></head><body>'
            f'<h1>{meta["title"]}</h1><p class="author">{meta["author"]}<sup>*</sup></p>'
            f'<p class="date">{meta["date"]}</p>'
            f'<p class="thanks"><sup>*</sup> {meta["thanks"]}</p>{html_body}</body></html>')
    out_html = WP / "working_paper.html"
    out_html.write_text(html, encoding="utf-8")
    print(f"wrote {out_html.relative_to(ROOT)}")

    exe = next((b for b in BROWSERS if Path(b).exists()), None)
    if not exe:
        print("No Edge/Chrome found: open working_paper.html and print to PDF.")
        return
    pdf = WP / "working_paper.pdf"
    with tempfile.TemporaryDirectory() as prof:
        subprocess.run([exe, "--headless=new", "--disable-gpu", "--no-first-run", "--no-pdf-header-footer",
                        f"--user-data-dir={prof}", f"--print-to-pdf={pdf}", out_html.resolve().as_uri()],
                       capture_output=True, timeout=180)
    print(f"wrote {pdf.relative_to(ROOT)}" if pdf.exists() else "PDF rendering failed")


if __name__ == "__main__":
    main()
