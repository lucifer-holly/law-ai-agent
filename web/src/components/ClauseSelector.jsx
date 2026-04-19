import { levelCells } from "../lib/levels.js";

export default function ClauseSelector({ queries, categories, selectedId, onSelect }) {
  const byCategory = categories.map((cat) => ({
    cat,
    items: queries.filter((q) => q.clause_type === cat),
  }));

  return (
    <div>
      <div className="eyebrow mb-3">Demo Queries</div>
      <nav className="space-y-6 max-h-[calc(100vh-12rem)] overflow-y-auto pr-2">
        {byCategory.map(({ cat, items }) => (
          <div key={cat}>
            <div className="font-mono text-[10px] uppercase tracking-wide-cap text-ink-500 mb-2 pb-1 border-b border-ink-900/10">
              {cat}
            </div>
            <ul className="space-y-1">
              {items.map((q) => (
                <li key={q.clause_id}>
                  <button
                    onClick={() => onSelect(q.clause_id)}
                    className={`group w-full text-left px-2 py-2 rounded transition-colors
                                ${
                                  selectedId === q.clause_id
                                    ? "bg-cognac-50 ring-1 ring-cognac-400/40"
                                    : "hover:bg-parchment-200/60"
                                }`}
                  >
                    <div className="flex items-center gap-1.5 mb-1">
                      {levelCells(q.index_score.level).map((on, i) => (
                        <span
                          key={i}
                          className={`h-1 w-3 rounded-sm ${
                            on ? cellColor(q.index_score.level) : "bg-ink-900/10"
                          }`}
                        />
                      ))}
                      <span className="ml-1 font-mono text-[10px] text-ink-500">
                        {q.index_score.score.toFixed(2)}
                      </span>
                    </div>
                    <div className="text-[12.5px] leading-snug text-ink-800 line-clamp-2">
                      {q.text.slice(0, 100)}…
                    </div>
                  </button>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </nav>
    </div>
  );
}

function cellColor(level) {
  switch (level) {
    case "Highly Atypical": return "bg-level-highly-atypical";
    case "Atypical":        return "bg-level-atypical";
    case "Mixed":           return "bg-level-mixed";
    case "Standard":        return "bg-level-standard";
    case "Highly Standard": return "bg-level-highly-standard";
    default:                return "bg-ink-500";
  }
}
