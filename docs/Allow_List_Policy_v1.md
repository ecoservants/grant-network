# Grant Network Allow-List Policy v1.0

## 1. Overview
This document defines the policies and procedures for maintaining the allow-list of domains for the Grant Network Community Compute system. The goal is to ensure ethical, legal, and efficient crawling of grant-related information.

## 2. Domain Inclusion Criteria
A domain may be included in the allow-list if it meets the following criteria:

### 2.1 Relevance
- The domain belongs to a recognized grant-making entity (e.g., foundation, government agency, trust).
- The domain hosts public information about grant opportunities, funding guidelines, or awarded grants.

### 2.2 Accessibility
- Content is publicly available without authentication (no login required).
- Content is not behind a paywall.
- The site uses standard HTTP/HTTPS protocols.

### 2.3 Reputation
- The organization is a verified legal entity in its jurisdiction.
- The domain has no history of malicious behavior (phishing, malware).

## 3. Robots.txt Compliance and Ethics
The Grant Network crawler MUST strictly adhere to the following rules:

### 3.1 Robots.txt
- The crawler MUST fetch and parse `robots.txt` for every domain.
- `User-agent: *` directives must be respected unless a specific `User-agent: GrantNetworkBot` directive exists.
- Disallowed paths must NEVER be crawled.

### 3.2 Crawl Rate
- Respect `Crawl-delay` directives in `robots.txt`.
- If no delay is specified, default to a polite delay (e.g., 1 request per second max) to avoid server load.

### 3.3 Identification
- The crawler must identify itself via the User-Agent string, providing a URL to this policy or a contact page.
  - Example: `Mozilla/5.0 (compatible; GrantNetworkBot/1.0; +https://github.com/ecoservants/grant-network)`

## 4. Exclusion and Removal
Domains will be excluded or removed if:
- They request removal (opt-out).
- They implement technical blocks (IP bans, CAPTCHAs).
- They cease to be relevant or active.
- They violate the Terms of Service of the crawling infrastructure.

## 5. Maintenance
- The allow-list is reviewed quarterly.
- New domains are added via Pull Request to `allow-list.json`, requiring review by at least one maintainer.
- Automated checks run weekly to verify domain accessibility and `robots.txt` compliance.
