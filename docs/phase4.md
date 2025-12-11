Phase 4: Implement WordPress Grant Search UI (Grid + Filters)
## Summary
Build the primary grant search interface in WordPress, using the Grant Network API to display opportunities in a responsive grid with filters and search controls.

## Requirements
- Create a grants listing interface (grid or table) in the ESGT plugin.
- Add filters for keyword, location, deadline, amount range, and eligibility.
- Connect UI controls to the backend WordPress REST bridge.
- Ensure layout is mobile responsive and accessible (basic a11y).

## Deliverables
- WordPress template or shortcode for the grant search UI.
- CSS/JS for filters and responsive layout.
- Integration with /api/wp_bridge/ opportunity search endpoints.

## Acceptance Criteria
- Users can search and filter grants from within WordPress.
- Results update without full page reload (AJAX or fetch).
- Layout renders correctly on desktop and mobile.
- No sensitive internal data exposed in UI.

## Suggested Labels
wordpress, ui/ux, integration, opportunity-search, phase-4

Phase 4: Add Funder Preview Modal in WordPress Plugin
## Summary
Create a funder preview modal in the ESGT plugin that shows key details about a funder and its related opportunities, powered by the Grant Network API.

## Requirements
- Implement modal UI that opens from funder or opportunity listings.
- Display funder name, mission, location, giving focus, and recent opportunities.
- Fetch data via WP REST bridge (funder + related opportunities endpoint).
- Ensure modal is keyboard accessible and easy to close.

## Deliverables
- Modal markup and JS behavior.
- API integration code for loading preview content.
- CSS to match EcoServants brand style.

## Acceptance Criteria
- Funder preview opens and loads content quickly.
- Related opportunities appear in the modal.
- Modal works on mobile and desktop.
- No console errors or broken layouts.

## Suggested Labels
wordpress, ui/ux, funder-intelligence, integration, phase-4

Phase 4: Implement Saved Filters / Search Presets in WP UI
## Summary
Allow users to save commonly used search filters (e.g., “California environment grants,” “student research funding”) as reusable presets within the WordPress UI.

## Requirements
- Add UI elements for saving and naming filter presets.
- Store presets per user in WordPress (user meta or plugin table).
- Allow users to load, update, and delete saved presets.
- Integrate presets with existing search filters.

## Deliverables
- Preset management UI.
- Backend storage and retrieval logic.
- Documentation for using saved searches.

## Acceptance Criteria
- Users can create, edit, and delete their own presets.
- Presets correctly apply all saved filters when loaded.
- Presets persist across sessions.
- No impact on users who choose not to use presets.

## Suggested Labels
wordpress, ui/ux, opportunity-search, enhancement, phase-4

Phase 4: Optimize Search Query Performance for High Volume
## Summary
Optimize the search and matching queries used by the Grant Network backend to support larger datasets and high-traffic usage from WordPress and external clients.

## Requirements
- Profile existing funder and opportunity search queries.
- Add necessary indexes to hot tables.
- Optimize JOINs and filters for speed.
- Implement query caching where beneficial.

## Deliverables
- Query profiling report.
- Database migration with new indexes.
- Updated search query implementations.

## Acceptance Criteria
- Median search latency reduced to under 200ms under normal load.
- Queries handle 100k+ opportunities and 50k+ funders without timeout.
- CPU and memory usage within acceptable range in test environment.
- No regression in search accuracy.

## Suggested Labels
performance, backend, optimization, phase-4

Add Admin Analytics Dashboard for Grant Network Usage
## Summary
Create an admin-facing analytics dashboard (either in WordPress or a standalone admin view) to display key metrics about Grant Network usage, searches, and matches.

## Requirements
- Track daily search volume, top queries, and API usage.
- Display counts of funders, opportunities, and active compute nodes.
- Visualize basic trends (last 7 days / 30 days).
- Restrict access to admin-only roles.

## Deliverables
- Admin dashboard page UI.
- Metrics aggregation queries or endpoints.
- Basic charts or tables showing key metrics.

