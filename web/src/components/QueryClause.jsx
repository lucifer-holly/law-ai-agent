export default function QueryClause({ query }) {
  // Contract filename in CUAD is long — show just the cleaner core
  const contractShort =
    query.contract_name
      .replace(/\.pdf$/i, "")
      .split("_")
      .slice(-2)
      .join(" · ") || query.contract_name;

  return (
    <article className="relative">
      <div className="flex flex-wrap items-baseline gap-x-4 gap-y-1 mb-4">
        <div className="eyebrow">Query Clause</div>
        <div className="font-mono text-[11px] text-ink-500">
          {query.clause_type}
        </div>
        <div className="font-mono text-[11px] text-ink-400 truncate">
          {contractShort}
        </div>
      </div>

      <blockquote className="relative pl-6 border-l-2 border-cognac-500/60">
        <p className="font-display text-[20px] sm:text-[22px] leading-[1.45] text-ink-900">
          {query.text}
        </p>
      </blockquote>

      <div className="mt-3 font-mono text-[10px] text-ink-400 tracking-wide-cap uppercase">
        <span className="text-ink-500">Clause&nbsp;ID&nbsp;</span>
        {query.clause_id}
      </div>
    </article>
  );
}
