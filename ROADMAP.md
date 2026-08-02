# Project ATLAS Roadmap

Project ATLAS is a long-term software-engineering project focused on building a modular, local-first AI operating system and lifelong engineering partner.

Development follows semantic versioning. Each release introduces a focused capability while preserving architectural stability, backward compatibility, security boundaries, testing, and documentation.

This roadmap intentionally concentrates on realistic near-term development.

The broader purpose and long-term ambition of ATLAS are maintained separately in:

```text
docs/vision.md
docs/future_backlog.md
```

---

# Current Release

## Project ATLAS v1.0.0 — Agent Foundation

Version 1.0.0 transformed ATLAS from a command-driven assistant into a constrained, tool-using AI agent.

Current development status:

| Component | Status |
|---|---|
| Foundation | ✅ Complete |
| AI Provider Architecture | ✅ Complete |
| Local AI Support | ✅ Complete |
| Persistent Memory | ✅ Complete |
| Conversation Engine | ✅ Complete |
| Structured Logging | ✅ Complete |
| Tool Framework | ✅ Complete |
| Permission System | ✅ Complete |
| Secure Filesystem | ✅ Complete |
| Agent Foundation | ✅ Complete |
| Response Performance | 🚧 Next |
| Web Research | ⏳ Planned |
| Multi-Step Agent | ⏳ Planned |
| Semantic Memory | ⏳ Planned |
| Project Intelligence | ⏳ Planned |
| Engineering Capabilities | ⏳ Future |
| Voice Interface | ⏳ Future |
| Vision System | ⏳ Future |
| Rocket Engineering | ⏳ Future |
| Spatial Interfaces | ⏳ Long-Term |
| Robotics Platform | ⏳ Long-Term |

---

# Development Strategy

ATLAS development should progress through the following sequence:

```text
Performance
    ↓
Current Knowledge
    ↓
Reasoning and Planning
    ↓
Relevant Memory
    ↓
Project Understanding
    ↓
Engineering Capability
    ↓
Natural Interfaces
    ↓
Physical-System Integration
```

This order is intentional.

A fast assistant is more useful than a slow assistant with more features.

An informed assistant is more useful than one that confidently relies on outdated knowledge.

A bounded, verifiable agent is more valuable than an unrestricted autonomous loop.

Engineering, voice, vision, robotics, and spatial interfaces should build on a responsive and trustworthy intelligence platform.

---

# Release Principles

Every release should:

- Address one focused capability
- Solve a clear user problem
- Preserve modular architecture
- Preserve user control
- Include automated tests
- Include regression tests for corrected defects
- Include manual acceptance testing when real-model behavior is involved
- Define security and permission boundaries
- Update documentation
- Update the changelog
- Avoid claiming unfinished capabilities
- Leave the system in a stable, releasable state

Release numbers beyond the near-term roadmap should remain flexible.

Long-term ideas should not receive fixed version numbers until their architecture, scope, dependencies, and safety requirements are understood.

---

# Completed Milestones

## v0.1.0 — Foundation

Objective:

Establish the initial Python application and development environment.

Completed:

- Python project structure
- Package architecture
- Command-line interface
- Development environment
- Editable package installation
- Automated testing
- Ruff linting and formatting
- MyPy static type checking
- Git version control
- Initial documentation

Status:

✅ Complete

---

## v0.2.0 — AI Provider Architecture

Objective:

Separate ATLAS from any single model provider.

Completed:

- Model-provider abstraction
- Mock provider
- OpenAI provider
- Provider factory
- Environment-based provider configuration
- Provider-specific error handling
- Model-provider tests

Status:

✅ Complete

---

## v0.3.0 — Local AI

Objective:

Support completely local model inference.

Completed:

- Ollama integration
- Local model execution
- Ollama host configuration
- Local-provider configuration
- Offline development workflow
- Ollama provider tests

Status:

✅ Complete

---

## v0.4.0 — Persistent Memory

Objective:

Allow ATLAS to preserve explicit information across sessions.

Completed:

- SQLite memory database
- Memory records and IDs
- Memory timestamps
- Memory categories
- Source tracking
- `remember` command
- `memories` command
- `forget` command
- Memory-context injection
- Memory tests

