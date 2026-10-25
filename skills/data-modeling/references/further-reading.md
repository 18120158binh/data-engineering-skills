# Further reading

GitLab's database development guidelines cover table design topics that this skill does not. They are GitLab's practice, not the owner's rules. Read the page that matches your design question, and where a page disagrees with [SKILL.md](../SKILL.md), SKILL.md wins.

| Design question | GitLab page |
|---|---|
| Text columns and length limits | [Strings and the text data type](https://docs.gitlab.com/development/database/strings_and_the_text_data_type/) |
| Storing hashes | [Storing SHA1 hashes as binary](https://docs.gitlab.com/development/database/sha1_as_binary/) |
| Foreign keys, cascades, and their indexes | [Foreign keys and associations](https://docs.gitlab.com/development/database/foreign_keys/) |
| Column order and row size | [Ordering table columns](https://docs.gitlab.com/development/database/ordering_table_columns/) |
| Enums | [Creating enums](https://docs.gitlab.com/development/database/creating_enums/) |
| Serialized data in columns | [Serializing data](https://docs.gitlab.com/development/database/serializing_data/) |
| Polymorphic references | [Polymorphic associations](https://docs.gitlab.com/development/database/polymorphic_associations/) |
| One table for several types | [Single table inheritance](https://docs.gitlab.com/development/database/single_table_inheritance/) |
| Wide tables, hot rows, and index counts | [Data layout and access patterns](https://docs.gitlab.com/development/database/layout_and_access_patterns/) |
| Keeping derived counters out of hot transactions | [Namespaces storage statistics](https://docs.gitlab.com/development/database/namespaces_storage_statistics/) (case study) |
| Which store to use | [Datastore guidance](https://docs.gitlab.com/development/database/datastore_guidance/) |
| Retention and table size limits | [Data retention policy](https://docs.gitlab.com/development/database/database_growth_control/data_retention_policy/) and [Time-decay data](https://docs.gitlab.com/development/database/scalability/patterns/time_decay/) |
| Partitioning | [Partitioning](https://docs.gitlab.com/development/database/partitioning/) |
| ClickHouse tables copied from PostgreSQL | [Table design with Siphon](https://docs.gitlab.com/development/database/clickhouse/clickhouse_table_design_with_siphon/) |
| ClickHouse table design for analytics | [Activity data](https://docs.gitlab.com/development/database/clickhouse/gitlab_activity_data/) and [Merge request analytics](https://docs.gitlab.com/development/database/clickhouse/merge_request_analytics/) (case studies) |
