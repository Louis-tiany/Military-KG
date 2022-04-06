import Vue from 'vue'

// 导入ElementUI
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'

import App from './App.vue'
import router from './router'
import store from './store'
import axios from 'axios'

// 进度条
// 引入nprogress插件
import NProgress from 'nprogress'
// 这个nprogress样式必须引入
import 'nprogress/nprogress.css'

Vue.use(ElementUI)
Vue.config.productionTip = false
Vue.prototype.$axios = axios

NProgress.configure({
  easing: 'ease',
  // 递增进度条的速度
  speed: 500,
  // 是否显示加载ico
  showSpinner: false,
  // 自动递增间隔
  trickleSpeed: 200,
  // 初始化时的最小百分比
  minimum: 0.3
})

axios.interceptors.request.use(config => {
  NProgress.start()
  config.headers.Authorization = sessionStorage.getItem('token')
  return config
})

axios.interceptors.response.use(config => {
  NProgress.done()
  return config
})

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')
