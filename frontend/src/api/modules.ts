/** 业务模块注册信息：与后端 app/modules.py 同口径，顺序即首页与侧栏的 18 个模块。 */
export type ModuleMeta = {
  key: string
  name: string
  /** 清单页展示字段（后端会再下发一遍，这里仅用于接口失败时的兜底展示） */
  fields: string[]
  /** 涉及金额的字段；不涉及金额的模块为 null */
  amountField: string | null
}

export const MODULES: ModuleMeta[] = [
  { key: 'flight', name: '航班计划', fields: ['航班号', '执行日期', '机型', '起降性质', '计划时刻', '预计时刻', '保障等级', '航班状态'], amountField: null },
  { key: 'stand', name: '机位资源', fields: ['机位编号', '机位类别', '所属区域', '适用机型', '廊桥配置', '加注接口', '保障能力', '机位状态'], amountField: null },
  { key: 'apron', name: '机坪巡查', fields: ['巡查单号', '巡查区域', '巡查人员', '巡查日期', '巡查项目', '发现问题数', '巡查时长', '巡查状态'], amountField: null },
  { key: 'bridge', name: '廊桥对接', fields: ['对接单号', '关联航班', '廊桥编号', '对接时刻', '撤桥时刻', '操作人员', '对接结果', '对接状态'], amountField: null },
  { key: 'deicing', name: '除冰作业', fields: ['除冰单号', '关联航班', '除冰方式', '除冰液用量', '作业车辆', '作业人员', '完成时刻', '除冰状态'], amountField: null },
  { key: 'fueling', name: '航油加注', fields: ['加注单号', '关联航班', '加注车号', '加注油量', '油品规格', '加注人员', '完成时刻', '加注状态'], amountField: null },
  { key: 'baggage', name: '行李装卸', fields: ['装卸单号', '关联航班', '行李件数', '装卸车辆', '作业班组', '开始时刻', '完成时刻', '装卸状态'], amountField: null },
  { key: 'cargo', name: '货邮装载', fields: ['装载单号', '关联航班', '货邮重量', '装载位置', '装载车辆', '作业人员', '完成时刻', '装载状态'], amountField: null },
  { key: 'catering', name: '航空配餐', fields: ['配餐单号', '关联航班', '餐食份数', '餐食类别', '配餐车辆', '送达时刻', '接收人员', '配餐状态'], amountField: null },
  { key: 'shuttle', name: '摆渡接送', fields: ['任务编号', '关联航班', '车辆编号', '乘客人数', '出发时刻', '到达时刻', '驾驶人员', '摆渡状态'], amountField: null },
  { key: 'towing', name: '航空器牵引', fields: ['牵引编号', '关联航班', '牵引车号', '起点机位', '终点机位', '牵引人员', '完成时刻', '牵引状态'], amountField: null },
  { key: 'loadsheet', name: '载重平衡', fields: ['配载单号', '关联航班', '计算重量', '重心位置', '油量数据', '配载人员', '复核人员', '配载状态'], amountField: null },
  { key: 'permit', name: '通行证件', fields: ['证件编号', '持证人员', '所属单位', '通行区域', '有效期至', '发证人员', '发证日期', '证件状态'], amountField: null },
  { key: 'gse', name: '保障车辆', fields: ['车辆编号', '车辆类别', '适用作业', '停放区域', '上次保养日', '下次保养日', '责任人', '车辆状态'], amountField: null },
  { key: 'safety', name: '安全监察', fields: ['监察编号', '监察区域', '监察事项', '违规情形', '涉及单位', '监察人员', '监察日期', '监察状态'], amountField: null },
  { key: 'agreement', name: '保障协议', fields: ['协议编号', '服务单位', '保障项目', '协议金额', '服务期限', '签订人员', '到期日期', '协议状态'], amountField: '协议金额' },
  { key: 'settlement', name: '保障结算', fields: ['结算单号', '关联协议', '结算周期', '应付金额', '已付金额', '审核人员', '付款日期', '结算状态'], amountField: '应付金额' },
  { key: 'training', name: '资质培训', fields: ['培训编号', '培训主题', '培训对象', '授课人员', '培训课时', '考核成绩', '培训日期', '培训状态'], amountField: null },
]

/** 卡点口径：all 尚未办结+出错、pending 仅未办结、abnormal 仅出错 */
export type IssueKind = 'all' | 'pending' | 'abnormal'

export const ISSUE_KIND_LABELS: Record<IssueKind, string> = {
  all: '全部卡点',
  pending: '尚未办结',
  abnormal: '出错条目',
}

export type ModuleIssuesPayload = {
  key: string
  name: string
  kind: IssueKind
  fields: string[]
  amountField: string | null
  /** 始终是「未办结+出错」全集口径，用来与首页那一行对账，不随 kind 变 */
  issuesCount: number
  issuesAmount: number | null
  pendingCount: number
  abnormalCount: number
  /** 当前口径下的清单条数与金额 */
  total: number
  amount: number | null
  items: Record<string, string | number | boolean | null>[]
}
