# NASA Space Explorer — Project Plan

> A children's educational game built on NASA Open APIs. Transforms real space data into missions, puzzles, and interactive play that teaches earth science, astronomy, and physics to ages 6–14 (and curious adults).

---

## Table of Contents

**Part I — Product & Game Design**
1. [Vision & Design Philosophy](#1-vision--design-philosophy)
2. [NASA APIs → Game Mechanics](#2-nasa-apis--game-mechanics)
3. [Game Design Principles & Theory](#3-game-design-principles--theory)
4. [Navigation & Information Architecture](#4-navigation--information-architecture)

**Part II — System Architecture**
5. [Full-Stack System Layers](#5-full-stack-system-layers)
6. [Caching, Performance & Resilience](#6-caching-performance--resilience)
7. [Backend Architecture (Django)](#7-backend-architecture-django)
8. [Data Model & Persistence](#8-data-model--persistence)
9. [API Key Security & Secrets Management](#9-api-key-security--secrets-management)
10. [Admin Panel](#10-admin-panel)
11. [Infrastructure, Deployment & Scaling](#11-infrastructure-deployment--scaling)

**Part III — Frontend**
12. [Frontend Architecture](#12-frontend-architecture)
13. [Game Engine & Technology](#13-game-engine--technology)
14. [Module Separation & Project Structure](#14-module-separation--project-structure)
15. [State Management & Module Communication](#15-state-management--module-communication)

**Part IV — Look, Feel & Sound**
16. [Theme & Color Palette](#16-theme--color-palette)
17. [Typography & Visual Identity](#17-typography--visual-identity)
18. [Visual Design System](#18-visual-design-system)
19. [Animation System](#19-animation-system)
20. [Sound Design](#20-sound-design)

**Part V — Privacy, Safety & Compliance**
21. [Children's Privacy & Data Protection (COPPA/GDPR-K)](#21-childrens-privacy--data-protection-coppagdpr-k)
22. [Content Moderation & Child Safety](#22-content-moderation--child-safety)
23. [NASA Data Licensing & API Compliance](#23-nasa-data-licensing--api-compliance)

**Part VI — Analytics, Feedback & Data-Driven Evolution**
24. [Analytics & Engagement Measurement](#24-analytics--engagement-measurement)
25. [Dynamic Difficulty Adjustment (DDA) System](#25-dynamic-difficulty-adjustment-dda-system)
26. [Feedback Mechanisms](#26-feedback-mechanisms)
27. [Data-Driven Content Evolution & Roadmap](#27-data-driven-content-evolution--roadmap)

**Part VII — Reference**
28. [Technology Stack Recap & Team Organization](#28-technology-stack-recap--team-organization)

---

# Part I — Product & Game Design

## 1. Vision & Design Philosophy

### 1.1 What We're Building

An educational space exploration game for children that combines **real NASA data**, **interactive gameplay**, and **structured learning**. The goal: teach space science through play — exploration feels like a reward, not homework.

**Target Audience:** Children ages 6–14 (age-adaptive difficulty). Adults are welcome — the real NASA data keeps it interesting for them too.

**Core Pillars:**
- Learn real space science through play
- Touch real NASA data and imagery — not fake placeholders
- Progress through missions that build knowledge cumulatively
- Feel the wonder of space exploration

### 1.2 The Central Design Bet

**Raw data is boring. Data with a story is magic.**

A table of asteroid approach distances means nothing to a nine-year-old. But *"An asteroid the size of a school bus passed Earth yesterday — can you find it and calculate if we were in danger?"* — that's a mission. Same data. Different framing.

Every NASA dataset becomes a narrative hook:

| Raw Data | Narrative Reframe |
|----------|-------------------|
| APOD image metadata | "Hubble captured something strange. You're the first explorer to see it." |
| NEO approach velocities | "Planetary Defense needs you — is this asteroid a threat?" |
| Mars rover sol count | "Perseverance has been alone for 1,247 days. Send it a mission." |
| EPIC Earth imagery | "Watch your home planet spin from a million miles away." |
| Solar flare classification | "A storm is erupting on the Sun. Warn the ISS before it hits." |

### 1.3 Learning Through Real Data

Why real NASA data instead of invented content?

- **Authenticity is felt** — kids know when something is real. "This is the actual photo from Mars" lands harder than a cartoon.
- **The universe writes better content than we do** — 5,000+ exoplanets, daily asteroid near-misses, live ISS telemetry. We can't out-imagine this.
- **Facts become souvenirs** — when a child unlocks a real Hubble image, they *own* that knowledge. It's theirs.
- **Built-in freshness** — APOD updates daily, NEO feeds update hourly. The game never goes stale.

### 1.4 Gameplay Philosophy: Three Pillars

Every interaction is one of these three modes. The game cycles between them to maintain engagement:

| Mode | Player Feeling | Example |
|------|----------------|---------|
| **Exploration** | "I'm discovering" | Free-fly the space map, click on anything, find hidden facts |
| **Challenge** | "I'm solving" | Puzzles, quizzes, timed missions, boss encounters |
| **Creation** | "I'm making" | Build rockets from earned parts, design a Mars base, arrange a gallery |

Most children's games over-index on Challenge. We deliberately weight Exploration highest — the universe is the draw, not the score.

---

## 2. NASA APIs → Game Mechanics

This is the content engine. Each NASA Open API endpoint feeds one or more game mechanics. The backend ingests and transforms; the frontend plays.

### 2.1 Full Endpoint → Mechanic Map

| NASA API | Data Provided | Game Mechanics |
|----------|---------------|----------------|
| **APOD** (Picture of the Day) | Daily image + explanation text | Jigsaw puzzles · Daily reveal ritual · Gallery collection · "Guess the object" quiz |
| **Mars Rover Photos** | Curiosity, Perseverance, Opportunity cameras by sol | Rover driving minigame · Spot-the-difference · "What did the rover see?" exploration · Terrain jigsaws |
| **NeoWs** (Near Earth Objects) | Asteroid sizes, velocities, approach distances | Planetary Defense mode · Orbit prediction puzzle · Size comparison sorting game · Real-time threat dashboard |
| **DONKI** (Space Weather) | Solar flares, CMEs, geomagnetic storms | Solar Storm Surfer (dodge game) · Aurora prediction quiz · "Protect the ISS" shield timing |
| **EPIC** (Earth Polychromatic Camera) | Full-disc Earth images from L1 | Earth rotation time-lapse builder · "Find your continent" · Cloud pattern matching · Climate observation diary |
| **Exoplanet Archive** | 5,000+ confirmed exoplanets, stellar data | Planet builder (match real parameters) · Habitability scorer · "Would you survive here?" · Star system explorer |
| **NASA Image & Video Library** | Searchable archive, historical missions | History timeline builder · "Meet the Astronaut" profiles · Mission replay stories · Media scavenger hunt |
| **Insight Weather** (Mars) | Temperature, wind, pressure on Mars | "Pack for Mars" survival quiz · Weather comparison widget (Earth vs Mars) · Seasonal tracker |
| **TLE** (Two-Line Elements) | Orbital parameters for satellites | Satellite spotting game · Orbit shape puzzle · "Track the ISS" live map |
| **TechTransfer / Patents** | NASA inventions & spinoffs | "Invented by NASA?" true/false · Innovation matching (problem → solution) · Spinoff discovery cards |
| **EONET** (Earth Observatory Events) | Wildfires, storms, volcanoes — live | Earth Guardian dispatch game · Disaster science quizzes · "What's happening now?" globe |
| **SSD/CNEOS** (Small Bodies) | Comet/asteroid orbit calculations | Trajectory drawing puzzle · Comet tail direction quiz · Historic impact stories |

### 2.2 Detailed Game Designs by API

#### 2.2.1 APOD — The Daily Ritual

**The hook:** A new real image every single day. This is our retention engine.

- **Morning Reveal**: Image starts pixelated. Every correct quiz answer reveals more pixels. Full reveal earns the image for the gallery.
- **Jigsaw Mode**: Image sliced into 12/24/48 pieces (age-scaled). Completing unlocks the NASA scientist's explanation text.
- **Caption Challenge**: Show image, hide title. Multiple choice — "Is this a nebula, galaxy, or star cluster?" Teaches classification.
- **Streak Calendar**: Visual calendar showing which days you've collected. Gaps create completionist pull.

#### 2.2.2 Mars Rovers — Embodiment

**The hook:** You ARE the rover. First-person (well, first-robot) exploration.

- **Rover Driver**: Top-down view, real terrain photos as background. Navigate waypoints, avoid rocks. Each waypoint reveals a real photo from that sol.
- **Instrument Panel**: Real rover cameras (Mastcam, Navcam, Hazcam) — switch views, learn what each is for.
- **Sol Journal**: Chronological story mode. "Sol 1: Landing. Sol 60: First drill. Sol 200: Dust storm." Each sol is a mini-chapter.
- **Rock Classifier**: Show real rock close-ups. Sedimentary, igneous, or meteorite? Teaches geology with Mars samples.

#### 2.2.3 NeoWs — Planetary Defense

**The hook:** Real asteroids, real approach dates. Low-stakes urgency.

- **Threat Assessment**: Live feed of approaching NEOs. For each: calculate if it's dangerous (size × speed × distance). Teaches scale and math.
- **Orbit Drawer**: Given velocity and distance data, drag to draw the orbit path. Score on accuracy vs real trajectory.
- **Size Sorter**: Drag asteroids onto a comparison line (school bus → football field → city). Internalize scale intuitively.
- **Deflection Mission**: Boss mode. A hazardous asteroid is coming (fictional, but with real physics). Choose deflection method, time it right.

#### 2.2.4 DONKI — Space Weather Action

**The hook:** Visually dramatic, time-sensitive. The action game of the suite.

- **Solar Storm Surfer**: Side-scrolling dodge game. Your ship rides the solar wind, avoiding CME bursts. CME speeds pulled from real data.
- **Aurora Forecaster**: Given a solar event, predict where on Earth auroras will be visible. Check against real aurora reports.
- **Shield Timing**: A CME is en route to the ISS (real event data). Calculate travel time from solar wind speed. Raise shields at the right moment.

#### 2.2.5 EPIC — Homeworld Observer

**The hook:** See Earth from outside. Emotional, perspective-shifting.

- **Spin Builder**: Arrange a day's worth of EPIC frames into the correct rotation sequence. Play back as time-lapse.
- **Continent Finder**: "Find Australia in this frame." Teaches geography with a space twist.
- **Cloud Detective**: Compare frames from different days. "What changed? Is that a hurricane forming?"
- **Overview Effect Journal**: Collect favorite Earth images. Write one observation for each. A reflective, non-gamey mode.

#### 2.2.6 Exoplanets — The Physics Playground

**The hook:** Thousands of real alien worlds. Each is a physics puzzle.

- **Habitability Scorer**: Pick a real exoplanet. Check temperature, atmosphere, gravity, star type. Could humans survive? Score the planet.
- **Planet Builder**: Sliders for mass, radius, orbital distance. Build a planet — then reveal which real exoplanet you accidentally matched.
- **Goldilocks Hunt**: Browse the archive with filters. Find planets in the habitable zone. Each find is a collectible card.
- **Character Connections**: "This planet orbits a star studied by Kepler — who was he?" Bridges data to history of science.

#### 2.2.7 Image Library — The History Game

**The hook:** Meet the humans behind the missions. Connect to the story of exploration.

- **Timeline Builder**: Drag mission photos onto a timeline. Apollo → Shuttle → ISS → Artemis.
- **Astronaut Profiles**: Unlock biographical cards. "Mae Jemison — first Black woman in space. Also: dancer, doctor, Star Trek guest."
- **Mission Replay**: Narrated story sequences using archival photos + audio. "Relive Apollo 11 in 10 minutes."
- **Scavenger Hunts**: "Find a photo of: a spacewalk, a splashdown, a moon buggy." Teaches search skills on real archives.

#### 2.2.8 EONET — Earth Guardian

**The hook:** You're watching over the planet. Live events, real stakes.

- **Dispatch Game**: Live globe with event markers (fires, storms, volcanoes). Click an event, answer a question about its science, "dispatch" the right response team.
- **Event Science Cards**: Each event type has a lesson. Why do wildfires spread? How do hurricanes form?
- **Change Over Time**: Compare this month's events to last year's. Introduces climate observation gently.

### 2.3 Cross-API Missions (The Best Part)

Multi-API missions feel like real science — combining data sources to answer one question:

- **"Is There Life Out There?"** — Exoplanet habitability + Mars water evidence + DONKI (what solar activity does to atmospheres)
- **"Defend the Planet"** — NeoWs threat assessment + DONKI solar storm warnings + EONET ground impact tracking
- **"A Day in Space"** — APOD morning ritual + ISS position tracking (TLE) + EPIC Earth observation + evening Mars weather check
- **"Scale of Everything"** — Sort objects from all APIs by size: rover wheel → asteroid → Earth → Sun → galaxy in APOD

### 2.4 Content Types Summary

| Type | Best For | APIs |
|------|----------|------|
| **Jigsaw puzzles** | Visual engagement, low literacy requirement | APOD, Mars Rovers, EPIC |
| **Quizzes** | Knowledge check, quick reward | All |
| **Sorting/dragging** | Scale and classification intuition | NeoWs, Exoplanets, Image Library |
| **Action/dodge games** | High energy, reflex fun | DONKI, NeoWs deflection |
| **Builders/creators** | Self-expression, deep engagement | Exoplanets, EPIC, Ship customization |
| **Story/narrative** | Emotional connection, context | Image Library, Mars Sol Journal |
| **Live dashboards** | Real-world relevance, daily return | NeoWs, EONET, ISS, DONKI |

---

## 3. Game Design Principles & Theory

### 3.1 Core Framework: Self-Determination Theory (SDT)

The three psychological needs that drive intrinsic motivation. Every design decision must serve at least one:

| Need | In Our Game | Implementation |
|------|-------------|----------------|
| **Autonomy** | "I choose what to explore" | Non-linear mission selection, multiple paths to goals, player-driven exploration |
| **Competence** | "I'm getting better at this" | Scaffolded difficulty, clear progress feedback, skill trees that unlock visibly |
| **Relatedness** | "I belong to something bigger" | Crew/team mechanics, shared discoveries board, astronaut character companionship |

### 3.2 Flow State Design (Csikszentmihalyi)

Keep children in the "flow channel" — the sweet spot between boredom and anxiety:

```
Anxiety Zone     ← Challenge too high, skill too low
─────────────────────────────────────
  ★ FLOW CHANNEL ★   ← We target here
─────────────────────────────────────
Boredom Zone     ← Challenge too low, skill too high
```

**How we maintain flow:**
- **Dynamic difficulty adjustment (DDA)**: 3+ wrong in a row → silently reduce difficulty. Breezing through → increase challenge.
- **Clear goals at all times**: Every screen answers "what should I do next?"
- **Immediate feedback**: Every action gets a response within 200ms.
- **Eliminate friction**: No login walls for initial play. No long loads. No unskippable tutorials.

### 3.3 Reinforcement Schedule (Operant Conditioning)

**Variable ratio reinforcement** — the most engagement-sustaining schedule:

| Schedule | Where We Use It | Example |
|----------|-----------------|---------|
| **Fixed ratio** | Core progress | Complete 5 quiz questions → earn 1 star |
| **Variable ratio** | Discovery | Random chance to find a "rare" NASA fact or hidden collectible |
| **Fixed interval** | Daily engagement | APOD refreshes every 24h |
| **Variable interval** | Surprise delight | Random "meteor shower" bonus events |

**Critical rule**: Rewards must be **informational, not controlling**. The reward says "you learned something real" — not "you clicked enough buttons."

### 3.4 Progression Systems

**Mission Ranks (Macro):**
```
Cadet → Pilot → Commander → Captain → Admiral → Legend
```

**Knowledge Constellation (Skill Tree):**
- Each star = a concept learned
- Stars connect into constellations = topic mastery
- Constellations light up in the player's personal "night sky"
- Progress tracker AND visual reward in one

**Collections:**
- NASA Image Album (real APOD images earned)
- Mission Patches (illustrated badges per arc)
- Audio Logs (real NASA communications)
- Ship Blueprints (collect parts, build spacecraft)

### 3.5 Engagement Loops

```
Core Loop (2-5 min):    Explore → Discover → Learn → Quiz → Reward → Explore
Session Loop (15-30m):  Choose Mission → 3-5 Core Loops → Boss → Complete → Progress
Long-Term (weeks):      Unlock Planet → Master Topics → Constellation → Next Region
```

### 3.6 Anti-Frustration Design

| Principle | Implementation |
|-----------|----------------|
| **No fail states** | Wrong answers reduce bonus, never block. "Not quite — try this hint!" |
| **Generous hints** | 3 tiers: nudge → clue → show answer with explanation |
| **Save everywhere** | Auto-save after every action. Closing the tab loses nothing. |
| **Celebrate mistakes** | "You discovered that X isn't right — that's how scientists learn!" |
| **Cooldown, not punishment** | Rapid wrong clicks → offer a "space walk" break minigame |

### 3.7 Curiosity Gaps (Loewenstein)

Present just enough to make children *need* to know more:
- Blurred NASA image: "Complete this mission to reveal what Hubble photographed..."
- Counter: "3 of 7 Mars mysteries solved"
- Teaser: "Commanders unlock the Black Hole Zone..."
- Real questions: "Why is Mars red? Scientists weren't sure for decades..."

### 3.8 Social Elements (Opt-In, Parental Control)

- Leaderboards: pseudonyms only, weekly reset
- Shared discoveries: "42 explorers found this today!"
- Cooperative missions: aggregate progress to "map" a region
- No PvP. All competition is vs. personal best or collective goals.

---

## 4. Navigation & Information Architecture

### 4.1 Core Model: The Space Map

Primary navigation IS the game world. Children fly their ship between celestial bodies:

```
┌─────────────────────────────────────────────┐
│              🌌 SPACE MAP 🌌                │
│                                             │
│    ☆ Asteroid        ★ Mars ────── ★ Jupiter│
│      Belt              │                    │
│        \               │                    │
│         ★ Earth ──── ★ Moon    ★ Saturn     │
│         │                        │          │
│    ★ Venus    ★ Sun          ★ Neptune      │
│         │       │                           │
│    ★ Mercury    ★ (Black Hole Zone - locked)│
│                                             │
│  [My Ship]  [Missions]  [Collection]  [⚙]  │
└─────────────────────────────────────────────┘
```

- Each body = navigable node with missions + content
- Locked nodes visible but dimmed → curiosity gaps
- Bottom bar for non-spatial features

### 4.2 Screen Hierarchy

```
Space Map (Home)
├── Planet/Body View
│   ├── Overview (facts, NASA image, atmosphere)
│   ├── Missions → Mission Play (game viewport)
│   ├── Gallery (collected images)
│   └── Data Lab (interactive visualizations)
├── My Ship (profile)
│   ├── Rank & Progress
│   ├── Knowledge Constellation
│   ├── Collection
│   └── Ship Customization
├── Mission Control
│   ├── Current / Available / Completed
├── NASA Live
│   ├── Picture of the Day
│   ├── Near-Earth Objects
│   └── ISS Position
└── Settings
    ├── Audio / Accessibility / Age / Parental
```

### 4.3 Navigation Principles for Children

| Principle | Implementation |
|-----------|----------------|
| **Always know where you are** | Breadcrumb "flight path" dotted line |
| **Always know how to go back** | Large "Return to Ship" button — not just browser back |
| **Max 3 taps deep** | Anything reachable in 3 taps from Space Map |
| **Show, don't tell** | Destinations are images/icons, not text links |
| **No dead ends** | Every screen suggests next: "Explore Mars next?" |
| **Age-appropriate density** | Ages 6-8: 3-4 large items. Ages 12-14: fuller layouts. |

### 4.4 Onboarding Flow

```
1. Choose Your Astronaut → pick avatar
2. Name Your Ship → text input + suggestions
3. First Mission → guided Moon trip (simplest content)
4. You Discovered Something! → first NASA image earned
5. The Universe Awaits → Space Map revealed
```
~3 minutes. Each step teaches one nav concept. Earns "First Launch" badge.

### 4.5 Contextual Aids

- **Astronaut Guide**: Floating companion, points at interactive elements. Dismissible by older kids.
- **Pulsing Highlights**: New content glows gently.
- **Smart Suggestions**: "You learned Mars' surface — see the latest rover photos?"
- **Flight Path Breadcrumb**: Visual dotted line tracing your ship's route.

---

# Part II — System Architecture

## 5. Full-Stack System Layers

### 5.1 End-to-End Request Flow

The complete journey from NASA's servers to a child's browser:

```
┌──────────────────────────────────────────────────────────────┐
│                    NASA Open API Servers                      │
│     api.nasa.gov (APOD, NeoWs, DONKI, EPIC, Mars, etc.)      │
└──────────────────────────────────────────────────────────────┘
                            │
                  (Our API key, rate-limited
                   1000 req/hour per key)
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│              LAYER 1: Ingestion Workers (Celery)              │
│   Scheduled tasks pull from NASA on fixed intervals          │
│   APOD: daily · NeoWs: hourly · DONKI: 15min · EPIC: 6hr     │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│           LAYER 2: Transformation Pipeline (Python)           │
│   Raw JSON → cleaned → enriched → game-ready format          │
│   • Normalize units  • Generate quiz questions               │
│   • Compute derived fields (difficulty, tags)                │
│   • Slice images for jigsaws  • Extract quiz distractors     │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│              LAYER 3: Persistence (PostgreSQL)                │
│   Long-lived, queryable, source of truth                     │
│   NASA content tables + User/progress tables + Game config   │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│               LAYER 4: Cache Layer (Redis)                    │
│   Hot data served without touching Postgres                  │
│   • Today's APOD  • Current NEO feed  • Leaderboards         │
│   • Session state  • Rate limit counters                     │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│            LAYER 5: Django REST API (our backend)             │
│   Game-specific endpoints. Browser NEVER sees NASA directly. │
│   /api/missions/  /api/progress/  /api/nasa/today/           │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                   LAYER 6: CDN (CloudFront/CF)                │
│   Static assets + cached API responses + media proxy         │
│   NASA images re-served from our CDN (resized, optimized)    │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│              LAYER 7: Frontend (Next.js + PixiJS)             │
│   React shell + Canvas game engine + local state cache       │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │  Child's iPad │
                    └───────────────┘
```

### 5.2 Why Each Layer Exists

| Layer | Problem It Solves |
|-------|-------------------|
| **Ingestion Workers** | NASA rate limits (1000/hr). Ten thousand kids can't all hit NASA. We hit NASA once, serve everyone. |
| **Transformation** | NASA returns scientist-formatted data. Kids need game-formatted data. Transform once, serve many. |
| **PostgreSQL** | Historical queries ("all APODs from last month"), relational integrity (user → progress → missions), admin editability. |
| **Redis** | Sub-10ms reads for hot paths. Today's APOD is requested by every user — no reason to hit Postgres each time. |
| **Django API** | One stable contract for the frontend. NASA changes their API? We absorb it here. Frontend doesn't notice. |
| **CDN** | NASA's image servers aren't built for our traffic. We proxy, resize, cache, and serve from the edge. |
| **Next.js + local cache** | Offline play, instant navigation, zero-latency UI on already-fetched content. |

### 5.3 Data Freshness Policy

Different NASA data changes at different rates. Our ingestion schedule matches each:

| Data Type | NASA Poll | Rationale |
|-----------|-----------|-----------|
| APOD | 1×/day at 05:00 UTC | Updates once daily |
| NeoWs feed | 1×/hour | Near-real-time relevance |
| DONKI space weather | Every 15 min | Solar events can be sudden |
| EPIC Earth images | Every 6h | Satellite posts ~12×/day |
| Mars rover photos | 1×/day | Rover downlinks are batched |
| Exoplanet archive | 1×/week | New planets confirmed slowly |
| Image Library | On-demand | Historical, doesn't change |
| EONET events | Every 30 min | Wildfires/storms evolve |
| ISS position | Every 30s | Moves fast, lightweight call |

How this data is cached, and what happens when NASA is unreachable, is covered in depth in **§6**.

---

## 6. Caching, Performance & Resilience

This section is the operational heart of the system. Everything in §5 depends on getting this right: if caching fails, we hit NASA's rate limit and go dark. If resilience fails, kids see blank screens when NASA has a bad day. Neither is acceptable.

### 6.1 The Four-Tier Cache Hierarchy

Every piece of NASA data passes through four cache layers before reaching a child. Each layer serves a different purpose and has a different miss cost:

```
┌─────────────────────────────────────────────────────────┐
│  L1: Browser Cache         ~0ms    Per-device           │
│      Service Worker + TanStack Query + IndexedDB        │
├─────────────────────────────────────────────────────────┤
│  L2: CDN Edge              ~20ms   Per-region           │
│      CloudFront / Cloudflare — static & API responses   │
├─────────────────────────────────────────────────────────┤
│  L3: Redis                 ~1ms    Shared, volatile     │
│      Hot data, serialized responses, session state      │
├─────────────────────────────────────────────────────────┤
│  L4: PostgreSQL            ~10ms   Shared, durable      │
│      Permanent archive — every NASA response ever       │
├─────────────────────────────────────────────────────────┤
│  Origin: NASA API          ~200ms  Rate-limited!        │
│      1000 req/hour. ONLY Celery workers touch this.     │
└─────────────────────────────────────────────────────────┘
```

**The golden rule: a cache miss at Ln falls through to Ln+1, never skips to origin.** User traffic can NEVER cause a NASA API call. Only scheduled Celery tasks hit NASA, on a fixed cadence, regardless of how many users we have.

This means: 1 user or 1 million users → same number of NASA calls (~500/day). Rate limits become a non-issue by design.

### 6.2 Layer-by-Layer Detail

#### L1 — Browser Cache

Three sub-mechanisms, each for a different data shape:

| Mechanism | Stores | TTL | Why |
|-----------|--------|-----|-----|
| **Service Worker** (Workbox) | HTML shell, JS bundles, sprite sheets, fonts, last 7 days of mission JSON | Until next deploy (assets) / 7d (content) | Offline play. Game loads instantly on repeat visits, works on a plane. |
| **TanStack Query** | API responses in memory | `staleTime` per-endpoint (5min–24h) | Dedup. 3 components asking for today's APOD → 1 network request. |
| **IndexedDB** | Player progress, collection, constellation state | Forever (sync to server when online) | Offline progress. Kid completes a mission on the bus → syncs at home. |

```ts
// TanStack Query config — per-endpoint freshness
export const queryConfig = {
  '/api/v1/nasa/today/':    { staleTime: 1 * HOUR,  gcTime: 24 * HOUR },
  '/api/v1/planets/:id/':   { staleTime: 6 * HOUR,  gcTime: 7 * DAY  },
  '/api/v1/missions/:id/':  { staleTime: 24 * HOUR, gcTime: 30 * DAY },
  '/api/v1/progress/me/':   { staleTime: 0,         gcTime: 1 * HOUR }, // always revalidate
  '/api/v1/live/iss/':      { staleTime: 30 * SEC,  gcTime: 5 * MIN  },
};
```

#### L2 — CDN Edge Cache

Two distinct CDN behaviors:

**Static assets** (JS, CSS, sprites, audio): `Cache-Control: public, max-age=31536000, immutable`. Filenames are content-hashed by Next.js, so cache forever — a new deploy gets new filenames.

**API responses**: Short edge TTL + stale-while-revalidate:

```
Cache-Control: public, s-maxage=300, stale-while-revalidate=3600
```

This means: CDN serves cached response for 5 minutes fresh, then for another hour it serves the stale copy *while* refetching in the background. Users never wait for the origin.

**Media (NASA images)**: See §6.5 — these get special treatment.

#### L3 — Redis Application Cache

Redis sits between Django views and Postgres. Two caching patterns:

**Pattern A — Full response cache.** For endpoints where every user gets identical data:

```python
# apps/nasa_ingest/views.py
class TodayView(APIView):
    @method_decorator(cache_page(60 * 60))  # 1h — entire HTTP response cached
    def get(self, request):
        return Response({
            'apod': APODSerializer(APODEntry.objects.latest('date')).data,
            'neo_count': cache.get('neo:approaching_count'),
            'solar_activity': cache.get('donki:active_events'),
        })
```

**Pattern B — Cache-aside for computed values.** For expensive derivations:

```python
def get_planet_missions(planet_id, age_group):
    key = f'planet:{planet_id}:missions:{age_group}'
    if cached := cache.get(key):
        return cached
    result = Mission.objects.filter(
        planet_id=planet_id, is_published=True,
        game__min_age_group__lte=age_group
    ).select_related('game').prefetch_related('unlocks')
    data = MissionListSerializer(result, many=True).data
    cache.set(key, data, timeout=6 * 3600)
    return data
```

**Invalidation**: Admins publishing a mission triggers `cache.delete_pattern(f'planet:{mission.planet_id}:*')`. Prefer key-pattern deletion over short TTLs — explicit beats implicit.

#### L4 — PostgreSQL Permanent Archive

Postgres is not a cache — it's the **durable fallback**. Every NASA response we ingest is stored forever. This is what saves us when NASA is down (§6.7).

Query optimizations that keep L4 fast enough to be a viable fallback:
- Covering indexes on hot paths (see §8.3)
- `select_related`/`prefetch_related` to kill N+1 queries
- Read replicas for analytics queries so they don't compete with gameplay reads
- Connection pooling via PgBouncer (Django's default pool is per-worker, wasteful)

### 6.3 Rate Limit Protection

NASA gives us 1000 requests/hour. Here's how we never come close:

#### Scheduled Ingestion Only

```
Worst-case NASA calls per hour:
  APOD:        1/day    → 0.04/hr
  NeoWs:       1/hr     → 1/hr
  DONKI:       4/hr     → 4/hr
  EPIC:        1/6hr    → 0.17/hr
  Mars:        1/day    → 0.04/hr
  Exoplanets:  1/week   → 0.006/hr
  EONET:       2/hr     → 2/hr
  ISS (TLE):   120/hr   → 120/hr  ← highest consumer
  ────────────────────────────────
  Total:                 ~127/hr  ← 13% of quota
```

Comfortable 8× headroom. Even if every task retries 5× simultaneously, we stay under.

#### Distributed Lock on Ingestion

Multiple Celery workers must not run the same ingestion concurrently (double-fetch = wasted quota):

```python
# apps/nasa_ingest/tasks.py
from redis.lock import Lock

@shared_task
def ingest_apod():
    lock = Lock(redis_client, 'lock:ingest:apod', timeout=300, blocking=False)
    if not lock.acquire():
        logger.info('ingest_apod already running, skipping')
        return
    try:
        _do_ingest_apod()
    finally:
        lock.release()
```

#### Live Quota Tracking

Every NASA client call increments a Redis counter. The admin dashboard shows it; a Celery task alerts if we exceed 70%:

```python
class NASAClient:
    def _request(self, url, params):
        hour_key = f"nasa:quota:{datetime.now():%Y%m%d%H}"
        used = redis_client.incr(hour_key)
        redis_client.expire(hour_key, 3600)
        if used > 700:
            alert_ops(f"NASA quota at {used}/1000 this hour")
        if used > 950:
            raise QuotaExhaustedError  # Don't make the call — serve from archive
        return requests.get(url, params={**params, 'api_key': settings.NASA_API_KEY})
```

### 6.4 Cache Warming — Never Serve a Cold Miss

The first user of the day should be as fast as the thousandth. We pre-populate caches *before* traffic arrives.

#### Ingest-Time Warming

Every Celery ingestion task ends by writing to Redis and pinging the CDN:

```python
@shared_task
def ingest_apod():
    # ... fetch, transform, save to Postgres ...

    # Warm L3 (Redis)
    cache.set('apod:today', APODSerializer(entry).data, timeout=86400)

    # Warm L2 (CDN) — request our own endpoint so CloudFront caches it
    for region in CDN_WARM_REGIONS:
        requests.get(f'{API_BASE}/api/v1/nasa/today/',
                     headers={'CloudFront-Viewer-Country': region})

    # Warm media variants (see §6.5)
    MediaWarmer(entry.image_url).generate_all_sizes()
```

#### Predictive Prefetch (Browser-Side)

When a player lands on Mars, silently prefetch adjacent planets:

```ts
// When Mars mounts, prefetch neighbors in the Space Map graph
useEffect(() => {
  const neighbors = spaceMapGraph.neighbors('mars'); // ['earth', 'jupiter', 'asteroid-belt']
  neighbors.forEach(id =>
    queryClient.prefetchQuery({ queryKey: ['planet', id], queryFn: ... })
  );
}, []);
```

Ship-flying animation between planets takes ~2 seconds — more than enough to have Jupiter's data ready before arrival.

### 6.5 Image & Media Caching

NASA images are the heaviest payload and the most cacheable (they never change). They get a dedicated pipeline.

#### Content-Addressed, Pre-Generated Variants

On ingest, each image is fetched **once**, then every size variant is generated upfront and pushed to S3. No on-the-fly resizing in the request path.

```
APOD image arrives (3000×2000 JPEG, 2.4MB)
  │
  ├─ hash = sha256(nasa_url)[:16]  → 'a3f8b2c1d4e5f6a7'
  │
  ├─ Generate variants:
  │    thumb   →  200w  WebP  (12KB)   → s3://media/a3f8b2c1/thumb.webp
  │    card    →  600w  WebP  (45KB)   → s3://media/a3f8b2c1/card.webp
  │    full    → 1200w  WebP  (180KB)  → s3://media/a3f8b2c1/full.webp
  │    puzzle  → 1600w  WebP  (320KB)  → s3://media/a3f8b2c1/puzzle.webp
  │    hd      → 2400w  JPEG  (900KB)  → s3://media/a3f8b2c1/hd.jpg
  │
  └─ Store hash → variants mapping in Postgres
```

Frontend requests by hash + size name, never by NASA URL:

```html
<img src="https://cdn.ourgame.com/media/a3f8b2c1/card.webp"
     srcset="https://cdn.ourgame.com/media/a3f8b2c1/thumb.webp 200w,
             https://cdn.ourgame.com/media/a3f8b2c1/card.webp 600w,
             https://cdn.ourgame.com/media/a3f8b2c1/full.webp 1200w"
     sizes="(max-width: 600px) 100vw, 600px">
```

CDN headers: `Cache-Control: public, max-age=31536000, immutable`. Content-addressed URLs never change → cache forever.

#### Rover Photos: The Volume Problem

Mars rovers have produced **1M+ photos**. We can't pre-process all of them. Strategy:

- **Curated set** (~500 photos): Pre-processed, used in missions. Full variant pipeline.
- **Browse catalog** (the rest): Lazy proxy. First request triggers fetch+process, result cached 30 days. Proxy endpoint rate-limited to 10/min/user to prevent gallery-scroll abuse.

### 6.6 Stale-While-Revalidate Everywhere

The single most important pattern for perceived performance. At every layer:

```
Request arrives
  │
  ├─ Cache hit (fresh)?      → Return immediately. Done.
  │
  ├─ Cache hit (stale)?      → Return stale immediately
  │                            + trigger background refresh
  │                            User sees: instant (slightly old) data
  │
  └─ Cache miss entirely?    → Fall through to next layer
                               (Never blocks on origin if any layer has anything)
```

Django implementation for endpoints where slight staleness is fine:

```python
class StaleWhileRevalidateMixin:
    swr_fresh_ttl = 300     # 5 min: serve without question
    swr_stale_ttl = 3600    # 1 hr: serve but refresh behind the scenes

    def dispatch(self, request, *args, **kwargs):
        key = self.get_cache_key(request)
        entry = cache.get(key)

        if entry and entry['age'] < self.swr_fresh_ttl:
            return Response(entry['data'])                    # Fresh

        if entry and entry['age'] < self.swr_stale_ttl:
            refresh_cache_async.delay(key, request.path)      # Celery
            return Response(entry['data'])                    # Stale-but-served

        return super().dispatch(request, *args, **kwargs)     # Miss → compute
```

### 6.7 Resilience: When NASA Goes Down

NASA's API has outages. NASA has government shutdowns. We must assume the origin is unreliable and design so children never notice.

#### The Fallback Chain

When a Celery task fails to reach NASA, **nothing changes for users** — they're served from caches that were populated before the outage:

```
Ingestion fails  →  Redis still has yesterday's data (TTL extended)
Redis expires    →  Postgres has years of archived content
Postgres down    →  Frontend IndexedDB has last 7 days
Everything down  →  Seed bundle (50 curated APODs shipped in the app)
```

#### Circuit Breaker on NASA Calls

After repeated failures, stop trying. Retrying a dead endpoint wastes quota and delays recovery detection:

```python
# apps/nasa_ingest/circuit.py
class NASACircuitBreaker:
    """
    CLOSED    → normal operation
    OPEN      → NASA unreachable, skip all calls, serve archive
    HALF_OPEN → send one probe; success closes, failure reopens
    """
    FAILURE_THRESHOLD = 5       # consecutive failures before opening
    RECOVERY_TIMEOUT  = 300     # 5 min before probing

    def call(self, fn, *args, **kwargs):
        state = cache.get('circuit:nasa:state', 'CLOSED')

        if state == 'OPEN':
            if self._should_probe():
                cache.set('circuit:nasa:state', 'HALF_OPEN')
            else:
                raise CircuitOpenError('NASA circuit open — using archive')

        try:
            result = fn(*args, **kwargs)
            self._on_success()   # resets failure count, closes circuit
            return result
        except (RequestException, Timeout) as e:
            self._on_failure()   # increments count, may open circuit
            raise
```

When the circuit opens, a Celery task extends all Redis TTLs and posts to the ops channel: *"NASA circuit OPEN — serving from archive. Will probe in 5 min."*

#### Graceful Feature Degradation

Some features need fresh data; most don't. When the circuit is open, selectively hide the fresh-data features:

| Feature | NASA Down Behavior |
|---------|-------------------|
| APOD daily puzzle | Serve most recent successfully-ingested day. Banner: *"Showing yesterday's image — new one coming soon!"* |
| Mars rover missions | Fully playable — all content is pre-ingested |
| NEO threat dashboard | Show last-known feed with timestamp: *"Last updated 4 hours ago"* |
| ISS live position | Hide the widget entirely (position 4 hours old is meaningless) |
| Exoplanet explorer | Fully playable — weekly refresh, archive is always fresh enough |
| Leaderboards | Fully functional — our data, not NASA's |
| All quizzes, jigsaws, progression | Fully functional — zero NASA dependency at play-time |

Controlled by a single `nasa_degraded` feature flag that the circuit breaker flips automatically. Flag propagates to frontend via `/api/v1/status/`.

#### Retry Policy

Transient failures (timeout, 503) retry with exponential backoff + jitter; permanent failures (404, 401) do not:

```python
@shared_task(
    autoretry_for=(Timeout, ConnectionError, HTTPError),
    retry_backoff=60,           # 60s, 120s, 240s, 480s, 960s
    retry_backoff_max=1800,     # cap at 30 min
    retry_jitter=True,          # ±25% — avoid thundering herd on recovery
    max_retries=5,
)
def ingest_apod():
    with nasa_circuit_breaker:
        ...
```

### 6.8 Performance Budgets & Monitoring

Concrete targets — if we miss these, something is broken:

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| API p50 response | < 50ms | > 100ms |
| API p99 response | < 300ms | > 1s |
| Redis hit rate | > 95% | < 90% |
| CDN hit rate | > 90% | < 80% |
| NASA calls/hour | < 200 | > 500 |
| Time-to-interactive (frontend) | < 2s on 4G | > 4s |
| Game frame rate | 60fps | < 45fps sustained |
| Cold-start mission load | < 1s | > 3s |

**Tooling:**
- **django-silk** in dev — profile every query, catch N+1 early
- **Prometheus + Grafana** in prod — response times, cache hit rates, quota usage
- **Sentry Performance** — frontend Core Web Vitals, transaction traces
- **PgHero** — slow query log, index usage, bloat detection

### 6.9 Summary: The Caching Contract

| Guarantee | How |
|-----------|-----|
| **NASA rate limit is unreachable** | Only scheduled Celery tasks call NASA. ~127 calls/hour regardless of user count. |
| **NASA outages are invisible** | Circuit breaker + TTL extension + Postgres archive + IndexedDB + seed bundle. Five layers of fallback. |
| **First user is as fast as the millionth** | Cache warming on ingest. CDN pre-warmed across regions. No cold misses. |
| **Images load instantly** | Pre-generated size variants. Content-addressed. CDN-cached forever. |
| **Navigation feels instant** | Predictive prefetch during ship-flying animation. SWR on everything. |
| **Offline play works** | Service Worker + IndexedDB hold 7 days of content. Progress syncs on reconnect. |

---

## 7. Backend Architecture (Django)

### 7.1 Why Django

- **Batteries included**: ORM, admin, auth, migrations — less glue code
- **Django Admin**: 80% of our admin panel is free (see §10)
- **DRF**: Mature, well-documented REST layer with serializers, permissions, throttling
- **Celery integration**: First-class async task support for NASA ingestion
- **Python ecosystem**: NumPy/Pillow for image processing, requests for HTTP, etc.

### 7.2 Django Project Structure

```
backend/
├── config/                    # Django project config
│   ├── settings/
│   │   ├── base.py
│   │   ├── dev.py
│   │   └── prod.py
│   ├── urls.py
│   ├── celery.py              # Celery app config
│   └── wsgi.py / asgi.py
│
├── apps/
│   ├── nasa_ingest/           # NASA API clients + Celery tasks
│   │   ├── clients/           # One client class per NASA API
│   │   │   ├── apod.py
│   │   │   ├── neows.py
│   │   │   ├── donki.py
│   │   │   └── ...
│   │   ├── tasks.py           # @shared_task Celery ingestion jobs
│   │   ├── transformers/      # Raw JSON → Django model instances
│   │   └── models.py          # NASAContent, APODEntry, NEOObject, ...
│   │
│   ├── games/                 # Game definitions, missions, mechanics
│   │   ├── models.py          # Game, Mission, Puzzle, Quiz
│   │   ├── generators/        # Auto-generate puzzles from NASA content
│   │   │   ├── jigsaw.py      # Image → puzzle pieces
│   │   │   ├── quiz.py        # Facts → quiz questions + distractors
│   │   │   └── sorting.py     # NEO sizes → sorting challenges
│   │   ├── serializers.py
│   │   └── views.py
│   │
│   ├── users/                 # Player accounts, COPPA compliance
│   │   ├── models.py          # Player, ParentAccount, AgeGroup
│   │   ├── auth.py            # JWT, session handling
│   │   └── permissions.py
│   │
│   ├── progress/              # What each player has done/earned
│   │   ├── models.py          # Progress, Achievement, Collection
│   │   ├── services.py        # Rank calculation, streak logic, DDA
│   │   └── views.py
│   │
│   ├── leaderboards/          # Redis-backed rankings
│   │   ├── services.py        # ZADD/ZRANGE operations
│   │   └── views.py
│   │
│   ├── media_proxy/           # NASA image proxy + resize + CDN
│   │   ├── views.py           # /media/nasa/<hash>?w=800
│   │   └── processors.py      # Pillow resize, WebP conversion
│   │
│   └── admin_panel/           # Custom admin extensions (see §10)
│       ├── admin.py
│       ├── dashboards.py
│       └── actions.py
│
├── api/                       # DRF viewsets + URL routing
│   ├── v1/
│   │   ├── urls.py
│   │   └── views.py           # Thin — delegates to app services
│   └── throttles.py
│
└── tests/
```

### 7.3 Celery Task Architecture

```python
# apps/nasa_ingest/tasks.py

@shared_task(
    autoretry_for=(RequestException,),
    retry_backoff=60,           # 1min, 2min, 4min...
    retry_backoff_max=3600,     # cap at 1 hour
    max_retries=5,
)
def ingest_apod():
    """Fetch today's APOD, transform, persist, warm cache."""
    raw = APODClient().fetch_today()           # NASA call (uses secret key)
    entry = APODTransformer(raw).to_model()    # Clean + enrich
    entry.save()                               # → Postgres
    JigsawGenerator(entry).create_puzzle()     # Pre-slice image
    QuizGenerator(entry).create_questions()    # Generate 5 quiz Qs
    cache.set('apod:today', APODSerializer(entry).data, timeout=86400)
    MediaProxy.prefetch(entry.image_url)       # Warm CDN
```

**Celery Beat schedule** (in `config/celery.py`):

```python
beat_schedule = {
    'apod-daily':      {'task': 'ingest_apod',      'schedule': crontab(hour=5, minute=0)},
    'neows-hourly':    {'task': 'ingest_neows',     'schedule': crontab(minute=0)},
    'donki-15min':     {'task': 'ingest_donki',     'schedule': crontab(minute='*/15')},
    'epic-6hourly':    {'task': 'ingest_epic',      'schedule': crontab(hour='*/6')},
    'mars-daily':      {'task': 'ingest_mars',      'schedule': crontab(hour=6, minute=0)},
    'exoplanet-weekly':{'task': 'ingest_exoplanets','schedule': crontab(day_of_week=1)},
    'eonet-30min':     {'task': 'ingest_eonet',     'schedule': crontab(minute='*/30')},
}
```

### 7.4 API Endpoints (Frontend-Facing)

The frontend NEVER knows NASA exists. It only knows our game API:

| Endpoint | Purpose | Cache |
|----------|---------|-------|
| `GET /api/v1/nasa/today/` | Today's APOD + NEO count + any active solar events | Redis 1h |
| `GET /api/v1/planets/{id}/` | Planet overview, available missions, gallery | Redis 6h |
| `GET /api/v1/missions/{id}/` | Mission detail: puzzles, quizzes, content | Redis 24h |
| `POST /api/v1/missions/{id}/attempt/` | Submit quiz/puzzle answer | — |
| `GET /api/v1/progress/me/` | Player rank, constellation, collection | Per-user 5min |
| `POST /api/v1/progress/sync/` | Batch sync offline progress | — |
| `GET /api/v1/leaderboard/weekly/` | Top players this week | Redis 5min |
| `GET /api/v1/live/iss/` | ISS position (near-real-time passthrough) | Redis 30s |
| `GET /media/nasa/{hash}?w={px}` | Proxied, resized NASA image | CDN 30d |

### 7.5 Puzzle Generation Pipeline

When NASA content arrives, we **pre-generate** game artifacts so gameplay is instant:

```
APOD image arrives
    ↓
JigsawGenerator
    → Slice into 12, 24, 48 piece sets
    → Store piece coordinates + edge shapes in JSON
    → Upload piece images to S3/CDN
    ↓
QuizGenerator
    → Parse explanation text for facts (dates, distances, names)
    → Generate 5 questions with plausible wrong answers
    → Tag with difficulty (based on vocabulary level)
    ↓
Store as Mission(type='apod_daily', date=today, puzzles=[...], quizzes=[...])
```

---

## 8. Data Model & Persistence

### 8.1 What We Store vs What We Don't

| Store in Postgres | Proxy / Cache Only |
|-------------------|--------------------|
| NASA content metadata (titles, dates, URLs, facts) | Raw NASA JSON blobs (keep 7 days for debugging, then purge) |
| Transformed game content (quizzes, puzzle definitions) | Full-resolution NASA images (proxy + CDN cache) |
| User accounts, progress, achievements | ISS position (too ephemeral — Redis only) |
| Game configuration (mission definitions, reward rules) | Leaderboard rankings (Redis sorted sets) |
| Admin audit logs | Session tokens (Redis with TTL) |

**Principle**: Store what we've *added value to*. Raw NASA data is reproducible from NASA. Our transformations, our users, our game state — that's what we protect.

### 8.2 Core Models

```python
# ─── apps/nasa_ingest/models.py ──────────────────────────────

class NASAContent(models.Model):
    """Base for all ingested NASA content."""
    source_api      = models.CharField(max_length=32)   # 'apod', 'neows', ...
    source_id       = models.CharField(max_length=255)  # NASA's identifier
    raw_url         = models.URLField()
    ingested_at     = models.DateTimeField(auto_now_add=True)
    is_published    = models.BooleanField(default=False) # Admin curation gate
    class Meta: abstract = True

class APODEntry(NASAContent):
    date            = models.DateField(unique=True)
    title           = models.CharField(max_length=255)
    explanation     = models.TextField()
    media_type      = models.CharField(max_length=16)   # 'image' | 'video'
    image_url       = models.URLField()
    hd_image_url    = models.URLField(null=True)
    proxied_url     = models.URLField()                 # Our CDN copy
    copyright       = models.CharField(max_length=255, blank=True)

class NEOObject(NASAContent):
    neo_id              = models.CharField(max_length=32, unique=True)
    name                = models.CharField(max_length=255)
    diameter_min_m      = models.FloatField()
    diameter_max_m      = models.FloatField()
    is_hazardous        = models.BooleanField()
    # Approach data stored separately (one NEO, many approaches)

class NEOApproach(models.Model):
    neo             = models.ForeignKey(NEOObject, related_name='approaches')
    approach_date   = models.DateTimeField()
    velocity_kmh    = models.FloatField()
    miss_distance_km = models.FloatField()
    # Derived fields for gameplay:
    threat_score    = models.IntegerField()             # Computed 0-100
    size_comparison = models.CharField(max_length=64)   # "school bus", "football field"

class MarsPhoto(NASAContent):
    rover           = models.CharField(max_length=32)
    camera          = models.CharField(max_length=32)
    sol             = models.IntegerField()
    earth_date      = models.DateField()
    image_url       = models.URLField()
    proxied_url     = models.URLField()

class Exoplanet(NASAContent):
    name            = models.CharField(max_length=128, unique=True)
    host_star       = models.CharField(max_length=128)
    mass_earth      = models.FloatField(null=True)
    radius_earth    = models.FloatField(null=True)
    orbital_period_days = models.FloatField(null=True)
    equilibrium_temp_k  = models.FloatField(null=True)
    discovery_year  = models.IntegerField()
    # Derived:
    habitability_score = models.IntegerField()          # Computed 0-100
    fun_fact        = models.TextField(blank=True)      # Admin-editable


# ─── apps/games/models.py ────────────────────────────────────

class Game(models.Model):
    """A game type: jigsaw, quiz, rover-drive, etc."""
    slug            = models.SlugField(unique=True)
    name            = models.CharField(max_length=128)
    description     = models.TextField()
    game_type       = models.CharField(max_length=32)   # 'jigsaw', 'quiz', 'action', ...
    min_age_group   = models.CharField(max_length=8)    # '6-8', '9-11', '12-14'
    engine_config   = models.JSONField(default=dict)    # PixiJS scene config
    is_active       = models.BooleanField(default=True)

class Mission(models.Model):
    """A playable unit. Combines content + game mechanic + rewards."""
    slug            = models.SlugField(unique=True)
    title           = models.CharField(max_length=255)
    planet          = models.ForeignKey('Planet', related_name='missions')
    game            = models.ForeignKey(Game)
    # Content linkage — a mission can pull from multiple NASA sources:
    nasa_content    = GenericRelation('MissionContent')
    # Progression:
    difficulty      = models.IntegerField()             # 1-10, used by DDA
    xp_reward       = models.IntegerField()
    prerequisite    = models.ForeignKey('self', null=True, blank=True)
    unlocks         = models.ManyToManyField('Achievement', blank=True)
    # Admin control:
    is_published    = models.BooleanField(default=False)
    featured_until  = models.DateTimeField(null=True)   # Homepage feature

class Quiz(models.Model):
    mission         = models.ForeignKey(Mission, related_name='quizzes')
    question        = models.TextField()
    correct_answer  = models.CharField(max_length=500)
    distractors     = ArrayField(models.CharField(max_length=500), size=3)
    explanation     = models.TextField()                # Shown after answering
    difficulty      = models.IntegerField()
    auto_generated  = models.BooleanField()             # vs admin-written

class JigsawPuzzle(models.Model):
    mission         = models.ForeignKey(Mission, related_name='jigsaws')
    source_image    = models.ForeignKey(APODEntry)      # or MarsPhoto via generic
    piece_count     = models.IntegerField()             # 12, 24, 48
    piece_data      = models.JSONField()                # Coordinates + edge shapes
    pieces_cdn_path = models.CharField(max_length=500)


# ─── apps/users/models.py ────────────────────────────────────

class Player(AbstractUser):
    display_name    = models.CharField(max_length=50)   # Pseudonym, not real name
    age_group       = models.CharField(max_length=8)
    avatar_config   = models.JSONField(default=dict)    # Ship color, astronaut skin
    parent          = models.ForeignKey('ParentAccount', null=True)
    # COPPA: no email for under-13 unless parent-verified
    is_parent_verified = models.BooleanField(default=False)
    created_at      = models.DateTimeField(auto_now_add=True)
    last_active     = models.DateTimeField(null=True)

class ParentAccount(models.Model):
    email           = models.EmailField(unique=True)
    verified        = models.BooleanField(default=False)
    children        = models.ManyToManyField(Player)
    # Parental controls:
    allow_leaderboards  = models.BooleanField(default=False)
    daily_time_limit_min = models.IntegerField(null=True)


# ─── apps/progress/models.py ─────────────────────────────────

class Progress(models.Model):
    player          = models.OneToOneField(Player, related_name='progress')
    rank            = models.CharField(max_length=32, default='cadet')
    total_xp        = models.IntegerField(default=0)
    current_streak  = models.IntegerField(default=0)
    longest_streak  = models.IntegerField(default=0)
    # DDA state:
    skill_estimate  = models.FloatField(default=0.5)    # 0-1, updated per answer
    last_played     = models.DateTimeField(null=True)

class MissionCompletion(models.Model):
    player          = models.ForeignKey(Player)
    mission         = models.ForeignKey(Mission)
    completed_at    = models.DateTimeField(auto_now_add=True)
    score           = models.IntegerField()
    time_seconds    = models.IntegerField()
    attempts        = models.IntegerField(default=1)
    class Meta: unique_together = ('player', 'mission')

class ConstellationNode(models.Model):
    """One star in the player's knowledge constellation."""
    player          = models.ForeignKey(Player, related_name='constellation')
    concept_slug    = models.CharField(max_length=128)  # 'gravity', 'mars-atmosphere'
    unlocked_at     = models.DateTimeField(auto_now_add=True)
    mastery_level   = models.IntegerField(default=1)    # 1-3 stars

class CollectionItem(models.Model):
    player          = models.ForeignKey(Player, related_name='collection')
    item_type       = models.CharField(max_length=32)   # 'apod', 'patch', 'audio', 'blueprint'
    item_id         = models.CharField(max_length=128)
    earned_at       = models.DateTimeField(auto_now_add=True)
    earned_from     = models.ForeignKey(Mission, null=True)
```

### 8.3 Indexes & Query Optimization

Hot paths that need indexes:

```python
# Most frequent queries
APODEntry:        index on (date) — "today's APOD", "last 30 days"
NEOApproach:      index on (approach_date) — "approaching this week"
MissionCompletion: index on (player, completed_at) — "what did I do recently"
Mission:          index on (planet, is_published, difficulty) — mission list per planet
CollectionItem:   index on (player, item_type) — "my APOD gallery"
```

### 8.4 Redis Data Structures

| Key Pattern | Type | Purpose |
|-------------|------|---------|
| `apod:today` | String (JSON) | Serialized today's APOD |
| `neo:feed:{date}` | String (JSON) | This week's approach list |
| `leaderboard:weekly` | Sorted Set | `ZADD score player_id` |
| `leaderboard:planet:{id}` | Sorted Set | Per-planet rankings |
| `session:{token}` | Hash | Session data, TTL 7d |
| `ratelimit:{ip}:{endpoint}` | String | Counter with TTL |
| `dda:{player_id}` | Hash | Recent performance for difficulty adjustment |
| `celery:lock:{task}` | String | Prevent duplicate ingestion runs |

---

## 9. API Key Security & Secrets Management

### 9.1 The Core Rule

**The NASA API key NEVER reaches the browser. Period.**

The browser doesn't know NASA exists. It only knows `api.ourgame.com`. All NASA calls originate from our Django backend — specifically from Celery workers running on our infrastructure.

```
┌─────────┐         ┌─────────────┐         ┌──────────┐
│ Browser │────────▶│  Django API │────────▶│ NASA API │
└─────────┘         └─────────────┘         └──────────┘
     │                     │                      │
  No key            Key loaded from          Validates
  ever sent         secrets manager          our key
                    at process start
```

Even if we wanted to let the browser hit NASA directly (we don't), the NASA key would be extractable from any JavaScript bundle via browser devtools in seconds. There is no such thing as a secret in client-side code.

### 9.2 Secret Storage: Where Keys Live

| Environment | Storage | Access |
|-------------|---------|--------|
| **Local dev** | `.env` file, gitignored | `django-environ` loads into settings |
| **Staging/Prod** | AWS Secrets Manager (or Vault, or GCP Secret Manager) | IAM role on EC2/ECS — no credentials on disk |
| **CI/CD** | GitHub Actions encrypted secrets | Injected as env vars at build time, never logged |

```python
# config/settings/base.py
import environ
env = environ.Env()

# In prod, these are injected from Secrets Manager at container start
NASA_API_KEY    = env('NASA_API_KEY')          # Never has a default
DJANGO_SECRET_KEY = env('DJANGO_SECRET_KEY')
DATABASE_URL    = env.db('DATABASE_URL')
REDIS_URL       = env('REDIS_URL')
```

**Absolute prohibitions:**
- No keys in `settings.py` (even "for testing")
- No keys in git history (use `git-secrets` pre-commit hook to block)
- No keys in Docker images (inject at runtime, not build time)
- No keys in frontend `.env` files (Next.js `NEXT_PUBLIC_*` vars ARE exposed to browser)
- No keys in logs (Django `DEBUG=False` in prod + log scrubbing middleware)

### 9.3 Secret Loading in Production

```python
# config/settings/prod.py — AWS example
import boto3, json

def load_secrets():
    """Called once at process start. IAM role grants access."""
    client = boto3.client('secretsmanager', region_name='us-east-1')
    resp = client.get_secret_value(SecretId='nasa-explorer/prod')
    return json.loads(resp['SecretString'])

_secrets = load_secrets()
NASA_API_KEY      = _secrets['NASA_API_KEY']
DJANGO_SECRET_KEY = _secrets['DJANGO_SECRET_KEY']
# ... etc
```

The ECS task / EC2 instance has an IAM role with `secretsmanager:GetSecretValue` scoped to exactly one secret ARN. No long-lived AWS credentials anywhere.

### 9.4 Key Rotation

| Secret | Rotation Cadence | Method |
|--------|------------------|--------|
| NASA API key | Quarterly (or on suspected leak) | Generate new key on api.nasa.gov → update Secrets Manager → rolling restart workers → revoke old key after 24h overlap |
| Django `SECRET_KEY` | Annually | Dual-key support during rotation (Django 4.1+ `SECRET_KEY_FALLBACKS`) |
| JWT signing key | Quarterly | Key ID (`kid`) in JWT header, accept old+new during overlap window |
| Database password | Quarterly | AWS RDS managed rotation — fully automated |

### 9.5 Frontend ↔ Backend Authentication

The browser authenticates to *our* API, not NASA's:

```
┌─────────────────────────────────────────────────────────┐
│ 1. Player logs in → POST /api/auth/login/               │
│ 2. Django returns JWT in httpOnly, Secure, SameSite     │
│    cookie (NOT localStorage — XSS can't read cookies)   │
│ 3. Browser sends cookie automatically on every request  │
│ 4. Django validates JWT, identifies player, serves data │
│ 5. JWT expires in 1h; refresh token in 7d               │
└─────────────────────────────────────────────────────────┘
```

**JWT claims:**
```json
{
  "sub": "player_12345",
  "age_group": "9-11",
  "rank": "pilot",
  "parent_verified": true,
  "exp": 1234567890
}
```

Why httpOnly cookies over localStorage:
- XSS attacks can't read httpOnly cookies
- CSRF mitigated with `SameSite=Strict` + Django's CSRF token for state-changing requests
- Kids' accounts are a high-value target for trolls — defense in depth matters

### 9.6 Media Proxy: Hiding NASA Image URLs

Even NASA image URLs are kept off the client. Why?
- NASA's CDN isn't sized for our traffic (we'd be a bad citizen)
- We want to resize/WebP-convert images for mobile
- We want consistent cache headers we control

```python
# apps/media_proxy/views.py
class NASAMediaProxy(View):
    """
    GET /media/nasa/{content_hash}?w=800&fmt=webp
    Serves a resized, cached copy of a NASA image.
    Original NASA URL never exposed to browser.
    """
    def get(self, request, content_hash):
        entry = get_object_or_404(APODEntry, content_hash=content_hash)
        width = min(int(request.GET.get('w', 1200)), 2400)

        cache_key = f'media:{content_hash}:{width}'
        if cached_url := cache.get(cache_key):
            return redirect(cached_url)  # Already on our CDN

        # Fetch from NASA (server-side), process, upload to our S3
        processed_url = ImageProcessor(entry.hd_image_url).resize(width).to_webp().upload()
        cache.set(cache_key, processed_url, timeout=86400 * 30)
        return redirect(processed_url)
```

### 9.7 Rate Limiting Our Own API

Protect our backend (and by extension, NASA) from abuse:

```python
# api/throttles.py
class PlayerThrottle(UserRateThrottle):
    rate = '300/hour'       # Generous for normal play

class AnonymousThrottle(AnonRateThrottle):
    rate = '60/hour'        # Enough for onboarding before login

class MissionSubmitThrottle(ScopedRateThrottle):
    scope = 'mission_submit'
    rate = '30/minute'      # Anti-cheat: can't spam-submit answers
```

### 9.8 Security Checklist

- [ ] `.env` in `.gitignore`; `.env.example` committed with placeholder values
- [ ] `git-secrets` pre-commit hook blocks AWS/API key patterns
- [ ] Secrets Manager IAM policy scoped to single ARN, single action
- [ ] `DEBUG = False` in prod; error pages show nothing useful
- [ ] Sentry DSN is public-safe (it's a write-only endpoint) but still env-var'd
- [ ] Log scrubber removes anything matching `key|token|secret|password` patterns
- [ ] HTTPS everywhere; HSTS header set; `SECURE_SSL_REDIRECT = True`
- [ ] CSP header blocks inline scripts (XSS mitigation)
- [ ] `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SESSION_COOKIE_HTTPONLY` all True

---

## 10. Admin Panel

### 10.1 Philosophy

**Extend Django Admin, don't rebuild it.** Django's admin is a decades-refined CRUD interface. We get 80% of our admin panel for free. Custom code only for: dashboards, bulk actions, visual previews, and moderation workflows.

Every single model in §8.2 is registered in admin. Admins can edit *anything* — but with guardrails (permissions, audit logs, soft deletes).

### 10.2 Admin Roles & Permissions

| Role | Can Do | Cannot Do |
|------|--------|-----------|
| **Super Admin** | Everything, including user management and system config | — |
| **Content Curator** | Publish/unpublish NASA content, edit quiz text, write fun facts, feature missions | Touch user data, change game rules |
| **Game Designer** | Create/edit missions, tune difficulty, configure rewards, manage achievements | Touch user PII, system config |
| **Moderator** | View player accounts, ban/suspend, review flagged content, reset progress | Edit game content, see API keys |
| **Analyst** | Read-only dashboard access, export aggregated stats | Change anything |
| **Parent Support** | Look up child accounts by parent email, assist with progress issues | Bulk operations, content |

Implemented via Django Groups + `django-guardian` for object-level permissions where needed (e.g., curators can only edit content they're assigned to).

### 10.3 Admin Sections

```
/admin/
├── Dashboard                  # Landing page — metrics at a glance
│
├── 📡 NASA Content
│   ├── Ingestion Status       # Last run per API, next scheduled, error log
│   ├── APOD Entries           # Browse, preview, publish toggle
│   ├── NEO Objects            # Asteroid browser, threat score override
│   ├── Mars Photos            # Grid view, bulk curation
│   ├── Exoplanets             # Edit fun_fact, adjust habitability
│   ├── Space Weather Events   # DONKI feed
│   └── Media Proxy Cache      # Clear/warm specific images
│
├── 🎮 Games & Missions
│   ├── Game Types             # Jigsaw, quiz, action — engine configs
│   ├── Missions               # Full CRUD + live preview iframe
│   ├── Quizzes                # Edit questions, flag bad auto-gen
│   ├── Jigsaw Puzzles         # Preview piece layout, regenerate
│   ├── Planets/Bodies         # Space map node config
│   ├── Achievements           # Badge design, unlock criteria
│   ├── Reward Rules           # XP values, rank thresholds
│   └── Feature Scheduler      # "Feature Mars Week starting Monday"
│
├── 👥 Users
│   ├── Players                # Search, filter, view progress
│   ├── Parent Accounts        # Verification status, linked children
│   ├── Moderation Queue       # Flagged display names, etc.
│   ├── Bans & Suspensions     # With reason + expiry
│   └── COPPA Compliance       # Under-13 without verification report
│
├── 📊 Analytics
│   ├── Engagement Dashboard   # DAU/MAU, session length, retention
│   ├── Mission Funnel         # Start → complete rates per mission
│   ├── Quiz Difficulty        # Which questions are too hard/easy
│   ├── Content Popularity     # Most-collected APODs, most-played missions
│   ├── DDA Health             # Skill distribution, adjustment frequency
│   └── Export                 # CSV/JSON exports for deeper analysis
│
├── ⚙️ System
│   ├── API Key Status         # Masked display (****abc123), age, usage quota
│   ├── Celery Monitor         # Flower embedded — task queue health
│   ├── Cache Control          # Invalidate Redis keys by pattern
│   ├── Feature Flags          # Toggle features without deploy
│   ├── Maintenance Mode       # "We'll be back soon" switch
│   └── Audit Log              # Every admin action, immutable
│
└── 🔧 Configuration
    ├── Global Settings        # Default age group, XP multipliers
    ├── Content Filters        # Blocked words for display names
    └── Email Templates        # Parent verification emails, etc.
```

### 10.4 Key Custom Admin Features

#### Mission Builder with Live Preview

```python
# apps/admin_panel/admin.py
@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    list_display = ('title', 'planet', 'game', 'difficulty',
                    'completion_rate', 'is_published', 'preview_link')
    list_filter  = ('planet', 'game__game_type', 'is_published', 'difficulty')
    list_editable = ('is_published', 'difficulty')
    search_fields = ('title', 'slug')
    actions = ['publish', 'unpublish', 'clone', 'feature_on_homepage']
    inlines = [QuizInline, JigsawInline, RewardInline]

    def completion_rate(self, obj):
        """Color-coded: red <30%, yellow 30-70%, green >70%"""
        rate = obj.stats.completion_rate
        color = 'green' if rate > 0.7 else 'orange' if rate > 0.3 else 'red'
        return format_html('<b style="color:{}">{:.0%}</b>', color, rate)

    def preview_link(self, obj):
        """Opens iframe loading the actual frontend in preview mode."""
        return format_html(
            '<a href="/admin/preview/mission/{}/" target="_blank">▶ Play</a>',
            obj.id
        )
```

The preview opens the real Next.js frontend inside an iframe with `?preview_token=xxx` — so admins see exactly what players see, before publishing.

#### Ingestion Control Panel

```
┌───────────────────────────────────────────────────────┐
│  NASA Ingestion Status                   [Force Sync] │
├─────────────┬──────────┬──────────┬─────────┬─────────┤
│ API         │ Last Run │ Next Run │ Status  │ Action  │
├─────────────┼──────────┼──────────┼─────────┼─────────┤
│ APOD        │ 2h ago   │ 22h      │ ✓ OK    │ [Run]   │
│ NeoWs       │ 12m ago  │ 48m      │ ✓ OK    │ [Run]   │
│ DONKI       │ 5m ago   │ 10m      │ ✓ OK    │ [Run]   │
│ Mars Rovers │ 3h ago   │ 21h      │ ⚠ Retry │ [Run]   │
│ EPIC        │ 4h ago   │ 2h       │ ✓ OK    │ [Run]   │
│ Exoplanets  │ 2d ago   │ 5d       │ ✓ OK    │ [Run]   │
└─────────────┴──────────┴──────────┴─────────┴─────────┘

Recent Errors:
  [Mars Rovers] 2026-03-17 06:00 — HTTPError 503 (retry 2/5 in 4min)

API Quota: 847 / 1000 requests this hour  [████████░░] 85%
```

#### Feature Flags (Runtime Config)

Powered by `django-waffle` or a simple model + Redis cache:

| Flag | Status | Scope |
|------|--------|-------|
| `leaderboards_enabled` | ON | All players |
| `black_hole_zone` | OFF | Staged for next release |
| `auto_quiz_generation` | ON | — |
| `new_onboarding_flow` | ON for 10% | A/B test |
| `maintenance_mode` | OFF | Kills all gameplay, shows message |

Toggles take effect instantly — no deploy, no restart. Critical for incident response ("turn off the leaderboard, it's showing a bad name").

#### Audit Log (Immutable)

Every admin write goes through `django-auditlog`:

```
2026-03-17 14:23  curator_jane    Mission #42      published=False → True
2026-03-17 14:19  curator_jane    Quiz #891        question="..." → "..."
2026-03-17 13:01  mod_alex        Player #5521     status=active → suspended  reason="inappropriate name"
2026-03-17 11:45  admin_sam       FeatureFlag      leaderboards=True → False
```

Append-only. No admin can delete audit entries (enforced at DB level with row-level security).

### 10.5 Admin Panel Security

- **Separate subdomain**: `admin.ourgame.com` — completely isolated from the game frontend
- **VPN or IP allowlist**: Admin panel not reachable from public internet
- **2FA mandatory**: `django-otp` — TOTP required for all admin logins, no exceptions
- **Short sessions**: 2-hour timeout, re-auth required for destructive actions
- **No API key visibility**: System → API Keys shows `nasa_****xy7q` (last 4 only), never the full key
- **Rate limiting on login**: `django-axes` — 5 failed attempts → 15min lockout
- **Separate database user**: Admin panel connects with a DB role that cannot `DROP` or `TRUNCATE`

---

## 11. Infrastructure, Deployment & Scaling

### 11.1 The Cost Shape of This Architecture

Before picking providers, understand *what scales with what*. Our §6 design gives us an unusually friendly cost curve:

| Cost Driver | Scales With | Shape |
|-------------|-------------|-------|
| **NASA API calls** | Nothing — fixed ~127/hr via Celery | **Flat. $0.** Regardless of 1 user or 10M. |
| **Compute (Django)** | Requests/sec after cache misses | Linear, but >95% Redis hit rate → very shallow slope |
| **Compute (Celery)** | Number of NASA APIs × frequency | **Flat.** Schedule is fixed. One `t3.small` forever. |
| **Compute (Next.js)** | SSR page loads | Linear, but most routes are static-generated → shallow |
| **Database** | Write volume (progress saves, quiz answers) | Linear with active players |
| **Redis** | Concurrent sessions + cached response size | Cheap; memory is the only limit |
| **CDN bandwidth** | Image/asset delivery | **Dominant variable cost.** This is where money goes at scale. |
| **S3 storage** | Total NASA images ingested | Grows ~1GB/month. Negligible. |

**Key insight: bandwidth is the cost.** Everything else is either flat or grows slowly. So we optimize bandwidth aggressively (WebP, responsive images, long cache TTLs) and accept the rest.

### 11.2 Provider Choice: AWS Primary

**Primary stack: AWS.** Not because it's cheapest (it often isn't), but because:

- **Secrets Manager + IAM** — §9 already assumes this. IAM roles for ECS tasks mean zero long-lived credentials.
- **RDS + ElastiCache** — managed Postgres and Redis with automated backups, failover, patching.
- **ECS Fargate** — containers without managing EC2 instances. Scales to zero for dev/staging.
- **CloudFront + S3** — the media pipeline (§6.5) is content-addressed URLs pointing at S3 behind CloudFront. Standard, boring, works.
- **Single vendor for compliance** — one BAA/DPA to sign for GDPR sub-processor agreements (§21).

**Alternatives considered:**

| Option | Why Not Primary | When We'd Use It |
|--------|-----------------|------------------|
| **Render / Railway** | Great DX but less control over networking, IAM, and compliance artifacts | Early MVP/staging before AWS migration |
| **GCP** | Cloud Run is excellent, but we'd rebuild §9 for GCP Secret Manager | If AWS pricing becomes unfavorable |
| **Cloudflare (full stack)** | Workers can't run Django; D1 isn't Postgres-compatible | We DO use Cloudflare as CDN in front of CloudFront (see §11.5) |
| **Self-managed K8s** | Operational overhead we don't need at this scale | Never. Fargate is K8s without the pain. |

### 11.3 Compute Topology

All compute runs as containers on **ECS Fargate** — no EC2 instances to patch, no cluster to manage.

```
┌─────────────────────────────────────────────────────────────────┐
│                         ECS Cluster                              │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ Service: web    │  │ Service: worker │  │ Service: beat   │  │
│  │ Django + Guni.  │  │ Celery worker   │  │ Celery beat     │  │
│  │ 2-20 tasks      │  │ 1-3 tasks       │  │ 1 task (fixed)  │  │
│  │ Auto-scaled     │  │ Mostly idle     │  │ Scheduler only  │  │
│  │ 0.5 vCPU, 1GB   │  │ 0.5 vCPU, 2GB   │  │ 0.25 vCPU, 0.5G │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐                       │
│  │ Service: nextjs │  │ Service: admin  │                       │
│  │ Next.js server  │  │ Django admin    │                       │
│  │ 2-10 tasks      │  │ 1 task (fixed)  │                       │
│  │ Auto-scaled     │  │ Private subnet  │                       │
│  │ 0.5 vCPU, 1GB   │  │ VPN only        │                       │
│  └─────────────────┘  └─────────────────┘                       │
└─────────────────────────────────────────────────────────────────┘
         │                      │
         ▼                      ▼
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│ ALB (public)    │   │ RDS Postgres    │   │ ElastiCache     │
│ → web, nextjs   │   │ db.t3.medium    │   │ Redis           │
│                 │   │ Multi-AZ        │   │ cache.t3.small  │
│ ALB (private)   │   │ + read replica  │   │ (→ cluster mode │
│ → admin         │   │   (analytics)   │   │  when needed)   │
└─────────────────┘   └─────────────────┘   └─────────────────┘
```

**Per-service notes:**

- **`web` (Django API)**: Stateless. Scales horizontally behind the ALB. Health check on `/health/`. This is the only service that auto-scales aggressively.
- **`worker` (Celery)**: Runs NASA ingestion + image processing. Load is schedule-driven, not traffic-driven — 1 task is enough 95% of the time. Scales to 3 only when backlog detected (image variant generation is the one bursty job).
- **`beat` (Celery scheduler)**: Exactly 1 replica. Runs the crontab. Lock in Redis prevents split-brain if it briefly restarts.
- **`nextjs`**: Serves SSR routes + static asset origin. Most routes are pre-rendered (ISR), so this is lightly loaded.
- **`admin`**: Separate Django process, same image, different entrypoint. Private subnet, accessible only via VPN (§10.5). Never scales — if 2 admins feels slow, something is very wrong.

### 11.4 Storage Architecture (S3)

Four buckets, each with a distinct access pattern and lifecycle:

| Bucket | Contents | Access | Lifecycle Policy |
|--------|----------|--------|------------------|
| **`nse-media-prod`** | Processed NASA images (all size variants, §6.5) | Public via CloudFront only (bucket policy blocks direct access) | Keep forever. Images are content-addressed — no staleness. |
| **`nse-assets-prod`** | Next.js build output (JS, CSS, sprites, audio) | Public via CloudFront | Delete objects from builds >5 deploys old |
| **`nse-raw-prod`** | Raw NASA API JSON responses (debugging) | Private, backend only | **Delete after 7 days** — these are reproducible, storing them forever is waste |
| **`nse-backups-prod`** | RDS snapshots, Redis dumps | Private, cross-region replicated | 30 daily → 12 monthly → 3 yearly. Glacier after 90 days. |

**Storage growth projection:**

```
Media bucket growth:
  APOD:     1 image/day × 5 variants × ~200KB avg  = ~1 MB/day
  Mars:     ~20 curated/day × 5 variants × ~150KB  = ~15 MB/day
  EPIC:     ~12 images/day × 3 variants × ~100KB   = ~3.6 MB/day
  ────────────────────────────────────────────────────────
  Total:    ~20 MB/day → ~600 MB/month → ~7 GB/year

  At S3 Standard $0.023/GB/month: Year 1 ≈ $2/mo. Year 5 ≈ $8/mo.
  This is noise. We don't optimize storage costs.
```

**Intelligent-Tiering** on `nse-media-prod`: Old APOD images (>90 days) that nobody views auto-move to Infrequent Access. If a player earns one for their gallery, it moves back. Zero code, saves ~40% on cold objects.

### 11.5 CDN Architecture — Where the Money Goes

Bandwidth is our dominant variable cost. We use a **two-tier CDN** to minimize it:

```
Browser
   │
   ▼
┌─────────────────────────────────────────┐
│  Cloudflare (Tier 1 — outer edge)       │
│  • Free tier: unlimited bandwidth        │
│  • DDoS protection, WAF                  │
│  • 300+ PoPs globally                    │
│  • Absorbs ~85% of requests              │
└─────────────────────────────────────────┘
   │ (cache miss)
   ▼
┌─────────────────────────────────────────┐
│  CloudFront (Tier 2 — origin shield)    │
│  • Single region, close to S3 origin    │
│  • Absorbs ~95% of what Cloudflare      │
│    misses                               │
│  • Pays AWS rates only for true misses  │
└─────────────────────────────────────────┘
   │ (cache miss)
   ▼
┌─────────────────────────────────────────┐
│  Origins:                               │
│  • S3 (media, assets)                   │
│  • ALB → Next.js (SSR pages)            │
│  • ALB → Django (API)                   │
└─────────────────────────────────────────┘
```

**Why two CDN tiers:** Cloudflare's free/pro tier offers unlimited egress bandwidth. CloudFront charges $0.085/GB. If Cloudflare eats 85% of traffic before it hits CloudFront, we pay CloudFront for 15% of what we'd otherwise pay. At scale this is thousands of dollars a month.

**CloudFront behavior configuration:**

| Path Pattern | Origin | Cache Policy | TTL |
|--------------|--------|--------------|-----|
| `/media/*` | S3 `nse-media-prod` | CachingOptimized | 1 year (`immutable`) |
| `/_next/static/*` | S3 `nse-assets-prod` | CachingOptimized | 1 year (`immutable`) |
| `/_next/image/*` | ALB → Next.js | Cache by query string | 30 days |
| `/api/v1/nasa/today/` | ALB → Django | Cache ignoring cookies | 1 hour |
| `/api/v1/planets/*` | ALB → Django | Cache ignoring cookies | 6 hours |
| `/api/v1/missions/*` | ALB → Django | Cache ignoring cookies | 24 hours |
| `/api/v1/progress/*` | ALB → Django | **CachingDisabled** | — (per-user) |
| `/api/v1/live/iss/` | ALB → Django | Cache ignoring cookies | 30 sec |
| `/*` (catch-all) | ALB → Next.js | Cache by path | ISR revalidation |

**Bandwidth discipline — why we obsess over this:**

| Optimization | Saving | Already Covered In |
|--------------|--------|-------|
| WebP instead of JPEG | ~30% smaller | §6.5 |
| Responsive `srcset` — mobile gets 600w not 2400w | ~75% on mobile | §6.5 |
| `immutable` on content-addressed URLs | Zero revalidation requests | §6.5 |
| Brotli compression on API JSON | ~20% smaller than gzip | CloudFront default |
| Service Worker serves repeat visits from disk | Zero bandwidth for return users | §6.2 L1 |

### 11.6 Database & Redis

**RDS PostgreSQL:**

| Setting | Value | Why |
|---------|-------|-----|
| Instance | `db.t3.medium` (2 vCPU, 4GB) to start | Burstable — most queries hit Redis first, DB is quiet |
| Storage | gp3, 50GB, autoscaling to 500GB | gp3 is cheaper than gp2 and we don't need the IOPS |
| Multi-AZ | Yes | Automatic failover. ~2× cost but non-negotiable for prod. |
| Read replica | 1× `db.t3.small` | Analytics queries (admin dashboards) run here, never compete with gameplay writes |
| Backups | 30-day automated + monthly manual → S3 | Point-in-time recovery for "oops" moments |
| Connection pooling | PgBouncer sidecar in each `web` task | Django's per-worker connections waste RDS connection slots |

**ElastiCache Redis:**

| Setting | Value | Why |
|---------|-------|-----|
| Instance | `cache.t3.small` (1.37GB) to start | Hot cache is small: ~50MB of serialized responses + sessions |
| Cluster mode | Disabled initially | Single shard is simpler; enable when memory > 10GB |
| Replicas | 1 | Automatic failover if primary dies |
| Eviction policy | `allkeys-lru` | If memory pressure hits, drop least-used — all our cache data is reproducible from Postgres |
| Persistence | AOF disabled, RDB disabled | It's a cache. Postgres is truth. Rebuilding on restart takes ~30s of cache warming. |

**When to scale up:**

| Component | Trigger | Action |
|-----------|---------|--------|
| RDS | CPU > 60% sustained, or connection count > 80% | Vertical first (`t3.medium` → `t3.large` → `r6g.large`). Read replica for more reads. Sharding is a 2028 problem. |
| Redis | Memory > 75% | Vertical first. Cluster mode only if we exceed single-node max (~400GB). |

### 11.7 Auto-Scaling Policy

Only two services auto-scale. Everything else is fixed or manual.

**Django `web` service:**

```hcl
# Terraform — ECS auto-scaling
resource "aws_appautoscaling_policy" "web_requests" {
  policy_type = "TargetTrackingScaling"
  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ALBRequestCountPerTarget"
    }
    target_value       = 500        # requests/min per task
    scale_out_cooldown = 60         # add tasks quickly
    scale_in_cooldown  = 300        # remove tasks slowly (avoid flapping)
  }
}

# Floor/ceiling
min_capacity = 2                    # always 2 for AZ redundancy
max_capacity = 20                   # ~10k req/min ceiling — if we hit this, celebrate then raise it
```

**Next.js `nextjs` service:** Same pattern, `target_value = 300` (SSR is heavier per-request than API).

**Scheduled scaling for the school-day pattern:**

Our traffic has a predictable shape — kids play after school and on weekends:

```hcl
# Scale up before the 3pm-8pm wave hits
resource "aws_appautoscaling_scheduled_action" "afternoon_prewarm" {
  schedule = "cron(0 14 ? * MON-FRI *)"    # 2pm UTC weekdays
  scalable_target_action {
    min_capacity = 5                        # warm pool
  }
}

resource "aws_appautoscaling_scheduled_action" "night_cooldown" {
  schedule = "cron(0 2 * * ? *)"            # 2am UTC
  scalable_target_action {
    min_capacity = 2                        # back to floor
  }
}
```

**What does NOT auto-scale and why:**

| Service | Why Fixed |
|---------|-----------|
| Celery workers | Load is schedule-driven, not traffic-driven. 1 worker handles the entire NASA ingestion schedule with capacity to spare. |
| Celery beat | Exactly 1 by definition — it's a scheduler. |
| Admin panel | Serves 5 humans. If it needs to scale, something's deeply wrong. |
| RDS / Redis | Vertical scaling, manually triggered by alerts. Auto-scaling databases is a great way to hide a bad query. |

### 11.8 Environments & Infrastructure-as-Code

Three environments, one Terraform codebase:

| Environment | Purpose | Cost Profile |
|-------------|---------|--------------|
| **dev** | Local Docker Compose. No AWS. | $0 |
| **staging** | Full AWS stack, smallest instance sizes, single-AZ, Fargate Spot | ~$80/mo |
| **prod** | Full stack, Multi-AZ, auto-scaled, on-demand + reserved | ~$400/mo at launch, scales with traffic |

**Terraform structure:**

```
infra/
├── modules/
│   ├── network/          # VPC, subnets (public/private), NAT, security groups
│   ├── ecs/              # Cluster, services, task definitions, auto-scaling
│   ├── rds/              # Postgres, replica, parameter group, backup config
│   ├── elasticache/      # Redis, subnet group
│   ├── s3/               # Four buckets + lifecycle policies + bucket policies
│   ├── cloudfront/       # Distribution, behaviors, origin access identity
│   ├── iam/              # Task roles, Secrets Manager policies
│   └── monitoring/       # CloudWatch dashboards, alarms, SNS → PagerDuty
├── environments/
│   ├── staging/
│   │   ├── main.tf       # Instantiates modules with staging sizing
│   │   └── terraform.tfvars
│   └── prod/
│       ├── main.tf       # Same modules, prod sizing
│       └── terraform.tfvars
└── global/
    └── route53/          # DNS — shared across environments
```

**State backend:** S3 + DynamoDB lock table. One state file per environment. `terraform plan` required in PR before `apply` runs in CI.

**CI/CD (GitHub Actions):**

```
Push to main
  → Build Docker images (Django, Next.js)
  → Push to ECR with git SHA tag
  → terraform plan on staging → auto-apply
  → Run integration tests against staging
  → Manual approval gate
  → terraform apply on prod (rolling deployment, ECS handles it)
  → Smoke test prod /health/
  → If smoke fails: auto-rollback to previous task definition
```

### 11.9 Cost Projections & Guardrails

Monthly cost by traffic tier:

| Component | Launch (1K DAU) | Growth (50K DAU) | Scale (500K DAU) |
|-----------|-----------------|------------------|------------------|
| ECS Fargate (`web` + `nextjs`) | $120 | $800 | $4,500 |
| ECS Fargate (`worker` + `beat` + `admin`) | $45 | $45 | $45 ← flat |
| RDS Postgres (Multi-AZ + replica) | $140 | $280 | $900 |
| ElastiCache Redis | $25 | $50 | $200 |
| S3 storage | $1 | $3 | $8 ← negligible |
| CloudFront egress (after Cloudflare absorbs 85%) | $20 | $600 | $4,000 |
| Cloudflare | $0 (free) | $20 (Pro) | $200 (Business) |
| ALB | $20 | $40 | $150 |
| NAT Gateway | $35 | $35 | $35 ← flat |
| Secrets Manager, CloudWatch, Route53 | $15 | $25 | $50 |
| **Total** | **~$420/mo** | **~$1,900/mo** | **~$10,100/mo** |
| **Per DAU** | $0.42 | $0.038 | $0.020 |

Per-user cost drops 20× from launch to scale — fixed costs get amortized and cache hit rates improve with more traffic.

**Cost discipline tactics:**

| Tactic | Saving | Effort |
|--------|--------|--------|
| **Fargate Spot for Celery workers** | 70% off worker compute | One Terraform flag. Ingestion tasks are retry-safe, interruption is fine. |
| **1-year Compute Savings Plan** on baseline (`min_capacity` tasks) | ~30% off the always-on floor | Commit after 3 months of stable traffic data |
| **1-year Reserved Instance** on RDS | ~40% off database | Same — commit after baseline is known |
| **S3 Intelligent-Tiering** | ~40% on media >90 days old | Zero effort, enable and forget |
| **Cloudflare in front of CloudFront** | ~85% off egress | Already in §11.5 — this is the big one |
| **NAT Gateway → NAT Instance** | ~$30/mo | Only if NAT becomes material. Usually not worth the ops. |

**Budget alarms (CloudWatch → SNS → Slack):**

```hcl
resource "aws_budgets_budget" "monthly" {
  budget_type  = "COST"
  limit_amount = var.monthly_budget        # set per environment

  # Warn at 70%, alert at 90%, page at 110% of forecast
  notification { threshold = 70;  notification_type = "FORECASTED" }
  notification { threshold = 90;  notification_type = "FORECASTED" }
  notification { threshold = 110; notification_type = "ACTUAL" }      # → PagerDuty
}
```

### 11.10 Disaster Recovery

| Scenario | RTO | RPO | Mechanism |
|----------|-----|-----|-----------|
| Single ECS task dies | ~30s | 0 | ECS restarts it. ALB health check routes around it. Non-event. |
| Entire AZ fails | ~2min | 0 | Multi-AZ RDS fails over. ECS tasks in surviving AZ absorb load. Auto-scaling backfills. |
| RDS primary corrupted | ~10min | ≤5min | Point-in-time recovery from automated backups |
| Redis dies | ~1min | Full cache loss | Replica promotes. Cache rebuilds from Postgres in ~30s via warming tasks. No user-visible data loss — Redis is not source of truth. |
| Region-wide outage | ~4hr | ≤24hr | Manual restore from cross-region S3 backup replication. Terraform rebuilds infra in secondary region. Not automated — probability × cost doesn't justify active-active yet. |
| Bad deploy breaks prod | ~5min | 0 | CI auto-rollback on smoke test failure. Manual rollback = one `aws ecs update-service --task-definition previous` command. |
| NASA API permanently shuts down | ∞ | 0 for existing content | §6.7 — Postgres has years archived. Game runs indefinitely on archive. Only new daily content stops. |

**Quarterly DR drill:** Restore staging from prod backup. Time it. If RTO target missed, fix the runbook.

### 11.11 Observability

Already sketched in §6.8; here's the infrastructure side:

| Layer | Tool | What We Watch |
|-------|------|---------------|
| **Infrastructure** | CloudWatch | ECS CPU/memory per service, RDS connections/CPU/IOPS, Redis memory/evictions, ALB 5xx rate |
| **Application** | Sentry | Exceptions (PII-scrubbed per §21), performance traces, release health |
| **Business** | Custom Django → Prometheus → Grafana | DAU, mission completion rate, Redis hit rate, NASA quota consumption, p50/p99 latency |
| **Cost** | AWS Cost Explorer + Budgets | Daily spend by service tag, forecast vs actual |
| **Uptime** | External: UptimeRobot or Pingdom | Black-box probe of `/health/` from outside AWS — catches "AWS says healthy but DNS is broken" |

**On-call:** PagerDuty. Pages on: 5xx rate > 1% for 5min, any RDS failover event, budget forecast > 110%, NASA circuit breaker open > 30min, external health check down > 2min.

---

# Part III — Frontend

## 12. Frontend Architecture

### 12.1 Hybrid: UI Framework + Canvas Engine

Traditional UI framework as shell, HTML5 Canvas engine embedded for gameplay:

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **App Shell & Routing** | React (Next.js) | SSR for SEO, routing, auth, accessibility |
| **Game Viewport** | PixiJS (Canvas/WebGL) | Hardware-accelerated rendering for gameplay |
| **Data Visualizations** | D3.js + Three.js | D3 for 2D charts, Three.js for 3D orbits |
| **Educational Content** | Standard HTML/CSS in React | Rich text, quizzes, forms — DOM is best here |

**Why hybrid:**
- Pure game framework → educational content painful, accessibility poor
- Pure React → struggles with 60fps sprites, particles, real-time physics
- Hybrid → each layer uses the right tool; game canvas is just a React component

### 12.2 Technology Summary

| Decision | Choice | Why |
|----------|--------|-----|
| App framework | React + Next.js | SSR, image optimization, API routes, ecosystem |
| Game engine | PixiJS | Fast 2D WebGL, embeds cleanly via `@pixi/react` |
| Visualizations | D3.js + Three.js | Best-in-class for each use case |
| State | Zustand | Lightweight, works across React and game bridge |
| Styling | Tailwind + CSS custom properties | Utility-first with theme tokens |
| Animation (DOM) | Framer Motion | Declarative, interruptible, reduced-motion aware |
| Audio | Howler.js | Cross-browser Web Audio, sprite sheets, spatial |
| API client | TanStack Query | Cache, dedupe, background refetch, offline |

---

## 13. Game Engine & Technology

### 13.1 Engine Choice: PixiJS

Why PixiJS over alternatives:
- ~150KB vs Phaser ~1MB vs Unity WebGL 5MB+
- Pure renderer — add only systems we need
- WebGL with Canvas fallback
- Excellent sprite, particle, filter support
- `@pixi/react` for clean React integration

Supplement with Phaser only if gameplay needs built-in physics/tilemaps.

### 13.2 Viewport Architecture

```
┌──────────────── React Shell ────────────────┐
│  Navigation, HUD overlays, educational UI   │
│  ┌────────────────────────────────────────┐  │
│  │         PixiJS Canvas Viewport         │  │
│  │  ┌──────────┐  ┌───────────────────┐   │  │
│  │  │ Entities │  │ Particle Systems  │   │  │
│  │  │ (ships,  │  │ (thrust, stars,   │   │  │
│  │  │ planets) │  │  explosions)      │   │  │
│  │  └──────────┘  └───────────────────┘   │  │
│  │  ┌──────────────────────────────────┐  │  │
│  │  │    Interaction Layer (clicks,    │  │  │
│  │  │    drags, touch gestures)        │  │  │
│  │  └──────────────────────────────────┘  │  │
│  └────────────────────────────────────────┘  │
│  Score counter, quiz overlay, lesson drawer  │
└──────────────────────────────────────────────┘
```

### 13.3 React ↔ Game Bridge

```ts
// src/modules/game/bridge/GameBridge.ts
type GameEvent =
  | { type: 'LEVEL_COMPLETE'; score: number }
  | { type: 'NASA_DATA_NEEDED'; dataset: string }
  | { type: 'SHOW_LESSON'; lessonId: string }
  | { type: 'ACHIEVEMENT_EARNED'; id: string }
  | { type: 'SOUND_PLAY'; sound: string };

type GameCommand =
  | { type: 'START_LEVEL'; levelId: string }
  | { type: 'PAUSE' }
  | { type: 'INJECT_NASA_DATA'; data: NASADataset }
  | { type: 'UPDATE_DIFFICULTY'; level: number };

class GameBridge extends EventEmitter {
  sendToGame(command: GameCommand): void { /* ... */ }
  emitToUI(event: GameEvent): void { /* ... */ }
}
```

Game engine fully decoupled — swap PixiJS for Phaser without touching other modules.

---

## 14. Module Separation & Project Structure

```
frontend/src/
├── modules/
│   ├── education/              # Layer 1: Educational Content
│   │   ├── components/         # Lesson cards, quizzes, progress bars
│   │   ├── content/            # Lesson data (JSON/MDX)
│   │   └── hooks/              # useLesson, useProgress
│   │
│   ├── game/                   # Layer 2: Game Engine
│   │   ├── engine/             # PixiJS setup, game loop
│   │   ├── scenes/             # Space map, mission scenes
│   │   ├── entities/           # Ship, planets, collectibles
│   │   ├── systems/            # Physics, scoring, collision, DDA
│   │   ├── audio/              # Howler.js setup, sprites, mixer
│   │   ├── animations/         # Sprite sheets, particle configs
│   │   └── bridge/             # React ↔ Game event bus
│   │
│   └── nasa-data/              # Layer 3: NASA Visualizations
│       ├── api/                # Clients for OUR Django API (not NASA)
│       ├── transforms/         # API response → visualization-ready
│       ├── visualizations/     # D3/Three.js components
│       └── cache/              # TanStack Query configs
│
├── shared/
│   ├── theme/                  # Color tokens, typography, spacing
│   ├── components/             # UI primitives (Button, Card, Modal)
│   ├── animations/             # Framer Motion variants
│   ├── state/                  # Zustand stores
│   └── types/                  # Shared TypeScript interfaces
│
├── app/                        # Next.js app directory
│   ├── (space-map)/
│   ├── (planet)/[planetId]/
│   ├── (missions)/
│   ├── (profile)/
│   └── layout.tsx
│
└── assets/
    ├── sprites/
    ├── audio/
    ├── images/
    └── fonts/
```

**Separation principle**: Modules communicate only through shared state or event bus — never direct cross-module imports.

```
┌─────────────────────────────────────────────┐
│                  App Shell                   │
│          (Next.js + React Router)            │
├──────────┬──────────────┬───────────────────┤
│Education │  Game Engine  │  NASA Data Viz    │
│  (DOM)   │  (Canvas)     │  (D3/Three.js)   │
├──────────┴──────────────┴───────────────────┤
│           Shared State (Zustand)             │
│    (progress, score, NASA data, settings)    │
└─────────────────────────────────────────────┘
```

---

## 15. State Management & Module Communication

### 15.1 Zustand Stores

```ts
interface ProgressStore {
  rank: Rank;
  completedMissions: string[];
  constellation: ConstellationNode[];
  collection: CollectibleItem[];
  currentStreak: number;
}

interface GameStore {
  currentScene: string;
  score: number;
  difficulty: number;   // DDA-adjusted
  isPaused: boolean;
}

interface NASAStore {
  apod: APODEntry | null;
  neoFeed: NEOEntry[];
  issPosition: { lat: number; lng: number } | null;
  lastFetched: Record<string, number>;
}

interface SettingsStore {
  ageGroup: '6-8' | '9-11' | '12-14';
  volume: { master: number; music: number; sfx: number; voice: number };
  reducedMotion: boolean;
  highContrast: boolean;
}
```

### 15.2 Data Flow Example

```
Child clicks Mars on Space Map
  → React navigates to /planet/mars
  → TanStack Query fetches /api/v1/planets/mars/ (Django, cached)
  → Game Bridge sends START_SCENE to PixiJS
  → PixiJS renders Mars approach animation
  → Howler crossfades to Mars ambient theme
  → Education module renders Mars lesson content
  → All three layers render simultaneously, independently
```

---

# Part IV — Look, Feel & Sound

## 16. Theme & Color Palette

Space/NASA-inspired — vibrant enough to excite, dark enough to feel like space, high contrast for readability.

```ts
// src/shared/theme/tokens.ts
export const palette = {
  // Core backgrounds
  spaceBlack:    '#0B0D17',   // Primary bg — deep space
  deepNavy:      '#1B2735',   // Card/panel bg
  midnightBlue:  '#162447',   // Secondary surfaces

  // Primary interactive
  cosmicBlue:    '#2E86AB',   // Buttons, links
  nasaBlue:      '#105BD8',   // Official NASA blue

  // Accents
  nebulaPurple:  '#7B2D8E',   // Discovery moments
  marsRust:      '#C1440E',   // Mars content, warm accent
  solarGold:     '#F0A500',   // Achievements, rewards
  auroraGreen:   '#2ECC71',   // Correct answers
  cometTeal:     '#1ABC9C',   // Secondary interactive

  // Functional
  starWhite:     '#E8E8E8',   // Primary text
  lunarGray:     '#9BA3AF',   // Secondary text
  alertRed:      '#E74C3C',   // Errors

  // Surfaces & effects
  panelBg:       'rgba(27, 39, 53, 0.85)',
  panelBorder:   'rgba(46, 134, 171, 0.3)',
  overlay:       'rgba(11, 13, 23, 0.7)',
  glowBlue:      'rgba(46, 134, 171, 0.4)',
  glowGold:      'rgba(240, 165, 0, 0.4)',
};
```

**Usage rules:**
- Backgrounds always dark — never white pages
- Interactive = `cosmicBlue` with `glowBlue` hover
- Rewards = always `solarGold` (Pavlovian association)
- Each planet gets signature accent (Mars=rust, Earth=teal, Jupiter=gold bands)
- WCAG AA contrast minimum on all text

---

## 17. Typography & Visual Identity

```ts
export const typography = {
  heading: '"Orbitron", sans-serif',        // Mission-control feel
  body:    '"Nunito", sans-serif',          // Rounded, child-friendly
  mono:    '"JetBrains Mono", monospace',   // Data/coordinates
};

export const fontSizes = {
  xs:   '0.75rem',   sm:   '0.875rem',  base: '1rem',
  lg:   '1.25rem',   xl:   '1.5rem',    '2xl':'2rem',   '3xl':'2.5rem',
};
```

- Nunito over Inter — rounded terminals friendlier for kids
- Minimum body text 16px — scaled up for ages 6-8

---

## 18. Visual Design System

### 18.1 Backgrounds & Environment

Every screen is a living spaceship window:
- **Parallax star field**: Layers shift on scroll/mouse
- **Nebula gradients**: Animated purple/blue/teal overlays
- **Planetary ambiance**: Mars warms with rust, Jupiter swirls
- **Day/night cycle**: Subtly darker at night, dawn glow in morning

### 18.2 Component Styles

| Component | Style |
|-----------|-------|
| Cards | Glassmorphism, blur backdrop, glowing border |
| Buttons | Rounded 12px, glow on hover, scale on press |
| Modals | Slide-up mobile, fade-scale desktop |
| Progress bars | Rocket icon on dotted orbital path |
| Badges | Circular, metallic sheen, particle burst on earn |
| Tooltips | Speech-bubble with astronaut character |

### 18.3 Illustration Style

- Semi-realistic with friendly softness
- Real NASA imagery as backdrops, illustrated overlays for interactives
- Characters: rounded, expressive, large eyes

### 18.4 Age-Adaptive Visuals

| Element | Ages 6-8 | Ages 9-11 | Ages 12-14 |
|---------|----------|-----------|------------|
| Colors | Brighter, saturated | Standard | Slightly desaturated |
| Icons | Large, labeled | Icon + short label | Compact, tooltip |
| Characters | Always visible | On hints | On request |
| Data | Pictographs | Simple charts | Full visualizations |

---

## 19. Animation System

### 19.1 Three Purposes (Cut Everything Else)

1. **Feedback** — confirm action happened
2. **Orientation** — show where things came from/went
3. **Delight** — reward moments

### 19.2 Micro-Interactions (Framer Motion)

| Interaction | Animation | Duration |
|-------------|-----------|----------|
| Button hover | Glow expand + scale(1.03) | 200ms ease-out |
| Button press | Scale(0.97) + glow intensify | 100ms ease-in |
| Card appear | Fade + translateY(20→0) | 300ms, stagger 50ms |
| Page transition | Fade+slide left; new slides from right | 400ms spring |
| Correct answer | Green flash + checkmark draws in | 500ms |
| Wrong answer | Gentle shake ±4px + orange (not red) | 400ms |
| Loading | Pulsing skeleton with star twinkle | Loop |

### 19.3 Game Animations (PixiJS, 60fps)

| Element | Animation |
|---------|-----------|
| Rocket thrust | Particle flame trail |
| Planet approach | Scale-up + atmospheric glow |
| Orbit paths | Dashed lines draw progressively |
| Warp travel | Star field stretches into lines |
| Collectible pickup | Spirals to UI counter with trail |

### 19.4 Reward Animations (High Fidelity)

| Moment | Animation |
|--------|-----------|
| Achievement | Badge drops, bounces, particle burst, glow pulse 3× |
| Level complete | Stars sweep, score counts up, rank stamps down |
| Discovery | "Discovery!" zooms in, NASA image fades behind, music swells |
| Streak bonus | Fire trail on counter, combo text scales |

### 19.5 Performance Budget

- Max 3 simultaneous DOM transitions per screen
- 60fps target; reduce particles on low-end devices
- Respect `prefers-reduced-motion` → instant opacity only
- No autoplay video

---

## 20. Sound Design

### 20.1 Philosophy

**Friendly space cockpit.** Soft beeps, warm synths, real NASA clips. Never jarring.

### 20.2 Categories

**Ambient Music**
- Exploration: Soft synth pads, slow arpeggios. Per-planet texture.
- Mission: Slightly rhythmic, tempo increases near completion.
- Reward: Short major-key fanfares, 2-4s.
- Default 30% volume, subordinate to SFX/narration.

**UI Sound Effects**

| Action | Sound | Character |
|--------|-------|-----------|
| Click | Soft sine-wave blip | Friendly |
| Hover | Very quiet tick | Subconscious |
| Transition | Gentle whoosh | Spaceship corridor |
| Card expand | Mechanical "shhhk" | Hydraulic |
| Error | Low gentle bonk | Not punishing |
| Success | Ascending 3-note chime | Warm |
| Notification | Radar ping | Mission control |

**Game SFX**

| Event | Sound |
|-------|-------|
| Thrust | Low rumble + high crackle |
| Collect | Crystalline ding, pitch rises with streak |
| Achievement | Brass stab + sparkle + subtle cheer |
| Discovery | NASA beeps + orchestral swell |
| Warp | Rising sweep + bass drop on arrival |

**NASA Authentic Audio**
Apollo countdown, "Houston..." comms, rover sounds, telemetry beeps — as unlockable collectibles and ambient flavor.

### 20.3 Controls

- Master slider always accessible
- Separate: Music | SFX | Voice
- Defaults: SFX 70%, Music 30%, Voice 100%
- Respect system silent mode
- Howler.js for implementation

---

# Part V — Privacy, Safety & Compliance

## 21. Children's Privacy & Data Protection (COPPA/GDPR-K)

### 21.1 Why This Section Is Non-Negotiable

Our primary users are children ages 6–14. This puts us squarely under the strictest data protection laws on the planet:

| Law | Jurisdiction | Applies To | Penalty for Violation |
|-----|-------------|------------|----------------------|
| **COPPA** (Children's Online Privacy Protection Act) | USA | Children under 13 | Up to **$50,120 per violation** (FTC-enforced) |
| **GDPR Article 8 / GDPR-K** | EU/EEA | Children under 16 (member states may lower to 13) | Up to **4% of global annual revenue** or €20M |
| **UK Children's Code** (Age Appropriate Design Code) | UK | Under 18 | ICO enforcement, significant fines |
| **CCPA/CPRA** | California | Under 16 | $7,500 per intentional violation |
| **LGPD** | Brazil | Under 12 requires parental consent | Up to 2% of revenue |
| **PIPL** | China | Under 14 | Up to ¥50M or 5% of revenue |

**Our principle: design for the strictest law, then everyone is covered.** We treat ALL users under 13 as COPPA-protected. We treat ALL users under 16 as GDPR-K protected. We don't build separate compliance per jurisdiction — we build one high-watermark standard.

### 21.2 Data Minimization: What We Collect vs What We Don't

The safest data is data we never collect. Every field must pass the test: *"Does the game break without this?"*

#### What We DO Collect

| Data | Why We Need It | Storage | Retention |
|------|---------------|---------|-----------|
| Display name (pseudonym) | Leaderboards, personalization | Postgres, encrypted | Until account deletion |
| Age group (band, not birthdate) | Content difficulty, COPPA gating | Postgres | Until account deletion |
| Avatar config (colors, ship) | Personalization | Postgres | Until account deletion |
| Game progress, scores, streaks | Core gameplay | Postgres + IndexedDB | Until account deletion |
| Quiz answers (aggregate) | DDA, content improvement | Postgres (anonymized after 90d) | 90 days linked, then aggregated |
| Parent email (for verified accounts) | COPPA verification, account recovery | Postgres, encrypted at rest | Until parent requests deletion |
| Session tokens | Authentication | Redis, TTL 7d | Auto-expire |

#### What We DO NOT Collect — Ever

| Data | Why Not |
|------|---------|
| **Real name** | Not needed. Pseudonym works for everything. |
| **Birthdate** | Age *group* selector is sufficient. Exact birthdate is unnecessary PII. |
| **Email of child** | COPPA prohibits collecting child email without verifiable parental consent. We don't even offer the field. |
| **Location (GPS)** | Not needed for any game mechanic. |
| **Photos/videos of child** | Avatar is config-based (pick colors/shapes), not photo-based. |
| **Contacts/friend lists** | Social features use anonymous shared progress, not friend graphs. |
| **Device identifiers** | No IDFA, GAID, or fingerprinting. Session tokens are sufficient. |
| **Browsing history outside our app** | No third-party tracking pixels, no ad networks, no analytics that track cross-site. |
| **Voice recordings** | No voice input features. Text only. |
| **Chat messages** | No free-text chat between children (see §21). |

### 21.3 Verifiable Parental Consent (VPC)

COPPA requires **verifiable parental consent before collecting personal information from children under 13**. Our implementation:

#### The Consent Flow

```
Child creates account
  → Age group selector: "How old are you?" [6-8] [9-11] [12-14] [15+]
  │
  ├─ Selected 6-8 or 9-11 (under 13):
  │   → "Ask a grown-up to help!" screen
  │   → Parent enters their email
  │   → We send verification email with:
  │       • One-time link (expires 48h)
  │       • Clear description of what we collect
  │       • Option to approve or deny
  │   → Parent clicks link → shown consent form:
  │       "NASA Space Explorer would like to:"
  │       ☑ Store your child's display name and game progress
  │       ☑ Show your child's pseudonym on optional leaderboards
  │       ☐ Send your child educational mission reminders (opt-in)
  │       [I Consent] [I Do Not Consent]
  │   → Consent recorded with timestamp, parent IP, consent version
  │
  │   BEFORE consent arrives:
  │   → Child CAN play (guest mode — local IndexedDB only)
  │   → Child CANNOT appear on leaderboards
  │   → Child CANNOT have a persistent cloud account
  │   → No data leaves the device
  │
  ├─ Selected 12-14:
  │   → Parental consent still recommended (GDPR-K covers up to 16)
  │   → Reduced data collection by default
  │   → Leaderboards require email verification (not parent, but verified)
  │
  └─ Selected 15+:
      → Standard account creation
      → Still minimal data collection (our principle, not just law)
```

#### FTC-Approved Consent Methods

We support multiple verification methods (FTC approves these):

| Method | How It Works | Our Implementation |
|--------|-------------|-------------------|
| **Email Plus** | Parental email + confirmation activity | Parent email → consent link → must click within 48h |
| **Credit Card Transaction** | Small charge ($0.50) refunded | Stripe integration, charge description says "NASA Space Explorer parental verification" |
| **Government ID Check** | Photo ID scan + discard | Third-party service (Yoti/Veriff), we store only "verified=true", never the ID image |
| **Knowledge-Based Verification** | Questions only a parent would know | Integration with identity service for backup |

**Primary method**: Email Plus (lowest friction, FTC-accepted for most data uses).
**Escalated method**: Credit card or ID check — required only if we want to share data with third parties (we don't plan to, but built in for future-proofing).

### 21.4 Data Architecture: Privacy by Design

Privacy isn't a layer — it's baked into the Django models, API, and infrastructure.

#### Encryption

```python
# apps/users/models.py
from django_cryptography.fields import encrypt

class Player(AbstractUser):
    display_name     = models.CharField(max_length=50)          # Pseudonym, NOT encrypted (public)
    age_group        = models.CharField(max_length=8)           # Band only, not birthdate
    avatar_config    = models.JSONField(default=dict)
    parent           = models.ForeignKey('ParentAccount', null=True)
    is_parent_verified = models.BooleanField(default=False)
    # No email field on Player for under-13

class ParentAccount(models.Model):
    email            = encrypt(models.EmailField(unique=True))  # Encrypted at rest
    verified         = models.BooleanField(default=False)
    consent_version  = models.CharField(max_length=16)          # "v2.1" — tracks which consent form they signed
    consent_date     = models.DateTimeField()
    consent_ip       = encrypt(models.GenericIPAddressField())   # Encrypted, kept for legal proof
    children         = models.ManyToManyField(Player)
    # Parental controls:
    allow_leaderboards   = models.BooleanField(default=False)
    allow_reminders      = models.BooleanField(default=False)
    daily_time_limit_min = models.IntegerField(null=True)
```

#### Pseudonymization Pipeline

Every place where a child's data might surface outside their own session:

```
Leaderboard entry:
  Stored:    player_id=12345, display_name="CosmicPilot42", score=8700
  Displayed: "CosmicPilot42 — 8,700 pts"
  NEVER:     Any linkable identifier, age, or real name

Analytics event:
  Stored:    anonymous_session_hash, event_type="quiz_answer", is_correct=true, difficulty=3
  NEVER:     player_id, display_name, age_group (stripped before analytics pipeline)

Error log (Sentry):
  Stored:    error_type, stack_trace, browser_version
  NEVER:     player_id, session_token, IP (Sentry configured with beforeSend scrubber)
```

#### Right to Deletion (GDPR Article 17 / COPPA)

Parents (or the child, once over 13/16) can request full deletion:

```python
# apps/users/services.py
class AccountDeletionService:
    """
    GDPR Article 17 + COPPA deletion.
    Must complete within 30 days of request (GDPR) / "promptly" (COPPA).
    We target 72 hours.
    """
    def delete_player(self, player_id: int):
        player = Player.objects.get(id=player_id)

        # 1. Delete all linked data
        MissionCompletion.objects.filter(player=player).delete()
        ConstellationNode.objects.filter(player=player).delete()
        CollectionItem.objects.filter(player=player).delete()
        Progress.objects.filter(player=player).delete()

        # 2. Remove from leaderboards
        redis_client.zrem('leaderboard:weekly', player_id)
        for planet in Planet.objects.all():
            redis_client.zrem(f'leaderboard:planet:{planet.id}', player_id)

        # 3. Anonymize any remaining references
        # (e.g., if aggregated quiz stats reference this player)
        AuditLog.objects.filter(player=player).update(
            player=None, anonymized=True
        )

        # 4. Delete the account
        player.delete()  # CASCADE handles FKs

        # 5. Log deletion (for compliance proof, not for tracking)
        DeletionLog.objects.create(
            request_date=now(),
            completion_date=now(),
            data_categories_deleted=[
                'profile', 'progress', 'collection',
                'leaderboard', 'quiz_history'
            ]
        )
```

Accessible via: Admin panel (Parent Support role) → "Delete Account" action, with mandatory confirmation.
Also accessible via: Settings → Parental Controls → "Delete My Child's Account" (self-service).

### 21.5 Consent Management Dashboard

In the admin panel (§10), under Users → COPPA Compliance:

```
┌────────────────────────────────────────────────────────────┐
│  COPPA Compliance Dashboard                                │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Total players under 13:           4,231                   │
│  Parent-verified:                  3,812 (90.1%)           │
│  Pending verification (< 48h):       287 (6.8%)           │
│  Unverified (> 48h, guest only):     132 (3.1%)           │
│                                                            │
│  Consent version distribution:                             │
│    v2.1 (current):   3,400                                 │
│    v2.0 (outdated):    412  ⚠ Re-consent needed            │
│                                                            │
│  Pending deletion requests:          3                     │
│    Oldest: 2 days ago (within 72h SLA ✓)                   │
│                                                            │
│  [Export Compliance Report]  [Send Re-consent Emails]      │
└────────────────────────────────────────────────────────────┘
```

When we update our privacy policy or consent form, players on old consent versions are flagged. Parents receive an email asking them to review and re-consent. Until they do, features that rely on the new consent scope are disabled for that child.

### 21.6 Third-Party Services: Zero Child Data Sharing

| Service | Data It Sees | Child PII? |
|---------|-------------|------------|
| **Sentry** (error tracking) | Stack traces, browser info | NO — `beforeSend` scrubs all user identifiers |
| **Plausible** or self-hosted analytics | Page views, referrer, country | NO — cookieless, no user-level tracking |
| **Stripe** (parental verification) | Parent's payment info only | NO — child data never touches Stripe |
| **CloudFront CDN** | Request IPs (in access logs) | Logs disabled or anonymized (last octet zeroed) |
| **AWS infrastructure** | Encrypted data at rest | DPA signed; see §11 for full infrastructure details |

**We do not use:**
- Google Analytics (tracks users cross-site)
- Facebook Pixel (shares data with Meta)
- Any ad network (no ads, period)
- Any social login (Google/Facebook/Apple Sign-In) for under-13 accounts

### 21.7 Privacy Policy Requirements

The privacy policy must be:
- Written at a **6th-grade reading level** (required by COPPA for the children's version)
- Available in a **child-friendly summary** ("Here's what we know about you: your space name and your game scores. That's it!")
- Available in a **full legal version** for parents
- Accessible from every screen (footer link, always visible)
- Includes: what we collect, why, who sees it, how long we keep it, how to delete
- Updated and re-consented whenever collection practices change

### 21.8 Compliance Checklist

- [ ] No personal data collected from under-13 without VPC
- [ ] Guest mode works fully without any data collection
- [ ] Parent can review all data collected about their child (COPPA §312.6)
- [ ] Parent can revoke consent and trigger deletion at any time
- [ ] Deletion completes within 72 hours
- [ ] No behavioral advertising or data monetization
- [ ] No third-party data sharing without explicit consent
- [ ] Privacy policy at 6th-grade reading level
- [ ] Age gate cannot be bypassed by changing answer (cookie remembers for 24h)
- [ ] Consent form versioned; policy changes trigger re-consent
- [ ] Annual COPPA compliance audit scheduled
- [ ] Data Processing Agreement (DPA) signed with all sub-processors
- [ ] Privacy Impact Assessment (PIA) completed before launch

---

## 22. Content Moderation & Child Safety

### 22.1 Threat Model: What Are We Protecting Against?

| Threat | Vector | Severity |
|--------|--------|----------|
| **Inappropriate display names** | Account creation, name change | High — visible to other children on leaderboards |
| **Adult/violent content in NASA images** | Some APOD images show violent cosmic events; image descriptions may use complex/scary language | Medium — contextual, but we control it |
| **Predatory social behavior** | Free-text chat, messaging | Critical — this is why we DON'T have chat |
| **Excessive screen time** | Game engagement loops | Medium — parental controls mitigate |
| **Frightening content** | Space disasters, asteroid impacts, solar storms | Medium — age-appropriate framing needed |
| **External links** | NASA descriptions sometimes contain URLs | Low-Medium — links could lead anywhere |
| **User-generated content abuse** | If we ever add creation/sharing features | High — must be moderated before sharing |

### 22.2 Display Name Moderation

The **only** user-generated text visible to other players. It gets the heaviest scrutiny.

#### Three-Layer Filter

```python
# apps/users/moderation.py

class DisplayNameModerator:
    """
    Layer 1: Blocklist — instant reject
    Layer 2: Pattern matching — catch evasion
    Layer 3: Manual review queue — edge cases
    """

    def check(self, name: str) -> ModerationResult:
        normalized = self._normalize(name)  # lowercase, strip leetspeak, remove spaces

        # Layer 1: Exact blocklist (profanity, slurs, adult terms)
        # ~10,000 terms across 20+ languages, sourced from:
        # - Google's profanity list
        # - FOSI (Family Online Safety Institute) recommendations
        # - Custom additions from our moderation team
        if self._matches_blocklist(normalized):
            return ModerationResult.REJECTED_AUTO

        # Layer 2: Pattern matching
        # Catches: "a$$tronaut", "s.e.x.y.star", "n1c3butt"
        # Uses regex + phonetic matching (Soundex/Metaphone)
        if self._matches_patterns(normalized):
            return ModerationResult.REJECTED_AUTO

        # Layer 3: If it's borderline, queue for human review
        # The name works temporarily but is flagged
        if self._is_suspicious(normalized):
            ModerationQueue.objects.create(
                content_type='display_name',
                content=name,
                status='pending'
            )
            return ModerationResult.APPROVED_PENDING_REVIEW

        return ModerationResult.APPROVED

    def _normalize(self, name: str) -> str:
        """Convert leetspeak, remove non-alpha, phonetic normalize."""
        leet_map = {'0': 'o', '1': 'i', '3': 'e', '4': 'a',
                    '5': 's', '7': 't', '8': 'b', '@': 'a', '$': 's'}
        cleaned = ''.join(leet_map.get(c, c) for c in name.lower())
        return re.sub(r'[^a-z]', '', cleaned)
```

#### Suggested Names as Default

To reduce moderation load and help younger kids, offer pre-generated names:

```
"CosmicPilot" + random number   → CosmicPilot42
"StarCadet" + random number     → StarCadet789
"NebulaNinja" + random number   → NebulaNinja23
```

Children can pick a suggested name (no moderation needed) or type a custom one (moderated).

### 22.3 NASA Content Curation Gate

Not everything NASA publishes is suitable for a 6-year-old without context. Our content pipeline includes a human review step.

#### Auto-Publish vs Manual Review

```
NASA content arrives via ingestion
  │
  ├─ Content type in SAFE_AUTO_PUBLISH list?
  │   (Mars rover photos, EPIC Earth images, exoplanet data)
  │   → Auto-publish with is_published=True
  │
  ├─ Content type in REVIEW_REQUIRED list?
  │   (APOD — topics vary wildly, Image Library — historical content)
  │   → is_published=False, added to Content Curation Queue
  │   → Curator reviews: safe? scary? needs age gating?
  │
  └─ Content flagged by automated check?
      (Description contains words from sensitivity list: "death", "collision",
       "catastrophic", "nuclear", "weapon")
      → is_published=False, priority review
```

#### Age-Gating Content

Some NASA content is educational but intense. Rather than removing it, we gate it:

| Content | Ages 6-8 | Ages 9-11 | Ages 12-14 |
|---------|----------|-----------|------------|
| Asteroid impact simulations | Hidden | Shown with reassuring context: *"Scientists track these so we stay safe"* | Full scientific detail |
| Supernova/star death imagery | Simplified: *"Stars are born and stars change"* | *"Stars have lifecycles"* | Full explanation of stellar death |
| Historical disaster content (Challenger, Columbia) | Not shown | Brief mention with focus on lessons learned | Full historical context |
| Solar flare consequences | *"The Sun sends us energy!"* | *"Solar storms can affect satellites"* | Effects on power grids, radiation |
| Violent cosmic events (gamma ray bursts) | Reframed as *"space fireworks"* | Simplified physics | Accurate astrophysics |

```python
# apps/nasa_ingest/models.py
class NASAContent(models.Model):
    # ... existing fields ...
    content_rating   = models.CharField(
        max_length=8,
        choices=[
            ('all', 'All ages'),
            ('9+', 'Ages 9+'),
            ('12+', 'Ages 12+'),
        ],
        default='all'
    )
    sensitivity_flags = ArrayField(
        models.CharField(max_length=32), default=list
    )  # ['impact', 'death', 'disaster', 'scary_imagery']
    curator_notes    = models.TextField(blank=True)
```

#### Description Sanitization

NASA APOD explanations are written for adults. Before showing to children:

```python
# apps/nasa_ingest/transformers/text_sanitizer.py

class ChildFriendlyTextProcessor:
    """
    Takes NASA scientist-written text and produces age-appropriate versions.
    """
    def process(self, text: str, age_group: str) -> str:
        # 1. Strip external URLs (prevent link-out to unmoderated sites)
        text = re.sub(r'https?://\S+', '[link removed]', text)

        # 2. Replace jargon with simpler terms for younger groups
        if age_group in ('6-8', '9-11'):
            text = self._simplify_vocabulary(text)

        # 3. Add context to potentially scary terms
        text = self._add_reassurance(text)

        # 4. Limit length for younger readers
        if age_group == '6-8':
            text = self._summarize(text, max_sentences=3)

        return text

    def _add_reassurance(self, text):
        """
        'This asteroid will pass dangerously close to Earth'
        → 'This asteroid will pass close to Earth (but scientists
           are tracking it to make sure we're safe!)'
        """
        ...
```

### 22.4 No Direct Communication Between Children

**This is the single most important safety decision: there is no free-text communication between players.**

No chat. No messaging. No comments. No custom messages on leaderboards. No "send a message to your friend." None.

Why this is absolute:
- Free-text chat in children's platforms is the #1 vector for predatory behavior
- Moderating real-time chat at scale is nearly impossible to do perfectly
- The game doesn't need it — there's no gameplay mechanic that requires chat
- COPPA and the UK Children's Code strongly discourage child-to-child communication without robust safeguards (see §22.1 threat model)

**What we offer instead:**

| Feature | Safe Alternative |
|---------|-----------------|
| Social connection | "42 explorers discovered this today!" — aggregate, anonymous |
| Competition | Pseudonymous leaderboards with opt-in (parent-controlled) |
| Cooperation | Aggregate progress bars: "Our community has mapped 73% of Mars!" |
| Expression | Pre-set emoji reactions on achievements (no custom text) |
| Sharing | "Share your score" generates a static image card (no link to profile) |

### 22.5 External Link Protection

NASA descriptions and content sometimes reference external URLs. Children must not be able to navigate to unmoderated external sites.

```python
# apps/nasa_ingest/transformers/link_handler.py

class ExternalLinkPolicy:
    # URLs that are safe to link to (NASA properties only)
    ALLOWLISTED_DOMAINS = [
        'nasa.gov',
        'jpl.nasa.gov',
        'hubblesite.org',
        'solarsystem.nasa.gov',
        'science.nasa.gov',
    ]

    def process_content(self, html: str) -> str:
        """
        - Links to allowlisted domains: keep, but open in parent-controlled browser
        - Links to other domains: remove entirely, replace with descriptive text
        - All remaining links get interstitial: "You're leaving NASA Space Explorer!"
        """
        ...
```

The interstitial page:
```
┌────────────────────────────────────────────────────┐
│                                                    │
│  🚀 You're about to leave NASA Space Explorer!     │
│                                                    │
│  This link goes to: nasa.gov/mars-exploration      │
│                                                    │
│  This is an official NASA website.                 │
│  Ask a grown-up before visiting!                   │
│                                                    │
│  [Go Back to Game]     [Visit Website ↗]           │
│                                                    │
└────────────────────────────────────────────────────┘
```

For under-13 accounts without parental consent: the "Visit Website" button is **disabled**. Only the "Go Back" option works.

### 22.6 Screen Time & Wellbeing

The UK Children's Code (Standard 4) requires platforms to discourage excessive use. We build this in:

#### Parental Time Controls

```python
# apps/users/models.py
class ParentAccount(models.Model):
    # ... existing fields ...
    daily_time_limit_min = models.IntegerField(null=True)  # null = unlimited
    allowed_hours_start  = models.TimeField(null=True)     # e.g., 08:00
    allowed_hours_end    = models.TimeField(null=True)     # e.g., 21:00
    weekly_report_email  = models.BooleanField(default=True)
```

#### Built-In Break Reminders

Even without parental limits, the game itself encourages breaks:

| Trigger | Response |
|---------|----------|
| 30 min continuous play | Gentle reminder: *"Astronauts take breaks too! Stretch like you're floating in space."* (dismissible) |
| 60 min continuous play | Stronger nudge: *"Mission Control recommends a break. Your progress is saved!"* + mini space-walk animation |
| 90 min continuous play | Session pause: *"Great exploring today! Come back tomorrow for a new mission."* (overridable once) |
| Parent-set time limit reached | Hard stop: *"Time's up for today, explorer! See you tomorrow."* (not overridable, with countdown warning at 5 min) |

#### Anti-Addiction Design (UK Children's Code Standard 4)

| Dark Pattern We Avoid | What We Do Instead |
|----------------------|-------------------|
| Infinite scroll | Discrete missions with clear endings |
| Loss aversion ("Your streak will reset!") | Streaks are bonuses, never punishments. Missing a day doesn't reset. |
| FOMO notifications | No push notifications to children. Daily content refreshes but we don't nag. |
| Loot boxes / random paid rewards | No paid content. All rewards are deterministic or earned. |
| Social pressure ("Your friend is ahead!") | Only personal progress shown by default. Leaderboards are opt-in. |
| Autoplay | Every mission requires explicit "Launch" action |

### 22.7 Reporting & Incident Response

#### What Can Be Reported

- Inappropriate display names on leaderboards
- Content that seems wrong or scary
- Technical issues
- "Something else" (freeform — goes to moderation queue)

Accessible via: floating "!" icon on every screen → "Report a Problem" modal with pre-set categories (no freeform text for under-13 reporters, just tap the category).

#### Incident Response

```
Report submitted
  │
  ├─ Display name report:
  │   → Auto-hide name pending review (replaced with "Explorer")
  │   → Moderator reviews within 4 hours (SLA)
  │   → If inappropriate: name reset, player warned, parent notified
  │   → If 3+ offenses: account suspended, parent notified
  │
  ├─ Content report:
  │   → Content de-listed pending review
  │   → Curator reviews within 24 hours
  │   → If legitimately concerning: remove from all age groups, add to sensitivity list
  │
  └─ Safety concern:
      → Escalated to designated Safety Officer within 1 hour
      → If potential child exploitation: report to NCMEC CyberTipline (US law requires this)
      → Document everything in incident log (immutable, like audit log)
```

### 22.8 Moderation Team & Tools

| Role | Responsibility | Tools |
|------|---------------|-------|
| **Content Curator** | Review NASA content for age-appropriateness, write child-friendly descriptions | Admin panel → Curation Queue |
| **Moderator** | Review flagged display names, handle reports, issue warnings/bans | Admin panel → Moderation Queue |
| **Safety Officer** | Handle escalated safety concerns, NCMEC reporting, compliance oversight | Direct alert channel, incident dashboard |

Admin panel additions (extending §10):

```
/admin/
├── 🛡️ Moderation
│   ├── Display Name Queue      # Flagged names awaiting review
│   │   └── [Approve] [Reject] [Reset to Suggested] [Warn Player] [Suspend]
│   ├── Content Review Queue    # NASA content pending curation
│   │   └── [Approve] [Reject] [Set Age Rating] [Add Sensitivity Flag]
│   ├── Reports Inbox           # User-submitted reports
│   │   └── [Resolve] [Escalate] [Respond to Parent]
│   ├── Suspensions & Bans      # Active enforcement actions
│   └── Safety Incidents        # Escalated cases (restricted access)
```

---

## 23. NASA Data Licensing & API Compliance

### 23.1 NASA Media Usage Policy

NASA content is **not automatically public domain**. The rules are nuanced:

#### What IS Free to Use

| Content Type | License | Source |
|-------------|---------|--------|
| NASA-created images and video | Public domain (no copyright) | nasa.gov media policy |
| Data from NASA APIs | Public domain (US government work) | api.nasa.gov terms |
| NASA logo (meatball) | **Restricted** — requires NASA approval | 14 CFR 1221 |
| Hubble/JWST images (STScI) | Usually public domain, but check credits | Some have specific attribution |
| NASA audio recordings | Public domain | NASA Sound Cloud, historical archives |

#### What Requires Special Handling

| Content | Rule | Our Compliance |
|---------|------|---------------|
| **NASA logo** | Cannot be used to imply NASA endorsement. Cannot be used on commercial merchandise. | We do NOT use the NASA logo. We use the text "Built with NASA Open APIs" with a link. |
| **Astronaut likenesses** | Astronauts have publicity rights. Photos showing identifiable faces may have restrictions. | Image Library content with identifiable astronauts gets manual review. We use photos for educational purposes (fair use) and credit NASA. |
| **Third-party images in APOD** | ~30% of APOD images have non-NASA copyright holders (amateur astronomers, ESA, observatories). The `copyright` field is populated for these. | If `copyright` field is non-empty: display attribution. If license is unclear: don't use in jigsaw puzzles (derivative work). Show in gallery only with credit. |
| **Music/audio from NASA** | Some NASA audio compilations include licensed music. | Use only raw mission audio (comms, telemetry), never soundtrack compilations. |
| **ESA/JAXA/other agency content** | Not covered by US public domain. Each agency has its own license. | We only ingest from NASA APIs. If content has non-NASA origin metadata, flag for manual review. |

### 23.2 Attribution System

Even for public domain content, attribution is good practice and educational:

```python
# apps/nasa_ingest/models.py
class NASAContent(models.Model):
    # ... existing fields ...
    copyright        = models.CharField(max_length=255, blank=True)  # Non-empty = third-party
    credit           = models.CharField(max_length=500, blank=True)  # "NASA/JPL-Caltech/MSSS"
    attribution_required = models.BooleanField(default=False)
    usage_restrictions   = models.JSONField(default=list)
    # e.g., ['no_derivative', 'attribution_required', 'non_commercial_only']
```

Frontend display — every NASA image includes a small credit line:

```
┌─────────────────────────────────────────┐
│                                         │
│          [NASA APOD Image]              │
│                                         │
├─────────────────────────────────────────┤
│  📷 NASA/ESA/Hubble Heritage Team       │
│  Public Domain · March 15, 2026         │
└─────────────────────────────────────────┘
```

For copyrighted APOD images:
```
┌─────────────────────────────────────────┐
│  📷 © John Smith / Used with permission │
│  This image may not be downloaded       │
│  [View on original site ↗]              │
└─────────────────────────────────────────┘
```

Implementation: copyrighted images disable the jigsaw puzzle generator (derivative work), disable download button, and display full copyright notice.

### 23.3 NASA API Terms of Service

From api.nasa.gov terms:

| Requirement | Our Compliance |
|-------------|---------------|
| **Rate limit: 1,000 req/hour per key** | §6.3 — we use ~127/hr. Celery-only access. |
| **API key required** | §9 — key stored in Secrets Manager, never exposed. |
| **No implication of NASA endorsement** | We say "Built with NASA Open APIs" — never "NASA-approved" or "Official NASA game." |
| **Data accuracy** | We display NASA data as-is for factual content. Game mechanics (quizzes, puzzles) are clearly labeled as gameplay, not scientific instruments. |
| **No guaranteed uptime** | §6.7 — full resilience strategy for NASA downtime. |
| **Terms may change** | We monitor api.nasa.gov/terms for updates. Legal review quarterly. |

### 23.4 Intellectual Property: Our Original Content

| Content | Owner | License |
|---------|-------|---------|
| Game mechanics, mission designs | Us | Proprietary |
| Original illustrations, sprites | Us (or licensed from artist) | Proprietary, with work-for-hire agreements |
| Quiz questions (auto-generated) | Us (derivative of public domain NASA text) | Proprietary |
| Quiz questions (curator-written) | Us | Proprietary |
| Sound effects (original) | Us (or licensed) | Ensure commercial license on any stock audio |
| Astronaut guide character | Us | Proprietary — register trademark if commercially important |

**Music licensing**: Any background music must be:
- Original (commissioned), OR
- Licensed under a royalty-free commercial license (NOT Creative Commons NC — our game may monetize in the future), OR
- Generated with an AI music tool that grants commercial usage rights

### 23.5 Legal Disclaimers

Built into the app footer and About screen:

```
NASA Space Explorer is an independent educational platform.
It is not affiliated with, endorsed by, or sponsored by NASA.

Space data provided by NASA Open APIs (api.nasa.gov).
NASA imagery is in the public domain unless otherwise credited.

This game is for educational purposes. Game content (quizzes, puzzles, missions)
is designed to teach space science concepts but is not a substitute for
scientific instruments or official NASA communications.
```

### 23.6 Compliance Calendar

| Cadence | Action |
|---------|--------|
| **Daily** | Auto-moderation queues processed within SLA |
| **Weekly** | Content curation backlog reviewed, moderation metrics checked |
| **Monthly** | Parental consent audit — flag expired/outdated consents |
| **Quarterly** | NASA API terms review, privacy policy review, security audit |
| **Annually** | Full COPPA compliance audit, GDPR DPIA refresh, legal review of all third-party licenses |
| **On change** | Any new data collection → Privacy Impact Assessment → consent form version bump → re-consent flow |

### 23.7 Compliance Architecture Summary

```
┌────────────────────────────────────────────────────────────────┐
│                      COMPLIANCE LAYERS                         │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  Data Layer:     Encryption at rest · Pseudonymization ·       │
│                  Minimal collection · Auto-expiry               │
│                                                                │
│  Access Layer:   Age-gated features · Parental consent gate ·  │
│                  Role-based admin · Audit logging               │
│                                                                │
│  Content Layer:  NASA curation pipeline · Display name filter · │
│                  External link blocker · Age-rated content      │
│                                                                │
│  Social Layer:   No child-to-child chat · Pseudonymous         │
│                  leaderboards · Aggregate-only social           │
│                                                                │
│  Wellbeing:      Break reminders · Time limits · No dark       │
│                  patterns · No ads · No loot boxes              │
│                                                                │
│  Legal:          COPPA VPC flow · GDPR deletion · NASA         │
│                  attribution · IP licensing · Disclaimers       │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

# Part VI — Analytics, Feedback & Data-Driven Evolution

## 24. Analytics & Engagement Measurement

This section defines how we measure what's working, what's not, and how to evolve the product using real player data — all while respecting our strict COPPA/GDPR-K privacy requirements from §21.

### 24.1 Privacy-First Analytics Principles

Every metric described below follows these non-negotiable rules:

| Principle | Implementation |
|-----------|----------------|
| **Aggregate, never individual** | All dashboards show cohort-level data. No "what did player X do?" views except for parent-requested reports. |
| **Pseudonymized at ingestion** | Raw events use `player_id` (UUID). Display name, age, parent email are NEVER in the analytics pipeline. |
| **No third-party trackers** | No Google Analytics, no Mixpanel, no ad pixels. Self-hosted Plausible for page-level metrics (§21). All behavioral analytics run on our own infrastructure. |
| **Minimal collection** | We log actions that serve a specific analytical purpose (listed below). No "log everything, analyze later." |
| **Retention limits** | Raw event data: 90 days. Aggregated rollups: 2 years. Player-level data deleted on account deletion (§21.5). |
| **Parental transparency** | Parent dashboard shows exactly what data we collect about their child and allows export/deletion. |

### 24.2 Event Taxonomy

Every meaningful player action emits a structured event. Events are the atomic unit of all analytics.

```python
# apps/analytics/events.py

class AnalyticsEvent:
    """Base event schema. All events include these fields."""
    event_type: str           # e.g., 'mission.started', 'quiz.answered'
    player_id: UUID           # Pseudonymized — no PII attached
    session_id: UUID          # Groups events within one play session
    age_group: str            # '6-8', '9-11', '12-14' — for cohort analysis only
    timestamp: datetime
    payload: dict             # Event-specific data (see below)
```

#### Core Event Types

| Event | Payload | Analytics Purpose |
|-------|---------|-------------------|
| `session.started` | `{device_type, screen_size, is_returning}` | DAU/MAU, device breakdown, new vs returning |
| `session.ended` | `{duration_seconds, screens_visited, missions_played}` | Session length, engagement depth |
| `mission.started` | `{mission_id, planet_id, game_type, difficulty_level}` | Mission popularity, start rates |
| `mission.completed` | `{mission_id, score, time_seconds, attempts, hints_used}` | Completion rates, difficulty calibration |
| `mission.abandoned` | `{mission_id, time_before_abandon, last_screen}` | Drop-off points, frustration detection |
| `quiz.answered` | `{quiz_id, mission_id, is_correct, time_to_answer_ms, hint_tier_used}` | Question difficulty, learning measurement |
| `jigsaw.completed` | `{puzzle_id, piece_count, time_seconds, misplacements}` | Puzzle difficulty tuning |
| `collection.earned` | `{item_type, item_id, earned_from_mission}` | Collection engagement, reward effectiveness |
| `navigation.planet_visited` | `{planet_id, source_screen}` | Space map heat maps, content discovery |
| `dda.adjustment` | `{direction, old_level, new_level, trigger_reason}` | DDA health monitoring |
| `streak.updated` | `{new_streak, previous_streak}` | Retention correlation |
| `onboarding.step_completed` | `{step_number, time_on_step}` | Onboarding funnel, drop-off |
| `break_reminder.shown` | `{session_duration_at_trigger}` | Wellbeing compliance |
| `break_reminder.accepted` | `{session_duration_at_trigger}` | Wellbeing effectiveness |
| `content.nasa_image_viewed` | `{content_type, content_id, view_duration_ms}` | Content engagement |
| `error.game_crash` | `{game_type, error_code, device_info}` | Stability monitoring |

#### What We Do NOT Track

Explicitly excluded to maintain COPPA compliance:

- Free-text input content (display name attempts, search queries)
- Precise location (no GPS, no IP geolocation beyond country)
- Cross-session behavioral fingerprinting
- Time-of-day patterns for individual players (only aggregate)
- Any data that could identify a specific child

### 24.3 Analytics Pipeline Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Frontend   │────▶│  Django API  │────▶│  Event Queue │────▶│  Analytics   │
│  (emit event)│     │ /api/events/ │     │   (Redis     │     │  Worker      │
│              │     │  validates + │     │   Stream)    │     │  (Celery)    │
│              │     │  strips PII  │     │              │     │              │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
                                                                      │
                                                               ┌──────┴──────┐
                                                               │             │
                                                               ▼             ▼
                                                    ┌──────────────┐ ┌──────────────┐
                                                    │  Raw Events  │ │  Aggregated  │
                                                    │  (Postgres   │ │  Rollups     │
                                                    │   partitioned│ │  (Postgres   │
                                                    │   by day)    │ │   materialized│
                                                    │   90d retain │ │   views)     │
                                                    └──────────────┘ └──────────────┘
                                                                           │
                                                                           ▼
                                                                  ┌──────────────┐
                                                                  │ Admin Panel  │
                                                                  │ Dashboards   │
                                                                  │ (§10.3)      │
                                                                  └──────────────┘
```

**Key design decisions:**

- **Batch, not real-time**: Events are buffered on the client (up to 20 events or 30 seconds) then sent as a batch. Reduces HTTP requests from children's devices.
- **Server-side validation**: The `/api/events/` endpoint validates event schemas and strips any accidentally-included PII before queuing.
- **Redis Streams as buffer**: Events flow through Redis Streams (not direct DB writes) so gameplay API latency is never affected by analytics load.
- **Partitioned storage**: Raw events table is partitioned by day. Dropping partitions older than 90 days is a single DDL statement, not a DELETE.
- **Materialized views for dashboards**: Pre-computed rollups refresh every 15 minutes. Admin dashboards read these, never raw events.

```python
# apps/analytics/models.py

class RawEvent(models.Model):
    """Partitioned by day. 90-day retention."""
    event_type      = models.CharField(max_length=64, db_index=True)
    player_id       = models.UUIDField(db_index=True)
    session_id      = models.UUIDField()
    age_group       = models.CharField(max_length=8)
    timestamp       = models.DateTimeField(db_index=True)
    payload         = models.JSONField()

    class Meta:
        managed = False  # Partitioned table created via migration SQL
        indexes = [
            models.Index(fields=['event_type', 'timestamp']),
            models.Index(fields=['age_group', 'event_type', 'timestamp']),
        ]


class DailyEngagementRollup(models.Model):
    """Materialized view refreshed every 15 min."""
    date            = models.DateField(primary_key=True)
    age_group       = models.CharField(max_length=8)
    dau             = models.IntegerField()         # Distinct player_ids
    sessions        = models.IntegerField()
    avg_session_seconds = models.FloatField()
    missions_started = models.IntegerField()
    missions_completed = models.IntegerField()
    quizzes_answered = models.IntegerField()
    quizzes_correct  = models.IntegerField()
    new_players      = models.IntegerField()
    returning_players = models.IntegerField()

    class Meta:
        managed = False
        unique_together = ('date', 'age_group')


class MissionRollup(models.Model):
    """Per-mission stats, refreshed every 15 min."""
    date            = models.DateField()
    mission_id      = models.IntegerField()
    age_group       = models.CharField(max_length=8)
    starts          = models.IntegerField()
    completions     = models.IntegerField()
    abandons        = models.IntegerField()
    avg_score       = models.FloatField()
    avg_time_seconds = models.FloatField()
    avg_attempts    = models.FloatField()
    avg_hints_used  = models.FloatField()
    p50_time_seconds = models.FloatField()   # Median
    p90_time_seconds = models.FloatField()   # 90th percentile

    class Meta:
        managed = False
        unique_together = ('date', 'mission_id', 'age_group')


class QuizQuestionRollup(models.Model):
    """Per-question difficulty stats."""
    date            = models.DateField()
    quiz_id         = models.IntegerField()
    age_group       = models.CharField(max_length=8)
    attempts        = models.IntegerField()
    correct_count   = models.IntegerField()
    avg_time_to_answer_ms = models.FloatField()
    hint_usage_rate = models.FloatField()        # % who used hints

    class Meta:
        managed = False
        unique_together = ('date', 'quiz_id', 'age_group')
```

### 24.4 Key Metrics & Dashboards

These dashboards extend the admin panel analytics section (§10.3):

#### Engagement Dashboard

| Metric | Definition | Healthy Range | Alert If |
|--------|-----------|---------------|----------|
| **DAU / MAU** | Daily & monthly active unique players | — | DAU drops >20% week-over-week |
| **D1 / D7 / D30 Retention** | % of new players returning after 1/7/30 days | D1 >40%, D7 >20%, D30 >10% | D1 <30% |
| **Avg Session Length** | Mean seconds per session, by age group | 10–25 min (age 6-8), 15–35 min (9-14) | <5 min or >45 min |
| **Sessions per DAU** | How many times a day active players return | 1.2–2.0 | <1.1 |
| **Mission Completion Rate** | Completions / starts, by mission | 60–85% | <40% (too hard) or >95% (too easy) |
| **Daily Streak Distribution** | Histogram of current streaks | Healthy long tail | >80% at streak=0 |

#### Learning Outcomes Dashboard

| Metric | Definition | Purpose |
|--------|-----------|---------|
| **Quiz Accuracy by Topic** | % correct per concept tag (gravity, orbits, geology) | Identifies which topics students struggle with |
| **Knowledge Constellation Growth** | Avg nodes unlocked per week, by age group | Measures learning velocity |
| **Mastery Progression** | % of players reaching mastery level 2/3 per concept | Identifies concepts that need better teaching |
| **Hint Dependency Rate** | % of correct answers that required hints | High hint rate = question is poorly scaffolded |
| **Pre/Post Concept Scores** | Accuracy on a topic before vs after completing its mission arc | Direct learning measurement |
| **Time-to-Mastery** | Sessions needed to reach mastery on each concept | Calibrate mission length and pacing |

```python
# apps/analytics/learning.py

def compute_learning_gain(player_id: UUID, concept_slug: str) -> dict:
    """
    Compare quiz accuracy on a concept before and after completing
    its associated mission arc. Returns learning gain metrics.
    """
    arc_missions = Mission.objects.filter(
        concept_tags__contains=[concept_slug]
    ).values_list('id', flat=True)

    first_completion = MissionCompletion.objects.filter(
        player_id=player_id, mission_id__in=arc_missions
    ).order_by('completed_at').first()

    if not first_completion:
        return {'status': 'no_data'}

    pre_accuracy = RawEvent.objects.filter(
        player_id=player_id,
        event_type='quiz.answered',
        payload__concept=concept_slug,
        timestamp__lt=first_completion.completed_at,
    ).aggregate(
        correct=Count('id', filter=Q(payload__is_correct=True)),
        total=Count('id'),
    )

    post_accuracy = RawEvent.objects.filter(
        player_id=player_id,
        event_type='quiz.answered',
        payload__concept=concept_slug,
        timestamp__gte=first_completion.completed_at,
    ).aggregate(
        correct=Count('id', filter=Q(payload__is_correct=True)),
        total=Count('id'),
    )

    return {
        'pre_accuracy': safe_divide(pre_accuracy['correct'], pre_accuracy['total']),
        'post_accuracy': safe_divide(post_accuracy['correct'], post_accuracy['total']),
        'learning_gain': post_accuracy_rate - pre_accuracy_rate,
        'sample_size': {'pre': pre_accuracy['total'], 'post': post_accuracy['total']},
    }
```

#### Content Popularity Dashboard

| Metric | Definition | Use Case |
|--------|-----------|----------|
| **Most-Played Missions** | Ranked by starts, by age group | Identify hits to replicate |
| **Most-Collected Items** | Top APOD images, badges, audio logs earned | Understand what rewards resonate |
| **API Content Engagement** | Which NASA API sources drive the most play time | Prioritize API investment |
| **Planet Visit Heatmap** | Which space map nodes get traffic | Identify underexplored content areas |
| **Search/Discovery Paths** | Most common navigation sequences | Optimize space map layout |
| **Content Freshness Impact** | Engagement delta when new NASA data arrives (e.g., new APOD) vs stale days | Measure real-data value |

---

## 25. Dynamic Difficulty Adjustment (DDA) System

### 25.1 Why DDA Matters

Our audience spans ages 6–14 — a massive cognitive range. A challenge that delights a 12-year-old will crush a 7-year-old. Static difficulty settings aren't enough because:

- Age is a rough proxy — a sharp 7-year-old may outperform an average 10-year-old
- Skill varies by topic — a child strong in astronomy may struggle with physics puzzles
- Difficulty perception is emotional — two failures in a row feel very different from two spread across a session

DDA keeps every player in the flow channel (§3.2) by continuously adjusting challenge level based on observed performance.

### 25.2 DDA Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   DDA Decision Flow                          │
│                                                              │
│  Player answers / completes mission                          │
│           │                                                  │
│           ▼                                                  │
│  ┌─────────────────┐                                        │
│  │ Update Rolling   │  Last 10 answers tracked in Redis     │
│  │ Performance      │  Key: dda:{player_id}                 │
│  │ Window           │  Fields: recent_correct, recent_total,│
│  │                  │          streak, topic_scores          │
│  └────────┬────────┘                                        │
│           │                                                  │
│           ▼                                                  │
│  ┌─────────────────┐                                        │
│  │ Compute          │  accuracy = recent_correct / recent_  │
│  │ Performance      │            total                      │
│  │ Score            │  weighted by recency (newer = heavier)│
│  └────────┬────────┘                                        │
│           │                                                  │
│           ▼                                                  │
│  ┌─────────────────┐     ┌─────────────┐                    │
│  │ Compare to       │────▶│ Adjust?     │                    │
│  │ Thresholds       │     │             │                    │
│  │                  │     │ >80% acc    │──▶ Increase (+1)   │
│  │                  │     │ 50-80% acc  │──▶ Hold (no change)│
│  │                  │     │ <50% acc    │──▶ Decrease (-1)   │
│  │                  │     │ 3 wrong     │──▶ Decrease (-1)   │
│  │                  │     │ streak      │    immediately     │
│  └─────────────────┘     └─────────────┘                    │
│           │                                                  │
│           ▼                                                  │
│  ┌─────────────────┐                                        │
│  │ Apply to Next    │  Select quiz questions at new level   │
│  │ Content          │  Adjust jigsaw piece count            │
│  │ Selection        │  Modify action game speed             │
│  │                  │  Choose mission recommendations       │
│  └─────────────────┘                                        │
└─────────────────────────────────────────────────────────────┘
```

### 25.3 Per-Game-Type Difficulty Levers

Each game type has specific parameters that DDA controls:

| Game Type | Difficulty Lever | Easy (Level 1-3) | Medium (Level 4-6) | Hard (Level 7-10) |
|-----------|-----------------|-------------------|--------------------|--------------------|
| **Quiz** | Question pool | Simple recall, 2 choices | Application, 4 choices | Multi-step reasoning, 4 choices + tricky distractors |
| **Quiz** | Hints available | 3 hint tiers, auto-nudge after 15s | 3 hint tiers | 1 hint tier, no auto-nudge |
| **Quiz** | Time pressure | None | Optional timer (bonus XP) | Timer standard |
| **Jigsaw** | Piece count | 12 pieces, grid cut | 24 pieces, irregular cut | 48 pieces, irregular cut, no preview |
| **Jigsaw** | Rotation | No rotation needed | Pieces may be rotated | Pieces rotated + edge hints hidden |
| **Action** (Solar Storm) | Speed | 0.5× base speed | 1× base speed | 1.5× + random speed bursts |
| **Action** | Obstacle density | 3 per screen | 5 per screen | 8 per screen + combo patterns |
| **Rover Drive** | Terrain complexity | Wide paths, few obstacles | Narrower, some dead ends | Narrow, dead ends, timed |
| **Sorting/Dragging** | Item count | 4 items | 6-8 items | 10+ items, closer values |
| **Planet Builder** | Parameter count | 2 sliders (mass, distance) | 4 sliders | 6 sliders + derived calculations |

### 25.4 DDA Implementation

```python
# apps/progress/dda.py

import redis
from dataclasses import dataclass
from typing import Optional

WINDOW_SIZE = 10          # Last N answers considered
INCREASE_THRESHOLD = 0.80 # >80% accuracy → increase
DECREASE_THRESHOLD = 0.50 # <50% accuracy → decrease
FRUSTRATION_STREAK = 3    # 3 wrong in a row → immediate decrease
COOLDOWN_ACTIONS = 5      # Min actions between adjustments

@dataclass
class DDAState:
    recent_results: list[bool]     # Last N correct/incorrect
    current_level: int             # 1-10
    actions_since_adjustment: int
    topic_levels: dict[str, int]   # Per-topic levels

    @property
    def accuracy(self) -> float:
        if not self.recent_results:
            return 0.5
        # Recency-weighted: most recent answers count more
        weights = [1.0 + (i * 0.1) for i in range(len(self.recent_results))]
        weighted_correct = sum(w for w, r in zip(weights, self.recent_results) if r)
        return weighted_correct / sum(weights)

    @property
    def has_frustration_streak(self) -> bool:
        return (len(self.recent_results) >= FRUSTRATION_STREAK and
                not any(self.recent_results[-FRUSTRATION_STREAK:]))


def get_dda_state(player_id: str) -> DDAState:
    """Load DDA state from Redis (hot path) with Postgres fallback."""
    r = redis.get_connection()
    key = f'dda:{player_id}'
    data = r.hgetall(key)
    if not data:
        # Cold start: load from Postgres Progress model
        progress = Progress.objects.get(player_id=player_id)
        return DDAState(
            recent_results=[],
            current_level=_skill_to_level(progress.skill_estimate),
            actions_since_adjustment=0,
            topic_levels={},
        )
    return DDAState.from_redis(data)


def record_answer(player_id: str, is_correct: bool, topic: str) -> Optional[int]:
    """
    Record an answer and return new difficulty level if adjusted.
    Returns None if no adjustment made.
    """
    state = get_dda_state(player_id)
    state.recent_results.append(is_correct)
    state.recent_results = state.recent_results[-WINDOW_SIZE:]
    state.actions_since_adjustment += 1

    new_level = None

    # Frustration streak: immediate decrease, bypass cooldown
    if state.has_frustration_streak and state.current_level > 1:
        new_level = state.current_level - 1
        state.actions_since_adjustment = 0

    # Normal threshold check with cooldown
    elif state.actions_since_adjustment >= COOLDOWN_ACTIONS:
        if state.accuracy > INCREASE_THRESHOLD and state.current_level < 10:
            new_level = state.current_level + 1
            state.actions_since_adjustment = 0
        elif state.accuracy < DECREASE_THRESHOLD and state.current_level > 1:
            new_level = state.current_level - 1
            state.actions_since_adjustment = 0

    if new_level is not None:
        state.current_level = new_level
        # Also update topic-specific level
        state.topic_levels[topic] = new_level
        # Emit analytics event
        emit_event('dda.adjustment', player_id, {
            'direction': 'up' if new_level > state.current_level else 'down',
            'old_level': state.current_level,
            'new_level': new_level,
            'trigger_reason': 'frustration_streak' if state.has_frustration_streak else 'threshold',
            'accuracy': state.accuracy,
        })

    save_dda_state(player_id, state)
    return new_level


def select_content_at_level(game_type: str, level: int, topic: str) -> dict:
    """
    Returns game configuration adjusted for the current difficulty level.
    Each game type maps level to its specific levers (§25.3).
    """
    configs = {
        'quiz': {
            'choices': 2 if level <= 3 else 4,
            'hint_tiers': 3 if level <= 6 else 1,
            'auto_nudge_seconds': 15 if level <= 3 else (30 if level <= 6 else None),
            'time_limit': None if level <= 6 else 45,
            'question_difficulty_max': level,
        },
        'jigsaw': {
            'piece_count': 12 if level <= 3 else (24 if level <= 6 else 48),
            'rotation_enabled': level > 3,
            'preview_enabled': level <= 6,
            'edge_hints': level <= 6,
        },
        'action': {
            'speed_multiplier': 0.5 + (level - 1) * 0.11,  # 0.5 at L1, ~1.5 at L10
            'obstacle_density': 3 + (level - 1) * 0.6,
            'combo_patterns': level > 6,
        },
    }
    return configs.get(game_type, {})
```

### 25.5 DDA Monitoring & Health

The admin DDA Health dashboard (§10.3) shows:

| Metric | What It Reveals | Action If Unhealthy |
|--------|----------------|---------------------|
| **Level Distribution Histogram** | Bell curve of player levels per age group | If skewed low → content is too hard globally. If skewed high → too easy. |
| **Adjustment Frequency** | How often DDA triggers per 100 actions | >30% → thresholds may be too sensitive. <5% → thresholds too wide. |
| **Frustration Streak Rate** | % of sessions with 3+ wrong streak | >15% in any age group → investigate those missions |
| **Level Stability** | % of players whose level hasn't changed in 7 days | High stability = good calibration. Low = oscillating (yo-yo problem). |
| **Topic Level Variance** | Spread of a player's per-topic levels | High variance is normal and expected (strong in astronomy, weak in physics). |
| **Accuracy After Adjustment** | Accuracy in the 5 actions after a DDA change | Should be 55-75%. If still <50% → adjustment step too small. |

---

## 26. Feedback Mechanisms

### 26.1 In-Game Feedback Loops

#### Immediate Feedback (per-action, <200ms)

Every player action gets instant feedback following the anti-frustration design (§3.6):

| Action | Correct Response | Incorrect Response |
|--------|-----------------|-------------------|
| Quiz answer | Star burst animation + "Correct!" + explanation | Gentle shake + "Not quite!" + hint or explanation |
| Jigsaw piece placed | Snap-to + satisfying click sound | Piece slides back + subtle glow on correct area |
| Action game dodge | Trail effect + score tick | Shield flash + "Try again" (no fail state) |
| Mission complete | Celebration sequence + rewards + unlock animation | N/A — missions don't fail, they score |

#### Session Summary Feedback

At the end of each session (or when the break reminder triggers), show:

```
┌────────────────────────────────────────────┐
│         🚀 Mission Report                  │
│                                            │
│  Time Explored:  18 minutes                │
│  Missions:       3 completed               │
│  New Facts:      7 learned                 │
│  Accuracy:       82% (Great!)              │
│  New Collection:  2 items earned           │
│                                            │
│  ★ You learned about Mars' atmosphere!     │
│  ★ New constellation node unlocked!        │
│                                            │
│  [Continue Exploring]  [Take a Break]      │
└────────────────────────────────────────────┘
```

#### Progress Feedback (long-term)

- **Knowledge Constellation** (§3.4): Visual skill tree that lights up — players SEE their learning
- **Rank Progression**: Cadet → Pilot → Commander — clear macro-level advancement
- **Streak Calendar**: Visual daily engagement record with completionist pull
- **"You've Grown" Moments**: When a player successfully answers a harder question than they could a week ago, surface it: "Last week you found orbits tricky — look at you now!"

### 26.2 Parent Feedback Dashboard

Parents (with verified accounts, §21) see an age-appropriate summary:

```
┌──────────────────────────────────────────────────────┐
│  🌟 [Child's Display Name]'s Space Report            │
│  Week of March 10–16, 2026                           │
│                                                      │
│  📊 This Week                                        │
│  ├── Play time: 2h 15min across 5 sessions           │
│  ├── Topics explored: Mars geology, asteroid orbits  │
│  ├── Quiz accuracy: 76% (up from 68% last week)      │
│  ├── Missions completed: 12                          │
│  └── Rank: Pilot (45% to Commander)                  │
│                                                      │
│  📈 Learning Progress                                │
│  ├── Strong: Astronomy (89%), Earth Science (82%)    │
│  ├── Growing: Physics (71%), Geology (68%)           │
│  └── New topic started: Space Weather                │
│                                                      │
│  🏆 Achievements This Week                           │
│  ├── "Mars Expert" badge earned                      │
│  └── 7-day streak!                                   │
│                                                      │
│  [View Full History] [Download Report] [Settings]    │
└──────────────────────────────────────────────────────┘
```

**Implementation**: Generated from aggregated rollup data, never raw events. Parent sees summary statistics, not action-by-action logs. Weekly email digest is opt-in.

### 26.3 Educator/Institutional Feedback (Future)

For schools or science centers using the platform:

- **Class Dashboard**: Aggregate view of a group of players (no individual tracking without parental consent)
- **Topic Coverage Report**: Which curriculum areas the class has engaged with
- **Difficulty Distribution**: How the class is performing relative to age-level expectations
- **Exportable Reports**: PDF/CSV for teacher records, aligned with science education standards (NGSS)

### 26.4 Player Satisfaction Signals

Beyond behavioral metrics, we need qualitative signals:

| Signal | Collection Method | Frequency |
|--------|-------------------|-----------|
| **Mission rating** | Optional 1-3 star rating after mission complete (emoji: 😐⭐🌟) | Per mission |
| **"More like this"** | Button on mission complete: "Want more missions like this?" | Per mission |
| **Bug/content report** | Report button on every screen (§22.7) | On demand |
| **Parent feedback** | Optional survey in parent dashboard (quarterly) | Quarterly |
| **NPS-style question** | "Would you tell a friend about Space Explorer?" (parent-facing only) | Semi-annually |

---

## 27. Data-Driven Content Evolution & Roadmap

### 27.1 The Feedback → Content Loop

Analytics data directly drives what we build next. This is the system's learning loop:

```
       ┌────────────────────────────┐
       │   MEASURE                  │
       │   Analytics dashboards     │
       │   (§24) track engagement,  │
       │   learning, difficulty     │
       └─────────────┬──────────────┘
                     │
                     ▼
       ┌────────────────────────────┐
       │   IDENTIFY                 │
       │   Weekly analytics review  │
       │   surfaces signals:        │
       │   • High-engagement content│
       │   • Drop-off points        │
       │   • Underserved topics     │
       │   • Difficulty mismatches  │
       └─────────────┬──────────────┘
                     │
                     ▼
       ┌────────────────────────────┐
       │   DECIDE                   │
       │   Product team prioritizes │
       │   using Impact/Effort      │
       │   framework + data signals │
       └─────────────┬──────────────┘
                     │
                     ▼
       ┌────────────────────────────┐
       │   BUILD                    │
       │   New content, difficulty  │
       │   tweaks, new game types,  │
       │   UX improvements          │
       └─────────────┬──────────────┘
                     │
                     ▼
       ┌────────────────────────────┐
       │   RELEASE & MEASURE        │
       │   Feature flags (§10.3)    │
       │   → gradual rollout        │
       │   → measure impact         │
       │   → loop back to MEASURE   │
       └────────────────────────────┘
```

### 27.2 Signal-to-Action Framework

Concrete rules for translating data signals into product decisions:

#### Content Signals

| Signal | Data Source | Action |
|--------|-----------|--------|
| A mission has >95% completion rate across all age groups | MissionRollup | Increase difficulty or create a harder variant |
| A mission has <40% completion rate for its target age group | MissionRollup | Review DDA settings → add hints → simplify or split into smaller missions |
| An API content type (e.g., Mars photos) drives 3× session length vs others | Content Popularity Dashboard | Prioritize more game types using that API. Invest in deeper content. |
| A NASA API (e.g., EONET) has low engagement despite content availability | Content Popularity Dashboard | Redesign game mechanics for that API. Consider better narrative framing. |
| Quiz question accuracy <20% across all age groups | QuizQuestionRollup | Question is broken — flag for review. Auto-generated? Check the generation pipeline. |
| Quiz question accuracy >95% across all age groups | QuizQuestionRollup | Too easy — retire or move to lower difficulty pool |
| Players rate a mission type 🌟 (love) at 2× the rate of others | Player ratings | Create more missions of that type. Analyze what makes it special. |
| A concept has high time-to-mastery vs similar concepts | Learning Dashboard | Content needs rework — better scaffolding, more practice missions, clearer explanations |

#### Engagement Signals

| Signal | Data Source | Action |
|--------|-----------|--------|
| D1 retention drops below 30% | Engagement Dashboard | Investigate onboarding funnel. Is the first session compelling enough? |
| Session length drops across cohorts | Engagement Dashboard | Check for technical issues first. Then review recent content changes. |
| Streak distribution shows >80% at streak=0 | Engagement Dashboard | Streak mechanic isn't landing — reconsider incentives, or surface it more visibly |
| A specific age group's engagement drops | Engagement Dashboard | Content gap for that age. Review DDA — is difficulty well-calibrated for them? |
| New feature rollout shows no engagement lift | Feature flag metrics | Feature isn't resonating. A/B test alternatives or remove. |

#### New Game / Feature Signals

| Signal | Conclusion | Action |
|--------|-----------|--------|
| Action games (DONKI) consistently highest engagement + ratings | Players want more real-time gameplay | Build action variants for other APIs (asteroid deflection, satellite dodging) |
| Jigsaw puzzles have high completion but low repeat play | Good first-time but no replay value | Add competitive elements: speed run, daily challenge, fewer-piece records |
| Players explore the space map extensively but skip certain planets | Content quality varies by planet | Audit low-traffic planets. Add content or improve mission variety. |
| Cross-API missions (§2.3) have highest ratings and session lengths | Multi-source missions are the best content | Invest heavily in cross-API mission design. This is the differentiator. |
| Parents report children talking about real space facts | The educational mission is working | Double down on real-data integration. Consider "dinner table facts" feature. |
| Educators request curriculum alignment | Institutional market opportunity | Build NGSS-aligned mission packs. Add educator dashboard (§26.3). |

### 27.3 A/B Testing Framework

For major changes, use controlled experiments:

```python
# apps/analytics/ab_testing.py

class Experiment(models.Model):
    slug            = models.SlugField(unique=True)
    name            = models.CharField(max_length=255)
    description     = models.TextField()
    # Traffic allocation:
    traffic_percent = models.IntegerField(default=10)  # % of eligible players
    # Targeting:
    target_age_groups = ArrayField(models.CharField(max_length=8), default=list)
    target_new_players_only = models.BooleanField(default=False)
    # State:
    status          = models.CharField(max_length=16)  # draft, running, concluded
    started_at      = models.DateTimeField(null=True)
    concluded_at    = models.DateTimeField(null=True)
    winner_variant  = models.CharField(max_length=64, blank=True)
    # Success metric:
    primary_metric  = models.CharField(max_length=64)  # e.g., 'mission_completion_rate'
    minimum_sample  = models.IntegerField(default=500) # Min players before concluding


class ExperimentVariant(models.Model):
    experiment      = models.ForeignKey(Experiment, related_name='variants')
    slug            = models.SlugField()  # 'control', 'variant_a', 'variant_b'
    config          = models.JSONField()  # Variant-specific configuration
    # Results (computed):
    sample_size     = models.IntegerField(default=0)
    metric_value    = models.FloatField(null=True)
    confidence      = models.FloatField(null=True)     # Statistical significance


class PlayerExperiment(models.Model):
    """Assigns a player to an experiment variant. Stable once assigned."""
    player_id       = models.UUIDField()
    experiment      = models.ForeignKey(Experiment)
    variant         = models.ForeignKey(ExperimentVariant)
    assigned_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('player_id', 'experiment')
```

**A/B testing rules for a children's product:**
- Never test changes that could harm the learning experience for the control group
- Maximum 2 concurrent experiments per player
- Experiments must have a clear hypothesis and success metric defined before starting
- Minimum sample sizes enforced before drawing conclusions
- No experiments on wellbeing features (break reminders, time limits) — those are always on

### 27.4 Content Roadmap Cadence

| Cadence | Activity | Data Input |
|---------|----------|-----------|
| **Daily** | Auto-moderation queues processed. DDA health check (automated alerts). | Automated anomaly detection |
| **Weekly** | Analytics review meeting. Review mission completion funnels, quiz difficulty outliers, engagement trends. Adjust DDA thresholds if needed. Prioritize content tweaks. | All dashboards |
| **Monthly** | Content planning. Identify next game types to build, APIs to expand, missions to create. Review A/B test results. | Monthly rollup + experiment results |
| **Quarterly** | Strategic review. Assess learning outcomes data. Plan major features. Review platform goals against engagement and retention benchmarks. Update roadmap. | Quarterly trends + parent surveys + educator feedback |
| **On NASA event** | Real-world space events (eclipses, launches, asteroid flybys) → fast-track themed content. Use DONKI/EONET/NeoWs real-time data. | NASA event calendar + real-time API data |

### 27.5 Automated Alerts & Anomaly Detection

The system proactively surfaces issues without waiting for manual review:

```python
# apps/analytics/alerts.py

ALERT_RULES = [
    {
        'name': 'dau_drop',
        'description': 'DAU dropped >20% vs same day last week',
        'query': 'compare_metric("dau", period="week", threshold=-0.20)',
        'severity': 'high',
        'channel': 'slack:#analytics-alerts',
    },
    {
        'name': 'mission_completion_crash',
        'description': 'Any mission completion rate dropped >25% in 24h',
        'query': 'detect_drop("mission_completion_rate", window="24h", threshold=-0.25)',
        'severity': 'high',
        'channel': 'slack:#game-design',
    },
    {
        'name': 'dda_oscillation',
        'description': '>10% of players had 3+ DDA level changes in one session',
        'query': 'dda_stability_check(max_changes=3, player_threshold=0.10)',
        'severity': 'medium',
        'channel': 'slack:#game-design',
    },
    {
        'name': 'quiz_broken',
        'description': 'Quiz question with <10% accuracy and >50 attempts',
        'query': 'quiz_outlier(accuracy_max=0.10, min_attempts=50)',
        'severity': 'medium',
        'channel': 'slack:#content-team',
    },
    {
        'name': 'onboarding_dropout',
        'description': 'Onboarding step completion drops below 70%',
        'query': 'funnel_step_check("onboarding", min_rate=0.70)',
        'severity': 'high',
        'channel': 'slack:#product',
    },
    {
        'name': 'session_length_anomaly',
        'description': 'Average session length changed >30% vs 7-day rolling avg',
        'query': 'compare_metric("avg_session_seconds", period="7d_rolling", threshold=0.30)',
        'severity': 'medium',
        'channel': 'slack:#analytics-alerts',
    },
]
```

### 27.6 New Game Creation Pipeline (Data-Informed)

When analytics indicate the need for a new game type or feature, the pipeline follows:

```
1. SIGNAL       Analytics surfaces opportunity
                (e.g., "action games are 2× engagement, but only 1 API uses them")
                │
2. HYPOTHESIS   "Adding an action game for NeoWs (asteroid deflection)
                 will increase NeoWs API engagement by 50%"
                │
3. PROTOTYPE    Game designer creates mission in admin panel (§10.4)
                Preview mode for internal testing
                │
4. SOFT LAUNCH  Feature flag → 10% of target age group
                A/B test vs existing NeoWs content
                │
5. MEASURE      2-week data collection:
                - Engagement lift? Session length? Retention?
                - Learning outcomes maintained?
                - DDA functioning for new game type?
                - Player ratings vs control?
                │
6. DECISION     If metrics meet hypothesis → full rollout
                If not → iterate or retire
                │
7. ROLLOUT      Feature flag → 100%
                Add to content calendar
                Monitor for 30 days post-launch
```

This pipeline ensures no new game ships without data-backed validation, while the feature flag system (§10.3) allows safe experimentation without risk to the full player base.

---

# Part VII — Reference

## 28. Technology Stack Recap & Team Organization

A single-page view of every technology, tool, and service in this plan — organized by team competency to help project leads staff the project and stakeholders understand resource requirements. Each item links back to the section(s) where it's used in depth.

### 28.1 Stack-at-a-Glance

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          NASA SPACE EXPLORER                            │
│                         Technology Stack Map                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐        │
│   │    FRONTEND     │  │     BACKEND     │  │     INFRA       │        │
│   ├─────────────────┤  ├─────────────────┤  ├─────────────────┤        │
│   │ React / Next.js │  │ Python / Django │  │ AWS             │        │
│   │ TypeScript      │  │ DRF             │  │ ├─ ECS Fargate  │        │
│   │ PixiJS          │  │ Celery + Beat   │  │ ├─ RDS Postgres │        │
│   │ Zustand         │  │ PostgreSQL      │  │ ├─ ElastiCache  │        │
│   │ TanStack Query  │  │ Redis           │  │ ├─ S3 + CloudFr.│        │
│   │ Tailwind CSS    │  │ Pillow / NumPy  │  │ ├─ Secrets Mgr  │        │
│   │ Framer Motion   │  │ Gunicorn        │  │ └─ ALB / IAM    │        │
│   │ Howler.js       │  │ PgBouncer       │  │ Cloudflare CDN  │        │
│   │ D3 / Three.js   │  │ django-guardian │  │ Terraform       │        │
│   │ Workbox SW      │  │ Flower          │  │ Docker          │        │
│   │ IndexedDB       │  │                 │  │ GitHub Actions  │        │
│   └─────────────────┘  └─────────────────┘  └─────────────────┘        │
│                                                                         │
│   ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐        │
│   │  OBSERVABILITY  │  │  THIRD-PARTY    │  │   EXTERNAL DATA │        │
│   ├─────────────────┤  ├─────────────────┤  ├─────────────────┤        │
│   │ Sentry          │  │ Stripe (VPC)    │  │ NASA Open APIs  │        │
│   │ CloudWatch      │  │ Plausible       │  │ ├─ APOD         │        │
│   │ Prometheus      │  │ SendGrid/SES    │  │ ├─ NeoWs        │        │
│   │ Grafana         │  │                 │  │ ├─ DONKI        │        │
│   │ PagerDuty       │  │                 │  │ ├─ EPIC         │        │
│   │ UptimeRobot     │  │                 │  │ ├─ Mars Rovers  │        │
│   │                 │  │                 │  │ ├─ Exoplanets   │        │
│   │                 │  │                 │  │ └─ +6 more      │        │
│   └─────────────────┘  └─────────────────┘  └─────────────────┘        │
└─────────────────────────────────────────────────────────────────────────┘
```

### 28.2 Detailed Inventory by Layer

#### Backend Application

| Technology | Role | Plan Reference | Core Skill |
|------------|------|----------------|------------|
| **Python 3.x** | Primary backend language | §7 | Required |
| **Django** | Web framework, ORM, admin | §7.1, §10 | Required |
| **Django REST Framework** | API serialization, permissions, throttling | §7.4, §9.7 | Required |
| **Celery** | Async task queue for NASA ingestion & image processing | §7.3, §5.1 | Required |
| **Celery Beat** | Scheduled task runner (cron replacement) | §5.3, §11.3 | Same as Celery |
| **Gunicorn** | WSGI HTTP server | §11.3 | Deploy-time only |
| **PgBouncer** | Connection pooling sidecar | §11.6 | Deploy-time only |
| **Pillow** | Image processing (resize, WebP, jigsaw slicing) | §7.5, §6.5 | Required |
| **NumPy** | Numerical operations for puzzle generation | §7.1 | Nice-to-have |
| **django-guardian** | Object-level permissions for admin roles | §10.2 | Nice-to-have |
| **Flower** | Celery task monitoring dashboard | §10.3 | Ops only |

#### Data Stores

| Technology | Role | Plan Reference | Core Skill |
|------------|------|----------------|------------|
| **PostgreSQL** | Primary database — NASA content, users, progress, analytics | §8, §24.3 | Required |
| **Postgres partitioning** | Day-partitioned raw event tables for analytics | §24.3 | Required (analytics) |
| **Postgres materialized views** | Pre-computed analytics rollups | §24.3 | Required (analytics) |
| **Redis** | Cache layer, session store, leaderboards, DDA state, Celery broker | §6.2, §8.4, §25.4 | Required |
| **Redis Streams** | Analytics event buffer | §24.3 | Required (analytics) |
| **Redis Sorted Sets** | Leaderboard rankings (ZADD/ZRANGE) | §8.4 | Required |

#### Frontend Application

| Technology | Role | Plan Reference | Core Skill |
|------------|------|----------------|------------|
| **React** | UI component framework | §12 | Required |
| **Next.js** | App framework — SSR, ISR, image optimization, routing | §12.2, §11.3 | Required |
| **TypeScript** | Type-safe frontend code | §13.3, §15.1 | Required |
| **PixiJS** | 2D WebGL game engine for interactive scenes | §13.1 | Required (game team) |
| **@pixi/react** | React integration wrapper for PixiJS | §13.1 | Same as PixiJS |
| **Zustand** | State management across React + game bridge | §15.1 | Required |
| **TanStack Query** | API client — caching, dedup, background refetch | §6.2, §12.2 | Required |
| **Tailwind CSS** | Utility-first styling + theme tokens | §12.2, §16 | Required |
| **Framer Motion** | Declarative DOM animations (reduced-motion aware) | §19.2 | Required |
| **Howler.js** | Cross-browser audio engine, sound sprites, spatial | §20, §12.2 | Required |
| **D3.js** | Data visualizations (orbit diagrams, charts) | §12.2 | Nice-to-have |
| **Three.js** | 3D visualizations where needed | §12.2 | Nice-to-have |
| **Workbox** | Service Worker toolkit for offline play | §6.2 | Required |
| **IndexedDB** | Browser-side persistent storage for offline progress | §6.2 | Required |

#### Infrastructure & DevOps

| Technology | Role | Plan Reference | Core Skill |
|------------|------|----------------|------------|
| **AWS** | Primary cloud provider | §11.2 | Required |
| **ECS Fargate** | Serverless container orchestration | §11.3 | Required |
| **RDS (PostgreSQL)** | Managed database, Multi-AZ + read replica | §11.6 | Required |
| **ElastiCache (Redis)** | Managed Redis | §11.6 | Required |
| **S3** | Object storage — media, assets, raw JSON, backups | §11.4 | Required |
| **CloudFront** | Inner CDN tier — origin shield | §11.5, §6.2 | Required |
| **Cloudflare** | Outer CDN tier — unlimited egress bandwidth | §11.5 | Required |
| **ALB** | Load balancer for web + nextjs services | §11.3 | Required |
| **IAM** | Role-based AWS access, no long-lived credentials | §9.3, §11.2 | Required |
| **AWS Secrets Manager** | API key and credential storage | §9.2 | Required |
| **Route53** | DNS | §11.8 | Required |
| **NAT Gateway** | Outbound internet for private subnets | §11.9 | Deploy-time only |
| **ECR** | Docker image registry | §11.8 | Deploy-time only |
| **Terraform** | Infrastructure-as-Code for all AWS resources | §11.8 | Required |
| **Docker** | Container images + local dev (Compose) | §11.8 | Required |
| **GitHub Actions** | CI/CD pipeline — build, test, deploy, rollback | §11.8, §9.2 | Required |

#### Observability & Operations

| Technology | Role | Plan Reference | Core Skill |
|------------|------|----------------|------------|
| **Sentry** | Error tracking + performance traces (PII-scrubbed) | §11.11, §21.6 | Required |
| **CloudWatch** | AWS infrastructure metrics + budget alarms | §11.11, §11.9 | Required |
| **Prometheus** | Custom business metrics exporter | §11.11 | Required |
| **Grafana** | Metrics dashboards | §11.11 | Required |
| **PagerDuty** | On-call alerting and escalation | §11.11 | Ops only |
| **UptimeRobot / Pingdom** | External black-box health probes | §11.11 | Ops only |
| **SNS** | Alert routing (budget alarms → Slack) | §11.9 | Deploy-time only |

#### Third-Party Services

| Service | Role | Plan Reference | Notes |
|---------|------|----------------|-------|
| **Stripe** | Parental verification via credit card charge | §21.3 | Parent data only, never child data |
| **Plausible** | Privacy-respecting page analytics (self-hosted option) | §21.6, §24.1 | Cookieless, no user-level tracking |
| **SendGrid / AWS SES** | Transactional email (parent verification) | §21.3 | Parent-facing only |
| **Slack** | Alert channels for analytics anomalies & ops | §27.5, §11.9 | Internal only |

#### External Data Sources (NASA Open APIs)

| API | Data | Ingestion Cadence | Plan Reference |
|-----|------|-------------------|----------------|
| **APOD** | Astronomy Picture of the Day | Daily 05:00 UTC | §2.2.1, §5.3 |
| **Mars Rover Photos** | Curiosity, Perseverance, Opportunity imagery | Daily | §2.2.2, §5.3 |
| **NeoWs** | Near-Earth Object approach data | Hourly | §2.2.3, §5.3 |
| **DONKI** | Space weather — solar flares, CMEs | Every 15 min | §2.2.4, §5.3 |
| **EPIC** | Full-disc Earth imagery from L1 | Every 6 hours | §2.2.5, §5.3 |
| **Exoplanet Archive** | Confirmed exoplanet catalog | Weekly | §2.2.6, §5.3 |
| **NASA Image & Video Library** | Historical mission archive | On-demand | §2.2.7, §5.3 |
| **Insight Weather** | Mars surface meteorology | Daily | §2.1 |
| **TLE** | Satellite orbital elements (ISS tracking) | Every 30 seconds | §2.1, §5.3 |
| **TechTransfer** | NASA patents and spinoffs | On-demand | §2.1 |
| **EONET** | Live Earth natural events | Every 30 min | §2.2.8, §5.3 |
| **SSD/CNEOS** | Small body orbit calculations | On-demand | §2.1 |

#### Design & Content Assets

| Asset Type | Tool / Source | Plan Reference |
|------------|---------------|----------------|
| **Typography** | Orbitron (headings), Nunito (body), JetBrains Mono (data) | §17 |
| **Illustrations** | Original, work-for-hire agreements | §23.4 |
| **Sound effects** | Original or royalty-free commercial license | §20, §23.4 |
| **Background music** | Commissioned or commercial-license stock | §23.4 |
| **NASA audio** | Public domain mission comms/telemetry only | §20, §23.1 |

### 28.3 Team Organization Guide

Suggested team structure mapped to technology ownership. Sizes are indicative for the growth phase (~50K DAU).

```
┌─────────────────────────────────────────────────────────────────────┐
│                         PRODUCT & DESIGN                            │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐       │
│  │ Game Designer   │ │ Content Curator │ │ UX Designer     │       │
│  │ Mission design, │ │ NASA content    │ │ UI/IA, age-     │       │
│  │ difficulty,     │ │ review, quiz    │ │ adaptive design,│       │
│  │ progression     │ │ writing         │ │ accessibility   │       │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘       │
│  Reads: §1-4, §25, §27           Tools: Admin Panel (§10)          │
└─────────────────────────────────────────────────────────────────────┘
                                 │
┌─────────────────────────────────────────────────────────────────────┐
│                          ENGINEERING                                │
│                                                                     │
│  ┌─────────────────────────┐  ┌─────────────────────────┐          │
│  │   Frontend Team (2-3)   │  │   Backend Team (2-3)    │          │
│  │                         │  │                         │          │
│  │ • React / Next.js / TS  │  │ • Python / Django / DRF │          │
│  │ • Tailwind / Framer     │  │ • Celery task design    │          │
│  │ • TanStack Query        │  │ • PostgreSQL schema     │          │
│  │ • Service Worker / PWA  │  │ • Redis patterns        │          │
│  │ • Accessibility (WCAG)  │  │ • Analytics pipeline    │          │
│  │                         │  │ • Security (COPPA)      │          │
│  │ Reads: §12, §14-15, §19 │  │ Reads: §5-10, §21, §24  │          │
│  └─────────────────────────┘  └─────────────────────────┘          │
│                                                                     │
│  ┌─────────────────────────┐  ┌─────────────────────────┐          │
│  │   Game Engine Team (1-2)│  │   Platform / DevOps (1) │          │
│  │                         │  │                         │          │
│  │ • PixiJS scenes         │  │ • Terraform / AWS       │          │
│  │ • Game bridge API       │  │ • ECS / RDS / Redis ops │          │
│  │ • Howler.js audio       │  │ • CI/CD (GitHub Actions)│          │
│  │ • D3 / Three.js vis     │  │ • CDN config            │          │
│  │ • 60fps perf budget     │  │ • Observability stack   │          │
│  │                         │  │ • On-call rotation      │          │
│  │ Reads: §13, §19-20      │  │ Reads: §6, §9, §11      │          │
│  └─────────────────────────┘  └─────────────────────────┘          │
└─────────────────────────────────────────────────────────────────────┘
                                 │
┌─────────────────────────────────────────────────────────────────────┐
│                     OPERATIONS & COMPLIANCE                         │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐       │
│  │ Moderator       │ │ Safety Officer  │ │ Data Analyst    │       │
│  │ Display names,  │ │ COPPA/GDPR,     │ │ Dashboards,     │       │
│  │ content queue,  │ │ incident        │ │ A/B tests,      │       │
│  │ reports (§22.8) │ │ response (§22.7)│ │ roadmap (§27)   │       │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘       │
│  Reads: §21-23                    Tools: Admin Panel, Grafana       │
└─────────────────────────────────────────────────────────────────────┘
```

### 28.4 Skill Matrix for Hiring

| Role | Must Have | Should Have | Nice to Have |
|------|-----------|-------------|--------------|
| **Backend Engineer** | Python, Django, PostgreSQL, REST API design | Celery, Redis, Docker | NASA API familiarity, image processing |
| **Frontend Engineer** | React, TypeScript, CSS, responsive/a11y | Next.js, state management, SW/PWA | Animation, children's UX |
| **Game Engineer** | JavaScript/TS, canvas/WebGL, game loop fundamentals | PixiJS (or Phaser/similar), audio engines | Particle systems, shader basics |
| **Platform Engineer** | AWS (ECS, RDS, S3, IAM), Terraform, Docker | CDN tuning, cost optimization, observability | Security hardening, DR drills |
| **Game Designer** | Educational game design, progression systems, difficulty tuning | Analytics-informed iteration, children's psychology | NASA/space domain knowledge |
| **Content Curator** | Science communication for children, fact-checking | NASA ecosystem knowledge, quiz design | Education standards (NGSS) |
| **Data Analyst** | SQL, statistical significance, dashboard design | A/B testing methodology, Python/pandas | Learning science metrics |

### 28.5 Shared Ownership & Cross-Cutting Concerns

Some responsibilities span multiple teams and require explicit coordination:

| Concern | Primary Owner | Must Coordinate With | Why |
|---------|--------------|----------------------|-----|
| **DDA tuning** | Game Designer | Backend (Redis state), Data Analyst (thresholds) | DDA lives in Redis (§25.4) but thresholds are a design decision informed by analytics |
| **Analytics event schema** | Backend | Frontend (emit), Data Analyst (consume) | Frontend emits events, backend validates/stores, analyst queries — all three must agree on schema (§24.2) |
| **COPPA compliance** | Safety Officer | Backend (data model), Frontend (consent flows), Platform (audit logs) | Privacy touches every layer (§21) |
| **Performance budgets** | Platform | Frontend (bundle size), Game (60fps), Backend (p99 latency) | §6.8 and §19.5 define budgets; each team owns their slice |
| **Content pipeline** | Content Curator | Backend (ingestion), Game Designer (mission linking) | NASA data flows through ingestion → curation → mission design (§7.3, §22.3) |
| **Feature flags** | Platform | Everyone | Flags gate deploys across all surfaces (§10.3, §27.6) |

### 28.6 Onboarding Reading Order

For a new team member, the recommended reading path through this plan:

| Week | Sections | Goal |
|------|----------|------|
| **Day 1** | §1, §2.1, §5, §28 | Understand the product vision and the system at 10,000 feet |
| **Week 1** | Your team's primary sections (see §28.3) | Deep dive on your area of ownership |
| **Week 2** | §6 (caching), §21 (privacy), §24 (analytics) | The three cross-cutting systems everyone touches |
| **Ongoing** | Sections referenced from your tickets | Just-in-time depth as work requires |
