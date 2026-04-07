# Borrower Defense to Repayment Application Assistant

Guide users through filing a Borrower Defense to Repayment (BDTR) application on StudentAid.gov to discharge federal student loans when their school engaged in misconduct (misrepresentation, breach of contract, fraud, disability discrimination, etc.).

This skill was built from a real, successful application session. It handles the entire pipeline: evidence gathering, narrative drafting, human-writing polish, portal form filling, and strategic positioning review.

## When to Use

- User mentions student loan discharge, borrower defense, school fraud, or loan forgiveness due to school misconduct
- User describes being misled by a school about program outcomes, costs, or services
- User experienced disability discrimination, broken programs, or fraudulent retention at a college
- User mentions Sweet v. McMahon / Sweet v. Cardona settlement

## Prerequisites

- **Gemini CLI** must be installed and authenticated (`gemini --yolo` must work). This is used for Gmail evidence gathering. The user should have already run `gemini` interactively once to complete Google OAuth.
- **Claude in Chrome** browser extension for navigating StudentAid.gov portal
- **ffmpeg** for audio compression (will install via `winget install ffmpeg` if missing)
- User must have an FSA ID (Federal Student Aid account) at StudentAid.gov
- User must handle all 2FA/login steps themselves (Claude cannot enter passwords or security codes)

## Important Legal Disclaimer

Claude is not an attorney. This skill provides informational and strategic assistance, not formal legal advice. The user is filing under penalty of perjury and is responsible for the accuracy of all statements. Claude should clearly state this at the start of every session.

## Critical User Briefing (Tell the user ALL of this upfront)

Before starting ANY portal work, brief the user on what to expect. This saves enormous frustration:

### StudentAid.gov Portal Reality Check
**This portal is hostile to automation and impatient with humans.** Set expectations:

1. **You WILL be logged out multiple times.** The session timeout is roughly 15-20 minutes of inactivity. Every time Claude pauses to think, draft text, or you step away, the clock is ticking. When it times out, you'll need to log back in with your FSA ID, password, and 2FA code. Plan to log in 3-5 times during this process. It's normal and your draft is saved.

2. **Keep your email open in another tab.** The 2FA codes come by email. Having Gmail open means you can grab codes fast when the session expires.

3. **Your progress IS saved.** Every time we click "Save and Exit" or the portal auto-saves between steps, your draft is preserved. You can find it at My Activity > Borrower Defense > Draft. It will show "Last Updated" with today's date. Don't panic if you get logged out.

4. **The form rejects common characters.** No quotes, no parentheses, no dollar signs, no colons, no exclamation marks. Just letters, numbers, commas, periods, apostrophes, hyphens, slashes, ampersands, and pound signs. Claude will handle this but if you edit text yourself, keep this in mind.

5. **File uploads must be done manually.** Claude can fill all the text fields but cannot interact with the native file picker dialog. You'll upload evidence files yourself at the end - it takes about 5 minutes.

6. **Do NOT close the browser tab** while Claude is working. The portal connection is fragile.

7. **The whole process takes 1-3 hours** depending on how much evidence gathering is needed and how many times the portal logs you out. The text drafting and evidence gathering happen outside the portal (no timeout pressure). The portal form-filling is the fast part if we don't get logged out.

8. **Claude will NEVER click Submit.** The final submission includes a perjury attestation that only you can make. Claude will get everything filled and saved, then hand it back to you for review and submission.

### What the User Should Have Ready
- FSA ID username and password (for StudentAid.gov login)
- Access to their email for 2FA codes
- Any audio recordings, screenshots, or documents related to the school misconduct
- Names of key people involved (instructors, administrators, accommodation staff)
- Approximate dates of attendance and when the problems occurred
- Knowledge of their current loan balance (we can also look this up on the portal)

### Audio Evidence Is Your Secret Weapon
If you have ANY recordings of meetings, calls, or conversations with school staff, these are the single most powerful evidence type. Most BDTR applications are one person's word against a school. Audio recordings with faculty admissions are rare and devastating to the school's defense. Upload recordings to Gemini's web interface (gemini.google.com) and ask it to transcribe them with speaker attribution and pull out key quotes. Then share those quotes with Claude.

