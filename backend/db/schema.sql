-- ==========================================================
-- Open Grant Network
-- Database Schema
-- ==========================================================
-- Canonical schema for the Grant Network + Community Compute
-- Environment-agnostic (no CREATE DATABASE / USE)
-- ==========================================================

-- ----------------------------------------------------------
-- Core: organizations
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS organizations (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL COMMENT 'Funder or organization name',
  domain VARCHAR(255),
  homepage_url VARCHAR(1024),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  UNIQUE KEY idx_org_name (name),
  INDEX idx_org_domain (domain)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC;

-- ----------------------------------------------------------
-- Core: grants
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS grants (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  organization_id BIGINT UNSIGNED NOT NULL COMMENT 'FK to organizations',
  title VARCHAR(512) NOT NULL,
  description MEDIUMTEXT,
  amount_min DECIMAL(16,2),
  amount_max DECIMAL(16,2),
  deadline_date DATE,
  eligibility TEXT,
  country VARCHAR(64),
  region VARCHAR(64),
  url VARCHAR(1024) NOT NULL,

  -- Used for fast URL deduplication (not security-related)
  url_hash CHAR(32) AS (MD5(url)) STORED,

  robots_allowed TINYINT(1) DEFAULT 1 COMMENT '0 if robots.txt blocks; 1 if allowed',
  robots_audit_ts DATETIME COMMENT 'When robots.txt was last checked',
  robots_log_url TEXT COMMENT 'Path to robots audit log',

  -- SHA256 for content integrity & change detection
  content_hash CHAR(64) NOT NULL COMMENT 'SHA256 hash of grant content',

  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_grants_org
    FOREIGN KEY (organization_id)
    REFERENCES organizations(id)
    ON UPDATE CASCADE
    ON DELETE RESTRICT,

  UNIQUE KEY uq_grants_url_hash (url_hash),
  INDEX idx_grants_org (organization_id),
  FULLTEXT KEY idx_grants_title_desc (title, description)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC;

-- ----------------------------------------------------------
-- Community Compute: nodes
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS community_nodes (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  node_public_id CHAR(36) NOT NULL COMMENT 'Public unique identifier',
  wp_user_id BIGINT UNSIGNED NULL COMMENT 'Optional WordPress user link',
  api_token CHAR(64) NOT NULL COMMENT 'Auth token',

  consent_version VARCHAR(16) DEFAULT '1.0',
  consent_url VARCHAR(512) DEFAULT 'https://ecoservants.org/consent/latest',
  consent_hash CHAR(64) NULL COMMENT 'SHA256 hash of consent document',
  consented_at DATETIME NULL,

  last_seen_at DATETIME NULL,
  is_active TINYINT(1) DEFAULT 0,
  opt_out_at DATETIME NULL,

  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  UNIQUE KEY uq_nodes_public_id (node_public_id),
  UNIQUE KEY uq_nodes_api_token (api_token)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC;

-- ----------------------------------------------------------
-- Community Compute: node sessions
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS community_node_sessions (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  session_token CHAR(64) NOT NULL,
  node_id BIGINT UNSIGNED NOT NULL,

  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_seen_at DATETIME NULL,
  user_agent VARCHAR(255) NULL,
  ip_hash CHAR(64) NULL COMMENT 'SHA256 of IP or IP+salt',
  is_active TINYINT(1) DEFAULT 1,

  CONSTRAINT fk_sessions_node
    FOREIGN KEY (node_id)
    REFERENCES community_nodes(id)
    ON UPDATE CASCADE
    ON DELETE CASCADE,

  UNIQUE KEY uq_session_token (session_token),
  INDEX idx_sessions_node_active (node_id, is_active),
  INDEX idx_sessions_last_seen (last_seen_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC;

-- ----------------------------------------------------------
-- Community Compute: jobs
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS community_jobs (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  job_type VARCHAR(255) NOT NULL,
  payload_json JSON NOT NULL,

  status ENUM('pending','in_progress','completed','failed')
    NOT NULL DEFAULT 'pending',

  claimed_by_node_id BIGINT UNSIGNED NULL COMMENT 'FK to community_nodes',

  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_jobs_node
    FOREIGN KEY (claimed_by_node_id)
    REFERENCES community_nodes(id)
    ON UPDATE CASCADE
    ON DELETE SET NULL,

  INDEX idx_jobs_status (status),
  INDEX idx_jobs_type (job_type),
  INDEX idx_jobs_claimed_by (claimed_by_node_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC;

-- ----------------------------------------------------------
-- Community Compute: job results
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS community_job_results (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  job_id BIGINT UNSIGNED NOT NULL,
  node_id BIGINT UNSIGNED NOT NULL,

  result_json JSON NOT NULL,
  result_checksum CHAR(64) NULL COMMENT 'SHA256 checksum of canonical result payload',

  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_results_job
    FOREIGN KEY (job_id)
    REFERENCES community_jobs(id)
    ON UPDATE CASCADE
    ON DELETE CASCADE,

  CONSTRAINT fk_results_node
    FOREIGN KEY (node_id)
    REFERENCES community_nodes(id)
    ON UPDATE CASCADE
    ON DELETE CASCADE,

  UNIQUE KEY uq_results_job_node (job_id, node_id),
  INDEX idx_results_job (job_id),
  INDEX idx_results_node (node_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC;

-- ----------------------------------------------------------
-- Policy: domain_policy (CC-07)
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS domain_policy (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

  domain VARCHAR(255) NOT NULL COMMENT 'Canonical domain (e.g. grants.gov)',

  allow_crawl TINYINT(1) NOT NULL DEFAULT 0
    COMMENT 'Whether HTML crawling is permitted',

  allow_fetch_documents TINYINT(1) NOT NULL DEFAULT 0
    COMMENT 'Whether document downloads (PDF/CSV) are permitted',

  allow_extraction TINYINT(1) NOT NULL DEFAULT 0
    COMMENT 'Whether content extraction/parsing is permitted',

  max_depth INT NOT NULL DEFAULT 0
    COMMENT 'Maximum crawl depth (0 = no crawling)',

  notes TEXT NULL COMMENT 'Human notes or special handling',

  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  UNIQUE KEY uq_domain_policy_domain (domain),
  INDEX idx_domain_policy_crawl (allow_crawl),
  INDEX idx_domain_policy_fetch (allow_fetch_documents)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC;
-- CC-11 Migration: Add consent tracking fields
ALTER TABLE community_nodes
ADD COLUMN IF NOT EXISTS consent_provided BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS consent_version VARCHAR(50),
ADD COLUMN IF NOT EXISTS consent_hash VARCHAR(255),
ADD COLUMN IF NOT EXISTS consent_updated_at TIMESTAMP;
