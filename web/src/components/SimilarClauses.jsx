export default function SimilarClauses({ neighbours }) {
  return (
    <section>
      <div className="flex items-baseline gap-4 mb-5">
        <div className="eyebrow">Closest Neighbours</div>
        <div className="text-xs text-ink-500">
          the five most similar same-category clauses in the corpus
        </div>
      </div>

      <ol className="space-y-1">
        {neighbours.map((n, i) => (
          <li key={n.clause_id}>
            <div className="grid grid-cols-[32px_60px_1fr] gap-4 py-3 border-t border-ink-900/10">
              <div className="font-display text-lg text-ink-500 leading-none mt-1">
                {String(i + 1).padStart(2, "0")}
              </div>
              <div>
                <div className="eyebrow mb-0.5">sim</div>
                <div className="font-mono text-sm text-ink-900">
                  {n.similarity.toFixed(3)}
                </div>
              </div>
              <div className="min-w-0">
                <div className="text-ink-900 text-[14px] leading-[1.55]">
                  {n.text}
                </div>
                <div className="font-mono text-[10px] text-ink-400 mt-1.5 truncate">
                  {n.contract_name.replace(/\.pdf$/i, "")}
                </div>
              </div>
            </div>
          </li>
        ))}
      </ol>
    </section>
  );
}
