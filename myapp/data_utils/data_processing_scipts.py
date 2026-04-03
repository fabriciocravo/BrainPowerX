from data_utils.data_plot_utils import *

# This is likely only compatible with the old data structure.
# I will likely need to upload a check for the new versus old .mat files



raise ValueError('This script is current being accessed for usage. '
                 'I decided to move plotting generation to matlab to avoid major issues')

# ─────────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────────
data_p = r"C:\Users\Fabricio\Desktop\Cloned Repos\BrainPowerX\myapp\data\hpc_fc_tasks\power_calculation"
data_set_folder_path = Path(data_p)

parent_name = data_set_folder_path.parent.name
output_dir  = Path(__file__).parent / "data" / parent_name
output_dir.mkdir(parents=True, exist_ok=True)

EDGE_METHODS    = ["Parametric_FWER", "Parametric_FDR", "Size", "Fast_TFCE"]
NETWORK_METHODS = ["Constrained_FWER", "Constrained_FDR"]
OMNIBUS_METHODS = ["Omnibus_Multidimensional_cNBS"]
ALL_METHODS     = EDGE_METHODS + NETWORK_METHODS + OMNIBUS_METHODS

POWER_THRESHOLDS = [80, 50, 20]


# ─────────────────────────────────────────────
#  LOAD ALL FILES
# ─────────────────────────────────────────────
grouped   = defaultdict(lambda: defaultdict(dict))
mat_files = sorted(data_set_folder_path.glob("*.mat"))

if not mat_files:
    raise FileNotFoundError(f"No .mat files found in {data_set_folder_path}")

print(f"Found {len(mat_files)} .mat files.")

for mat_file in mat_files:
    try:
        dataset, map_type, task, test, n_subs = parse_filename(mat_file)
    except Exception as e:
        print(f"  [SKIP] {mat_file.name}: {e}")
        continue

    data = loadmat(str(mat_file))
    key  = (dataset, map_type, task, test)

    for method in ALL_METHODS:
        if method in data:
            grouped[key][n_subs][method] = extract_power(data, method)

    if "mask" not in grouped[key]:
        try:
            mask, edge_groups = extract_meta(data)
            grouped[key]["mask"]        = mask
            grouped[key]["edge_groups"] = edge_groups
        except Exception as e:
            print(f"  [WARN] meta extraction failed {mat_file.name}: {e}")

    print(f"  Loaded: {mat_file.name}")

print(f"\nGrouped into {len(grouped)} combinations.\n")

# ─────────────────────────────────────────────
#  EXCEL HELPERS
# ─────────────────────────────────────────────
HDR_FILL = PatternFill("solid", start_color="1a1d2e", end_color="1a1d2e")
HDR_FONT = Font(bold=True, color="a5b4fc", name="Arial", size=9)
DAT_FONT = Font(name="Arial", size=9)
TTL_FONT = Font(bold=True, color="06b6d4", name="Arial", size=11)


def write_matrix_tab(ws, matrix, title, number_format="0.00"):
    """Write title then a labelled square matrix starting at row 1."""
    n = matrix.shape[0]

    ws["A1"] = title
    ws["A1"].font = TTL_FONT

    for j in range(n):
        c = ws.cell(row=2, column=j + 2, value=j + 1)
        c.font = HDR_FONT
        c.fill = HDR_FILL
        c.alignment = Alignment(horizontal="center")

    for i in range(n):
        rh = ws.cell(row=i + 3, column=1, value=i + 1)
        rh.font = HDR_FONT
        rh.fill = HDR_FILL
        rh.alignment = Alignment(horizontal="center")
        for j in range(n):
            c = ws.cell(row=i + 3, column=j + 2, value=float(matrix[i, j]))
            c.font          = DAT_FONT
            c.number_format = number_format
            c.alignment     = Alignment(horizontal="right")

    ws.column_dimensions["A"].width = 6
    for j in range(n):
        ws.column_dimensions[get_column_letter(j + 2)].width = 7


