# Third-party works

This repository is MIT licensed (see [LICENSE](LICENSE)). It contains no code or text copied from the projects below. The skills name them, link to them, or adapt an idea from them, and credit each one where it is used.

## Projects the skills build on

| Project | Author | License | Used in | How |
|---|---|---|---|---|
| [Superpowers](https://github.com/obra/superpowers) | Jesse Vincent | MIT | `engineering-lead` | Named as a default provider of engineering method (brainstorming, planning, test-first, debugging, verification, review). The skill tells the agent to open and follow the installed Superpowers skills, and does not restate them. |
| [pstack](https://github.com/cursor/plugins/tree/main/pstack) (mirror: [backnotprop/pstack](https://github.com/backnotprop/pstack)) | Lauren Tan | MIT | `engineering-lead`, `pipeline-review`, `database-optimization` | `engineering-lead` names it as a default provider of investigation, execution playbooks, and orchestration. `pipeline-review` adapts the ladder of proof from its `blast-radius` skill. `database-optimization` follows the ideas of its explain-the-number and prove-it-works principles. All wording is our own. |
| [rea](https://github.com/morluto/rea) (`reverse-engineer-anything`) | morluto | MIT | `engineering-lead` | The idea that each conclusion carries its evidence, how sure it is, and what is still unresolved, used in the decision trail. |

Superpowers and pstack are not bundled. Install them separately to use the parts of `engineering-lead` that rely on them; their own licenses apply to them.

## Formats and documentation

- The skills follow the [Agent Skills specification](https://agentskills.io/specification) for their folder layout and frontmatter.
- Several skills and principles link to vendor documentation, such as GitLab, PostgreSQL, Apache Flink, and Apache Kafka, for the reader to consult. Those pages are linked, not reproduced, and remain under their owners' terms.

## Reporting an issue

If you believe something here is used without proper credit or permission, open an issue and it will be corrected.
