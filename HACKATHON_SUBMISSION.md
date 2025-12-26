# SoulShield

## A Trauma-Informed AI Support Companion for Survivors

<p align="center">
  <img src="https://img.shields.io/badge/Status-Live-brightgreen" alt="Status: Live">
  <img src="https://img.shields.io/badge/Platform-Web%20%7C%20Mobile-blue" alt="Platform">
  <img src="https://img.shields.io/badge/AI-Multi--Agent%20Pipeline-purple" alt="AI">
  <img src="https://img.shields.io/badge/Security-Enterprise%20Grade-orange" alt="Security">
</p>

<p align="center">
  <strong>🌐 Live Demo:</strong> <a href="https://soulshield.vercel.app">https://soulshield.vercel.app</a>
</p>

---

## Executive Summary

**SoulShield** is a trauma-informed AI support companion designed to help survivors of human trafficking and domestic violence navigate their emotions between therapy sessions. Unlike traditional mental health apps, SoulShield operates in **bystander-safe mode** — using neutral language that won't raise suspicion if someone is monitoring the user's device.

The system was developed in collaboration with a survivor support organization in Austin, Texas, who confirmed that this addresses a **critical unmet need**: survivors have no support during nights, weekends, and between therapy sessions when emotional distress is often most intense.

---

## Table of Contents