## Acceptance Criteria
- Admins can view live usage metrics without errors.
- Dashboard loads under 2 seconds for typical usage.
- Only authorized users can access analytics.
- Metrics help guide optimization and content decisions.

## Suggested Labels
analytics, admin-ui, wordpress, backend, phase-4

Phase 4: Implement Advanced Matching Engine v3 (Semantic Layer)
## Summary
Upgrade the matching engine to include semantic similarity scoring, enabling deeper matching between EcoServants projects and opportunity descriptions.

## Requirements
- Add keyword expansion and similarity scoring.
- Incorporate embeddings or lightweight semantic models (no external API needed).
- Add tunable scoring weights for semantics vs. exact matches.
- Produce expanded match reports with explanation fields.

## Deliverables
- matching_engine_v3.py.
- Semantic scoring documentation.
- Example match reports with explanation output.

## Acceptance Criteria
- Matching accuracy improves over v2 in internal benchmarks.
- Semantic matching does not introduce regressions.
- Match reports clearly show why opportunities were recommended.
- WP plugin can consume new scoring fields.

## Suggested Labels
matching, algorithms, funder-intelligence, opportunity-search, phase-4

Phase 4: Add Pagination, Sorting & Load States to WP UI
## Summary
Enhance the WordPress UI to support pagination, sorting options, and loading indicators for a polished user experience when browsing grants.

## Requirements
- Add pagination UI (next/previous buttons).
- Add sorting controls: relevance, deadline, amount, newest.
- Show loading states during API requests.
- Ensure accessibility compliance for interactive controls.

## Deliverables
- Updated WordPress UI components.
- Improved fetch wrapper with loading states.
- Sorting logic integrated with REST bridge.

## Acceptance Criteria
- Pagination works with all search results.
- Sorting accurately reflects API queries.
- Loading states appear and disappear correctly.
- UI remains responsive on mobile and tablet.

## Suggested Labels
wordpress, ui/ux, frontend, enhancement, phase-4

Phase 4: Create Developer Documentation Hub
## Summary
Build a centralized documentation hub covering setup, local development, API usage, compute node participation, and contribution guidelines.

## Requirements
- Create a /docs directory index.
- Write onboarding guide for new contributors.
- Document API endpoints, schemas, workflows, and compute architecture.
- Include examples for common development tasks.

## Deliverables
- docs/index.md.
- Developer onboarding guide.
- API and compute documentation.
- Folder structure reference.

## Acceptance Criteria
- New contributors can onboard within 20–30 minutes.
- All major components documented clearly.
- README links correctly to the documentation hub.
- Documentation passes internal review.

## Suggested Labels
documentation, onboarding, contributors, phase-4

Phase 4: Create Contributor Guide & Coding Standards
## Summary
Create a Contributor Guide containing Git workflow standards, branch naming rules, commit conventions, code review expectations, and testing procedures.

## Requirements
- Define contribution workflow (fork, PR, review cycle).
- Establish commit message and branch naming standards.
- Document code formatting rules for Python and WP plugin PHP/JS.
- Describe CI expectations and how contributors run tests locally.

## Deliverables
- CONTRIBUTING.md.
- Code style guides.
- PR checklist and templates.

## Acceptance Criteria
- Contributors follow guide successfully during PRs.
- Maintainers approve structure and clarity.
- All rules aligned with public open-source standards.
- Templates appear automatically when opening a new PR.

## Suggested Labels
documentation, governance, contributors, phase-4

Phase 4: Implement Public Release Checklist & Stability Review
## Summary
Prepare the repository for public release by validating security, stability, UX, contributor onboarding, and API reliability.

## Requirements
- Review all API endpoints for security & rate limiting.
- Verify WP plugin integration works from clean install.
- Ensure documentation is complete and accessible.
- Create a pre-release checklist document.

## Deliverables
- public_release_checklist.md.
- Release candidate tag (v1.0.0-rc1).
- Summary of resolved blockers and known issues.

## Acceptance Criteria
- All critical issues resolved or labeled for post-launch.
- Public users can install WP plugin and retrieve data successfully.
- API stable under low-to-moderate traffic.
- Final approval from maintainers.

## Suggested Labels
release, stability, governance, documentation, phase-4

