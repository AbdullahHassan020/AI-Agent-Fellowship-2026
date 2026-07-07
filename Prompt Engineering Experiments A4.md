# Prompt Engineering Experiments

A hands-on report comparing five core prompting techniques. Each experiment shows the exact **prompt**, a representative **output**, **observations** about what happened and why, and concrete **improvements** you could make from there.

---

## Experiment 1 — Role Prompting

**Goal:** See how assigning the model a persona/role changes tone, depth, and vocabulary of a technical explanation.

### Prompt A (no role)
```
Explain overfitting in machine learning.
```

### Output A
> Overfitting happens when a model learns the training data too closely, including its noise and random fluctuations, so it performs well on training data but poorly on new, unseen data. It's usually caused by a model that's too complex relative to the amount of training data. Common fixes include regularization, cross-validation, simplifying the model, and gathering more data.

### Prompt B (with role)
```
You are a senior machine learning engineer mentoring a junior developer
who just joined the team. Explain overfitting in machine learning,
using an analogy they'd remember, and end with one practical tip
they can apply this week.
```

### Output B
> Think of overfitting like a student who memorizes last year's exam questions word-for-word instead of actually understanding the subject. They'll ace a test with the exact same questions, but the moment a new question shows up, they're lost — because they never learned the underlying concepts, just the specific answers.
>
> That's exactly what an overfit model does: it memorizes the quirks and noise in the training set instead of learning the general pattern, so it looks great on training data and falls apart on real-world data.
>
> **This week's tip:** split off a validation set before you start tuning anything, and watch the gap between training and validation loss. If training loss keeps dropping while validation loss climbs, that gap is your early-warning sign.

### Observations
- The role prompt didn't just change tone — it changed **structure** (analogy → explanation → actionable tip) because the role implied an audience and a purpose.
- Output B is longer but more useful in a real mentoring context; Output A is more "textbook" and better for a glossary or FAQ.
- Role prompting is most powerful when the role implies both an **expertise level** and a **relationship** (mentor→junior, not just "expert").

### Improvements
- Combine role + audience explicitly: *"...explain to someone who knows Python but has never trained a model."* Role alone can be vague; role + audience narrows the output further.
- Add a constraint on length or format (e.g., "3 sentences max") to prevent the persona from over-elaborating.
- Test whether the role changes *correctness*, not just style — for factual/technical tasks, always verify the persona hasn't traded accuracy for personality.

---

## Experiment 2 — Chain-of-Thought (CoT) Prompting

**Goal:** Compare direct-answer prompting against step-by-step reasoning on a task with multiple interacting constraints.

### Prompt A (direct answer)
```
A bakery sells cupcakes for $3 and cookies for $1.50. Sarah spent $18
and bought twice as many cookies as cupcakes. How many of each did she buy?
```

### Output A
> Sarah bought 4 cupcakes and 8 cookies.

*(This happens to be correct here, but direct prompts on multi-step arithmetic are more prone to silently skipping a constraint or making an arithmetic slip, especially as problems get more complex.)*

### Prompt B (chain-of-thought)
```
A bakery sells cupcakes for $3 and cookies for $1.50. Sarah spent $18
and bought twice as many cookies as cupcakes. How many of each did she buy?

Think through this step by step:
1. Define variables for the unknowns.
2. Write an equation using the total cost.
3. Use the "twice as many" relationship to substitute.
4. Solve and verify the answer against both original conditions.
```

### Output B
> **Step 1:** Let c = number of cupcakes, k = number of cookies.
> **Step 2:** Cost equation: 3c + 1.5k = 18
> **Step 3:** "Twice as many cookies as cupcakes" means k = 2c. Substitute: 3c + 1.5(2c) = 18 → 3c + 3c = 18 → 6c = 18 → c = 3.
> **Step 4:** So k = 2(3) = 6. Check: 3(3) + 1.5(6) = 9 + 9 = 18 ✓, and 6 is twice 3 ✓.
>
> **Answer: 3 cupcakes and 6 cookies.**

### Observations
- The two outputs **disagree** (4/8 vs 3/6) — the direct-answer version got it wrong, and CoT caught it because it forced an explicit verification step.
- CoT trades tokens/latency for reliability. On simple lookups this is wasted effort; on multi-constraint or arithmetic-heavy problems it materially reduces error rate.
- Numbering the steps *for* the model (rather than just saying "think step by step") produced a more consistent, checkable structure than a generic instruction would.

