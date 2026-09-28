"""业务模块元数据：首页看板与未办结清单共用的模块中文名、金额口径。

键名与 store 里的表名（即 /api/{module} 的路径段）保持一致；
只有带金额字段的协议、结算两个模块登记金额字段，其他模块金额按 0 汇总。
"""
from __future__ import annotations

# 模块键 -> 首页/清单展示用的中文名
MODULE_LABELS: dict[str, str] = {
    "flight": "航班计划",
    "stand": "机位资源",
    "apron": "机坪巡查",
    "bridge": "廊桥对接",
    "deicing": "除冰作业",
    "fueling": "航油加注",
    "baggage": "行李装卸",
    "cargo": "货邮装载",
    "catering": "航空配餐",
    "shuttle": "摆渡接送",
    "towing": "航空器牵引",
    "loadsheet": "载重平衡",
    "permit": "通行证件",
    "gse": "保障车辆",
    "safety": "安全监察",
    "agreement": "保障协议",
    "settlement": "保障结算",
    "training": "资质培训",
}

# 模块键 -> 该模块条目的金额字段（无金额字段的模块不在此登记）
MODULE_AMOUNT_FIELDS: dict[str, str] = {
    "agreement": "协议金额",
    "settlement": "应付金额",
}
