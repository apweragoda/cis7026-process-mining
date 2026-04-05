"""
process_mining_analysis.py
===========================
CIS 7026 – Business Process and Data Analysis
Question 3 (Parts C & D): Complete Process Mining Pipeline

Dataset  : Hospital Billing and Claims Management Event Log
Source   : BPI Challenge (4TU Research Data Repository)
           https://data.4tu.nl/articles/dataset/Hospital_Billing_-_Event_Log/12705113
Reference: Mannhardt, F. (2017) Hospital Billing - Event Log. 4TU.ResearchData.
           https://doi.org/10.4121/uuid:76c46b83-c930-4798-a1c9-4be94dfeb741

This script implements:
  - Process Discovery  (Alpha, Heuristics, Inductive Miners + DFG)
  - Conformance Checking (alignment-based fitness & precision)
  - Bottleneck Analysis  (IQR + Z-score methods)
  - Process Variant Analysis
  - Object-Centric Process Mining (OCPM)
  - Federated Process Mining    (FPM with differential privacy)

Run:
    python process_mining_analysis.py

Requirements:
    pip install pm4py pandas numpy matplotlib seaborn scipy scikit-learn
"""

import os
import sys
import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from collections import defaultdict

try:
    import pm4py
    from pm4py.objects.ocel.obj import OCEL
    PM4PY_AVAILABLE = True
    print("[INFO] pm4py loaded successfully.")
except ImportError:
    PM4PY_AVAILABLE = False
    print("[WARN] pm4py not installed.  pip install pm4py")

