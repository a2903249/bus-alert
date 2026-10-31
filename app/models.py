from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    city: Mapped[str] = mapped_column(String(50))
    route_name: Mapped[str] = mapped_column(String(100))
    route_uid: Mapped[str] = mapped_column(String(50))
    direction: Mapped[int] = mapped_column(Integer)          # 0 去程、1 返程
    stop_uid: Mapped[str] = mapped_column(String(50))
    stop_name: Mapped[str] = mapped_column(String(100))
    notify_minutes: Mapped[int] = mapped_column(Integer, default=5)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class NotificationLog(Base):
    __tablename__ = "notification_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    subscription_id: Mapped[int] = mapped_column(ForeignKey("subscriptions.id"))
    plate_numb: Mapped[str] = mapped_column(String(20))
    notified_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)