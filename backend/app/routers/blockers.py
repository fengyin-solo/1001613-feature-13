"""未办结/异常清单接口：按模块独立取数，单个模块失败不牵连其他模块。

前端清单页对每个模块各发一次请求并独立处理失败行；simulate_fail 只用于联调与验收
（模拟某个模块数据源取数失败），生产不传即可。
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from app.store import row_amount, store

router = APIRouter(prefix="/api/blockers", tags=["未办结清单"])


@router.get("/{module}")
def list_blockers(
    module: str,
    simulate_fail: bool = Query(default=False, description="联调用：置 true 时该模块返回取数失败"),
) -> dict[str, Any]:
    """返回单个模块尚未办结或出错的条目，并附上条数与金额（口径同首页该行）。"""
    if not store.has_module(module):
        raise HTTPException(status_code=404, detail=f"业务模块「{module}」不存在")
    if simulate_fail:
        raise HTTPException(status_code=503, detail=f"{store.label(module)}数据暂时取不到，请稍后重试")

    rows = store.blocked_rows(module)
    amount_field = store.amount_field(module)
    items: list[dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        item["amount"] = row_amount(module, row)
        items.append(item)
    return {
        "module": module,
        "label": store.label(module),
        "total": len(items),
        "pending": sum(1 for row in rows if row.get("pending")),
        "abnormal": sum(1 for row in rows if row.get("abnormal")),
        "amount": round(sum(row_amount(module, row) for row in rows), 2),
        "amountField": amount_field,
        "items": items,
    }
