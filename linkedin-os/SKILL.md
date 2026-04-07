---
name: linkedin-os
description: "Automated LinkedIn networking system with two campaign types: (1) Job Search — 25 personalized connection requests/week, follow-up day 3/7/14, referral requests after context. (2) VC Networking — build relationships with investors over weeks, share traction/insights, eventually request intro meetings. Uses Claude in Chrome. Invoke with /linkedin-os or args like 'setup', 'daily', 'connect', 'followup', 'referral', 'status', 'vc-connect', 'vc-followup', 'vc-status'."
---

# LinkedIn Networking OS

Automated LinkedIn networking system with two campaign tracks. Uses Claude in Chrome to control LinkedIn directly.

**Two campaign types:**
1. **Job Search** — Build referral paths BEFORE submitting applications. 25 personalized connection requests per week, follow-up on day 3/7/14, ask for referral only after building context.
2. **VC Networking** — Build genuine relationships with investors over weeks/months. Share insights and traction, engage with their content, eventually request an intro meeting when the time is right. No rushing — VCs smell desperation instantly.

## Data Files

- **Config:** `~/.claude/linkedin-os/config.json` — target companies, roles, user background
- **Connections DB:** `~/.claude/linkedin-os/connections.json` — tracks all connections and follow-up state
- **Message Log:** `~/.claude/linkedin-os/message-log.json` — history of all sent messages
- **Pending Messages:** `~/.claude/linkedin-os/pending-messages.md` — drafted messages awaiting user approval
- **Session Notes:** `~/.claude/linkedin-os/session-notes.md` — learnings, mistakes, voice notes, and constraints discovered during each session. **Read this at the start of every session** to avoid repeating past mistakes.
- **GitHub Notepad:** `github.com/SolshineCode/linkedin-os-notepad` (private) — persistent record of all contacts, messages, engagements, and session logs. Local clone at `~/linkedin-os-notepad/`.

All paths use `~/.claude/linkedin-os/`. Create the directory and files if they don't exist.

## Logging to GitHub Notepad (Mandatory)

**Every action taken in this skill MUST be logged to the `linkedin-os-notepad` repo.** After each session, commit and push all changes.

### What to log:
- **Connection requests:** Add/update `contacts/[company]-[name].md` with the note sent and date
- **Messages:** Add to `messages/YYYY-MM-DD.md` with full text, recipient, and timestamp
- **Comments on posts:** Add to `engagements/YYYY-MM-DD.md` with post topic, comment text, and person
- **Likes:** Add to `engagements/YYYY-MM-DD.md` with person and post topic
- **Session summary:** Add to `sessions/YYYY-MM-DD.md` with actions table and lessons learned
- **Contact updates:** Update the contact's file in `contacts/` when status changes (accepted, replied, etc.)

### When to commit:
At the end of every session, or after every 5+ actions, run:
```bash
cd ~/linkedin-os-notepad && git add -A && git commit -m "Session YYYY-MM-DD: [brief summary]" && git push
```

### Skill snapshots:
Periodically (weekly or after major skill edits), copy the current SKILL.md to the repo as `skill-snapshot-YYYY-MM-DD.md` for portability across machines.

## ARGUMENTS Routing

Parse ARGUMENTS to determine which phase to run:

| Argument | Action |
|----------|--------|
| `setup` | Run first-time setup (create config interactively) |
| `daily` or no args | Run the full daily routine (all phases) |
| `connect` | Phase 3 only — send new connection requests |
| `followup` | Phase 2 only — send scheduled follow-ups |
| `referral` | Phase 4 only — send referral requests to mature connections |
| `status` | Show pipeline dashboard (counts by stage, upcoming follow-ups) |
| `add-company <name>` | Add a company to target list |
| `remove-company <name>` | Remove a company from target list |
| `vc-setup` | Configure VC networking campaign (firms, thesis areas, your startup context) |
| `vc-daily` | Run VC networking daily routine |
| `vc-connect` | Send new VC connection requests only |
| `vc-followup` | Send VC follow-up messages only |
| `vc-engage` | Engage with VC content (like/comment on their posts) |
| `vc-ask` | Send intro meeting requests to mature VC relationships |
| `vc-status` | Show VC pipeline dashboard |
| `add-firm <name>` | Add a VC firm to target list |
| `remove-firm <name>` | Remove a VC firm from target list |

## Phase 0: Load State

1. Read `~/.claude/linkedin-os/config.json`. If it doesn't exist, run Setup.
2. Read `~/.claude/linkedin-os/connections.json`. If it doesn't exist, create empty: `{"connections": []}`.
3. Read `~/.claude/linkedin-os/message-log.json`. If it doesn't exist, create empty: `{"messages": []}`.
4. Calculate today's date and determine what actions are needed.

### Config Schema

