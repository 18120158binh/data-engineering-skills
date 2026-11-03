---
name: principle-follow-the-common-shape
description: Apply when designing a component, choosing a tool, or reviewing a design that solves a problem other products have already solved. Look at how four to six established products solve it, from their own documentation, and write down the shape they share. Following it needs little argument; departing from it needs a requirement the common shape cannot meet.
metadata:
  version: "0.1"
---

# Follow the common shape

Before you design something, find out how established products already do it. Use the shape most of them share, unless a stated requirement rules it out.

**Why:** a new design tends to repeat mistakes that others have already paid for and fixed. A familiar shape is also cheaper to review, run, and hand over, because people already know how it fails.

**How:**

- Read four to six established products' own documentation, and keep the links.
- Write the shape they share in a few lines, and where they differ, with the reason each gives.
- If your design departs from the shared shape, name the requirement or the number that forces it.

**The test:**

1. Which products did you look at, with links?
2. What do most of them have in common?
3. Where the design departs from that, which requirement makes it necessary?

Related: `principle-analyze-trade-offs`.
