# UI track

Read alongside the flow file whenever the `ui` track is active. Rules already in SKILL.md (gates, modes, roles, safeguards) are not repeated here.

## Before exploring

- If config `tasteFile` is set, read it first. It overrides the defaults in this file; it never forbids proposing something new and better.
- If config `designLibrary` is set, look in `<designLibrary>/*/<page-type>/` for prior art. It is reference material, not a copy mandate.
- Consult `design-taste-frontend` (art direction), `animation` (motion), and `modern-web-guidance` (platform features).

## Purpose calibration

Match styling density to what the screen is for:
- **Utility, tasks and forms** (task lists, auth, settings): practical, fast to scan, comfortable spacing, plain styling, no decoration.
- **SaaS engines and workflows** (dashboards, data grids, multi-step tools): dense but clear; show the functional advantage.
- **Brand and editorial** (landing heroes, case studies, portfolios): expressive layout, distinctive type, purposeful motion.

## Anti-slop defaults

- No lifeless pastel gradients, cookie-cutter three-card feature rows, empty 3D blobs, or placeholder fluff copy.
- Don't default to Inter, Roboto, Arial, Open Sans or Helvetica. Pick type to match the brand (e.g. Geist, Plus Jakarta Sans, Manrope, Outfit, Satoshi, Space Grotesk, Instrument Serif, Newsreader, Fraunces), and don't limit a product to one family when a pairing serves it better.
- Generated imagery has a job on the screen; no generic stock tropes.

## Explore options

- How many options: the workflow-mode table in SKILL.md.
- Each option is an interactive HTML/CSS draft at desktop 1440×900 and mobile 390×844, with a rationale naming the requirement or existing UX weakness it solves.
- Options must differ in substance (layout model, density, type, motion), not just color.
- Upload each draft to SuperDesign: find the installed SuperDesign tool or CLI (for example `superdesign_import_design_draft` or `superdesign create-design-draft`), create or reuse one project per product, import, confirm it renders, and record the canvas URL, node URLs (`?node=…`) and preview URL. Screenshots are evidence for you, never the deliverable.
- Assets: generate with SuperDesign only when a screen needs them, store them in the project's asset folder, and label them generated.

## Spec artifact

- **Project copy (source of truth):** `docs/design/DESIGN.md`, plus `docs/design/prototype-<a|b|c>-design.md` while options are open. Use the build/change variant in `references/design-md-template.md`.
- **Library copy:** if `designLibrary` is set, copy the project's DESIGN.md (and prototype docs) to `<designLibrary>/<project-name>/<page-type>/` after Gate 1 and again at the end of the run. Never edit the library copy directly; refresh it from the project copy. Refresh means merge, as in the next bullet, never a plain overwrite.
- **`inspect` output:** `<designLibrary>/<domain>/<page-type>/DESIGN.md`, or `./design-library/<domain>/<page-type>/DESIGN.md` when `designLibrary` is not set.
- **Existing entries:** merge updates into them; never silently erase historical notes or working canvas links. Carry the existing `history:` list and notes over unchanged and append a new `history:` entry for this run.

## Implementation defaults

- Semantic HTML; native `<dialog>` and the Popover API before UI libraries.
- Tokens as CSS custom properties taken from DESIGN.md.
- Container queries, `subgrid`, `@starting-style`, `text-wrap: balance | pretty` where they fit.
- Animate `transform` and `opacity`; spring-like easing (e.g. `cubic-bezier(0.2, 0.7, 0, 1)`); staggered siblings; no heavy animation libraries; no unthrottled scroll handlers; honor `prefers-reduced-motion`.

## Verify

- Drive a real browser at 1440, 768 and 390 px wide.
- For each in-scope route: render, interact (hover, focus, forms, dialogs, navigation), read the console, watch for layout shift.
- Check text contrast with `python <skill-dir>/scripts/contrast-check.py <fg> <bg>`, where `<skill-dir>` is the folder holding this skill's SKILL.md. It exits 1 whenever normal text fails, so for large text read the printed large-text verdict, not the exit code.
- Review against the current Vercel Web Interface Guidelines via `web-design-guidelines`.

## Quality lenses

1. **Visual fidelity:** matches DESIGN.md tokens, type and spacing; contrast ≥ 4.5:1 for body text, ≥ 3:1 for large text.
2. **Functional behavior:** routes, links, forms, validation, error / empty / loading states.
3. **Responsive:** correct at 1440 / 768 / 390; touch targets ≥ 44px; no horizontal overflow.
4. **Accessibility:** full keyboard use, visible `:focus-visible`, correct semantics and ARIA, `prefers-reduced-motion` respected.
5. **Technical:** no console errors or warnings, CLS 0, assets load, animation stays smooth.
