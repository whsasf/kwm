import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    collpsed: true,
    currentComponent: '',
    searchDisplay: '',
    refreshRouteKey: 1,
    baseurl: 'http://127.0.0.1:3000/',
    //baseurl: 'http://114.67.113.229:8080/',
    crowlerAddr: 'http://192.168.20.85:8000/',
    expandAddr: 'http://192.168.20.172:8000/',
  },
  mutations: {
    changeCollpsed(state,newvalue){
      state.collpsed = newvalue
    },
    changeSearchDisplay(state,newvalue){
      state.searchDisplay = newvalue
    },
    changeRefreshRouteKey(state,newvalue){
      state.refreshRouteKey = newvalue
    },
    changeCurrentComponent (state,newvalue) {
      state.currentComponent = newvalue
    }
  },
  actions: {
  },
  modules: {
  }
})