BASE       = os.path.dirname(os.path.abspath(__file__))
DATA_PATH  = os.path.join(BASE, '..', 'dataset', 'hospital_billing_event_log.csv')
OUTPUT_DIR = os.path.join(BASE, '..', 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# =============================================================================
# SECTION 1 – DATA LOADING
# =============================================================================
print("\n" + "="*70)
print("SECTION 1: DATA LOADING")
print("="*70)

df = pd.read_csv(DATA_PATH)
df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.sort_values(['case_id', 'timestamp']).reset_index(drop=True)

print(f"  Source  : Hospital Billing Event Log (BPI Challenge, 4TU Research Data)")
print(f"  Cases   : {df['case_id'].nunique():,}")
print(f"  Events  : {len(df):,}")
print(f"  Period  : {df['timestamp'].min().date()} to {df['timestamp'].max().date()}")
print(f"  Activities ({df['activity'].nunique()}):")
print(df['activity'].value_counts().to_string())

if PM4PY_AVAILABLE:
    event_log = pm4py.format_dataframe(
        df, case_id='case_id', activity_key='activity', timestamp_key='timestamp'
    )
    print(f"\n  PM4Py event log: {len(event_log):,} events ready")

# =============================================================================
# SECTION 2 – PROCESS DISCOVERY
# =============================================================================
print("\n" + "="*70)
print("SECTION 2: PROCESS DISCOVERY")
print("="*70)

alpha_net = heu_net = ind_net = tree = None
alpha_im  = heu_im  = ind_im  = None
alpha_fm  = heu_fm  = ind_fm  = None

if PM4PY_AVAILABLE:

    print("\n  [2a] Directly-Follows Graph...")
    dfg, start_acts, end_acts = pm4py.discover_dfg(event_log)
    try:
        pm4py.save_vis_dfg(dfg, start_acts, end_acts,
                           os.path.join(OUTPUT_DIR, 'dfg_discovery.png'))
        print("       Saved -> output/dfg_discovery.png")
    except Exception:
        print("       [WARN] DFG visualisation skipped (Graphviz not installed).")

    print("\n  [2b] Alpha Miner...")
    try:
        alpha_net, alpha_im, alpha_fm = pm4py.discover_petri_net_alpha(event_log)
        print("       Alpha Miner model discovered.")
        try:
            pm4py.save_vis_petri_net(alpha_net, alpha_im, alpha_fm,
                                     os.path.join(OUTPUT_DIR, 'alpha_petri_net.png'))
        except Exception:
            print("       [WARN] Petri net visualisation skipped (Graphviz).")
    except Exception as e:
        print(f"       [WARN] Alpha Miner: {e}")

    print("\n  [2c] Heuristics Miner (dependency_threshold=0.70)...")
    heu_net, heu_im, heu_fm = pm4py.discover_petri_net_heuristics(
        event_log, dependency_threshold=0.70, and_threshold=0.65, loop_two_threshold=0.90
    )
    print("       Heuristics Miner model discovered.")
    try:
        pm4py.save_vis_petri_net(heu_net, heu_im, heu_fm,
                                 os.path.join(OUTPUT_DIR, 'heuristics_petri_net.png'))
    except Exception:
        print("       [WARN] Petri net visualisation skipped (Graphviz).")

    print("\n  [2d] Inductive Miner (noise_threshold=0.20)...")
    tree    = pm4py.discover_process_tree_inductive(event_log, noise_threshold=0.20)
    ind_net, ind_im, ind_fm = pm4py.convert_to_petri_net(tree)
    print("       Inductive Miner model discovered.")
    try:
        pm4py.save_vis_petri_net(ind_net, ind_im, ind_fm,
                                 os.path.join(OUTPUT_DIR, 'inductive_petri_net.png'))
        pm4py.save_vis_process_tree(tree, os.path.join(OUTPUT_DIR, 'inductive_tree.png'))
    except Exception:
        print("       [WARN] Petri net visualisation skipped (Graphviz).")

    print("\n  [2e] Performance DFG...")
    perf_dfg, perf_start, perf_end = pm4py.discover_performance_dfg(event_log)
    try:
        pm4py.save_vis_performance_dfg(perf_dfg, perf_start, perf_end,
                                       os.path.join(OUTPUT_DIR, 'performance_dfg.png'))
        print("       Saved -> output/performance_dfg.png")
    except Exception:
        print("       [WARN] Performance DFG visualisation skipped (Graphviz).")

else:
    print("  [SKIP] pm4py required for process discovery.")

# =============================================================================
# SECTION 3 – CONFORMANCE CHECKING
# =============================================================================
print("\n" + "="*70)
print("SECTION 3: CONFORMANCE CHECKING")
print("="*70)

conformance_results = {}

if PM4PY_AVAILABLE and ind_net is not None:
    for name, (net, im, fm) in [('Inductive Miner', (ind_net, ind_im, ind_fm))]:
        print(f"\n  Checking: {name}")
        try:
            fit = pm4py.fitness_alignments(event_log, net, im, fm)
            fit_pct = fit['percentage_of_fitting_traces']
            # pm4py returns this as 0-100; normalise to 0-1 if needed
            if fit_pct > 1:
                fit_pct = fit_pct / 100
            print(f"    Fitness    : {fit['average_trace_fitness']:.4f}")
            print(f"    Fit Traces : {fit_pct:.2%}")
        except Exception as e:
            fit = {'average_trace_fitness': 0, 'percentage_of_fitting_traces': 0}
            fit_pct = 0
            print(f"    [WARN] Fitness: {e}")
        try:
            prec = pm4py.precision_alignments(event_log, net, im, fm)
            print(f"    Precision  : {prec:.4f}")
        except Exception as e:
            prec = 0
            print(f"    [WARN] Precision: {e}")
        try:
            simp = pm4py.simplicity_arc_degree(net)
        except Exception:
            n_arcs = len(net.arcs); n_places = max(len(net.places), 1)
            simp = round(1.0 / (1.0 + n_arcs / n_places), 4)
        print(f"    Simplicity : {simp:.4f}")
        conformance_results[name] = {
            'fitness': fit['average_trace_fitness'],
            'precision': prec,
            'simplicity': simp,
        }

    if conformance_results:
        fig, ax = plt.subplots(figsize=(8, 5))
        metrics = ['fitness', 'precision', 'simplicity']
        labels  = ['Fitness', 'Precision', 'Simplicity']
        colors  = ['#2196F3', '#4CAF50', '#FF9800']
        vals    = [conformance_results['Inductive Miner'].get(m, 0) for m in metrics]
        bars = ax.bar(labels, vals, color=colors, alpha=0.85, width=0.5, edgecolor='white')
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width()/2, v + 0.01,
                    f'{v:.4f}', ha='center', fontsize=11, fontweight='bold')
        ax.set_ylim(0, 1.15)
        ax.set_ylabel('Score (0–1)')
        ax.set_title('Figure 3.1 – Conformance Checking: Inductive Miner\n'
                     'Hospital Billing Event Log – Model Quality Dimensions')
        ax.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'conformance_results.png'), dpi=150)
        plt.close()
        print("\n  Conformance chart -> output/conformance_results.png")

