#!/usr/bin/env python3
"""
explore_mxaod.py

Opens MxAOD (DAOD_HIGG1D1) ROOT files directly via uproot to investigate
jet GN2v01 b-tagging discriminant distributions, split by truth flavour.

Motivated by the observation that reducing the PCBT working point from 85%
to 65% does not reduce the light-jet background as strongly as expected.
The PCBT score (bin 1-6) is derived from the GN2v01 log-likelihood:

    D_b = ln( p_b / (f_c*p_c + f_tau*p_tau + (1 - f_c - f_tau)*p_u) )
    with f_c = 0.2, f_tau = 0.01

    WP65 : D_b > +2.669  (PCBT bin >= 6)
    WP70 : D_b > +1.892  (PCBT bin >= 5)
    WP77 : D_b > +0.844  (PCBT bin >= 4)
    WP85 : D_b > -0.378  (PCBT bin >= 3)
    WP90 : D_b > -1.340  (PCBT bin >= 2)

Usage (examples):
    # HHbbyy SM signal (mc23, kappa_lambda=1) — DAOD_PHYS
    python explore_mxaod.py \\
        --path /eos/atlas/atlascerngroupdisk/phys-higp/higgs-pairs/Run3/yybb/mc23_13p6TeV.603559.PhPy8EG_PDF4LHC21_HHbbyy_chhh1p0.deriv.DAOD_PHYS.e8564_a911_r15530_p6697/ \\
        --pattern "*.root" \\
        --tag mc23_HHbbyy_SM

    # HHbbyy VBF signal (mc23, CV=CVV=Cf=1) — DAOD_PHYS
    python explore_mxaod.py \\
        --path /eos/atlas/atlascerngroupdisk/phys-higp/higgs-pairs/Run3/yybb/mc23_13p6TeV.525376.MGPy8EG_hh_bbyy_vbf_novhh_l1cvv1cv1_5fns.deriv.DAOD_PHYS.e8529_a911_r15530_p6266/ \\
        --pattern "*.root" \\
        --tag mc23_HHbbyy_VBF

    # Data 2018 — DAOD_PHYS
    python explore_mxaod.py \\
        --path /eos/atlas/atlascerngroupdisk/phys-higp/higgs-pairs/Run3/yybb/data18_13TeV.periodAllYear.physics_Main.PhysCont.DAOD_PHYS.grp18_v01_p6479/ \\
        --pattern "*.root" \\
        --tag data18

    # HH→bbyy validation MxAOD (mc23e, PhPy8)
    python explore_mxaod.py \\
        --path /eos/atlas/unpledged/group-tokyo/users/yonoda/elmazzeo/2025-11-19_VALIDATION/ \\
        --pattern "user.elmazzeo.mc23e.PhPy8_HHchhh1p0.MxAODDetailedNoSkim.*.MxAOD.root" \\
        --tag mc23e_HHbbyy_validation

Outputs (saved to --outdir):
    disc_GN2v01_<tag>.png     — D_b distributions per flavour with WP cuts
    disc_GN2v01_zoom_<tag>.png — zoom around the WP85/WP65 region
    photon_pt_<tag>.png       — photon pT sanity check (if branch present)
    wp_table_<tag>.txt        — efficiency / rejection numbers per WP

Dependencies: uproot, awkward, numpy, matplotlib
"""

import argparse
import glob
import os
import sys

import numpy as np

try:
    import uproot
    import awkward as ak
except ImportError:
    sys.exit(
        "uproot and awkward are required.\n"
        "Install via:  pip install uproot awkward\n"
        "Or with LCG:  lsetup 'views LCG_106 x86_64-el9-gcc13-opt'"
    )

# Shared object cache for uproot.open() calls.  Caches deserialized TTree
# metadata (headers, streamers) so that when probe_file() and load_branches()
# both open the same file the header is only fetched once over the network.
# This is the uproot equivalent of ROOT's TTreeCache and matters most for
# remote/WAN access (e.g. EOS from UChicago via XROOTD or FUSE over WAN).
# A plain dict is accepted by all uproot versions as an object_cache.
_OBJECT_CACHE: dict = {}

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# ─────────────────────────────────────────────────────────────────────────────
# GN2v01 / PCBT constants  (from makePlot_withRecoJets.py)
# ─────────────────────────────────────────────────────────────────────────────
FC    = 0.20   # charm fraction
FTAU  = 0.01   # tau fraction
FU    = 1.0 - FC - FTAU  # light fraction = 0.79

