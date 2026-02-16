# app/routes/ui.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_
from datetime import datetime, timedelta

from app.db.database import get_db
from app.db.models import ScanResult
from app.schemas.scan import ScanStatus

router = APIRouter(include_in_schema=False)

# ==================== UI API ROUTES (AJAX) ====================
# HTML routes have been removed to prioritize the React frontend.

@router.get("/ui/api/dashboard-stats")
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """
    Get aggregated stats for the dashboard.
    """
    
    # Total Scans
    count_query = select(func.count()).select_from(ScanResult)
    count_res = await db.execute(count_query)
    total_scans = count_res.scalar() or 0
    
    # Running Scans
    running_query = select(func.count()).select_from(ScanResult).where(ScanResult.status == ScanStatus.RUNNING.value)
    running_res = await db.execute(running_query)
    running_scans = running_res.scalar() or 0
    
    # Average Risk Score
    avg_query = select(func.avg(ScanResult.risk_score)).select_from(ScanResult)
    avg_res = await db.execute(avg_query)
    avg_risk = avg_res.scalar() or 0.0
    
    # Critical Findings Scans (Risk >= 9.0)
    critical_query = select(func.count()).select_from(ScanResult).where(ScanResult.risk_score >= 9.0)
    critical_res = await db.execute(critical_query)
    critical_scans = critical_res.scalar() or 0
    
    # Recent Scans (Last 5)
    recent_query = select(ScanResult).order_by(desc(ScanResult.created_at)).limit(5)
    recent_res = await db.execute(recent_query)
    recent_scans = recent_res.scalars().all()
    
    # Severity Distribution (Across all scans - approximated by risk score buckets for speed)
    # Ideally this would be aggregated from JSON results, but doing that in DB is complex across backends.
    # We will approximate distribution based on risk scores of scans for the dashboard overview.
    # Or fetch recent 100 scans and aggregate their JSON summaries in Python.
    
    # Let's aggregate JSON summaries from last 50 completed scans for accuracy
    dist_query = select(ScanResult.result).where(
        ScanResult.status == ScanStatus.COMPLETED.value
    ).order_by(desc(ScanResult.created_at)).limit(50)
    dist_res = await db.execute(dist_query)
    scan_results = dist_res.scalars().all()
    
    severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    
    for res in scan_results:
        if res and isinstance(res, dict):
            summary = res.get("summary", {}).get("severity_distribution", {})
            for k, v in summary.items():
                if k.lower() in severity_counts:
                    severity_counts[k.lower()] += v
                    
    # Risk Trend (Last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    trend_query = select(ScanResult.created_at, ScanResult.risk_score).where(
        ScanResult.created_at >= thirty_days_ago
    ).order_by(ScanResult.created_at)
    trend_res = await db.execute(trend_query)
    trend_data = trend_res.all()
    
    # Resample to daily averages for trend chart
    daily_risks = {}
    for date, score in trend_data:
        day_str = date.strftime("%Y-%m-%d")
        if day_str not in daily_risks:
            daily_risks[day_str] = []
        daily_risks[day_str].append(score)
        
    risk_history = [
        {"date": day, "risk_score": sum(scores) / len(scores)}
        for day, scores in daily_risks.items()
    ]
    
    return {
        "total_scans": total_scans,
        "running_scans": running_scans,
        "avg_risk": float(avg_risk),
        "critical_findings": critical_scans, # Using high risk scans as proxy for dashboard card
        "severity_distribution": severity_counts,
        "risk_history": risk_history,
        "recent_scans": [
            {
                "scan_id": s.scan_id,
                "target": s.target,
                "status": s.status,
                "risk_score": s.risk_score,
                "created_at": s.created_at
            }
            for s in recent_scans
        ]
    }
