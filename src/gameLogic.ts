import type { ActionCard, Effect, GoalRule, Level, MetabolicState } from "./types";

const metabolicKeys = [
  "ATP",
  "Glucose",
  "Glycogen",
  "Fat",
  "AminoAcidPool",
  "NADH",
  "NADPH",
  "ROS",
  "NH3",
  "CellHealth",
] as const;

export const clamp = (value: number) => Math.max(0, Math.min(100, Math.round(value)));

export function applyLevelModifier(card: ActionCard, level: Level): Effect {
  const effect: Effect = { ...card.effect };
  const modifier = level.modifier;

  if (!modifier || modifier.cardId !== card.id) {
    return effect;
  }

  for (const [metric, multiplier] of Object.entries(modifier.effectMultiplier ?? {})) {
    const key = metric as keyof Effect;
    if (typeof effect[key] === "number" && typeof multiplier === "number") {
      effect[key] = Math.round(effect[key]! * multiplier);
    }
  }

  return effect;
}

export function applyEffects(state: MetabolicState, effects: Effect[]): MetabolicState {
  const next = { ...state };

  effects.forEach((effect) => {
    Object.entries(effect).forEach(([metric, delta]) => {
      const key = metric as keyof MetabolicState;
      next[key] = clamp(next[key] + (delta ?? 0));
    });
  });

  return applyHomeostaticPressure(next);
}

export function applyHomeostaticPressure(state: MetabolicState): MetabolicState {
  const next = { ...state };

  if (next.ROS > 65) next.CellHealth -= Math.ceil((next.ROS - 65) / 8);
  if (next.NH3 > 55) next.CellHealth -= Math.ceil((next.NH3 - 55) / 9);
  if (next.ATP < 25) next.CellHealth -= 4;
  if (next.Glucose < 18) next.CellHealth -= 3;
  if (next.Glucose > 82) next.CellHealth -= 2;
  if (next.NADH > 85) next.ROS += 4;
  if (next.NADPH < 15 && next.ROS > 45) next.CellHealth -= 2;

  metabolicKeys.forEach((key) => {
    next[key] = clamp(next[key]);
  });

  return next;
}

export function isGoalMet(state: MetabolicState, goal: GoalRule) {
  return goal.operator === ">=" ? state[goal.metric] >= goal.value : state[goal.metric] <= goal.value;
}

export function evaluateLevel(state: MetabolicState, level: Level) {
  const goalResults = level.goals.map((goal) => ({
    ...goal,
    achieved: isGoalMet(state, goal),
    actual: state[goal.metric],
  }));

  const scoreItems = [
    state.ATP >= 50,
    state.Glucose >= 35 && state.Glucose <= 70,
    state.ROS <= 55,
    state.NH3 <= 50,
    state.CellHealth >= 70,
  ];
  const score = scoreItems.reduce((sum, ok) => sum + (ok ? 20 : 0), 0);
  const passed = goalResults.every((goal) => goal.achieved);

  let maxim = "稳态来自调度，而不是单一路径的极限输出。";
  if (state.ROS > 65) maxim = "高能通量必须配套还原力，否则效率会转化为损伤。";
  if (state.NH3 > 60) maxim = "碳骨架可以被利用，氮毒性必须被付费清除。";
  if (state.Glucose < 30) maxim = "缺糖时要逆势而行，但糖异生不能脱离能量账本。";
  if (state.ATP < 40) maxim = "能量不足时，优先抓住最短的供能路径。";
  if (passed && score >= 80) maxim = "能量、物质、还原力和毒性被纳入同一张动态账本。";

  return { score, passed, goalResults, maxim };
}

export function formatEffect(effect: Effect) {
  return Object.entries(effect)
    .map(([metric, delta]) => `${metric} ${delta! > 0 ? "+" : ""}${delta}`)
    .join("  ");
}
