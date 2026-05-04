import { useMemo, useState } from "react";
import { Activity, Gauge, Play, RotateCcw } from "lucide-react";
import { actionCards } from "./data/cards";
import { levels } from "./data/levels";
import { applyEffects, applyLevelModifier, evaluateLevel, formatEffect } from "./gameLogic";
import { CardDeck } from "./components/CardDeck";
import { EventLog } from "./components/EventLog";
import { LevelPanel } from "./components/LevelPanel";
import { MetabolicMap } from "./components/MetabolicMap";
import { ResultModal } from "./components/ResultModal";
import { StatusPanel } from "./components/StatusPanel";
import type { CardId, LogEntry, MetabolicState } from "./types";

function initialLogs(levelName: string): LogEntry[] {
  return [{ turn: 0, text: `进入「${levelName}」情境。选择 2 张行动卡，调度代谢通量。` }];
}

export default function App() {
  const [levelIndex, setLevelIndex] = useState(0);
  const level = levels[levelIndex];
  const [state, setState] = useState<MetabolicState>(level.initialState);
  const [turn, setTurn] = useState(0);
  const [selected, setSelected] = useState<CardId[]>([]);
  const [logs, setLogs] = useState<LogEntry[]>(initialLogs(level.name));
  const [activeNodes, setActiveNodes] = useState<string[]>([]);
  const [showResult, setShowResult] = useState(false);

  const selectedCards = useMemo(() => actionCards.filter((card) => selected.includes(card.id)), [selected]);
  const result = evaluateLevel(state, level);

  function resetLevel(index = levelIndex) {
    const nextLevel = levels[index];
    setLevelIndex(index);
    setState(nextLevel.initialState);
    setTurn(0);
    setSelected([]);
    setActiveNodes([]);
    setShowResult(false);
    setLogs(initialLogs(nextLevel.name));
  }

  function toggleCard(id: CardId) {
    setSelected((current) => {
      if (current.includes(id)) return current.filter((item) => item !== id);
      if (current.length >= 2) return current;
      return [...current, id];
    });
  }

  function executeTurn() {
    if (selectedCards.length !== 2 || showResult) return;

    const effects = selectedCards.map((card) => applyLevelModifier(card, level));
    const nextState = applyEffects(state, effects);
    const nextTurn = turn + 1;
    const nodeSet = new Set(selectedCards.flatMap((card) => card.nodes));
    const cardSummary = selectedCards.map((card, index) => `${card.title}（${formatEffect(effects[index])}）`).join("；");

    setState(nextState);
    setTurn(nextTurn);
    setActiveNodes([...nodeSet]);
    setLogs((current) => [
      { turn: nextTurn, text: `执行 ${cardSummary}。` },
      ...current,
    ]);
    setSelected([]);

    if (nextTurn >= level.turnLimit || nextState.CellHealth <= 0) {
      setTimeout(() => setShowResult(true), 450);
    }
  }

  function changeLevel(direction: -1 | 1) {
    const next = Math.max(0, Math.min(levels.length - 1, levelIndex + direction));
    resetLevel(next);
  }

  function nextLevel() {
    if (levelIndex < levels.length - 1) {
      resetLevel(levelIndex + 1);
    } else {
      setShowResult(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <div className="fixed inset-0 -z-10 bg-[radial-gradient(circle_at_18%_12%,rgba(14,165,233,0.22),transparent_26%),radial-gradient(circle_at_80%_0%,rgba(124,58,237,0.18),transparent_30%),linear-gradient(180deg,#020617,#0f172a_52%,#020617)]" />
      <div className="mx-auto flex w-full max-w-[1680px] flex-col gap-5 px-4 py-5 sm:px-6 lg:px-8">
        <header className="rounded-lg border border-white/10 bg-slate-950/70 p-5 shadow-glow backdrop-blur">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <div className="mb-2 flex items-center gap-2 text-xs uppercase tracking-[0.25em] text-cyan-200">
                <Activity className="h-4 w-4" />
                Metabolic City
              </div>
              <h1 className="text-3xl font-semibold text-white sm:text-5xl">代谢之城：Cell City</h1>
              <p className="mt-2 text-sm tracking-wide text-slate-300 sm:text-base">A Strategy Game of Metabolic Homeostasis</p>
            </div>
            <div className="flex flex-wrap gap-3">
              <div className="rounded border border-cyan-300/20 bg-cyan-300/10 px-4 py-3">
                <div className="text-xs uppercase tracking-[0.18em] text-cyan-200">Goal Status</div>
                <div className="mt-1 text-lg font-semibold text-cyan-50">{result.goalResults.filter((goal) => goal.achieved).length}/{level.goals.length}</div>
              </div>
              <div className="rounded border border-violet-300/20 bg-violet-300/10 px-4 py-3">
                <div className="text-xs uppercase tracking-[0.18em] text-violet-200">Score Probe</div>
                <div className="mt-1 flex items-center gap-2 text-lg font-semibold text-violet-50">
                  <Gauge className="h-4 w-4" />
                  {result.score}
                </div>
              </div>
            </div>
          </div>
        </header>

        <div className="grid gap-5 xl:grid-cols-[320px_minmax(0,1fr)_360px]">
          <aside className="space-y-5">
            <StatusPanel state={state} />
            <EventLog entries={logs} />
          </aside>

          <div className="space-y-5">
            <LevelPanel
              level={level}
              turn={turn}
              state={state}
              onReset={() => resetLevel()}
              onLevelChange={changeLevel}
              levelIndex={levelIndex}
              totalLevels={levels.length}
            />
            <MetabolicMap activeNodes={activeNodes} />
            <CardDeck cards={actionCards} selected={selected} level={level} onToggle={toggleCard} />
          </div>

          <aside className="space-y-5">
            <section className="rounded-lg border border-white/10 bg-slate-950/70 p-4 shadow-violet">
              <h2 className="mb-3 text-sm font-semibold uppercase tracking-[0.2em] text-cyan-100">Turn Console</h2>
              <div className="mb-4 space-y-3">
                {selectedCards.length === 0 && <p className="text-sm text-slate-400">请选择 2 张行动卡。</p>}
                {selectedCards.map((card) => (
                  <div key={card.id} className="rounded border border-cyan-300/20 bg-cyan-300/10 p-3">
                    <div className="font-semibold text-cyan-50">{card.title}</div>
                    <div className="mt-1 text-xs text-slate-300">{formatEffect(applyLevelModifier(card, level))}</div>
                  </div>
                ))}
              </div>
              <button
                onClick={executeTurn}
                disabled={selectedCards.length !== 2}
                className="mb-3 flex w-full items-center justify-center gap-2 rounded bg-cyan-300 px-4 py-3 font-semibold text-slate-950 transition hover:bg-cyan-200 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-400"
              >
                <Play className="h-4 w-4" />
                执行本回合
              </button>
              <button
                onClick={() => resetLevel()}
                className="flex w-full items-center justify-center gap-2 rounded border border-white/10 px-4 py-3 text-sm text-slate-200"
              >
                <RotateCcw className="h-4 w-4" />
                重新调度
              </button>
            </section>

            <section className="rounded-lg border border-white/10 bg-slate-950/70 p-4">
              <h2 className="mb-3 text-sm font-semibold uppercase tracking-[0.2em] text-violet-100">Design Lens</h2>
              <div className="space-y-2 text-sm leading-6 text-slate-300">
                <p>每回合不是寻找唯一正确答案，而是在能量收益、底物消耗、还原力储备、ROS 与 NH3 毒性之间权衡。</p>
                <p>状态会被稳态压力修正：ROS、NH3、ATP 过低或 Glucose 极端值都会影响 CellHealth。</p>
              </div>
            </section>
          </aside>
        </div>
      </div>

      {showResult && (
        <ResultModal
          level={level}
          state={state}
          isFinalLevel={levelIndex === levels.length - 1}
          onRetry={() => resetLevel()}
          onNext={nextLevel}
        />
      )}
    </main>
  );
}
