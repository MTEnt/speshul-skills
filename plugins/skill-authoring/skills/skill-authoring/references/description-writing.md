# Writing the description

The description is loaded for every skill at session start and is the only text the router uses to choose. Budget: under 1024 characters, ideally 250 to 500.

## Shape

```text
<What it does, as verbs over concrete objects>. Use when <triggering requests, in the user's words>. <Boundary: what it is not for, or which sibling skill takes those requests>.
```

1. **Verbs over objects.** "Audit and improve conversion on marketing pages and lead forms" routes; "Helps with CRO" does not.
2. **Trigger phrases in the user's vocabulary.** Include the nouns a user types: the platform names, artifact names, and symptoms ("form abandonment", "tests fail only in CI").
3. **A boundary sentence.** Name the nearest sibling and hand its requests over explicitly. This is what stops two skills from firing on the same prompt.
4. **No claims about quality.** "Comprehensive", "best-practice", and "expert" carry no routing information.

## Check overlap

For every pair of skills that a user could confuse, the token sets of their descriptions should share less than about a third of their distinctive words. `scripts/skill_lint.py --siblings <dir>` computes this. When two descriptions overlap:

- merge the skills if they answer the same question;
- otherwise move the shared vocabulary to the boundary sentence of the one that does not own it ("use X for ...").

## Examples

Weak:

```text
description: Expert copywriting assistant for all your marketing needs.
```

Routes on nothing specific, overlaps with every marketing skill, and promises quality instead of scope.

Strong:

```text
description: Write or substantially rewrite persuasive page copy for homepages, landing, pricing, feature, and product pages. Use for value propositions, headlines, message hierarchy, and CTA language; use copy-review for a bounded edit of existing copy.
```

Names the artifacts, names the triggers, and hands the neighboring job to its owner.
