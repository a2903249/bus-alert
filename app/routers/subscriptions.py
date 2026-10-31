from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Subscription, User
from app.schemas import SubscriptionCreate, SubscriptionOut

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.post("", response_model=SubscriptionOut, status_code=status.HTTP_201_CREATED)
def create_subscription(
    data: SubscriptionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    sub = Subscription(user_id=user.id, **data.model_dump())
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub


@router.get("", response_model=list[SubscriptionOut])
def list_subscriptions(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return db.scalars(
        select(Subscription).where(Subscription.user_id == user.id)
    ).all()


@router.delete("/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subscription(
    subscription_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    sub = db.get(Subscription, subscription_id)
    if sub is None or sub.user_id != user.id:
        raise HTTPException(status_code=404, detail="找不到此訂閱")
    db.delete(sub)
    db.commit()