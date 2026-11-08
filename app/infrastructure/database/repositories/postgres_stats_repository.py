from app.domain.entities.system_info import SystemInfo
from app.domain.repositories.stats_repository import StatsRepository
from app.infrastructure.database.connection import get_connection

ORDER_STATUSES = ["PENDING", "CONFIRMED", "PROCESSING", "SHIPPED", "DELIVERED", "CANCELLED"]


class PostgresStatsRepository(StatsRepository):
    def get_system_info(self) -> SystemInfo:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT COUNT(*) FILTER (WHERE role = 'customer') AS customers,
                           COUNT(*) FILTER (WHERE role = 'admin') AS admins
                    FROM users
                    """
                )
                users = cur.fetchone()

                cur.execute(
                    """
                    SELECT COUNT(*) AS total,
                           COUNT(*) FILTER (WHERE is_active) AS active,
                           COUNT(*) FILTER (WHERE is_active AND stock <= 5) AS low_stock
                    FROM products
                    """
                )
                products = cur.fetchone()

                cur.execute("SELECT status, COUNT(*) AS n FROM orders GROUP BY status")
                by_status = {status: 0 for status in ORDER_STATUSES}
                for row in cur.fetchall():
                    by_status[row["status"]] = row["n"]

                cur.execute(
                    """
                    SELECT COALESCE(SUM(total_amount), 0) AS revenue
                    FROM orders
                    WHERE status IN ('CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED')
                    """
                )
                revenue = cur.fetchone()["revenue"]

                cur.execute(
                    "SELECT COUNT(*) AS n FROM payments WHERE status = 'UNDER_REVIEW'"
                )
                under_review = cur.fetchone()["n"]

                return SystemInfo(
                    total_customers=users["customers"],
                    total_admins=users["admins"],
                    total_products=products["total"],
                    active_products=products["active"],
                    low_stock_products=products["low_stock"],
                    total_orders=sum(by_status.values()),
                    orders_by_status=by_status,
                    payments_under_review=under_review,
                    total_revenue=revenue,
                )