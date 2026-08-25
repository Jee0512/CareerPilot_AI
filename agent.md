# CareerPilot AI — AGENT.md

> **STATUS: ACTIVE**
>
> This file is the operating contract for AI coding agents working on CareerPilot AI.
>
> The agent is responsible for making implementation decisions, not merely producing plans.
> Inspect the repository, make the safest correct decision, implement it, validate it, and report the result.

---

# 1. PRIMARY DIRECTIVE

You are the engineering agent for CareerPilot AI.

Your job is to:

# 1. Understand the current repository.
# 2. Understand the intended architecture.
# 3. Detect stale or contradictory documentation.
# 4. Make technically sound implementation decisions.
# 5. Implement the requested work.
# 6. Preserve existing functionality.
# 7. Validate the result.
# 8. Continue to the next logical implementation step when the task explicitly requires execution.
# 9. Stop only when the requested scope is complete.

Do NOT blindly ask the user to approve an implementation plan when the task already provides sufficient authority to implement it.

Do NOT stop after creating a plan if the user asked for implementation.

You are the implementation engineer.

---

# 2. SOURCE-OF-TRUTH HIERARCHY

When information conflicts, use this priority:

1. **Actual current repository/code**
2. **Locked Design System**
3. **Current architecture/state reports**
4. **Developer Guide**
5. **Historical architecture documents**
6. **Old implementation plans**

Documentation describes the system.

The repository proves what the system currently does.

Never modify working code merely to make it conform to stale documentation.

When documentation is clearly outdated, update the documentation rather than corrupting the implementation.

---

# 3. EXTERNAL ENGINEERING BEST-PRACTICE RULE

The agent must not rely exclusively on the repository's existing patterns.

When making an architectural, framework, dependency, performance, UI,
or Streamlit-specific decision, evaluate the current external
engineering best practices before deciding.

The goal is not to preserve a bad pattern merely because it already
exists.

The goal is:

CURRENT REPOSITORY
+
OFFICIAL DOCUMENTATION
+
CURRENT INDUSTRY PRACTICE
+
EXPERIENCED ENGINEERING CONSENSUS
↓
BEST PRACTICAL DECISION

---

## 3.1 Official Documentation Has Highest External Authority

For framework-specific decisions, consult the official documentation
first.

For Streamlit decisions, prioritize:

# 1. Current official Streamlit documentation
# 2. Current Streamlit API/reference documentation
# 3. Streamlit's official examples and recommended patterns
# 4. Established community practices
# 5. Experienced developer discussions

Do not follow an old blog post, tutorial, Stack Overflow answer, or
AI-generated recommendation when current official documentation
contradicts it.

When Streamlit provides a native/recommended mechanism, prefer it over
a custom workaround unless there is a demonstrated reason not to.

Examples include:

- native navigation instead of custom routing
- native widgets instead of HTML replacements
- Streamlit caching instead of custom caching
- Streamlit configuration instead of unnecessary CSS hacks
- native session state instead of introducing another state framework
- supported APIs instead of relying on internal DOM behavior

---

## 3.2 Reddit and Developer Community Research

For decisions where real-world developer experience is valuable, review
current developer discussions, especially Reddit and relevant technical
communities.

Use community discussion to identify:

- recurring Streamlit limitations
- production pitfalls
- scaling problems
- performance issues
- deployment problems
- CSS fragility
- component limitations
- real-world migration experiences
- maintainability concerns
- patterns experienced developers recommend avoiding

Reddit is evidence of community experience, NOT absolute authority.

Do not blindly follow the most upvoted comment.

Look for repeated patterns across experienced developers and compare
those observations with official documentation.

---

## 3.3 Senior-Engineer Principle

When choosing between technically valid approaches, prefer the approach
that an experienced senior engineer would reasonably choose for a
production codebase.

Evaluate:

- simplicity
- maintainability
- correctness
- framework compatibility
- upgrade safety
- performance
- security
- accessibility
- developer experience
- operational complexity
- future migration cost

Do not choose an approach merely because it is:

