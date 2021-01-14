import Vue from 'vue'
import VueRouter from 'vue-router'
import Account from '../views/Account.vue'
import Signin from '../components/Account/Signin.vue'
import Signup from '../components/Account/Signup.vue'
import store from '@/store'

Vue.use(VueRouter)


const originalPush = VueRouter.prototype.push
   VueRouter.prototype.push = function push(location) {
   return originalPush.call(this, location).catch(err => err)
}

const routes = [
  {
    path: '/Account',
    name: 'Account',
    redirect: '/Account/Signin',
    component: Account,
    children: [
      {
        path: 'Signin',
        name: 'Signin',
        component: Signin
      },
      {
        path: 'Signup',
        name: 'Signup',
        component: Signup
      },
      {
        path: '*',
        redirect: '/Account/Signin'
      }
    ]
  },
  {
    path: '/',
    name: '/',
    redirect: '/Management',
    component: function () {
      return import('../views/Main.vue')
    },
    children: [
      {
        path: 'Management',
        name: 'Management',
        component: function () {
          return import('../components/Management.vue')
        },
      },
      {
        path: 'Project/:project',
        name: 'project',
        redirect: '/Project/:project/Url',
        component: function () {
          return import('../components/Project.vue')
        },
        children: [
          {
            path: 'Url',
            name: 'Url',
            component: function () {
              return import('../components/Url.vue')
            }
          },
          {
            path: 'Articles',
            name: 'Articles',
            component: function () {
              return import('../components/Articles.vue')
            }
          },
          {
            path: 'basicWords',
            name: 'basicWords',
            component: function () {
              return import('../components/basicWords.vue')
            }
          },
          {
            path: 'extendedWords-bacicView',
            name: 'extendedWords-basicView',
            component: function () {
              return import('../components/extendedWordsBasic.vue')
            }
          },
          {
            path: 'extendedWords-topicView',
            name: 'extendedWords-topicView',
            component: function () {
              return import('../components/extendedWordsTopic.vue')
            }
          },
          {
            path: 'extendedWords-inheritView',
            name: 'extendedWords-inheritView',
            component: function () {
              return import('../components/extendedWordsInherit.vue')
            }
          },
          {
            path: 'stopDict',
            name: 'stopDict',
            component: function () {
              return import('../components/stopDict.vue')
            }
          },

          {
            path: 'userDict',
            name: 'userDict',
            component: function () {
              return import('../components/userDict.vue')
            }
          },
          {
            path: 'invalidDict',
            name: 'invalidDict',
            component: function () {
              return import('../components/invalidDict.vue')
            }
          },
          {
            path: 'usageTag',
            name: 'usageTag',
            component: function () {
              return import('../components/usageTag.vue')
            }
          },
          {
            path: '*',
            redirect: '/Project/:project/Url'
          },
        ]
      },
      {
        path: '*',
        redirect: 'Management'
      }
    ]
  },
  {
    path: '*',
    redirect: '/'
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

// reset SearchDisplay before enter new router
router.beforeEach((to, from, next) => {
  store.commit('changeSearchDisplay','')
  next()
})


export default router
