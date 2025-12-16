-- ==========================================================
-- Open Grant Network
-- Database Schema
-- ==========================================================
-- This file defines the canonical database schema
-- for the Grant Network + Community Compute system.
-- ==========================================================

SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------------------------------------
-- Community Compute: Jobs
-- ----------------------------------------------------------

CREATE TABLE IF NOT EXISTS community_jobs (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  job_uuid CHAR(36) NOT NULL,
  node_id BIGINT UNSIGNED NULL,
  job_type VARCHAR(64) NOT NULL,
  payload JSON NOT NULL,
  status VARCHAR(24) NOT NULL DEFAULT 'queued',
  priority INT NOT NULL DEFAULT 0,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  started_at DATETIME NULL,
  completed_at DATETIME NULL,
  error_message TEXT NULL,

  UNIQUE KEY uq_community_jobs_job_uuid (job_uuid),
  KEY idx_community_jobs_status_created (status, created_at),
  KEY idx_community_jobs_node_id (node_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------
-- Community Compute: Job Results
-- ----------------------------------------------------------

CREATE TABLE IF NOT EXISTS community_job_results (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  job_id BIGINT UNSIGNED NOT NULL,
  node_id BIGINT UNSIGNED NULL,
  result JSON NOT NULL,
  result_hash CHAR(64) NULL,
  status VARCHAR(24) NOT NULL DEFAULT 'submitted',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  reviewed_at DATETIME NULL,
  reviewer VARCHAR(128) NULL,
  notes TEXT NULL,

  KEY idx_job_results_job_id (job_id),
  KEY idx_job_results_node_id (node_id),

  CONSTRAINT fk_job_results_job
    FOREIGN KEY (job_id)
    REFERENCES community_jobs(id)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

SET FOREIGN_KEY_CHECKS = 1;