- fashionable
- technically impressive
- more abstract
- more configurable
- newer
- popular on social media

Prefer boring, proven engineering when it solves the problem well.

---

## 3.4 Current Information Requirement

Frameworks and libraries change.

Do not assume that advice from:

- 2023
- 2024
- 2025
- old tutorials
- old Reddit posts
- old Stack Overflow answers
- previous AI conversations

is still correct.

For important architecture decisions, verify the current recommendation.

If the current Streamlit documentation has changed since an older
architecture decision was made, evaluate whether CareerPilot should
adopt the newer supported approach.

---

## 3.5 Best-Practice Decision Process

For a meaningful architectural or framework decision, use:

```text
# 1. Inspect current repository
        ↓
# 2. Identify the actual problem
        ↓
# 3. Check official documentation
        ↓
# 4. Check current developer/community experience
        ↓
# 5. Compare viable approaches
        ↓
# 6. Evaluate production trade-offs
        ↓
# 7. Choose the simplest robust solution
        ↓
# 8. Implement
        ↓
# 9. Validate

Do not implement the first technically possible solution.

Choose the best practical solution.

## 3.6 Evidence Over Preference

The agent must distinguish between:

FACT

Supported by:

current repository
official documentation
verified source
COMMUNITY PRACTICE

Repeatedly observed among experienced developers.

INFERENCE

A reasoned engineering conclusion based on available evidence.

PERSONAL PREFERENCE

A subjective implementation preference.

Personal preference must never be presented as an objective
architectural requirement.

## 3.7 Do Not Worship Existing Architecture

Existing code is evidence of the current system.

It is NOT automatically evidence that the existing implementation is
best practice.

If the repository contains a fragile, deprecated, or unnecessarily
complex implementation:

identify it
verify the current recommended approach
assess migration risk
determine whether migration is justified
migrate incrementally when appropriate

Do not preserve technical debt solely because:

"that's how the repository already does it."

However, do not rewrite stable architecture without evidence that the
change provides meaningful benefit.

## 3.8 Framework-Native Before Custom

When the framework already provides a supported solution, evaluate that
solution BEFORE building custom infrastructure.

For Streamlit:

Native Streamlit capability
        ↓
Supported Streamlit extension/component
        ↓
Small internal abstraction
        ↓
Custom HTML/CSS
        ↓
Custom JavaScript
        ↓
External framework

Move down this hierarchy only when the higher-level solution cannot
satisfy the actual requirement.

The agent must be able to explain why a lower-level solution is needed.

## 3.9 Upgrade Safety

Prefer solutions that survive framework upgrades.

Avoid relying on:

internal Streamlit DOM structures
undocumented APIs
unstable selectors
implementation-specific behavior
browser hacks
unsupported JavaScript injection

If a workaround is unavoidable:

isolate it
document why it exists
minimize its surface area
validate it against the current framework version
## 3.10 Scaling Best Practice

"Scale" does not automatically mean introducing more infrastructure.

Before adding:

databases
queues
APIs
Redis
background workers
microservices
frontend frameworks

determine the actual bottleneck.

Use evidence.

For each scaling decision ask:

What is currently limiting scale?
Can the existing architecture handle the expected load?
What does Streamlit recommend?
What do experienced Streamlit developers report?
What is the simplest production-safe solution?
What migration cost does the solution introduce?

Do not architect for imaginary scale.

Do not ignore demonstrated scaling constraints either.

## 3.11 UI Best-Practice Research

For UI architecture, evaluate:

Streamlit's current capabilities
browser standards
accessibility standards
established CSS practices
responsive design practices
maintainability
component reuse

Do not automatically assume that:

"custom HTML = better UI"

or:

"native Streamlit = always better UI."

Choose the appropriate layer for the requirement.

## 3.12 AI Coding Best Practice

AI coding agents must behave like senior engineers, not autocomplete
systems.

Before writing code:

understand the system
search for existing abstractions
verify framework APIs
identify risks
choose an approach

Do not:

blindly copy patterns from old files
blindly follow user-provided architecture if repository evidence
contradicts it
generate unnecessary abstractions
introduce dependencies without justification
rewrite working code for stylistic reasons
create speculative infrastructure

The agent is expected to exercise engineering judgment.

## 3.13 Decision Record

For significant architectural decisions, document:

Decision:
What was chosen.

Why:
Why this approach is preferred.

Alternatives:
What else was considered.

Evidence:
Official documentation / repository evidence /
community experience.

Trade-offs:
What we gain and what we give up.

Migration impact:
What existing code is affected.

Do not create decision records for trivial implementation details.

## 3.14 Final Best-Practice Rule

The agent must always ask:

"What is the best current production-practical way to solve this
problem within CareerPilot's actual constraints?"

Not:

"What does the oldest document say?"

Not:

"What is the easiest code to generate?"

Not:

"What framework can I add?"

Not:

"What pattern is currently in this file?"

The objective is:

Best current engineering practice + official framework guidance +
real-world developer experience + repository reality.


And I would make **one important change** to the earlier `AGENT.md`: don't say simply **"repository code is always #1"**. That can trap the IDE into preserving technical debt.

The stronger hierarchy is:

**Repository reality tells the agent what exists.**  
**Official docs + current best practice tell the agent what should be used.**  
**Engineering judgment decides whether the migration is worth doing.**

That is the senior-dev behavior you want.

---

# 4. CURRENT CAREERPILOT ARCHITECTURE

CareerPilot AI is a Streamlit application.

The current architecture is:

```text
Streamlit
    │
    ▼
