# Technique: UI Quality

Source: design-taste-frontend, web-design-guidelines, modern-web-guidance

Apply to every UI task and review:

1. **Design tokens and theme:** follow `DESIGN.md` tokens, typography, spacing, and corner-radius scale strictly. Keep one consistent theme (no random light/dark inversions, unrequested gradients, or extra fonts).
2. **Semantic HTML & native features:** use semantic elements (`<main>`, `<nav>`, `<button>`, `<dialog>`, Popover API) and modern CSS before JS or new UI packages. Never add UI dependencies without approval.
3. **Keyboard & accessibility:** every interactive control is keyboard reachable with visible `:focus-visible`; touch targets ≥ 44px; labels sit above inputs (never placeholder-as-label).
4. **Contrast:** body text ≥ 4.5:1 and large text ≥ 3:1 (check buttons, ghost CTAs, placeholders, and form errors).
5. **Responsive & layout:** clean at 375/390, 768, and 1280/1440 px with no horizontal overflow; single-line desktop nav; `min-h-[100dvh]` over `h-screen`; CLS 0 (no layout shift).
6. **Interactive states & motion:** implement loading (layout-matched skeletons), empty, inline/contextual error, and tactile `:active` states; honor `prefers-reduced-motion`.
7. **Copy & console:** use plain verbs, sentence case, and one CTA label per intent; browser console clean (zero warnings or failures).