```json
{
  "user": {
    "name": "Your Name",
    "headline": "Your current role/headline",
    "background": "2-3 sentence summary of your experience and what you bring",
    "target_role": "The type of role you're seeking (e.g., Senior Product Manager)",
    "key_skills": ["skill1", "skill2", "skill3"],
    "unique_angles": ["What makes you distinctive — specific achievements, rare combos of experience"]
  },
  "targets": {
    "companies": [
      {
        "name": "Company Name",
        "why": "Why you want to work here (specific product/mission reason)",
        "product_knowledge": "What you know about their product that most candidates don't",
        "team_preference": "Specific team or area if any"
      }
    ],
    "roles_to_search": ["Product Manager", "Senior PM", "Group PM"],
    "people_titles_to_connect": ["Product Manager", "Senior Product Manager", "Engineering Manager", "Recruiter", "Hiring Manager", "Director of Product"]
  },
  "vc_campaign": {
    "startup": {
      "name": "Your Startup Name",
      "one_liner": "One sentence: what you do, for whom, why now",
      "stage": "pre-seed | seed | series-a",
      "traction": "Key metrics — users, revenue, growth rate, notable customers",
      "sector": "AI/ML, Fintech, SaaS, etc.",
      "fundraise_status": "not yet | exploring | actively raising | closed round",
      "fundraise_target": "$X at $Y valuation (leave blank if not raising yet)",
      "unique_insight": "The non-obvious insight your company is built on — this is what VCs remember"
    },
    "target_firms": [
      {
        "name": "VC Firm Name",
        "why": "Why this firm specifically (thesis alignment, portfolio synergy, partner expertise)",
        "thesis_match": "Which part of their investment thesis your startup fits",
        "portfolio_companies": ["Relevant portfolio co's you've researched"],
        "target_partners": ["Specific partner names to prioritize, if known"]
      }
    ],
    "people_titles_to_connect": ["Partner", "General Partner", "Principal", "Vice President", "Investor", "Venture Partner", "EIR", "Scout"],
    "settings": {
      "connections_per_day": 3,
      "connections_per_week_max": 15,
      "followup_days": [5, 14, 30],
      "content_engagements_per_day": 5,
      "min_touchpoints_before_ask": 4,
      "min_days_before_ask": 30
    }
  },
  "settings": {
    "connections_per_day": 5,
    "connections_per_week_max": 25,
    "followup_days": [3, 7, 14],
    "min_context_messages_before_referral": 2,
    "daily_time_limit_minutes": 20
  }
}
```

### Connection Record Schema

```json
{
  "id": "unique-id (linkedin-url-slug)",
  "name": "Person's Name",
  "title": "Their Title",
  "company": "Their Company",
  "linkedin_url": "https://linkedin.com/in/slug",
  "status": "pending_request | connected | followup_1 | followup_2 | followup_3 | referral_asked | referral_received | dormant",
  "connection_request_sent": "2026-04-01",
  "connection_accepted": null,
  "messages_sent": [
    {"date": "2026-04-01", "type": "connection_request", "summary": "Brief summary"}
  ],
  "next_action": "followup_1",
  "next_action_date": "2026-04-04",
  "notes": "Any relevant context about this person",
  "target_company": "Which target company this relates to",
  "campaign": "job-search | vc"
}
```

### VC Connection Record (additional/overridden fields)

```json
{
  "campaign": "vc",
  "firm": "VC Firm Name",
  "role_at_firm": "Partner | Principal | etc.",
  "investment_focus": "What sectors/stages they focus on",
  "status": "pending_request | connected | warming | engaged | relationship_built | intro_asked | meeting_scheduled | dormant",
  "content_engagements": [
    {"date": "2026-04-01", "type": "like | comment", "post_topic": "Brief description", "comment_text": "What you commented if applicable"}
  ],
  "touchpoints": 0,
  "next_action": "engage_content | followup_1 | followup_2 | followup_3 | intro_ask",
  "next_action_date": "2026-04-06"
}
```

## Phase 1: Setup (if `setup` or `vc-setup` argument or no config exists)

**IMPORTANT: Ask the user for their information. Do NOT make up details.**

### Job Search Setup (`setup`)
1. Ask the user to provide:
   - Their name and current headline
   - A 2-3 sentence background summary
   - Their target role
   - Key skills (comma-separated)
   - What makes them distinctive
2. Ask for target companies (can add more later with `add-company`):
   - For each company: name, why they want to work there, what they know about the product
3. Ask for role titles to search for and people titles to connect with
4. Show the complete config and ask for confirmation
5. Write to `~/.claude/linkedin-os/config.json`

After setup, offer to run the first daily routine.

### VC Campaign Setup (`vc-setup`)
1. Ask the user to provide their startup info:
   - Startup name and one-liner
   - Stage (pre-seed, seed, series A)
   - Key traction metrics (users, revenue, growth)
   - Sector
   - Fundraise status and target (if applicable)
   - The non-obvious insight the company is built on
2. Ask for target VC firms (can add more later with `add-firm`):
   - For each firm: name, why this firm, thesis alignment, relevant portfolio companies, specific partners to target
3. Confirm people titles to connect with (defaults: Partner, GP, Principal, VP, Investor, Venture Partner, EIR, Scout)
4. Show the complete VC config and ask for confirmation
5. Merge into `~/.claude/linkedin-os/config.json`

After setup, offer to run the first VC daily routine.

## Phase 1.5: Mine Existing Connections (Warm Pipeline)

**Before sending cold connection requests, always check for existing 1st-degree connections at target companies.** These are people who already know you — they're 10x more likely to respond and help than cold contacts.

This phase runs during initial setup AND periodically (weekly) during the daily routine.

### When to Run
- **First time:** During setup or first daily run, scan ALL target companies for 1st-degree connections
- **Weekly refresh:** Every Monday, re-scan to catch people who changed jobs to target companies
- **After adding a new target company:** Immediately scan for existing connections there

