---
name: database-upgrade
description: Upgrade a database to a new major version, or move it to another instance, following GitLab's upgrade and administration docs and the database vendor's upgrade documentation as references. Orders the work (plan in waves, test compatibility on every way the database is hosted, back up and prove the restore, finish background data jobs, freeze schema changes when logical replication is used, choose the method and its way back, run it, check after, operate migrations safely during the window, hand production to a person) and points the agent to the page to read at each step. Use it for PostgreSQL major upgrades, managed database version changes, moving a database to a new host, and ClickHouse or operator upgrades, even if the user only says "upgrade Postgres", "move the database", or "bump the database version".
metadata:
  version: "0.1"
---

# Database upgrade

This skill orders the work of a major upgrade or a move. The procedures come from GitLab's upgrade and administration documentation and from the database vendor's own documentation, which are the references for this skill. Read the pages each step names, and cite them in the hand-back.

## Where this fits

| You need | Skill |
|---|---|
| Move data into a different store or shape | `data-migration` |
| Move a pipeline onto the upgraded engine, running old and new side by side | `pipeline-migration` |
| Schema changes the new version needs | `schema-change` |

## Steps

Open a todo list with one entry per step.

### 1. Plan

Write a dated plan with an owner for each phase, the waves (staging before production, a few databases before the rest), what must be true before each wave starts, and how users are told.

Read: [Timeline for version upgrades](https://docs.gitlab.com/development/database/pg_upgrade_timeline/).

### 2. Test compatibility

Run the application's tests against the new version, test the upgrade on every way the database is hosted, and read the vendor's release notes for every version you cross. Some operators and tools must be upgraded one version at a time; check their documentation.

Read: the vendor's release notes, such as the [PostgreSQL release notes](https://www.postgresql.org/docs/release/), and [Timeline for version upgrades](https://docs.gitlab.com/development/database/pg_upgrade_timeline/).

### 3. Prepare

- **Back up, and prove the backup by restoring it.** Replication is not a backup.
- **Finish background data jobs**, with a check that fails the upgrade if any are unfinished. Read [Check for background migrations before upgrading](https://docs.gitlab.com/update/background_migrations/).
- **Freeze schema changes** when the upgrade or move uses logical replication. Read [Database upgrade DDL lock](https://docs.gitlab.com/development/database/database_upgrade_ddl_lock/).

### 4. Choose the method

Write down the method, its expected downtime, its way back, and the point after which there is no way back.

| Method | Read |
|---|---|
| In place, on a replicated cluster | [Replication and failover](https://docs.gitlab.com/administration/postgresql/replication_and_failover/), the section on upgrading the major version, and the PostgreSQL [pg_upgrade](https://www.postgresql.org/docs/current/pgupgrade.html) documentation |
| A new cluster fed by logical replication, then a switch | The same page, the section on a near-zero-downtime upgrade, and the PostgreSQL [logical replication](https://www.postgresql.org/docs/current/logical-replication.html) documentation |
| Dump and restore to another instance | [Moving GitLab databases to a different PostgreSQL instance](https://docs.gitlab.com/administration/postgresql/moving/) |

### 5. Run it

Follow the procedure for the chosen method, step by step, with a check after each step and the rollback order written down before you start.

### 6. Check after the upgrade

Check planner statistics, extensions, client tool versions, replicas and replication slots, and the first backup and its restore. The [pg_upgrade](https://www.postgresql.org/docs/current/pgupgrade.html) documentation lists what the upgrade does not carry over. Re-check objects that were created by hand.

### 7. Operate migrations during the window

Run migrations, backups, and restores against the primary directly, from one node, and watch replica lag and read-after-write behavior.

Read: [Working with the bundled PgBouncer service](https://docs.gitlab.com/administration/postgresql/pgbouncer/), [Load balancing](https://docs.gitlab.com/development/database/load_balancing/), [Troubleshooting PostgreSQL](https://docs.gitlab.com/administration/troubleshooting/postgresql/), and [Maintenance operations](https://docs.gitlab.com/development/database/maintenance_operations/).

### 8. ClickHouse and operators

Read the release notes for settings that were removed or changed, upgrade replicas one at a time, and check that each has caught up before the next. The owner's team has seen an operator hang on one abandoned read-only table while waiting for replication delay to drop, so look for such tables before you start.

### 9. Hand production to a person

An agent does not upgrade production. It hands over the plan, the test results, and the exact commands for each step, including rollback.

## Hand back

1. The plan: phases, owners, waves, and the method with its downtime and way back.
2. The compatibility results for each way the database is hosted.
3. The backup and its restore test, and the background job check.
4. The runbook: each step, its check, and the rollback order.
5. The checks after the upgrade, and their results.
6. The pages followed, and what was not checked.
