<template>
  <div class="issue-detail">
    <div class="detail-head">
      <strong>{{ data.name }} · {{ kindLabel }}清单</strong>
      <span class="reconcile">
        共 <b>{{ data.total }}</b> 条
        <template v-if="data.amountField !== null">，合计 <b>{{ formatAmount(data.amount) }}</b>（{{ data.amountField }}）</template>
      </span>
      <RouterLink class="link" :to="`/${data.key}`">前往{{ data.name }}管理页 →</RouterLink>
    </div>
    <p class="detail-reconcile muted-cell">
      与首页那一行对账：卡点 {{ data.issuesCount }} 条
      <template v-if="data.issuesAmount !== null">、涉及金额 {{ formatAmount(data.issuesAmount) }}</template>
      （尚未办结 {{ data.pendingCount }} 条、出错 {{ data.abnormalCount }} 条），当前口径下列出 {{ data.total }} 条。
    </p>
    <table v-if="data.items.length" class="data-table detail-table">
      <thead>
        <tr>
          <th>卡点类型</th>
          <th v-for="field in displayFields" :key="field">{{ field }}</th>
          <th>当前状态</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in data.items" :key="String(item.id)">
          <td class="issue-tag-cell">
            <span v-if="item.abnormal" class="tag tag-error">出错</span>
            <span v-if="item.pending" class="tag tag-pending">未办结</span>
          </td>
          <td v-for="field in displayFields" :key="field">{{ item[field] ?? '—' }}</td>
          <td>{{ item.status ?? '—' }}</td>
        </tr>
      </tbody>
    </table>
    <p v-else class="empty-state detail-empty">当前口径下没有卡点条目</p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

import { ISSUE_KIND_LABELS, type IssueKind, type ModuleIssuesPayload } from '@/api/modules'

const props = defineProps<{ data: ModuleIssuesPayload }>()

/** 清单只取前四个业务字段，避免横向过宽；金额字段在时确保保留 */
const displayFields = computed(() => {
  const fields = props.data.fields ?? []
  const picked = fields.slice(0, 4)
  if (props.data.amountField && !picked.includes(props.data.amountField)) {
    picked[3] = props.data.amountField
  }
  return picked
})

const kindLabel = computed(() => ISSUE_KIND_LABELS[props.data.kind as IssueKind] ?? ISSUE_KIND_LABELS.all)

function formatAmount(value: number | null): string {
  if (value === null || value === undefined) return '—'
  return `¥${Number(value).toFixed(2)}`
}
</script>

<style scoped>
.issue-detail { padding: 4px 8px 8px; }
.detail-head { display: flex; align-items: center; gap: 16px; margin-bottom: 6px; font-size: 13px; }
.reconcile { color: var(--muted); }
.reconcile b { color: #1f2937; }
.detail-reconcile { font-size: 12px; margin: 0 0 8px; }
.detail-table th, .detail-table td { font-size: 12px; padding: 6px 8px; }
.detail-empty { padding: 12px; }
.tag { display: inline-block; border-radius: 4px; padding: 1px 6px; font-size: 12px; margin-right: 4px; }
.tag-pending { background: #fff4e5; color: #b54708; }
.tag-error { background: #fee4e2; color: #b42318; }
</style>
