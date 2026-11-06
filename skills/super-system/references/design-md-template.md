# DESIGN.md template

Every DESIGN.md (project copy, library copy, or `inspect` output) follows this structure. Locations are in `track-ui.md` under "Spec artifact".

## Inspect variant (the canonical template)

Evidence labels: `[Measured]` from computed styles, DOM geometry or stylesheets; `[Observed]` from rendered behavior, resizing or interaction; `[Inferred]` from recurring rhythms or incomplete evidence.

```markdown
---
version: "superdesign-v1"
name: "[Brand/System Name] — [Aesthetic Descriptor]"
pageType: "[landing-page | dashboard | pricing | authentication | settings | product-detail | checkout]"
sourceUrl: "[Normalized URL]"
inspectionDate: "[YYYY-MM-DD]"
superdesign:
  projectId: "<uuid>"
  canvasUrl: "https://superdesign.dev/teams/.../projects/<uuid>"
  embedCanvasUrl: "https://superdesign.dev/...#eh=..."
  drafts:
    - id: "<uuid>"
      name: "[Draft Title] · desktop"
      viewport: "1440x900"
    - id: "<uuid>"
      name: "[Draft Title] · mobile"
      viewport: "390x844"
history:                        # append-only; one entry per run that changed this file
  - date: "[YYYY-MM-DD]"
    canvasUrl: "https://superdesign.dev/..."
    note: "[what changed and why]"
evidenceSummary:
  measuredTokens: [Count]
  observedProperties: [Count]
  inferredRules: [Count]

colors:
  # Base & Surfaces
  background: "#..."            # [Measured] dominant page ground
  surface: "#..."               # [Measured] content cards & panels
  surface-dark: "#..."          # [Measured] tonal break bands
  # Typography Inks
  text-primary: "#..."          # [Measured] high-contrast body & headlines
  text-secondary: "#..."        # [Measured] supporting metadata
  # Brand & Actions
  accent-primary: "#..."        # [Measured] solid buttons & active indicators
  border-hairline: "#..."       # [Measured] 1px boundary rules
  # Semantic / Palette Roles
  accent-tint: "#..."           # [Measured] feature band wash

typography:
  display-hero:
    fontFamily: "..."           # [Measured]
    fontSize: "..."             # [Measured]
    fontWeight: ...             # [Measured]
    lineHeight: "..."           # [Measured]
    letterSpacing: "..."        # [Measured]
  body-default:
    fontFamily: "..."           # [Measured]
    fontSize: "..."             # [Measured]
    fontWeight: ...             # [Measured]
    lineHeight: "..."           # [Measured]

spacing:
  base: "8px"                   # [Inferred]
  gutter: "..."                 # [Measured]
  section-padding: "..."        # [Measured]
  content-max-width: "..."      # [Measured]

rounded:
  control: "..."                # [Measured]
  card: "..."                   # [Measured]
  pill: "9999px"                # [Measured]

components:
  button-primary:
    background: "{colors.accent-primary}"
    textColor: "#..."
    height: "..."
    padding: "..."
    radius: "{rounded.pill}"
    hoverBackground: "#..."
  card-panel:
    background: "{colors.surface}"
    radius: "{rounded.card}"
    padding: "..."
    border: "1px solid {colors.border-hairline}"
---

# [Brand Name] — [Page Type] Design Language Specification

**Source:** [Normalized URL]  
**Page Type:** `[landing-page | dashboard | pricing | ...]`  
**Inspected Date:** [YYYY-MM-DD]  
**SuperDesign Canvas:** [Clickable Canvas URL]

## 1. Evidence Classification & Provenance
- **[Measured]**: Obtained directly from computed styles, browser DOM geometry, and accessible stylesheet declarations.
- **[Observed]**: Confirmed through rendered behavior, screen resize tests, or interaction states.
- **[Inferred]**: Reconstructed from recurring structural rhythms or incomplete evidence.

## 2. Overview & Creative Philosophy
Architectural summary of visual tone, color rationing, depth philosophy, and emotional character.

## 3. Composition & Spatial Hierarchy
Detailed progression through the viewport (hero structure, density gradients, section cadences).

## 4. Colors & Surface Banding
All color roles, surface contrasts, and WCAG AA verification tagged with evidence levels.

## 5. Typography System & Micro-Details
Display and body font families, optical sizing (`opsz`), negative letter-spacing, and italic rules.

## 6. Layout, Container & Grid Geometry
Max-width caps, responsive `clamp()` padding, and responsive column split arrangements.

## 7. Component Dictionary
Exhaustive anatomies for navbars, buttons, doors, cards, and input controls.

## 8. Graphics, Materials & Elevation
Border treatments, inset shadows, scrims, blur filters, and elevation policies.

## 9. Motion, Transitions & Physics
Easing curves, UI response timings, ambient loop rules, and reduced-motion compliance.

## 10. Guardrails & Non-Negotiables
Enforceable Do's and Don'ts preventing design degradation.
```

## Build / change variant

Same structure, with these differences:
- Frontmatter `sourceUrl` and `inspectionDate` become `project: "<project name>"` and `date: "YYYY-MM-DD"`; the body header lines change the same way.
- Evidence labels are `[Decided]` (chosen at Gate 1 or set in the approved prototype) and `[Inferred]` (filled in during implementation, not explicitly chosen). Nothing is `[Measured]` unless it was measured from the running build.
- `evidenceSummary` counts `decidedTokens` and `inferredRules`.
- Per-prototype documents (`prototype-a-design.md`, …) use the same structure, one per option, until Gate 1 picks one; the chosen one becomes `DESIGN.md`.
