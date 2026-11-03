# principles

Each folder here holds one principle: a single rule that more than one skill relies on. Workflow skills cite a principle by name instead of repeating it, so each rule is written once.

## How a principle works

```mermaid
flowchart TD
    A["A task or a review"] --> B["A workflow skill runs"]
    B --> C["A step cites a principle by name"]
    C --> D["The agent opens that principle"]
    D --> E["Applies the rule"]
    E --> F{"The test question:<br/>does the work pass?"}
    F -->|yes| G["Next step"]
    F -->|no| H["Fix the work, or record why not"]
    H --> F
```

An agent can also load a principle on its own when the task matches its description, without any workflow.

## What a principle holds

- **The rule**, in one or two sentences.
- **Why**: the failure the rule prevents.
- **The test**: questions a reviewer can answer from the work.
- **An example**, with numbers marked as illustrative when they are.
- **Read**: links to outside documentation, when the rule rests on it.

## When a rule becomes a principle

`principle-extract-shared-rules` decides it: two or more skills need the rule, it makes sense on its own, and it does not depend on one workflow's order or tools. A rule used by one step of one workflow stays in that workflow.

## Tests

Principles have no evals of their own. The eval cases of the workflow skills that cite them check whether the rule changes behavior.
