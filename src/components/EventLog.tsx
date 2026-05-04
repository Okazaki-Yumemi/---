import type { LogEntry } from "../types";

export function EventLog({ entries }: { entries: LogEntry[] }) {
  return (
    <section className="rounded-lg border border-white/10 bg-slate-950/70 p-4">
      <h2 className="mb-3 text-sm font-semibold uppercase tracking-[0.2em] text-violet-100">Event Log</h2>
      <div className="max-h-64 space-y-2 overflow-y-auto pr-1">
        {entries.map((entry, index) => (
          <div key={`${entry.turn}-${index}`} className="rounded border border-white/10 bg-white/[0.03] p-3 text-sm text-slate-300">
            <span className="mr-2 font-mono text-cyan-200">T{entry.turn}</span>
            {entry.text}
          </div>
        ))}
      </div>
    </section>
  );
}