# Discriminant thresholds for each WP (from PCBT_WP_BINS comment block)
WP_CUTS = {
    "WP90": -1.340,
    "WP85": -0.378,
    "WP77":  0.844,
    "WP70":  1.892,
    "WP65":  2.669,
}
# Highlight only the two WPs the user is investigating
HIGHLIGHT_WPS = {"WP85", "WP65"}

# Flavour map:  HadronConeExclTruthLabelID values
#   5 = b-jet,  4 = c-jet,  0 = light/gluon (all others also collapsed to 0)
FLAVOUR_LABELS = {5: "b-jet", 4: "c-jet", 0: "light-jet"}
FLAVOUR_COLORS = {5: "#d62728", 4: "#ff7f0e", 0: "#1f77b4"}


# ─────────────────────────────────────────────────────────────────────────────
# Branch name candidates
# ─────────────────────────────────────────────────────────────────────────────
# Two naming conventions are supported:
#   DAOD / MxAOD  : "<Prefix>.<Tagger>_<comp>"
#                   e.g. AntiKt4EMPFlowJets_BTagging201903AuxDyn.GN2v01_pb
#   HGam flat ntuple : "<Prefix>_<Tagger>_<comp>_NOSYS"
#                   e.g. recojet_antikt4PFlow_GN2v01_pb_NOSYS
#
# Each (separator, suffix) pair in _SEP_SUFFIX_COMBOS is tried in order.
_SEP_SUFFIX_COMBOS = [
    (".", ""),          # DAOD / MxAOD
    ("_", "_NOSYS"),    # HGam AnalysisMiniTree (nominal systematic tag)
    ("_", ""),          # HGam without systematic tag
]

_JET_AUX_CANDIDATES = [
    "recojet_antikt4PFlow",                        # HGam AnalysisMiniTree
    "HGamAntiKt4EMPFlowCustomVtxJetsAuxDyn",       # HGam MxAOD (custom diphoton vtx)
    "HGamAntiKt4EMPFlowJetsAuxDyn",                # HGam MxAOD (standard vtx)
    "AnalysisJetsAuxDyn",                          # DAOD_PHYSLITE
    "AntiKt4EMPFlowJetsAuxDyn",                    # DAOD_PHYS
    "AntiKt4EMPFlowJets_BTagging201903AuxDyn",     # DAOD (older)
]
_BTAG_PREFIX_CANDIDATES = [
    "recojet_antikt4PFlow",                        # HGam AnalysisMiniTree
    "HGamAntiKt4EMPFlowCustomVtxJetsAuxDyn",       # HGam MxAOD (custom diphoton vtx)
    "HGamAntiKt4EMPFlowJetsAuxDyn",                # HGam MxAOD (standard vtx)
    "BTagging_AntiKt4EMPFlowAuxDyn",               # DAOD_PHYSLITE
    "AntiKt4EMPFlowJets_BTagging201903AuxDyn",     # DAOD_PHYS
    "BTagging_AntiKt4EMPFlow_201903AuxDyn",        # DAOD alt
    "AntiKt4EMPFlowJetsAuxDyn",                    # some derivations flatten here
]
_TRUTH_LABEL_SUFFIXES = [
    "HadronConeExclTruthLabelID",
    "HadronConeExclExtendedTruthLabelID",
    "TruthLabelID",
]
_GN2_SCORE_NAMES = ["GN2v01", "GN2v00", "GN2"]
_SCORE_COMPONENTS = ["pb", "pc", "pu", "ptau"]

PHOTON_BRANCHES = [
    "HGamPhotonsAuxDyn.pt",
    "HGamPhotonsAuxDyn.eta",
]

