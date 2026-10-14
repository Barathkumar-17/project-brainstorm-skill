# Standards Core

Built-in standards the skill applies without web access. Pick only the rows that apply to the project. Editions below were current in October 2026; when web access is available, check for newer ones.

Contents: How to select · Requirements · Quality model · Architecture · Testing · Security · Authentication and data formats · Accessibility · Privacy and data protection · Operations

## How to select

1. Always apply: **Requirements**, **Quality model**, **Architecture**, **Testing**.
2. Apply the other sections only when their "Applies when" condition is met.
3. In the SRS, list each applied standard with one line on why it applies.

## Requirements: ISO/IEC/IEEE 29148:2018

Each requirement must be:
- **Necessary:** removing it leaves a gap.
- **Appropriate:** at the right level of detail for the document it sits in.
- **Unambiguous:** one reading only; no "fast", "easy", "user-friendly" without a number.
- **Complete:** needs nothing else to be understood.
- **Singular:** one requirement per statement.
- **Feasible:** achievable within the project's constraints (free tools, target platform) at acceptable risk.
- **Verifiable:** has a pass/fail check.
- **Correct:** accurately states the stakeholder need.
- **Conforming:** follows the SRS template and wording style.

The set as a whole must be complete, consistent (no two requirements conflict), feasible, comprehensible and able to be validated.

Attributes on every requirement: ID, priority (core / supporting), source, rationale, verification method. Traceability comes from these attributes and the traceability matrix, not from the requirement text. Verification methods commonly used with 29148: inspection, analysis, demonstration, test.

## Quality model: ISO/IEC 25010:2023

Write at least one NFR per characteristic, or state why it doesn't apply.

| Characteristic | What to pin down |
|---|---|
| Functional suitability | Completeness, correctness and appropriateness of core functions |
| Performance efficiency | Response time, throughput, CPU, memory, storage, network use |
| Compatibility | Coexistence and interoperability with other systems |
| Interaction capability | Learnability, operability, error protection, inclusivity (accessibility), user assistance, self-descriptiveness |
| Reliability | Faultlessness, availability, fault tolerance, recoverability |
| Security | Confidentiality, integrity, non-repudiation, accountability, authenticity, resistance to attack |
| Maintainability | Modularity, reusability, analysability, modifiability, testability |
| Flexibility | Adaptability, scalability, installability, replaceability |
| Safety | Operational constraints, risk identification, fail-safe behaviour, hazard warnings, safe integration |

## Architecture: ISO/IEC/IEEE 42010:2022

The standard sets what an architecture description contains, not which views to draw. Include: stakeholders and their concerns; views that answer those concerns; correspondences between views (which component owns which entity, which endpoint serves which flow); and decisions with rationale and rejected alternatives (ADRs).

This skill's choice of views: component (with trust boundaries), core-flow sequence, data model and deployment, as set in `templates.md`.

## Testing: ISO/IEC/IEEE 29119-3:2021

The test plan covers: context and scope, assumptions and constraints, stakeholders, test risks, test strategy (levels, techniques, completion criteria, suspension and resumption criteria), environment, and test cases traced to requirements. Unit, integration, system and acceptance are the conventional levels. Staffing and schedule sections are left out by design, since this skill does not collect team size or deadlines.

Non-functional tests (performance, security, accessibility) are included wherever an NFR exists.

## Security

| Standard | Applies when | Use |
|---|---|---|
| OWASP Top 10:2025 | Any web app or backend | Check the design against every category: broken access control, security misconfiguration, software supply chain failures, cryptographic failures, injection, insecure design, authentication failures, software or data integrity failures, security logging and alerting failures, mishandling of exceptional conditions |
| OWASP ASVS 5.0 | Any app with users or stored data | Level 1 minimum for every tier; Level 2 for MVP, Production, or any app with personal or sensitive data; Level 3 for high-value or high-risk apps |
| OWASP API Security Top 10 (2023) | The project exposes an API | Check every endpoint against it |
| OWASP MASVS 2.x | Mobile app | Cover all eight control groups: storage, crypto, auth, network, platform, code, resilience, privacy |
| STRIDE | Always (threat model) | Spoofing (authentication), tampering (integrity), repudiation (non-repudiation), information disclosure (confidentiality), denial of service (availability), elevation of privilege (authorization), applied per component and data flow |
| NIST SP 800-63B-4 | The project has password or login flows | Minimum 15 characters for password-only login (8 with MFA); allow at least 64; no composition rules or forced periodic changes; check against breached-password lists; no hints or security questions; rate-limit failed logins; reauthentication limits per assurance level |

Baseline controls whatever the tier:
- TLS on every network hop; security headers (HSTS, Content-Security-Policy) and hardened default config.
- Server-side, deny-by-default authorization on every request.
- Passwords hashed with Argon2id (scrypt if unavailable; bcrypt only for legacy systems), using current OWASP Password Storage parameters.
- Sessions: Secure, HttpOnly, SameSite cookies; new session ID at login; idle and absolute timeouts; CSRF protection for cookie-based auth.
- Server-side input validation, parameterised queries and output encoding.
- Rate limits on login and API endpoints.
- Secrets kept out of code, client and logs; no personal data in logs.
- Generic error messages to users; fail closed.
- Security logging and alerting for sensitive actions.
- Supply chain: lockfiles, dependency and secret scanning.

## Authentication and data formats

| Standard | Applies when |
|---|---|
| OAuth 2.0 (RFC 6749) with PKCE (RFC 7636) and the OAuth Security BCP (RFC 9700); OpenID Connect | Third-party or social login, delegated access. OAuth 2.1 is still a draft; don't cite it as a standard |
| JWT (RFC 7519) with JWT Best Current Practices (RFC 8725) | Stateless tokens are used |
| OpenAPI 3.1 or later (3.2 current) | Any HTTP API; the API spec follows its structure |
| HTTP Semantics (RFC 9110) | Any HTTP API: correct methods and status codes |
| Problem Details (RFC 9457) | API error responses |
| JSON (RFC 8259), UTF-8 | Data exchange and storage of text |
| RFC 3339 / ISO 8601 timestamps, stored in UTC | Any date or time |
| Semantic Versioning 2.0.0 | APIs, libraries, releases |

## Accessibility

| Standard | Applies when |
|---|---|
| WCAG 2.2, level AA (also ISO/IEC 40500:2025) | Any user interface (web or mobile). WCAG 3.0 is still a draft |

## Privacy and data protection

Applies when the project handles any personal data. Apply the law that covers the users or the organisation; name it and mark it `verify` if unsure.

| Law | Applies when |
|---|---|
| GDPR | The organisation is established in the EU, or offers goods or services to, or monitors, people in the EU |
| UK GDPR | Same tests, for the UK |
| DPDP Act 2023 and DPDP Rules 2025 | Personal data of people in India. Core duties phase in through 2027 (mark dates `verify`); breaches go to the Data Protection Board within 72 hours |
| CCPA/CPRA, LGPD, other national laws | Users in California, Brazil or elsewhere; look them up |

Principles to design in whatever the law: collect the minimum data needed, state the purpose, get consent where required, let users access, correct and delete their data, set retention limits, and plan breach notification.

## Operations

| Practice | Applies when |
|---|---|
| Twelve-Factor App (guideline) | Any deployed backend: config in environment, stateless processes, logs as streams |
| SBOM in SPDX (ISO/IEC 5962) or CycloneDX (ECMA-424) format | Production tier |
| Structured logging without personal data or secrets | Any deployed backend |
