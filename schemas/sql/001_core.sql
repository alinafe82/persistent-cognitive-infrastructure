CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TYPE data_classification AS ENUM (
  'public',
  'internal',
  'confidential',
  'restricted',
  'regulated'
);

CREATE TYPE confidence_band AS ENUM (
  'unknown',
  'low',
  'medium',
  'high',
  'verified',
  'contradicted'
);

CREATE TYPE claim_state AS ENUM (
  'asserted',
  'confirmed',
  'drifted',
  'contradicted',
  'superseded',
  'expired',
  'retracted'
);

CREATE TYPE workload_state AS ENUM (
  'candidate',
  'rejected_low_value',
  'rejected_policy',
  'deferred_budget',
  'deferred_capacity',
  'admitted',
  'admitted_requires_approval',
  'running',
  'succeeded',
  'failed',
  'cancelled',
  'superseded'
);

CREATE TABLE tenants (
  tenant_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  slug text NOT NULL UNIQUE,
  display_name text NOT NULL,
  data_residency_region text NOT NULL DEFAULT 'us',
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE source_systems (
  source_system_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id uuid NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
  name text NOT NULL,
  authority_score numeric(4, 3) NOT NULL CHECK (authority_score >= 0 AND authority_score <= 1),
  owns_entity_kinds text[] NOT NULL DEFAULT ARRAY[]::text[],
  owns_fields text[] NOT NULL DEFAULT ARRAY[]::text[],
  freshness_slo_seconds integer NOT NULL DEFAULT 86400,
  reconciliation_cadence_seconds integer NOT NULL DEFAULT 86400,
  rate_limit_per_minute integer,
  auth_profile_ref text,
  failure_policy text NOT NULL DEFAULT 'degrade_freshness',
  adapter_version text NOT NULL DEFAULT 'unversioned',
  supports_replay boolean NOT NULL DEFAULT false,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (tenant_id, name)
);

CREATE TABLE semantic_events (
  event_id uuid PRIMARY KEY,
  tenant_id uuid NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
  event_type text NOT NULL,
  schema_version text NOT NULL,
  source_system text NOT NULL,
  source_event_id text,
  occurred_at timestamptz NOT NULL,
  observed_at timestamptz NOT NULL,
  published_at timestamptz NOT NULL DEFAULT now(),
  partition_key text NOT NULL,
  causation_id uuid,
  correlation_id uuid,
  trace_id text,
  actor jsonb NOT NULL DEFAULT '{}'::jsonb,
  data_classification data_classification NOT NULL DEFAULT 'internal',
  policy_tags text[] NOT NULL DEFAULT ARRAY[]::text[],
  payload jsonb NOT NULL,
  payload_hash text NOT NULL,
  stream_sequence bigint,
  UNIQUE (tenant_id, source_system, source_event_id)
);

CREATE INDEX semantic_events_tenant_time_idx ON semantic_events (tenant_id, occurred_at DESC);
CREATE INDEX semantic_events_partition_idx ON semantic_events (tenant_id, partition_key, occurred_at DESC);
CREATE INDEX semantic_events_payload_gin_idx ON semantic_events USING gin (payload);

CREATE TABLE entities (
  entity_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id uuid NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
  kind text NOT NULL,
  canonical_name text NOT NULL,
  aliases text[] NOT NULL DEFAULT ARRAY[]::text[],
  primary_source_system text,
  primary_external_id text,
  confidence_score numeric(5, 4) NOT NULL DEFAULT 0.5 CHECK (confidence_score >= 0 AND confidence_score <= 1),
  confidence_band confidence_band NOT NULL DEFAULT 'unknown',
  data_classification data_classification NOT NULL DEFAULT 'internal',
  attributes jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (tenant_id, kind, canonical_name)
);

CREATE INDEX entities_tenant_kind_idx ON entities (tenant_id, kind);
CREATE INDEX entities_attributes_gin_idx ON entities USING gin (attributes);

CREATE TABLE entity_embeddings (
  entity_id uuid PRIMARY KEY REFERENCES entities(entity_id) ON DELETE CASCADE,
  tenant_id uuid NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
  embedding_model text NOT NULL,
  embedding vector(1536) NOT NULL,
  embedded_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX entity_embeddings_vector_idx ON entity_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE TABLE relationships (
  relationship_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id uuid NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
  subject_entity_id uuid NOT NULL REFERENCES entities(entity_id) ON DELETE CASCADE,
  predicate text NOT NULL,
  object_entity_id uuid NOT NULL REFERENCES entities(entity_id) ON DELETE CASCADE,
  valid_time_start timestamptz,
  valid_time_end timestamptz,
  source_event_id uuid REFERENCES semantic_events(event_id) ON DELETE SET NULL,
  confidence_score numeric(5, 4) NOT NULL DEFAULT 0.5 CHECK (confidence_score >= 0 AND confidence_score <= 1),
  attributes jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX relationships_subject_idx ON relationships (tenant_id, subject_entity_id, predicate);
CREATE INDEX relationships_object_idx ON relationships (tenant_id, object_entity_id, predicate);

CREATE TABLE evidence (
  evidence_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id uuid NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
  evidence_type text NOT NULL,
  source_system text NOT NULL,
  source_uri text,
  content_hash text NOT NULL,
  data_classification data_classification NOT NULL DEFAULT 'internal',
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  observed_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX evidence_tenant_source_idx ON evidence (tenant_id, source_system, observed_at DESC);

CREATE TABLE contradiction_sets (
  contradiction_set_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id uuid NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
  state text NOT NULL DEFAULT 'open',
  summary text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  resolved_at timestamptz
);

CREATE TABLE claims (
  claim_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id uuid NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
  subject_entity_id uuid NOT NULL REFERENCES entities(entity_id) ON DELETE CASCADE,
  predicate text NOT NULL,
  object_entity_id uuid REFERENCES entities(entity_id) ON DELETE SET NULL,
  object_value jsonb,
  claim_state claim_state NOT NULL DEFAULT 'asserted',
  valid_time_start timestamptz,
  valid_time_end timestamptz,
  observed_at timestamptz NOT NULL,
  confidence_score numeric(5, 4) NOT NULL CHECK (confidence_score >= 0 AND confidence_score <= 1),
  authority_score numeric(5, 4) NOT NULL DEFAULT 0.5 CHECK (authority_score >= 0 AND authority_score <= 1),
  freshness_score numeric(5, 4) NOT NULL DEFAULT 1 CHECK (freshness_score >= 0 AND freshness_score <= 1),
  evidence_score numeric(5, 4) NOT NULL DEFAULT 0.5 CHECK (evidence_score >= 0 AND evidence_score <= 1),
  contradiction_penalty numeric(5, 4) NOT NULL DEFAULT 1 CHECK (contradiction_penalty >= 0 AND contradiction_penalty <= 1),
  confidence_band confidence_band NOT NULL DEFAULT 'unknown',
  source_event_id uuid REFERENCES semantic_events(event_id) ON DELETE SET NULL,
  evidence_ids uuid[] NOT NULL DEFAULT ARRAY[]::uuid[],
  contradiction_set_id uuid REFERENCES contradiction_sets(contradiction_set_id) ON DELETE SET NULL,
  created_by_workload_id uuid,
  attributes jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX claims_subject_idx ON claims (tenant_id, subject_entity_id, predicate);
CREATE INDEX claims_confidence_idx ON claims (tenant_id, confidence_score, observed_at DESC);
CREATE INDEX claims_contradiction_idx ON claims (tenant_id, contradiction_set_id) WHERE contradiction_set_id IS NOT NULL;

CREATE TABLE workloads (
  workload_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id uuid NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
  workload_class text NOT NULL,
  objective text NOT NULL,
  input_event_ids uuid[] NOT NULL DEFAULT ARRAY[]::uuid[],
  input_entity_ids uuid[] NOT NULL DEFAULT ARRAY[]::uuid[],
  requested_depth text NOT NULL DEFAULT 'standard',
  selected_depth text,
  state workload_state NOT NULL DEFAULT 'candidate',
  score numeric(8, 4),
  score_components jsonb NOT NULL DEFAULT '{}'::jsonb,
  policy_tags text[] NOT NULL DEFAULT ARRAY[]::text[],
  required_approval_classes text[] NOT NULL DEFAULT ARRAY[]::text[],
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  deadline timestamptz
);

CREATE INDEX workloads_state_idx ON workloads (tenant_id, state, created_at DESC);

CREATE TABLE primitive_executions (
  primitive_execution_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  workload_id uuid NOT NULL REFERENCES workloads(workload_id) ON DELETE CASCADE,
  tenant_id uuid NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
  node_id text NOT NULL,
  primitive_type text NOT NULL,
  state text NOT NULL,
  input_hash text NOT NULL,
  output_hash text,
  trace_id text,
  started_at timestamptz,
  completed_at timestamptz,
  error jsonb
);

CREATE INDEX primitive_executions_workload_idx ON primitive_executions (tenant_id, workload_id, node_id);

CREATE TABLE approvals (
  approval_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id uuid NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
  workload_id uuid NOT NULL REFERENCES workloads(workload_id) ON DELETE CASCADE,
  approval_class text NOT NULL,
  state text NOT NULL DEFAULT 'requested',
  requested_by jsonb NOT NULL,
  decided_by jsonb,
  reason text,
  requested_at timestamptz NOT NULL DEFAULT now(),
  decided_at timestamptz
);

CREATE INDEX approvals_pending_idx ON approvals (tenant_id, state, requested_at DESC);

CREATE TABLE memories (
  memory_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id uuid NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
  memory_type text NOT NULL,
  title text NOT NULL,
  body text NOT NULL,
  source_event_ids uuid[] NOT NULL DEFAULT ARRAY[]::uuid[],
  source_claim_ids uuid[] NOT NULL DEFAULT ARRAY[]::uuid[],
  confidence_score numeric(5, 4) NOT NULL CHECK (confidence_score >= 0 AND confidence_score <= 1),
  importance_score numeric(5, 4) NOT NULL CHECK (importance_score >= 0 AND importance_score <= 1),
  data_classification data_classification NOT NULL DEFAULT 'internal',
  retention_policy text NOT NULL DEFAULT 'standard',
  promoted_at timestamptz NOT NULL DEFAULT now(),
  review_after timestamptz
);

CREATE INDEX memories_tenant_type_idx ON memories (tenant_id, memory_type, promoted_at DESC);

CREATE TABLE audit_events (
  audit_event_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id uuid NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
  actor jsonb NOT NULL,
  action text NOT NULL,
  target jsonb NOT NULL,
  policy_bundle_version text,
  decision text NOT NULL,
  reason_codes text[] NOT NULL DEFAULT ARRAY[]::text[],
  workload_id uuid,
  trace_id text,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX audit_events_tenant_time_idx ON audit_events (tenant_id, created_at DESC);