# Candidate tree names, tried in order.
# HGam analysis ntuples use "AnalysisMiniTree"; older HGam ntuples use "HGam";
# raw MxAODs/DAODs use "CollectionTree".
_TREE_NAME_CANDIDATES = ["AnalysisMiniTree", "HGam", "CollectionTree", "nominal", "physics", "tree"]
TREE_NAME = "CollectionTree"   # kept as CLI default; overridden by auto-discovery


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def _flatten(arr):
    """Flatten a jagged awkward array to a 1-D numpy array."""
    return ak.to_numpy(ak.flatten(arr, axis=None))


def _find_branch(available, candidates):
    """Return the first candidate that is present in `available`, or None."""
    for c in candidates:
        if c in available:
            return c
    return None


def discover_branches(tree_keys):
    """
    Given the set of branch names in the tree, return a dict mapping
    logical names -> actual branch names, for everything we can find.

    Supports both DAOD-style branches (dot separator, no suffix) and
    HGam flat-ntuple branches (underscore separator, _NOSYS suffix).
    """
    found = {}

    # Truth label — try every (prefix, separator, suffix, systematic-tag) combo
    outer_break = False
    for sep, sfx in _SEP_SUFFIX_COMBOS:
        for prefix in _JET_AUX_CANDIDATES:
            for tl_suffix in _TRUTH_LABEL_SUFFIXES:
                cand = f"{prefix}{sep}{tl_suffix}{sfx}"
                if cand in tree_keys:
                    found["truth_label"] = cand
                    outer_break = True
                    break
            if outer_break:
                break
        if outer_break:
            break

    # GN2v01 scores
    outer_break = False
    for sep, sfx in _SEP_SUFFIX_COMBOS:
        for btag_pfx in _BTAG_PREFIX_CANDIDATES:
            for gn2_name in _GN2_SCORE_NAMES:
                hits = {}
                for comp in _SCORE_COMPONENTS:
                    cand = f"{btag_pfx}{sep}{gn2_name}_{comp}{sfx}"
                    if cand in tree_keys:
                        hits[comp] = cand
                if "pb" in hits and "pu" in hits:
                    found["tagger_name"] = gn2_name
                    found["btag_prefix"]  = btag_pfx
                    for comp, bname in hits.items():
                        found[f"gn2_{comp}"] = bname
                    outer_break = True
                    break
            if outer_break:
                break
        if outer_break:
            break

    # Jet kinematics (optional, for basic sanity)
    for sep, sfx in _SEP_SUFFIX_COMBOS:
        for prefix in _JET_AUX_CANDIDATES:
            for kin in ("pt", "eta"):
                key = f"jet_{kin}"
                if key not in found:
                    cand = f"{prefix}{sep}{kin}{sfx}"
                    if cand in tree_keys:
                        found[key] = cand

    # Photons (sanity check)
    for bname in PHOTON_BRANCHES:
        if bname in tree_keys:
            found[bname] = bname

    return found


def _find_tree(rf, requested_name):
    """
    Return (actual_tree_name, tree) for the first matching candidate.
    If ``requested_name`` was supplied explicitly (i.e. is not the sentinel
    default 'CollectionTree'), try it first before the candidate list.
    Prints the keys present in the file when nothing matches.
    """
    candidates = ([requested_name] + [c for c in _TREE_NAME_CANDIDATES if c != requested_name]
                  if requested_name not in _TREE_NAME_CANDIDATES
                  else _TREE_NAME_CANDIDATES)
    for name in candidates:
        if name in rf:
            return name, rf[name]
    # Nothing matched — print what IS in the file to help the user
    top_keys = [str(k) for k in rf.keys()]
    print(f"  [warn] None of the candidate trees found. Objects in this file:")
    for k in top_keys[:20]:
        print(f"    {k}")
    if len(top_keys) > 20:
        print(f"    … and {len(top_keys) - 20} more")
    print(f"  Tip: pass the correct tree name with --tree <name>")
    return None, None


