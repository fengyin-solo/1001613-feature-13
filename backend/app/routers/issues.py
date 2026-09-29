"""卡点清单接口：从运营首页进入某个业务模块后，看它到底卡在哪。

每个模块独立请求、独立成败：前端对 18 个模块分别调用本接口，
某个模块返回失败时只有那一行进入失败态并可重新加载，其它行照常展示。
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.modules import MODULES
from app.store import store

router = APIRouter(prefix="/api/modules", tags=["运营卡点"])

ISSUE_KINDS = ("all", "pending", "abnormal")


@router.get("")
def list_modules() -> dict[str, object]:
    """登记在册的业务模块清单（别名与中文名），供前端按固定顺序逐行取数。"""
    return {"modules": [{"key": meta.key, "name": meta.label} for meta in MODULES]}


@router.get("/{module_key}/issues")
def module_issues(
    module_key: str,
    kind: str = Query(default="all", description="all 未办结+出错、pending 仅未办结、abnormal 仅出错"),
) -> dict[str, object]:
    """单个模块的卡点条目；不存在的模块返回 404，由前端只标记这一行为失败。"""
    if not any(meta.key == module_key for meta in MODULES):
        raise HTTPException(status_code=404, detail=f"业务模块 {module_key} 不存在")
    if kind not in ISSUE_KINDS:
        raise HTTPException(status_code=400, detail="kind 只支持 all、pending、abnormal")
    payload = store.module_issues(module_key, kind)
    if payload is None:
        raise HTTPException(status_code=503, detail=f"{module_key} 模块数据暂不可用，请稍后重试")
    return payload
