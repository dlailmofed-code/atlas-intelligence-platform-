// User types
export interface User {
  id: string;
  email: string;
  full_name: string;
  company?: string;
  bio?: string;
  avatar_url?: string;
  timezone: string;
  language: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserPreferences {
  email_notifications: boolean;
  push_notifications: boolean;
  weekly_digest: boolean;
  opportunity_alerts: boolean;
  market_updates: boolean;
  dark_mode: boolean;
  language: string;
}

// Auth types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
  company?: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token?: string;
  token_type: string;
  expires_in: number;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

// Opportunity types
export interface OpportunityScore {
  overall: number;
  demand: number;
  growth: number;
  competition: number;
  risk: number;
  confidence: number;
}

export interface EvidenceSource {
  source: string;
  type: string;
  date: string;
  relevance: number;
  summary: string;
}

export interface Opportunity {
  id: string;
  title: string;
  description: string;
  category: string;
  industry: string;
  region?: string;
  country?: string;
  city?: string;
  project_id?: string;
  score?: OpportunityScore;
  evidence: EvidenceSource[];
  signals: string[];
  insights: string[];
  key_players: string[];
  estimated_market_size?: string;
  growth_rate?: string;
  is_bookmarked: boolean;
  is_analyzed: boolean;
  created_at: string;
  updated_at: string;
}

export interface OpportunityListResponse {
  items: Opportunity[];
  total: number;
  page: number;
  page_size: number;
  has_next: boolean;
}

// Signal types
export interface SignalSource {
  source_id: string;
  source_name: string;
  source_type: string;
  reliability: number;
  last_updated: string;
}

export interface IntelligenceSignal {
  id: string;
  type: string;
  name: string;
  description: string;
  category: string;
  intensity: number;
  trend: 'up' | 'down' | 'stable' | 'volatile';
  confidence: number;
  region?: string;
  industry?: string;
  sources: SignalSource[];
  entities: string[];
  detected_at: string;
  updated_at: string;
}

// Project types
export interface Project {
  id: string;
  name: string;
  description?: string;
  user_id: string;
  organization_id?: string;
  is_public: boolean;
  opportunity_count: number;
  created_at: string;
  updated_at: string;
}

export interface ProjectListResponse {
  items: Project[];
  total: number;
  page: number;
  page_size: number;
  has_next: boolean;
}

// Health types
export interface HealthResponse {
  status: string;
  version: string;
  environment: string;
  timestamp: string;
  dependencies: Record<string, string>;
}

// API Response types
export interface ApiError {
  detail: string;
  code?: string;
  errors?: Array<{ field: string; message: string }>;
}

export interface PaginatedParams {
  page?: number;
  page_size?: number;
}

// Filter types
export interface OpportunityFilters {
  category?: string;
  industry?: string;
  region?: string;
  min_score?: number;
  max_score?: number;
  is_bookmarked?: boolean;
}

export interface SignalFilters {
  type?: string;
  category?: string;
  region?: string;
  industry?: string;
  min_intensity?: number;
  min_confidence?: number;
}

// Subscription types
export interface SubscriptionPlan {
  id: string;
  name: string;
  description: string;
  price_monthly: number;
  price_yearly: number;
  features: string[];
  limits: Record<string, number>;
  is_active: boolean;
}

export interface Subscription {
  id: string;
  user_id: string;
  plan_id: string;
  plan_name: string;
  status: 'active' | 'cancelled' | 'expired' | 'past_due' | 'trialing';
  billing_cycle: 'monthly' | 'yearly';
  started_at: string;
  current_period_start: string;
  current_period_end: string;
  cancelled_at?: string;
}

// Notification types
export interface Notification {
  id: string;
  title: string;
  message: string;
  type: string;
  priority: 'low' | 'normal' | 'high';
  is_read: boolean;
  read_at?: string;
  action_url?: string;
  created_at: string;
}

// Intelligence types
export interface Pattern {
  id: string;
  name: string;
  description: string;
  type: 'convergence' | 'divergence' | 'trend' | 'anomaly';
  confidence: number;
  signals: string[];
  detected_at: string;
}

export interface CausalLink {
  id: string;
  cause_entity: string;
  effect_entity: string;
  relationship_type: string;
  confidence: number;
  evidence_summary: string;
}

export interface IntelligenceIndicator {
  id: string;
  name: string;
  type: string;
  value: number;
  trend: 'up' | 'down' | 'stable';
  geography?: string;
  industry?: string;
  timestamp: string;
}

export interface IntelligenceDashboard {
  total_signals: number;
  active_signals: number;
  high_confidence_signals: number;
  patterns_detected: number;
  causal_links: number;
  top_indicators: IntelligenceIndicator[];
  recent_signals: IntelligenceSignal[];
}