### How It Works

1. For each target company, use Comet to search: `https://www.linkedin.com/search/results/people/?keywords=[COMPANY]&network=%5B%22F%22%5D&origin=FACETED_SEARCH`
2. Record every 1st-degree connection found with their name, title, and URL
3. Add them to `connections.json` with status `connected` and `connection_accepted: "existing"`
4. Set `next_action: "followup_1"` with `next_action_date` of tomorrow (start engaging immediately)
5. Skip anyone already in the DB

### Prioritizing Existing Connections

Existing connections get **priority over cold outreach** in the daily routine. Engagement order:

**Job Search campaign:**
1. Recruiters/talent at target company → they're literally the hiring pipeline
2. People in your target team/role → can refer you directly
3. Anyone at the company → can introduce you to the right people
4. People who recently joined → they remember the hiring process and are eager to help

**VC campaign:**
1. VCs/investors you're already connected with at target firms → skip straight to relationship deepening
2. Portfolio company founders you know → can make warm intros to partners
3. Other connections at the firm (ops, analysts) → can provide intel on who's actively looking at your space

### Messaging Existing Connections

Messages to existing connections are DIFFERENT from cold follow-ups. You already have a relationship — acknowledge that:

- **Don't pretend you just met.** "Hey [Name], it's been a while! I saw you're at [Company] now — congrats."
- **Be direct about why you're reaching out** (after the warm opener). These people expect honesty.
- **Reference the shared history** if you have it — how you met, mutual connections, shared interests.
- **Still provide value first** in the first message — but the timeline to an ask is shorter (1-2 exchanges, not 3).

### For Both Campaigns

This phase applies identically to both job search and VC networking. The only difference is the prioritization criteria above. Add a `"source": "existing_connection"` field to the connection record so the follow-up phases can adjust their messaging tone accordingly.

## Phase 2: Follow-ups (runs first in daily routine)

Follow-ups take priority because they're time-sensitive and build on existing momentum.

1. Query `connections.json` for connections where `next_action_date <= today`
2. For each due follow-up, sorted by priority (older first):

### Follow-up Day 3 (First Touch)
- Open their LinkedIn profile in Chrome
- Read their recent activity (posts, comments, job changes)
- Craft a message that references something SPECIFIC from their profile/activity
- The message should provide value — share a relevant article, insight, or congratulation
- **DO NOT ask for anything.** This is pure context-building.
- Template direction: "Hey [Name], I noticed [specific thing from their activity]. [Relevant value-add or genuine comment]. [Optional: brief connection to shared interest]."
- Send the message via LinkedIn messaging
- Update connection record: status → `followup_1`, log message, set next_action_date to +4 days

### Follow-up Day 7 (Deepen)
- Open their profile, check for any new activity since last message
- Craft a message that deepens the relationship — ask a thoughtful question about their work, share a relevant resource, or comment on something they posted
- Still NO ask. Building genuine rapport.
- Template direction: "I've been thinking about [topic from previous exchange or their work]. [Thoughtful question or insight]. [Brief mention of your relevant experience if natural]."
- Send via LinkedIn
- Update record: status → `followup_2`, log message, set next_action_date to +7 days

### Follow-up Day 14 (Bridge to Referral)
- This is the transition message. Still not a hard ask, but signals your interest.
- Mention you're exploring opportunities and that their company caught your eye for [specific reason]
- Ask if they'd be open to a quick chat about what it's like working there
- Template direction: "Really enjoyed connecting with you. I've been looking at [Company] — [specific product/mission reason]. Would you be open to a 15-min chat about your experience there? No pressure at all."
- Send via LinkedIn
- Update record: status → `followup_3`, log message, set next_action → `referral_ask`, next_action_date to +3 days

### Sending Messages

**Preferred (Comet):** Draft the message, show user for approval, then use `comet_ask` to navigate to LinkedIn messaging, type the approved message, and send. Use `comet_screenshot` to confirm.

**Fallback (Chrome):** Navigate to `https://www.linkedin.com/messaging/thread/new/`, find the compose area, type the message, show user for approval, then click Send and screenshot to confirm.

**CRITICAL: ALWAYS show the user each message and get explicit approval before sending — regardless of whether using Comet or Chrome. Never auto-send messages.**

## Phase 3: New Connection Requests

Goal: ~5 per day, ~25 per week. Rotate across target companies evenly.

1. Check how many requests sent this week (Mon-Sun). If >= 25, skip.
2. Determine which target company to focus on (round-robin based on least-recent activity)
3. For each target company needing connections:

### Finding People to Connect With

1. Navigate to LinkedIn Search: `https://www.linkedin.com/search/results/people/`
2. Use filters:
   - Current company: [target company name]
   - Title keywords from `people_titles_to_connect`
3. Read the search results page
4. For each result, check against `connections.json` to avoid duplicates
5. For promising candidates:
   - Click into their profile
   - Read their headline, about section, experience, recent activity
   - Determine personalization angle

### Crafting Connection Requests

Every connection request MUST be personalized. Generic requests get ignored.

**Personalization hierarchy (use the most specific you can find):**
1. Something they posted or commented on recently
2. A shared background element (school, previous company, interest)
3. Their specific work/project that you find genuinely interesting
4. A thoughtful observation about their team/company's product

