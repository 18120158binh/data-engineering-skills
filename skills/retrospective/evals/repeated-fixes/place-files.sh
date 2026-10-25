#!/usr/bin/env bash
# Builds a small pipeline repo whose history holds three fixes that share one wrong premise.
set -eu

git init -q -b main .
git config user.name "Data Engineer"
git config user.email "engineer@example.com"

commit() {
  GIT_AUTHOR_DATE="$1" GIT_COMMITTER_DATE="$1" git commit -q -m "$2"
}

mkdir -p dags tests
cat > AGENTS.md <<'EOF'
# AGENTS.md

Airflow DAGs that load orders into the warehouse. Run `python3 -m unittest discover -s tests` before you commit.
EOF
cat > dags/orders_daily.py <<'EOF'
from pendulum import now


def load_window():
    day = now().subtract(days=1).to_date_string()
    return f"SELECT * FROM orders WHERE order_date = '{day}'"
EOF
git add -A && commit "2026-09-01T09:00:00" "feat(orders): load yesterday's orders every day"

cat > dags/orders_daily.py <<'EOF'
from pendulum import now


def load_window():
    day = now("Africa/Johannesburg").subtract(days=1).to_date_string()
    return f"SELECT * FROM orders WHERE order_date = '{day}'"
EOF
git add -A && commit "2026-09-09T08:30:00" "fix(orders): use local time, the run at 00:30 SAST loaded the wrong day"

cat > dags/orders_monthly.py <<'EOF'
def load_month(ds):
    month = ds[:7].replace("-", "")
    return f"INSERT INTO orders_monthly SELECT * FROM orders_{month}"
EOF
git add -A && commit "2026-09-15T10:00:00" "feat(orders): monthly rollup from the month table"

cat > dags/orders_monthly.py <<'EOF'
def load_month(ds, data_interval_end):
    month = data_interval_end.in_timezone("Africa/Johannesburg").subtract(months=1).format("YYYYMM")
    return f"INSERT INTO orders_monthly SELECT * FROM orders_{month}"
EOF
git add -A && commit "2026-10-02T07:45:00" "fix(orders): monthly run at local midnight read the month before last, ds is UTC"

cat > dags/orders_daily.py <<'EOF'
from pendulum import now


def load_window(data_interval_end=None):
    anchor = data_interval_end or now("Africa/Johannesburg")
    day = anchor.in_timezone("Africa/Johannesburg").subtract(days=1).to_date_string()
    return f"SELECT * FROM orders WHERE order_date = '{day}'"
EOF
git add -A && commit "2026-10-12T11:20:00" "fix(orders): a retried run at 03:00 loaded today instead of yesterday"

cat > tests/test_orders.py <<'EOF'
import unittest


class OrdersTest(unittest.TestCase):
    def test_query_mentions_orders(self):
        from dags.orders_daily import load_window

        self.assertIn("orders", load_window())
EOF
git add -A && commit "2026-10-12T11:40:00" "test(orders): add a test for the daily query"
