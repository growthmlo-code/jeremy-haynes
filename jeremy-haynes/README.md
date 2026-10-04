# Jeremy Haynes — Business & Marketing Brain

A faithful, **AI-ready knowledge base** distilled from the real YouTube video
transcripts of **Jeremy Haynes** (`@JeremyHaynesTraining`) — a direct-response
marketer who scales coaching, info-product, agency, service and B2B businesses to
**$1M+/month** with paid ads (mostly Meta), call/VSL/webinar funnels, high-ticket
offers and sales teams.

Built by **MLO Growth** as an internal reference "brain": load it into any AI
assistant (Claude, ChatGPT, etc.) and ask questions in his domain — you get his
actual frameworks, numbers, scripts and benchmarks, cited to the source video.

## What's here

```
skill/
  SKILL.md                     # the brain's router + core operating system + usage
  reference/
    01-scaling-to-1m-roadmap.md
    01b-live-consult-diagnostic-method.md
    02-meta-paid-ads-mastery.md
    03-content-and-ad-creative-strategy.md
    04-funnels-architecture.md
    05-vsl-and-high-ticket-sales.md
    06-offers-and-marketing-math.md
    07-mindset-and-wealth-psychology.md
    08-business-model-recurring-revshare.md
manifest.json                  # index of the source videos (id/title/views/duration)
VIDEOS.md                      # same index, human-readable, ranked by views
```

## How to use it

- **As a Claude Code / Claude skill:** the `skill/` folder is a drop-in skill
  (`mlo-jeremy-haynes-brain`). Copy it to `~/.claude/skills/mlo-jeremy-haynes-brain/`
  and invoke it, or ask any question that maps to his domain.
- **As a ChatGPT / custom-GPT knowledge base:** upload the files in `skill/` (SKILL.md
  as the system/instructions, the `reference/*.md` as knowledge) and it will answer
  as the Jeremy Haynes brain.
- **As plain reference:** read the files directly. `SKILL.md` is the map.

## How it was built

1. Enumerated the full channel (**260 videos, ~162 hours**).
2. Pulled transcripts (prioritised by views) into a local corpus.
3. Synthesised the corpus into 9 thematic reference docs — **grounded only in the
   transcripts**, with short cited quotes, worked numbers and his real terminology.

## Scope & fidelity

- Everything is **grounded in his actual videos**. Where the corpus doesn't cover a
  topic, the brain is instructed to say so rather than invent.
- His advice targets **high-ticket / coaching / agency / info / B2B** economics — adapt
  explicitly before applying to low-AOV DTC ecom.
- Several benchmarks are **time-stamped** around Meta's 2025 "Andromeda" change
  (pre/post); prefer the most recent framing on algorithm-dependent topics.

## Copyright

The **raw verbatim transcripts are intentionally NOT included** (gitignored). They are
Jeremy Haynes' copyrighted content and are kept local only to produce this synthesis.
This repository ships MLO Growth's **synthesised knowledge base** (our own writing),
plus a metadata index of the public videos. All credit for the underlying ideas is his
— see each reference file's `## Source videos` and his channel.

_Not affiliated with or endorsed by Jeremy Haynes. Internal study resource._
