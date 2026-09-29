"""业务模块元数据：模块别名、中文名、清单字段与金额字段的统一口径。

概览汇总、卡点清单接口和前端跳转都依赖这里的注册信息，
保证「首页那一行」与「进入后的清单」用的是同一套名称与字段。
顺序即首页概览与侧栏的展示顺序，新增模块时在末尾登记即可。
"""
from __future__ import annotations

from typing import NamedTuple


class ModuleMeta(NamedTuple):
    key: str           # 接口前缀 / 数据表名，如 flight
    label: str         # 中文模块名，与侧栏、首页一致
    fields: list[str]  # 清单页展示字段
    amount_field: str | None = None  # 需要统计金额时取的字段；无金额业务为 None


MODULES: list[ModuleMeta] = [
    ModuleMeta("flight", "航班计划", ["航班号", "执行日期", "机型", "起降性质", "计划时刻", "预计时刻", "保障等级", "航班状态"]),
    ModuleMeta("stand", "机位资源", ["机位编号", "机位类别", "所属区域", "适用机型", "廊桥配置", "加注接口", "保障能力", "机位状态"]),
    ModuleMeta("apron", "机坪巡查", ["巡查单号", "巡查区域", "巡查人员", "巡查日期", "巡查项目", "发现问题数", "巡查时长", "巡查状态"]),
    ModuleMeta("bridge", "廊桥对接", ["对接单号", "关联航班", "廊桥编号", "对接时刻", "撤桥时刻", "操作人员", "对接结果", "对接状态"]),
    ModuleMeta("deicing", "除冰作业", ["除冰单号", "关联航班", "除冰方式", "除冰液用量", "作业车辆", "作业人员", "完成时刻", "除冰状态"]),
    ModuleMeta("fueling", "航油加注", ["加注单号", "关联航班", "加注车号", "加注油量", "油品规格", "加注人员", "完成时刻", "加注状态"]),
    ModuleMeta("baggage", "行李装卸", ["装卸单号", "关联航班", "行李件数", "装卸车辆", "作业班组", "开始时刻", "完成时刻", "装卸状态"]),
    ModuleMeta("cargo", "货邮装载", ["装载单号", "关联航班", "货邮重量", "装载位置", "装载车辆", "作业人员", "完成时刻", "装载状态"]),
    ModuleMeta("catering", "航空配餐", ["配餐单号", "关联航班", "餐食份数", "餐食类别", "配餐车辆", "送达时刻", "接收人员", "配餐状态"]),
    ModuleMeta("shuttle", "摆渡接送", ["任务编号", "关联航班", "车辆编号", "乘客人数", "出发时刻", "到达时刻", "驾驶人员", "摆渡状态"]),
    ModuleMeta("towing", "航空器牵引", ["牵引编号", "关联航班", "牵引车号", "起点机位", "终点机位", "牵引人员", "完成时刻", "牵引状态"]),
    ModuleMeta("loadsheet", "载重平衡", ["配载单号", "关联航班", "计算重量", "重心位置", "油量数据", "配载人员", "复核人员", "配载状态"]),
    ModuleMeta("permit", "通行证件", ["证件编号", "持证人员", "所属单位", "通行区域", "有效期至", "发证人员", "发证日期", "证件状态"]),
    ModuleMeta("gse", "保障车辆", ["车辆编号", "车辆类别", "适用作业", "停放区域", "上次保养日", "下次保养日", "责任人", "车辆状态"]),
    ModuleMeta("safety", "安全监察", ["监察编号", "监察区域", "监察事项", "违规情形", "涉及单位", "监察人员", "监察日期", "监察状态"]),
    ModuleMeta("agreement", "保障协议", ["协议编号", "服务单位", "保障项目", "协议金额", "服务期限", "签订人员", "到期日期", "协议状态"], amount_field="协议金额"),
    ModuleMeta("settlement", "保障结算", ["结算单号", "关联协议", "结算周期", "应付金额", "已付金额", "审核人员", "付款日期", "结算状态"], amount_field="应付金额"),
    ModuleMeta("training", "资质培训", ["培训编号", "培训主题", "培训对象", "授课人员", "培训课时", "考核成绩", "培训日期", "培训状态"]),
]

MODULE_KEYS: list[str] = [meta.key for meta in MODULES]
MODULE_LABELS: dict[str, str] = {meta.key: meta.label for meta in MODULES}
_MODULE_META: dict[str, ModuleMeta] = {meta.key: meta for meta in MODULES}


def get_meta(key: str) -> ModuleMeta | None:
    return _MODULE_META.get(key)


def is_pending(row: dict) -> bool:
    """尚未办结：以 pending 标记为准。"""
    return bool(row.get("pending"))


def is_abnormal(row: dict) -> bool:
    """出错条目：以 abnormal 标记为准。"""
    return bool(row.get("abnormal"))


def is_issue(row: dict) -> bool:
    """卡点 = 尚未办结或出错（同一条目两者都命中只算一次）。"""
    return is_pending(row) or is_abnormal(row)


def issue_rows(rows: list[dict], kind: str = "all") -> list[dict]:
    """按口径过滤卡点条目：all 尚未办结+出错、pending 仅未办结、abnormal 仅出错。"""
    matcher = {
        "all": is_issue,
        "pending": is_pending,
        "abnormal": is_abnormal,
    }.get(kind, is_issue)
    return [row for row in rows if matcher(row)]


def sum_amount(rows: list[dict], amount_field: str | None) -> float | None:
    """汇总金额；模块本身不涉及金额时返回 None，非数值样例自动跳过。"""
    if not amount_field:
        return None
    total = 0.0
    for row in rows:
        try:
            total += float(row.get(amount_field) or 0)
        except (TypeError, ValueError):
            continue
    return round(total, 2)
