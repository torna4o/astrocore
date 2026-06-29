import matplotlib.pyplot as plt
import numpy as np

from astrocore.io.registry import Registry
from astrocore.io.local import LocalFITS

from astrocore.segmentation import TimeSeriesSegmentation
from astrocore.preprocessors.ssa import SSA
from astrocore.analysis.component_analysis import ComponentAnalyzer
from astrocore.analysis.w_correlation import WCorrelation

# ============================================================
# 1. LOAD FROM REGISTRY
# ============================================================

registry = Registry()

for row in registry.list_products():
    print(row)

product_id = int(input("\nSelect product_id: "))
fits_path = registry.get_filepath(product_id)

print("\nSelected file:")
print(fits_path)

source = LocalFITS(fits_path)
lc = source.load()

t = lc["t"]
y = lc["y"]


# ============================================================
# 2. SEGMENTATION
# ============================================================

segmenter = TimeSeriesSegmentation(
    cadence_gap_tolerance=1.0
)

segments_output = segmenter.run(
    {
        "t": t,
        "y": y,
        "meta": {}
    }
)

segments = segments_output["chunks"]

print(f"\nSegments found: {len(segments)}")
"""
for i, seg in enumerate(segments):
    print(
        f"Segment {i}: "
        f"length={len(seg['t'])}, "
        f"span={seg['t'][-1] - seg['t'][0]:.3f}"
    )
"""

min_len = int(input("\nMinimum segment length to filter: "))

filtered = [
    c for c in segments
    if c["length"] >= min_len
    ]

print(f"\nFiltered segments: {len(filtered) / len(segments)}")

for i, c in enumerate(filtered):
    print(
        f"[{i}] len{c['length']:5d} | "
        f"span={c['duration']:.3f} | "
        f"pos={c['relative_position']:.2f}"
    )
    
# ============================================================
# 3. SELECT SEGMENT
# ============================================================

seg_id = int(input("\nSelect segment index: "))
segment = filtered[seg_id]


# ============================================================
# 4. CHOOSE SSA WINDOW
# ============================================================

L = int(input("\nEnter SSA window L: "))


ssa = SSA(window=L, analyses=None)
result = ssa.run(segment)


# ============================================================
# 5. COMPONENT ANALYSIS (FFT etc.)
# ============================================================

analyzer = ComponentAnalyzer()
result = analyzer.analyze(result, analyses=["fft"])


# ============================================================
# 6. PLOTS
# ============================================================

# ---- raw signal ----
plt.figure()
plt.plot(segment["t"], segment["y"])
plt.title("Selected Segment")
plt.xlabel("Time")
plt.ylabel("Flux")


# ---- SSA components ----
n = len(result.components)

fig, axes = plt.subplots(20, 1, figsize=(10, 2*n), sharex=True)

if n == 1:
    axes = [axes]

for i, comp in enumerate(result.components[0:20]):
    axes[i].plot(comp.time, comp.flux)
    axes[i].set_title(
        f"Component {i} | "
        f"Energy frac={comp.energy_fraction:.4f}"
    )

plt.tight_layout()


# ---- FFT plots ----
plt.figure()

for i, comp in enumerate(result.components[0:20]):

    fft = comp.analyses.get("fft")

    if fft is None:
        continue

    freq = fft["frequency"]
    power = fft["power"]

    plt.plot(freq, power, label=f"C{i}")

plt.legend()
plt.title("Component FFT Power Spectra")
plt.xlabel("Frequency")
plt.ylabel("Power")


# ---- W-Correlation Matrix Plot ----


comp_matrix = np.array((result.components[0].flux))
for idx, i in enumerate(result.components):
    print(idx)
    if idx + 1 == len(result.components):
        break
    comp_matrix = np.vstack((comp_matrix,result.components[idx+1].flux))
    
w_corr = WCorrelation(window=L).compute(comp_matrix.T)

plt.imshow(w_corr, cmap="afmhot")
plt.show()