def probe_file(fpath, tree_name):
    """Open one file and return (branch_map, n_events, found_tree_name) or (None, 0, None)."""
    try:
        with uproot.open(fpath, object_cache=_OBJECT_CACHE) as rf:
            actual_name, tree = _find_tree(rf, tree_name)
            if tree is None:
                return None, 0, None
            if actual_name != tree_name:
                print(f"  [info] tree '{tree_name}' not found; using '{actual_name}' instead")
            keys = set(tree.keys())
            branch_map = discover_branches(keys)

            # Print every b-tag / truth-label related branch for debugging.
            # Keywords cover both DAOD-style long names and flat-ntuple short names.
            btag_branches = sorted(
                k for k in keys
                if any(kw in k for kw in
                       ["GN2", "DL1", "HadronCone", "TruthLabel", "PCBT",
                        "MV2", "SV1", "JetFitter", "BTag", "btag",
                        "flavour", "Flavour", "truth", "Truth",
                        "jet_b", "jet_n", "njet", "nJet"])
            )
            print(f"\n  [{os.path.basename(fpath)}] tree='{actual_name}'  "
                  f"{tree.num_entries:,} events, "
                  f"{len(keys):,} branches total")
            print(f"  Found {len(btag_branches)} b-tagging / truth-label branches:")
            for b in btag_branches:
                print(f"    {b}")
            return branch_map, tree.num_entries, actual_name
    except Exception as exc:
        print(f"  [error] could not probe {fpath}: {exc}")
        return None, 0, None


def load_branches(files, tree_name, branch_map, max_events):
    """
    Read the branches listed in branch_map from all files (up to max_events).
    Returns a dict {logical_name: concatenated_awkward_array}.
    """
    read_keys = {k: v for k, v in branch_map.items()
                 if k not in ("tagger_name", "btag_prefix")}
    # De-duplicate branch names (several logical names may map to the same branch)
    unique_bnames = list(set(read_keys.values()))

    arrays = {k: [] for k in read_keys}
    n_read = 0

    for fpath in files:
        if n_read >= max_events:
            break
        try:
            with uproot.open(fpath, object_cache=_OBJECT_CACHE) as rf:
                _, tree = _find_tree(rf, tree_name)
                if tree is None:
                    continue
                remaining = max_events - n_read
                chunk = tree.arrays(unique_bnames,
                                    entry_stop=remaining,
                                    library="ak")
                for logical, bname in read_keys.items():
                    arrays[logical].append(chunk[bname])
                n_read += tree.num_entries if tree.num_entries <= remaining else remaining
        except Exception as exc:
            print(f"  [warn] skipping {os.path.basename(fpath)}: {exc}")

    merged = {}
    for logical, parts in arrays.items():
        if parts:
            merged[logical] = ak.concatenate(parts)

    print(f"\n  Events loaded: {n_read:,}")
    return merged


def compute_discriminant(arrays, branch_map):
    """
    Compute D_b = ln(p_b / (f_c*p_c + f_tau*p_tau + f_u*p_u)).
    Returns a 1-D numpy array (all jets flattened).
    """
    pb = _flatten(arrays["gn2_pb"]).astype(np.float64)
    pc = _flatten(arrays["gn2_pc"]).astype(np.float64) if "gn2_pc" in arrays else np.zeros_like(pb)
    pu = _flatten(arrays["gn2_pu"]).astype(np.float64)
    ptau = _flatten(arrays["gn2_ptau"]).astype(np.float64) if "gn2_ptau" in arrays else np.zeros_like(pb)

    denom = FC * pc + FTAU * ptau + FU * pu
    denom = np.where(denom > 0, denom, 1e-10)
    pb    = np.where(pb    > 0, pb,    1e-10)
    return np.log(pb / denom)