Status:

✅ Complete

---

## v0.5.0 — Conversation Engine

Objective:

Add persistent, multi-message conversations.

Completed:

- Multiple persistent conversations
- Conversation IDs and titles
- Persistent user and assistant messages
- Conversation history
- Conversation switching
- Conversation renaming
- Automatic active-conversation restoration
- Context reconstruction
- Conversation tests

Status:

✅ Complete

---

## v0.6.0 — Structured Logging

Objective:

Make application behavior observable and diagnosable.

Completed:

- Request IDs
- Rotating local log files
- Request timing
- Startup diagnostics
- Shutdown logging
- Error logging
- Memory audit logging
- Conversation audit logging
- Configurable log levels
- Configurable log rotation
- Logging tests

Status:

✅ Complete

---

## v0.7.0 — Tool Framework

Objective:

Create a controlled and extensible execution layer.

Completed:

- Tool interface
- Tool definitions
- JSON parameter schemas
- Tool registry
- Tool executor
- Structured tool results
- Tool risk metadata
- Confirmation metadata
- Calculator tool
- Current-time tool
- Explicit tool commands
- Tool execution logging
- Tool tests

Status:

✅ Complete

---

## v0.8.0 — Permission System

Objective:

Require authorization before tools may perform protected actions.

Completed:

- Permission decision models
- Permission policy
- Allow, confirm, and deny decisions
- Risk classification
- Confirmation workflow
- Pending tool requests
- `confirm yes` command
- `confirm no` command
- Permission audit logging
- Confirmation tests

Status:

✅ Complete

---

## v0.9.0 — Secure Filesystem

Objective:

Provide scoped local file access without granting unrestricted filesystem control.

Completed:

- Scoped filesystem subsystem
- Workspace sandbox
- Secure path resolver
- Configurable allowed directories
- Directory listing
- File metadata inspection
- UTF-8 text reading
- UTF-8 text writing
- Directory creation
- Read and write limits
- Existing-file protection
- Path-traversal protection
- Shared argument validation
- Filesystem integration tests
- Filesystem documentation

Status:

✅ Complete

---

## v1.0.0 — Agent Foundation

Objective:

Transform ATLAS from a command-driven assistant into a constrained, tool-using AI agent.

Completed:

- Dedicated agent package
- Agent decision models
- Structured agent-response parser
- Dynamic tool catalog
- Dynamic agent prompt generation
- Structured model decisions
- Natural-language tool selection
- JSON-schema-constrained Ollama decisions
- Agent orchestration service
- Permission-system integration
- Tool-executor integration
- Conversation-context integration
- Persistent-memory context integration
- Model-selected confirmation workflow
- Pending agent tool requests
- Approval and denial handling
- Trusted tool-result responses
- Deterministic file-creation routing
- Deterministic directory-creation routing
- Human-readable local-time output
- Backward-compatible explicit tool commands
- Application-level agent integration
- Agent unit tests
- Agent integration tests
- 204 passing automated tests
- Agent documentation

Current execution model:

```text
User Request
    ↓
AtlasApp
    ↓
Command Detection
    ↓
Deterministic Safety Routing
    ↓
Agent Prompt Builder
    ↓
Structured Model Decision
    ↓
Decision Parser
    ↓
Tool and Argument Validation
    ↓
Permission Evaluation
    ↓
Execution or Confirmation
    ↓
Trusted Tool Result
    ↓
Conversation Storage
    ↓
User Response
```

Current limitations:

- One model-selected tool per request
- No autonomous multi-step loop
- No current web research
- No semantic memory retrieval
- No background execution
- No persistent plans
- No unrestricted shell access
- No unrestricted filesystem access
- Deterministic routing covers a limited set of recognized English requests
- Local-model response speed remains a major usability limitation

Status:

✅ Complete

---

# Current Development Cycle

## v1.1.0 — Response Performance

Objective:

Make ATLAS responsive enough for natural conversation, routine use, and future voice interaction.

The first step is to measure the current system accurately. Optimization work should be guided by profiling rather than assumptions.

### Planned Capabilities

#### Performance Measurement

