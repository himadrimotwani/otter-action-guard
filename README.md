# 🦦 OtterActionGuard

> **Meeting-to-Action Disambiguation & Verification Engine**  
> Turning messy multi-speaker conversational speech into verified, deterministic enterprise workflows (Jira, Slack, ERP) using Model Context Protocol (MCP).

---

## 📌 The Problem Otter.ai & Meeting Agents Face

As Otter evolves from a passive transcription tool into an **Enterprise Conversational Knowledge Engine** and active **Meeting Agent**, turning spoken words into downstream actions is one of the highest-friction technical frontiers:

1. **Tentative proposals get confused with firm commitments:**  
   When a speaker brainstorms: *"What if we split the shipment into two 25k air-freight drops?"*, naive LLMs extract this as an assigned action item, polluting Jira / ERP with phantom tasks.
2. **Conditional commitments lack prerequisite gating:**  
   Speakers frequently state: *"We can commit to delivery by Friday **only if** customs clearance completes by Tuesday."* Naive extraction ignores the prerequisite and schedules premature executions.
3. **Implicit delegation and missing owners:**  
   Passive statements (*"Someone needs to follow up with the Vietnam testing lab"*) are either lost or assigned to the wrong person without human confirmation.

---

## 💡 The Solution: OtterActionGuard

**OtterActionGuard** acts as an intelligent intermediary layer between Otter's speech transcription engine and enterprise execution tools:

```
                                  ┌────────────────────────┐
                                  │ Otter Speech Stream    │
                                  │ (Diarized Transcript)  │
                                  └──────────┬─────────────┘
                                             │
                                             ▼
                                  ┌────────────────────────┐
                                  │   Transcript Parser    │
                                  │ (Turns, Timestamps)    │
                                  └──────────┬─────────────┘
                                             │
                                             ▼
                         ┌───────────────────────────────────────┐
                         │      Action Disambiguator Engine      │
                         │  - 5-Tier Commitment Taxonomy         │
                         │  - Prerequisite & Condition Extractor │
                         │  - Confidence & Ambiguity Scoring     │
                         └───────┬───────────────────────┬───────┘
                                 │                       │
                [High Confidence / Unblocked]     [Conditional / Ambiguous]
                                 │                       │
                                 ▼                       ▼
                     ┌───────────────────────┐ ┌───────────────────────┐
                     │  Auto-Approved MCP    │ │  Otter Live Assist    │
                     │  Tool Dispatch        │ │  Clarification Prompt │
                     │  (Jira / ERP / Cal)   │ │  (In-Call Validation) │
                     └───────────────────────┘ └───────────────────────┘
```

### 1. 5-Tier Commitment Taxonomy
- **`FIRM_COMMITMENT`**: Direct first-person pledge by an authorized speaker (*"I will deliver the revised BOM by tomorrow morning"*).
- **`CONDITIONAL_COMMITMENT`**: Pledges gated on external events (*"Delivery by Friday if QA finishes audit"*).
- **`EXPLORATORY_PROPOSAL`**: Hypothetical options / brainstorming (*"What if we lowered price by 3%?"*). Filtered out of execution pipelines.
- **`DELEGATED_REQUEST`**: Tasks assigned across participants (*"Dave, please log the PO numbers in ERP"*).
- **`AMBIGUOUS_PASSIVE`**: Unowned tasks (*"Someone should look at the lab results"*). Triggering human-in-the-loop assignment.

### 2. Model Context Protocol (MCP) Integration
Translates validated commitments directly into MCP tool call specifications with execution gating (`requires_approval: true/false`).

---

## 📊 Benchmark: Naive LLM vs. OtterActionGuard

Tested across enterprise operations & supply-chain negotiation transcripts:

| Metric | Naive LLM Extraction | OtterActionGuard | Impact |
| :--- | :---: | :---: | :--- |
| **Commitment Precision** | 62.5% | **94.0%** | Eliminates false tasks |
| **Exploratory Ideas Filtered** | 0% (Extracted as tasks) | **100% Filtered** | Clean enterprise task queues |
| **Gated Prerequisite Tracking** | ❌ Ignored | **✅ Gated (2/2)** | Prevents premature shipments/tickets |
| **Unowned Tasks Flagged** | ❌ Silently dropped | **✅ Live Assist Ping** | Proactive meeting clarification |

---

## 🚀 Quickstart

OtterActionGuard requires **Python 3.9+** and has **zero third-party runtime dependencies** (built with Python standard library):

```bash
# Clone the repository
git clone https://github.com/himadrimotwani/otter-action-guard.git
cd otter-action-guard

# Run the end-to-end interactive demo
python3 demo.py

# Run test suite
python3 -m unittest discover tests
```

---

## 📁 Repository Structure

```
otter-action-guard/
├── README.md                          # Architecture, problem analysis, benchmarks
├── demo.py                            # Interactive CLI demonstration
├── requirements.txt                   # Optional dependencies
├── data/
│   └── sample_transcripts.json        # Supply chain & engineering meeting datasets
├── otter_action_guard/
│   ├── __init__.py
│   ├── models.py                      # Data models (CommitmentType, ActionStatus, MCP Payload)
│   ├── parser.py                      # Multi-speaker Otter transcript parser
│   ├── disambiguator.py               # Linguistic & semantic commitment classifier
│   ├── extractor.py                   # Main orchestration engine
│   ├── mcp_bridge.py                  # Model Context Protocol tool schema generator
│   └── evaluator.py                   # Benchmark & false-positive evaluation
└── tests/
    └── test_pipeline.py               # Unit tests (100% passing)
```

---

## 💡 About the Author
Built by [Himadri Motwani](https://github.com/himadrimotwani) (MS Information Technology candidate at RPI, May 2027).  
Specializing in **agentic LLM systems, ASR pipelines, and backend service reliability**.
