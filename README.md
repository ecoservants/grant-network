# 🌐 **Open Grant Network (OGN)**
### *A Distributed, Open Architecture for Real-Time Grant Intelligence, Funding Discovery, and Public Data Accessibility*

The **Open Grant Network (OGN)** is an open, scalable architecture designed to make grant data accessible, searchable, and actionable at a global level.  
This repository contains the public documentation, APIs, database schemas, WordPress integrations, and system specifications that define the OGN framework.

OGN powers the EcoServants® Grant Tracker ecosystem, enabling organizations to:

- Aggregate and normalize grant data
- Build custom funding intelligence tools
- Deploy distributed compute nodes for public-data validation
- Integrate grant search into websites, dashboards, and applications

This repository serves as the **canonical reference implementation** for the OGN ecosystem.

---

# 🚀 **Project Goals**

The Open Grant Network aims to:

- **Democratize access to grant data** by providing a transparent open architecture
- **Unify fragmented funding sources** (federal, state, foundation, and private)
- **Enable organizations to analyze funding trends** in real time
- **Leverage distributed compute nodes** to validate and enrich public datasets
- **Provide open-source tooling** businesses and nonprofits can build upon

---

# 🏗️ **Repository Contents**

This repository is organized into several major components:

```
docs/                      → Architecture, workflows, schemas, and system documentation  
backend/                   → API specs, crawler architecture, and Community Compute modules  
wp-plugin/                 → Grant Tracker Pro WordPress plugin (public build)  
scripts/                   → Data loaders, ETL routines, and dev utilities  
tests/                     → Test scaffolding for future validation and QA  
```

---

# 📚 **Documentation Overview**

Key documentation lives under `docs/` and includes:

### **Architecture**
- System overview
- Hybrid Architecture Build Plan
- Community Compute infrastructure
- API endpoints and schemas
- Database layouts and entity relationships

### **Workflows**
- Contribution workflow
- Branching model
- Task claiming guidelines
- Governance structure

### **Tasks & Roadmaps**
- Community Compute task definitions
- Crawler phases
- Milestone outlines

---

# 🔌 **WordPress: Eco Grant Tracker Pro Plugin**

The repository includes a public build of the **Eco Grant Tracker Pro** plugin located under:

```
wp-plugin/eco-grant-tracker-pro/
```

This plugin provides:

- A React-styled front-end interface
- Grant grids, filters, and status badges
- Modal-based funder previews
- Modernized CSS and JS
- Integration points for OGN data endpoints

---

# 🌍 **Community Compute: Distributed Verification Layer**

OGN’s Community Compute layer enables volunteers and partner organizations to contribute compute resources for:

- Fetching and verifying public grant datasets
- Normalizing and cleaning financial filings
- Validating funder information using robots.txt-aware crawlers
- Supporting real-time updates to the grant intelligence network

---

# 🤝 **How to Contribute**

OGN welcomes open-source contributions.

1. **Fork the repository**  
2. **Pick an issue** from the Project Board  
3. **Submit a Pull Request**  
4. Changes are reviewed before merging into `main`

---

# 🔒 **Branch Model**

The project uses a single protected branch:

- `main` — stable, public-facing

All development occurs via forks.

---

# 📄 **License**

Apache 2.0

---

# 📬 **Contact**

support@ecoservantsproject.org  
https://ecoservantsproject.org
