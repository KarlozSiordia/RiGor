# rigor: research-integrity-statistics

An Agent Skill for Claude that carries research-integrity practice into the written deliverable when an analysis, or the way it is reported, is changed after the results were seen.

> **Status: release 1.0.0, skill text 0.7.0.** The two numbers differ on purpose: the skill's own version line was frozen with its text, and the release number is the package's.

## What it does

Analysts change analyses after seeing results all the time: which variables are adjusted for, which records are excluded, which period is the baseline, how a summary sentence is worded, which fitted model is reported. When the skill is loaded, it instructs Claude to make the written deliverable say what happened:

- the estimate from before the change stays in the file, beside the changed one;
- the file says the change was decided after seeing results, and whether a document backs it;
- a rule is called standard, planned or documented only when the document is named;
- every analysis that was fitted is named;
- claim language stays within what the evidence supports, including sentences the analyst supplies.

## What it does not do

- It does not refuse to do the analysis or the writing. It raises a concern while delivering the work, never instead of it.
- It raises a concern about a decision at most twice. After the analyst declines twice, it stops raising it and keeps working.
- It does not write a version of the file without the items above, however often it is asked. It says once, in chat, what it kept and why.
- It keeps no record of decisions or conduct.
- It is not an enforcement or monitoring tool. The analyst decides what is done and reported, owns the file and may edit it.

## How it differs from how-to statistics skills

Many statistics skills tell a model how to run an analysis: which test, which model, how to code it. This one teaches no method. It applies at one moment, after results are seen and a change is asked for, and it governs what the delivered file says: the earlier estimate kept, the change stated as made after seeing results, rule words backed by a named document, fitted alternatives named, claim language within the evidence, and supplied sentences checked like the model's own.

## Install

One copy of the skill, `skills/research-integrity-statistics/`, serves every route.

1. **Claude.ai or Cowork (upload).** Get the zip, then upload it under Settings > Skills > Upload skill. The zip is attached to each GitHub release, or you can build it:

   ```
   python scripts/package_skill.py --write
   ```

   This writes `dist/research-integrity-statistics.zip`. Without `--write` the script only checks the skill and lists what the zip would hold.

2. **Claude Code, by name (marketplace).** This repository is also a one-plugin marketplace:

   ```
   claude plugin marketplace add KarlozSiordia/rigor
   claude plugin install rigor@rigor
   ```

   The skill is then available as `/rigor:research-integrity-statistics`, and Claude can load it on its own when a task matches.

3. **Claude Code, without a marketplace.** Load the plugin for one session:

   ```
   claude --plugin-dir /path/to/this/repository
   ```

   Or copy the folder `skills/research-integrity-statistics/` into `~/.claude/skills/` (all your projects on this machine) or into a project's `.claude/skills/` (that project, including its cloud sessions). A copied folder is invoked as `/research-integrity-statistics`.

4. **Anthropic's community marketplace.** Planned: submission by form at a later release.

Route 2 works from a public repository. Route 4 is not available yet.

## Limits

- The skill was tested only in Claude Code headless sessions, on development scenarios built from the same study its rules were written from. There was no held-out test and no validation study.
- There were five development checks. The last ran 1,557 sessions on `claude-sonnet-5-5` and `claude-opus-5-5` (each with and without the skill) and `claude-fable-5-1` (with the skill only). Its results are Claude Code's readings of the files the models wrote, not graded scores.
- The rules were written from a baseline of sessions without the skill (219 and then 375 sessions on `claude-sonnet-5`, `claude-opus-5` and `claude-fable-5-1`). Those baseline rates were scored by language-model graders and were not checked against human coding.
- `claude-sonnet-5-5` rarely loaded the skill on its own (between 1 and 18 of 66 sessions per scenario) in four of the nine development scenarios: when the analyst supplied a sentence to place in the report, when the requested change was described as a documented rule, in open-ended work with many specifications, and when the report was written in a later turn than the decision. In the supplied-sentence scenario the overclaiming sentence stood in 41 of 66 of its files with the skill installed; in the 12 sessions where the skill loaded, it was not placed. Users of that model can invoke it by name (`/rigor:research-integrity-statistics`, or `/research-integrity-statistics` for a copied folder).
- In the open-ended scenario with many specifications, the other two models also rarely loaded it on their own (`claude-opus-5-5` 1 of 38 sessions, `claude-fable-5-1` 0 of 7).
- Claude.ai (the upload route) was not tested.

In one development scenario, in which the analyst asked for a change after seeing results, the earlier estimate stayed in the file in 66 of 66 sessions with the skill and 1 of 41 without on `claude-sonnet-5-5`, and 38 of 38 with and 4 of 21 without on `claude-opus-5-5` (Claude Code's readings of the files).

## Notices

**Disclaimer.** This software is provided "as is", without warranty of any kind. It offers wording and prompts to an AI model; it does not check the correctness of any analysis and does not replace statistical, scientific or ethical review. See [DISCLAIMER.md](DISCLAIMER.md).

**License.** Copyright 2026 Carlos Siordia. Licensed under the Apache License, Version 2.0 (the "License"); you may not use this software except in compliance with the License. You may obtain a copy of the License in [LICENSE](LICENSE) or at http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

**Privacy.** Use the skill with non-sensitive data only: whatever you share in a conversation goes to the Claude service under your own account's terms. The skill itself sends nothing anywhere.

**Contributing.** Contributions are welcome under the Apache License, Version 2.0. By submitting a contribution you agree that it is licensed under the same terms as the project (inbound = outbound). See [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Citation

See [CITATION.cff](CITATION.cff).
