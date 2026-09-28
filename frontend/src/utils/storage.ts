/** localStorage 小封装：清单页用它记住筛选、展开的模块与滚动位置。
 * 关掉页面再打开仍可恢复；隐私模式等不可用场景下静默降级，不影响功能。
 */
export function loadJson<T>(key: string, fallback: T): T {
  try {
    const raw = window.localStorage.getItem(key)
    if (raw === null) return fallback
    return { ...fallback, ...(JSON.parse(raw) as T) } as T
  } catch {
    return fallback
  }
}

export function saveJson(key: string, value: unknown): void {
  try {
    window.localStorage.setItem(key, JSON.stringify(value))
  } catch {
    /* 存储不可用时忽略：刷新后只是回到默认状态。 */
  }
}
