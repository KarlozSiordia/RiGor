# Contributing

Thank you for considering a contribution.

## License of contributions

This project is licensed under the [Apache License, Version 2.0](LICENSE). Under section 5 of the License, any contribution you intentionally submit for inclusion in the project is licensed under the same terms, without additional terms or conditions (inbound = outbound). Submit only work you have the right to license this way.

## How to contribute

1. For anything larger than a typo, open an issue first that describes the problem or the proposal.
2. Fork the repository and create a branch.
3. Make the change. Keep `SKILL.md` within the project's 150-line cap, and keep its frontmatter to the Agent Skills spec fields (`name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`) so the skill still uploads to Claude.ai.
4. Check it: `claude plugin validate .` and `python scripts/package_skill.py` (checks only; it writes nothing without `--write`).
5. If the change touches skill text, describe in the pull request what changed, why, and what was checked.
6. Open a pull request that describes the change and how you checked it.

## What not to include

- Sensitive or identifiable data, in issues, pull requests, examples or tests.
- Text that turns the skill into an enforcement tool. It helps the analyst and keeps no record of decisions or conduct.

## Code of conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md).
