const open = function () {
    let vm = this
    return [
      {
      // type：‘’  可以通过type类型来判断展示那些组件内容
        modules: [
          {
            id: 'baseInfo',
            refName: 'baseInfo',
            component: () => import('@/component/open/BaseInfo')
          },
          {
            id: 'lineInfo',
            refName: 'lineInfo',
            component: () => import('@/component/open/OpenInfo')
          },
          {
            id: 'reviewInfo',
            refName: 'reviewInfo',
            component: () => import('@/component/open/CommentReview')
          },
          {
            id: 'orderInfo',
            refName: 'orderInfo',
            component: () => import('@/component/open/OrderInfo')
          }
        ]
      }
    ]
  }
  
  export const openModules = vm => {
    return open.call(vm)
  }