Phase 4: Implement Automated Testing Framework for Backend
## Summary
Create a complete automated testing framework for the Grant Network backend, covering ingestion, normalization, search, matching, and compute endpoints.

## Requirements
- Set up pytest or equivalent test framework.
- Write unit tests for core modules (schemas, normalization, ingestion).
- Add integration tests for API endpoints.
- Create sample datasets for reproducible tests.

## Deliverables
- /tests directory with organized test files.
- pytest configuration + runner.
- Test datasets and fixtures.

## Acceptance Criteria
- Tests run successfully in local and CI environments.
- At least 60% coverage for core modules.
- Failures produce clear and actionable messages.
- CI pipeline blocks merges with failing tests.

## Suggested Labels
testing, backend, ci, quality, phase-4

Phase 4: Implement Continuous Integration Pipeline (GitHub Actions)
## Summary
Create a full GitHub Actions CI pipeline that automatically runs tests, linting, security checks, and build validation on every pull request.

## Requirements
- Set up GitHub Actions workflows for:
  - Python tests
  - Linting (flake8/black)
  - Security scanning (Bandit or equivalent)
  - WP plugin syntax validation
- Require CI checks to pass before merging.

## Deliverables
- /.github/workflows/ci.yaml.
- Linting and test configuration files.
- Security scanning workflow.

## Acceptance Criteria
- CI runs on all PRs and main/develop branches.
- Failures correctly block merges.
- CI completes under 5 minutes.
- Developers can reproduce CI runs locally.

## Suggested Labels
ci, automation, quality, backend, wordpress, phase-4

Phase 4: Implement Error Monitoring & Observability Layer
## Summary
Add centralized error monitoring and observability to track failures, performance issues, and anomaly patterns across API, ingestion, and compute workflows.

## Requirements
- Implement structured logging with correlation IDs.
- Add monitoring hooks for slow queries and API latencies.
- Track ingestion and compute job error rates.
- Provide high-level health metrics dashboards.

## Deliverables
- observability_module.py.
- Error event model and log format.
- Metrics JSON endpoints or dashboards.

## Acceptance Criteria
- System logs all errors with stack traces and context.
- Admins can see health indicators for ingestion, API, and compute.
- Performance anomalies are detectable through metrics.
- Logs stored in a consistent, queryable format.

## Suggested Labels
monitoring, observability, reliability, backend, phase-4

Phase 4: WordPress Plugin UX Stabilization & Polish Pass
## Summary
Improve usability, responsiveness, and visual consistency of the ESGT WordPress plugin to prepare it for public release.

## Requirements
- Optimize layouts for plugin admin pages.
- Improve loading and empty states.
- Unify typography, spacing, and color tokens with EcoServants brand.
- Fix UI inconsistencies reported during testing.

## Deliverables
- Updated CSS/JS for plugin UI.
- Polished templates and admin views.
- WP visual QA checklist.

## Acceptance Criteria
- All UI components render consistently across browsers.
- No overlapping elements or broken layouts.
- User testing feedback addressed.
- Plugin meets minimum UX standard for public release.

## Suggested Labels
wordpress, ui/ux, cleanup, polish, phase-4

Phase 4: Implement System-wide Configuration Management
## Summary
Create a centralized configuration system allowing the Grant Network to manage environment variables, API settings, rate limits, compute rules, and plugin settings consistently.

## Requirements
- Build config loader that reads from env + config files.
- Validate required settings at startup.
- Support secrets and sensitive data storage.
- Provide safe defaults for development mode.

## Deliverables
- config_manager.py.
- Sample .env.example and config file templates.
- Documentation on configuration hierarchy.

## Acceptance Criteria
- System loads cleanly with validated configuration.
- Missing or invalid settings produce clear errors.
- Secure handling of sensitive keys.
- Configuration consistent across backend and WP plugin.

## Suggested Labels
configuration, backend, infrastructure, phase-4

Phase 4: Build Public Documentation Website (Docs Portal)
## Summary
Create a public-facing documentation website for the Grant Network, including developer guides, API references, compute participation instructions, and WordPress plugin usage.