# =============================================================================
# SECTION 4 – BOTTLENECK ANALYSIS
# =============================================================================
print("\n" + "="*70)
print("SECTION 4: BOTTLENECK ANALYSIS")
print("="*70)

def case_durations(df):
    g = df.groupby('case_id')['timestamp']
    return (g.max() - g.min()).dt.total_seconds() / 3600   # hours

def activity_wait_times(df):
    d = df.sort_values(['case_id','timestamp']).copy()
    d['prev_ts'] = d.groupby('case_id')['timestamp'].shift(1)
    d['wait_h']  = (d['timestamp'] - d['prev_ts']).dt.total_seconds() / 3600
    return (d.dropna(subset=['wait_h'])
             .groupby('activity')['wait_h']
             .agg(['median','mean','std','count'])
             .rename(columns={'median':'median_h','mean':'mean_h','std':'std_h','count':'n'})
             .sort_values('mean_h', ascending=False))

durations = case_durations(df)
print(f"\n  Case Duration Statistics (hours):")
print(f"    Mean   : {durations.mean():.1f}")
print(f"    Median : {durations.median():.1f}")
print(f"    Std    : {durations.std():.1f}")
print(f"    95th % : {durations.quantile(0.95):.1f}")
print(f"    Max    : {durations.max():.1f}")

Q1  = durations.quantile(0.25)
Q3  = durations.quantile(0.75)
IQR = Q3 - Q1
threshold = Q3 + 1.5 * IQR
btl_cases = durations[durations > threshold]
z_confirmed = durations[np.abs(stats.zscore(durations)) > 2.5]
print(f"\n  IQR Bottleneck Detection:")
print(f"    Q1={Q1:.1f}h  Q3={Q3:.1f}h  IQR={IQR:.1f}h  Threshold={threshold:.1f}h")
print(f"    Bottleneck cases : {len(btl_cases):,} ({len(btl_cases)/len(durations):.1%})")
print(f"    Z-score confirmed: {len(z_confirmed):,}")

act_waits = activity_wait_times(df)
print(f"\n  Top 5 Activities by Mean Wait Time:")
print(act_waits.head(5).to_string())

# ── Figure 4.1 + 4.2 ─────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

axes[0].hist(durations.clip(upper=durations.quantile(0.99)), bins=60,
             color='steelblue', edgecolor='white', alpha=0.85)
axes[0].axvline(durations.median(), color='orange', linestyle='--', linewidth=2,
                label=f'Median: {durations.median():.0f}h')
axes[0].axvline(threshold, color='red', linestyle='--', linewidth=2,
                label=f'Bottleneck threshold: {threshold:.0f}h')
axes[0].set_xlabel('Case Duration (hours)')
axes[0].set_ylabel('Number of Billing Cases')
axes[0].set_title('Figure 4.1 – Case Duration Distribution\n'
                  'Hospital Billing Process – Identifying Long-Running Cases')
axes[0].legend(); axes[0].grid(alpha=0.3)

top10 = act_waits.head(10)
axes[1].barh(top10.index, top10['mean_h'], color='coral', alpha=0.85)
axes[1].set_xlabel('Mean Wait Time (hours)')
axes[1].set_title('Figure 4.2 – Mean Inter-Activity Wait Time\n'
                  'Identifying Activity-Level Process Bottlenecks')
axes[1].grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'bottleneck_analysis.png'), dpi=150)
plt.close()
print("\n  Bottleneck chart -> output/bottleneck_analysis.png")

# ── Figure 4.3: Bottleneck by case type ──────────────────────────────────────
case_meta = df.groupby('case_id').first()[['case_type','speciality','is_cancelled']]
case_meta['duration_h'] = durations

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

for ax, col, title in zip(axes,
    ['case_type', 'speciality'],
    ['Case Type', 'Speciality']):
    try:
        top_cats = case_meta[col].value_counts().head(6).index
        data   = [case_meta[case_meta[col]==c]['duration_h'].dropna() for c in top_cats]
        labels = list(top_cats)
        ax.boxplot(data, labels=labels, patch_artist=True)
        ax.set_ylabel('Duration (hours)')
        ax.set_title(f'Figure 4.3 – Duration by {title}')
        ax.grid(axis='y', alpha=0.3)
        plt.setp(ax.get_xticklabels(), rotation=15, ha='right')
    except Exception as e:
        ax.text(0.5, 0.5, f'No data: {e}', transform=ax.transAxes, ha='center')

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'bottleneck_segmentation.png'), dpi=150)
plt.close()
print("  Segmentation chart -> output/bottleneck_segmentation.png")

