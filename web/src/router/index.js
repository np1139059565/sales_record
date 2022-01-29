import Vue from 'vue'
import Router from 'vue-router'
import Index from '@/components/Index'

import Trend from '@/components/Trend'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'Index',
      component: Index
    },
    {
      path: '/trend',
      name: 'Trend',
      component: Trend
    }
  ]
})