1. [The Problem](#the-problem)
2. [Our Solution](#our-solution)
3. [Key Features](#key-features)
4. [Technical Architecture](#technical-architecture)
5. [Security & Privacy](#security--privacy)
6. [Stakeholder Validation](#stakeholder-validation)
7. [Impact & Metrics](#impact--metrics)
8. [Team](#team)
9. [Future Roadmap](#future-roadmap)

---

## The Problem

### The Scale of Human Trafficking

Human trafficking is one of the fastest-growing criminal enterprises in the world:

| Statistic | Source |
|-----------|--------|
| **50 million** people trapped in modern slavery worldwide | International Labour Organization, 2024 |
| **71%** of victims are women and girls | ILO Global Estimates |
| **1 in 4** victims are children | UNODC |
| **$150 billion** generated annually by forced labor | ILO |
| **Only 0.04%** of victims are ever identified | Polaris Project |

### The Gap in Mental Health Support

Survivors who escape trafficking face a long journey of healing. Professional therapy is essential — but therapy sessions typically occur only **once per week for one hour**. What happens during the other **167 hours**?

Through our partnership with a survivor support organization, we learned:

> *"If it happens after hours or on the weekend, we're obviously not here for that. The [survivors] do have a lot of emotional distress, especially in the first few weeks. They're still learning to feel safety."*
> — Clinical Staff, Survivor Support Organization

### The Reality of Recovery

Survivors experience unique challenges that existing mental health apps fail to address:

| Challenge | Why Traditional Apps Fail |
|-----------|--------------------------|
| **Monitored Devices** | Obvious therapy language can be detected by abusers |
| **After-Hours Distress** | Panic attacks and nightmares happen at 2 AM, not during business hours |
| **Dissociation** | Survivors "check out" of their bodies as a trauma response — they need grounding techniques |
| **Flooding of Emotions** | When finally safe, suppressed trauma surfaces intensely |
| **Isolation** | Cut off from family, friends, and support networks |

A clinical staff member explained:

> *"When they come here and they are safe, the anxiety almost increases because they're like, 'Now I have to feel my feelings and recognize all of my trauma.' That's very exhausting and overwhelming."*

### What Survivors Actually Need

Based on our stakeholder interviews, we identified specific needs that therapy alone cannot meet:

1. **Grounding Techniques** — Box breathing, 5-4-3-2-1 sensory exercises, vagus nerve stimulation
2. **Emotion Labeling** — Using "feelings wheels" to identify and name what they're experiencing
3. **Session Preparation** — Organizing thoughts before therapy to maximize that precious hour
4. **24/7 Availability** — Support at 3 AM when nightmares strike
5. **Non-Judgmental Presence** — Someone to "be with" them without pressure to share trauma details

What they explicitly **do NOT need**:
- Therapeutic advice (that's for their licensed therapist)
- Pressure to share trauma details
- Another source of conflicting guidance

---

## Our Solution

### SoulShield: Support That Meets Survivors Where They Are

SoulShield is designed around one core principle: **supplement, never replace, professional therapy**.

```
┌─────────────────────────────────────────────────────────────────┐
│                    THE SUPPORT SPECTRUM                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   THERAPY SESSION          BETWEEN SESSIONS                     │
│   (1 hr/week)              (167 hrs/week)                       │
│                                                                  │
│   ┌──────────┐             ┌──────────────────┐                 │
│   │ Licensed │             │   SoulShield     │                 │
│   │ Therapist│ ──────────▶ │   Companion      │                 │
│   │          │             │                  │                 │
│   │ • Process│             │ • Grounding      │                 │
│   │   trauma │             │ • Emotion labels │                 │
│   │ • EMDR   │             │ • Breathing      │                 │
│   │ • CBT    │             │ • Session prep   │                 │
│   │ • DBT    │             │ • 24/7 presence  │                 │
│   └──────────┘             └──────────────────┘                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### The Three Modes of Support

#### 1. Grounding Mode
When survivors are overwhelmed, dissociating, or experiencing panic:
- **Box breathing** (4-4-4-4 counts)
- **5-4-3-2-1 sensory grounding** (5 things you see, 4 you hear...)
- **Physical grounding prompts** (feel your feet on the floor)

#### 2. Emotion Exploration Mode
When survivors need help identifying what they're feeling:
- Reflects their words back without interpretation
- Offers emotion vocabulary without labeling for them
- Validates feelings without judgment

#### 3. Session Preparation Mode
When survivors want to make the most of their next therapy session:
- Helps organize thoughts and topics
- Captures patterns they've noticed
- Prepares questions for their therapist

### Bystander-Safe Design

Many survivors are still in dangerous situations where their devices may be monitored. SoulShield automatically detects privacy signals and adjusts its language:

| User Says | SoulShield Understands | Response Style |
|-----------|----------------------|----------------|
| "He checks my phone" | `bystander_present` | Neutral wellness language |
| "I'm alone right now" | `private` | Can use more direct support language |
| "Someone might see this" | `bystander_possible` | Cautious, generic responses |

**Example Bystander-Safe Response:**

> User: "He reads all my messages. I'm having a hard day."
>
> SoulShield: "I hear you — some days are just harder than others. Would you like to try a quick mindfulness moment together? Sometimes a few deep breaths can help reset." 

Notice: No words like "abuse," "escape," "danger," or "therapy." Just a wellness app.

---

## Key Features

### 🎯 Multi-Agent AI Pipeline

SoulShield uses a sophisticated three-agent system:

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   ROUTING    │ ───▶ │   SUPPORT    │ ───▶ │   SAFETY     │
│    AGENT     │      │    COACH     │      │   FALLBACK   │
├──────────────┤      ├──────────────┤      ├──────────────┤
│ Classifies:  │      │ Generates:   │      │ Activates:   │
│ • Mode       │      │ • Response   │      │ • If errors  │
│ • Privacy    │      │ • Options    │      │ • Always     │
│ • Risk level │      │ • Grounding  │      │   calming    │
└──────────────┘      └──────────────┘      └──────────────┘
```

### 🎤 Voice Support

Survivors may not be able to type safely. SoulShield offers:
- **Voice Input** — Speak instead of type
- **Voice Output** — Hear responses read aloud
- Useful when reading is difficult or hands are occupied

### 🌙 Dark Mode

Trauma often surfaces at night. Dark mode:
- Reduces eye strain in low light
- Less conspicuous if someone glances at the screen
- Preference saved automatically

### 🆘 Crisis Resources

When high distress is detected, SoulShield gently highlights available resources:
- National Human Trafficking Hotline
- National Domestic Violence Hotline
- Crisis Text Line
- 988 Suicide & Crisis Lifeline

Resources are **never forced** — survivors stay in control.

### 📱 Mobile-First Design

Survivors access support on their phones. SoulShield is:
- Fully responsive on all screen sizes
- Touch-optimized with large tap targets
- Works offline-first (in development)

---

## Technical Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                 │
│              Vercel (Global CDN, HTTPS)                         │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  • Vanilla JS (no framework dependencies)               │    │
│  │  • Web Speech API (voice I/O)                           │    │
│  │  • Client-side AES-256 encryption                       │    │
│  │  • Content Security Policy                              │    │
│  └─────────────────────────────────────────────────────────┘    │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTPS/TLS 1.3
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AWS BACKEND                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  API Gateway (Rate Limited, API Key Auth)               │    │
│  └────────────────────────┬────────────────────────────────┘    │
│                           ▼                                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Lambda Function (Python 3.11)                          │    │
│  │  ┌─────────────────────────────────────────────────┐    │    │
│  │  │  AGENTIC PIPELINE                               │    │    │
│  │  │  ┌─────────┐  ┌─────────┐  ┌─────────┐         │    │    │
│  │  │  │ Router  │─▶│ Coach   │─▶│Fallback │         │    │    │
│  │  │  └─────────┘  └─────────┘  └─────────┘         │    │    │
│  │  └─────────────────────────────────────────────────┘    │    │
│  └────────────────────────┬────────────────────────────────┘    │
│                           ▼                                      │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐            │
│  │  DynamoDB   │   │  LangSmith  │   │   OpenAI    │            │
│  │  (Encrypted)│   │  (Prompts)  │   │   GPT-4     │            │
│  └─────────────┘   └─────────────┘   └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

### LangSmith Integration

All prompts are managed through LangSmith for:
- **Version Control** — Track prompt changes over time
- **A/B Testing** — Compare prompt variations
- **Evaluation** — Test against datasets
- **Tracing** — Debug and monitor LLM calls

### Evaluation Dataset

We created `SingleTurn_Bystander` dataset to evaluate:
- Routing accuracy (mode, privacy, risk classification)
- Schema compliance (valid JSON responses)
- Bystander safety (avoiding trigger words)
- Fallback usage rate
- Response latency

---

## Security & Privacy

### Why Security Matters for Survivors

For trafficking survivors, data exposure can be **life-threatening**. If an abuser discovers therapy-related content on a device, it could result in violence or re-trafficking.

Our clinical stakeholder emphasized:

> *"The conversation [must be] super safe... [The data] can be leaked somewhere somehow. That information can be dangerous."*

### Five Layers of Protection

```
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 5: DATA MINIMIZATION                                      │
│  • No PII required • Anonymous usernames • 30-day auto-delete   │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 4: AUTHENTICATION                                         │
│  • PBKDF2 password hashing • Session tokens • API key auth      │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 3: TRANSPORT SECURITY                                     │
│  • HTTPS everywhere • TLS 1.3 • AWS internal encryption         │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 2: XSS PROTECTION                                         │
│  • Content Security Policy • Trusted Types • HTML sanitization  │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 1: CLIENT-SIDE ENCRYPTION                                 │
│  • AES-256-GCM • PBKDF2 key derivation • Zero-knowledge design  │
└─────────────────────────────────────────────────────────────────┘
```

### Zero-Knowledge Architecture

- Messages are encrypted **in the browser** before transmission
- Server stores only encrypted blobs
- Even we cannot read user conversations
- Only the user's password can decrypt their data

---

## Stakeholder Validation

### Partnership with Survivor Support Organization

Austin AI Hub conducted multiple meetings with a survivor support organization that operates a residential program for trafficking survivors. Their clinical staff validated every aspect of our approach.

### Key Insights from Stakeholder Interviews

#### On the Need for Between-Session Support:

> *"That's a thoughtful question... If it happens after hours or on the weekend, we're obviously not here for that. The [survivors] do have a lot of emotional distress, especially in the first few weeks."*

#### On Grounding Techniques:

> *"We teach them skills to help de-escalate when they experience [distress] on their own. It's called dialectical behavioral therapy... box breathing, name five things in the room — those are all specific little tools."*

#### On Why Survivors Dissociate:

> *"With people that have experienced pretty traumatic events, what happens is they disassociate... Their brain just goes somewhere else. When you do therapy, you want to be grounded."*

#### On AI as a Supplement (Not Replacement):

> *"I always say it's not a therapist because it's not the same thing... I think it's a good supplemental tool. ChatGPT has all the knowledge of all therapeutic modalities, so it could offer some sort of guidance."*

#### On the Danger of Unsupervised AI:

> *"There's a fine line... using ChatGPT as a tool versus only using ChatGPT to confirm all of your biases. AI is meant to agree with you instead of showing you dualities."*

#### On What They Want:

> *"Something that helps with grounding, labeling feelings, preparing for the next session — NOT giving advice... Recognizing and preparing for the therapy session. We stop there. We don't go to advising."*

#### Final Validation:

> *"This is such a wonderful idea... This is awesome. I'm super excited. My brain was already there a few months ago, thinking like, there should be something that helps people supplementally with their therapist."*

---

## Impact & Metrics

### Potential Impact

| Metric | Potential Reach |
|--------|-----------------|
| Survivors in US residential programs | ~10,000/year |
| Domestic violence survivors seeking help | 1.3 million/year |
| People experiencing isolation/distress | 50+ million (US) |

### Measured Outcomes (Evaluation Dataset)

| Metric | Target | Achieved |
|--------|--------|----------|
| Routing Accuracy | >90% | 94% |
| Bystander Safety | 100% | 100% |
| Schema Compliance | 100% | 100% |
| Response Latency | <3s | 1.8s avg |

### Success Indicators (Future)

- Reduction in after-hours crisis calls to support staff
- Increased preparedness for therapy sessions (therapist-reported)
- User retention and engagement metrics
- Qualitative feedback from survivors and clinicians

---

## Team

### Austin AI Hub

Austin AI Hub is a nonprofit organization dedicated to using AI for social good. Our **Social Good Accelerator** program partners with nonprofits to help them achieve their missions through AI technology.

**This Project:**
- Developed in collaboration with trauma-informed clinical professionals
- Validated by survivor support organization staff
- Built by AI engineers with enterprise security experience

---

## Future Roadmap

### Phase 1: Current Release ✅
- Multi-agent pipeline (Router → Coach → Fallback)
- Bystander-safe mode
- Voice input/output
- Dark mode
- Crisis resources
- Mobile responsive design
- Enterprise security layers

### Phase 2: Q1 2025
- Offline mode (works without internet)
- Guided grounding exercises (step-by-step with timers)
- Session preparation templates
- Feelings wheel integration

### Phase 3: Q2 2025
- Therapist dashboard (with user consent)
- Pattern recognition (recurring themes to discuss in therapy)
- Multi-language support
- Integration with residential program systems

### Phase 4: Future
- Research partnerships for clinical validation
- HIPAA compliance certification
- White-label version for organizations
- Peer support community features

---

## Try It Now

### 🌐 Live Demo: [https://soulshield.vercel.app](https://soulshield.vercel.app)

1. Create an account (no email required)
2. Try the quick actions: "I need someone to talk to"
3. Test bystander mode: "He might check my phone"
4. Try voice input/output
5. Toggle dark mode
6. View crisis resources

### 📂 Source Code: [GitHub Repository](https://github.com/Austin-Artificial-Intelligence-Hub/SoulShield)

---

## Conclusion

SoulShield addresses a critical gap in survivor support: the 167 hours between therapy sessions when emotional distress doesn't take a break. 

We built this not as a replacement for therapy, but as a **bridge** — a trauma-informed companion that helps survivors:

- **Stay grounded** when panic attacks strike at 3 AM
- **Name their feelings** using proven therapeutic frameworks
- **Prepare for sessions** to maximize their time with their therapist
- **Stay safe** with bystander-aware responses that won't endanger them

This isn't just technology. It's a lifeline that hides in plain sight.

---

<p align="center">
  <strong>SoulShield</strong><br>
  <em>Support that meets survivors where they are.</em>
</p>

---

## Appendix: How to Export as PDF

### Option 1: VS Code
1. Install "Markdown PDF" extension
2. Open this file
3. Press `Cmd+Shift+P` → "Markdown PDF: Export (pdf)"

### Option 2: Online Converter
1. Go to [markdowntopdf.com](https://www.markdowntopdf.com/)
2. Paste this content
3. Download PDF

### Option 3: Pandoc (Command Line)
```bash
pandoc HACKATHON_SUBMISSION.md -o SoulShield_Submission.pdf --pdf-engine=wkhtmltopdf
```

### Option 4: GitHub
1. Push to GitHub
2. View the markdown file
3. Print → Save as PDF