## Requirements
- Generate static docs site using MkDocs, Docusaurus, or similar.
- Include sections: API, Schemas, Compute, WP Plugin, Contributing.
- Deploy automatically via GitHub Pages or Netlify.
- Ensure branding matches EcoServants style.

## Deliverables
- /docs/site directory or build config.
- Navigation structure for all major areas.
- Deployment script or GitHub Pages workflow.

## Acceptance Criteria
- Public users can access documentation without login.
- All pages load cleanly and contain up-to-date content.
- Site rebuilds automatically on documentation updates.
- Design matches EcoServants brand guidelines.

## Suggested Labels
documentation, public-facing, infrastructure, phase-4

Phase 4: Build Community Support Tools (FAQs, Troubleshooting, Guides)
## Summary
Create community support resources to help contributors, developers, and compute node volunteers troubleshoot common issues and get started easily.

## Requirements
- Write FAQs for dataset ingestion, API issues, WP plugin usage, and compute node setup.
- Add troubleshooting steps for common errors.
- Provide examples for typical developer workflows.
- Organize support materials in the docs portal.

## Deliverables
- community_support.md.
- FAQ section in documentation site.
- Troubleshooting reference for compute and WP plugin.

## Acceptance Criteria
- Contributors can self-resolve common issues using documentation.
- Support materials consistently referenced in README and onboarding docs.
- FAQ reduces number of repeated contributor questions.

## Suggested Labels
documentation, community, support, phase-4

Phase 4: Create SDK & Helper Libraries for API Consumers
## Summary
Develop helper libraries or SDK-style utilities (Python + JS) that streamline connecting to the Grant Network API and performing search/matching tasks programmatically.

## Requirements
- Provide Python client library for funder/opportunity search.
- Provide JS utility functions for frontend integrations.
- Include authentication helpers for API keys.
- Add examples for common usage patterns.

## Deliverables
- /sdk/python directory.
- /sdk/js directory.
- Example scripts showing search, filter, match operations.

## Acceptance Criteria
- Users can connect to the API with only a few lines of code.
- Error handling and authentication work reliably.
- SDK included in documentation and public docs site.
- SDK functions align fully with API design.

## Suggested Labels
sdk, api, developer-tools, phase-4

Prepare WordPress Plugin for Release (Versioning + Packaging)
## Summary
Prepare the EcoServants Grant Tracker Pro (ESGT) WordPress plugin for public release, including versioning, packaging, update routines, and distribution readiness.

## Requirements
- Add plugin headers for versioning.
- Create a build ZIP with only necessary plugin files.
- Document installation steps and requirements.
- Ensure compatibility with WordPress 6.x and PHP 8.x.

## Deliverables
- Versioned plugin package (v1.0.0).
- Installation guide.
- WordPress.org-ready documentation (even if not uploaded yet).

## Acceptance Criteria
- Plugin installs on clean WP site without errors.
- All critical features work: search, matching, funder preview.
- Plugin files follow WP coding standards.
- Update path prepared for future versions.

## Suggested Labels
wordpress, release, packaging, phase-4

Phase 4: Final Security Hardening & Penetration Review
## Summary
Perform a final security hardening audit of the Grant Network ecosystem, including backend APIs, compute systems, WP plugin endpoints, and contributor workflows.

## Requirements
- Review all API endpoints for input sanitization.
- Validate WordPress REST requests and nonce protections.
- Ensure compute job payloads cannot induce exploits.
- Review authentication, rate limiting, and token lifecycles.

## Deliverables
- security_hardening_report.md.
- List of remediated vulnerabilities.
- Final approval for public v1.0 release.

## Acceptance Criteria
- No critical vulnerabilities remain.
- API and WP plugin pass penetration-style testing.
- Compute systems hardened against malformed job submissions.
- Security documentation updated and published.

## Suggested Labels
security, hardening, audit, release, phase-4

Phase 4: Establish Contributor Governance & Maintainer Roles
## Summary
Define a governance structure for the Grant Network project, including maintainer responsibilities, contributor permissions, decision-making rules, and escalation paths.