### Improvements
- Add a self-check instruction: *"After solving, plug your answer back into the original problem and flag any contradiction."* — this is what caught the error above.
- For production use, consider hiding the reasoning from the end user (show only the final answer) while still generating it internally, since reasoning traces can be verbose.
- For harder problems, combine CoT with **few-shot** worked examples (Experiment 3) so the model has a template for how much detail to show at each step.

---

## Experiment 3 — Few-Shot Prompting

**Goal:** Test whether providing labeled examples improves consistency on a task with a specific, non-obvious output style.

### Prompt A (zero-shot)
```
Classify the sentiment of this review as Positive, Negative, or Mixed.
Review: "The battery life is incredible, but the camera is a huge
step down from my last phone."
```

### Output A
> Mixed

*(Correct, but on ambiguous review sets, zero-shot classification is inconsistent about borderline cases — sometimes calling a mildly-mixed review "Positive" if the positive clause comes first, or ignoring the "Mixed" category and forcing binary output.)*

### Prompt B (few-shot)
```
Classify the sentiment as Positive, Negative, or Mixed. Use "Mixed"
whenever the review contains at least one clear positive AND one clear
negative point, even if one outweighs the other.

Review: "Fast shipping and great packaging."
Sentiment: Positive

Review: "Broke after two days, total waste of money."
Sentiment: Negative

Review: "Great sound quality, but the app crashes constantly."
Sentiment: Mixed

Review: "The battery life is incredible, but the camera is a huge
step down from my last phone."
Sentiment:
```

### Output B
> Mixed

### Observations
- On this single example both approaches agree, but the *value* of few-shot shows up across a **batch**: with the examples in place, the model consistently applies the "Mixed" rule to borderline cases, whereas zero-shot runs occasionally default to picking the dominant sentiment.
- The examples did double duty: they taught the **label set** and, more importantly, taught the **decision rule** ("Mixed" requires one clear point on each side) that was hard to state precisely in a single instruction sentence.
- Order and diversity of examples mattered — including one Positive, one Negative, and one Mixed example (rather than three Positive examples) is what let the model generalize the rule instead of memorizing a pattern.

### Improvements
- Add an "edge case" example (e.g., a purely neutral/factual review with no sentiment) if that category can appear in real data, so the model knows what to do outside the three defined labels.
- For larger datasets, rotate or randomize few-shot examples across calls to check the classifier isn't overfitting to the specific phrasing of the examples.
- Once the rule is stable, consider whether the few-shot examples can be replaced by a sharper zero-shot instruction (the rule you inferred from the examples) — this saves tokens once you know exactly what worked.

---

## Experiment 4 — Structured Output (JSON)

**Goal:** Get reliably parseable output for downstream code, rather than free-form prose.

### Prompt A (unstructured)
```
Extract the key details from this email:
"Hi team, quick reminder that the Q3 budget review is moved to
Thursday, July 16th at 2pm in Conference Room B. Please bring your
department's spend report. - Maria"
```

### Output A
> The Q3 budget review has been rescheduled to Thursday, July 16th at 2pm in Conference Room B. Attendees should bring their department's spend report. Sent by Maria.

*(Human-readable, but a script would need fragile string-parsing to pull out the date, time, and location.)*

### Prompt B (structured JSON)
```
Extract the key details from this email and return ONLY valid JSON
matching this exact schema, with no commentary before or after:

{
  "event": string,
  "date": string,       // format: YYYY-MM-DD, infer year as 2026 if omitted
  "time": string,       // 24-hour format, e.g. "14:00"
  "location": string,
  "action_items": string[],
  "sender": string
}

Email:
"Hi team, quick reminder that the Q3 budget review is moved to
Thursday, July 16th at 2pm in Conference Room B. Please bring your
department's spend report. - Maria"
```

### Output B
```json
{
  "event": "Q3 budget review",
  "date": "2026-07-16",
  "time": "14:00",
  "location": "Conference Room B",
  "action_items": ["Bring department's spend report"],
  "sender": "Maria"
}
```

### Observations
- Defining the schema **inline, with types and format comments**, was the single biggest factor in getting clean, parseable output — vaguer instructions like "return JSON" alone tend to produce inconsistent field names or nested structures that drift call to call.
- Explicitly saying "ONLY valid JSON... no commentary before or after" prevented the common failure mode of the model prefacing the answer with "Here's the JSON:" or wrapping it in markdown fences, both of which break naive `JSON.parse()` calls.
- Giving an inference rule for missing data (the year) avoided a null field the downstream code would have had to handle separately.

