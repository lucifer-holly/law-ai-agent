export default function ScoreCard({ score, categoryStats, clauseType }) {
  const pct = Math.round(score.percentile_in_category * 100);
  const pctOrdinal = ordinal(pct);
  const levelClass = levelTextClass(score.level);
  const dotClass = levelBgClass(score.level);

  return (
    <div className="bg-parchment-50 shadow-inset rounded-md p-6">
      <div className="flex items-center justify-between mb-5">
        <div className="eyebrow">Index Score</div>
        <div className="flex items-center gap-2">
          <span className={`inline-block h-2 w-2 rounded-full ${dotClass}`} />
          <span className={`font-mono text-[11px] uppercase tracking-wide-cap ${levelClass}`}>
            {score.level}
          </span>
        </div>
      </div>

      <div className="flex items-baseline gap-3">
        <div className="font-display text-[96px] leading-none tracking-tightest text-ink-900">
          {score.score.toFixed(2)}
        </div>
        <div className="text-ink-500 text-xs font-mono">/ 1.00</div>
      </div>

      <div className="rule-hairline-dashed my-5" />

      <div className="grid grid-cols-2 gap-x-6 gap-y-4 text-sm">
        <Metric
          label="Density"
          value={score.density.toFixed(2)}
          caption={`share of top-K ≥ sim threshold`}
        />
        <Metric
          label="Nearest"
          value={score.nearest.toFixed(3)}
          caption="similarity of top-1 neighbour"
        />
      </div>

      <div className="rule-hairline my-5" />

      <div>
        <div className="eyebrow mb-2">Percentile in Category</div>
        <div className="flex items-baseline gap-2">
          <div className="font-display text-4xl leading-none text-ink-900">
            {pctOrdinal}
          </div>
          <div className="text-xs text-ink-500">among {categoryStats.n} {clauseType} clauses</div>
        </div>

        <PercentileRail percentile={pct / 100} />

        <div className="mt-3 font-mono text-[10px] text-ink-500 leading-relaxed">
          category mean <span className="text-ink-800">{categoryStats.mean.toFixed(2)}</span>
          {"   "}· p25 <span className="text-ink-800">{categoryStats.p25.toFixed(2)}</span>
          {"   "}· p75 <span className="text-ink-800">{categoryStats.p75.toFixed(2)}</span>
        </div>
      </div>
    </div>
  );
}

function Metric({ label, value, caption }) {
  return (
    <div>
      <div className="eyebrow mb-1">{label}</div>
      <div className="font-display text-3xl text-ink-900 leading-none">{value}</div>
      <div className="mt-1 text-[11px] text-ink-500">{caption}</div>
    </div>
  );
}

function PercentileRail({ percentile }) {
  // A single horizontal rail with the current percentile marked.
  return (
    <div className="relative h-1.5 bg-ink-900/10 rounded-full mt-3 overflow-visible">
      <div
        className="absolute top-0 left-0 h-full bg-cognac-500/70 rounded-full"
        style={{ width: `${percentile * 100}%` }}
      />
      <div
        className="absolute top-1/2 -translate-y-1/2 w-[3px] h-4 bg-ink-900 rounded-sm"
        style={{ left: `calc(${percentile * 100}% - 1.5px)` }}
      />
    </div>
  );
}

function ordinal(n) {
  const s = ["th", "st", "nd", "rd"];
  const v = n % 100;
  return n + (s[(v - 20) % 10] || s[v] || s[0]);
}

function levelTextClass(level) {
  switch (level) {
    case "Highly Atypical": return "text-level-highly-atypical";
    case "Atypical":        return "text-level-atypical";
    case "Mixed":           return "text-level-mixed";
    case "Standard":        return "text-level-standard";
    case "Highly Standard": return "text-level-highly-standard";
    default:                return "text-ink-500";
  }
}

function levelBgClass(level) {
  switch (level) {
    case "Highly Atypical": return "bg-level-highly-atypical";
    case "Atypical":        return "bg-level-atypical";
    case "Mixed":           return "bg-level-mixed";
    case "Standard":        return "bg-level-standard";
    case "Highly Standard": return "bg-level-highly-standard";
    default:                return "bg-ink-500";
  }
}