- Profile end-to-end request latency
- Measure first-token latency
- Measure total-response latency
- Measure model-generation speed
- Measure prompt-construction time
- Measure conversation-context retrieval time
- Measure memory-retrieval time
- Measure permission-evaluation time
- Measure tool-execution time
- Add structured stage-level timing
- Add repeatable benchmark requests
- Add benchmark-result documentation
- Add performance regression tests

#### Streaming

- Add streamed Ollama responses
- Begin displaying output before generation is complete
- Preserve non-streaming provider compatibility
- Support interruption and cancellation
- Handle stream failures safely
- Prevent partial reasoning or structured JSON from reaching the user
- Add streaming tests

#### Prompt and Context Optimization

- Measure agent prompt size
- Reduce repeated instructions
- Reduce dynamic tool-catalog overhead
- Add token-aware conversation limits
- Avoid sending irrelevant conversation history
- Avoid sending irrelevant persistent memories
- Limit unnecessary context reconstruction
- Add configurable response-length limits
- Preserve enough context for accurate tool selection

#### Model and Provider Optimization

- Reuse Ollama HTTP connections
- Optimize Ollama keep-alive behavior
- Reduce first-request warm-up time
- Keep the selected local model loaded when appropriate
- Benchmark alternative local models
- Benchmark available quantization levels
- Compare latency, quality, memory usage, and reliability
- Preserve the provider abstraction
- Add request timeouts
- Add graceful cancellation

#### Deterministic Fast Paths

- Add deterministic calculator routing
- Add deterministic current-time routing
- Consider deterministic workspace-listing routing
- Avoid model calls for unambiguous built-in commands
- Preserve tool validation
- Preserve permission evaluation
- Preserve conversation storage
- Add positive and negative routing tests

#### Caching

- Research safe response caching
- Research tool-result caching
- Define cache invalidation rules
- Avoid caching time-sensitive information
- Avoid caching protected or personal content without clear controls
- Add cache observability
- Add cache tests before enabling caching by default

### Performance Targets

Initial targets should be treated as provisional until baseline measurements are collected.

Possible targets include:

```text
Explicit and deterministic commands:
under 1 second when no model call is required

Warm low-risk agent decisions:
first visible response within approximately 3–5 seconds

Tool-assisted requests:
no unnecessary second model-generation call

Long responses:
visible streaming output instead of a silent wait

Regression control:
measurable benchmark results recorded for each optimization
```

Performance targets may vary by model, hardware, prompt size, and request complexity.

ATLAS should report measured results honestly rather than guaranteeing unrealistic latency.

### Success Criteria

v1.1.0 is complete when:

- Request stages are measurable
- Streaming works reliably where supported
- Common deterministic requests bypass unnecessary model calls
- Agent prompts and context are smaller
- Ollama connections are reused appropriately
- Warm response latency improves measurably
- No performance optimization weakens validation or permissions
- Automated performance-related tests pass
- Manual responsiveness tests show a practical improvement
- Documentation includes before-and-after measurements

Estimated impact:

★★★★★

Status:

🚧 Next

---

# Near-Term Roadmap

## v1.2.0 — Web Research Foundation

Objective:

Allow ATLAS to answer time-sensitive questions using current and verifiable information.

ATLAS should no longer rely solely on static model knowledge when an answer may have changed.

### Planned Capabilities

- Web-search provider abstraction
- Search-provider adapter
- Registered web-search tool
- Webpage retrieval
- Readable-content extraction
- Source titles
- Source URLs
- Publication and update dates when available
- Source citations
- Source deduplication
- Source ranking
- Multi-source comparison
- Primary-source preference
- Official-documentation preference
- Authoritative-domain controls
- Search timeouts
- Page-size limits
- Content-size limits
- Search-result caching with freshness controls
- Research audit logging
- Web-research tests

### Current-Information Detection

ATLAS should recognize questions involving information that may have changed, including:

- Current office holders
- Current events
- Laws and regulations
- Software documentation
- Product information
- Standards
- Schedules
- Prices
- Research developments

Example:

```text
User:
Who is the current president?

ATLAS:
Recognizes that the answer may have changed
    ↓
Uses an approved web-search tool
    ↓
Checks an authoritative source
    ↓
Returns the current answer with a citation
```