def write_power_tab(ws, full_matrices, n_subs_list, methods):
    """
    Tab 1: one stacked block per method.
    Each block contains all sample sizes side by side as 268x268 matrices.
    """
    row_cursor = 1
    for method in methods:
        ws.cell(row=row_cursor, column=1, value=method).font = TTL_FONT
        row_cursor += 1

        col_cursor = 1
        n_nodes    = None

        for n in n_subs_list:
            mat = full_matrices.get((n, method))
            if mat is None:
                continue
            n_nodes = mat.shape[0]

            ws.cell(row=row_cursor, column=col_cursor,
                    value=f"n = {n}").font = Font(bold=True, color="f59e0b",
                                                   name="Arial", size=10)
            for j in range(n_nodes):
                c = ws.cell(row=row_cursor + 1, column=col_cursor + j + 1,
                            value=j + 1)
                c.font = HDR_FONT
                c.fill = HDR_FILL
                c.alignment = Alignment(horizontal="center")

            for i in range(n_nodes):
                rh = ws.cell(row=row_cursor + 2 + i,
                             column=col_cursor, value=i + 1)
                rh.font = HDR_FONT
                rh.fill = HDR_FILL
                rh.alignment = Alignment(horizontal="center")
                for j in range(n_nodes):
                    c = ws.cell(row=row_cursor + 2 + i,
                                column=col_cursor + j + 1,
                                value=float(mat[i, j]))
                    c.font          = DAT_FONT
                    c.number_format = "0.00"
                    c.alignment     = Alignment(horizontal="right")

            col_cursor += n_nodes + 2

        if n_nodes is not None:
            row_cursor += n_nodes + 5


def write_calculations_tab(ws, full_matrices, n_subs_list, methods, thresholds):
    """
    Tab 2: edge counts above each power threshold, per method x sample size.
    """
    ws["A1"] = "Number of edges (ROI pairs) above power threshold"
    ws["A1"].font = TTL_FONT

    ws.cell(row=2, column=1, value="Method").font = HDR_FONT
    ws.cell(row=2, column=1).fill                 = HDR_FILL
    ws.column_dimensions["A"].width               = 28

    col = 2
    for n in n_subs_list:
        ws.cell(row=2, column=col, value=f"n = {n}").font = \
            Font(bold=True, color="f59e0b", name="Arial", size=10)
        ws.cell(row=2, column=col).fill = HDR_FILL

        for thr in thresholds:
            c = ws.cell(row=3, column=col, value=f">= {thr}%")
            c.font      = HDR_FONT
            c.fill      = HDR_FILL
            c.alignment = Alignment(horizontal="center")
            ws.column_dimensions[get_column_letter(col)].width = 10
            col += 1

    for m_idx, method in enumerate(methods):
        row = 4 + m_idx
        ws.cell(row=row, column=1, value=method).font = \
            Font(bold=True, name="Arial", size=9, color="e2e8f0")

        col = 2
        for n in n_subs_list:
            mat = full_matrices.get((n, method))
            for thr in thresholds:
                if mat is not None:
                    # matrix is symmetric so divide by 2 for unique edge count
                    count = int(np.sum(mat > thr)) // 2
                else:
                    count = ""
                c = ws.cell(row=row, column=col, value=count)
                c.font      = DAT_FONT
                c.alignment = Alignment(horizontal="center")
                col += 1


def build_excel(group_dir, key, subs_data, n_subs_list):
    dataset, map_type, task, test = key
    mask        = subs_data.get("mask")
    edge_groups = subs_data.get("edge_groups")

    if mask is None:
        print("  [SKIP EXCEL] mask not found.")
        return

    full_matrices = {}
    for n in n_subs_list:
        for method in EDGE_METHODS:
            if method in subs_data[n]:
                full_matrices[(n, method)] = roi_roi_unflat(
                    subs_data[n][method], mask)

    wb = Workbook()
    wb.remove(wb.active)

    ws1 = wb.create_sheet("Power Data")
    write_power_tab(ws1, full_matrices, n_subs_list, EDGE_METHODS)

    ws2 = wb.create_sheet("Calculations")
    write_calculations_tab(ws2, full_matrices, n_subs_list,
                           EDGE_METHODS, POWER_THRESHOLDS)

    ws3 = wb.create_sheet("Networks")
    write_matrix_tab(ws3, edge_groups,
                     "Edge groups — Shen atlas network IDs",
                     number_format="0")

    ws4 = wb.create_sheet("Mask")
    write_matrix_tab(ws4, mask.astype(float),
                     "Mask (1 = included edge)",
                     number_format="0")

    fname = group_dir / f"{dataset}_{map_type}_{task}_{test}.xlsx"
    wb.save(str(fname))
    print(f"  ✓ Excel saved: {fname.name}")

