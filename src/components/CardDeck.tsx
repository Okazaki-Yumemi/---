import type { ActionCard, CardId, Effect, Level } from "../types";
import { applyLevelModifier, formatEffect } from "../gameLogic";

interface CardDeckProps {
  cards: ActionCard[];
  selected: CardId[];
  level: Level;
  onToggle: (id: CardId) => void;
}

function effectLines(effect: Effect) {
  return Object.entries(effect).map(([metric, delta]) => (
    <span
      key={metric}
      className={`rounded border px-2 py-1 font-mono text-[11px] ${
        delta! > 0
          ? "border-cyan-300/20 bg-cyan-300/10 text-cyan-100"
          : "border-rose-300/20 bg-rose-300/10 text-rose-100"
      }`}
    >
      {metric} {delta! > 0 ? "+" : ""}
      {delta}
    </span>
  ));
}

export function CardDeck({ cards, selected, level, onToggle }: CardDeckProps) {
  return (
    <section className="rounded-lg border border-white/10 bg-slate-950/60 p-4 shadow-violet">
      <div className="mb-3 flex items-center justify-between gap-3">
        <h2 className="text-sm font-semibold uppercase tracking-[0.2em] text-violet-100">Action Cards</h2>
        <span className="rounded border border-cyan-300/20 bg-cyan-300/10 px-3 py-1 text-xs text-cyan-100">
          已选择 {selected.length}/2
        </span>
      </div>
      <div className="grid gap-3 md:grid-cols-2 2xl:grid-cols-3">
        {cards.map((card) => {
          const isSelected = selected.includes(card.id);
          const effect = applyLevelModifier(card, level);
          const changed = formatEffect(effect) !== formatEffect(card.effect);

          return (
            <button
              key={card.id}
              onClick={() => onToggle(card.id)}
              className={`group min-h-52 rounded-lg border p-4 text-left transition ${
                isSelected
                  ? "border-cyan-300/70 bg-cyan-300/10 shadow-glow"
                  : "border-white/10 bg-slate-900/70 hover:border-violet-300/50 hover:bg-slate-900"
              }`}
            >
              <div className="mb-2 flex items-start justify-between gap-3">
                <div>
                  <div className="text-base font-semibold text-slate-50">{card.title}</div>
                  <div className="text-xs uppercase tracking-[0.18em] text-violet-200">{card.pathway}</div>
                </div>
                <div className="h-3 w-3 shrink-0 rounded-full border border-cyan-200/70 bg-cyan-300/20" />
              </div>
              <div className="mb-3 flex flex-wrap gap-2">{effectLines(effect)}</div>
              {changed && <p className="mb-2 text-xs text-amber-200">{level.modifier?.note}</p>}
              <p className="text-sm leading-6 text-slate-300">{card.explanation}</p>
              <div className="mt-3 flex flex-wrap gap-2">
                {card.tags.map((tag) => (
                  <span key={tag} className="rounded border border-white/10 bg-white/5 px-2 py-1 text-[11px] text-slate-300">
                    {tag}
                  </span>
                ))}
              </div>
            </button>
          );
        })}
      </div>
    </section>
  );
}
