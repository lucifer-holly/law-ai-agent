export default function MethodFootnote({ meta }) {
  return (
    <footer className="pt-10 border-t border-ink-900/10">
      <div className="grid grid-cols-1 md:grid-cols-[1fr_1fr] gap-10">
        <div>
          <div className="eyebrow mb-3">Method</div>
          <p className="text-sm text-ink-700 leading-relaxed">
            Each clause is embedded into a{" "}
            <span className="font-mono text-[12px] text-ink-900">
              {meta.embedding_dim}-d
            </span>{" "}
            unit vector. For a query clause, we compute cosine similarity
            against every other clause of the same category and derive two
            statistics — a <em>density</em> (fraction of the top-
            {meta.k} neighbours above similarity {meta.sim_threshold}) and a{" "}
            <em>nearest</em> (top-1 similarity). These blend into a single
            Index Score in [0, 1], mapped onto a five-level spectrum.
          </p>
        </div>

        <div>
          <div className="eyebrow mb-3">Notes</div>
          <ul className="text-sm text-ink-700 leading-relaxed space-y-2 list-none">
            <li>
              <span className="font-mono text-[11px] text-cognac-600 mr-2">
                01
              </span>
              The demo ships with{" "}
              <span className="font-mono text-[12px]">
                {meta.embedding_backend}
              </span>{" "}
              embeddings for portability. A production-grade{" "}
              <span className="font-mono text-[12px]">bge-m3</span>{" "}
              pipeline is included in{" "}
              <span className="font-mono text-[12px]">scripts/</span>.
            </li>
            <li>
              <span className="font-mono text-[11px] text-cognac-600 mr-2">
                02
              </span>
              There is no language model on the critical path. The score is
              pure geometry + statistics — inspired by Law Insider's Index
              Score design philosophy.
            </li>
            <li>
              <span className="font-mono text-[11px] text-cognac-600 mr-2">
                03
              </span>
              Source corpus: CUAD v1 (CC-BY 4.0), 510 EDGAR commercial
              contracts labelled by The Atticus Project.
            </li>
          </ul>
        </div>
      </div>

      <div className="mt-12 text-[11px] text-ink-500 font-mono flex flex-wrap gap-x-6 gap-y-2">
        <span>Clause Index · v0.1.0</span>
        <span>No LLM on the critical path</span>
        <a
          href="https://github.com/lucifer-holly/legal-clause-index"
          className="underline decoration-cognac-500/50 hover:text-cognac-600"
        >
          github.com/lucifer-holly/legal-clause-index
        </a>
      </div>
    </footer>
  );
}