# ─────────────────────────────────────────────
#  PLOTTING HELPERS
# ─────────────────────────────────────────────
STYLE = {"figure.facecolor": "#0f1117", "axes.facecolor": "#1a1d2e",
         "axes.edgecolor": "#3a3f5c", "grid.color": "#2a2f4a",
         "text.color": "#e2e8f0", "axes.labelcolor": "#e2e8f0",
         "xtick.color": "#94a3b8", "ytick.color": "#94a3b8",
         "axes.grid": True, "grid.alpha": 0.4}


def save_fig(fig, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)


def make_title(dataset, map_type, task, test, extra=""):
    t = f"{dataset.upper()} | {map_type.upper()} | {task} | test={test}"
    return t + (f"\n{extra}" if extra else "")

# ─────────────────────────────────────────────
#  MAIN LOOP
# ─────────────────────────────────────────────
for key, subs_data in grouped.items():
    dataset, map_type, task, test = key

    group_dir = output_dir / f"{dataset}_{map_type}" / task / test
    group_dir.mkdir(parents=True, exist_ok=True)

    n_subs_list = sorted([k for k in subs_data if isinstance(k, int)])
    ns          = np.array(n_subs_list, dtype=float)
    mask        = subs_data.get("mask")

    print(f"\nProcessing: {dataset}_{map_type} / {task} / {test}  "
          f"[n = {n_subs_list}]")

    # ── 1. AVERAGE POWER CURVES ──────────────────────────────────────────
    with plt.rc_context(STYLE):
        fig, axes = plt.subplots(
            len(ALL_METHODS), 1,
            figsize=(10, 3.8 * len(ALL_METHODS)),
            facecolor="#0f1117"
        )
        if len(ALL_METHODS) == 1:
            axes = [axes]

        for ax, method in zip(axes, ALL_METHODS):
            avg_p = np.array([
                np.mean(subs_data[n][method])
                if method in subs_data[n] else np.nan
                for n in n_subs_list
            ])
            valid = ~np.isnan(avg_p)
            ax.scatter(ns[valid], avg_p[valid], s=60, zorder=5,
                       color="#a5b4fc", label="Observed avg power")

            fit = fit_power_curve(ns, avg_p)
            if fit:
                popt, n_d, y_d = fit
                ax.plot(n_d, y_d, color="#06b6d4", lw=2,
                        label=f"Fit  P={popt[0]:.1f}  a={popt[1]:.1f}"
                              f"  b={popt[2]:.2f}")

            ax.axhline(80, color="#f59e0b", ls="--", lw=1.2, alpha=0.7,
                       label="80% threshold")
            ax.set_title(method, fontsize=11, fontweight="bold")
            ax.set_xlabel("Sample size (n)")
            ax.set_ylabel("Power (%)")
            ax.set_ylim(-2, 105)
            ax.legend(fontsize=8)

        fig.suptitle(make_title(dataset, map_type, task, test,
                                "Average Power Curves"),
                     fontsize=13, fontweight="bold", y=1.01)
        fig.tight_layout()
        save_fig(fig, group_dir / "power_curves_average.png")

    print("  ✓ Average power curves saved.")

    # ── 2. HEATMAPS ──────────────────────────────────────────────────────
    if mask is not None:
        for n in n_subs_list:
            heatmap_dir = group_dir / f"heatmaps_n{n}"
            heatmap_dir.mkdir(exist_ok=True)

            for method in EDGE_METHODS:
                if method not in subs_data[n]:
                    continue

                mat = roi_roi_unflat(subs_data[n][method], mask)

                with plt.rc_context(STYLE):
                    fig, ax = plt.subplots(figsize=(9, 8), facecolor="#0f1117")
                    im = ax.imshow(mat, cmap="inferno", vmin=0, vmax=100,
                                   aspect="auto", interpolation="nearest")
                    plt.colorbar(im, ax=ax, label="Power (%)",
                                 fraction=0.046, pad=0.04)
                    ax.set_title(make_title(dataset, map_type, task, test,
                                            f"{method}  |  n = {n}"),
                                 fontsize=10, fontweight="bold")
                    ax.set_xlabel("Node index")
                    ax.set_ylabel("Node index")
                    fig.tight_layout()
                    save_fig(fig, heatmap_dir / f"heatmap_{method}.png")

        print(f"  ✓ Heatmaps saved for n = {n_subs_list}.")

    # ── 3. EXCEL ──────────────────────────────────────────────────────────
    build_excel(group_dir, key, subs_data, n_subs_list)

print("\n✅  All done!  Outputs are under:", output_dir)