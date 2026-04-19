import { useMemo, useState } from "react";
import precomputed from "./data/precomputed.json";

import Header from "./components/Header.jsx";
import ClauseSelector from "./components/ClauseSelector.jsx";
import QueryClause from "./components/QueryClause.jsx";
import ScoreCard from "./components/ScoreCard.jsx";
import DensityChart from "./components/DensityChart.jsx";
import SimilarClauses from "./components/SimilarClauses.jsx";
import MethodFootnote from "./components/MethodFootnote.jsx";

export default function App() {
  const [selectedId, setSelectedId] = useState(
    precomputed.queries[0]?.clause_id ?? null
  );

  const selected = useMemo(
    () => precomputed.queries.find((q) => q.clause_id === selectedId),
    [selectedId]
  );

  if (!selected) {
    return (
      <div className="min-h-screen grid place-items-center text-ink-500">
        No demo queries loaded.
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <Header meta={precomputed.meta} />

      <main className="mx-auto max-w-[1400px] px-6 lg:px-10 pb-24">
        <div className="grid grid-cols-1 lg:grid-cols-[280px_1fr] gap-x-10 gap-y-8 pt-8">
          <aside className="lg:sticky lg:top-8 lg:self-start">
            <ClauseSelector
              queries={precomputed.queries}
              categories={precomputed.categories}
              selectedId={selectedId}
              onSelect={setSelectedId}
            />
          </aside>

          <section className="min-w-0 space-y-10">
            <QueryClause query={selected} />

            <div className="grid grid-cols-1 xl:grid-cols-[420px_1fr] gap-8">
              <ScoreCard
                score={selected.index_score}
                categoryStats={precomputed.category_stats[selected.clause_type]}
                clauseType={selected.clause_type}
              />
              <DensityChart
                distribution={selected.similarity_distribution}
                nearest={selected.index_score.nearest}
                simThreshold={precomputed.meta.sim_threshold}
              />
            </div>

            <SimilarClauses neighbours={selected.top_neighbours} />

            <MethodFootnote meta={precomputed.meta} />
          </section>
        </div>
      </main>
    </div>
  );
}
