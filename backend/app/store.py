"""内存数据仓库：给每个业务模块准备一份可筛选、可流转的示例数据。

真实项目里这里会换成数据库访问层；当前实现只依赖标准库，保证克隆下来就能起。
"""
from __future__ import annotations

from typing import Any

from app.modules import MODULE_AMOUNT_FIELDS, MODULE_LABELS
from app.seed import SEED_ROWS


def is_blocked(row: dict[str, Any]) -> bool:
    """未办结或出错的条目都算「卡住」，清单页只列这部分。"""
    return bool(row.get("pending")) or bool(row.get("abnormal"))


def row_amount(module: str, row: dict[str, Any]) -> float:
    """取该模块约定的金额字段；无金额口径或值非法时按 0 计。"""
    field = MODULE_AMOUNT_FIELDS.get(module)
    if field is None:
        return 0.0
    try:
        return float(row.get(field) or 0.0)
    except (TypeError, ValueError):
        return 0.0


class Store:
    def __init__(self) -> None:
        self._tables: dict[str, list[dict[str, Any]]] = {
            name: [dict(row) for row in rows] for name, rows in SEED_ROWS.items()
        }

    def module_names(self) -> list[str]:
        return sorted(self._tables)

    def has_module(self, module: str) -> bool:
        return module in self._tables

    def label(self, module: str) -> str:
        return MODULE_LABELS.get(module, module)

    def amount_field(self, module: str) -> str | None:
        return MODULE_AMOUNT_FIELDS.get(module)

    def blocked_rows(self, module: str) -> list[dict[str, Any]]:
        """单个模块下尚未办结或出错的条目；供清单页逐模块独立取数。"""
        return [row for row in self.rows(module) if is_blocked(row)]

    def blocked_stats(self, module: str, rows: list[dict[str, Any]] | None = None) -> dict[str, float]:
        """统计一个模块卡住条目的条数与金额，首页与清单页共用同一口径。"""
        if rows is None:
            rows = self.blocked_rows(module)
        return {
            "pending": float(sum(1 for row in rows if row.get("pending"))),
            "abnormal": float(sum(1 for row in rows if row.get("abnormal"))),
            "amount": round(sum(row_amount(module, row) for row in rows), 2),
        }

    def rows(self, module: str) -> list[dict[str, Any]]:
        return self._tables.setdefault(module, [])

    def find(self, module: str, entry_id: int) -> dict[str, Any] | None:
        for row in self.rows(module):
            if int(row.get("id", 0)) == entry_id:
                return row
        return None

    def overview(self) -> dict[str, object]:
        modules: list[dict[str, object]] = []
        for name in self.module_names():
            rows = self.rows(name)
            blocked = [row for row in rows if is_blocked(row)]
            stats = self.blocked_stats(name, blocked)
            modules.append({
                "name": name,
                "label": self.label(name),
                "created": len(rows),
                "pending": int(stats["pending"]),
                "abnormal": int(stats["abnormal"]),
                "blocked": len(blocked),
                "amount": stats["amount"],
                "amountField": self.amount_field(name),
            })
        cards = [
            {"label": "业务模块", "value": len(modules)},
            {"label": "今日新增", "value": sum(int(item["created"]) for item in modules)},
            {"label": "待处理", "value": sum(int(item["pending"]) for item in modules)},
            {"label": "异常量", "value": sum(int(item["abnormal"]) for item in modules)},
        ]
        return {"cards": cards, "modules": modules}


store = Store()
