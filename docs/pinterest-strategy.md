# Pinterest Distribution Strategy
## The Ritual Journal Collective

---

## Research Summary: What's Performing in This Niche (2026)

**Key finding:** Pinterest functions as a visual search engine — not social media. Content compounds for 6–18 months. Static pins drive 5–10% outbound CTR vs 1–3% for Idea Pins. For traffic-to-product goals: 80% static pins.

**Top performing pin formats in grief/wellness/somatic niche:**

1. **Educational long-form infographic** — step-by-step numbered lists, body maps, nervous system diagrams. Highest save rate (1.5–3%). Best for: polyvagal, IFS, somatic articles.
2. **Quote/insight pin** — single powerful sentence on dark atmospheric background. Easy saves, lower CTR. Best for: brand awareness, top of funnel.
3. **Title + outcome pin** — article headline with clear "you will learn X" subhead. Drives clicks. Best for: every article's primary pin.
4. **"Signs/symptoms" pin** — "5 signs your nervous system is in dorsal vagal shutdown" format. Very high save rate in therapy-adjacent content.

**What the algorithm rewards in 2026 (in order):**
- Save rate in first 48 hours (highest weight)
- Outbound click-through rate
- Long-term repin count
- Pin freshness (new images on existing URLs outperform repins)
- Board topical relevance
- Account-level history

**Format specs that matter:**
- Alt text on every pin: +25% impressions, +123% outbound clicks, +56% profile visits
- Fresh pin images weekly — Pinterest penalizes duplicate creative
- Pins 1–2 years old earn the most saves (68 saves/pin avg in last 90 days per Tailwind 2025 data)
- Do NOT use Idea Pins as primary traffic driver — outbound link is buried

---

## Board Setup (Create These 7 Boards BEFORE Pinning Articles)

Name each board exactly. Pinterest algorithm uses board names for topical authority.

1. **Grief Rituals for Healing**
   Description: "Practical rituals for processing grief and loss. Backed by polyvagal theory and somatic healing research."

2. **Polyvagal Theory + Nervous System**
   Description: "How your nervous system processes grief — and how to regulate it. Polyvagal theory made practical."

3. **IFS Therapy + Parts Work**
   Description: "Internal Family Systems approaches to grief, trauma, and emotional healing."

4. **Somatic Healing Practices**
   Description: "Body-based approaches to releasing stored grief and trauma."

5. **Moon Rituals + Sacred Practices**
   Description: "Lunar cycle rituals, full moon ceremonies, and seasonal healing practices."

6. **Emotional Healing Rituals**
   Description: "Evidence-based emotional release practices: breathwork, writing, movement, sound."

7. **Ritual Journaling + Morning Practice**
   Description: "Daily rituals for grief, journaling practices, and morning routines for healing."

**Before pinning your articles:** Fill each board with 15–20 existing relevant pins from other accounts. The algorithm needs topical context before it distributes your content.

---

## Pin Creation Strategy

### Visual Spec
- Size: 1000×1500px (2:3 ratio — Pinterest standard)
- Style: Dark atmospheric — candlelight, moon, hands holding stone, earth textures
- Color palette: Deep charcoal/midnight backgrounds, warm amber/gold text
- NO GREEN. No clinical white. No HMW branding.
- Font: Serif headings (Playfair Display), clean sans body (Inter or similar)
- Include article title as large text overlay
- Small "theritualjournalcollective.com" watermark at bottom center
- Alt text: write this as a sentence describing the image + what the article covers

### 3 Pin Types Per Article (create all 3, publish spaced out)

**Pin Type 1 — Title Pin**
Article headline as large text + 2-line subhead that states the outcome + URL watermark.
Best board: primary topical board for that article.
UTM: `?utm_source=pinterest&utm_medium=pin&utm_content=title`

**Pin Type 2 — Quote Pin**
Pull the most arresting line from the article's "My experience" or intro section.
Text-only or minimal background. Dark atmospheric image.
Best board: secondary board (e.g., Emotional Healing Rituals or Grief Rituals for Healing).
UTM: `?utm_source=pinterest&utm_medium=pin&utm_content=quote`