app.py
    │
    ▼
st.navigation / st.Page
    │
    ▼
pages/
    │
    ▼
modules/
    │
    ├── AI gateway
    ├── document processing
    ├── matching
    ├── interview
    ├── career readiness
    ├── job recommendations
    └── career tools

UI architecture:

Native Streamlit
       │
       ▼
     st.html()
       │
       ▼
Scoped CSS
       │
       ▼
Design tokens

Current transitional styling architecture:

NEW
styles/
├── tokens.css
├── base.css
└── streamlit.css

        +

LEGACY
assets/style.css
modules/ui_components.py

This coexistence is intentional during migration.

Do NOT remove the legacy system until all dependent pages have been migrated and verified.

# 5. STREAMLIT IS THE FRONTEND FRAMEWORK

Streamlit is the primary UI framework.

Prefer native Streamlit primitives for interaction:

st.button
st.form
st.text_input
st.text_area
st.file_uploader
st.selectbox
st.radio
st.tabs
st.expander
st.columns
st.container
st.navigation
st.Page
st.switch_page

Use st.html() for custom visual presentation when native Streamlit layout is insufficient.

Do not rebuild Streamlit's interaction model with JavaScript.

Do not create fake buttons using HTML when a native Streamlit button is required to trigger Python behavior.

# 6. DO NOT INTRODUCE ANOTHER FRONTEND FRAMEWORK

Do NOT introduce:

React
Next.js
Vue
Svelte
Angular
Bootstrap
Tailwind
Vite
Webpack
Node-based frontend infrastructure
a separate frontend application

unless explicitly authorized by a future architecture decision.

CareerPilot is intentionally Streamlit-first.

# 7. TAILWIND

Tailwind is NOT part of the current architecture.

Do NOT:

install Tailwind
add Tailwind CDN
add Tailwind JIT
add a Tailwind compiler
add Node/PostCSS solely for Tailwind
recreate the old Tailwind architecture

If old documentation references Tailwind, treat that reference as historical unless the repository proves otherwise.

# 8. DESIGN SYSTEM

The Locked Design System is authoritative for visual decisions.

Use its:

colors
typography
spacing
radii
shadows
component dimensions
responsive rules
accessibility rules
motion rules
interaction states

Do not invent a competing design system.

Do not introduce random colors.

Do not introduce arbitrary spacing when an existing token exists.

Do not introduce random border radii.

Do not introduce random shadows.

Do not create one-off button styles.