### Timeline Expectations
- **Today:** Application drafted, filled on portal, saved and ready for your review + submission
- **Within 1 week:** Upload any additional evidence files, review everything, submit
- **45 days:** FERPA records from school should arrive (supplemental evidence)
- **60 days:** If no acknowledgment from ED, call Borrower Defense Hotline 1-855-279-6207
- **Months to years:** ED processes the claim. Your loans are in forbearance while pending.

## Process Overview

The skill has 8 phases. Run them in order. Do NOT stop between phases unless the user asks.

---

### Phase 1: Intake Interview

Ask the user about their situation. Gather:

1. **School name** and approximate dates of attendance
2. **What happened** - what did the school promise vs. what they delivered?
3. **Key people involved** - instructors, administrators, financial aid officers, accommodation staff
4. **Disability accommodations** - were any on file? Were they violated?
5. **Evidence available** - recordings, emails, complaint documents, screenshots
6. **Current loan balance** - approximate amount owed
7. **Current employment** - does their job use the degree? Did they need other training?
8. **Prior complaints filed** - with the school, OCR, state agencies, DRW, etc.

**Critical questions to ask:**
- "Did you try to withdraw? What happened when you did?"
- "Did anyone at the school make specific promises to keep you enrolled?"
- "Do you have any recordings, emails, or written complaints?"
- "Did you have to get additional training/certifications after graduating to become employable?"

Save all intake notes to `~/Downloads/BDTR_Submission/intake_notes.txt`.

---

### Phase 2: Evidence Gathering

#### 2a: Gmail Evidence (via Gemini CLI)

Use the `/gemini-collab` skill to search the user's Gmail for evidence. Gemini CLI has Gmail API access when run with `--yolo`.

```bash
python "C:/Users/caleb/.claude/skills/gemini-collab/scripts/gemini_client.py" \
  --prompt "Search my Gmail for emails related to '[SCHOOL NAME]' OR '[KEY PEOPLE]' OR 'disability' OR 'accommodations' OR 'complaint' OR 'grievance'. For each email found, save the full Date, From, To, Subject, and complete body text as individual files in [OUTPUT_DIR]/email_evidence/. Name files descriptively." \
  --yolo \
  --cwd "[OUTPUT_DIR]" \
  --timeout 300
```

**Important:** Gemini's Gmail integration requires prior authentication via `gemini` CLI interactive mode. If exit code 41, tell user to run `! gemini` to authenticate first.

**Be selective about evidence.** Only include emails that directly support the claim:
- Correspondence with disability/accommodation offices
- Complaints or grievances filed
- Financial aid communications showing problems
- Emails from the school making specific promises
- Outside legal counsel communications (e.g., Disability Rights Washington)

Do NOT include alumni newsletters, marketing emails, or platform notification digests.

#### 2b: Audio Evidence

If the user has audio recordings (meetings, calls), this is extremely powerful evidence. Most BDTR applications are he-said/she-said. Audio recordings with faculty admissions are rare and devastating.

**Tell the user:**
"If you have any audio recordings related to your situation, upload them to the Gemini web interface at gemini.google.com and ask Gemini to transcribe them and pull out the most important quotes. Specifically ask it to identify:
1. Any admissions of fault or failure by faculty/staff
2. Any statements about the program's structure or lack thereof
3. Any statements about liability, legal risks, or refusal to provide support
4. Any hostile or discriminatory statements
5. Who said what - speaker attribution is critical

Then paste the transcript and key quotes back here so we can use them in the application."

**Audio files CANNOT be uploaded to the portal.** Accepted formats: .doc, .docx, .pdf, .xls, .xlsx, .txt, .ppt, .pptx, .bmp, .gif, .jpg, .png, .psd, .tiff, .tif. No audio or video files.

