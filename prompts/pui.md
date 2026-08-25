# CAREERPILOT AI
# PHASE 15 — MODERN APPLICATION UI & CONSOLIDATION AUDIT
# REPORT ONLY — NO IMPLEMENTATION
#
# This phase begins ONLY after Phase 14 has been completed and verified.
#
# IMPORTANT:
# This is an AUDIT and ARCHITECTURE DESIGN phase.
#
# DO NOT modify application source code.
# DO NOT redesign pages yet.
# DO NOT delete files.
# DO NOT introduce React.
# DO NOT introduce Components V2.
# DO NOT change business logic.
#
# The objective is to understand the COMPLETE application as one cohesive
# application and produce the implementation blueprint for the next
# modernization phase.
#
# ================================================================
# 1. APPLICATION DIRECTION
# ================================================================
#
# CareerPilot AI should no longer feel like:
#
#     landing page
#         +
#     collection of independent pages
#
# It should become:
#
#     ONE COHESIVE APPLICATION
#     with a consistent application shell
#     clear navigation
#     unified visual language
#     consistent components
#     and a coherent user workflow.
#
# The goal is a polished, modern, professional college-level application.
#
# It should NOT be treated as a commercial SaaS product.
#
# Do NOT introduce:
#
# - monetization concepts
# - subscription concepts
# - pricing
# - account/billing systems
# - commercial growth features
# - enterprise architecture
# - unnecessary product-management abstractions
#
# The focus is:
#
#     MODERN UI
#     CLEAN ARCHITECTURE
#     GOOD UX
#     CONSISTENT DESIGN
#     LOW DUPLICATION
#     STREAMLIT BEST PRACTICES
#     CLEAN UI / BUSINESS-LOGIC BOUNDARIES
#
# ================================================================
# 2. LANDING PAGE DECISION
# ================================================================
#
# The current landing page is NO LONGER the desired application home
# experience.
#
# The intended direction is:
#
#     REMOVE LANDING PAGE AS THE APPLICATION HOME EXPERIENCE.
#
# The application should open directly into the actual CareerPilot
# application.
#
# Do NOT delete landing.py yet.
#
# First audit:
#
# - where landing.py is referenced
# - whether it is the default page
# - whether session state depends on it
# - whether navigation points to it
# - whether documentation references it
# - whether business logic depends on it
# - whether reusable components exist inside it
#
# Determine the safest final state:
#
# A. DELETE landing.py
# B. CONVERT landing.py into an application home page
# C. REPLACE it with a new application home page
# D. RETAIN it separately
#
# Choose based on repository evidence.
#
# Do NOT choose based only on aesthetics.
#
# Do NOT delete anything during this phase.
#
# ================================================================
# 3. APPLICATION EXPERIENCE
# ================================================================
#
# The intended structure is approximately:
#
#                    CAREERPILOT AI
#                          │
#                  APPLICATION SHELL
#                          │
#          ┌───────────────┼────────────────┐
#          │               │                │
#       Sidebar         Page Header       Content
#          │
#          ├── Home
#          ├── Resume
#          ├── Job Description
#          ├── Match Results
#          ├── Resume Optimization
#          ├── Career Readiness
#          ├── Interview
#          ├── Mock Interview
#          ├── Jobs
#          └── Toolkit
#
# This is only a starting hypothesis.
#
# Audit the actual repository and determine the correct information
# architecture.
#
# Do not blindly use the list above.
#
# ================================================================
# 4. APPLICATION SHELL
# ================================================================
#
# Audit whether the application should have:
#
# - persistent sidebar
# - application logo
# - application name
# - navigation groups
# - active page state
# - page header
# - contextual actions
# - responsive sidebar behavior
# - mobile navigation
# - consistent content width
# - consistent page padding
#
# The shell should be shared.
#
# DO NOT duplicate shell HTML across pages.
#
# Preferred architecture:
#
#     app.py
#        │
#        ├── st.set_page_config()
#        ├── global CSS
#        ├── st.navigation()
#        └── page.run()
#
# Streamlit's native:
#
#     st.navigation()
#     st.Page()
#
# remains the preferred routing architecture.
#
# DO NOT introduce a second router.
#
# ================================================================
# 5. SIDEBAR AUDIT
# ================================================================
#
# Audit the current navigation.
#
# Determine:
#
# - every page
# - page purpose
# - current label
# - current icon
# - current order
# - whether the page should be visible
# - whether pages should be grouped
# - whether some pages are secondary tools
# - whether some pages should be hidden from primary navigation
#
# Possible grouping:
#
#     WORKSPACE
#       Home
#       Resume
#       Job Match
#
#     IMPROVE
#       Resume Optimization
#       Career Readiness
#
#     PRACTICE
#       Interview
#       Mock Interview
#
#     EXPLORE
#       Jobs
#       Toolkit
#
# This is ONLY a hypothesis.
#
# Do not implement it until repository analysis supports it.
#
# ================================================================
# 6. SIDEBAR DESIGN PRINCIPLES
# ================================================================
#
# The sidebar should be:
#
# - compact
# - clean
# - calm
# - easy to scan
# - clearly active
# - keyboard accessible
# - responsive
# - visually consistent
#
# Avoid:
#
# - excessive borders
# - giant navigation items
# - unnecessary gradients
# - emoji icons
# - decorative noise
# - duplicate navigation systems
# - custom clickable HTML replacing native navigation
#
# Prefer:
#
#     st.navigation()
#     st.Page()
#
# Use custom presentation only where it does not replace native
# navigation semantics.
#
# ================================================================
# 7. COMPLETE UI DUPLICATION AUDIT
# ================================================================
#
# Perform a repository-wide duplication audit.
#
# Search for repeated:
#
# - HTML strings
# - CSS declarations
# - card structures
# - headings
# - page headers
# - buttons
# - badges
# - score displays
# - job cards
# - metric cards
# - section titles
# - progress displays
# - empty states
# - error states
# - success states
# - warning states
# - navigation controls
# - upload containers
# - comparison cards
# - interview question cards
# - recommendation cards
# - AI output cards
#
# Do NOT only search for identical strings.
#
# Identify SEMANTIC duplication.
#
# Example:
#
#     render_score()
#     render_circular_score()
#     local_score_card()
#     score_html()
#
# may represent the same conceptual UI pattern.
#
# Create a duplication matrix:
#
# | Pattern | Locations | Existing Component | Duplicate Count | Recommendation |
# |---------|-----------|--------------------|-----------------|----------------|
#
# For every repeated pattern determine:
#
#     KEEP
#     CONSOLIDATE
#     REFACTOR
#     DELETE
#     PAGE-SPECIFIC
#
# ================================================================
# 8. COMPONENT INVENTORY
# ================================================================
#
# Create a complete inventory of:
#
#     ui/components.py
#
# and any remaining UI helper modules.
#
# For every component record:
#
# - name
# - purpose
# - inputs
# - outputs
# - pages using it
# - whether it contains business logic
# - whether it uses st.html()
# - whether it uses native Streamlit
# - whether styling is token-based
# - whether it is actually reusable
# - whether its API is coherent
# - whether another component duplicates it
#
# Classify each component:
#
#     GOOD COMPONENT
#     DUPLICATE
#     OVER-ABSTRACTION
#     UNDER-ABSTRACTION
#     PAGE-SPECIFIC
#     SHOULD BE DELETED
#
# Do not consolidate everything automatically.
#
# The goal is a SMALL and COHERENT component system.
#
# ================================================================
# 9. STREAMLIT CUSTOM COMPONENT / COMPONENTS V2 AUDIT
# ================================================================