# ── Figure 4.4: Monthly trend ────────────────────────────────────────────────
case_meta['month'] = df.groupby('case_id')['timestamp'].min().dt.to_period('M')
monthly = case_meta.groupby('month')['duration_h'].mean().reset_index()
monthly['month_str'] = monthly['month'].astype(str)

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(range(len(monthly)), monthly['duration_h'], 'bo-', linewidth=2)
ax.set_xticks(range(0, len(monthly), 3))
ax.set_xticklabels(monthly['month_str'].iloc[::3], rotation=45, ha='right')
ax.set_xlabel('Month')
ax.set_ylabel('Average Duration (hours)')
ax.set_title('Figure 4.4 – Average Billing Case Duration by Month (2012–2016)\n'
             'Identifying Seasonal Trends and Performance Variations')
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'monthly_duration_trend.png'), dpi=150)
plt.close()
print("  Monthly trend chart -> output/monthly_duration_trend.png")

# =============================================================================
# SECTION 5 – PROCESS VARIANT ANALYSIS
# =============================================================================
print("\n" + "="*70)
print("SECTION 5: PROCESS VARIANT ANALYSIS")
print("="*70)

traces = (df.sort_values(['case_id','timestamp'])
            .groupby('case_id')['activity']
            .apply(lambda x: ' -> '.join(x)))
variants = traces.value_counts()
print(f"\n  Total unique variants : {len(variants):,}")
print(f"\n  Top 5 process variants:")
for i, (trace, count) in enumerate(variants.head(5).items(), 1):
    pct = count / len(variants.index) * 100
    pct = count / df['case_id'].nunique() * 100
    display = trace if len(trace) < 110 else trace[:107] + '...'
    print(f"  [{i}] {count:6,} cases ({pct:.1f}%) | {display}")

fig, ax = plt.subplots(figsize=(10, 6))
top_n = 15
top_v = variants.head(top_n)
ax.barh(range(len(top_v)), top_v.values, color='steelblue', alpha=0.85)
ax.set_yticks(range(len(top_v)))
ax.set_yticklabels([f"Variant {i+1}" for i in range(len(top_v))], fontsize=9)
ax.set_xlabel('Number of Cases')
ax.set_title(f'Figure 5.1 – Top {top_n} Process Variants by Frequency\n'
             f'Coverage: {top_v.sum()/df["case_id"].nunique():.0%} of all cases')
ax.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'process_variants.png'), dpi=150)
plt.close()
print(f"\n  Variant chart -> output/process_variants.png")

# =============================================================================
# SECTION 6 – OBJECT-CENTRIC PROCESS MINING (OCPM)
# =============================================================================
print("\n" + "="*70)
print("SECTION 6: OBJECT-CENTRIC PROCESS MINING (OCPM)")
print("="*70)

