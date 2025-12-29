# SoulShield - Project Story

> Copy each section below into the corresponding field on Devpost

---

## Inspiration

It started with a conversation that changed everything. During a meeting with a survivor support organization in Austin, a clinical staff member told us:

> *"If it happens after hours or on the weekend, we're obviously not here for that. The survivors do have a lot of emotional distress, especially in the first few weeks."*

We learned that **50 million people** are trapped in modern slavery worldwide. Those who escape receive therapy once a week — but trauma doesn't follow a schedule. Panic attacks happen at 3 AM. Nightmares don't wait for business hours.

Existing mental health apps fail survivors for one critical reason: they use obvious clinical language. If an abuser checks a victim's phone and sees words like "therapy" or "abuse," it could mean violence. We asked: *What if we could build support that hides in plain sight?*

---

## What it does

SoulShield is a **trauma-informed AI support companion** that helps survivors navigate emotions between therapy sessions. It operates in three modes:

1. **Grounding Mode** — Box breathing, 5-4-3-2-1 sensory exercises when overwhelmed
2. **Emotion Exploration** — Helps name feelings without giving advice
3. **Session Preparation** — Organizes thoughts for the next therapy appointment

**Key innovation: Bystander-Safe Mode** — When users indicate someone might be monitoring them ("He checks my phone"), SoulShield automatically uses neutral wellness language that won't raise suspicion. It looks like a generic mindfulness app.

Additional features:
- Voice input/output for users who can't safely type
- Dark mode for nighttime use
- 24/7 availability
- Crisis resources (hotlines)
- Enterprise-grade security with client-side encryption

---

## How we built it

**Multi-Agent AI Pipeline:**

| Agent | Purpose |
| ----- | ------- |
| Routing Agent | Classifies message by mode, privacy context, and risk level |
| Support Coach | Generates trauma-informed responses using user's words |
| Safety Fallback | Catches errors with calming, generic responses |

**Tech Stack:**
- **Frontend**: Vanilla JS on Vercel with Web Speech API for voice
- **Backend**: AWS Lambda + API Gateway + DynamoDB
- **AI**: OpenAI GPT-4 with prompts managed in LangSmith
- **Security**: 5 layers including AES-256 client-side encryption

**Prompt Engineering:** We iterated dozens of times. The breakthrough came when we stopped asking AI to "be a therapist" and instead asked it to "be a calm presence that helps someone breathe."

---

## Challenges we ran into

1. **"Robotic Therapist" Problem** — Early responses felt scripted and unnatural.
   - *Solution*: Removed prescriptive rules, added instructions to mirror the user's words naturally.

2. **Bystander Detection** — Users don't say "someone is watching." They say "he checks my phone."
   - *Solution*: Created evaluation dataset with 40+ edge cases to train subtle signal detection.

3. **Security for Vulnerable Users** — Standard security isn't enough when a breach could be life-threatening.
   - *Solution*: Implemented 5 layers including zero-knowledge encryption (we can't read messages).

4. **Mobile Experience** — Survivors use phones in difficult conditions.
   - *Solution*: Complete mobile-responsive redesign with voice input for when typing isn't safe.

5. **Validation Without Users** — We're technologists, not trauma experts.
   - *Solution*: Multiple stakeholder meetings with clinical staff who confirmed this addresses a real need.

---

## Accomplishments that we're proud of

- **100% Bystander Safety**: Zero instances of dangerous language when privacy is compromised
- **Stakeholder Validation**: A survivor support organization confirmed this addresses a real, unmet need
- **Production Deployment**: Live at [soulshield.vercel.app](https://soulshield.vercel.app) — not just a prototype
- **Enterprise Security**: 5-layer protection including client-side encryption and auto-delete
- **Multi-Agent Architecture**: Three specialized AI agents working in sequence for reliability
- **Voice Support**: Full speech-to-text and text-to-speech for users who can't safely type
- **Prompt Engineering Breakthrough**: Responses that feel human, not robotic

---

## What we learned

**From Trauma Experts:**
- Grounding techniques are the first line of defense against panic
- AI should *supplement, never replace* the therapeutic relationship
- Sometimes just having a calm presence at 3 AM is enough

**From Building:**
- Multi-agent architectures allow specialization and fault tolerance
- Prompt engineering is an art — subtle wording changes transform "robotic" into "therapeutic"
- LangSmith transforms development with version-controlled prompts and evaluation datasets

**From Testing:**
- Bystander-safe language passes the "over-the-shoulder" test
- Voice input is crucial for some users
- Dark mode isn't aesthetic — it's safety at night

---

## What's next for SoulShield App

**Q1 2025:**
- Guided grounding exercises with visual timers
- Offline mode (works without internet)
- Feelings wheel integration

**Q2 2025:**
- Therapist dashboard (with user consent)
- Pattern recognition for therapy preparation
- Multi-language support

**Future:**
- Clinical validation research partnerships
- HIPAA compliance certification
- White-label version for organizations

---

> *We didn't build an app. We built a bridge — connecting survivors to their own resilience during the 167 hours between therapy sessions. Support that hides in plain sight.*