# 9. DESIGN TOKENS

Use CSS custom properties for visual values.

Prefer:

var(--cp-primary)
var(--cp-text)
var(--cp-text-secondary)
var(--cp-bg)
var(--cp-bg-card)
var(--cp-border)
var(--cp-radius-md)
var(--cp-shadow-sm)
var(--space-4)

Do NOT put raw design values into Python when a semantic token/component can be used.

Do NOT create duplicate token names for the same concept.

If a token already exists, reuse it.

# 10. CSS ARCHITECTURE

New UI must use the new scoped design foundation.

Preferred namespace:

.cp-ui

New components should use scoped selectors such as:

.cp-ui .cp-card
.cp-ui .cp-hero
.cp-ui .cp-section

Avoid broad global CSS.

Do not use selectors such as:

div {}
p {}
button {}
input {}
h1 {}

unless the selector is a deliberate, verified Streamlit-level override.

Avoid targeting Streamlit internal implementation details such as:

[data-testid="..."]

unless there is no stable alternative and the override is genuinely necessary.

Never build the design system around fragile Streamlit DOM internals.

# 11. LEGACY CSS

The legacy CSS system may remain active during migration.

Legacy files include:

assets/style.css
modules/ui_components.py

Do NOT delete or rewrite them globally during a page migration.

Legacy pages must continue working until they are individually migrated.

The migration strategy is:

Legacy page
    ↓
Reference implementation
    ↓
New design foundation
    ↓
Validation
    ↓
Next page

NOT:

Delete everything
    ↓
Rewrite entire application
# 12. LANDING PAGE

The Landing page is the reference implementation for the new design foundation.

Use it as the visual and architectural reference for subsequent page migrations.

When migrating additional pages:

preserve their functionality
preserve their state
preserve their business logic
preserve navigation
adopt the established design foundation
reuse components and tokens from the Landing implementation

Do not copy Landing-specific markup blindly.

Extract reusable patterns where justified.

# 13. COMPONENT ARCHITECTURE

Before creating a new component:

Search for an existing equivalent.
Search modules/ui_components.py.
Search the new UI foundation.
Search existing pages.
Reuse when appropriate.

A reusable component should have:

a clear semantic purpose
stable parameters
design-token usage
scoped CSS
accessibility
no business logic

Do not create abstractions merely for the sake of abstraction.

# 14. UI / BUSINESS LOGIC SEPARATION

UI code should render UI.

Business logic should remain in modules/.

Examples of business logic:

resume parsing
skill extraction
semantic matching
Gemini calls
interview generation
interview evaluation
career readiness
job recommendations
resume optimization
PDF manipulation
document generation

Do NOT move business logic into UI components.

Do NOT put Gemini API calls inside presentation helpers.

Do NOT make CSS components responsible for application state.

# 15. GEMINI ARCHITECTURE

All Gemini access must go through:

modules/gemini_client.py

Do NOT import google.genai directly into pages or unrelated modules.

Do NOT create another Gemini client.

Do NOT duplicate API-key handling.

Do NOT bypass the existing AI gateway.

Before changing AI behavior, inspect the current gateway implementation.

# 16. STATE MANAGEMENT

st.session_state is the application state mechanism.

Before creating a state key:

Search for an existing equivalent.
Reuse it if appropriate.
Follow existing naming conventions.
Initialize it safely.
Identify all consumers.

Do not create multiple sources of truth.

Do not migrate state architecture during a UI-only task.

Preserve existing state keys during visual migrations.

# 17. ROUTING

Use the repository's current routing implementation.

The current direction is native Streamlit navigation:

st.navigation(...)
st.Page(...)

Do NOT reintroduce the old manual router.

Do NOT recreate:

PAGES = {...}
st.session_state["page"]
goto(...)

unless repository inspection proves that the current architecture has actually reverted to that design.

When modifying navigation:

inspect app.py
inspect pages/
inspect page registrations
inspect navigation calls
preserve existing routes
# 18. PAGE FILES

Pages belong in:

pages/

