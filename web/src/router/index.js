import Vue from 'vue'
import Router from 'vue-router'
import Index from '@/components/Index'

import Trend from '@/components/Trend'

import Table from '@/components/Table'

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
    },
    {
      path: '/table',
      name: 'Table',
      component: Table
    }
  ]
})
