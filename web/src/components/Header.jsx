export default function Header({ meta }) {
  return (
    <header className="border-b border-ink-900/10 bg-parchment-50/50 backdrop-blur-sm sticky top-0 z-10">
      <div className="mx-auto max-w-[1400px] px-6 lg:px-10 py-5 flex items-end justify-between gap-6">
        <div>
          <div className="eyebrow mb-1">A Law Insider–Inspired Experiment</div>
          <h1 className="display text-[44px] sm:text-[52px] leading-none">
            Clause{" "}
            <em className="font-display italic text-cognac-500">Index</em>
          </h1>
          <p className="mt-2 text-sm text-ink-600 max-w-xl">
            A market-alignment score for commercial-contract clauses, derived
            from {meta.n_clauses_total} expert-labelled CUAD clauses across{" "}
            {meta.n_categories} categories — computed entirely without a
            language model on the critical path.
          </p>
        </div>

        <div className="hidden md:grid grid-cols-3 gap-6 text-right font-mono text-[11px] text-ink-500">
          <Metric label="clauses" value={meta.n_clauses_total} />
          <Metric label="categories" value={meta.n_categories} />
          <Metric label="backend" value={meta.embedding_backend} />
        </div>
      </div>
    </header>
  );
}

function Metric({ label, value }) {
  return (
    <div>
      <div className="text-ink-400 uppercase tracking-wide-cap text-[9px]">
        {label}
      </div>
      <div className="text-ink-900 text-sm mt-0.5">{value}</div>
    </div>
  );
}