**Connection note structure (300 char limit on LinkedIn):**
- Line 1: Why you're reaching out (specific to THEM, not you)
- Line 2: Brief context about you (1 sentence max)
- Line 3: Low-pressure close

**Example directions (adapt, don't copy):**
- "Your post about [topic] resonated — I had a similar experience at [company]. Would love to connect and learn more about your work at [company]."
- "I've been following [Company]'s work on [specific product/feature]. As someone working in [your area], I'd love to connect."
- "Noticed we both came from [shared background]. I'm exploring PM roles and your path to [their role] is really interesting."

**CRITICAL: Show the user each connection request note and get approval before sending.**

### Sending Connection Requests

**Preferred (Comet):** After user approves the note, use `comet_ask` to navigate to the profile, click Connect, add the approved note, and send. Use `comet_screenshot` to confirm.

**Fallback (Chrome):** On the person's profile, click Connect, click "Add a note", type the approved note, click Send, screenshot to confirm.

**In both cases:** Show user the note FIRST. Wait for approval. Only then send. Update `connections.json` with the new record.

## Phase 4: Referral Requests

For connections that have completed the follow-up sequence (status is `referral_ask` ready):

1. Only proceed if at least 2 messages have been exchanged AND it's been 14+ days since connection
2. Check if there's an open role at their company that matches your target
3. Craft the referral ask:
   - Reference your previous conversations
   - Mention the specific role you're interested in
   - Make it easy for them: offer to send your resume, a brief blurb they can forward, etc.
   - Be gracious — "totally understand if you're not comfortable" language
4. **Show user the message. Wait for approval.**
5. Send and update record

**Template direction:** "Thanks for the great conversation about [topic]. I saw [Company] has an opening for [Role] on the [Team] team — it's really aligned with my background in [specific]. Would you be comfortable referring me? Happy to send over my resume and a short blurb you can forward. Completely understand if it's not the right fit."

---

# VC NETWORKING CAMPAIGN

The VC campaign is fundamentally different from job search networking. Key differences:
- **Longer timeline.** VCs build relationships over months, not weeks. The follow-up cadence is day 5 / 14 / 30, not 3 / 7 / 14.
- **Content engagement comes first.** Before you ever DM a VC, you should have liked/commented on 3-5 of their posts. They notice who engages consistently.
- **You're positioning as a founder, not a candidate.** Every interaction should signal that you're building something worth paying attention to.
- **The ask is a conversation, not a referral.** You're asking for 20 minutes to share what you're building and get their perspective — not asking them to vouch for you.
- **Never pitch in a DM.** The goal of messages is to get to a call. The pitch happens on the call.
- **Fewer connections, higher quality.** 3/day max, 15/week. You want every VC connection to be someone you've actually researched.

## VC Phase 1: Content Engagement (`vc-engage`)

This is the warm-up before connecting. Do this daily, even before sending connection requests.

1. For each target firm, find partners/investors who post actively on LinkedIn
2. Navigate to their profile → Activity → Posts
3. For each recent post (last 7 days):
   - Read the full post
   - If genuinely relevant to your space, **like** it
   - For 1-2 posts per session, write a **thoughtful comment** (not "Great post!"):
     - Add a specific data point, contrarian take, or founder perspective
     - Reference something from your own experience building in the space
     - Keep it to 2-3 sentences — substantive but concise
     - **Show user the comment and get approval before posting**
4. Log each engagement in the connection record's `content_engagements` array
5. After 3-5 engagements with a person over 1-2 weeks, they're warm enough for a connection request

### Comment Quality Rules for VC Posts
- **Add signal, not noise.** "Agree!" is worthless. A data point from your own company is gold.
- **Be the founder in the room.** Comments like "We're seeing exactly this with our users — [specific insight]" position you as someone building, not lurking.
- **Disagree respectfully when genuine.** VCs respect founders who think independently. "Interesting framing — though from the builder side, I'd push back on X because [reason]" is memorable.
- **Never pitch in comments.** No "We're solving this at [Startup]!" — it's transparent and annoying.
- **Reference their thesis.** If a VC posts about a trend that aligns with your startup, your comment should connect to their thesis without being salesy.

### Engaging via Browser

**Preferred (Comet):** Use `comet_ask` to navigate to their profile, find recent posts, like them, and post approved comments. Use `comet_screenshot` to confirm.

**Fallback (Chrome):** Navigate to their profile, click Activity, find posts, like/comment directly.

**In both cases:** Show user the comment text FIRST. Wait for approval. Only then post it.

## VC Phase 2: Connection Requests (`vc-connect`)

Only connect with VCs you've already engaged with (liked/commented on posts) OR who have a very clear thesis match.

1. Check weekly quota (sent X/15 this week). If >= 15, skip.
2. Round-robin across target firms
3. For each target VC:

### Finding VCs to Connect With

1. Search LinkedIn for people at the target firm with investor titles
2. Prioritize:
   - Partners who post about your sector
   - People you've already engaged with via comments
   - VCs whose portfolio includes companies in adjacent spaces
   - Scouts and EIRs (often more accessible than GPs)
3. Check their recent posts/activity for personalization hooks

### Crafting VC Connection Notes

**The 300-character connection note for a VC must be completely different from a job search note.**

**What works:**
- Reference a specific post or thesis of theirs
- Mention a shared portfolio company connection or sector overlap
- Position yourself as a founder building in their area of interest
- Be direct about why you'd find their perspective valuable

**What kills your chances:**
- "I'm raising and would love to pitch you" — instant ignore
- Generic flattery — "I admire your work" without specifics
- Long-winded notes — you have 300 chars, use them surgically
- Mentioning fundraising at all in the connection request

**Template directions (adapt, never copy):**
- "Your take on [specific post topic] mirrored what we're seeing building [product type]. Would love to connect — always looking for sharp perspectives on [sector]."
- "Noticed [Portfolio Co] in your portfolio — we're building in an adjacent space ([one-liner]). Your thesis on [area] resonated. Would love to connect."
- "Fellow [sector] nerd here — building [brief what]. Your post about [topic] shifted how I think about [aspect]. Would love to stay in touch."

**CRITICAL: Show user each note. Wait for approval.**

## VC Phase 3: Follow-ups (`vc-followup`)

**SLOWER cadence than job search.** VCs are busy, and pushing too fast signals desperation.

### Follow-up Day 5 (Value Drop)
- Open their profile, read recent activity
- Send a message that provides genuine value — NO ask:
  - Share a relevant industry data point, report, or article
  - Comment on something they posted since you connected
  - Share a non-obvious insight from your space as a founder
- Template direction: "Hey [Name], saw [specific thing]. Thought you'd find this interesting — [relevant insight or resource]. Building in [space] gives a unique vantage point on this."
- Update record: status → `warming`, log message, next_action_date to +9 days

### Follow-up Day 14 (Deepen with Founder Signal)
- Share something that demonstrates traction or insight without being pitch-y:
  - A learning from your startup that relates to their investment thesis
  - A question about a trend you're both watching, asked from the builder's perspective
  - A reaction to something in their portfolio ("Saw [PortCo] launched X — smart move, we're seeing similar demand from [angle]")
- Template direction: "Been thinking about [topic related to their thesis]. From the building side, [specific insight or data from your experience]. Curious how you're thinking about [related question]?"
- Update record: status → `engaged`, log message, next_action_date to +16 days

### Follow-up Day 30 (Bridge to Meeting)
- By now you've had 2+ exchanges and multiple content engagements
- This is the transition — still not a pitch, but an invitation:
  - Reference the relationship you've built
  - Mention you're building something in their area and would value their perspective
  - Ask for a 20-minute conversation — framed as seeking advice, not pitching
  - Make it easy to say yes (suggest specific times, offer to come to them)
- Template direction: "Really enjoyed exchanging thoughts on [topic]. I'm building [one-liner] and your perspective on [their expertise area] would be incredibly valuable. Would you be open to a 20-min call? Happy to work around your schedule. No deck, just a conversation."
- Update record: status → `relationship_built`, log message, next_action → `intro_ask`, next_action_date to +5 days

**CRITICAL: Show user each message. Wait for approval.**

## VC Phase 4: Intro Meeting Request (`vc-ask`)

For VCs with status `relationship_built` and 4+ touchpoints over 30+ days:

1. This is the formal ask for a meeting — still framed as a conversation, not a pitch
2. Reference your previous exchanges specifically
3. Briefly mention what you're building and why their perspective matters
4. If you're actively raising, you can mention it here — but frame it as context, not the purpose
5. Suggest a specific format (20-min call, coffee, office visit)
6. Make it trivially easy to accept

**Template direction:** "Hey [Name], thanks for the great conversations about [topic]. Quick context — we're building [one-liner], currently at [traction metric]. Given your depth in [their area], I think you'd have sharp takes on [specific question]. Would you be open to 20 minutes next week? I can share a brief overview beforehand if helpful."

**If they agree:** Update status → `meeting_scheduled`. Offer to help prep a one-pager or brief deck (separate from this skill — just note it).

**If no response after 7 days:** One gentle bump. "Hey [Name], just bumping this in case it got buried. Totally understand if timing doesn't work — happy to reconnect down the road."

**If they decline:** Update status → `dormant`. Set next_action_date to +90 days for a re-engagement check. No hard feelings — you've built a relationship that may pay off later.

## VC Phase 5: Status Dashboard (`vc-status`)

```
=== LinkedIn VC Networking — Pipeline Dashboard ===
Date: [today]

Pipeline Summary:
  Pending requests:       [count] (awaiting acceptance)
  Warming:                [count] (connected, early engagement)
  Engaged:                [count] (2+ exchanges, building rapport)
  Relationship built:     [count] (ready for intro ask)
  Intro asked:            [count] (meeting requested)
  Meetings scheduled:     [count]
  Dormant:                [count] (parked for re-engagement)

This Week:
  Connection requests sent: [X] / 15
  Content engagements:      [X] (likes + comments)
  Follow-ups sent:          [X]
  Intro asks sent:          [X]

Today's Queue:
  Content to engage with: [list VCs with recent posts]
  Follow-ups due:         [list names + firms]
  Intros ready to ask:    [list names + firms]

Firm Distribution:
  [Firm A]: [X] connections ([Y] warming, [Z] engaged)
  [Firm B]: [X] connections ([Y] warming, [Z] engaged)
  ...

Engagement Quality:
  Total comments made: [count]
  Total likes given:   [count]
  Avg touchpoints before intro ask: [number]
```

## VC Daily Routine Flow (`vc-daily`)

Run phases in this order:
1. Load state
2. Show VC status dashboard
3. Mine existing VC connections if first run or Monday (Phase 1.5 — check target firms for 1st-degree connections)
4. Content engagement — like/comment on VC posts (VC Phase 1)
5. Follow-ups due today — existing connections first (VC Phase 3)
6. New connection requests if quota allows (VC Phase 2)
7. Intro requests if any are ready (VC Phase 4)
8. Save all state
9. Show updated dashboard

---

## Phase 5: Status Dashboard

When `status` argument is used, display:

```
=== LinkedIn Networking OS — Daily Dashboard ===
Date: [today]

Pipeline Summary:
  Pending requests:     [count] (awaiting acceptance)
  Connected:            [count] (accepted, pre-followup)
  In follow-up sequence: [count]
  Ready for referral:   [count]
  Referrals asked:      [count]
  Referrals received:   [count]

This Week:
  Connection requests sent: [X] / 25
  Follow-ups sent:          [X]
  Referral asks sent:       [X]

Today's Queue:
  Follow-ups due:  [list names + companies]
  Slots for new connections: [remaining today]

Company Distribution:
  [Company A]: [X] connections ([Y] in pipeline)
  [Company B]: [X] connections ([Y] in pipeline)
  ...
```

## Daily Routine Flow (default / `daily`)

Run phases in this order:
1. Load state (Phase 0)
2. Show status dashboard
3. Mine existing connections if first run or Monday (Phase 1.5)
4. Follow-ups due today — existing connections first, then new ones (Phase 2)
5. New connection requests (Phase 3)
6. Referral requests if any are ready (Phase 4)
7. Save all state
8. Show updated dashboard

## Browser Strategy: Comet First, Chrome Fallback

**Comet (`comet-bridge` MCP) is the PREFERRED browser for all LinkedIn operations.** Comet is an autonomous agentic browser — treat it as a capable assistant that handles browsing independently. Do NOT micromanage it.

### Why Comet First
- Every Chrome screenshot/read_page dumps thousands of tokens into Claude's context
- Comet handles browsing autonomously and returns only the relevant results
- A full daily routine via Chrome can burn 50-100K tokens on page content alone
- Comet keeps Claude's context clean for decision-making and message crafting

### How to Work with Comet: Trust & Autonomy

**Comet is an agentic browser, not a dumb automation tool.** It understands natural language instructions, navigates complex UIs, handles pagination, and compiles results. The key principles:

1. **Give big tasks, not micro-steps.** Don't tell Comet to "click the search box, type X, press enter, read the results." Just say "Search LinkedIn for [X] and give me the results." Comet figures out the UI.

2. **Use long timeouts.** Comet navigates real web pages. Use 60-300 seconds for multi-page tasks. Never use 15-second timeouts.

3. **Don't over-poll.** Wait at least 60 seconds before the first `comet_poll`. Only poll to check if a long task (2+ min) is still progressing.

4. **Batch work into single requests.** Instead of "search company A" then "search company B," say "search companies A, B, C, D and compile all results." Comet handles multi-step workflows natively.

5. **Trust the output.** When Comet returns results, use them. Don't re-verify with Chrome.

6. **Use `newChat: true` for fresh tasks.** If Comet seems confused or stuck from a previous task, start a new chat.

7. **Let it research broadly.** Comet excels at cross-platform research. It can check LinkedIn, X/Twitter, personal blogs, and company pages in a single task.

8. **Delegate screening and analysis, not just navigation.** Comet can do much more than browse. Give it the full context of what you're trying to accomplish and let it make recommendations. For example, instead of "find their posts," say "find their posts, tell me which ones are relevant to my sectors (AI PropTech and biotech diagnostics), check for personal interests like Grateful Dead references, and recommend which 2-3 I should engage with first." Comet handles the analysis, Claude just reviews the recommendations.

9. **One comprehensive prompt beats five small ones.** Combine the connection scan, content research, and partner analysis into a single detailed prompt. Comet keeps context across the whole task. Multiple small prompts lose context, waste time reconnecting, and risk input failures.

10. **If Comet crashes or input fails, restart fully.** Kill all Comet processes, relaunch with `--remote-debugging-port=9222`, reconnect with `comet_connect`, and start a `newChat`. Don't try to recover a broken session.

11. **Comet CAN click Send/Submit/Post, but needs explicit authorization in the prompt.** Include "click Send/Post/Submit immediately, this is authorized" in your original prompt. Comet will ask for confirmation if you don't include this upfront. It may take a second `comet_ask` saying "Yes, confirmed. Post it now." Don't assume it failed just because it asked for confirmation. Check the actual LinkedIn page to verify.

12. **Don't assume Comet failed. Verify first.** Comet sometimes appears stuck in its UI (showing "Listening..." or asking for confirmation) but has actually completed the action on the LinkedIn page. Always check the actual page state before concluding something didn't work.

### Comet for LinkedIn Operations

**All LinkedIn navigation and actions should go through Comet when available:**

**Searching for people (batch):**
```
comet_ask (timeout: 120000): "Go to LinkedIn and search for my 1st-degree connections at these companies: [Company A], [Company B], [Company C]. For each company, use this URL pattern: https://www.linkedin.com/search/results/people/?keywords=COMPANY&network=%5B%22F%22%5D&origin=FACETED_SEARCH — scroll through all pages. Give me a final list of every person grouped by company with their name and title."
```

**Reading a profile + research:**
```
comet_ask (timeout: 60000): "Research [Person Name] who is [Title] at [Company]. Check their LinkedIn profile, recent posts, and X/Twitter if they have one. Tell me: their headline, about section, recent posts (last 3), any shared connections, anything I could reference in a personalized message, and any signals of personal interests (especially Grateful Dead / Dead & Company / jam band culture, Sphere concert references, tie-dye imagery)."
```

**Sending a connection request (with user-approved note):**
```
comet_ask: "Go to this LinkedIn profile: [URL]. Click the Connect button. If it asks to add a note, click 'Add a note' and type exactly this message: [APPROVED_MESSAGE]. Then click Send."
```

**Sending a message:**
```
comet_ask: "Go to LinkedIn messaging. Start a new message to [Person Name]. Type exactly this message: [APPROVED_MESSAGE]. Then click Send."
```

**Engaging with posts (batch):**
```
comet_ask (timeout: 120000): "Go to these LinkedIn profiles and like their most recent post: [URL1], [URL2], [URL3]. For [URL2], also leave this comment on their post about [topic]: [APPROVED_COMMENT]."
```

**Checking connection acceptances:**
```
comet_ask: "Go to LinkedIn notifications or My Network page. Check for any new connection acceptances in the last 24 hours. List the names and companies of anyone who accepted."
```

**Mining existing connections at target companies:**
```
comet_ask (timeout: 180000): "Search LinkedIn for my 1st-degree connections at each of these companies: [list]. For each company, use the 1st-degree filter. Go through ALL result pages. Give me a complete list grouped by company: Name | Title | LinkedIn URL."
```

### Comet Workflow in Daily Routine

1. At the start of the daily routine, send Comet a **single big research task** — "scan my connections at target companies, check for new acceptances, and research today's follow-up targets"
2. While Comet works (2-5 minutes), Claude loads config, calculates the dashboard, and plans today's actions
3. When Comet returns, use the research to craft personalized messages
4. Show messages to user for approval
5. Send approved messages via `comet_ask` (these are quick, one-shot tasks)
6. Use `comet_screenshot` only if you need to verify something specific went wrong

### CRITICAL: Message Approval Flow with Comet

Even though Comet handles the browsing, the **message approval flow stays with the user:**
1. Comet researches the person → returns findings to Claude
2. Claude drafts the message → shows user for approval
3. User approves (or edits) → Claude sends the approved text via `comet_ask`
4. Comet types and sends the message
5. Claude updates the DB

**NEVER pass an unapproved message to Comet for sending.**

### Fallback: Claude in Chrome

If Comet is not available (won't connect), fall back to Claude in Chrome:

#### Starting a Chrome LinkedIn Session
1. Call `tabs_context_mcp` to get current tabs
2. Create a new tab with `tabs_create_mcp`
3. Navigate to `https://www.linkedin.com/feed/`
4. Check if logged in — look for the feed content or a sign-in prompt
5. If not logged in: **Tell the user they need to log in manually.** Do NOT enter credentials.
6. Once logged in, proceed with the routine

#### LinkedIn-Specific Navigation (Chrome)
- Profile: `https://www.linkedin.com/in/[slug]/`
- Search people: `https://www.linkedin.com/search/results/people/?keywords=[query]`
- Search with company filter: add `&currentCompany=["companyId"]` (find company ID from search)
- Messaging: `https://www.linkedin.com/messaging/`
- Jobs: `https://www.linkedin.com/jobs/search/?keywords=[query]`

#### Handling LinkedIn UI (Chrome)
- LinkedIn's UI changes frequently. Use `read_page` to understand current layout before clicking
- Look for `aria-label` attributes to find buttons reliably
- The Connect button may say "Connect", "Follow", or "Message" depending on connection status
- Connection request modals may have different flows — always read the modal before acting
- If a profile says "Pending" the request is already sent — skip and note in DB

### Rate Limiting & Safety (applies to BOTH Comet and Chrome)
- **Never send more than 5 connection requests in a single session**
- **Wait 10-30 seconds between actions** to avoid triggering LinkedIn's automation detection
- **Never auto-send messages** — always get user approval
- If you see a CAPTCHA or "unusual activity" warning, STOP immediately and alert the user
- If LinkedIn shows a "weekly invitation limit" warning, STOP and note it in the dashboard
- Space out actions naturally — read profiles, scroll, pause like a human would

## Message Quality Rules

1. **Never lie or fabricate.** Don't claim to have read their post if you haven't. Don't invent shared connections.
2. **Be specific.** "I enjoyed your post" is garbage. "Your point about X in your post about Y" is real.
3. **Provide value first.** Every message before the referral ask should give something — insight, resource, genuine congratulation.
4. **Keep it short.** LinkedIn messages should be 2-4 sentences max. Nobody reads walls of text.
5. **Sound human.** No corporate speak. No "I hope this message finds you well." Write like a real person.
6. **Match their tone.** If their posts are casual, be casual. If they're formal, match that.

## Human Writing Check (Mandatory for ALL Messages)

**Every message, connection note, and comment MUST pass a human-writing check before being shown to the user for approval.** AI-written LinkedIn messages are an instant credibility killer — researchers and VCs can smell them immediately.

After drafting any outgoing text, self-review against these AI writing tells and fix them BEFORE presenting to the user:

### BANNED words/patterns in LinkedIn messages:
- "I'd love to" → just say "Would love to" or rephrase entirely
- "I hope this message finds you well" → delete entirely
- "I came across your profile" → too generic, be specific about HOW
- "I'm reaching out because" → cut the preamble, just say the thing
- "leverage", "delve", "landscape", "tapestry", "testament" → never
- "Additionally", "Furthermore", "Moreover" → never in short messages
- "aligns with", "resonates with" → use sparingly, max once
- "insightful", "thought-provoking", "compelling" → generic flattery, cut
- "I'm passionate about" → show it, don't say it
- "synergy", "ecosystem", "paradigm" → corporate garbage
- **Em dashes (—) are a top AI writing giveaway.** Real people use commas, periods, or just start a new sentence. Em dashes scream "Claude wrote this." ZERO em dashes in LinkedIn messages. Use a comma, period, or "and" instead. Every single one.
- Starting with "I" → vary your sentence openings

### What human LinkedIn messages actually sound like:
- Slightly informal, like texting a smart colleague
- One specific detail that proves you actually read their stuff
- Short. Shorter than you think. Then cut it again.
- Imperfect grammar is fine. Fragments, contractions, casual punctuation.
- A real person might say "super cool" or "really interesting", not "profoundly insightful"
- Natural filler words occasionally ("honestly", "actually", "essentially", "btw"), but not overdone

### Caleb's voice (learned from his own edits):
- Uses "I saw" not just "saw". Includes the subject pronoun naturally.
- Uses filler words like "essentially" that ground the message as conversational
- Claims achievements directly with venue names ("I had published in AAAI last year") rather than hedging ("if you've come across that one"). Confidence, not false modesty.
- Breaks sentences with periods, not commas or em dashes. Short and declarative.
- Confident without being salesy. States what he's doing, doesn't oversell it.
- "Super cool" is natural for him. Casual praise, not formal compliments.

### Self-review process:
1. Draft the message
2. Read it back — does it sound like something you'd text to a colleague? If it sounds like a cover letter, rewrite.
3. Check for banned words/patterns above
4. **ZERO em dashes.** Replace every — with a comma, period, or "and". This is non-negotiable. Also check: varied sentence openings, contractions used.
5. If the message is for a VC or senior researcher, read it one more time — would YOU respond to this if you got 50 DMs a day?
6. Only THEN show it to the user for approval

## Personal Hooks (from config `personal_hooks`)

The config may contain `personal_hooks` — shared interests or cultural connections that create instant rapport. These are **the highest-value personalization angles** because they bypass professional small talk entirely.

**How to use personal hooks:**
1. When researching a person (via Comet or Chrome), scan their profile and posts for signals that match any `personal_hooks[].how_to_spot` patterns
2. If a match is found, **prioritize this over professional personalization** for the connection request or first message
3. Personal hooks work best when they feel natural and genuine — don't force it
4. A shared passion creates a bond that purely professional connections can't match

**When to deploy:**
- **Connection request note**: If their profile has clear signals (e.g., Grateful Dead imagery, concert photos), lead with it. "Noticed the Steal Your Face — fellow Deadhead here. Caught Dead & Co at the Sphere last year. Would love to connect."
- **Follow-up day 3**: If you connected professionally but discover the hook later, use it. "Scrolling your posts and saw [signal] — didn't realize you were into [topic] too! [Genuine comment or question]."
- **VC engagement**: Especially powerful with VCs. Shared cultural identity (Deadhead, surfer, poker player, etc.) creates a "tribe" bond that accelerates trust far faster than professional rapport alone.

**Rules:**
- Only use hooks that are **genuinely true** for the user — never fake shared interests
- Don't overuse the same hook with everyone at the same firm — it looks calculated
- If the signal is ambiguous, don't assume — ask casually rather than claiming shared membership

## Error Handling

- If Chrome tools fail 3 times, stop and tell the user
- If LinkedIn is down or unreachable, stop and report
- If a profile can't be found, mark as "not_found" in DB and move on
- If connection request fails (already connected, pending, etc.), update DB status accordingly
- Always save state after each action so progress isn't lost if the session is interrupted

## Content Posting Constraints

**DO NOT post or publish any LinkedIn content about Apex Agent, ChatFiller, STI-Detect, or any business ventures.** Caleb's day job (Misfits and Machines) has a clean IP assignment clause but office politics are messier than legal text. Avoid any public LinkedIn activity that makes side businesses visible to his employer.

**Safe to post/share publicly:**
- Published research (AAAI paper, nanochat-SAE)
- Open source HuggingFace contributions
- General mech interp / SAE / AI safety commentary
- Reactions to others' research

**Keep private (DMs and comments only, no standalone posts):**
- ChatFiller / Apex Agent (voice AI for real estate)
- STI-Detect (biotech diagnostics)
- Fundraising activity
- Cofounder/CTO role

**VC engagement is fine** because commenting on a VC's post from a "founder perspective" is low-profile. It's one comment in a thread, not a broadcast. But never create a standalone post announcing ventures or fundraising.

## Important Notes

- This skill controls a real LinkedIn account with real professional consequences
- LinkedIn has weekly connection request limits (~100-200/week depending on account age and SSI score)
- Excessive automation can get accounts restricted — the safety limits in this skill are conservative on purpose
- The 25/week target from the strategy is well within LinkedIn's limits for most accounts
- All messages MUST be approved by the user before sending
- The user can say "skip" to skip any individual action
