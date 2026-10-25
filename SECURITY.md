# Security policy

## Reporting a problem

Report a security problem privately, by email to csiordia@gmail.com, not in a public issue. Say what you found, in which file and version, and how to reproduce it.

## Supported versions

Only release 1.0.x is supported.

## Scope

The project contains:

- `skills/research-integrity-statistics/SKILL.md`: instruction text for an AI model;
- `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`: two JSON manifests that let Claude Code install the plugin;
- `.claude-plugin/icon.png`: the plugin's icon;
- `scripts/package_skill.py`: one Python packaging script that builds the upload zip. It runs only when a user runs it.

It runs no service, makes no network calls and collects no data. A problem in Claude or Claude Code themselves is outside this project.
