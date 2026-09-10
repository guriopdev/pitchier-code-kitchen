export type SlideType =
  | "problem"
  | "solution"
  | "market"
  | "product"
  | "traction"
  | "business_model"
  | "gtm"
  | "competition"
  | "team"
  | "ask";

export interface MetricCallout {
  label: string;
  value: string;
  context?: string;
}

export interface InvestorCritique {
  strengths: string[];
  red_flags: string[];
  hard_questions: string[];
}

export interface ChartDataPoint {
  label: string;
  value: number;
  percentage?: number;
  color?: string;
}

export interface SlideChart {
  chart_type: "pie" | "bar";
  title: string;
  data: ChartDataPoint[];
}

export interface SlideAnalysis {
  strategic_takeaway: string;
  unit_economics_verdict?: string;
  moat_rating: "High" | "Medium" | "Developing";
}

export interface Slide {
  slide_number: number;
  slide_type: SlideType;
  headline: string;
  subtitle?: string;
  key_points: string[];
  metrics: MetricCallout[];
  visual_layout_hint?: string;
  speaker_notes?: string;
  investor_critique: InvestorCritique;
  chart?: SlideChart;
  analysis?: SlideAnalysis;
}

export interface PitchDeck {
  company_name: string;
  one_liner: string;
  target_round: string;
  target_amount: string;
  slides: Slide[];
  overall_investment_thesis?: string;
  overall_red_flags: string[];
}

export interface DeckGenerationRequest {
  company_name: string;
  one_liner?: string;
  target_round: string;
  target_amount?: string;
  raw_notes: string;
  competitor_urls: string[];
  industry_sector?: string;
}