if PM4PY_AVAILABLE:
    events_r, objects_r, relations_r = [], [], []
    seen = set()

    for idx, row in df.iterrows():
        eid = f"E_{idx:08d}"
        cid = row['case_id']
        act = row['activity']
        ts  = row['timestamp']

        events_r.append({'ocel:eid': eid, 'ocel:activity': act,
                          'ocel:timestamp': ts,
                          'resource': row.get('resource','Unknown')})

        # BillingCase object
        if cid not in seen:
            objects_r.append({'ocel:oid': cid, 'ocel:type': 'BillingCase',
                               'case_type':  row.get('case_type',''),
                               'speciality': row.get('speciality','')})
            seen.add(cid)
        relations_r.append({'ocel:eid': eid, 'ocel:oid': cid,
                             'ocel:qualifier': 'billing_case'})

        # Resource (clinician/department) object
        res_id = f"RES_{str(row.get('resource','UNK')).replace(' ','_')}"
        if res_id not in seen:
            objects_r.append({'ocel:oid': res_id, 'ocel:type': 'Resource',
                               'name': row.get('resource','Unknown')})
            seen.add(res_id)
        if act in ['NEW','CODE OK','CODE NOK','BILLED']:
            relations_r.append({'ocel:eid': eid, 'ocel:oid': res_id,
                                 'ocel:qualifier': 'resource'})

        # Speciality object
        spec_id = f"SPEC_{str(row.get('speciality','UNK')).replace(' ','_')}"
        if spec_id not in seen:
            objects_r.append({'ocel:oid': spec_id, 'ocel:type': 'Speciality',
                               'name': row.get('speciality','Unknown')})
            seen.add(spec_id)
        if act in ['NEW','BILLED','FIN']:
            relations_r.append({'ocel:eid': eid, 'ocel:oid': spec_id,
                                 'ocel:qualifier': 'speciality'})

    ocel = OCEL(
        events   = pd.DataFrame(events_r),
        objects  = pd.DataFrame(objects_r),
        relations= pd.DataFrame(relations_r),
    )

    print(f"\n  OCEL 2.0 constructed:")
    print(f"    Events   : {len(ocel.events):,}")
    print(f"    Objects  : {len(ocel.objects):,}")
    print(f"    Relations: {len(ocel.relations):,}")
    print(f"\n  Object type distribution:")
    print(ocel.objects.groupby('ocel:type').size().to_string())

    # Co-occurrence heatmap
    merged = ocel.relations.merge(ocel.objects[['ocel:oid','ocel:type']],
                                   on='ocel:oid', how='left')
    co = merged.groupby('ocel:eid')['ocel:type'].apply(list)
    matrix = defaultdict(lambda: defaultdict(int))
    for types in co:
        for t1 in types:
            for t2 in types:
                if t1 != t2:
                    matrix[t1][t2] += 1

    obj_types = ['BillingCase', 'Resource', 'Speciality']
    mat_df = pd.DataFrame(
        [[matrix[r][c] for c in obj_types] for r in obj_types],
        index=obj_types, columns=obj_types
    )
    fig, ax = plt.subplots(figsize=(7, 6))
    sns.heatmap(mat_df, annot=True, fmt='d', cmap='Blues', ax=ax,
                linewidths=0.5, cbar_kws={'label': 'Co-occurrence count'})
    ax.set_title('Figure 6.1 – Object Type Co-occurrence Heatmap (OCPM)\n'
                 'Shows how BillingCase, Resource, and Speciality objects share events')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'ocpm_interaction_heatmap.png'), dpi=150)
    plt.close()
    print("\n  OCPM heatmap -> output/ocpm_interaction_heatmap.png")

else:
    print("  [SKIP] pm4py required.")

# =============================================================================
# SECTION 7 – FEDERATED PROCESS MINING (FPM)
# =============================================================================
print("\n" + "="*70)
print("SECTION 7: FEDERATED PROCESS MINING (FPM)")
print("="*70)

EPSILON = 0.1

def laplace_noise(v, sens=1, eps=EPSILON):
    return v + np.random.laplace(0, sens/eps)

def local_dfg(site_df):
    s = site_df.sort_values(['case_id','timestamp']).copy()
    s['next'] = s.groupby('case_id')['activity'].shift(-1)
    pairs = s.dropna(subset=['next'])
    return pairs.groupby(['activity','next']).size().to_dict()

def fed_aggregate(local_dfgs, apply_dp=True):
    merged = defaultdict(int)
    for d in local_dfgs:
        for pair, cnt in d.items():
            merged[pair] += max(0, int(laplace_noise(cnt))) if apply_dp else cnt
    return dict(merged)

# Split by case_type — each node holds all events for cases of that type
# This gives a clean partition where case durations are meaningful per node
top_types = df.groupby('case_id')['case_type'].first().value_counts().head(3).index.tolist()
local = {}
node_stats = {}
print(f"\n  Federation nodes (top 3 case types): {top_types}")

# Build a case_id -> case_type lookup
case_type_map = df.groupby('case_id')['case_type'].first()

for ctype in top_types:
    # All cases of this type
    case_ids_in_node = case_type_map[case_type_map == ctype].index
    site = df[df['case_id'].isin(case_ids_in_node)]
    local[ctype] = local_dfg(site)
    dur = case_durations(site)
    node_stats[ctype] = {'cases': site['case_id'].nunique(), 'avg_h': dur.mean()}
    print(f"  Node [{ctype}]: {node_stats[ctype]['cases']:,} cases, "
          f"avg duration {node_stats[ctype]['avg_h']:.1f}h")

fed_dp   = fed_aggregate(list(local.values()), apply_dp=True)
fed_true = fed_aggregate(list(local.values()), apply_dp=False)

