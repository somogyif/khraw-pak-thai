# Khraw Pak Thai — rebuilding a restaurant's website, and learning to distrust the output

**Live:** [khrawpakthai.com](https://khrawpakthai.com) · **Code:** [github.com/somogyif/khraw-pak-thai](https://github.com/somogyif/khraw-pak-thai)

*A month of work on a real business's public website, built by directing AI coding
tools. I am not a developer. What follows is what I wanted, how I worked, what went
wrong, and what I would tell someone starting the same way.*

---

## Why I did it

Khraw Pak Thai is a Thai–Hungarian restaurant in Budapest, beside Heroes' Square. In
February 2026 it moved to a new location, and the website did not move with it. It was
a page-builder one-pager whose browser tab still read **`Weboldal HU`** — the
template's placeholder title, never changed. The menu was out of date. There was no
English page, in a spot where half the passing traffic is tourists coming off a UNESCO
square.

The business problem was simple and unglamorous: **people were standing outside
looking for a reason to come in, and the website was not giving them one.**

I could have paid an agency. I wanted to find out whether I could direct AI coding
tools well enough to ship something a professional would not be embarrassed by — and
to learn what that actually takes, which turned out to be the more interesting
question.

---

## What I brought, and what the AI brought

I want to be precise about this, because the honest version is more useful than the
flattering one.

**Mine:** the commercial goal and the positioning. The decision to lead with fusion —
authentic Thai *and* Hungarian classics on one menu, so a mixed group can eat at the
same table. The brand voice. Every judgement call about what belongs on the page.
Native-Hungarian quality control, which mattered more than I expected. And the
decision, repeatedly, about what *not* to build.

**The AI's:** all of the code. The research. Extracting a 20-page print PDF into a
structured menu with 48 dish photographs, converting CMYK to sRGB along the way. The
deployment, the DNS cutover, the test suites.

**Neither of us alone:** the architecture. I set the constraints — no framework, no
build step, something a non-developer can still open in three years — and pushed back
when the proposals drifted from them.

The site is **not hand-coded**, and the documents used to say it was. I had that
removed twice, and the second time we added an automated check that fails the build if
the claim reappears. The point of the project is that one person with the right tools
can ship a real product end to end. Claiming otherwise sells that short, and happens to
be false.

---

## How I worked

### I assumed the output was wrong until something proved otherwise

This turned out to be the whole game.

The code looked right. It passed review. It shipped. And **seven bugs sat in it for
three weeks** — through three separate rounds of external AI review by three different
models — because every check we had read the *files* rather than the *rendered page*:

- The English page relabelled itself Hungarian at runtime.
- 36 of 60 image descriptions stayed Hungarian, so a blind English-speaking visitor
  got the entire image layer in the wrong language.
- The spam honeypot's input field vanished from the generated English form.
- The 48 menu photographs could not be opened with a keyboard at all.
- A sanitiser, since removed, silently converted the privacy-notice link into plain
  text on every page load — the link that satisfies a legal information duty.

Every HTML source was correct. The output was not. Text-based checking could not have
found any of them, no matter how many checks we wrote.

Nobody found them by being careful. They were found the first time anyone **opened the
page in a browser**.

### So I built the check that could see them

```
tests/audit.py         81 checks · no dependencies · runs in a second · pre-commit gate
tests/render-check.py  62 checks · real browser · every push, and weekly against production
```

The second layer drives Chromium and asserts on what the browser actually produces:
document language, leftover Hungarian in attributes, links that are actually links,
keyboard reachability and focus return, zero cookies, no horizontal overflow at 320,
390 and 1280 pixels. It would have caught all seven. On its first run it found an
eighth nobody had noticed.

It also runs weekly against the live site — because that catches a broken *deploy*,
not just broken code.

### I made three other AI models attack the work

Three rounds, three models (Grok, Gemini, Kimi), each explicitly asked to find what
was wrong rather than to be helpful. I gave each one a different lens and told the
third what the first two had claimed, so it could argue with them instead of repeating
them.

**The measured result: roughly ten real findings and six factually false ones.**

The false ones were confident and specific — that images lacked dimensions when every
one had them; that the menu was images-only when it is 61 text entries with prices.
Each cost an afternoon to disprove.

The genuinely valuable findings were the ones no code review could reach. An abandoned
Foodora listing, still live and indexed, showing the restaurant as **CLOSED at the old
address**. The Google listing filing us under the neighbouring hotel. And the one that
stung: the restaurant does not appear in the **official Thai SELECT registry**, though
its certificate runs to 2027 — the record still carries the old address and is flagged
inactive, while every Budapest competitor is listed. The page's strongest sentence is
*"we don't claim to be authentic — the Thai government certifies it."* Anyone checking
that in the government's own registry would not have found us.

**The lesson I actually took from this:** more reviewers is the third-best answer. The
best is one automated check that looks at the thing differently. The two worst bugs of
the whole project surfaced not from a reviewer's finding, but from *verifying a
reviewer's claim that turned out to be wrong.*

### I wrote down what broke, and turned it into rules

`MISTAKES.md` records what broke silently or broke twice: what happened, the root
cause, and what now prevents it. When the same pattern shows up repeatedly it graduates
into a one-line rule in `CLAUDE.md`, and the log keeps the reasoning so nobody
undoes the rule later having forgotten why it exists.

One mechanism caused three separate bugs in three disguises before we understood it —
a translation attribute that replaces an element's *entire contents*, quietly deleting
a nested form field in one case. That is now four automated checks and one rule.

### I stopped work when it stopped paying

The multi-agent review sweep cost roughly **10 million tokens** and exhausted a rate
limit twice. It found real things. But when the remaining half of it was verifying
claims about our own files — things checkable locally in seconds, for free — I killed
it and did that part by hand.

That decision is written into the project's rules as *quarterly, not weekly*, with the
measurement that justifies it. Send the expensive tool where you cannot see; use the
free one everywhere else.

---

## What shipped

**A bilingual site on two indexable URLs.** Hungarian at `/`, English generated at
`/en/` from the same source, with reciprocal `hreflang` and a plain link between them.
No client-side language switching — that was removed after it caused most of the
bilingual bugs, taking about 60 lines of JavaScript and an entire bug family with it.

**Zero npm dependencies in what ships.** No framework, no build step at deploy, no
`package.json`. The whole site is 2,433 lines of my own HTML, CSS, JavaScript and
Python across 71 commits.

**Nothing stored in a visitor's browser.** No cookies, no local storage, measured on
every CI run. The Google map is a placeholder until you click it, so Google receives
nothing until you ask. Fonts are self-hosted after the 2022 Munich ruling on passing
visitor IPs to Google. Consequently: no cookie banner, because there is nothing to
consent to.

**Images: 7.0 MB → a 717 KB page.** Three food photographs had been stored as PNG;
menu thumbnails were 720-pixel images rendered into a 62-pixel box. Fixing the format
and the size, not the compression, did almost all of it.

**Compliance treated as a feature, not paperwork.** Bilingual privacy notice, complete
imprint including the hosting provider that Hungarian law requires, and — added last —
the consumer complaint and conciliation board notice that the Consumer Protection Act
requires on the website itself, which was entirely absent. Verified against the
statute text, not from memory, and now guarded by seven automated checks.

**A deliberately removed feature.** I built an automation that pulled fresh Google
reviews via the Places API. It worked end to end. Then I read the Maps Platform Terms
properly: user reviews must not be copied or stored. I deleted it. Later a reviewer
raised a second, independent reason — an English translation of a Hungarian review is a
derivative work the reviewer owns the copyright to. The quoted reviews came off the
page entirely; the rating and a link remain.

---

## What I would tell someone starting this way

**Your job is not to write prompts. Your job is to be the thing that does not trust
the output.** The model will produce something plausible every single time. Plausible
is the failure mode, not an error message.

**Build the check that looks at it differently.** Not more of the same check. Our
81 text checks could never have found the seven rendering bugs; 62 browser checks found
them in one session.

**Verify the critics too.** Six of sixteen external findings were false, and disproving
them is where the two worst real bugs turned up.

**Write down what broke.** Not for tidiness — because the same mechanism will come back
wearing a different mask, and you will not recognise it the third time without notes.

**Know what you are not building.** Every removed feature here — the review
automation, the runtime language switch, the sanitiser — made the project better.

**And check the world outside the repository.** The single most valuable finding in a
month of work was not in the code. It was a stale listing on someone else's website
telling customers we were closed.

---

## Where it stands

81 automated text checks and 62 browser checks, green, on every push. Weekly
verification against production. A written rules file, a mistakes log, and a quarterly
review that must convert every confirmed finding into a permanent check.

Still open, and all of it outside the code: email authentication records, the
Foodora takedown, the Google listing, and a letter to the Thai Trade Center about
that registry entry.

*Human direction, AI implementation — and a month spent learning that the direction is
mostly the distrust.*
