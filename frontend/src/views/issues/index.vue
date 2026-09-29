<template>
  <section class="page" data-module="issues">
    <header class="page-head">
      <div>
        <h2>业务卡点清单</h2>
        <p class="page-desc">
          从运营概览逐模块下钻，列出尚未办结与出错的条目；每个模块独立取数，
          单个模块失败只影响它自己那一行，可单独重新加载。
        </p>
      </div>
      <div class="page-actions">
        <RouterLink class="btn ghost" to="/">返回运营概览</RouterLink>
      </div>
    </header>

    <div class="kind-tabs" role="tablist">
      <button
        v-for="tab in kindTabs"
        :key="tab.kind"
        type="button"
        class="kind-tab"
        :class="{ active: kind === tab.kind }"
        @click="switchKind(tab.kind)"
      >
        {{ tab.label }}
      </button>
    </div>

    <form class="filter-bar" @submit.prevent>
      <label class="filter-item">
        <span>模块名称</span>
        <input v-model="keyword" placeholder="按模块名称收窄，如：结算" @input="persistState" />
      </label>
      <button class="btn" type="button" @click="persistState">收窄</button>
      <button class="btn ghost" type="button" @click="resetKeyword">重置条件</button>
    </form>

    <table class="data-table issue-table">
      <thead>
        <tr>
          <th>业务模块</th>
          <th>卡点条目</th>
          <th>尚未办结</th>
          <th>出错条目</th>
          <th>涉及金额</th>
          <th>取数状态</th>
        </tr>
      </thead>
      <tbody>
        <template v-for="row in visibleRows" :key="row.key">
          <tr class="issue-row" :class="{ expanded: isExpanded(row.key) }" @click="toggleExpand(row.key)">
            <td>
              <span class="expand-mark">{{ isExpanded(row.key) ? '▾' : '▸' }}</span>
              {{ row.name }}
            </td>
            <template v-if="row.status === 'success' && row.data">
              <td>{{ row.data.issuesCount }}</td>
              <td>{{ row.data.pendingCount }}</td>
              <td>{{ row.data.abnormalCount }}</td>
              <td>{{ formatAmount(row.data.issuesAmount) }}</td>
              <td class="muted-cell">正常，点击查看清单</td>
            </template>
            <template v-else-if="row.status === 'error'">
              <td colspan="4" class="error-text">
                {{ row.name }} 数据取不到：{{ row.error }}
              </td>
              <td>
                <button class="link" type="button" @click.stop="retry(row)">重新加载</button>
              </td>
            </template>
            <template v-else>
              <td colspan="4" class="muted-cell">正在取数…</td>
              <td class="muted-cell">加载中</td>
            </template>
          </tr>
          <tr v-if="isExpanded(row.key)" class="issue-detail-row">
            <td colspan="6" class="issue-detail-cell">
              <template v-if="row.status === 'success' && row.data">
                <IssueDetail :data="row.data" />
              </template>
              <p v-else-if="row.status === 'error'" class="error-text detail-tip">
                该模块取数失败，其它模块不受影响，点「重新加载」只重试这一行。
              </p>
              <p v-else class="muted-cell detail-tip">清单加载中…</p>
            </td>
          </tr>
        </template>
        <tr v-if="!visibleRows.length">
          <td colspan="6" class="empty-state">没有名称包含「{{ keyword }}」的业务模块</td>
        </tr>
      </tbody>
    </table>

    <footer class="page-foot">
      <span>共 {{ visibleRows.length }} / {{ rows.length }} 个业务模块，按模块独立取数、互不牵连</span>
      <span class="muted-cell">口径：尚未办结（pending）或出错（abnormal），同一条目只计一次</span>
    </footer>
  </section>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { fetchJson } from '@/api/client'
import { ISSUE_KIND_LABELS, MODULES, type IssueKind, type ModuleIssuesPayload } from '@/api/modules'
import IssueDetail from './IssueDetail.vue'

type RowStatus = 'loading' | 'success' | 'error'

type ModuleRow = {
  key: string
  name: string
  status: RowStatus
  error: string
  data: ModuleIssuesPayload | null
}