# ─────────────────────────────────────────────────────────────────────────────
# Plotting
# ─────────────────────────────────────────────────────────────────────────────
def plot_discriminant(disc, labels, tagger_name, outdir, tag,
                      disc_range=(-6, 8), zoom_range=(-1.5, 4.0)):
    """
    Full-range and zoomed plots of D_b split by truth flavour,
    with WP cut lines overlaid.
    """
    for suffix, xrange in [("", disc_range), ("_zoom", zoom_range)]:
        fig, ax = plt.subplots(figsize=(9, 5))
        bins = np.linspace(xrange[0], xrange[1], 120)

        # WP cut lines drawn first so flavour curves render on top
        for wp_name, cut in WP_CUTS.items():
            if xrange[0] <= cut <= xrange[1]:
                ls   = "-"  if wp_name in HIGHLIGHT_WPS else ":"
                lw   = 2.0  if wp_name in HIGHLIGHT_WPS else 1.2
                col  = "black" if wp_name in HIGHLIGHT_WPS else "gray"
                ax.axvline(cut, linestyle=ls, linewidth=lw, color=col,
                           zorder=1,
                           label=f"{wp_name}  (D_b > {cut:.3f})")

        for flav, flabel in FLAVOUR_LABELS.items():
            mask = (labels == flav)
            vals = disc[mask]
            if len(vals) == 0:
                continue
            ax.hist(vals, bins=bins, histtype="step", density=True,
                    label=f"{flabel}  (N={len(vals):,})",
                    color=FLAVOUR_COLORS[flav], linewidth=1.8, zorder=2)

        ax.set_xlabel(f"{tagger_name} discriminant  $D_b$", fontsize=13)
        ax.set_ylabel("Normalised entries / bin", fontsize=12)
        ax.set_title(
            f"{tagger_name} discriminant by truth flavour"
            + (f" — {tag}" if tag else ""),
            fontsize=12,
        )
        ax.set_yscale("log")
        ax.legend(fontsize=9, loc="upper left")
        ax.set_xlim(*xrange)

        fname = os.path.join(
            outdir,
            f"disc_{tagger_name}{suffix}{'_' + tag if tag else ''}.png",
        )
        fig.savefig(fname, bbox_inches="tight", dpi=150)
        plt.close(fig)
        print(f"  Saved: {fname}")


def plot_photon_pt(arrays, outdir, tag):
    """Quick photon-pT sanity check."""
    key = "HGamPhotonsAuxDyn.pt"
    if key not in arrays:
        return
    pt = _flatten(arrays[key]) / 1e3  # MeV → GeV
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(pt, bins=50, histtype="step", color="steelblue")
    ax.set_xlabel("Photon $p_T$ [GeV]", fontsize=12)
    ax.set_ylabel("Entries", fontsize=12)
    ax.set_title("Photon $p_T$ — sanity check" + (f" ({tag})" if tag else ""))
    fname = os.path.join(outdir, f"photon_pt{'_' + tag if tag else ''}.png")
    fig.savefig(fname, bbox_inches="tight", dpi=150)
    plt.close(fig)
    print(f"  Saved: {fname}")


# ─────────────────────────────────────────────────────────────────────────────
# Tightest WP passed bar chart
# ─────────────────────────────────────────────────────────────────────────────
def plot_tightest_wp(disc, labels, tagger_name, outdir, tag):
    """
    Bar chart showing the tightest WP each jet passes, split by truth flavour.
    Each jet is assigned to exactly one bin — the tightest WP it passes, or
    'Fail all' if it passes none.  Bars are normalised per WP bin so that the
    three flavours sum to 1 within each bin, showing the flavour composition
    (purity) at each working point.
    """
    wp_sorted = sorted(WP_CUTS.items(), key=lambda x: x[1])   # loosest → tightest
    bin_names = ["Fail all"] + [wp for wp, _ in wp_sorted]     # 6 bins

    # Assign each jet its tightest passing WP (index into wp_sorted, or -1)
    tightest = np.full(len(disc), -1, dtype=int)
    for i, (_, cut) in enumerate(wp_sorted):
        tightest[disc >= cut] = i
    tightest += 1   # shift: fail-all → 0, WP90 → 1, …, WP65 → 5

    n_bins   = len(bin_names)
    x        = np.arange(n_bins)
    n_flavs  = sum(1 for f in FLAVOUR_LABELS if np.any(labels == f))
    width    = 0.8 / max(n_flavs, 1)

    # First pass: collect per-(flavour, bin) counts
    flavor_counts = {}
    for flav in FLAVOUR_LABELS:
        mask = labels == flav
        if not np.any(mask):
            continue
        flavor_counts[flav] = np.array(
            [np.sum(tightest[mask] == b) for b in range(n_bins)], dtype=float
        )

    # Per-bin totals — used to normalise so flavours sum to 1 within each bin
    bin_totals = np.zeros(n_bins)
    for counts in flavor_counts.values():
        bin_totals += counts

    fig, ax = plt.subplots(figsize=(10, 5))

    for idx, (flav, flabel) in enumerate(FLAVOUR_LABELS.items()):
        if flav not in flavor_counts:
            continue
        n_flav    = int(np.sum(labels == flav))
        counts    = flavor_counts[flav]
        fractions = np.where(bin_totals > 0, counts / bin_totals, 0.0)
        offset    = (idx - (len(FLAVOUR_LABELS) - 1) / 2) * width
        ax.bar(x + offset, fractions, width,
               label=f"{flabel}  (N={n_flav:,})",
               color=FLAVOUR_COLORS[flav], alpha=0.85,
               edgecolor="white", linewidth=0.5)

    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels(bin_names, fontsize=11)
    ax.set_xlabel("Tightest WP passed", fontsize=13)
    ax.set_ylabel("Fraction of jets (normalised per WP bin)", fontsize=12)
    ax.set_title(
        f"{tagger_name} — tightest WP passed by truth flavour"
        + (f" — {tag}" if tag else ""),
        fontsize=12,
    )
    ax.legend(fontsize=9)
    ax.set_xlim(-0.5, n_bins - 0.5)

    fname = os.path.join(outdir, f"tightest_wp_{tagger_name}{'_' + tag if tag else ''}.png")
    fig.savefig(fname, bbox_inches="tight", dpi=150)
    plt.close(fig)
    print(f"  Saved: {fname}")