**Instead, convert audio to a transcript document:**
1. Tell the user to upload the audio to Gemini's web interface at gemini.google.com
2. Ask Gemini to: "Transcribe this entire recording with speaker attribution. For each speaker turn, label who is speaking. Then separately list the 10 most important quotes where faculty or administration make admissions, contradict themselves, or say anything that could be evidence of institutional misconduct."
3. Save the transcript as a .txt file and upload THAT to the portal
4. The user should also keep the original audio file safely stored in case the Department of Education requests it later

**Audio compression (for backup/reference only):** Even though the portal won't accept audio, compress and save it locally in case ED requests it:
```bash
ffmpeg -i "INPUT.m4a" -c:a aac -b:a 12k -ar 8000 -ac 1 "OUTPUT.m4a"
```
Install ffmpeg if missing: `winget install ffmpeg --accept-package-agreements --accept-source-agreements`

#### 2c: Additional Evidence to Request

Advise the user to send these requests (draft the emails for them):

1. **FERPA Request** to the school's registrar - demand complete educational records, financial aid records, grievance files, accommodation records
2. **Records Request** to any disability rights organization they consulted
3. **FOIA/Public Records** to any state agencies they filed complaints with

These take 45 days. The application can be filed now and supplemented later.

---

### Phase 3: Narrative Drafting

Draft the sworn statement narrative. Create these files in `~/Downloads/BDTR_Submission/`:

1. **`BDTR_Sworn_Narrative.txt`** - Full comprehensive narrative (the master document)
2. **`Evidence_Index_and_Transcript.txt`** - Key quotes with speaker attributions
3. **`1_Misrepresentation.txt`** - For the Employment Prospects form field
4. **`2_Breach_of_Contract.txt`** - For the Educational Services form field
5. **`3_Hostile_Environment_Retention.txt`** - For the Other/Urgency form fields
6. **`4_Lack_of_Educational_Benefit.txt`** - For the Financial Harm form field
7. **`Supplemental_Sworn_Statement.txt`** - Extended version for upload as evidence

**Writing guidelines:**
- Write in first person as the applicant
- Be specific: names, dates, direct quotes, exact dollar amounts
- Show emotional texture: frustration, fear, betrayal. This is a real person's story.
- Reference evidence by exhibit letter (Exhibit A, Exhibit B, etc.)
- Request discharge of ALL loans for ALL terms, not just one program

**Portal character restrictions (critical):**
The StudentAid.gov form rejects these characters: `" ( ) : ; $ ! @ [ ] { } < > = + ~ ^ |`
Allowed characters: letters, numbers, spaces, comma, period, apostrophe, hyphen, slash, ampersand, pound sign.
- Use single quotes instead of double quotes for quoting people
- Use hyphens or slashes instead of parentheses
- Write out dollar amounts without the $ sign
- Use periods instead of colons

---

### Phase 4: Human Writing Check

Run `/human-writing-check` on all narrative text files before entering them into the portal. This is essential because:

1. The application is signed under penalty of perjury - it must read as written by the applicant
2. AI-generated text has detectable patterns that could undermine credibility
3. The Department of Education reviewers read thousands of applications

Key tells to eliminate:
- Em dashes (replace with commas or periods)
- Rule of three lists
- "Additionally", "furthermore", "moreover"
- Uniform paragraph structure
- Overly formal language that doesn't match how the person actually talks

---

### Phase 5: Portal Form Filling

Navigate StudentAid.gov via Claude in Chrome. The portal is at `https://studentaid.gov/borrower-defense/`.

**Session management is critical.** The portal has aggressive timeouts. Key strategies:
- User must handle all login/2FA steps - expect to re-login 3-5 times
- Move fast once logged in - do NOT pause to research, draft, or deliberate while logged in
- Do ALL text drafting, evidence gathering, and human-writing-check BEFORE touching the portal
- Use JavaScript execution for rapid form filling (much faster than click-by-click)
- Save and Exit frequently to preserve progress
- The draft can be resumed via My Activity > Manage Applications
- If the Chrome extension disconnects (happens occasionally), call `tabs_context_mcp` to reconnect
- If a "Leave site?" dialog blocks navigation, use `force: true` on the navigate call or click Continue via JS
- When the "Are you still there?" timeout dialog appears, immediately click "I'm Still Here!" via ref or coordinate
- NEVER stop to ask the user questions while the portal is open - keep moving or Save and Exit first
- Draft ALL narrative text into local files first, run human-writing-check, THEN open the portal and paste everything in one fast session
- The JS bulk-fill approach (setting all textareas in one JS call) is 10x faster than using form_input one field at a time