### Research Security

Retrieved content must be treated as untrusted data.

Required protections include:

- Prompt-injection defenses
- Domain controls
- Download limits
- Timeout limits
- Content isolation
- Citation validation
- Clear source attribution
- Separation of model knowledge from retrieved information
- No automatic execution of instructions found inside webpages

### Success Criteria

v1.2.0 is complete when:

- ATLAS can identify time-sensitive questions
- Current information can be retrieved through a registered tool
- Answers include traceable citations
- Primary and authoritative sources are preferred
- Web content cannot bypass tool or permission controls
- Retrieval failures produce clear errors
- Political and current-office-holder questions are tested
- Technical-documentation research is tested
- Research behavior is documented

Estimated impact:

★★★★★

Status:

⏳ Planned

---

## v1.3.0 — Multi-Step Agent and Verification

Objective:

Allow ATLAS to complete bounded tasks requiring multiple tools.

The agent must remain constrained, observable, cancellable, and permission-controlled.

### Planned Capabilities

- Multi-step agent loop
- Configurable maximum step count
- Sequential tool execution
- Tool-result observation
- Replanning after each result
- Task-completion detection
- Final completion summary
- Failed-tool recovery
- Retry limits
- Timeout limits
- Loop detection
- Duplicate-action protection
- Agent cancellation
- Partial-completion reporting
- Agent-run identifiers
- Agent-step audit logging
- Multi-step integration tests

Example:

```text
User:

Create a folder called Rockets,
create notes.txt inside it,
and write Project Wraith into the file.
```

Planned execution:

```text
Interpret Request
    ↓
Create Directory
    ↓
Request Confirmation
    ↓
Observe Result
    ↓
Write Text File
    ↓
Request Confirmation
    ↓
Observe Result
    ↓
Verify Completion
    ↓
Return Completion Summary
```

### Safety Requirements

- Hard maximum step count
- Registered tools only
- Validation before every step
- Permission evaluation before every step
- Confirmation for every protected action
- High-risk denial
- No silent continuation after denial
- No repeated execution of completed steps
- Clear cancellation behavior
- Resource and timeout limits
- Complete audit history
- Final state verification where practical

### Success Criteria

v1.3.0 is complete when:

- ATLAS can complete a bounded multi-tool workflow
- Every tool step remains validated
- Every protected step requires confirmation
- Denial stops the workflow safely
- Duplicate actions are prevented
- Failed steps produce controlled recovery or termination
- Tasks stop when complete
- Agent loops cannot run without a hard bound
- Multi-step behavior is covered by integration tests

Estimated impact:

★★★★★

Status:

⏳ Planned

---

## v1.4.0 — Semantic Memory

Objective:

Retrieve information according to relevance rather than relying primarily on recent context.

Semantic memory should improve both intelligence and response performance.

### Planned Capabilities

- Local embedding provider
- Embedding generation
- Vector storage
- Semantic similarity search
- Hybrid keyword and semantic retrieval
- Memory relevance ranking
- Recency weighting
- Source weighting
- Confidence metadata
- Project-specific retrieval
- Duplicate-memory detection
- Near-duplicate detection
- Memory correction
- Memory consolidation
- Memory review
- Memory editing
- Memory deletion
- Context-budget controls
- Semantic-memory tests
- Privacy-focused memory controls

### Retrieval Model

```text
User Request
    ↓
Determine Relevant Topics
    ↓
Search Memory
    ↓
Rank Results
    ↓
Select Only Relevant Memories
    ↓
Build Model Context
```

### Success Criteria

v1.4.0 is complete when:

- Relevant memories can be retrieved semantically
- Irrelevant memories are excluded from prompts
- Duplicate memories can be identified
- Memory sources remain traceable
- The user can review and remove stored memories
- Semantic retrieval improves context quality
- Prompt size remains controlled
- Memory behavior remains local-first by default
- Automated retrieval and privacy tests pass

Estimated impact:

★★★★☆

Status:

⏳ Planned

---

## v1.5.0 — Project Intelligence and Completion Estimates

Objective:

Allow ATLAS to understand long-running projects as structured systems of goals, tasks, dependencies, risks, resources, and deadlines.

