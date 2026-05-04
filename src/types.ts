export type Metabolite =
  | "ATP"
  | "Glucose"
  | "Glycogen"
  | "Fat"
  | "AminoAcidPool"
  | "NADH"
  | "NADPH"
  | "ROS"
  | "NH3"
  | "CellHealth";

export type MetabolicState = Record<Metabolite, number>;

export type Effect = Partial<Record<Metabolite, number>>;

export type CardId =
  | "glycolysis"
  | "tca"
  | "etc"
  | "ppp"
  | "antioxidant"
  | "glycogenolysis"
  | "glycogenesis"
  | "lipolysis"
  | "betaOxidation"
  | "gluconeogenesis"
  | "ureaCycle"
  | "proteolysis";

export interface ActionCard {
  id: CardId;
  title: string;
  pathway: string;
  effect: Effect;
  explanation: string;
  tags: string[];
  nodes: string[];
}

export interface GoalRule {
  metric: Metabolite;
  operator: ">=" | "<=";
  value: number;
  label: string;
}

export interface Level {
  id: string;
  name: string;
  context: string;
  turnLimit: number;
  initialState: MetabolicState;
  goals: GoalRule[];
  recommendedStrategy: string;
  modifier?: {
    cardId: CardId;
    effectMultiplier?: Partial<Record<Metabolite, number>>;
    note: string;
  };
}

export interface LogEntry {
  turn: number;
  text: string;
}
