import type { Level, MetabolicState } from "../types";
import { isGoalMet } from "../gameLogic";

export function LevelPanel({
  level,
  turn,
  state,
  onReset,
  onLevelChange,
  levelIndex,
  totalLevels,
}: {
  level: Level;
  turn: number;
  state: MetabolicState;
  onReset: () => void;
  onLevelChange: (direction: -1 | 1) => void;
  levelIndex: number;
  totalLevels: number;
}) {
  return (
    <section className="rounded-lg border border-white/10 bg-slate-950/70 p-4">
      <div className="mb-3 flex flex-wrap items-start justify-between gap-3">
        <div>
          <div className="text-xs uppercase tracking-[0.25em] text-cyan-200">Scenario {levelIndex + 1}/{totalLevels}</div>
          <h2 className="mt-1 text-2xl font-semibold text-slate-50">{level.name}</h2>
        </div>
        <div className="rounded border border-violet-300/20 bg-violet-300/10 px-3 py-2 text-sm text-violet-100">
          回合 {turn}/{level.turnLimit}
        </div>
      </div>
      <p className="mb-4 text-sm leading-6 text-slate-300">{level.context}</p>
      {level.modifier && <p className="mb-4 rounded border border-amber-300/20 bg-amber-300/10 p-3 text-sm text-amber-100">{level.modifier.note}</p>}
      <div className="mb-4 grid gap-2 sm:grid-cols-2">
        {level.goals.map((goal) => {
          const met = isGoalMet(state, goal);
          return (
            <div
              key={goal.label}
              className={`rounded border px-3 py-2 text-sm ${
                met ? "border-emerald-300/30 bg-emerald-300/10 text-emerald-100" : "border-slate-500/30 bg-slate-900/70 text-slate-300"
              }`}
            >
              {met ? "已满足" : "目标"} · {goal.label}
            </div>
          );
        })}
      </div>
      <p className="mb-4 text-sm text-slate-400">推荐策略：{level.recommendedStrategy}</p>
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => onLevelChange(-1)}
          disabled={levelIndex === 0}
          className="rounded border border-white/10 px-3 py-2 text-sm text-slate-200 disabled:cursor-not-allowed disabled:opacity-40"
        >
          上一关
        </button>
        <button
          onClick={() => onLevelChange(1)}
          disabled={levelIndex === totalLevels - 1}
          className="rounded border border-white/10 px-3 py-2 text-sm text-slate-200 disabled:cursor-not-allowed disabled:opacity-40"
        >
          下一关
        </button>
        <button onClick={onReset} className="rounded border border-cyan-300/30 bg-cyan-300/10 px-3 py-2 text-sm text-cyan-100">
          重置本关
        </button>
      </div>
    </section>
  );
}
