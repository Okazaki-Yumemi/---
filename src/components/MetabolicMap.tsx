const nodes = [
  { id: "Glucose", x: 8, y: 32 },
  { id: "G-6-P", x: 20, y: 32 },
  { id: "Glycolysis", x: 34, y: 32 },
  { id: "Pyruvate", x: 48, y: 32 },
  { id: "Acetyl-CoA", x: 60, y: 32 },
  { id: "TCA", x: 72, y: 32 },
  { id: "NADH/FADH2", x: 84, y: 32 },
  { id: "ETC", x: 84, y: 57 },
  { id: "ATP", x: 72, y: 57 },
  { id: "PPP", x: 20, y: 58 },
  { id: "NADPH", x: 34, y: 58 },
  { id: "Antioxidant", x: 48, y: 58 },
  { id: "ROS", x: 60, y: 58 },
  { id: "Glycogen", x: 8, y: 58 },
  { id: "Fat", x: 48, y: 12 },
  { id: "Beta-oxidation", x: 60, y: 12 },
  { id: "Amino Acids", x: 8, y: 82 },
  { id: "NH3", x: 24, y: 82 },
  { id: "Urea Cycle", x: 40, y: 82 },
  { id: "Carbon Skeleton", x: 58, y: 82 },
  { id: "Gluconeogenesis", x: 76, y: 82 },
];

const edges = [
  ["Glucose", "G-6-P"],
  ["G-6-P", "Glycolysis"],
  ["Glycolysis", "Pyruvate"],
  ["Pyruvate", "Acetyl-CoA"],
  ["Acetyl-CoA", "TCA"],
  ["TCA", "NADH/FADH2"],
  ["NADH/FADH2", "ETC"],
  ["ETC", "ATP"],
  ["G-6-P", "PPP"],
  ["PPP", "NADPH"],
  ["NADPH", "Antioxidant"],
  ["Antioxidant", "ROS"],
  ["Glycogen", "Glucose"],
  ["Fat", "Beta-oxidation"],
  ["Beta-oxidation", "Acetyl-CoA"],
  ["Amino Acids", "NH3"],
  ["NH3", "Urea Cycle"],
  ["Amino Acids", "Carbon Skeleton"],
  ["Carbon Skeleton", "TCA"],
  ["Carbon Skeleton", "Gluconeogenesis"],
  ["Gluconeogenesis", "Glucose"],
];

function getNode(id: string) {
  const node = nodes.find((item) => item.id === id);
  if (!node) throw new Error(`Unknown node: ${id}`);
  return node;
}

export function MetabolicMap({ activeNodes }: { activeNodes: string[] }) {
  return (
    <section className="rounded-lg border border-white/10 bg-slate-950/60 p-4 shadow-glow">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-sm font-semibold uppercase tracking-[0.2em] text-cyan-100">Metabolic Network</h2>
        <span className="text-xs text-slate-400">pathway activity map</span>
      </div>
      <div className="relative aspect-[16/10] overflow-hidden rounded-lg border border-white/10 bg-[radial-gradient(circle_at_20%_20%,rgba(56,189,248,0.16),transparent_28%),radial-gradient(circle_at_80%_30%,rgba(139,92,246,0.16),transparent_30%),linear-gradient(135deg,rgba(15,23,42,0.96),rgba(2,6,23,0.96))]">
        <svg viewBox="0 0 100 100" className="absolute inset-0 h-full w-full">
          <defs>
            <marker id="arrow" markerHeight="6" markerWidth="6" orient="auto" refX="5" refY="3">
              <path d="M0,0 L6,3 L0,6 Z" fill="rgba(125, 211, 252, 0.55)" />
            </marker>
          </defs>
          {edges.map(([from, to]) => {
            const a = getNode(from);
            const b = getNode(to);
            const active = activeNodes.includes(from) && activeNodes.includes(to);
            return (
              <line
                key={`${from}-${to}`}
                x1={a.x}
                y1={a.y}
                x2={b.x}
                y2={b.y}
                stroke={active ? "rgba(34,211,238,0.95)" : "rgba(148,163,184,0.28)"}
                strokeWidth={active ? 0.7 : 0.35}
                markerEnd="url(#arrow)"
              />
            );
          })}
        </svg>
        {nodes.map((node) => {
          const active = activeNodes.includes(node.id);
          return (
            <div
              key={node.id}
              className={`absolute -translate-x-1/2 -translate-y-1/2 rounded border px-2 py-1 text-center text-[10px] font-medium transition-all sm:text-xs ${
                active
                  ? "border-cyan-200 bg-cyan-300/20 text-cyan-50 shadow-glow"
                  : "border-slate-500/30 bg-slate-950/80 text-slate-300"
              }`}
              style={{ left: `${node.x}%`, top: `${node.y}%` }}
            >
              {node.id}
            </div>
          );
        })}
      </div>
    </section>
  );
}