### Planned Capabilities

#### Project Records

- Project names and descriptions
- Goals
- Requirements
- Constraints
- Assumptions
- Milestones
- Deadlines
- Risks
- Files
- Conversations
- Memories
- Decisions
- Status history

#### Task Management

- Task creation
- Subtasks
- Dependencies
- Blockers
- Priorities
- Status
- Deadlines
- Required materials
- Required approvals
- Progress tracking
- Suggested next actions
- Critical-path identification

#### Completion Estimates

- Individual task-duration estimates
- Optimistic completion estimates
- Expected completion estimates
- Pessimistic completion estimates
- Confidence ranges
- Deadline-completion probability
- Historical-duration learning
- User-pace learning
- Supplier lead-time tracking
- Schedule-drift warnings
- Automatic recalculation after progress or scope changes

#### Integration

- GitHub Issues integration
- GitHub Projects integration
- Repository status summaries
- Milestone tracking
- Calendar integration
- Project status reports
- Weekly progress summaries

Example future interaction:

```text
User:
How long until Wraith is finished?

ATLAS:
Estimated completion: 3–5 weeks

Critical remaining work:
- Avionics integration
- Recovery testing
- Ground deployment test
- Final flight-readiness review

Primary schedule risk:
Recovery-system testing

Confidence:
Moderate
```

### Success Criteria

v1.5.0 is complete when:

- Projects can be represented structurally
- Tasks and dependencies can be tracked
- Blockers can be identified
- Completion estimates include uncertainty
- Estimates update when progress changes
- ATLAS can explain the basis of an estimate
- GitHub project information can be linked safely
- Project status can be summarized accurately
- Project data remains user-controlled

Estimated impact:

★★★★★

Status:

⏳ Planned

---

# Medium-Term Capability Directions

The following capabilities are important but are not yet assigned fixed release numbers.

Their ordering may change as ATLAS develops.

---

## Scientific and Code Execution

Potential direction:

- Sandboxed Python execution
- Resource limits
- Time limits
- Package allowlists
- Data analysis
- Plot generation
- Numerical methods
- Engineering calculations
- Reproducible scripts
- Safe artifact creation
- Explicit execution approval

Code execution should not begin until isolation, permission, resource-limit, and audit requirements are defined.

---

## Personal Knowledge System

Potential direction:

- Local document indexing
- PDF understanding
- Source-linked answers
- Local semantic search
- Document metadata
- Version comparison
- Personal knowledge graphs
- Project-linked documents
- Document permissions
- Encrypted local storage

---

## Voice Interface

Potential direction:

- Speech recognition
- Speech synthesis
- Streaming conversation
- Push-to-talk
- Wake-word detection
- Interruption handling
- Offline speech options
- Voice privacy controls
- Physical microphone controls
- Multiple languages

Voice work should build on the response-performance milestone so the interaction feels natural.

---

## Vision System

Potential direction:

- Image understanding
- Screenshot analysis
- OCR
- Diagram interpretation
- Plot interpretation
- Engineering-drawing analysis
- Camera support
- Visual tool selection
- Visual inspection
- Vision-specific privacy and permission controls

---

## Desktop Automation

Potential direction:

- Approved application launching
- Window discovery
- Keyboard and mouse control
- Screenshot-based state verification
- File interaction
- CAD application integration
- Development-tool integration
- Application allowlists
- Strong confirmation requirements
- Emergency cancellation
- Complete audit logging

---

## Engineering Assistant

Potential direction:

- Unit-aware calculations
- Dimensional analysis
- Scientific computing
- MATLAB integration
- CAD assistance
- Simulation support
- Design reviews
- Requirement tracking
- Trade studies
- Data analysis
- Failure-mode analysis
- Manufacturing planning
- Engineering reports

Engineering functionality should clearly identify assumptions, limits, sources, and uncertainty.

---

## Manufacturing Assistant

Potential direction:

- Manufacturing-method comparison
- Bills of materials
- Cost estimates
- Lead-time estimates
- Procurement lists
- Cutting lists
- Composite layup schedules
- Cure schedules
- Assembly instructions
- Inspection plans
- Quality-control records
- Inventory tracking
- Revision control