## Requirements
- Create Maintainer Guide describing duties and expectations.
- Define permission levels for contributors, maintainers, and admins.
- Establish decision processes for major changes.
- Add Code of Conduct link and enforcement steps.

## Deliverables
- GOVERNANCE.md.
- Maintainer Roles & Responsibilities document.
- Updated README links to governance materials.

## Acceptance Criteria
- Clear contributor and maintainer roles documented.
- Governance model approved by project leadership.
- Contributors understand how decisions are made.
- Escalation and moderation process defined.

## Suggested Labels
governance, contributors, documentation, phase-4

Phase 4: Implement Automated Issue Labeling & Triage Rules
## Summary
Add automation (GitHub Actions or Probot) to automatically label new issues based on keywords, assign them to project boards, and guide contributors through triage.

## Requirements
- Create YAML or Probot configuration for label automation.
- Auto-apply labels like dataset, backend, wordpress, compute, docs.
- Assign new issues to the correct project roadmap column.
- Provide contributors with initial triage instructions.

## Deliverables
- /.github/labeler.yml or probot config.
- Documentation for automated labeling.
- Triage flow diagram.

## Acceptance Criteria
- New issues receive appropriate labels automatically.
- Issues appear in the Project board without manual intervention.
- Maintainers verify automation accuracy with multiple test cases.
- Contributors guided toward correct workflow.

## Suggested Labels
automation, github-actions, maintainership, phase-4

Phase 4: Improve Developer Experience (DX) for Local Setup
## Summary
Streamline the local development experience by providing setup scripts, seed datasets, environment templates, and debugging tools for backend and WP plugin developers.

## Requirements
- Create a local bootstrap script for environment setup.
- Provide sample .env files and test datasets.
- Document local WordPress + plugin installation.
- Add debugging tools or scripts for common workflows.

## Deliverables
- setup_local_dev.sh or equivalent.
- Local development guide.
- Seed datasets for funder/opportunity tests.

## Acceptance Criteria
- New developers can set up a working local environment in <10 minutes.
- Setup tested across Windows, macOS, and Linux.
- WP plugin installation instructions verified.
- DX improvements reflected in contributor feedback.

## Suggested Labels
developer-tools, onboarding, documentation, phase-4

Phase 4: Create Long-Term Maintenance & Update Roadmap
## Summary
Develop a long-term maintenance plan outlining how datasets, APIs, schemas, and compute systems will be updated and versioned over time.

## Requirements
- Define versioning strategy for schemas and APIs.
- Add rules for dataset refresh cycles (IRS, Grants.gov, third-party).
- Create deprecation policy for outdated fields or endpoints.
- Provide timeline for future feature phases.

## Deliverables
- maintenance_roadmap.md.
- Versioning guidelines.
- Schema/API deprecation checklist.

## Acceptance Criteria
- Maintenance roadmap reviewed and approved by leadership.
- All major system components included in versioning policy.
- Contributors understand how updates and deprecations occur.
- Roadmap linked in README and documentation site.

## Suggested Labels
planning, governance, documentation, phase-4

Phase 4: Create Post-Launch Monitoring & Support System
## Summary
Establish a post-launch monitoring and support workflow to handle bug reports, performance issues, compute node anomalies, and plugin support requests.

## Requirements
- Define support channels (GitHub Issues, Discussions, email optional).
- Add templates for bug reports and feature requests.
- Implement monitoring alerts for API downtime and compute failures.
- Document the support SLA and triage workflow.

## Deliverables
- SUPPORT.md.
- Bug and feature issue templates.
- Monitoring alert rules (API + compute).
- Triage workflow diagram.

## Acceptance Criteria
- Users have a clear way to request help.
- Alerts fire correctly for outages or anomalies.
- Maintainers can triage issues efficiently.
- Support system prepared for ongoing public use.

## Suggested Labels
support, monitoring, maintainership, documentation, phase-4

Phase 4: Build Community Engagement & Outreach Plan
## Summary
Create a community engagement strategy to attract contributors, compute node volunteers, nonprofit partners, and open-source collaborators after public launch.

