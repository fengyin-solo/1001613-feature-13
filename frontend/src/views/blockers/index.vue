<template>
  <section class="page" data-module="blockers">
    <header class="page-head">
      <div>
        <h2>未办结与异常清单</h2>
        <p class="page-desc">
          逐模块列出尚未办结、出错的条目。某个模块取不到数据时只影响它自己一行，可单独重新加载。
        </p>
      </div>
      <div class="page-actions">
        <RouterLink class="btn ghost" to="/">返回运营概览</RouterLink>
      </div>
    </header>

    <div class="stat-row">
      <article class="stat-card">
        <span class="stat-label">卡住条目（去重）</span>
        <strong class="stat-value">{{ totals.blocked }}</strong>
      </article>
      <article class="stat-card">
        <span class="stat-label">其中未办结</span>
        <strong class="stat-value">{{ totals.pending }}</strong>
      </article>
      <article class="stat-card">
        <span class="stat-label">其中出错</span>
        <strong class="stat-value">{{ totals.abnormal }}</strong>
      </article>
      <article class="stat-card">
        <span class="stat-label">涉及金额合计</span>
        <strong class="stat-value">{{ formatAmount(totals.amount) }}</strong>
      </article>
    </div>

    <form class="filter-bar" @submit.prevent>
      <label class="filter-item">
        <span>按模块名称收窄</span>
        <input v-model.trim="moduleQuery" list="blocker-module-options" placeholder="输入模块名称或拼音键" />
        <datalist id="blocker-module-options">
          <option v-for="item in MODULES" :key="item.key" :value="item.label" />
        </datalist>
      </label>
      <label class="filter-item">
        <span>条目范围</span>
        <select v-model="kind">
          <option value="all">未办结 + 出错</option>
          <option value="pending">仅未办结</option>
          <option value="abnormal">仅出错</option>
        </select>
      </label>
      <button class="btn ghost" type="button" @click="resetFilter">重置条件</button>
    </form>

    <p v-if="overviewError" class="reconcile warn">首页合计暂时取不到（{{ overviewError }}），各模块明细仍在独立加载，合计不受影响。</p>
    <p v-else-if="mismatches.length" class="reconcile warn">
      以下模块与首页口径对不上：{{ mismatches.join('、') }}，可点对应行的「重新加载」再试。
    </p>
    <p v-else class="reconcile ok">清单条数与金额已与首页逐行核对一致。</p>

    <div class="blocker-list">
      <article v-for="row in visibleRows" :key="row.key" class="blocker-card" :class="{ failed: row.status === 'error' }">
        <header class="blocker-head" @click="toggle(row.key)">
          <span class="blocker-caret" :class="{ open: expanded.has(row.key) }">▶</span>
          <strong class="blocker-name">{{ row.label }}</strong>
          <span class="blocker-badges">
            <span class="badge pending">未办结 {{ headStats(row).pending }}</span>
            <span class="badge abnormal">出错 {{ headStats(row).abnormal }}</span>
            <span class="badge amount">
              涉及金额 {{ row.meta.amountField ? formatAmount(headStats(row).amount) : '—' }}
            </span>
          </span>
          <span v-if="row.status === 'loading'" class="blocker-state muted">加载中…</span>
          <span v-else-if="row.status === 'error'" class="blocker-state error-text" @click.stop>
            取数失败：{{ row.errorMessage }}
            <button class="link" type="button" @click="loadModule(row.key, true)">重新加载</button>
          </span>
          <span v-else class="blocker-state muted">共 {{ row.items?.length ?? 0 }} 条</span>
        </header>

        <div v-show="expanded.has(row.key)" class="blocker-body">
          <p v-if="row.status === 'loading'" class="blocker-loading muted">正在读取{{ row.label }}的卡住条目…</p>
          <template v-else-if="row.status === 'error'">
            <p class="error-text">{{ row.errorMessage }}</p>
            <button class="btn primary" type="button" @click="loadModule(row.key, true)">重新加载该模块</button>
          </template>
          <template v-else>
            <table v-if="visibleItems(row).length" class="data-table blocker-table">
              <thead>
                <tr>
                  <th v-for="column in columnsFor(row)" :key="column">{{ column }}</th>
                  <th>状态</th>
                  <th v-if="row.meta.amountField">涉及金额（{{ row.meta.amountField }}）</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in visibleItems(row)" :key="String(item.id)">
                  <td v-for="column in columnsFor(row)" :key="column">{{ displayValue(item[column]) }}</td>
                  <td>
                    <span class="badge pending" v-if="item.pending">未办结</span>
                    <span class="badge abnormal" v-if="item.abnormal">出错</span>
                    <span class="muted" v-if="!item.pending && !item.abnormal">{{ item.status ?? '—' }}</span>
                  </td>
                  <td v-if="row.meta.amountField">{{ formatAmount(item.amount) }}</td>
                </tr>
              </tbody>
            </table>
            <p v-else class="empty-state">当前范围下{{ row.label }}没有卡住的条目。</p>
          </template>
        </div>
      </article>
    </div>

    <p v-if="!visibleRows.length" class="empty-state">没有名称匹配「{{ moduleQuery }}」的业务模块。</p>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, onBeforeUnmount, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import { fetchJson } from '@/api/client'
