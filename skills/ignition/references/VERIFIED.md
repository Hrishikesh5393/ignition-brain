# Verification baseline

Every mechanism claim in this skill marked verified was checked by **decompiling the shipped
jars and/or a live write → fsync → scan → runtime-read round-trip** against an Ignition
**8.3.9** gateway (build 2026-08-25, standard edition), 2026-09-04 unless a section names a
later date. Companion facts:

- Official-manual distillation (`references/ignition-8-3/`): docs snapshot 2026-09-22.
- `<repo>/schema/system-api.raw.json` reflection dump: 2026-09-03; enriched and Perspective components
  enumerated 2026-09-04 (Perspective 3.3.9, Reporting 7.3.9, alarm-notification 7.3.9).
- Method (how to re-verify on another build): `references/gateway/notes/verification.md`.

Version stamps inside individual files (e.g. "8.3.9 removed …") mark **behavioural version
differences** and are global knowledge, not gateway references. Re-verify the specifics you
depend on when the target gateway build differs from the baseline above.