This audit MUST NOT assume that native Streamlit is always sufficient.

It also MUST NOT assume that Components V2 is required.

The decision must be evidence-based.

Use the CURRENT official Streamlit documentation as the primary
authority for custom-component architecture and recommendations.

Evaluate the current application and the planned modern UI against
the capabilities of:

    1. Native Streamlit widgets
    2. st.html()
    3. ui/components.py
    4. Streamlit Components V2
    5. Components V2 with Pure TypeScript
    6. Components V2 with React + TypeScript

For each major UI requirement determine:

- Can native Streamlit implement it cleanly?
- Can st.html() implement the presentation without JavaScript?
- Does it require client-side state?
- Does it require browser-side interaction?
- Does it require JavaScript?
- Does it require bidirectional communication?
- Does it require multiple frontend callbacks?
- Does it require persistent frontend state?
- Does it require complex event handling?
- Does it require advanced animations or interactions?
- Does it require a third-party frontend library?
- Would implementing it natively create brittle workarounds?
- Would a custom component materially improve maintainability?

IMPORTANT:

Do not introduce Components V2 merely because it is newer.

Do not reject Components V2 merely because the application currently
works with native Streamlit.

Use the actual requirements.

Streamlit's CURRENT official documentation MUST be consulted before
making the architectural recommendation.