const STORAGE_KEY = 'ops-issues-view-state-v1'
const kindTabs = [
  { kind: 'all' as IssueKind, label: ISSUE_KIND_LABELS.all },
  { kind: 'pending' as IssueKind, label: ISSUE_KIND_LABELS.pending },
  { kind: 'abnormal' as IssueKind, label: ISSUE_KIND_LABELS.abnormal },
]

const route = useRoute()
const router = useRouter()

const rows = ref<ModuleRow[]>(MODULES.map((meta) => ({
  key: meta.key,
  name: meta.name,
  status: 'loading',
  error: '',
  data: null,
})))
const kind = ref<IssueKind>('all')
const keyword = ref('')
const expanded = ref<Set<string>>(new Set())
let initialRestored = false

const visibleRows = computed(() => {
  const word = keyword.value.trim()
  if (!word) return rows.value
  return rows.value.filter((row) => row.name.includes(word))
})

function isExpanded(key: string): boolean {
  return expanded.value.has(key)
}

function toggleExpand(key: string) {
  const next = new Set(expanded.value)
  if (next.has(key)) {
    next.delete(key)
  } else {
    next.add(key)
  }
  expanded.value = next
  persistState()
}

function switchKind(next: IssueKind) {
  if (next === kind.value) return
  kind.value = next
  persistState()
  void router.replace({ query: { ...route.query, kind: next } })
  void loadAll()
}

function resetKeyword() {
  keyword.value = ''
  persistState()
}

async function loadModule(row: ModuleRow) {
  row.status = 'loading'
  row.error = ''
  try {
    const payload = await fetchJson<ModuleIssuesPayload>(
      `/api/modules/${row.key}/issues?kind=${kind.value}`,
    )
    row.data = payload
    row.status = 'success'
  } catch (error) {
    // 只标记当前模块这一行，其它模块的展示与首页合计都不受牵连
    row.status = 'error'
    row.error = error instanceof Error ? error.message : '请求未送达'
  }
}

async function loadAll() {
  await Promise.all(rows.value.map((row) => loadModule(row)))
  if (!initialRestored) {
    initialRestored = true
    await nextTick()
    restoreScroll()
  }
}

function retry(row: ModuleRow) {
  void loadModule(row)
}

function formatAmount(value: number | null | undefined): string {
  if (value === null || value === undefined) return '—'
  return `¥${Number(value).toFixed(2)}`
}

function persistState() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
      kind: kind.value,
      keyword: keyword.value,
      expanded: [...expanded.value],
      scrollY: window.scrollY,
    }))
  } catch {
    // 隐私模式等场景写不进 storage 时静默降级，仅影响“回到原位”能力
  }
}

function restoreState() {
  let saved: { kind?: IssueKind; keyword?: string; expanded?: string[] } = {}
  try {
    saved = JSON.parse(localStorage.getItem(STORAGE_KEY) ?? '{}') as typeof saved
  } catch {
    saved = {}
  }
  // 地址栏参数优先，保证链接可分享；其次回到上次关掉页面时的位置
  const queryKind = String(route.query.kind ?? '')
  if (queryKind === 'all' || queryKind === 'pending' || queryKind === 'abnormal') {
    kind.value = queryKind
  } else if (saved.kind) {
    kind.value = saved.kind
  }
  keyword.value = typeof route.query.q === 'string' ? route.query.q : (saved.keyword ?? '')
  if (Array.isArray(saved.expanded)) {
    expanded.value = new Set(saved.expanded.filter((key) => MODULES.some((meta) => meta.key === key)))
  }
}

function restoreScroll() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) ?? '{}') as { scrollY?: number }
    if (typeof saved.scrollY === 'number') {
      window.scrollTo(0, saved.scrollY)
    }
  } catch {
    // 忽略无法读取的滚动位置
  }
}

function onScroll() {
  // 直接记录，事件本身频率不高；关闭页面时也会再写一次
  persistState()
}

onMounted(() => {
  restoreState()
  window.addEventListener('scroll', onScroll, { passive: true })
  window.addEventListener('beforeunload', persistState)
  void loadAll()
})

onBeforeUnmount(() => {
  persistState()
  window.removeEventListener('scroll', onScroll)
  window.removeEventListener('beforeunload', persistState)
})
</script>