### Improvements
- Add explicit handling for missing/unclear fields, e.g., `"location": string | null`, so the model has a defined way to signal "not found" instead of guessing.
- For production systems, pair this prompt with a JSON-schema validator on the code side and a retry-with-error-message loop for the rare malformed response.
- If using an API that supports it, prefer a native structured-output / tool-calling mode over prompt-only JSON — it guarantees schema conformance instead of relying on the model to follow instructions.

---

## Experiment 5 — Prompt Optimization

**Goal:** Show the iterative process of tightening a vague prompt into a reliable one, across several revisions.

### v1 — Vague
```
Write a follow-up email after a sales call.
```
**Output:** A generic, overly formal email with placeholder-sounding language ("I hope this email finds you well... following up on our recent conversation...") and no specifics — usable as a skeleton at best.

**Problem:** No context about the call, the recipient, or the desired next step, so the model fills gaps with clichés.

### v2 — Added context
```
Write a follow-up email after a sales call with a prospect named Alex
at a mid-sized logistics company. We discussed their need to cut
warehouse costs, and they seemed interested in our inventory
software's automated reordering feature. Ask for a 30-minute demo
next week.
```
**Output:** A more specific, relevant email that references the actual pain point (warehouse costs) and feature (automated reordering), and proposes a demo — a real improvement, but the tone still runs long and slightly salesy.

**Problem:** Content is right, but style/length is still unconstrained, so the model defaults to a "sales-brochure" voice.

### v3 — Added tone, length, and format constraints
```
Write a follow-up email after a sales call. Context: prospect is
Alex at a mid-sized logistics company; we discussed cutting
warehouse costs; they showed interest in our automated reordering
feature.

Constraints:
- Under 120 words
- Conversational, not salesy — write like a helpful peer, not a
  brochure
- One clear call to action: propose a 30-minute demo next week
- Subject line included
- No exclamation points, no "I hope this email finds you well"
```
**Output:**
> **Subject: Automated reordering — quick next step?**
>
> Hi Alex,
>
> Good talking through your warehouse cost challenges yesterday. The automated reordering feature we touched on is designed exactly for the kind of manual overhead you described — it could be a strong fit.
>
> Want to grab 30 minutes next week for a live demo? I can tailor it to your current reorder workflow so you can see the impact directly.
>
> Let me know a couple of times that work, and I'll send an invite.
>
> Best,
> [Your name]

**Improvement realized:** Concise, specific, on-tone, and immediately usable with only a name swap.

### Observations across the process
- Each revision fixed exactly one category of problem: v1→v2 fixed **content specificity**, v2→v3 fixed **style/format**. Trying to fix both at once in a single giant prompt tends to produce a prompt that's hard to debug when something goes wrong.
- Negative constraints ("no exclamation points," "not salesy") were as useful as positive ones — naming the failure mode you saw in v2 is often the fastest way to eliminate it in v3.
- Word/format constraints (length cap, subject line required) made the output far more consistent across repeated runs, not just better on a single sample.

### Improvements (next iteration)
- A/B test v3 against a version with a few-shot example of a "good" email in the target voice, to see if that closes the gap further with less explicit instruction-writing.
- Parameterize the prompt (name, company, pain point, feature) as a template so it can be reused programmatically instead of hand-edited each time.
- Track output quality over many runs (not just one sample) — optimization decisions should be based on consistency across a batch, since any single output can look good or bad by chance.

---

## Summary Table

| Experiment | Technique | Key Lever | Biggest Win |
|---|---|---|---|
| 1 | Role Prompting | Persona + audience | Matches tone/structure to context |
| 2 | Chain-of-Thought | Explicit reasoning steps + self-check | Catches multi-step errors |
| 3 | Few-Shot | Examples that encode a *rule*, not just labels | Consistency on edge cases |
| 4 | Structured Output | Inline schema + strict format instruction | Reliable, parseable results |
| 5 | Prompt Optimization | Iterative, one-fix-at-a-time revisions | Compounding, debuggable gains |

**General takeaway:** the most effective prompts usually combine two or more of these techniques — e.g., a role + few-shot examples + a JSON schema — rather than relying on any single trick in isolation.
