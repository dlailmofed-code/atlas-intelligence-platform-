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

export interface UserNotificationPreferences {
  email: boolean;
  push: boolean;
  in_app: boolean;
  opportunity_alerts: boolean;
  market_updates: boolean;
  weekly_digest: boolean;
  security_alerts: boolean;
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

export interface ForgotPasswordRequest {
  email: string;
}

export interface ResetPasswordRequest {
  token: string;
  password: string;
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

export interface SignalEvidence {
  id: string;
  source: string;
  type: string;
  content: string;
  timestamp: string;
  relevance: number;
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
  evidence: SignalEvidence[];
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

export interface UsageRecord {
  id: string;
  user_id: string;
  feature: string;
  count: number;
  limit: number;
  period: string;
  reset_at: string;
}

export interface Invoice {
  id: string;
  subscription_id: string;
  amount: number;
  currency: string;
  status: 'paid' | 'pending' | 'failed' | 'refunded';
  paid_at?: string;
  created_at: string;
}

export interface PaymentMethod {
  id: string;
  type: 'card' | 'bank_account';
  last4: string;
  brand?: string;
  expiry_month?: number;
  expiry_year?: number;
  is_default: boolean;
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

export interface NotificationListResponse {
  items: Notification[];
  total: number;
  page: number;
  page_size: number;
  unread_count: number;
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

export interface KnowledgeEntity {
  id: string;
  name: string;
  type: string;
  description: string;
  properties: Record<string, unknown>;
  connections: number;
}

export interface KnowledgeRelation {
  id: string;
  source_id: string;
  target_id: string;
  type: string;
  weight: number;
}

export interface KnowledgeGraph {
  entities: KnowledgeEntity[];
  relations: KnowledgeRelation[];
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

// Report types
export interface Report {
  id: string;
  title: string;
  description: string;
  type: string;
  status: 'draft' | 'generating' | 'completed' | 'failed';
  content?: Record<string, unknown>;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface ReportListResponse {
  items: Report[];
  total: number;
  page: number;
  page_size: number;
}

export interface ReportTemplate {
  id: string;
  name: string;
  description: string;
  type: string;
  default_config: Record<string, unknown>;
}

export interface ReportSchedule {
  id: string;
  report_id: string;
  cron_expression: string;
  enabled: boolean;
  last_run?: string;
  next_run?: string;
}

// AI Provider types
export interface AIProvider {
  id: string;
  name: string;
  type: string;
  status: 'active' | 'inactive' | 'error';
  health: number;
  latency_ms: number;
  cost_today: number;
  cost_monthly: number;
  requests_today: number;
  requests_monthly: number;
  tokens_used_today: number;
  tokens_used_monthly: number;
  error_rate: number;
  failover_enabled: boolean;
}

export interface AIProviderMetrics {
  provider_id: string;
  requests: number;
  tokens: number;
  cost: number;
  latency_avg: number;
  latency_p50: number;
  latency_p95: number;
  latency_p99: number;
  errors: number;
  timestamp: string;
}

// Connector types
export interface Connector {
  id: string;
  name: string;
  type: string;
  provider: string;
  status: 'active' | 'inactive' | 'error' | 'syncing';
  health: number;
  last_sync?: string;
  items_synced: number;
  errors_today: number;
  config: Record<string, unknown>;
}

export interface ConnectorLog {
  id: string;
  connector_id: string;
  level: 'info' | 'warning' | 'error';
  message: string;
  created_at: string;
}

// Admin types
export interface Organization {
  id: string;
  name: string;
  slug: string;
  plan_id: string;
  plan_name: string;
  member_count: number;
  seat_count: number;
  created_at: string;
  is_active: boolean;
}

export interface Role {
  id: string;
  name: string;
  description: string;
  permissions: string[];
  is_system: boolean;
}

export interface Permission {
  id: string;
  name: string;
  resource: string;
  action: string;
}

export interface AuditLog {
  id: string;
  user_id: string;
  user_email: string;
  action: string;
  resource: string;
  resource_id?: string;
  ip_address: string;
  user_agent: string;
  details?: Record<string, unknown>;
  created_at: string;
}

export interface FeatureFlag {
  id: string;
  key: string;
  name: string;
  description: string;
  enabled: boolean;
  targeting: {
    percentage?: number;
    user_ids?: string[];
    roles?: string[];
  };
  created_at: string;
  updated_at: string;
}

export interface APIKey {
  id: string;
  name: string;
  key_prefix: string;
  permissions: string[];
  last_used?: string;
  expires_at?: string;
  created_at: string;
  is_active: boolean;
}

export interface SystemHealth {
  status: 'healthy' | 'degraded' | 'unhealthy';
  components: {
    name: string;
    status: 'up' | 'down' | 'degraded';
    latency_ms?: number;
    error_rate?: number;
  }[];
  timestamp: string;
}

export interface UsageAnalytics {
  period: string;
  total_requests: number;
  total_signals: number;
  total_opportunities: number;
  total_reports: number;
  storage_used_bytes: number;
  api_calls_by_endpoint: Record<string, number>;
  top_users: { user_id: string; email: string; requests: number }[];
}
