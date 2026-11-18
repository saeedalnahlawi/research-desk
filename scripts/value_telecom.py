#!/usr/bin/env python3
"""Telecom valuation engine: DCF + EV/EBITDA + P/E, reconciled rather than blended.

Built for operators whose economics are: long capex cycles, high EBITDA margins, modest
revenue growth, and a peer set that is usually larger than the subject. It exists because a
generic DCF hides the two things that decide a telecom's value — capex intensity and the
terminal assumption — and because blending three methods without checking that they agree
is how a 17x P/E gets published as "fair value" for a 12x sector.

  python3 scripts/value_telecom.py --profile profiles/jtel.json
  python3 scripts/value_telecom.py --profile profiles/jtel.json --beta 1.0 --discount 0.30

Outputs: forecast, WACC with market weights, DCF, peer multiples with a stated discount,
football field, reverse DCF (what the price implies), and a sensitivity grid.
"""
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path


def load(path: str) -> dict:
    return json.loads(Path(path).read_text())


def fmt(x: float, dp: int = 2) -> str:
    return f"{x:,.{dp}f}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", required=True)
    ap.add_argument("--beta", type=float)
    ap.add_argument("--rf", type=float)
    ap.add_argument("--erp", type=float)
    ap.add_argument("--g", type=float)
    ap.add_argument("--discount", type=float, help="peer multiple discount (size/liquidity)")
    ap.add_argument("--margin", type=float, help="override EBITDA margin")
    ap.add_argument("--capex", type=float, help="override capex %% of revenue")
    a = ap.parse_args()

    p = load(a.profile)
    f, w, peers = p["forecast"], dict(p["wacc"]), p.get("peers", {})
    if a.rf is not None:
        w["rf"] = a.rf
    if a.beta is not None:
        w["beta"] = a.beta
    if a.erp is not None:
        w["erp"] = a.erp
    g = a.g if a.g is not None else p["terminal_g"]
    disc = a.discount if a.discount is not None else peers.get("discount_for_size_liquidity", 0.0)
    margin = a.margin if a.margin is not None else f["ebitda_margin"]
    capex_pct = a.capex if a.capex is not None else f["capex_pct_of_revenue"]
    tax = p["tax_rate"]
    shares = p["shares_m"]
    price = p["price"]

    print(f"=== {p['name']} · FY{p['base_year']} base · {p['currency']} m ===")
    print(f"  revenue {fmt(p['revenue'])} | EBITDA {fmt(p['ebitda'])} ({p['ebitda']/p['revenue']:.1%}) "
          f"| D&A {fmt(p['da'])} | capex {fmt(p['capex'])} ({capex_pct:.1%} of revenue)")
    print(f"  net debt {fmt(p['net_debt'])} | book equity {fmt(p['book_equity'])} | shares {shares:.1f}m "
          f"| price {price:.2f} ({p.get('price_date','')})")
    pb = f"{price*shares/p['book_equity']:.2f}x" if p.get("book_equity") else "n/a (no equity tag)"
    print(f"  market cap {fmt(price*shares)} | P/E {price/(p['net_income']/shares):.1f}x | P/B {pb}")

    # ---------- WACC with market weights ----------
    ke = w["rf"] + w["beta"] * w["erp"]
    e_mv = price * shares
    d = p["gross_debt"]
    if w.get("use_market_weights", True):
        wd = d / (d + e_mv)
    else:
        wd = d / (d + p["book_equity"])
    we = 1 - wd
    wacc = we * ke + wd * w["kd"] * (1 - tax)
    print(f"\n=== WACC (market weights) ===")
    print(f"  ke = {w['rf']:.2%} + {w['beta']:.2f} x {w['erp']:.2%} = {ke:.2%}")
    print(f"  kd {w['kd']:.2%} after tax {w['kd']*(1-tax):.2%} | weights E {we:.1%} / D {wd:.1%}")
    print(f"  WACC = {wacc:.2%}")
    if not w.get("use_market_weights", True):
        wd_b = d / (d + p["book_equity"])
        alt = (1-wd_b)*ke + wd_b*w["kd"]*(1-tax)
        print(f"  NOTE: book weights would give {alt:.2%} — market weights are the correct basis.")

    # ---------- forecast ----------
    years = f["years"]
    rows, rev = [], p["revenue"]
    print(f"\n=== forecast ({years}y, {'mid-year' if f.get('mid_year_convention') else 'year-end'} discounting) ===")
    print("  year    revenue   EBITDA    EBIT   NOPAT    capex    dNWC    FCFF")
    for i in range(years):
        prev = rev
        rev *= 1 + f["revenue_growth"][min(i, len(f["revenue_growth"])-1)]
        ebitda = rev * margin
        da = rev * f["da_pct_of_revenue"]
        ebit = ebitda - da
        nopat = ebit * (1 - tax)
        capex = rev * capex_pct
        dnwc = (rev - prev) * f["nwc_pct_of_revenue_change"]
        fcff = nopat + da - capex - dnwc
        rows.append(dict(year=p["base_year"]+1+i, rev=rev, ebitda=ebitda, ebit=ebit, fcff=fcff))
        print(f"  {p['base_year']+1+i} {fmt(rev):>9} {fmt(ebitda):>8} {fmt(ebit):>7} "
              f"{fmt(nopat):>7} {fmt(capex):>8} {fmt(dnwc):>7} {fmt(fcff):>7}")

    def dcf(wacc_r: float, g_r: float) -> tuple[float, float, float]:
        if wacc_r - g_r < 0.002:      # Gordon breaks down as wacc -> g
            return float("inf"), float("inf"), float("inf")
        mid = 0.5 if f.get("mid_year_convention") else 0.0
        pv = sum(r["fcff"] / (1 + wacc_r) ** (i + 1 - mid) for i, r in enumerate(rows))
        tv = rows[-1]["fcff"] * (1 + g_r) / (wacc_r - g_r)
        pv_tv = tv / (1 + wacc_r) ** (years - mid)
        ev = pv + pv_tv
        return ev, pv, pv_tv

    ev, pv, pv_tv = dcf(wacc, g)
    eq = ev - p["net_debt"]
    ps_dcf = eq / shares
    print(f"\n=== DCF ===")
    print(f"  PV explicit {fmt(pv)} ({pv/ev:.0%}) | PV terminal {fmt(pv_tv)} ({pv_tv/ev:.0%}) | EV {fmt(ev)}")
    print(f"  equity = EV {fmt(ev)} - net debt {fmt(p['net_debt'])} = {fmt(eq)}")
    print(f"  fair value {fmt(ps_dcf)} {p['currency']}/share vs market {price:.2f} ({ps_dcf/price-1:+.0%})")
    pb2 = f"{ps_dcf*shares/p['book_equity']:.2f}x" if p.get("book_equity") else "n/a"
    print(f"  implied P/E at that value {ps_dcf/(p['net_income']/shares):.1f}x | P/B {pb2}")

    # ---------- multiples ----------
    print(f"\n=== peer multiples (discount {disc:.0%} for size/liquidity) ===")
    legs = {}
    if peers.get("ev_ebitda"):
        med_ev = statistics.median(peers["ev_ebitda"])
        adj = med_ev * (1 - disc)
        ev_m = adj * p["ebitda"]
        ps = (ev_m - p["net_debt"]) / shares
        legs["EV/EBITDA"] = ps
        print(f"  peers median {med_ev:.2f}x -> adjusted {adj:.2f}x | EV {fmt(ev_m)} | "
              f"{fmt(ps)} {p['currency']}/share")
    if peers.get("pe"):
        med_pe = statistics.median(peers["pe"])
        adj_pe = med_pe * (1 - disc)
        ps = adj_pe * p["net_income"] / shares
        legs["P/E"] = ps
        print(f"  peers median {med_pe:.1f}x -> adjusted {adj_pe:.1f}x | "
              f"{fmt(ps)} {p['currency']}/share")

    # ---------- reconciliation: why the methods disagree ----------
    ni = p["net_income"]
    if "EV/EBITDA" in legs and "P/E" in legs:
        pe_ev_ebitda = (legs["P/E"] * shares + p["net_debt"]) / p["ebitda"]
        eve_pe = ((legs["EV/EBITDA"] * shares + p["net_debt"]) / ni)
        print(f"\n=== reconciliation ===")
        print(f"  D&A / revenue            {p['da']/p['revenue']:.1%}  (drives the whole gap)")
        print(f"  net debt / EBITDA        {p['net_debt']/p['ebitda']:.2f}x")
        print(f"  effective tax            {tax:.1%}")
        print(f"  the P/E leg implies EV/EBITDA of {pe_ev_ebitda:.2f}x, against the peer median "
              f"{statistics.median(peers.get('ev_ebitda',[0])):.2f}x")
        print(f"  the EV/EBITDA leg implies a P/E of {eve_pe:.1f}x, against the peer median "
              f"{statistics.median(peers.get('pe',[0])):.1f}x")
        print(f"  -> the two peer sets are not describing the same company. For a capital-intensive "
              f"operator with heavy D&A, EV/EBITDA is the primary method; P/E is a sanity check and "
              f"the divergence must be explained, not averaged.")

    # ---------- football field, reconciled not blended ----------
    print(f"\n=== football field ===")
    table = [("DCF", ps_dcf)] + list(legs.items())
    for name, v in table:
        print(f"  {name:10} {fmt(v):>8} {p['currency']}  ({v/price-1:+6.0%} vs market)")
    lo = min(v for _, v in table)
    hi = max(v for _, v in table)
    print(f"  range {fmt(lo)} - {fmt(hi)} | market {price:.2f}")
    spread = hi/lo - 1
    if spread > 0.25:
        print(f"  WARNING: methods disagree by {spread:.0%}. Do not average them — explain the gap "
              f"(usually capex or terminal growth) or publish the range as the answer.")
    else:
        print(f"  Methods agree within {spread:.0%} — a central estimate is defensible.")

    # ---------- plausibility gate ----------
    warnings = []
    if ps_dcf > price * 2:
        warnings.append(f"DCF is {ps_dcf/price:.1f}x the market price — check WACC, capex and D&A before publishing")
    if ps_dcf < price * 0.5:
        warnings.append(f"DCF is {ps_dcf/price:.1f}x the market price — check the growth path and terminal value")
    impl_ev_ebitda = (ps_dcf * shares + p["net_debt"]) / p["ebitda"]
    if impl_ev_ebitda > 15 or impl_ev_ebitda < 2:
        warnings.append(f"implied EV/EBITDA of {impl_ev_ebitda:.1f}x is outside any telecom range")
    if p["capex"] / p["revenue"] < 0.08:
        warnings.append(f"capex at {p['capex']/p['revenue']:.1%} of revenue is below maintenance level for a telecom")
    if warnings:
        print("\n=== PLAUSIBILITY WARNINGS ===")
        for w in warnings:
            print(f"  ! {w}")
        print("  A telecom valuation that fails these checks is usually a data problem, not an insight.")

    # ---------- reverse DCF ----------
    mid = 0.5 if f.get("mid_year_convention") else 0.0
    def price_of(wacc_r: float, g_r: float) -> float:
        e, _, _ = dcf(wacc_r, g_r)
        return (e - p["net_debt"]) / shares
    lo_w, hi_w = 0.03, 0.60
    for _ in range(100):
        m = (lo_w + hi_w) / 2
        if price_of(m, g) > price:
            lo_w = m
        else:
            hi_w = m
    lo_g, hi_g = -0.10, 0.12          # value rises with g, so solve downwards when value > price
    for _ in range(100):
        m = (lo_g + hi_g) / 2
        if price_of(wacc, m) > price:
            hi_g = m
        else:
            lo_g = m
    print(f"\n=== reverse DCF: what the market price implies ===")
    print(f"  at g {g:.1%}: implied WACC {lo_w:.2%} (model {wacc:.2%})")
    print(f"  at WACC {wacc:.2%}: implied terminal growth {lo_g:.2%} (model {g:.1%})")
    print(f"  at model WACC and g, fair value is {ps_dcf/price-1:+.0%} versus the market — "
          f"the gap is the market's growth or risk premium, not an error.")

    # ---------- sensitivity ----------
    print(f"\n=== sensitivity: fair value {p['currency']}/share (WACC x g) ===")
    for dw in (-0.02, -0.01, 0.0, 0.01, 0.02):
        cells = []
        for gg in (g - 0.01, g, g + 0.01):
            e, _, _ = dcf(wacc + dw, gg)
            cells.append(f"g{gg:.1%} {fmt((e - p['net_debt'])/shares):>7}")
        print(f"  WACC {wacc+dw:.2%}  " + " | ".join(cells))
    print(f"\n=== sensitivity: fair value {p['currency']}/share (EBITDA margin x capex % revenue) ===")
    print(f"  {'margin':>7} " + " ".join(f"capex{c:.0%}" for c in (capex_pct-0.03, capex_pct, capex_pct+0.03)))
    for dm in (-0.03, 0.0, 0.03):
        cells = []
        for dc in (-0.03, 0.0, 0.03):
            f2 = dict(f)
            rows2, rev2 = [], p["revenue"]
            for i in range(years):
                prev = rev2
                rev2 *= 1 + f2["revenue_growth"][min(i, len(f2["revenue_growth"])-1)]
                da = rev2 * f2["da_pct_of_revenue"]
                ebit = rev2 * (margin + dm) - da
                fcff = ebit*(1-tax) + da - rev2*(capex_pct+dc) - (rev2-prev)*f2["nwc_pct_of_revenue_change"]
                rows2.append(dict(fcff=fcff, year=p["base_year"]+1+i))
            pv2 = sum(r["fcff"]/(1+wacc)**(i+1-mid) for i, r in enumerate(rows2))
            tv2 = rows2[-1]["fcff"]*(1+g)/(wacc-g)/(1+wacc)**(years-mid)
            cells.append(fmt(((pv2+tv2)-p["net_debt"])/shares, 2))
        print(f"  {margin+dm:>7.1%} " + "     ".join(cells))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
