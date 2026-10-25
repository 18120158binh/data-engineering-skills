-- ClickHouse target for orders replicated from each source database
CREATE TABLE warehouse.orders_raw ON CLUSTER '{cluster}'
(
    source_id        LowCardinality(String),
    merchant_id      UInt64,
    order_id         UInt64,
    created_at       DateTime64(3, 'UTC'),
    updated_at       DateTime64(3, 'UTC'),
    amount_cents     UInt32
)
ENGINE = ReplicatedReplacingMergeTree
PARTITION BY toYYYYMM(created_at)
ORDER BY (source_id, merchant_id, created_at, order_id)
TTL created_at + toIntervalMonth(3)
SETTINGS ttl_only_drop_parts = 1;
