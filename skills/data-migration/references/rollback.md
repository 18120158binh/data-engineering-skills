# The way back

## Backups

- **Take a backup before the first change, and prove it by restoring it.** A backup job that runs is not a backup: backup jobs can fail silently for months, and only a restore shows it.
- Keep a dump only when its listing shows one data entry for each source table.
- Run restore drills into a throwaway database. Write down how long a restore takes, because that time is part of the outage you would face.
- A deploy refuses to run a migration without a verified backup.
- Some stores restore snapshots only into the same or a newer version. Check before relying on a snapshot across an upgrade, and copy through the API when the snapshot cannot cross.

## Reverse steps

- **Write the reverse SQL next to each forward step**, with the order and the precondition for running it. For example, put a default back before you roll back the application that relies on it.
- **No schema rollback is automatic.** A person runs it, in the written order.
- **Keep the old object under a new name** instead of dropping it, for example `orders_before_view`. You can then diff old against new, and roll back by renaming.
- **Keep the running image or build tagged as the rollback**, at the exact digest that runs now.

## No automatic rollback onto migrated data

- Turn off any automatic rollback, such as a deploy that reverts the image when a smoke test fails, once a migration has run. Reverting puts the old code on the new schema.
- Prefer fixing forward once migrated data has taken new writes.

## Point of no return

Name it before you start, and time-box it. For example:

- **Within about an hour, with few new writes:** stop the application, swap the restored copy in as live, and roll back the code.
- **After that:** fix forward, because a restore would lose the writes made since.

For change data capture, the point of no return is where the replication log no longer holds every change since the savepoint or backup you would roll back to. Know that window as a number, for example the number of checkpoints the slot keeps.

## Rollback for stream state

A rollback works only if the old version can read the state the new version wrote. Prove that in both directions before you call a state change safe. See [stream-state.md](stream-state.md).
