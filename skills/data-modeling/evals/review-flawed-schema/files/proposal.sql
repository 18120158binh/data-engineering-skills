-- Postgres: written by the Flink "rewards" job (at-least-once, can replay after restart)
CREATE TABLE reward_events (
  id          bigserial PRIMARY KEY,
  customer_id varchar NOT NULL,
  campaign_id varchar NOT NULL,
  reward_type varchar,            -- 'points' | 'voucher' | 'cashback'
  amount      numeric,
  happened_at timestamp,          -- local time of the shop
  created_at  timestamp DEFAULT now()
);

-- one row per campaign, every job subtask adds to it
CREATE TABLE campaign_reward_totals (
  campaign_id varchar PRIMARY KEY,
  total_amount numeric NOT NULL DEFAULT 0,
  reward_count bigint  NOT NULL DEFAULT 0
);
-- job runs: UPDATE campaign_reward_totals SET total_amount = total_amount + $1, reward_count = reward_count + 1 WHERE campaign_id = $2

-- ClickHouse copy for dashboards
CREATE TABLE analytics.reward_events (
  event_id      UUID,
  customer_id   Nullable(String),
  customer_name String,
  campaign_id   String,
  campaign_name String,
  reward_type   String,
  amount        Float64,
  happened_at   DateTime('Asia/Ho_Chi_Minh')
) ENGINE = MergeTree
PARTITION BY customer_id
ORDER BY (event_id, customer_id, happened_at);
