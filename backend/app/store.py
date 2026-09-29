"""内存数据仓库：给每个业务模块准备一份可筛选、可流转的示例数据。

真实项目里这里会换成数据库访问层；当前实现只依赖标准库，保证克隆下来就能起。
"""
from __future__ import annotations

from typing import Any

from app.modules import (
    MODULES,
    get_meta,
    is_abnormal,
    is_pending,
    issue_rows,
    sum_amount,
)
from app.seed import SEED_ROWS


class Store:
    def __init__(self) -> None:
        self._tables: dict[str, list[dict[str, Any]]] = {
            name: [dict(row) for row in rows] for name, rows in SEED_ROWS.items()
        }

    def module_names(self) -> list[str]:
        """按注册中心顺序返回已知模块，顺序与侧栏、首页保持一致。"""
        known = [key for key in (meta.key for meta in MODULES) if key in self._tables]
        known.extend(sorted(key for key in self._tables if key not in set(known)))
        return known

    def rows(self, module: str) -> list[dict[str, Any]]:
        return self._tables.setdefault(module, [])

    def find(self, module: str, entry_id: int) -> dict[str, Any] | None:
        for row in self.rows(module):
            if int(row.get("id", 0)) == entry_id:
                return row
        return None

    def module_summary(self, key: str) -> dict[str, object] | None:
        """单个模块的概览口径，也是进入后清单条数/金额的对账来源。

        某个模块的数据取不到（表损坏、字段异常）时返回 None，
        由调用方决定如何隔离，避免一个模块拖垮整行合计。
        """
        meta = get_meta(key)
        if meta is None:
            return None
        try:
            rows = self.rows(key)
            issues = issue_rows(rows, "all")
            pending = sum(1 for row in rows if is_pending(row))
            abnormal = sum(1 for row in rows if is_abnormal(row))
            return {
                "key": key,
                "name": meta.label,
                "created": len(rows),
                "pending": pending,
                "abnormal": abnormal,
                "issues": len(issues),
                "amount": sum_amount(issues, meta.amount_field),
            }
        except Exception:
            return None

    def module_issues(self, key: str, kind: str = "all") -> dict[str, object] | None:
        """进入某模块后看到的卡点清单；条数与金额与概览那一行同口径。

        取数失败时返回 None，由路由转成 503：前端只把这一个模块置为失败态，
        其它模块的并发请求与首页合计均不受影响。
        """
        meta = get_meta(key)
        if meta is None:
            return None
        try:
            rows = self.rows(key)
            matched = issue_rows(rows, kind)
            all_issues = issue_rows(rows, "all")
            return {
                "key": key,
                "name": meta.label,
                "kind": kind,
                "fields": meta.fields,
                "amountField": meta.amount_field,
                # 概览行对账用：始终是「未办结+出错」全集口径，不随 kind 变
                "issuesCount": len(all_issues),
                "issuesAmount": sum_amount(all_issues, meta.amount_field),
                "pendingCount": sum(1 for row in rows if is_pending(row)),
                "abnormalCount": sum(1 for row in rows if is_abnormal(row)),
                # 当前口径下的清单
                "total": len(matched),
                "amount": sum_amount(matched, meta.amount_field),
                "items": matched,
            }
        except Exception:
            return None

    def overview(self) -> dict[str, object]:
        modules: list[dict[str, object]] = []
        for key in self.module_names():
            summary = self.module_summary(key)
            if summary is not None:
                modules.append(summary)
        # 合计只累加取数成功的模块；失败模块不参与，也不影响其它行
        cards = [
            {"label": "业务模块", "value": len(modules)},
            {"label": "今日新增", "value": sum(int(item["created"]) for item in modules)},
            {"label": "待处理", "value": sum(int(item["pending"]) for item in modules)},
            {"label": "异常量", "value": sum(int(item["abnormal"]) for item in modules)},
        ]
        return {"cards": cards, "modules": modules}


store = Store()