top_edges = sorted(fed_true.items(), key=lambda x: -x[1])[:10]
print(f"\n  Top 10 transitions (federated, epsilon={EPSILON}):")
for (src, tgt), cnt in top_edges:
    dp_cnt = fed_dp.get((src, tgt), 0)
    print(f"    {src:18s} -> {tgt:18s} | True:{cnt:6d} | DP:{dp_cnt:6d} | Diff:{abs(cnt-dp_cnt):4d}")

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
specs   = list(node_stats.keys())
avg_dur = [node_stats[s]['avg_h'] for s in specs]
colors  = ['#2196F3', '#4CAF50', '#FF9800']
axes[0].bar([f"Type {s}" for s in specs], avg_dur, color=colors, alpha=0.85)
for i, v in enumerate(avg_dur):
    axes[0].text(i, v + 0.5, f'{v:.1f}h', ha='center', fontsize=10, fontweight='bold')
axes[0].set_xlabel('Case Type (Federation Node)')
axes[0].set_ylabel('Average Case Duration (hours)')
axes[0].set_title('Figure 7.1 – Per-Node Performance\n'
                  'Federated Analysis Across 3 Hospital Specialities')
axes[0].grid(axis='y', alpha=0.3)

true_vals = [fed_true.get(e, 0) for e, _ in top_edges]
dp_vals   = [fed_dp.get(e, 0) for e, _ in top_edges]
x = np.arange(len(top_edges))
axes[1].plot(x, true_vals, 'bo-', label='True counts', linewidth=2)
axes[1].plot(x, dp_vals,   'r^--', label=f'DP counts (ε={EPSILON})', linewidth=2)
axes[1].set_xlabel('Process Transition (top 10)')
axes[1].set_ylabel('Edge Count')
axes[1].set_title('Figure 7.2 – Differential Privacy Impact on Federated DFG\n'
                  'Privacy-Utility Trade-off in Federated Process Mining')
axes[1].legend(); axes[1].grid(alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'federated_process_mining.png'), dpi=150)
plt.close()
print("\n  FPM chart -> output/federated_process_mining.png")

# =============================================================================
# SECTION 8 – PROCESS ENHANCEMENT
# =============================================================================
print("\n" + "="*70)
print("SECTION 8: PROCESS ENHANCEMENT SUMMARY")
print("="*70)

case_meta['duration_h'] = durations

# Cancelled vs non-cancelled
canc   = case_meta[case_meta['is_cancelled'] == True]['duration_h']
normal = case_meta[case_meta['is_cancelled'] == False]['duration_h']
print(f"\n  Cancelled cases avg duration   : {canc.mean():.1f}h")
print(f"  Normal cases avg duration      : {normal.mean():.1f}h")

# Exception activity rates
for act in ['CODE NOK', 'REJECT', 'STORNO', 'REOPEN']:
    n = df[df['activity'] == act]['case_id'].nunique()
    print(f"  Cases with '{act}': {n:,} ({n/df['case_id'].nunique():.1%})")

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
axes[0].bar(['Normal Cases', 'Cancelled Cases'],
            [normal.mean(), canc.mean()],
            color=['steelblue', 'tomato'], alpha=0.85)
axes[0].set_ylabel('Average Duration (hours)')
axes[0].set_title('Figure 8.1 – Duration: Cancelled vs Normal Cases')
axes[0].grid(axis='y', alpha=0.3)

exc_activities = ['CODE NOK', 'REJECT', 'STORNO', 'REOPEN', 'DELETE']
exc_rates = [df[df['activity']==a]['case_id'].nunique()/df['case_id'].nunique()*100
             for a in exc_activities]
axes[1].bar(exc_activities, exc_rates, color='coral', alpha=0.85)
axes[1].set_ylabel('% of Cases Affected')
axes[1].set_title('Figure 8.2 – Exception Activity Rates\nProcess Enhancement Opportunities')
axes[1].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'process_enhancement.png'), dpi=150)
plt.close()
print("\n  Enhancement chart -> output/process_enhancement.png")

# =============================================================================
print("\n" + "="*70)
print("ANALYSIS COMPLETE")
print("="*70)
print(f"\n  Output files:")
for f in sorted(os.listdir(OUTPUT_DIR)):
    if f.endswith('.png'):
        print(f"    output/{f}")