**The 7-step form:**

1. **Borrower Information** - Pre-filled from FSA account. Just click Continue.
2. **School Information** - Check the school, select program, fill enrollment details. Education level at enrollment, state during enrollment, still enrolled (No), attended online.
3. **Allegations** - Check categories: Employment Prospects, Educational Services, Program Cost and Nature of Loans, Urgency to Enroll, Other. Then fill text fields for each.
4. **Financial Harm** - Monetary loss amount, date discovered, employment details, narrative about financial impact.
5. **Other Relief** - Usually No to all (no other compensation received).
6. **Loan Payment Pause** - Yes for forbearance while claim is pending.
7. **Review and Submit** - **NEVER click Submit.** Only the user can do this (perjury attestation).

**JavaScript form filling pattern (fastest approach):**

```javascript
// Fill all textareas on a page in one shot
const textareas = document.querySelectorAll('textarea');
const texts = ['text for field 1', 'text for field 2', ...];
textareas.forEach((ta, i) => {
  if (i < texts.length) {
    const setter = Object.getOwnPropertyDescriptor(
      window.HTMLTextAreaElement.prototype, 'value'
    ).set;
    setter.call(ta, texts[i]);
    ta.dispatchEvent(new Event('input', { bubbles: true }));
    ta.dispatchEvent(new Event('change', { bubbles: true }));
  }
});

// Click Continue
const buttons = document.querySelectorAll('button');
for (const btn of buttons) {
  if (btn.textContent.trim() === 'Continue') { btn.click(); break; }
}
```

**For date fields (Month/Day/Year):** Use `form_input` tool with element refs, not JS. The React form doesn't register JS-set values on date fields.

**For radio buttons:** Click the first radio in each group for "Yes", second for "No".

**For checkboxes:** Click directly via coordinate or ref.

**File uploads cannot be automated.** The native OS file picker blocks programmatic access. Tell the user to upload files manually after all text is entered. Files go on each allegation sub-page's "Upload File" button.

---

### Phase 6: Evidence File Upload (Manual)

Tell the user exactly which files to upload and where. Provide a checklist:

```
FILES TO UPLOAD (all in ~/Downloads/BDTR_Submission/):

On the Employment Prospects allegation page:
[ ] Supplemental_Sworn_Statement.txt
[ ] Full_Audio_Transcript.txt (from Gemini transcription - NOT the audio file)
[ ] Evidence_Index_and_Transcript.txt
[ ] DRW/legal counsel email
[ ] Access Services/accommodation emails
[ ] Financial aid correspondence

Upload limit: 5MB per file
Accepted formats: .doc .docx .pdf .xls .xlsx .txt .ppt .pptx .bmp .gif .jpg .png .psd .tiff .tif
NOTE: NO audio or video files accepted. Convert recordings to transcripts.
```

---

### Phase 7: Strategic Review

Before the user submits, run a strategic assessment. Check:

1. **Does the narrative hit all required elements for the applicable legal standard?**
   - Pre-7/1/2017 loans: State consumer protection law violations
   - 7/1/2017-6/30/2020 loans: Breach of contract OR substantial misrepresentation
   - Post-7/1/2020 loans: School's knowledge of falsity + financial harm + limited to employment/programs/charges

2. **Is there contemporaneous evidence?** (Audio recordings, emails from the time period, outside legal counsel communications)

3. **Are all the right allegation categories checked?** Don't over-check (dilutes the claim) but don't under-check (misses applicable categories).

4. **Is financial harm concrete and documented?** Exact loan balance, specific alternative training costs, clear causal link.

5. **Does the narrative sound human?** Run /human-writing-check if not already done.

6. **Are all people named with titles?** Faculty, administrators, accommodation staff, financial aid office.

