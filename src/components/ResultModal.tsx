import type { Level } from "../types";
import { evaluateLevel } from "../gameLogic";
import type { MetabolicState } from "../types";

export function ResultModal({
  level,
  state,
  isFinalLevel,
  onRetry,
  onNext,
}: {
  level: Level;
  state: MetabolicState;
  isFinalLevel: boolean;
  onRetry: () => void;
  onNext: () => void;
}) {
  const result = evaluateLevel(state, level);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 p-4 backdrop-blur">
      <div className="max-h-[90vh] w-full max-w-3xl overflow-y-auto rounded-lg border border-cyan-300/20 bg-slate-950 p-6 shadow-glow">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <div>
            <div className="text-xs uppercase tracking-[0.25em] text-cyan-200">Level Report</div>
            <h2 className="mt-1 text-3xl font-semibold text-slate-50">{result.passed ? "稳态达成" : "稳态失衡"}</h2>
          </div>
          <div className="rounded border border-violet-300/30 bg-violet-300/10 px-4 py-2 font-mono text-2xl text-violet-100">{result.score}</div>
        </div>
        <div className="mb-5 grid gap-2 sm:grid-cols-2">
          {result.goalResults.map((goal) => (
            <div
              key={goal.label}
              className={`rounded border p-3 text-sm ${
                goal.achieved ? "border-emerald-300/30 bg-emerald-300/10 text-emerald-100" : "border-rose-300/30 bg-rose-300/10 text-rose-100"
              }`}
            >
              {goal.achieved ? "达成" : "未达成"} · {goal.label}，当前 {goal.actual}
            </div>
          ))}
        </div>
        <p className="mb-5 rounded border border-cyan-300/20 bg-cyan-300/10 p-4 text-lg leading-8 text-cyan-50">生化之道：{result.maxim}</p>
        {isFinalLevel && result.passed && (
          <div className="mb-5 rounded-lg border border-violet-300/20 bg-violet-300/10 p-5">
            <p className="mb-4 text-xl leading-9 text-slate-50">
              代谢不是追求单一最大化，而是在能量、物质、还原力、毒性和环境需求之间维持动态平衡。
            </p>
            <div className="grid gap-2 sm:grid-cols-3">
              {["抓住关键", "动态平衡", "响应需求", "藏器于势", "逆势而行", "分合自然"].map((item) => (
                <div key={item} className="rounded border border-white/10 bg-white/5 px-3 py-2 text-center text-cyan-100">
                  {item}
                </div>
              ))}
            </div>
          </div>
        )}
        <div className="flex flex-wrap justify-end gap-3">
          <button onClick={onRetry} className="rounded border border-white/10 px-4 py-2 text-slate-200">
            重试本关
          </button>
          <button onClick={onNext} className="rounded bg-cyan-300 px-4 py-2 font-semibold text-slate-950">
            {isFinalLevel ? "查看最终状态" : "进入下一关"}
          </button>
        </div>
      </div>
    </div>
  );
}