import { findModule, formatAmount, MODULES, type ModuleMeta } from '@/api/modules'
import { loadJson, saveJson } from '@/utils/storage'

type BlockerItem = Record<string, string | number | null> & {
  id: number
  status?: string
  pending?: boolean
  abnormal?: boolean
  amount?: number
}

type BlockerPayload = {
  module: string
  label: string
  total: number
  pending: number
  abnormal: number
  amount: number
  amountField: string | null
  items: BlockerItem[]
}

type Overview = {
  cards: { label: string; value: number }[]
  modules: {
    name: string
    label?: string
    created: number
    pending: number
    abnormal: number
    blocked?: number
    amount: number
    amountField?: string | null
  }[]
}

type RowStatus = 'idle' | 'loading' | 'ready' | 'error'

type ModuleRow = {
  key: string
  label: string
  meta: ModuleMeta
  status: RowStatus
  items: BlockerItem[]
  pending: number
  abnormal: number
  amount: number
  errorMessage: string
}

const STORAGE_KEY = 'ops:blockers:v1'

const route = useRoute()

const saved = loadJson(STORAGE_KEY, {
  moduleQuery: '',
  kind: 'all',
  expanded: [] as string[],
  scrollY: 0,
})

const KIND_VALUES = ['all', 'pending', 'abnormal'] as const
type KindValue = (typeof KIND_VALUES)[number]
function normalizeKind(value: unknown): KindValue {
  return KIND_VALUES.includes(value as KindValue) ? (value as KindValue) : 'all'
}

// query 里的 module 优先（首页点进来）：键名（agreement）或中文名都能识别，统一归一成中文名。
const queriedModule = typeof route.query.module === 'string' ? findModule(route.query.module) : undefined
const moduleQuery = ref<string>(queriedModule?.label ?? String(saved.moduleQuery ?? ''))
const kind = ref<KindValue>(normalizeKind(route.query.kind ?? saved.kind))
// 从具体模块点进来（query 带 module）时，即便本地存过展开集合也要保证该模块展开。
const expanded = ref<Set<string>>(new Set(saved.expanded))
const overviewRows = ref<Overview['modules']>([])
const overviewError = ref('')
const rows = ref<ModuleRow[]>(
  MODULES.map((meta) => ({
    key: meta.key,
    label: meta.label,
    meta,
    status: 'idle',
    items: [],
    pending: 0,
    abnormal: 0,
    amount: 0,
    errorMessage: '',
  })),
)

const rowByKey = new Map(rows.value.map((row) => [row.key, row]))

function rowOf(key: string): ModuleRow {
  const row = rowByKey.get(key)
  if (!row) throw new Error(`未知模块 ${key}`)
  return row
}

const visibleRows = computed(() => {
  const keyword = moduleQuery.value.trim()
  if (!keyword) return rows.value
  return rows.value.filter(
    (row) => row.label.includes(keyword) || row.key.toLowerCase().includes(keyword.toLowerCase()),
  )
})

function visibleItems(row: ModuleRow): BlockerItem[] {
  if (kind.value === 'pending') return row.items.filter((item) => item.pending)
  if (kind.value === 'abnormal') return row.items.filter((item) => item.abnormal)
  return row.items
}

/** 明细列：取条目里除 id/状态标记/金额之外的业务字段，保证列与该模块数据对得上。 */
const RESERVED_KEYS = new Set(['id', 'status', 'pending', 'abnormal', 'amount'])
function columnsFor(row: ModuleRow): string[] {
  const seen = new Set<string>()
  for (const item of row.items) {
    for (const key of Object.keys(item)) {
      if (!RESERVED_KEYS.has(key)) seen.add(key)
    }
  }
  return [...seen]
}