Machine control should remain deferred until deterministic safety layers and physical emergency controls exist.

---

## Rocket Engineering Suite

Potential direction:

- OpenRocket integration
- Vehicle configuration tracking
- Stability analysis
- Motor comparison
- Recovery analysis
- Flight simulation
- Launch checklists
- Telemetry ingestion
- Sensor synchronization
- Simulation comparison
- Anomaly detection
- Post-flight diagnostics
- Flight reports
- Real-time monitoring
- Onboard advisory systems

Rocket integration should progress through:

```text
Ground-Based Analysis
    ↓
Post-Flight Diagnostics
    ↓
Live Telemetry Monitoring
    ↓
Advisory Warnings
    ↓
Embedded Advisory Runtime
```

Direct model control of flight-critical hardware is not a near-term goal.

---

## Automation and Scheduling

Potential direction:

- One-time tasks
- Recurring tasks
- Conditional monitoring
- Scheduled summaries
- Project reminders
- Research refreshes
- Retry controls
- Notification policies
- Persistent automation state
- Permission-aware scheduling
- Audit history

---

## Companion Experience

Potential direction:

- Long-term conversational continuity
- Goal awareness
- Milestone recognition
- Progress celebration
- Communication-style adaptation
- Reflection support
- Work mode
- Companion mode
- Engineering mode
- Personality controls
- Memory transparency
- Healthy interaction boundaries

ATLAS should support the user’s life and relationships rather than attempting to replace them.

---

# Long-Term Direction

The following areas remain intentionally unscheduled.

They belong to the long-term vision and future backlog until their dependencies, risks, and architectures are better understood.

---

## Spatial Interfaces

Potential direction:

- Augmented-reality interfaces
- Mixed-reality interfaces
- Spatial dashboards
- Three-dimensional CAD inspection
- Digital-twin visualization
- Gesture-controlled engineering models
- Projection-based displays
- Volumetric displays
- Future holographic interfaces

Spatial interfaces should remain presentation layers connected to the same ATLAS intelligence platform.

---

## Robotics

Potential direction:

- Sensor integration
- Robot-state monitoring
- High-level task planning
- Simulation
- Diagnostics
- Laboratory assistance
- Manufacturing assistance
- Mobile platforms
- Manipulators
- Safety interlocks
- Emergency stops
- Hardware watchdogs
- Deterministic low-level control

ATLAS may provide high-level coordination, but real-time motor control should remain inside dedicated deterministic systems.

---

## Embedded and Onboard Systems

Potential direction:

- Lightweight embedded runtime
- Offline operation
- Edge-model support
- Telemetry processing
- Sensor-health monitoring
- Diagnostic reporting
- Ground-station communication
- Strict CPU, memory, and power budgets
- Watchdogs
- Fail-safe behavior
- Hardware-in-the-loop testing

For rockets and other safety-critical systems, early onboard use should remain advisory and separate from deterministic flight control.

---

## Multi-Device Platform

Potential direction:

- Desktop client
- Mobile client
- Web client
- Ground-station client
- Embedded client
- Wearable client
- Secure synchronization
- Device authentication
- Encrypted communication
- Device-specific permissions
- Offline operation
- Session handoff

---

## Plugin Ecosystem

Potential direction:

- Dynamic plugin discovery
- Plugin manifests
- Plugin permissions
- Plugin isolation
- Plugin signatures
- Plugin versioning
- Compatibility checks
- Trusted publishers
- Local plugin registry
- Optional community ecosystem

---

# Long-Term Vision

Project ATLAS is intended to become a persistent AI platform capable of supporting years of continued development.

A mature ATLAS may eventually:

- Understand long-running projects
- Retrieve current information
- Manage tasks and schedules
- Estimate completion times
- Assist with engineering analysis
- Support CAD and rendering
- Assist manufacturing
- Analyze rocket telemetry
- Diagnose test and flight anomalies
- Communicate by voice
- Interpret images and video
- Display spatial engineering models
- Operate across multiple devices
- Support embedded and robotic systems
- Provide meaningful personal continuity

These ideas are preserved in:

```text
docs/vision.md
docs/future_backlog.md
```

