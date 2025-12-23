-- ==========================================================
-- Open Grant Network
-- Reset / Teardown Script
-- ==========================================================
-- Drops all tables in correct dependency order
-- ==========================================================

-- Community Compute (dependent first)
DROP TABLE IF EXISTS community_job_results;
DROP TABLE IF EXISTS community_jobs;
DROP TABLE IF EXISTS community_node_sessions;

-- Community Compute (core)
DROP TABLE IF EXISTS community_nodes;

-- Core data
DROP TABLE IF EXISTS grants;
DROP TABLE IF EXISTS organizations;

-- Policy
DROP TABLE IF EXISTS domain_policy;