function displayValue(value: string | number | null | undefined): string {
  if (value === null || value === undefined || value === '') return '—'
  return String(value)
}

/** 头部徽标数：加载成功后用明细统计（与首页核对）；未加载/失败时退回首行数。 */
function headStats(row: ModuleRow): { pending: number; abnormal: number; amount: number } {
  if (row.status === 'ready') {
    return { pending: row.pending, abnormal: row.abnormal, amount: row.amount }
  }
  const overview = overviewRows.value.find((item) => item.name === row.key)
  if (overview) {
    return { pending: overview.pending, abnormal: overview.abnormal, amount: overview.amount ?? 0 }
  }
  return { pending: row.pending, abnormal: row.abnormal, amount: row.amount }
}

/** 合计只用各模块独立加载的结果；任何模块失败都不会污染首页合计。 */
const totals = computed(() => {
  const ready = rows.value.filter((row) => row.status === 'ready')
  const pending = ready.reduce((sum, row) => sum + row.pending, 0)
  const abnormal = ready.reduce((sum, row) => sum + row.abnormal, 0)
  const blocked = ready.reduce((sum, row) => sum + row.items.length, 0)
  const amount = ready.reduce((sum, row) => sum + row.amount, 0)
  return { pending, abnormal, blocked, amount: Math.round(amount * 100) / 100 }
})

/** 逐行核对：明细里的未办结数、出错数、金额必须与首页那一行一致。 */
const mismatches = computed(() => {
  const result: string[] = []
  for (const row of rows.value) {
    if (row.status !== 'ready') continue
    const overview = overviewRows.value.find((item) => item.name === row.key)
    if (!overview) continue
    const amountEqual = Math.abs((overview.amount ?? 0) - row.amount) < 0.005
    if (overview.pending !== row.pending || overview.abnormal !== row.abnormal || !amountEqual) {
      result.push(row.label)
    }
  }
  return result
})

async function loadOverview() {
  overviewError.value = ''
  try {
    const payload = await fetchJson<Overview>('/api/overview')
    overviewRows.value = payload.modules ?? []
  } catch (error) {
    overviewError.value = error instanceof Error ? error.message : '概览读取失败'
  }
}

async function loadModule(key: string, force = false) {
  const row = rowOf(key)
  if (row.status === 'loading' || (row.status === 'ready' && !force)) return
  row.status = 'loading'
  row.errorMessage = ''
  try {
    const payload = await fetchJson<BlockerPayload>(`/api/blockers/${encodeURIComponent(key)}`)
    row.items = payload.items ?? []
    row.pending = payload.pending ?? 0
    row.abnormal = payload.abnormal ?? 0
    row.amount = payload.amount ?? 0
    row.status = 'ready'
  } catch (error) {
    row.items = []
    row.status = 'error'
    row.errorMessage = error instanceof Error ? error.message : '该模块数据读取失败'
  }
}

function toggle(key: string) {
  const next = new Set(expanded.value)
  if (next.has(key)) {
    next.delete(key)
  } else {
    next.add(key)
    void loadModule(key)
  }
  expanded.value = next
}

function resetFilter() {
  moduleQuery.value = ''
  kind.value = 'all'
}

function persist() {
  saveJson(STORAGE_KEY, {
    moduleQuery: moduleQuery.value,
    kind: kind.value,
    expanded: [...expanded.value],
    scrollY: window.scrollY,
  })
}

watch([moduleQuery, kind], persist)
watch(expanded, persist, { deep: true })
window.addEventListener('scroll', persist, { passive: true })
onBeforeUnmount(() => window.removeEventListener('scroll', persist))

onMounted(async () => {
  // 从首页某行点进来（query 带 module）时，即便本地存过展开集合也要保证该模块展开。
  if (queriedModule) {
    expanded.value.add(queriedModule.key)
  }
  await loadOverview()
  // 恢复上次展开的模块：各发各的请求，互不等待，单个失败只落在自己一行。
  await Promise.allSettled([...expanded.value].map((key) => loadModule(key)))
  // 展开模块的表格是异步渲染的：等两帧让高度稳定后再恢复滚动，避免被夹回顶部。
  const restoreY = Number(saved.scrollY ?? 0)
  if (Number.isFinite(restoreY) && restoreY > 0) {
    requestAnimationFrame(() => requestAnimationFrame(() => window.scrollTo({ top: restoreY })))
  }
})
</script>