7. **Is the request clear?** Full discharge of ALL loans, ALL terms, ALL programs.

---

### Phase 8: Handoff

Save comprehensive session notes for future reference:

1. Update `~/Downloads/BDTR_Submission/APPLICATION_COMPLETE_REFERENCE.txt` with final status
2. Save to Claude Code memory: draft ID, filing status, pending evidence (FERPA deadline, etc.)
3. Set calendar reminder for FERPA response deadline (45 days)
4. Tell user to call Borrower Defense Hotline at 1-855-279-6207 after submitting to confirm receipt

**Post-submission checklist for the user:**
- [ ] Upload remaining evidence files before clicking Submit
- [ ] Review all text on the Review page
- [ ] Click Submit (perjury attestation - only you can do this)
- [ ] Screenshot the confirmation page
- [ ] Note your case/claim number
- [ ] Call 1-855-279-6207 in 3-5 days to confirm receipt
- [ ] When FERPA records arrive, upload as supplemental evidence
- [ ] When DRW intake notes arrive, upload as supplemental evidence

---

## Key Research Findings

### Submission Method
- **Portal is strongly preferred** over email. Gives instant tracking, claim number, Status Center access.
- Email to BorrowerDefense@ed.gov is a valid backup but provides no confirmation receipt.
- Do NOT submit via both methods simultaneously - duplicates can delay processing.
- If portal has technical issues with file uploads, supplement via email for oversized files only.

### Legal Standards by Loan Period
- The 2023 borrower defense regulation is **enjoined** - 1994, 2016, and 2020 rules apply
- Post-7/1/2020 (2020 Rule) is strictest: requires school's "knowledge of falsity", demonstrable "financial harm", limited to 3 claim areas
- Audio recordings proving the school admitted fault are the single strongest evidence type

### Sweet v. McMahon Context
- Settlement forced ED to clear backlog and process claims fairly
- Does not automatically approve new applications
- Court-enforced deadlines mean ED is under scrutiny to take claims seriously
- New applications are evaluated on individual merits under current regulations

### Hard-Won Lessons from Real Sessions
- **Do all prep work BEFORE opening the portal.** Draft narratives, gather Gmail evidence, compress audio, run human-writing-check - all of this should be done while the portal is closed. Only open the portal when you have all text ready to paste.
- **The portal will log you out mid-work.** This is not a bug, it is a feature of government websites. The user will need to re-login with 2FA each time. Have them keep Gmail open for the codes.
- **React form fields don't always accept programmatic value setting.** The JS `Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set` trick works for textareas but date fields (split into Month/Day/Year) need the `form_input` Chrome tool instead.
- **Gemini CLI Gmail integration is for SEARCHING and SAVING emails, never for SENDING.** If the user says "get the emails" they mean retrieve evidence from Gmail, not compose new emails.
- **Be selective about email evidence.** A Gmail search for school-related keywords will return hundreds of results. Most are alumni newsletters and platform notifications. Only include emails that directly document misconduct, accommodations, complaints, or financial aid problems.
- **The "Other" checkbox on the Urgency to Enroll category** is how you cover fraudulent RETENTION (pressuring someone to stay) since the category name implies initial enrollment pressure.
- **Name everyone.** The form asks "who told you this" - list every person from every office who was involved, not just the teachers. Include administration, financial aid, disability services, accommodation coaches.
- **ffmpeg path after winget install** may not be in the current shell's PATH. Use the full path: find it with `find /c/Users/*/AppData -name "ffmpeg.exe" -type f`

### Portal Technical Notes
- Session timeout: aggressive, roughly 15-20 minutes of inactivity
- Save and Exit preserves all entered data including text fields
- Draft resumes via My Activity > Borrower Defense > Draft
- Character limit per text field: 2000 characters
- File upload limit: 5MB per file
- No confirmed save-and-return for mid-page progress (only Save and Exit)
- Form rejects special characters: must strip quotes, parentheses, dollar signs, colons

### Advocacy Organization Consensus
Every major org (PPSL, DefenseClaims, NASFAA, Tate Esq.) recommends the portal as primary submission method. Email is backup only.
