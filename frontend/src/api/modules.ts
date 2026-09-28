/** 业务模块元数据：与后端 app/modules.py 的键、中文名保持一致。
 * 首页、未办结清单、侧栏共用这一份顺序，保证三处模块数都是 18 个。
 */
export type ModuleMeta = {
  key: string
  label: string
  /** 该模块金额字段的中文名；无金额口径的模块为 null，清单金额按 ¥0.00 展示。 */
  amountField: string | null
}

export const MODULES: ModuleMeta[] = [
  { key: 'flight', label: '航班计划', amountField: null },
  { key: 'stand', label: '机位资源', amountField: null },
  { key: 'apron', label: '机坪巡查', amountField: null },
  { key: 'bridge', label: '廊桥对接', amountField: null },
  { key: 'deicing', label: '除冰作业', amountField: null },
  { key: 'fueling', label: '航油加注', amountField: null },
  { key: 'baggage', label: '行李装卸', amountField: null },
  { key: 'cargo', label: '货邮装载', amountField: null },
  { key: 'catering', label: '航空配餐', amountField: null },
  { key: 'shuttle', label: '摆渡接送', amountField: null },
  { key: 'towing', label: '航空器牵引', amountField: null },
  { key: 'loadsheet', label: '载重平衡', amountField: null },
  { key: 'permit', label: '通行证件', amountField: null },
  { key: 'gse', label: '保障车辆', amountField: null },
  { key: 'safety', label: '安全监察', amountField: null },
  { key: 'agreement', label: '保障协议', amountField: '协议金额' },
  { key: 'settlement', label: '保障结算', amountField: '应付金额' },
  { key: 'training', label: '资质培训', amountField: null },
]

export function findModule(keyOrLabel: string): ModuleMeta | undefined {
  const keyword = keyOrLabel.trim()
  return MODULES.find((item) => item.key === keyword || item.label === keyword)
}

export function formatAmount(value: number | null | undefined): string {
  const amount = Number(value ?? 0)
  return `¥${Number.isFinite(amount) ? amount.toFixed(2) : '0.00'}`
}
