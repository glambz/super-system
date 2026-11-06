# Flow: inspect

Turn a live page into an evidence-labeled DESIGN.md and a SuperDesign canvas draft. Track: `ui` only. No gates.

Invocation: `/super-system inspect <url> [page-type]`. Page types: `landing-page`, `dashboard`, `pricing`, `authentication`, `settings`, `product-detail`, `checkout`; otherwise a short descriptive slug. If omitted, infer it from the URL and the page content.

1. **Scope.** Inspect the given URL deeply. Follow same-origin links only when needed to understand the page type, its navigation, slide-out panels or shared dialogs. Don't crawl unrelated sections.
2. **Crawl.** Scouts drive a real browser at 1440 and 390 px wide and record computed styles, type scale, line-height, letter-spacing, colors, radii, container widths, animation timings and interaction states.
3. **Label the evidence.** Tag every token and rule with the inspect labels in `references/design-md-template.md`.
4. **Reconstruct on canvas.** Author interactive HTML/CSS drafts (desktop and mobile) and upload them following the upload steps under "Explore options" in `references/track-ui.md`. Record the URLs.
5. **Write DESIGN.md.** Use the inspect variant of the template, at the `inspect` location under "Spec artifact" in `references/track-ui.md`, merging into any existing entry.
6. **Check.** A reviewer checks every label in every mode: each `[Measured]` value must trace to recorded evidence, each `[Observed]` to a described behavior, and anything unsupported is relabeled `[Inferred]`. Workflow mode only scales how much is re-measured on the live page: full = every token; normal = every color and type token; economy = colors plus display and body type. Confirm the canvas drafts render.
7. **Report.** As in SKILL.md, including the DESIGN.md path, the canvas links, and the counts per evidence label.
