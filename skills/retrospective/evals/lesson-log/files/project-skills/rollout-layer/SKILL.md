---
name: rollout-layer
description: Roll one layer of the orders-stream staging environment out (cloud base, images, nodes, platform, data, Flink jobs, apps) and check it before the next layer.
---

# Roll out one layer

1. Name the layer and its check.
2. Commit the layer's manifests to the environment overlay as their own commit.
3. Wait for Argo CD to report the layer Synced and Healthy.
4. Run the layer's check and report the result before starting the next layer.
5. Pause for the owner's yes before any layer that creates billable resources.
