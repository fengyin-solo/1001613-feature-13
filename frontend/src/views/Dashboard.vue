<template>
  <section class="page">
    <header class="page-head">
      <div>
        <h2>运营概览</h2>
        <p class="page-desc">汇总各业务模块的关键指标，先看总量再看异常；点任意卡片或模块行可查看卡在哪。</p>
      </div>
    </header>
    <div class="stat-row">
      <RouterLink
        v-for="card in cardLinks"
        :key="card.label"
        class="stat-card stat-link"
        :to="card.to"
      >
        <span class="stat-label">{{ card.label }}</span>
        <strong class="stat-value">{{ card.value }}</strong>
      </RouterLink>
    </div>
    <table class="data-table">
      <thead>
        <tr><th>业务模块</th><th>今日新增</th><th>待处理</th><th>异常量</th><th>涉及金额</th><th>明细</th></tr>
      </thead>
      <tbody>
        <tr
          v-for="row in moduleRows"
          :key="row.name"
          class="module-row"
          role="link"
          tabindex="0"
          @click="openModule(row.name)"
          @keydown.enter="openModule(row.name)"
        >
          <td class="module-name">{{ row.label ?? row.name }}</td>
          <td>{{ row.created }}</td>
          <td>{{ row.pending }}</td>
          <td>{{ row.abnormal }}</td>
          <td>{{ formatAmount(row.amount) }}</td>
          <td><span class="link">查看未办结/异常 →</span></td>
        </tr>
      </tbody>
    </table>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { fetchJson } from '@/api/client'
import { formatAmount, MODULES } from '@/api/modules'

type ModuleRow = {
  name: string
  label?: string
  created: number
  pending: number
  abnormal: number
  blocked?: number
  amount?: number
}

type Overview = {
  cards: { label: string; value: number }[]
  modules: ModuleRow[]
}

const router = useRouter()
const cards = ref<Overview['cards']>([])
const moduleRows = ref<ModuleRow[]>([])

// 顶部卡片：待处理/异常量点进去直接按对应范围过滤，模块数/今日新增进入全部模块清单。
const cardLinks = computed(() => [
  { label: cards.value[0]?.label ?? '业务模块', value: cards.value[0]?.value ?? MODULES.length, to: '/blockers' },
  { label: cards.value[1]?.label ?? '今日新增', value: cards.value[1]?.value ?? 0, to: '/blockers' },
  { label: cards.value[2]?.label ?? '待处理', value: cards.value[2]?.value ?? 0, to: '/blockers?kind=pending' },
  { label: cards.value[3]?.label ?? '异常量', value: cards.value[3]?.value ?? 0, to: '/blockers?kind=abnormal' },
])

function openModule(name: string) {
  void router.push({ path: '/blockers', query: { module: name } })
}

function fallbackRows(): ModuleRow[] {
  return MODULES.map((meta) => ({ name: meta.key, label: meta.label, created: 0, pending: 0, abnormal: 0, amount: 0 }))
}

onMounted(async () => {
  try {
    const payload = await fetchJson<Overview>('/api/overview')
    cards.value = payload.cards
    moduleRows.value = payload.modules
  } catch {
    cards.value = [
      { label: '业务模块', value: MODULES.length },
      { label: '今日新增', value: 0 },
      { label: '待处理', value: 0 },
      { label: '异常量', value: 0 },
    ]
    moduleRows.value = fallbackRows()
  }
})
</script>
