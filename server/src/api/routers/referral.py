from typing import List

from fastapi import APIRouter, Depends

from src.crud import get_referrals_by_referrer_id
from src.schemas import ReferralResponse

from src.api.dependencies.auth import get_current_user_id
from src.api.dependencies.core import DBSessionDep

referral_router = APIRouter(
    prefix="/referral",
    tags=["referral"],
    responses={404: {"description": "Not found"}},
)


@referral_router.get("/history")
async def get_referral_history(
    db: DBSessionDep,
    user_id: str = Depends(get_current_user_id),
) -> List[ReferralResponse]:
    referrals = await get_referrals_by_referrer_id(db, int(user_id))
    return [
        ReferralResponse(
            referredId=referral.referred_id,
            referredName=referral.referred_name,
            bonusAmount=referral.bonus_amount,
            status=referral.status.capitalize(),
            createdAt=referral.created_at,
        )
        for referral in referrals
    ]
