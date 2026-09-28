import { createRouter, createWebHistory } from 'vue-router'

import Dashboard from '@/views/Dashboard.vue'
const Blockers = () => import('@/views/blockers/index.vue')
const Flight = () => import('@/views/flight/index.vue')
const Stand = () => import('@/views/stand/index.vue')
const Apron = () => import('@/views/apron/index.vue')
const Bridge = () => import('@/views/bridge/index.vue')
const Deicing = () => import('@/views/deicing/index.vue')
const Fueling = () => import('@/views/fueling/index.vue')
const Baggage = () => import('@/views/baggage/index.vue')
const Cargo = () => import('@/views/cargo/index.vue')
const Catering = () => import('@/views/catering/index.vue')
const Shuttle = () => import('@/views/shuttle/index.vue')
const Towing = () => import('@/views/towing/index.vue')
const Loadsheet = () => import('@/views/loadsheet/index.vue')
const Permit = () => import('@/views/permit/index.vue')
const Gse = () => import('@/views/gse/index.vue')
const Safety = () => import('@/views/safety/index.vue')
const Agreement = () => import('@/views/agreement/index.vue')
const Settlement = () => import('@/views/settlement/index.vue')
const Training = () => import('@/views/training/index.vue')

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'dashboard', component: Dashboard },
    { path: '/blockers', name: 'blockers', component: Blockers },
    { path: '/flight', name: 'flight', component: Flight },
    { path: '/stand', name: 'stand', component: Stand },
    { path: '/apron', name: 'apron', component: Apron },
    { path: '/bridge', name: 'bridge', component: Bridge },
    { path: '/deicing', name: 'deicing', component: Deicing },
    { path: '/fueling', name: 'fueling', component: Fueling },
    { path: '/baggage', name: 'baggage', component: Baggage },
    { path: '/cargo', name: 'cargo', component: Cargo },
    { path: '/catering', name: 'catering', component: Catering },
    { path: '/shuttle', name: 'shuttle', component: Shuttle },
    { path: '/towing', name: 'towing', component: Towing },
    { path: '/loadsheet', name: 'loadsheet', component: Loadsheet },
    { path: '/permit', name: 'permit', component: Permit },
    { path: '/gse', name: 'gse', component: Gse },
    { path: '/safety', name: 'safety', component: Safety },
    { path: '/agreement', name: 'agreement', component: Agreement },
    { path: '/settlement', name: 'settlement', component: Settlement },
    { path: '/training', name: 'training', component: Training },
  ],
})

const LAST_ROUTE_KEY = 'ops:last-route:v1'
const SESSION_KEY = 'ops:session-active'

// 关掉页面再打开：仅在本次浏览器会话的第一次导航（即重开应用）时，
// 若上次停在清单页则回到那里；会话内通过侧栏、返回按钮回首页属于主动导航，不重定向。
router.beforeEach((to) => {
  let sessionActive = false
  try {
    sessionActive = window.sessionStorage.getItem(SESSION_KEY) === '1'
    window.sessionStorage.setItem(SESSION_KEY, '1')
  } catch {
    /* 存储不可用时不做恢复，照常进入目标页。 */
    return true
  }
  if (!sessionActive && to.name === 'dashboard' && !Object.keys(to.query).length) {
    try {
      const last = window.localStorage.getItem(LAST_ROUTE_KEY)
      // 上次停在清单页则回到该页；入口查询参数（?module=…）只是一次性进入手势，
      // 清单页自己保存的筛选/展开/滚动才是「刚才的位置」，故恢复时不带 query。
      if (last && last.startsWith('/blockers')) {
        return '/blockers'
      }
    } catch {
      /* 存储不可用时忽略，照常进入首页。 */
    }
  }
  return true
})

// 记录最后访问的完整路径（含 module/kind 查询参数），供下次打开恢复。
router.afterEach((to) => {
  try {
    window.localStorage.setItem(LAST_ROUTE_KEY, to.fullPath)
  } catch {
    /* 存储不可用时忽略。 */
  }
})

export default router