# ─────────────────────────────────────────────────────────────────────────────
# WP efficiency / rejection table
# ─────────────────────────────────────────────────────────────────────────────
def print_wp_table(disc, labels, outdir, tag):
    """
    For each WP threshold compute and print:
      b-efficiency, c-rejection, light-rejection
    alongside the naive expectation from inclusive dijet (for context).
    """
    totals = {flav: int(np.sum(labels == flav)) for flav in FLAVOUR_LABELS}
    lines = []
    header = (f"{'WP':<8}  {'cut':>7}  "
              f"{'b-eff':>7}  {'c-rej':>7}  {'light-rej':>10}")
    lines.append(header)
    lines.append("-" * len(header))

    for wp_name, cut in sorted(WP_CUTS.items(), key=lambda x: x[1]):
        pass_mask = disc >= cut
        eff = {}
        for flav in FLAVOUR_LABELS:
            n_pass  = int(np.sum(pass_mask & (labels == flav)))
            n_total = totals[flav]
            eff[flav] = n_pass / n_total if n_total > 0 else float("nan")

        rej_c = 1.0 / eff[4] if eff[4] > 0 else float("inf")
        rej_l = 1.0 / eff[0] if eff[0] > 0 else float("inf")
        marker = "  <-- highlighted" if wp_name in HIGHLIGHT_WPS else ""
        line = (f"{wp_name:<8}  {cut:>7.3f}  "
                f"{eff[5]:>7.4f}  {rej_c:>7.1f}  {rej_l:>10.1f}{marker}")
        lines.append(line)

    # Print to terminal
    print(f"\n  WP efficiency / rejection table ({tag or 'no tag'}):")
    for ln in lines:
        print(f"    {ln}")

    # Also save to file
    fname = os.path.join(outdir, f"wp_table{'_' + tag if tag else ''}.txt")
    with open(fname, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"  Saved: {fname}")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--path",
        default="/eos/atlas/atlascerngroupdisk/phys-higp/higgs-pairs/Run3/yybb/ntuples_v9/bbyy_output_ntuples_Run3_v9/",
        help="Directory containing MxAOD .root files (or a glob expression). "
             "Defaults to the Run 3 v9 ntuple path; override to point at raw MxAODs.",
    )
    parser.add_argument(
        "--pattern",
        default="*.root",
        help="Glob pattern for ROOT files within --path (default: '*.root')",
    )
    parser.add_argument(
        "--tree",
        default=TREE_NAME,
        help=f"TTree name inside the ROOT files (default: '{TREE_NAME}')",
    )
    parser.add_argument(
        "--nevents",
        type=int,
        default=500_000,
        help="Maximum number of events to read (default: 500 000)",
    )
    parser.add_argument(
        "--outdir",
        default="./mxaod_plots",
        help="Output directory for plots and tables (default: ./mxaod_plots)",
    )
    parser.add_argument(
        "--tag",
        default="",
        help="Label appended to output filenames, e.g. 'mc23a_yyjets'",
    )
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    # ── Find files ────────────────────────────────────────────────────────────
    # On EOS, ATLAS datasets are often stored as a container *directory* whose
    # name matches the dataset pattern (e.g. "…MxAOD.root/") containing the
    # actual chunk files inside.  We expand any matched directory one level.
    pattern = os.path.join(args.path, args.pattern)
    files = []
    for match in sorted(glob.glob(pattern)):
        if os.path.isfile(match):
            files.append(match)
        elif os.path.isdir(match):
            # Expand dataset container directories (EOS rucio layout)
            inner = sorted(
                f for f in glob.glob(os.path.join(match, "*"))
                if os.path.isfile(f)
            )
            if inner:
                print(f"  [info] '{os.path.basename(match)}' is a directory "
                      f"— expanding to {len(inner)} file(s) inside")
                files.extend(inner)
            else:
                print(f"  [warn] '{match}' is a directory with no files inside — skipping")
    if not files:
        print(f"[error] No files found matching: {pattern}")
        print("  Tip: check --path and --pattern; on EOS the dataset may be a")
        print("       container directory — this script will expand it automatically.")
        sys.exit(1)

    print(f"Found {len(files)} file(s):")
    for f in files[:8]:
        print(f"  {f}")
    if len(files) > 8:
        print(f"  … and {len(files) - 8} more")

    # ── Probe first file ──────────────────────────────────────────────────────
    print("\n── Probing first file for available branches ──")
    branch_map, _, found_tree = probe_file(files[0], args.tree)
    if branch_map is None:
        sys.exit(1)
    # Use the discovered tree name for all subsequent reads
    args.tree = found_tree

    if "tagger_name" not in branch_map:
        print("\n[error] Could not find GN2v01 (or GN2) score branches.")
        print("  Known b-tagging branches printed above — adjust _BTAG_PREFIX_CANDIDATES")
        print("  in this script if the collection name differs in your production.")
        sys.exit(1)

    tagger_name = branch_map["tagger_name"]
    print(f"\n  Using tagger : {tagger_name}")
    print(f"  btag prefix  : {branch_map['btag_prefix']}")
    print(f"  truth label  : {branch_map.get('truth_label', 'NOT FOUND')}")

    # ── Load data ─────────────────────────────────────────────────────────────
    print(f"\n── Loading up to {args.nevents:,} events from {len(files)} file(s) ──")
    arrays = load_branches(files, args.tree, branch_map, args.nevents)

    # ── Compute discriminant ──────────────────────────────────────────────────
    if not all(k in arrays for k in ("gn2_pb", "gn2_pu")):
        print("[error] p_b or p_u arrays missing — cannot compute discriminant.")
        sys.exit(1)

    disc = compute_discriminant(arrays, branch_map)
    print(f"\n  Discriminant range:  [{disc.min():.3f}, {disc.max():.3f}]")
    print(f"  Median D_b         :  {np.median(disc):.3f}")

    # ── Truth labels ──────────────────────────────────────────────────────────
    if "truth_label" in arrays:
        raw_labels = _flatten(arrays["truth_label"]).astype(int)
        # Collapse everything that is not b=5 or c=4 to light=0
        labels = np.where(raw_labels == 5, 5,
                 np.where(raw_labels == 4, 4, 0))
        for flav, flabel in FLAVOUR_LABELS.items():
            print(f"  {flabel:<12}: {int(np.sum(labels == flav)):>10,} jets")
    else:
        print("\n  [warn] No truth-label branch found — all jets treated as unlabelled.")
        labels = np.zeros(len(disc), dtype=int)   # everything → light slot

    # ── Plots ─────────────────────────────────────────────────────────────────
    print(f"\n── Saving plots to {args.outdir}/ ──")
    plot_discriminant(disc, labels, tagger_name, args.outdir, args.tag)
    plot_tightest_wp(disc, labels, tagger_name, args.outdir, args.tag)
    plot_photon_pt(arrays, args.outdir, args.tag)

    # ── WP table ─────────────────────────────────────────────────────────────
    print_wp_table(disc, labels, args.outdir, args.tag)

    print("\nDone.")


if __name__ == "__main__":
    main()
