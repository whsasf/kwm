<template>
<div class="Project">
    <myhead myTitle="关键词管理系统" :myProject="currentComponent" :myName="currentUserName" :myDepartment="currentUserDepartment"></myhead>
    <div class="Project-main">
        <router-view :key="refreshRouteKey" />
    </div>
</div>
</template>

<script>
import {
    mapState,
    mapMutations
} from 'vuex'
import Myhead from '@/components/Myhead.vue'
export default {
    name: 'Main',
    data() {
        return {
            currentUserName: ''
        }
    },
    components: {
        'myhead': Myhead,
    },
    computed: {
        ...mapState(['currentComponent', 'refreshRouteKey'])
    },
    created() {
        this.currentUserName = localStorage.getItem('kwmUser')
        this.currentUserDepartment = localStorage.getItem('kwmdepart')
    },
    beforeDestroy() {},
    methods: {
        ...mapMutations(['changeCurrentComponent'])
    }
}
</script>

<style>
.projectScope .ivu-tabs-nav-scroll {
    display: flex !important;
    justify-content: center !important
}

.layout-sider.ivu-layout-sider.ivu-layout-sider-collapsed .ivu-menu-submenu-title>i.ivu-icon.ivu-icon-ios-arrow-down.ivu-menu-submenu-title-icon {
    display: none !important
}

.layout-sider.ivu-layout-sider.ivu-layout-sider-collapsed .ivu-menu-submenu-title>span {
    text-align: center
}

.layout-sider.ivu-layout-sider.ivu-layout-sider-collapsed .ivu-menu-submenu-title {
    padding: 20px 5px
}

.projectScope .ivu-tabs-bar {
    border-bottom: 0px
}

.ivu-card-body {
    padding: 5px 0 !important
}
</style>
