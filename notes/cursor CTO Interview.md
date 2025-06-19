---
created: 2025-06-18
tags: 
  - llm-generated
  - azure/gpt-4_1-mini
tool_version: v0.1
---

# Cursor Infrastructure and Scaling: Insights from the CTO Interview

This note summarizes key insights from a detailed interview with the CTO and co-founder of Cursor, discussing the infrastructure, scaling challenges, and incident management of Cursor's AI-assisted coding platform.

---

## Overview of Cursor's Scale and Architecture

- Cursor has scaled by a factor of 100+ in the last year.
- Handles ~100 million model calls per day on custom models.
- Processes indexing of billions of documents daily, totaling hundreds of billions over the company's lifetime.
- Infrastructure is globally distributed: East Coast (Phoenix, Virginia), London, Tokyo, and more.
- Uses a monolithic architecture with compartmentalization to isolate critical services from experimental code.

---

## Core Components

### 1. Indexing Systems
- Multiple indexing systems, including retrieval systems and large-scale indexing of code repositories.
- Uses Merkle Trees for efficient client-server state reconciliation.
- Initially used YugabyteDB for global scale but migrated to PostgreSQL (RDS) due to operational challenges.
- Encountered complex race conditions and caching bugs during scaling.

### 2. Model Inference
- Autocomplete model runs on every keystroke (~20,000 model calls per second).
- Fleet of ~2000 H100 GPUs distributed globally.
- Mix of self-hosted models and third-party providers (Anthropic, OpenAI, Google Cloud).
- Faces challenges with rate limits, cold start problems, and provider reliability.

### 3. Product Layer (Apply Model)
- Applies "apply tricks" to make model responses feel instantaneous and natural.
- Runs over large token contexts (100k-200k tokens).
- Includes streaming infrastructure for data storage, screening, and background processing.

---

## Incident Case Study: Indexing System Database Scaling

- Initial choice of YugabyteDB proved difficult to scale; switched to PostgreSQL RDS.
- Hit storage and performance limits with 22TB+ data size.
- PostgreSQL's MVCC and vacuuming caused performance degradation due to heavy update/delete workload.
- Incident response involved:
  - Removing foreign keys to reduce load.
  - Rewriting workload to reduce database pressure.
  - Migrating large tables to object storage (blob storage) to avoid database bottlenecks.
- Demonstrates the complexity of scaling distributed databases and the importance of choosing appropriate storage solutions.

---

## Challenges with Third-Party Model Providers

- Providers often have limited rate limits and reliability issues.
- Cursor runs multi-cloud and multi-provider strategies to balance load and increase reliability.
- Negotiations with providers for increased capacity are ongoing and critical.
- Cold start problems cause cascading failures during scale-up.
- Incident management includes prioritizing traffic and killing requests to protect core services.

---

## Security Considerations

- Cursor encrypts vector embeddings with keys stored on user devices.
- Ensures proprietary code remains private even if vector databases are compromised.
- Takes security seriously with multiple layers of encryption and access control.

---

## Reflections on AI and Software Development

- AI assistance is expected to increase productivity and enable tackling more complex systems.
- AI models help with mundane tasks, allowing engineers to focus on creative work.
- The role of traditional IDEs and software development tools will evolve but remain significant.
- Education in computer science remains valuable; AI augments rather than replaces human expertise.

---

## Related Notes

- [[Cursor]]
- [[Cursor CTO Interview]]

---

*This note captures the technical and operational insights shared by Cursor's CTO, providing a