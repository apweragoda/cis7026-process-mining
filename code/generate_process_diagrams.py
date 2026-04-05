"""
generate_process_diagrams.py
==============================
Generates two diagrams for the CIS 7026 submission:

1. Business Flow Diagram  – high-level stakeholder interactions
2. Process Flow Diagram   – step-by-step activity flow (start to end)
   for the Hospital Billing and Claims Management process.

Run:
    python generate_process_diagrams.py
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

BASE       = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE, '..', 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# COLOUR PALETTE
# ─────────────────────────────────────────────────────────────────────────────
C_START  = '#1B5E20'   # dark green  – start/end events
C_TASK   = '#1565C0'   # dark blue   – normal activities
C_GW     = '#E65100'   # orange      – gateways / decisions
C_EXCEPT = '#B71C1C'   # red         – exception activities
C_ARROW  = '#37474F'   # dark grey   – arrows
C_BG     = '#FAFAFA'   # near-white  – background


def draw_rounded_box(ax, x, y, w, h, color, label, fontsize=9,
                     text_color='white', radius=0.3):
    box = FancyBboxPatch((x - w/2, y - h/2), w, h,
                          boxstyle=f"round,pad=0.05,rounding_size={radius}",
                          linewidth=1.2, edgecolor='white',
                          facecolor=color, zorder=3)
    ax.add_patch(box)
    ax.text(x, y, label, ha='center', va='center',
            fontsize=fontsize, color=text_color,
            fontweight='bold', zorder=4, wrap=True,
            multialignment='center')


def draw_diamond(ax, x, y, w, h, color, label, fontsize=8):
    diamond = plt.Polygon(
        [[x, y + h/2], [x + w/2, y], [x, y - h/2], [x - w/2, y]],
        closed=True, facecolor=color, edgecolor='white',
        linewidth=1.2, zorder=3
    )
    ax.add_patch(diamond)
    ax.text(x, y, label, ha='center', va='center',
            fontsize=fontsize, color='white', fontweight='bold', zorder=4,
            multialignment='center')


def arrow(ax, x1, y1, x2, y2, label='', color=C_ARROW):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=color,
                                lw=1.5, connectionstyle='arc3,rad=0'))
    if label:
        mx, my = (x1+x2)/2, (y1+y2)/2
        ax.text(mx + 0.05, my, label, fontsize=7.5, color=color,
                ha='left', va='center', style='italic')


# =============================================================================
# 1. BUSINESS FLOW DIAGRAM
# =============================================================================
def draw_business_flow():
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.set_xlim(0, 16); ax.set_ylim(0, 10)
    ax.set_facecolor(C_BG); fig.patch.set_facecolor(C_BG)
    ax.axis('off')
    ax.set_title('Figure B.1 – Business Flow Diagram: Hospital Billing & Claims Management Process\n'
                 'Showing stakeholder roles, system interactions, and information flows',
                 fontsize=12, fontweight='bold', pad=15, color='#1A237E')

    # ── Swim-lane backgrounds ──────────────────────────────────────────────
    lanes = [
        (0.2, 9.0, 1.4, 1.6, '#E3F2FD', 'Patient /\nInsurer'),
        (0.2, 7.2, 1.4, 1.6, '#E8F5E9', 'Clinical\nStaff'),
        (0.2, 5.4, 1.4, 1.6, '#FFF3E0', 'Hospital\nBilling Dept'),
        (0.2, 3.6, 1.4, 1.6, '#FCE4EC', 'ERP\nSystem'),
        (0.2, 1.8, 1.4, 1.6, '#F3E5F5', 'Insurance /\nPayer'),
    ]
    for lx, ly, lw, lh, lcolor, label in lanes:
        rect = FancyBboxPatch((lx, ly - lh/2), 15.6, lh,
                               boxstyle='round,pad=0.1', linewidth=0.5,
                               edgecolor='#BDBDBD', facecolor=lcolor, alpha=0.5, zorder=1)
        ax.add_patch(rect)
        ax.text(lx + 0.7, ly, label, ha='center', va='center',
                fontsize=9, fontweight='bold', color='#37474F', zorder=2)

    # ── Nodes ──────────────────────────────────────────────────────────────
    nodes = {
        # (x, y, color, label)
        'patient_visit':   (2.8,  9.0, C_START,  'Patient\nVisit / Admission'),
        'treatment':       (2.8,  7.2, C_TASK,   'Medical\nTreatment'),
        'diag_entry':      (5.2,  7.2, C_TASK,   'Diagnosis\nCode Entry'),
        'erp_new':         (5.2,  3.6, C_TASK,   'ERP: NEW\nCase Created'),
        'code_check':      (7.6,  3.6, C_GW,     'Validate\nBilling Code?'),
        'code_ok':         (7.6,  5.4, C_TASK,   'CODE OK\nConfirmed'),
        'code_nok':        (9.8,  3.6, C_EXCEPT, 'CODE NOK\nError Flagged'),
        'correction':      (9.8,  5.4, C_TASK,   'Diagnosis\nCorrection'),
        'release':         (11.8, 5.4, C_TASK,   'RELEASE\nFor Billing'),
        'billed':          (11.8, 3.6, C_TASK,   'BILLED\nInvoice Sent'),
        'ins_review':      (11.8, 1.8, C_TASK,   'Insurance\nReview'),
        'accept_reject':   (13.8, 1.8, C_GW,     'Claim\nAccepted?'),
        'payment':         (13.8, 3.6, C_TASK,   'Payment\nReceived'),
        'reject':          (13.8, 5.4, C_EXCEPT, 'REJECT /\nSTORNO'),
        'fin':             (13.8, 7.2, C_START,  'FIN\nCase Closed'),
    }

    for key, (x, y, color, label) in nodes.items():
        draw_rounded_box(ax, x, y, 1.8, 1.1, color, label, fontsize=8)

    # ── Arrows ────────────────────────────────────────────────────────────
    edges = [
        ('patient_visit', 'treatment',    ''),
        ('treatment',     'diag_entry',   'clinical notes'),
        ('diag_entry',    'erp_new',      'ERP input'),
        ('erp_new',       'code_check',   ''),
        ('code_check',    'code_ok',      'Valid'),
        ('code_check',    'code_nok',     'Invalid'),
        ('code_nok',      'correction',   'rework'),
        ('correction',    'code_ok',      ''),
        ('code_ok',       'release',      ''),
        ('release',       'billed',       ''),
        ('billed',        'ins_review',   'invoice'),
        ('ins_review',    'accept_reject',''),
        ('accept_reject', 'payment',      'Accept'),
        ('accept_reject', 'reject',       'Reject'),
        ('payment',       'fin',          ''),
        ('reject',        'fin',          'STORNO'),
    ]

    for src, tgt, lbl in edges:
        x1, y1 = nodes[src][0], nodes[src][1]
        x2, y2 = nodes[tgt][0], nodes[tgt][1]
        arrow(ax, x1, y1, x2, y2, lbl)

    # ── Legend ─────────────────────────────────────────────────────────────
    legend_items = [
        mpatches.Patch(color=C_START,  label='Start / End Event'),
        mpatches.Patch(color=C_TASK,   label='Normal Activity'),
        mpatches.Patch(color=C_GW,     label='Decision Gateway'),
        mpatches.Patch(color=C_EXCEPT, label='Exception Activity'),
    ]
    ax.legend(handles=legend_items, loc='lower left', fontsize=8,
              framealpha=0.9, ncol=4, bbox_to_anchor=(0.1, -0.01))

    plt.tight_layout()
    out = os.path.join(OUTPUT_DIR, 'business_flow_diagram.png')
    plt.savefig(out, dpi=180, bbox_inches='tight')
    plt.close()
    print(f"[OK] Business Flow Diagram -> output/business_flow_diagram.png")


# =============================================================================
# 2. PROCESS FLOW DIAGRAM (Start to End – all paths)
# =============================================================================
def draw_process_flow():
    fig, ax = plt.subplots(figsize=(14, 18))
    ax.set_xlim(0, 14); ax.set_ylim(0, 18)
    ax.set_facecolor(C_BG); fig.patch.set_facecolor(C_BG)
    ax.axis('off')
    ax.set_title('Figure B.2 – Process Flow Diagram: Hospital Billing & Claims Management\n'
                 'Complete activity flow from case creation (NEW) to closure (FIN)',
                 fontsize=12, fontweight='bold', pad=15, color='#1A237E')

    # Vertical layout: x=centre lane, y decreasing top to bottom
    # Happy path: NEW → CHANGE DIAGN → FIN → RELEASE → CODE OK → BILLED → FIN(close)
    # Exception paths branch left/right

    W, H = 2.2, 0.75   # box width, height
    CX   = 7.0          # centre x

    steps = [
        # (x,    y,     color,    type,   label)
        (CX,    17.2,  C_START,  'box',  'START EVENT\nBilling Case Opened'),
        (CX,    16.0,  C_TASK,   'box',  'NEW\nCase Created in ERP'),
        (CX,    14.8,  C_GW,     'dmd',  'Diagnosis\nComplete?'),
        (CX,    13.6,  C_TASK,   'box',  'CHANGE DIAGN\nUpdate Diagnosis Code'),
        (CX,    12.4,  C_GW,     'dmd',  'Valid\nBilling Code?'),
        (CX,    11.2,  C_TASK,   'box',  'CODE OK\nBilling Code Validated'),
        (CX,    10.0,  C_TASK,   'box',  'RELEASE\nCase Released for Billing'),
        (CX,     8.8,  C_TASK,   'box',  'BILLED\nInvoice Sent to Payer'),
        (CX,     7.6,  C_GW,     'dmd',  'Claim\nOutcome?'),
        (CX,     6.4,  C_TASK,   'box',  'FIN\nCase Finalised'),
        (CX,     5.2,  C_START,  'box',  'END EVENT\nCase Closed'),
    ]

    # Exception / side paths
    side_steps = [
        # CODE NOK branch (right side)
        (10.5, 12.4,  C_EXCEPT, 'box', 'CODE NOK\nValidation Failed'),
        (10.5, 11.2,  C_TASK,   'box', 'MANUAL\nReview Required'),
        # STORNO/REJECT branch (left)
        (3.5,   7.6,  C_EXCEPT, 'box', 'REJECT\nor STORNO'),
        (3.5,   6.4,  C_TASK,   'box', 'REOPEN\nCase Corrected'),
        # DELETE branch (right top)
        (10.5, 14.8,  C_EXCEPT, 'box', 'DELETE\nCase Removed'),
        # SET STATUS
        (10.5,  6.4,  C_TASK,   'box', 'SET STATUS\nStatus Update'),
    ]

    # Draw main path
    for x, y, color, shape, label in steps:
        if shape == 'dmd':
            draw_diamond(ax, x, y, W * 0.9, H * 1.4, color, label, fontsize=8)
        else:
            draw_rounded_box(ax, x, y, W, H, color, label, fontsize=8)

    # Draw side paths
    for x, y, color, shape, label in side_steps:
        draw_rounded_box(ax, x, y, W, H, color, label, fontsize=8)

    # ── Main flow arrows ──────────────────────────────────────────────────
    main_arrows = [
        (CX, 17.2-H/2, CX, 16.0+H/2, ''),
        (CX, 16.0-H/2, CX, 14.8+0.35, ''),           # to gateway
        (CX, 14.8-0.35, CX, 13.6+H/2, 'No'),
        (CX, 13.6-H/2, CX, 12.4+0.35, ''),
        (CX, 12.4-0.35, CX, 11.2+H/2, 'Yes'),
        (CX, 11.2-H/2, CX, 10.0+H/2, ''),
        (CX, 10.0-H/2, CX,  8.8+H/2, ''),
        (CX,  8.8-H/2, CX,  7.6+0.35, ''),
        (CX,  7.6-0.35, CX, 6.4+H/2, 'Paid'),
        (CX,  6.4-H/2, CX,  5.2+H/2, ''),
    ]
    for x1, y1, x2, y2, lbl in main_arrows:
        arrow(ax, x1, y1, x2, y2, lbl)

    # ── Side path arrows ──────────────────────────────────────────────────
    # Delete branch
    ax.annotate('', xy=(10.5, 14.8+H/2), xytext=(CX+0.45, 14.8),
                arrowprops=dict(arrowstyle='->', color=C_EXCEPT, lw=1.4,
                                connectionstyle='arc3,rad=0'))
    ax.text(8.9, 14.9, 'Yes (delete)', fontsize=7.5, color=C_EXCEPT, style='italic')

    # CODE NOK branch
    ax.annotate('', xy=(10.5, 12.4+H/2), xytext=(CX+0.45, 12.4),
                arrowprops=dict(arrowstyle='->', color=C_EXCEPT, lw=1.4,
                                connectionstyle='arc3,rad=0'))
    ax.text(8.9, 12.5, 'No', fontsize=7.5, color=C_EXCEPT, style='italic')
    arrow(ax, 10.5, 12.4-H/2, 10.5, 11.2+H/2, '')
    # CODE NOK loop back to CODE OK
    ax.annotate('', xy=(CX+W/2, 11.2), xytext=(10.5, 11.2-H/2),
                arrowprops=dict(arrowstyle='->', color=C_TASK, lw=1.4,
                                connectionstyle='arc3,rad=-0.3'))
    ax.text(10.0, 10.5, 're-validate', fontsize=7, color=C_TASK, style='italic')

    # REJECT branch
    ax.annotate('', xy=(3.5, 7.6+H/2), xytext=(CX-0.45, 7.6),
                arrowprops=dict(arrowstyle='->', color=C_EXCEPT, lw=1.4,
                                connectionstyle='arc3,rad=0'))
    ax.text(4.3, 7.75, 'Rejected', fontsize=7.5, color=C_EXCEPT, style='italic')
    arrow(ax, 3.5, 7.6-H/2, 3.5, 6.4+H/2, '')
    # Reopen loops back
    ax.annotate('', xy=(CX-W/2, 13.6), xytext=(3.5, 6.4+H/2),
                arrowprops=dict(arrowstyle='->', color=C_TASK, lw=1.4,
                                connectionstyle='arc3,rad=0.4'))
    ax.text(2.0, 10.5, 'reopen →\nrecode', fontsize=7, color=C_TASK,
            style='italic', ha='center')

    # SET STATUS side step
    ax.annotate('', xy=(10.5, 6.4+H/2), xytext=(CX+0.45, 6.4),
                arrowprops=dict(arrowstyle='->', color=C_TASK, lw=1.4,
                                connectionstyle='arc3,rad=0'))
    ax.text(8.9, 6.5, 'set status', fontsize=7.5, color=C_TASK, style='italic')
    ax.annotate('', xy=(CX+0.45, 5.2+H/2), xytext=(10.5, 6.4-H/2),
                arrowprops=dict(arrowstyle='->', color=C_TASK, lw=1.4,
                                connectionstyle='arc3,rad=-0.3'))

    # ── Legend ────────────────────────────────────────────────────────────
    legend_items = [
        mpatches.Patch(color=C_START,  label='Start / End Event'),
        mpatches.Patch(color=C_TASK,   label='Normal Activity'),
        mpatches.Patch(color=C_GW,     label='Decision Gateway'),
        mpatches.Patch(color=C_EXCEPT, label='Exception Activity'),
    ]
    ax.legend(handles=legend_items, loc='lower center', fontsize=9,
              framealpha=0.9, ncol=2, bbox_to_anchor=(0.5, 0.0))

    plt.tight_layout()
    out = os.path.join(OUTPUT_DIR, 'process_flow_diagram.png')
    plt.savefig(out, dpi=180, bbox_inches='tight')
    plt.close()
    print(f"[OK] Process Flow Diagram   -> output/process_flow_diagram.png")


# =============================================================================
if __name__ == '__main__':
    draw_business_flow()
    draw_process_flow()
    print("\nBoth diagrams saved to output/")
