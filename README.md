# TTP Solutions Web Explorer

Interactive browser-based viewer for **Travelling Thief Problem (TTP)** solver results.

**Live demo:** https://YOUR_USERNAME.github.io/ttpweb/

> Replace the link above with your actual GitHub Pages URL once published.

---

## What is this?

The TTP combines the Travelling Salesman Problem (TSP) with the 0/1 Knapsack Problem: a thief must visit cities, pick up items to maximize profit, and return home — while carrying weight that slows them down. This explorer lets you visually browse and compare solutions produced by different solvers (Gurobi, Hexaly, etc.) across multiple TTP instances.

No installation needed — everything runs in your browser.

---

## Files

| File | Purpose |
|---|---|
| `index.html` | Self-contained web explorer — all solution data embedded, no server or dependencies needed |
| `generate_index.py` | Scans solution folders, embeds all data, and writes `index.html` |
| `solutions_index.json` | Auto-generated JSON manifest (written alongside `index.html`) |

---

## Open Locally

Double-click `index.html` or drag it into any browser — no server needed.  
All solution data is embedded directly in the file at generation time.

---

## Regenerate After a New Solver Run

Every time a solver produces new `*_sol.json` files, regenerate the explorer:

```bash
# from inside this folder:
python3 generate_index.py
```

This rewrites both `index.html` (self-contained) and `solutions_index.json`.

> **Tour index normalization:** the generator automatically converts 0-based tour arrays (as saved by some Gurobi runs) to 1-based to match the node index convention.

---

## Using the Explorer

| Area | Description |
|---|---|
| **Sidebar (left)** | Collapsible file tree: runs → pools → solutions. Use the search box to filter. |
| **Map (center)** | SVG tour map. Drag to pan, scroll to zoom. |
| **Info panel (right)** | Solver status, objective, profit, distance, weight/capacity bar, sortable picked-items table. |

### Map Controls

| Button | Action |
|---|---|
| **Tour** | Toggle tour edges on/off |
| **Items** | Toggle item-city highlights on/off |
| **Labels** | Toggle city index labels on/off |
| **Fit** | Reset zoom and re-center the map |

### City Colors

| Color | Meaning |
|---|---|
| Red | Depot (city 1) |
| Amber with halo | City with at least one picked item |
| Blue-grey | Empty city (no items picked) |

Tour edges are drawn in gray with directional arrowheads showing the traversal order.

---

## Solution File Naming Convention

```
ttp_solutions_json/
  {solver}_{YYYYMMDD_HHMMSS}/     ← one folder per run
    {pool_name}/
      {instance_name}_sol.json    ← one file per instance
```

Example:
```
ttp_solutions_json/
  gurobi_20260505_231626/
    toy-10-ttp/
      toy-10_n9_bounded-strongly-corr_01_sol.json
```