The report must explicitly classify each candidate interaction as:

    NATIVE STREAMLIT
    ST.HTML
    COMPONENTS V2 — PURE TYPESCRIPT
    COMPONENTS V2 — REACT + TYPESCRIPT
    UNKNOWN

For every COMPONENTS V2 recommendation explain:

- exact UI requirement
- why native Streamlit is insufficient
- why st.html() is insufficient
- whether bidirectional communication is required
- whether persistent frontend state is required
- whether JavaScript is required
- whether React is actually required
- whether Pure TypeScript would be sufficient
- expected architectural complexity
- maintenance implications

Do NOT implement Components V2 in this phase.

If Components V2 is recommended:

    DOCUMENT THE REQUIREMENT
    DOCUMENT THE REASON
    DOCUMENT THE RECOMMENDED APPROACH
    STOP THAT PART OF THE PLAN FOR APPROVAL

Do not silently introduce a frontend framework.

# ================================================================
# 10. REACT + TYPESCRIPT FEASIBILITY AUDIT
# ================================================================

React MUST be treated as an architectural option, not a forbidden
technology.

Evaluate React only where a custom Streamlit Component V2 is actually
being considered.

Use the CURRENT official Streamlit documentation to determine whether
React + TypeScript is appropriate for the identified component.

Evaluate:

- UI complexity
- state complexity
- number of interactive elements
- component-local state
- event handling
- frontend composition
- reusable frontend logic
- third-party JavaScript libraries
- animation requirements
- drag/drop requirements
- rich editors
- complex visualizations
- keyboard interactions
- browser APIs
- accessibility requirements
- bidirectional communication
- frontend testing requirements

Compare:

    Native Streamlit
        vs
    Components V2 + Pure TypeScript
        vs
    Components V2 + React + TypeScript

Do NOT choose React simply because:

- it looks modern
- it is popular
- it is easier to make attractive UIs
- another developer prefers React
- Streamlit CSS is inconvenient

However, do NOT reject React simply because:

- this is a Streamlit application
- the project is a college project
- the current application already works
- avoiding complexity is preferred

The decision must follow technical requirements and current Streamlit
recommendations.

Possible outcomes:

    REACT NOT REQUIRED
    PURE TYPESCRIPT IS SUFFICIENT
    REACT + TYPESCRIPT IS JUSTIFIED
    UNKNOWN

If:

    REACT + TYPESCRIPT IS JUSTIFIED

then:

    DO NOT IMPLEMENT IT IN PHASE 15.

Produce a detailed feasibility recommendation for Phase 16 and identify
exactly which components require React.

If React is NOT justified, explain why native Streamlit or Pure TypeScript
is the better engineering choice.

# ================================================================
# STREAMLIT-FIRST DOES NOT MEAN STREAMLIT-ONLY
# ================================================================

CareerPilot AI should follow Streamlit's recommended architecture.

The default preference is:

    Native Streamlit
        ↓
    st.html()
        ↓
    Components V2 / Pure TypeScript
        ↓
    Components V2 / React + TypeScript

BUT this is a decision hierarchy, NOT a prohibition.

Move to the next level only when the requirements justify it.

Never introduce frontend complexity for aesthetic reasons alone.