**Pin Type 3 — Step/List Pin**
Visual numbered list from the article's protocol steps. 5–7 items max.
Show the steps as a scannable vertical list with icons or numbers.
Best board: most specific topical board.
UTM: `?utm_source=pinterest&utm_medium=pin&utm_content=steps`

---

## Pin Schedule

- Fill all 7 boards with 15–20 curated pins first (1 week, before posting your content)
- Then: 3–5 pins/day via Pinterest native scheduler (or Tailwind)
- **Best posting times:** Wednesday/Thursday 9–11am ET, Friday 7–9pm ET
- Never repin the same URL more than 1x per week
- Rotate pins across boards: each article pin goes in 2–3 relevant boards
- Publish fresh images weekly — same URL, new creative = treated as fresh pin
- Do not judge performance in the first 30 days. Pinterest compounds over 3–18 months.

---

## Rich Pins Setup

Rich Pins pull article metadata directly from HTML. Required meta tags (add to every article):

```html
<meta property="og:title" content="[ARTICLE TITLE]">
<meta property="og:description" content="[META DESCRIPTION]">
<meta property="og:image" content="https://theritualjournalcollective.com/assets/og-[slug].jpg">
<meta property="og:type" content="article">
<meta property="og:url" content="https://theritualjournalcollective.com/posts/[cluster]/[slug].html">
<meta name="twitter:card" content="summary_large_image">
```

**OG image spec:** 1200×630px. Use same dark atmospheric visual style as Pinterest pins.

Enable Rich Pins at: pinterest.com/settings/claimedsites — validate the domain, then Pinterest will auto-pull metadata for every pin from your domain.

Rich Pins outperform standard pins measurably. Do this before pinning any articles.

---

## Group Boards

Skip group boards in 2026. They are dead for reach. Focus on own boards only.

---

## Content Hooks That Perform in This Niche

These angles drive saves and clicks in grief/wellness/somatic Pinterest:

- "Why you can't cry after loss (it's not what you think)"
- "Your nervous system stores grief — here's how to release it"
- "Ancient ritual, modern neuroscience"
- "5 signs you're in dorsal vagal shutdown (not depression)"
- "IFS explains why part of you won't let go"
- "7 studies on why grief lives in the body"
- "What happens in your nervous system when you hold a stone"
- "The polyvagal ladder: where are you right now?"
- "This is not depression. This is dorsal vagal."
- "Grief wave hit at work. Here's what to do in 5 minutes."

**Pin title formula that works:** [Number] + [Specific outcome] + [Credibility signal]
Example: "5 Steps to Reset Your Nervous System After a Grief Wave (Polyvagal Protocol)"

---

## Tracking

Add UTM parameters to every pin URL so Plausible captures Pinterest as a source:

```
?utm_source=pinterest&utm_medium=pin&utm_content=[title|quote|steps]
```

Example full URL:
```
https://theritualjournalcollective.com/posts/grief-rituals/stone-release-ritual.html?utm_source=pinterest&utm_medium=pin&utm_content=title
```

Track in Plausible: Sources > pinterest. Monitor which articles and pin types drive actual traffic and conversions.

---

## Article-to-Board Mapping

| Article | Primary Board | Secondary Boards |
|---|---|---|
| Stone Release Ritual | Grief Rituals for Healing | Somatic Healing Practices, Polyvagal Theory + Nervous System |
| Why You Can't Cry | Grief Rituals for Healing | Emotional Healing Rituals, Polyvagal Theory + Nervous System |
| Grief Wave Protocol | Grief Rituals for Healing | Emotional Healing Rituals, Ritual Journaling + Morning Practice |
| Somatic Grief Ritual | Somatic Healing Practices | Grief Rituals for Healing, Emotional Healing Rituals |
| Dorsal Vagal Grief | Polyvagal Theory + Nervous System | Grief Rituals for Healing, Emotional Healing Rituals |
| Science Behind Stone Rituals | Polyvagal Theory + Nervous System | Grief Rituals for Healing, Somatic Healing Practices |
| Polyvagal Reset Ritual | Polyvagal Theory + Nervous System | Grief Rituals for Healing, Somatic Healing Practices |
| IFS Unburdening Physical Ritual | IFS Therapy + Parts Work | Somatic Healing Practices, Emotional Healing Rituals |
