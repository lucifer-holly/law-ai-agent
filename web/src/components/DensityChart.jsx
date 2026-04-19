import { useMemo } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  ResponsiveContainer,
  ReferenceLine,
  Tooltip,
  Cell,
} from "recharts";

/**
 * Similarity distribution histogram.
 *
 * X axis: cosine similarity bucket (0 to 1, 25 equal-width bins).
 * Y axis: count of same-category clauses falling in that bucket.
 * A dashed rule marks the sim_threshold used for the density statistic.
 * A cognac rule marks the top-1 similarity (the "nearest" score).
 */
export default function DensityChart({ distribution, nearest, simThreshold }) {
  const { bins, maxSim } = useMemo(() => {
    const N_BINS = 25;
    const maxSim = 1.0;
    const bins = Array.from({ length: N_BINS }, (_, i) => ({
      start: (i / N_BINS) * maxSim,
      end: ((i + 1) / N_BINS) * maxSim,
      label: `${((i + 0.5) / N_BINS).toFixed(2)}`,
      count: 0,
    }));
    for (const s of distribution) {
      const s_clamped = Math.max(0, Math.min(maxSim - 1e-9, s));
      const idx = Math.min(N_BINS - 1, Math.floor((s_clamped / maxSim) * N_BINS));
      bins[idx].count += 1;
    }
    return { bins, maxSim };
  }, [distribution]);

  const nearestBinIndex = Math.min(
    bins.length - 1,
    Math.floor((Math.max(0, nearest) / maxSim) * bins.length)
  );

  // Which bin label to anchor the "threshold" reference line on.
  const thresholdBinIdx = bins.findIndex((b) => b.start >= simThreshold);
  const thresholdLabel =
    thresholdBinIdx >= 0
      ? bins[thresholdBinIdx].label
      : bins[bins.length - 1].label;

  return (
    <div className="bg-parchment-50 shadow-inset rounded-md p-6">
      <div className="flex items-start justify-between mb-1">
        <div>
          <div className="eyebrow mb-1">Distance to Market</div>
          <div className="text-sm text-ink-700 max-w-md">
            Similarity of <em>every</em> same-category clause to this query.
            Dense clusters near 1 → standard phrasing; long tail near 0 →
            idiosyncratic drafting.
          </div>
        </div>
        <LegendKey simThreshold={simThreshold} />
      </div>

      <div className="h-[260px] mt-5 -ml-2">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={bins} barGap={1} margin={{ top: 20, right: 8, left: 0, bottom: 8 }}>
            <XAxis
              dataKey="label"
              interval={3}
              tick={{
                fontFamily: "JetBrains Mono, monospace",
                fontSize: 10,
                fill: "#6b7690",
              }}
              axisLine={{ stroke: "#0a1e3a22" }}
              tickLine={false}
            />
            <YAxis
              width={28}
              tick={{
                fontFamily: "JetBrains Mono, monospace",
                fontSize: 10,
                fill: "#6b7690",
              }}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip
              cursor={{ fill: "rgba(10,30,58,0.05)" }}
              contentStyle={{
                background: "#fbf9f4",
                border: "1px solid #0a1e3a22",
                borderRadius: "4px",
                padding: "6px 10px",
                fontFamily: "JetBrains Mono, monospace",
                fontSize: 11,
              }}
              labelFormatter={(v) => `sim ≈ ${v}`}
              formatter={(v) => [v, "clauses"]}
            />
            <ReferenceLine
              x={thresholdLabel}
              stroke="#0a1e3a"
              strokeDasharray="3 3"
              strokeOpacity={0.5}
              label={{
                value: `threshold ${simThreshold}`,
                position: "top",
                fontSize: 9,
                fill: "#43516a",
                fontFamily: "JetBrains Mono, monospace",
              }}
            />
            <Bar dataKey="count" radius={[1, 1, 0, 0]}>
              {bins.map((_, i) => (
                <Cell
                  key={i}
                  fill={i === nearestBinIndex ? "#b8562c" : "#28384f"}
                  fillOpacity={i === nearestBinIndex ? 0.95 : 0.78}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="rule-hairline mt-2 mb-3" />

      <div className="flex flex-wrap gap-x-6 gap-y-1 font-mono text-[11px] text-ink-500">
        <div>
          sample&nbsp;size&nbsp;
          <span className="text-ink-800">{distribution.length}</span>
        </div>
        <div>
          top-1&nbsp;
          <span className="text-ink-800">{nearest.toFixed(3)}</span>
        </div>
        <div>
          threshold&nbsp;
          <span className="text-ink-800">{simThreshold}</span>
        </div>
      </div>
    </div>
  );
}

function LegendKey({ simThreshold }) {
  return (
    <div className="font-mono text-[10px] text-ink-500 space-y-1 text-right">
      <div className="flex items-center justify-end gap-2">
        <span className="w-3 h-2 bg-cognac-500 opacity-90" /> top-1 bin
      </div>
      <div className="flex items-center justify-end gap-2">
        <span className="w-3 h-0 border-t border-dashed border-ink-900/60" /> threshold {simThreshold}
      </div>
    </div>
  );
}