Never avoid frontend complexity when the requirements genuinely justify it.

Always prefer the simplest architecture that fully satisfies the
requirements.

Always verify the decision against CURRENT official Streamlit
documentation before implementation.

If official Streamlit guidance has changed since this document was written,
follow the current official guidance rather than this document.

For architectural decisions involving React, Components V2, routing,
custom components, or Streamlit APIs:

    OFFICIAL STREAMLIT DOCUMENTATION > PERSONAL PREFERENCE

When community recommendations are considered, treat them as supporting
evidence rather than authoritative architecture rules.
# ================================================================
# 11. PAGE-BY-PAGE UX AUDIT
# ================================================================
#
# Audit every application page.
#
# For each page document:
#
# - purpose
# - primary user goal
# - primary CTA
# - secondary actions
# - inputs
# - outputs
# - information hierarchy
# - navigation relationship
# - current visual structure
# - duplicated UI
# - unnecessary UI
# - confusing UI
# - dead UI
# - inconsistent UI
# - mobile issues
# - accessibility issues
# - component opportunities
#
# Create:
#
#     docs/architecture/page-ux-audit.md
#
# with one section per page.
#
# ================================================================
# 12. APPLICATION FLOW AUDIT
# ================================================================
#
# Map the actual user journey through CareerPilot AI.
#
# Example:
#
#     Resume
#        ↓
#     Job Description
#        ↓
#     Match Results
#        ↓
#     Resume Optimization
#        ↓
#     Career Readiness
#        ↓
#     Interview
#        ↓
#     Jobs / Toolkit
#
# Determine whether this is actually the correct flow.
#
# Identify:
#
# - dead ends
# - duplicated flows
# - unnecessary page switches
# - confusing navigation
# - repeated inputs
# - repeated outputs
# - opportunities to preserve context
# - session-state dependencies
# - places where the user loses context
#
# Create:
#
#     docs/architecture/application-flow-audit.md
#
# ================================================================
# 13. APPLICATION HOME
# ================================================================
#
# Since the landing page will no longer be the application home,
# determine what the user should see when the application opens.
#
# DO NOT automatically create a generic dashboard.
#
# Determine what is genuinely useful based on existing functionality.
#
# Possible content:
#
# - current resume status
# - latest match
# - career readiness score
# - recommended next action
# - optimization progress
# - interview readiness
#
# Only include information already supported by the application.
#
# DO NOT invent features.
#
# If there is insufficient information for a meaningful dashboard:
#
# recommend a minimal workspace home.
#
# ================================================================
# 14. PAGE HEADER SYSTEM
# ================================================================
#
# Audit all page headers.
#
# Determine whether the application should have a canonical structure:
#
#     optional section label
#     H1
#     supporting description
#     optional contextual action
#
# Define:
#
# - hierarchy
# - spacing
# - maximum width
# - title scale
# - subtitle scale
# - action placement
#
# The system should support page-specific content while maintaining a
# unified visual language.
#
# ================================================================
# 15. CARD SYSTEM AUDIT
# ================================================================
#
# Audit every card.
#
# Identify:
#
# - base card
# - metric card
# - score card
# - job card
# - recommendation card
# - comparison card
# - AI output card
# - action card
# - upload card
# - interview card
#
# Determine whether these can share a common structural foundation.
#
# Preferred direction:
#
#     cp-card-base
#
# with semantic variants where justified.
#
# Do not over-generalize.
#
# ================================================================
# 16. INPUT SYSTEM AUDIT
# ================================================================
#
# Audit every input.
#
# Inventory:
#
# - file uploaders
# - text inputs
# - text areas
# - radios
# - selectboxes
# - tabs
# - buttons
# - downloads
# - forms
#
# For each determine:
#
# - purpose
# - label
# - helper text
# - validation
# - error behavior
# - empty state
# - disabled state
# - loading state
# - mobile behavior
# - accessibility
#
# Determine whether the visual framing is consistent.
#
# DO NOT replace native Streamlit inputs with fake HTML.
#
# ================================================================
# 17. BUTTON SYSTEM AUDIT
# ================================================================
#
# Create a semantic button inventory:
#
#     Primary CTA
#     Secondary
#     Tertiary
#     Destructive
#     Navigation
#     Download
#     External link
#
# Determine whether usage is consistent.
#
# Do not create multiple visually identical button systems.
#
# Prefer native Streamlit button semantics.
#
# ================================================================
# 18. ICON SYSTEM AUDIT
# ================================================================
#
# Audit:
#
#     ui/icons.py
#
# Find:
#
# - duplicated icons
# - emoji usage
# - inconsistent icon sizes
# - inconsistent visual language
# - unnecessary icons
# - missing icons
# - incorrect semantic icons
#
# Establish ONE canonical icon system.
#
# Do not introduce another icon library unless repository evidence shows
# the current system cannot satisfy the requirements.
#
# ================================================================
# 19. TYPOGRAPHY AUDIT
# ================================================================
#
# Audit all typography.
#
# Find:
#
# - arbitrary font sizes
# - arbitrary weights
# - inline font styles
# - duplicate heading classes
# - inconsistent line heights
# - inconsistent muted text
# - legacy tokens
# - page-specific typography hacks
#
# Map everything to the design-system tokens.
#
# Produce typography consolidation recommendations.
#
# ================================================================
# 20. SPACING AUDIT
# ================================================================
#
# Audit:
#
# - page padding
# - section spacing
# - card padding
# - grid gaps
# - input spacing
# - heading spacing
# - button spacing
#
# Identify arbitrary values.
#
# Determine the canonical spacing rhythm.
#
# Do NOT blindly normalize every value.
#
# ================================================================
# 21. RESPONSIVE DESIGN AUDIT
# ================================================================
#
# Inspect every page for:
#
# - desktop layout
# - tablet layout
# - mobile layout
# - columns
# - tabs
# - cards
# - sidebar
# - long text
# - score visualization
# - comparison grids
# - job cards
# - buttons
#
# Identify components that become difficult or unusable on narrow screens.
#
# Do not claim mobile support simply because st.columns exists.
#
# Analyze actual information density and layout behavior.
#
# ================================================================
# 22. ACCESSIBILITY AUDIT
# ================================================================
#
# Audit:
#
# - semantic headings
# - labels
# - keyboard navigation
# - focus behavior
# - color contrast
# - color-only meaning
# - button semantics
# - input labels
# - error messages
# - status messages
# - icon meaning
#
# Native Streamlit interaction remains the default.
#
# Do not replace accessible native widgets with custom HTML.
#
# ================================================================
# 23. CSS CONSOLIDATION AUDIT
# ================================================================
#
# Inspect:
#
#     styles/tokens.css
#     styles/base.css
#     styles/streamlit.css
#
# Find:
#
# - duplicate selectors
# - duplicate declarations
# - dead classes
# - unused tokens
# - conflicting tokens
# - page-specific hacks
# - Streamlit DOM hacks
# - unnecessary !important
# - inline styles
# - old naming
# - legacy references
#
# Produce a CSS consolidation plan.
#
# DO NOT modify CSS during this phase.
#
# ================================================================
# 24. LEGACY CSS AUDIT
# ================================================================
#
# Verify whether:
#
#     assets/style.css
#
# is removable after the previous migration phases.
#
# If it remains:
#
# identify every remaining dependency.
#
# Do not delete it during this audit.
#
# ================================================================
# 25. VISUAL LANGUAGE
# ================================================================
#
# The desired UI direction is:
#
#     modern
#     clean
#     calm
#     professional
#     focused
#     polished
#     cohesive
#
# It should feel like a well-designed modern application.
#
# Avoid:
#
# - excessive glassmorphism
# - excessive gradients
# - excessive shadows
# - oversized rounded cards
# - dashboard clutter
# - decorative animations
# - neon colors
# - unnecessary illustrations
# - emoji-heavy UI
# - visual noise
#
# Prioritize usability and hierarchy over decoration.
#
# ================================================================
# 26. MODERNIZATION PRINCIPLE
# ================================================================
#
# DO NOT redesign every page independently.
#
# First establish:
#
#     Application Shell
#           ↓
#     Navigation System
#           ↓
#     Page Header System
#           ↓
#     Typography
#           ↓
#     Spacing
#           ↓
#     Card System
#           ↓
#     Input System
#           ↓
#     Button System
#           ↓
#     Feedback System
#           ↓
#     Score / Data Visualization
#           ↓
#     Page-specific compositions
#
# This creates consistency without forcing every page into the same layout.
#
# ================================================================
# 27. DUPLICATION REDUCTION TARGET
# ================================================================
#
# After modernization, aim for ONE canonical implementation of:
#
# - application shell
# - navigation
# - icons
# - page header
# - section title
# - base card
# - score card
# - job card
# - badge
# - step tracker
# - feedback/status patterns
# - common empty states
#
# DO NOT create components for:
#
# - one-off layouts
# - trivial one-line wrappers
# - page-specific business logic
# - arbitrary abstractions
#
# ================================================================
# 28. BUSINESS LOGIC PROTECTION
# ================================================================
#
# This phase is UI/UX architecture only.
#
# DO NOT modify:
#
#     modules/*.py
#
# unless absolutely necessary to understand dependencies.
#
# Do not change:
#
# - AI prompts
# - scoring
# - matching
# - resume parsing
# - career calculations
# - interview evaluation
# - job recommendation algorithms
# - session-state semantics
#
# ================================================================
# 29. LANDING PAGE MIGRATION ANALYSIS
# ================================================================
#
# Produce an explicit recommendation:
#
#     LANDING PAGE:
#         DELETE
#         REPLACE
#         CONVERT
#         RETAIN SEPARATELY
#
# Explain:
#
# - why
# - affected files
# - navigation impact
# - default route impact
# - session-state impact
# - reusable code worth extracting
# - migration risks
#
# No deletion in this phase.
#
# ================================================================
# 30. FINAL REPORT
# ================================================================
#
# Create:
#
#     docs/architecture/phase-15-modern-ui-audit.md
#
# The report MUST contain:
#
# 1. Executive summary
# 2. Current application architecture
# 3. Current navigation architecture
# 4. Recommended information architecture
# 5. Landing-page recommendation
# 6. Application-shell recommendation
# 7. Sidebar recommendation
# 8. Complete page inventory
# 9. Complete UI duplication audit
# 10. Component inventory
# 11. Component consolidation recommendations
# 12. CSS duplication audit
# 13. Typography audit
# 14. Spacing audit
# 15. Card-system audit
# 16. Input-system audit
# 17. Button-system audit
# 18. Icon-system audit
# 19. Responsive audit
# 20. Accessibility audit
# 21. Application-flow audit
# 22. Application-home recommendation
# 23. React feasibility decision
# 24. Components V2 feasibility decision
# 25. Native Streamlit feasibility decision
# 26. Recommended final architecture
# 27. Recommended implementation sequence
# 28. Files expected to change
# 29. Files that must remain untouched
# 30. Risks
# 31. Unknowns
# 32. Technical debt
# 33. Explicit deviations from previous architecture
# 34. Proposed Phase 16
# 35. Exact acceptance criteria for Phase 16
#
# ================================================================
# 31. REQUIRED ARCHITECTURE DIAGRAM
# ================================================================
#
# Include a final architecture diagram similar to:
#
#                 CAREERPILOT AI
#                       │
#                APPLICATION SHELL
#                       │
#        ┌──────────────┼───────────────┐
#        │              │               │
#     Sidebar        Page Header      Content
#        │                              │
#        ▼                              ▼
# st.navigation()                 Native Streamlit
# st.Page()                       widgets
#        │                              │
#        └──────────────┬───────────────┘
#                       │
#                  ui/components.py
#                       │
#                     .cp-ui
#                       │
#              ┌────────┴─────────┐
#              │                  │
#         tokens.css          base.css
#              │
#              ▼
#        DESIGN SYSTEM
#
#                       +
#                  BUSINESS LOGIC
#                       │
#                    modules/
#                       │
#                AI / Parsing /
#              Matching / Jobs
#
# ================================================================
# 32. STOP CONDITIONS
# ================================================================
#
# STOP and create:
#
#     docs/architecture/PHASE-15-BLOCKER-REPORT.md
#
# if:
#
# - removing landing.py would break an unknown dependency
# - a custom router appears necessary
# - React appears necessary
# - Components V2 appears necessary
# - business logic must be changed
# - session state must be redesigned
# - the design system must be replaced
# - multiple competing component systems are required
# - repository state contradicts the documented architecture
# - the final UI cannot reasonably be achieved within the current
#   Streamlit architecture without a major architectural change
#
# DO NOT IMPLEMENT A SOLUTION.
#
# REPORT THE PROBLEM.
#
# ================================================================
# 33. IMPORTANT — NO IMPLEMENTATION
# ================================================================
#
# This phase is REPORT ONLY.
#
# Allowed:
#
# - repository inspection
# - static analysis
# - dependency analysis
# - architecture analysis
# - duplication analysis
# - UX analysis
# - CSS analysis
# - component analysis
# - documentation
#
# Forbidden:
#
# - modifying Python
# - modifying CSS
# - deleting files
# - moving pages
# - changing routing
# - changing session state
# - creating components
# - redesigning pages
#
# The output of this phase is the blueprint for Phase 16.
#
# ================================================================
# 34. SUCCESS CONDITION
# ================================================================
#
# Phase 15 is successful when we can answer, with evidence:
#
# 1. What is the final application shell?
# 2. What belongs in the sidebar?
# 3. What happens when the app opens?
# 4. What happens to landing.py?
# 5. What are the final application sections?
# 6. Which components are duplicated?
# 7. Which components should become canonical?
# 8. Which CSS rules are duplicated?
# 9. What should the design system look like?
# 10. What should be removed?
# 11. What should be consolidated?
# 12. What should remain page-specific?
# 13. Is React unnecessary?
# 14. Is Components V2 unnecessary?
# 15. What exactly should Phase 16 implement?
# 16. What files should Phase 16 change?
# 17. What files must Phase 16 NOT touch?
#
# If any of these cannot be answered confidently:
#
#     DO NOT INVENT AN ANSWER.
#
# Mark it:
#
#     UNKNOWN
#
# and explain what evidence is missing.
#
# ================================================================
# 35. FINAL INSTRUCTION
# ================================================================
#
# Treat this phase as a complete application architecture and UI audit.
#
# Do not optimize individual pages in isolation.
#
# We are moving from:
#
#     "page-by-page migration"
#
# to:
#
#     "application consolidation and modernization."
#
# The final goal is:
#
#     ONE APPLICATION
#     ONE APPLICATION SHELL
#     ONE NAVIGATION MODEL
#     ONE DESIGN LANGUAGE
#     ONE COHERENT COMPONENT SYSTEM
#     ONE INPUT SYSTEM
#     ONE ICON SYSTEM
#     ONE CSS FOUNDATION
#     MINIMAL DUPLICATION
#     ZERO UNNECESSARY LEGACY UI DEPENDENCIES
#     NATIVE STREAMLIT INTERACTION
#     CLEAN BUSINESS/UI BOUNDARIES
#
# And:
#
#     NO LANDING PAGE AS THE APPLICATION HOME.
#
# Follow these principles throughout the audit:
#
# - Prefer official Streamlit best practices.
# - Prefer native Streamlit APIs when they are sufficient.
# - Prefer simple, maintainable architecture.
# - Follow established engineering best practices.
# - Do not introduce complexity without evidence.
# - Do not create abstractions prematurely.
# - Consolidate duplication only when patterns are genuinely shared.
# - Preserve existing functionality.
# - Preserve business logic.
# - Verify assumptions against the repository.
# - Clearly identify uncertainty.
#
# Audit first.
# Report second.
# Implement later.
#
# If the architecture needs to change:
#
#     STOP.
#
# ================================================================
# END PHASE 15
# ================================================================