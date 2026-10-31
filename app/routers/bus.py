from fastapi import APIRouter, HTTPException, Query
import requests

from app.services.tdx_client import get_stops, search_routes

router = APIRouter(prefix="/cities", tags=["bus"])


@router.get("/{city}/routes")
def routes(city: str, q: str = Query(min_length=1)):
    try:
        return search_routes(city, q)
    except requests.RequestException:
        raise HTTPException(status_code=502, detail="無法取得 TDX 資料，請稍後再試")


@router.get("/{city}/routes/{route_name}/stops")
def stops(city: str, route_name: str, direction: int = Query(0, ge=0, le=1)):
    try:
        return get_stops(city, route_name, direction)
    except requests.RequestException:
        raise HTTPException(status_code=502, detail="無法取得 TDX 資料，請稍後再試")