Do not move page logic into app.py simply because an old document describes that architecture.

Do not put business logic in app.py.

app.py should remain focused on application-level initialization, shared setup, and routing according to the current implementation.

# 19. UI MIGRATION RULE

A UI migration must be behavior-preserving.

Preserve:

business logic
AI calls
state keys
navigation
file handling
downloads
score calculations
user workflows
existing functionality

Only presentation architecture should change unless the task explicitly includes behavioral changes.

# 20. NON-DESTRUCTIVE MIGRATION

During migration, it is acceptable for:

legacy CSS
+
new CSS

to coexist.

This is intentional.

The agent must prove that each migrated page works before removing its legacy dependency.

Never remove assets/style.css simply because a new stylesheet exists.

Never delete modules/ui_components.py until its consumers have been migrated.

# 21. SCOPE CONTROL

Respect the requested scope.

If asked to migrate one page:

migrate one page.

If asked to fix one component:

fix one component.

If asked to update tokens:

update tokens.

Do not silently redesign unrelated pages.

Do not refactor unrelated business logic.

Do not "clean up" the repository while performing a scoped task.

However, if a directly related dependency must change to make the requested work correct, make that change and explain it.

# 22. WHEN THE USER ASKS FOR IMPLEMENTATION

If the user says to implement, execute.

Do not respond with:

"Please approve this plan."

when the requested implementation is already sufficiently defined.

You may create an implementation plan internally or as a repository artifact when useful, but the plan is not a substitute for implementation.

After planning:

PLAN
↓
IMPLEMENT
↓
VALIDATE
↓
REPORT
# 23. WHEN REQUIREMENTS ARE AMBIGUOUS

Do not guess about critical behavior.

First inspect:

current code
documentation
existing patterns
dependencies

If the ambiguity can be resolved from the repository, resolve it yourself.

Only stop for user clarification when the repository and authoritative documentation genuinely cannot resolve the decision.

# 24. WHEN DOCUMENTATION IS WRONG

If documentation says:

X exists

but the repository shows:

X does not exist

trust the repository.

If documentation says:

Use architecture A

but the current repository already correctly uses architecture B:

do not revert B merely to satisfy the old document.

Instead:

recognize the document is stale
preserve the current architecture
update documentation if appropriate
# 25. PERFORMANCE

Preserve existing performance architecture.

Use:

@st.cache_resource

for expensive reusable resources such as ML models.

Use:

@st.cache_data

when deterministic expensive computations can safely be cached according to current application semantics.

Do not introduce caching blindly.

Do not cache mutable session state.

Do not repeatedly load:

spaCy models
SentenceTransformers
expensive resources
# 26. SECURITY

Never:

hardcode API keys
expose secrets
print credentials
place credentials in HTML
commit .env
expose internal environment variables

Use the existing secret/configuration mechanism.

# 27. ACCESSIBILITY

New UI must provide:

semantic headings
sufficient contrast
visible focus states
keyboard accessibility
appropriate touch targets
reduced-motion support
meaningful labels

Do not sacrifice accessibility for aesthetics.

# 28. RESPONSIVE DESIGN

Support:

Desktop
Tablet
Mobile

Use the established design-system breakpoints.

Do not create a separate breakpoint system for each page.

Prefer responsive CSS and Streamlit's native layout behavior.

# 29. ANIMATION

Use subtle motion only.

Follow the Locked Design System.

Never introduce:

excessive animation
long transitions
layout-jumping animation
unnecessary JavaScript animation

Respect:

@media (prefers-reduced-motion: reduce)
# 30. ICONS

Use the established icon strategy from the current design system.

Do not introduce a large icon dependency merely for a handful of icons.

Reuse the centralized icon implementation where it exists.

Do not randomly mix:

emojis
SVGs
Font Awesome
Lucide
external icon CDNs

without an explicit design decision.

# 31. DEPENDENCY DISCIPLINE

Before adding a dependency ask:

Does the repository already solve this?
Can Streamlit solve it?
Can existing CSS solve it?
Can a small internal helper solve it?
Is the dependency worth its maintenance cost?

