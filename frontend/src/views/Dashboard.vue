<template>
  <section class="page">
    <header class="page-head">
      <div>
        <h2>运营概览</h2>
        <p class="page-desc">汇总各业务模块的关键指标，先看总量再看异常；点卡片可逐模块查看卡点条目。</p>
      </div>
    </header>
    <div class="stat-row">
      <article
        v-for="card in cards"
        :key="card.label"
        class="stat-card"
        :class="{ 'stat-card-link': card.target }"
        :role="card.target ? 'link' : undefined"
        :tabindex="card.target ? 0 : undefined"
        :title="card.target ? '查看各业务模块的卡点清单' : undefined"
        @click="card.target ? go(card.target) : undefined"
        @keydown.enter="card.target ? go(card.target) : undefined"
      >
        <span class="stat-label">{{ card.label }}</span>
        <strong class="stat-value">{{ card.value }}</strong>
      </article>
    </div>
    <table class="data-table">
      <thead>
        <tr><th>业务模块</th><th>今日新增</th><th>待处理</th><th>异常量</th><th>卡点条目</th><th>涉及金额</th></tr>
      </thead>
      <tbody>
        <tr v-for="row in moduleRows" :key="row.key ?? row.name">
          <td>{{ row.name }}</td>
          <td>{{ row.created }}</td>
          <td>{{ row.pending }}</td>
          <td>{{ row.abnormal }}</td>
          <td>{{ row.issues ?? 0 }}</td>
          <td>{{ formatAmount(row.amount) }}</td>
        </tr>
      </tbody>
    </table>
    <footer class="page-foot">
      <span>共 {{ moduleRows.length }} 个业务模块</span>
      <span class="muted-cell">「卡点条目」「涉及金额」与进入后的卡点清单同口径；个别模块取数失败不累及合计</span>
    </footer>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { fetchJson } from '@/api/client'

type Overview = {
  cards: { label: string; value: number }[]
  modules: {
    key?: string
    name: string
    created: number
    pending: number
    abnormal: number
    issues?: number
    amount?: number | null
  }[]
}

/** 卡片与卡点页口径的对应；今日新增没有卡点语义，保持不可点。 */
const CARD_TARGETS: Record<string, string> = {
  业务模块: '/issues',
  待处理: '/issues?kind=pending',
  异常量: '/issues?kind=abnormal',
}

const cards = ref<{ label: string; value: number; target: string | null }[]>([])
const moduleRows = ref<Overview['modules']>([])
const router = useRouter()

function go(target: string) {
  void router.push(target)
}

function formatAmount(value: number | null | undefined): string {
  if (value === null || value === undefined) return '—'
  return `¥${Number(value).toFixed(2)}`
}

function withTargets(list: Overview['cards']) {
  return list.map((card) => ({ ...card, target: CARD_TARGETS[card.label] ?? null }))
}

onMounted(async () => {
  try {
    const payload = await fetchJson<Overview>('/api/overview')
    cards.value = withTargets(payload.cards)
    moduleRows.value = payload.modules
  } catch {
    // 概览整体取不到时给全零兜底，合计卡片与 18 个模块入口仍在，不因接口失败而缺行
    cards.value = withTargets([
      { label: '业务模块', value: 0 },
      { label: '今日新增', value: 0 },
      { label: '待处理', value: 0 },
      { label: '异常量', value: 0 },
    ])
    moduleRows.value = FALLBACK_MODULES
  }
})

const FALLBACK_MODULES: Overview['modules'] = [
  { key: 'flight', name: '航班计划', created: 0, pending: 0, abnormal: 0, issues: 0, amount: null },
  { key: 'stand', name: '机位资源', created: 0, pending: 0, abnormal: 0, issues: 0, amount: null },
  { key: 'apron', name: '机坪巡查', created: 0, pending: 0, abnormal: 0, issues: 0, amount: null },
  { key: 'bridge', name: '廊桥对接', created: 0, pending: 0, abnormal: 0, issues: 0, amount: null },
  { key: 'deicing', name: '除冰作业', created: 0, pending: 0, abnormal: 0, issues: 0, amount: null },
  { key: 'fueling', name: '航油加注', created: 0, pending: 0, abnormal: 0, issues: 0, amount: null },
  { key: 'baggage', name: '行李装卸', created: 0, pending: 0, abnormal: 0, issues: 0, amount: null },
  { key: 'cargo', name: '货邮装载', created: 0, pending: 0, abnormal: 0, issues: 0, amount: null },
  { key: 'catering', name: '航空配餐', created: 0, pending: 0, abnormal: 0, issues: 0, amount: null },
  { key: 'shuttle', name: '摆渡接送', created: 0, pending: 0, abnormal: 0, issues: 0, amount: null },
  { key: 'towing', name: '航空器牵引', created: 0, pending: 0, abnormal: 0, issues: 0, amount: null },
  { key: 'loadsheet', name: '载重平衡', created: 0, pending: 0, abnormal: 0, issues: 0, amount: null },
  { key: 'permit', name: '通行证件', created: 0, pending: 0, abnormal: 0, issues: 0, amount: null },
  { key: 'gse', name: '保障车辆', created: 0, pending: 0, abnormal: 0, issues: 0, amount: null },
  { key: 'safety', name: '安全监察', created: 0, pending: 0, abnormal: 0, issues: 0, amount: null },
  { key: 'agreement', name: '保障协议', created: 0, pending: 0, abnormal: 0, issues: 0, amount: 0 },
  { key: 'settlement', name: '保障结算', created: 0, pending: 0, abnormal: 0, issues: 0, amount: 0 },
  { key: 'training', name: '资质培训', created: 0, pending: 0, abnormal: 0, issues: 0, amount: null },
]
</script>