## Requirements
- Draft messaging for GitHub, LinkedIn, EcoServants.org, and partner channels.
- Create simple “How to Contribute” share kits.
- Identify target communities (open-source, nonprofit tech, data for good).
- Provide onboarding guides for each contributor type.

## Deliverables
- outreach_strategy.md.
- Contributor share kit (graphics, text templates).
- List of potential partner communities.

## Acceptance Criteria
- Engagement plan approved by leadership.
- Messaging aligned with EcoServants brand and mission.
- New contributors can clearly understand how to get started.
- Outreach materials ready for post-launch announcement.

## Suggested Labels
community, outreach, documentation, governance, phase-4

Phase 4: Create Backlog & Future Feature Roadmap (Post v1.0)
## Summary
Build a structured backlog of future enhancements and features to guide post-launch development of the Grant Network ecosystem.

## Requirements
- Identify all MVP-excluded features.
- Group tasks into short-term, mid-term, and long-term priorities.
- Create roadmap sections: backend, datasets, compute, WP plugin, UX, AI/ML.
- Publish roadmap for public visibility.

## Deliverables
- backlog.md.
- future_roadmap.md.
- Prioritized list of next-phase milestones.

## Acceptance Criteria
- Roadmap clearly distinguishes MVP vs post-MVP work.
- Contributors know which features are open for development.
- Roadmap linked in README and docs site.
- Reviewed and approved by maintainers.

## Suggested Labels
planning, roadmap, governance, phase-4

Phase 4: Compute Network Scaling Strategy (Nodes → Thousands)
## Summary
Develop a scaling strategy for Community Compute to support thousands of distributed volunteer nodes while maintaining security, stability, and ethical compliance.

## Requirements
- Model scaling needs for job scheduling, storage, and verification load.
- Define requirements for node reputation, batching, and rate limiting.
- Plan horizontal scaling options for API and ingestion layers.
- Identify bottlenecks and propose mitigation strategies.

## Deliverables
- compute_scaling_strategy.md.
- System diagrams showing growth pathways.
- Initial performance/stress benchmarks.

## Acceptance Criteria
- Strategy supports at least 5k nodes in theoretical scaling.
- Bottlenecks identified and documented.
- Scaling plan approved for future implementation cycles.
- Summary included in long-term maintenance roadmap.

## Suggested Labels
scaling, community-compute, architecture, planning, phase-4

Phase 4: Research Task — Semantic Search Enhancements (v4)
## Summary
Explore next-generation semantic search techniques (embeddings, vector similarity, hybrid lexical-semantic models) to improve accuracy of funder and opportunity matching.

## Requirements
- Evaluate open-source embedding models.
- Prototype vector indexing for opportunities and funders.
- Compare semantic recall vs baseline keyword search.
- Document tradeoffs for performance and interpretability.

## Deliverables
- semantic_search_research.md.
- Prototype vector search module.
- Benchmark results comparing v3 and semantic v4.

## Acceptance Criteria
- Research produces clear recommendations for v4 engine.
- Prototype demonstrates measurable improvements in recall.
- Complexity and infrastructure costs documented.
- Maintainers decide whether to implement semantic search in future release.

## Suggested Labels
research, matching, ai-ml, opportunity-search, phase-4

Phase 4: Research Task — LLM-Assisted Grant Summaries & Insights
## Summary
Investigate the feasibility of generating AI-assisted summaries, eligibility insights, and funder alignment notes using lightweight, optional LLM integrations.

## Requirements
- Prototype a summary generator using open-source LLMs (local inference preferred).
- Evaluate hallucination risk and mitigation approaches.
- Test eligibility extraction using rule-based + AI hybrid methods.
- Document where AI adds value vs complexity.

## Deliverables
- llm_research_report.md.
- Summary-generation prototype.
- Eligibility extraction benchmark tests.

## Acceptance Criteria
- Research outlines safe, ethical use cases for LLM assistance.
- Prototypes demonstrate meaningful UX improvements.
- Risks and safeguards documented clearly.
- Decision made on whether to include AI features in future releases.

## Suggested Labels
research, ai-ml, opportunity-insights, future, phase-4
