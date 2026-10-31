from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import NotificationLog, Subscription, User
from app.services.notifier import build_arrival_message, send_email
from app.services.tdx_client import get_eta

import logging

logger = logging.getLogger(__name__)

def should_notify(eta_item: dict, notify_minutes: int) -> bool:
    """這筆到站資料是否該觸發通知。"""
    if eta_item.get("StopStatus") != 0:
        return False
    eta = eta_item.get("EstimateTime")
    if eta is None:
        return False
    return 0 < eta <= notify_minutes * 60


def already_notified(db: Session, subscription_id: int, plate_numb: str) -> bool:
    cutoff = datetime.utcnow() - timedelta(minutes=30)
    log = db.scalar(
        select(NotificationLog).where(
            NotificationLog.subscription_id == subscription_id,
            NotificationLog.plate_numb == plate_numb,
            NotificationLog.notified_at >= cutoff,
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

def run_poll_once() -> None:
    """跑一輪：檢查所有啟用的訂閱，需要通知的就寄信並寫紀錄。"""
    db = SessionLocal()
    try:
        subs = db.scalars(
            select(Subscription).where(Subscription.is_active == True)  # noqa: E712
        ).all()

        for sub in subs:
            try:
                items = check_subscription(db, sub)
                user = db.get(User, sub.user_id)
                for item in items:
                    subject, body = build_arrival_message(
                        sub.route_name, sub.stop_name, item["EstimateTime"]
                    )
                    send_email(user.email, subject, body)
                    db.add(
                        NotificationLog(
                            subscription_id=sub.id,
                            plate_numb=item["PlateNumb"],
                        )
                    )
                    db.commit()
                    logger.info("已通知 %s：%s %s", user.email, sub.route_name, item["PlateNumb"])
            except Exception:
                db.rollback()
                logger.exception("處理訂閱 %s 時發生錯誤", sub.id)
    finally:
        db.close()