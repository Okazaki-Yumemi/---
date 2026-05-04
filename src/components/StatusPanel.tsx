import type { MetabolicState, Metabolite } from "../types";

const labels: Record<Metabolite, string> = {
  ATP: "ATP",
  Glucose: "Glucose",
  Glycogen: "Glycogen",
  Fat: "Fat",
  AminoAcidPool: "Amino Acids",
  NADH: "NADH",
  NADPH: "NADPH",
  ROS: "ROS",
  NH3: "NH3",
  CellHealth: "Cell Health",
};

const order = Object.keys(labels) as Metabolite[];

function tone(metric: Metabolite, value: number) {
  if (metric === "ROS" || metric === "NH3") {
    if (value >= 70) return "from-rose-500 to-orange-400";
    if (value >= 45) return "from-amber-400 to-yellow-300";
    return "from-cyan-400 to-emerald-300";
  }
  if (metric === "CellHealth") {
    if (value < 40) return "from-rose-500 to-red-400";
    if (value < 70) return "from-amber-400 to-yellow-300";
  }
  return "from-sky-400 to-violet-400";
}

export function StatusPanel({ state }: { state: MetabolicState }) {
  return (
    <section className="rounded-lg border border-white/10 bg-slate-950/70 p-4 shadow-glow backdrop-blur">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-sm font-semibold uppercase tracking-[0.2em] text-cyan-100">Cell Telemetry</h2>
        <span className="text-xs text-slate-400">0-100</span>
      </div>
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-1">
        {order.map((metric) => (
          <div key={metric}>
            <div className="mb-1 flex items-center justify-between text-xs">
              <span className="text-slate-300">{labels[metric]}</span>
              <span className="font-mono text-cyan-100">{state[metric]}</span>
            </div>
            <div className="h-2 overflow-hidden rounded-full bg-slate-800">
              <div
                className={`h-full rounded-full bg-gradient-to-r ${tone(metric, state[metric])} transition-all duration-500`}
                style={{ width: `${state[metric]}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
