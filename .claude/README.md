# Claude Code skills & agents for this repo

Claude Code loads everything here automatically when a session opens this repo.
All packs are MIT licensed (see `third-party-licenses/`).

| Source | Commit | Installed as |
|---|---|---|
| jherrodthomas/automotive-skills-suite | 1135289 | 152 skills (ISO 26262, ASPICE, 21434, UDS, A2L, ARXML, FMEA, 8D...) |
| zhinkgit/embeddedskills | 0e2fb63 | 12 skills: can, eide, gcc, jlink, keil, net, openocd, probe-rs, serial, ssh, terminal, workflow |
| AmethystLuna/embedded-workbench | 05b7709 | 8 skills + 4 agents. Its SessionStart hook was **not** installed. |
| CSS-Electronics/can-bus-reverse-engineering-skills | d357d6e | 3 skills: cansub-reverse-engineering, cansub-knowledge, combine-dbc |
| VoltAgent/awesome-claude-code-subagents | ed74d11 | 166 subagents in `agents/` |

hesreallyhim/awesome-claude-code is a reading list, not an installable pack:
https://github.com/hesreallyhim/awesome-claude-code

To update a pack, re-clone it and copy its skill folders over the ones here.
To trim the skill list, delete the folders you don't use from `skills/`.
