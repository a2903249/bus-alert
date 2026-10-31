from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import NotificationLog, Subscription
from app.services.tdx_client import get_eta


def should_notify(eta_item: dict, notify_minutes: int) -> bool:
    """這筆到站資料是否該觸發通知。"""
    if eta_item.get("StopStatus") != 0:
        return False
    eta = eta_item.get("EstimateTime")
    if eta is None:
        return False
    return 0 < eta <= notify_minutes * 60


def already_notified(db: Session, subscription_id: int, plate_numb: str) -> bool:
    log = db.scalar(
        select(NotificationLog).where(
            NotificationLog.subscription_id == subscription_id,
            NotificationLog.plate_numb == plate_numb,
        )
    )
    return log is not None


def check_subscription(db: Session, sub: Subscription) -> list[dict]:
    """檢查單一訂閱，回傳『需要通知』的到站資料（尚未寄信）。"""
    items = get_eta(sub.city, sub.route_name, sub.direction, sub.stop_uid)
    result = []
    for item in items:
        plate = item.get("PlateNumb")
        if not plate or plate == "-1":
            continue
        if should_notify(item, sub.notify_minutes) and not already_notified(db, sub.id, plate):
            result.append(item)
    return result