They are not current promises or fixed release commitments.

---

# Development Principles

Every release follows the same engineering philosophy:

- Architecture before spectacle
- Performance before unnecessary breadth
- Current information before confident outdated answers
- Verification before autonomy
- Advisory roles before physical control
- One focused capability per milestone
- Backward-compatible evolution where practical
- Comprehensive automated testing
- Explicit security boundaries
- Thorough documentation
- Versioned releases
- Continuous integration
- Manual acceptance testing
- Clear deferred scope
- Local-first operation where practical
- User authority over every meaningful action

This incremental approach ensures ATLAS remains maintainable as it grows from a command-line agent into a broader AI operating platform.

---

# Roadmap Governance

A capability should enter the official roadmap only when:

1. It supports the ATLAS mission.
2. It solves a clear problem.
3. Its architectural dependencies are understood.
4. Its security boundaries are understood.
5. Its permission requirements are understood.
6. Its failure behavior can be defined.
7. It can be tested.
8. It can be divided into concrete implementation issues.
9. It is likely to enter active development within the foreseeable future.
10. It is more valuable than improving an existing weak capability.

Ideas that do not yet meet these conditions should remain in:

```text
docs/future_backlog.md
```

---

# Relationship to Other Documents

Each project document has a separate purpose.

| Document | Purpose |
|---|---|
| `README.md` | Describes what ATLAS currently is and how to use it |
| `ROADMAP.md` | Defines realistic upcoming development |
| `CHANGELOG.md` | Records completed changes |
| `ARCHITECTURE.md` | Explains the current system design |
| `docs/vision.md` | Defines why ATLAS exists and what it should become |
| `docs/future_backlog.md` | Preserves unscheduled and exploratory ideas |
| `docs/development.md` | Defines implementation and release practices |
| `docs/agent.md` | Documents the current agent subsystem |

The roadmap should remain realistic.

The vision may remain ambitious.

The backlog may remain expansive.

The changelog must remain historical.

---

# Release Sequence

## Completed

| Version | Milestone | Status |
|---|---|---|
| v0.1.0 | Foundation | ✅ Complete |
| v0.2.0 | AI Provider Architecture | ✅ Complete |
| v0.3.0 | Local AI | ✅ Complete |
| v0.4.0 | Persistent Memory | ✅ Complete |
| v0.5.0 | Conversation Engine | ✅ Complete |
| v0.6.0 | Structured Logging | ✅ Complete |
| v0.7.0 | Tool Framework | ✅ Complete |
| v0.8.0 | Permission System | ✅ Complete |
| v0.9.0 | Secure Filesystem | ✅ Complete |
| v1.0.0 | Agent Foundation | ✅ Complete |

## Near-Term

| Version | Milestone | Status |
|---|---|---|
| v1.1.0 | Response Performance | 🚧 Next |
| v1.2.0 | Web Research Foundation | ⏳ Planned |
| v1.3.0 | Multi-Step Agent and Verification | ⏳ Planned |
| v1.4.0 | Semantic Memory | ⏳ Planned |
| v1.5.0 | Project Intelligence and Completion Estimates | ⏳ Planned |

## Future Capability Areas

| Capability Area | Status |
|---|---|
| Scientific and Code Execution | ⏳ Future |
| Personal Knowledge System | ⏳ Future |
| Voice Interface | ⏳ Future |
| Vision System | ⏳ Future |
| Desktop Automation | ⏳ Future |
| Engineering Assistant | ⏳ Future |
| Manufacturing Assistant | ⏳ Future |
| Rocket Engineering Suite | ⏳ Future |
| Automation and Scheduling | ⏳ Future |
| Companion Experience | ⏳ Future |
| Spatial Interfaces | ⏳ Long-Term |
| Robotics | ⏳ Long-Term |
| Embedded and Onboard Systems | ⏳ Long-Term |
| Multi-Device Platform | ⏳ Long-Term |
| Plugin Ecosystem | ⏳ Long-Term |

---

**Current Release:** **v1.0.0 — Agent Foundation**

**Next Milestone:** **v1.1.0 — Response Performance**

**Long-Term Vision:** `docs/vision.md`

**Future Ideas:** `docs/future_backlog.md`