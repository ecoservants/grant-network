-- ==========================================================
-- Open Grant Network
-- Database Schema
-- ==========================================================
-- This file defines the canonical database schema
-- for the Grant Network + Community Compute system.
-- ==========================================================
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------------------------------------
-- Core: organizations
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS organizations (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL COMMENT 'Funder or organization name',
  domain VARCHAR(255),
  homepage_url VARCHAR(1024),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  UNIQUE KEY idx_name (name),
  INDEX idx_domain (domain)
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
  url_hash CHAR(32) AS (MD5(url)) STORED,
  robots_allowed TINYINT(1) DEFAULT 1 COMMENT '0 if robots.txt blocks; 1 if allowed',
  robots_audit_ts DATETIME COMMENT 'When robots.txt was last checked',
  robots_log_url TEXT COMMENT 'Path to detailed per-domain robots audit log',
  content_hash CHAR(32) NOT NULL COMMENT 'MD5 hash of grant content',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (organization_id) REFERENCES organizations(id) ON UPDATE CASCADE ON DELETE RESTRICT,
  UNIQUE KEY uq_grant_url_hash (url_hash),
  INDEX idx_organization_id (organization_id),
  FULLTEXT KEY idx_title_desc (title, description)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC;

-- ----------------------------------------------------------
-- Community Compute: nodes
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS community_nodes (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  node_public_id CHAR(36) NOT NULL COMMENT 'Public unique identifier for the node',
  wp_user_id BIGINT UNSIGNED NULL COMMENT 'Optional WordPress user link',
  api_token CHAR(64) NOT NULL COMMENT 'Auth token assigned at registration',
  consent_version VARCHAR(16) DEFAULT '1.0',
  consent_url VARCHAR(512) DEFAULT 'https://ecoservants.org/consent/latest',
  consent_hash CHAR(64) NULL COMMENT 'SHA256 hash of consent document',
  consented_at DATETIME NULL,
  last_seen_at DATETIME NULL,
  is_active TINYINT(1) DEFAULT 0,
  opt_out_at DATETIME NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_node_public_id (node_public_id),
  UNIQUE KEY uq_api_token (api_token)
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
    FOREIGN KEY (node_id) REFERENCES community_nodes(id)
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
  status ENUM('pending','in_progress','completed','failed') NOT NULL DEFAULT 'pending',
  claimed_by_node_id BIGINT UNSIGNED NULL COMMENT 'FK to community_nodes',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_jobs_node
    FOREIGN KEY (claimed_by_node_id) REFERENCES community_nodes(id)
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
    FOREIGN KEY (job_id) REFERENCES community_jobs(id)
    ON UPDATE CASCADE
    ON DELETE CASCADE,

  CONSTRAINT fk_results_node
    FOREIGN KEY (node_id) REFERENCES community_nodes(id)
    ON UPDATE CASCADE
    ON DELETE CASCADE,

  UNIQUE KEY uq_job_node (job_id, node_id),
  INDEX idx_results_job (job_id),
  INDEX idx_results_node (node_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC;

-- -----------------------------
-- Policy: allow-list (placeholder mapping)
-- -----------------------------
CREATE TABLE IF NOT EXISTS allow_list_domains (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  domain VARCHAR(255) NOT NULL,
  is_allowed TINYINT(1) NOT NULL DEFAULT 1,
  policy_version VARCHAR(32) NULL,
  source VARCHAR(128) NULL,
  notes TEXT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_allow_domain (domain),
  INDEX idx_allow_allowed (is_allowed)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC;

-- -----------------------------
-- Robots audit summary (placeholder mapping)
-- -----------------------------
CREATE TABLE IF NOT EXISTS robots_audit_domains (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  domain VARCHAR(255) NOT NULL,
  robots_txt_url VARCHAR(1024) NULL,
  is_allowed TINYINT(1) NOT NULL DEFAULT 1,
  checked_at DATETIME NULL,
  crawl_delay_seconds INT NULL,
  sitemap_url VARCHAR(1024) NULL,
  raw_rules_hash CHAR(64) NULL,
  notes TEXT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_robots_domain (domain),
  INDEX idx_robots_allowed (is_allowed),
  INDEX idx_robots_checked (checked_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC;

SET FOREIGN_KEY_CHECKS = 1;
