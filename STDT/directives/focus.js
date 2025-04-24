import { nextTick } from 'vue'

export const focus = {
  mounted: (el) => {
    // 使用Vue的nextTick确保组件已完全挂载
    nextTick(() => {
      setTimeout(() => {
        // 获取uni-easyinput组件实例
        const instance = el.__vueParentComponent?.proxy
        if (instance && typeof instance.onFocus === 'function') {
          // 如果是uni-easyinput组件，调用其onFocus方法
          instance.onFocus()
        } else if (el.tagName === 'INPUT') {
          // 如果是原生input元素
          el.focus()
        }
      }, 100)
    })
  }
}