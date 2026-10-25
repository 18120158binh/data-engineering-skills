---
type: llm
focus: trace
weight: 1
---

plan.md adds CHECK (shipping_country IS NOT NULL) NOT VALID, then VALIDATE CONSTRAINT in a separate step, rather than SET NOT NULL directly on the full table.