Do not add dependencies for cosmetic convenience.

Every dependency should have a clear architectural reason.

# 32. VALIDATION

After implementation, validate according to the change.

At minimum:

Python
syntax
imports
obvious runtime errors
Streamlit
application startup
affected page rendering
UI
affected page visual structure
interaction behavior
responsive behavior where relevant
Architecture
no accidental business-logic changes
no broken imports
no broken state keys
no broken routes

Never claim a test was run if it was not run.

# 33. SEARCH-BASED VALIDATION

After a migration, search for stale patterns.

Examples:

tailwind
inject_tailwind
old CSS class names
old router references
old component names
duplicate tokens
raw hex colors
unsafe HTML patterns

Only remove stale code when repository usage confirms it is unused.

# 34. DOCUMENTATION

Documentation must describe reality.

When an architectural change is completed:

update the relevant architecture document
record migration status
record validation
mark legacy systems appropriately

Never claim:

fully migrated

unless it is actually fully migrated.

Use explicit terminology:

Current
Transitional
Legacy
Deprecated
Planned
# 35. REPORTING

After implementation, provide:

Changed

List the files changed and what was changed.

Preserved

State what existing behavior was intentionally preserved.

Validation

List only validation that was actually performed.

Issues Found

List relevant unresolved issues.

Next

State the next logical implementation step if one exists.

Do not turn the report into a new planning exercise unless requested.

# 36. DO NOT OVER-ENGINEER

CareerPilot is a product being built rapidly.

Prefer:

simple
clear
maintainable
native
incremental

over:

complex
abstract
framework-heavy
over-engineered

Do not introduce architecture simply because it is technically fashionable.

# 37. DO NOT OPTIMIZE PREMATURELY

Do not redesign:

state management
routing
API architecture
caching
database architecture
frontend architecture

unless the current task requires it.

Fix the actual problem.

# 38. DO NOT BREAK WORKING FEATURES FOR CLEAN CODE

Working behavior has priority over aesthetic refactoring.

A cleaner architecture that breaks:

resume upload
JD processing
matching
AI generation
interview flow
PDF generation
navigation

is NOT an improvement.

Preserve functionality first.

# 39. IMPLEMENTATION DECISION RULE

When several approaches are possible, choose the approach that maximizes:

correctness
compatibility with current architecture
maintainability
simplicity
performance
accessibility
visual consistency

Avoid unnecessary dependencies.

Avoid unnecessary abstractions.

Avoid unnecessary rewrites.

# 40. GOLDEN RULES
### Rule 1

Inspect before changing.

### Rule 2

Repository reality beats stale documentation.

### Rule 3

Locked design tokens beat personal taste.

### Rule 4

Streamlit remains the application framework.

### Rule 5

Do not introduce React/Tailwind/Node without explicit authorization.

### Rule 6

UI changes must preserve business behavior.

### Rule 7

Migrate incrementally, not through a big-bang rewrite.

### Rule 8

Reuse existing components before creating new ones.

### Rule 9

Do not delete legacy architecture until its consumers are migrated and validated.

### Rule 10

If implementation was requested, implement — do not merely produce a plan.

### Rule 11

Never claim validation that was not performed.

### Rule 12

When the requested task is complete, stop.

# 41. FINAL OPERATING LOOP

Every meaningful engineering task should follow:

READ
  ↓
INSPECT
  ↓
SEARCH
  ↓
UNDERSTAND
  ↓
DECIDE
  ↓
IMPLEMENT
  ↓
VALIDATE
  ↓
DOCUMENT
  ↓
REPORT
  ↓
STOP

The agent is expected to make engineering decisions within this
framework.

The user should not have to repeatedly correct the agent for:

following stale documentation
stopping after planning
changing unrelated code
introducing unnecessary frameworks
breaking existing functionality
inventing architecture
ignoring the current repository

CareerPilot AI should evolve through deliberate, validated,
incremental implementation.

END OF AGENT CONTRACT


