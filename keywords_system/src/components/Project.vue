<template>
<div class="Management-projects-i-layout layout">
    <i-layout :default-collapsed="false">
        <i-sider class="layout-sider" ref="side1" hide-trigger collapsible :collapsed-width="50" v-model="isCollapsed">
            <i-menu class="layout-sider-menu" :active-name="activeIndex" theme="light" width="auto" :class="menuitemClasses" @on-select="ChangeSelect" :open-names="['1','2']">
                <i-submenu class="layout-sider-menu-title" name="1">
                    <template slot="title">
                        <span>
                            <i-poptip class="mypiptip" v-show="!collpsed" trigger="hover" :transfer="true" placement="right-start">
                                <el-icon class="el-icon-s-management"></el-icon>
                                <div slot="content">
                                    <i-menuItem class="sidebar-item" v-show="!collpsed" name="1-1">
                                        <router-link :to="'/Project/'+ (currentComponent) + '/Url'">Url管理</router-link>
                                    </i-menuItem>
                                    <i-menuItem class="sidebar-item" v-show="!collpsed" name="1-2">
                                        <router-link :to="'/Project/'+ (currentComponent) + '/Articles'">查看语料</router-link>
                                    </i-menuItem>
                                </div>
                            </i-poptip>
                            <el-icon v-show="collpsed" class="el-icon-s-management"></el-icon>
                            <span v-show="collpsed">语料资源管理</span>
                        </span>
                    </template>
                    <i-menuItem class="sidebar-item" v-show="collpsed" name="1-1">
                        <router-link :to="'/Project/'+ (currentComponent) + '/Url'">Url管理</router-link>
                    </i-menuItem>
                    <i-menuItem class="sidebar-item" v-show="collpsed" name="1-2">
                        <router-link :to="'/Project/'+ (currentComponent) + '/Articles'">查看语料</router-link>
                    </i-menuItem>
                </i-submenu>

                <i-submenu name="2">
                    <template slot="title">
                        <span>
                            <i-poptip v-show="!collpsed" trigger="hover" :transfer="true" placement="right-start">
                                <el-icon class="el-icon-notebook-2"></el-icon>
                                <div slot="content">
                                    <i-menuItem class="sidebar-item" v-show="!collpsed" name="2-1">
                                        <router-link :to="'/Project/'+ (currentComponent) + '/basicWords'">基础词表</router-link>
                                    </i-menuItem>
                                    <i-menuItem class="sidebar-item" v-show="!collpsed" name="2-2">
                                        <router-link :to="'/Project/'+ (currentComponent) + '/extendedWords-bacicView'">拓展词表</router-link>
                                    </i-menuItem>
                                    <i-menuItem class="sidebar-item" v-show="!collpsed" name="2-4">
                                        <router-link :to="'/Project/'+ (currentComponent) + '/userDict'">用户词典</router-link>
                                    </i-menuItem>
                                    <i-menuItem class="sidebar-item" v-show="!collpsed" name="2-3">
                                        <router-link :to="'/Project/'+ (currentComponent) + '/stopDict'">停止词典</router-link>
                                    </i-menuItem>
                                    <i-menuItem class="sidebar-item" v-show="!collpsed" name="2-6">
                                        <router-link :to="'/Project/'+ (currentComponent) + '/invalidDict'">无效词典</router-link>
                                    </i-menuItem>
                                    <i-menuItem class="sidebar-item" v-show="!collpsed" name="2-5">
                                        <router-link :to="'/Project/'+ (currentComponent) + '/usageTag'">用途标签</router-link>
                                    </i-menuItem>
                                </div>
                            </i-poptip>
                            <el-icon v-show="collpsed" class="el-icon-notebook-2"></el-icon>
                            <span v-show="collpsed">词根管理</span>
                        </span>
                    </template>
                    <i-menuItem class="sidebar-item" v-show="collpsed" name="2-1">
                        <router-link :to="'/Project/'+ (currentComponent) + '/basicWords'">基础词表</router-link>
                    </i-menuItem>
                    <i-menuItem class="sidebar-item" v-show="collpsed" name="2-2">
                        <router-link :to="'/Project/'+ (currentComponent) + '/extendedWords-bacicView'">拓展词表</router-link>
                    </i-menuItem>
                    <i-menuItem class="sidebar-item" v-show="collpsed" name="2-4">
                        <router-link :to="'/Project/'+ (currentComponent) + '/userDict'">用户词典</router-link>
                    </i-menuItem>
                    <i-menuItem class="sidebar-item" v-show="collpsed" name="2-3">
                        <router-link :to="'/Project/'+ (currentComponent) + '/stopDict'">停止词典</router-link>
                    </i-menuItem>
                    <i-menuItem class="sidebar-item" v-show="collpsed" name="2-6">
                        <router-link :to="'/Project/'+ (currentComponent) + '/invalidDict'">无效词典</router-link>
                    </i-menuItem>
                    <i-menuItem class="sidebar-item" v-show="collpsed" name="2-5">
                        <router-link :to="'/Project/'+ (currentComponent) + '/usageTag'">用途标签</router-link>
                    </i-menuItem>
                </i-submenu>
            </i-menu>
        </i-sider>
        <i-layout>
            <i-content class="layout-content" :class="{'collpsed':!collpsed}">
                <currentPath class="breadCrumb"></currentPath>
                <router-view />
            </i-content>
        </i-layout>
    </i-layout>
</div>
</template>

<script>
import {
    mapMutations,
    mapState
} from 'vuex'
import {
    Icon
} from 'element-ui';
import currentPath from '@/components/currentPath.vue'
export default {
    name: 'Project',
    data() {
        return {
            routerActiveMap: {
                'Url': '1-1',
                'Articles': '1-2',
                'basicWords': '2-1',
                'extendedWords': '2-2',
                'stopDict': '2-3',
                'userDict': '2-4',
                'usageTag': '2-5',
                'invalidDict': '2-6'
            },
            showit1: false,
            // activeIndex: '',
            isCollapsed: false,
            content: ['hi', 'hello']
        }
    },
    computed: {
        ...mapState(['collpsed', 'currentComponent']),
        rotateIcon() {
            return [
                'menu-icon',
                this.isCollapsed ? 'rotate-icon' : ''
            ];
        },
        menuitemClasses() {
            return [
                'menu-item',
                this.isCollapsed ? 'collapsed-menu' : ''
            ]
        },
        activeIndex: function () {
            let temp = this.$route.path.split('/')
            // console.log('active',this.routerActiveMap[temp[temp.length -1]])
            let ii = temp[temp.length - 1]
            if (ii.indexOf('extendedWords') !== -1) {
                ii = 'extendedWords'
            }
            return this.routerActiveMap[ii]
        }
    },
    created() {
        this.changeCurrentComponent(this.$route.params.project)
    },
    beforeMount() {

    },
    mounted() {
        // console.log(this.isCollapsed)
        // this.grecoverSeleccted()
        // console.log('path',this.$route.path)
    },
    components: {
        'el-icon': Icon,
        'currentPath': currentPath
    },
    watch: {
        collpsed: function () {
            //console.log('switch')
            this.collapsedSider()
        }
    },
    methods: {
        ...mapMutations(['changeCurrentComponent']),
        collapsedSider() {
            this.$refs.side1.toggleCollapse();
        },
        ChangeSelect: function (name) {
            localStorage.setItem('nav_selected', name)
        },
        //grecoverSeleccted: function (){
        //        if (localStorage.getItem('nav_selected')){
        //          this.activeIndex = localStorage.getItem('nav_selected')
        //        }
        //      }
    }
}
</script>

<style scoped>
.layout-sider-menu.ivu-menu.ivu-menu-light.ivu-menu-vertical.menu-item {
    height: 100%
}

.layout {
    border: 1px solid #d7dde4;
    background: #f5f7f9;
    position: relative;
    border-radius: 4px;
    overflow: hidden;

}

.layout-sider.ivu-layout-sider {
    height: calc(100vh - 60px);
    background: #fff;
    width: 150px !important;
    min-width: 0px !important;
    position: fixed;
    top: 61px;
    left: 1px;
    text-align: left !important;
    font-weight: bold;
}

.layout-sider.ivu-layout-sider.ivu-layout-sider-collapsed {
    width: 50px !important;
    min-width: 0px !important;

}

.layout-sider.ivu-layout-sider span {
    width: auto
}

.layout-sider.ivu-layout-sider span {
    width: auto
}

.menu-icon {
    transition: all .3s;
}

.rotate-icon {
    transform: rotate(-90deg);
}

.menu-item span {
    display: inline-block;
    overflow: hidden;
    width: 69px;
    text-overflow: ellipsis;
    white-space: nowrap;
    vertical-align: bottom;
    transition: width .2s ease .2s;
}

.menu-item i {
    transform: translateX(0px);
    transition: font-size .2s ease, transform .2s ease;
    vertical-align: middle;
    font-size: 16px;
}

.collapsed-menu span {
    width: 0px;
    transition: width .2s ease;
}

.collapsed-menu i {
    transform: translateX(5px);
    transition: font-size .2s ease .2s, transform .2s ease .2s;
    vertical-align: middle;
    font-size: 22px;
}

.layout-content {
    padding-top: 40px;
    margin-left: 160px;
    margin-right: 20px
}

.layout-content.collpsed {
    margin-left: 60px;
    margin-right: 10px
}

.sidebar-item.ivu-menu-item.ivu-menu-item-active.ivu-menu-item-selected {
    color: white !important;
    background-color: #212990
}

.sidebar-item.ivu-menu-item.ivu-menu-item-active.ivu-menu-item-selected a {
    color: white
}

.sidebar-item a {
    color: #212990;
    display: block;
    padding: 15px 5px
}

.ivu-poptip-body-content .sidebar-item a {
    padding: 5px
}

.ivu-menu li {
    padding: 0
}

.ivu-menu-submenu-title span {
    color: #057009
}

>>>.ivu-menu-submenu-title {
    padding: 14px 5px !important
}

.layout-sider.ivu-layout-sider {
    flex: 0 0 150px !important
}

>>>.ivu-icon.ivu-icon-ios-arrow-down.ivu-menu-submenu-title-icon {
    right: 14px
}

.menu-item span {
    overflow: visible
}

.sidebar-item.ivu-menu-item {
    padding-left: 30px !important
}

.ivu-poptip-body-content .sidebar-item.ivu-menu-item {
    padding-left: 5px !important
}

>>>li.sidebar-item.ivu-menu-item:hover {
    background-color: #057009;
    color: #fff !important;

}

>>>li.sidebar-item.ivu-menu-item:hover a {
    color: #fff !important;

}

.breadCrumb {
    margin-bottom: 10px;
    background-color: #eaeaea;
    position: fixed;
    top: 60px;
    z-index: 5;
    width: 100%
}

>>>.ivu-table th {
    background: #fff;
    border-bottom: 10px solid #e8eaec;
}

>>>.ivu-table-hidden {
    visibility: visible;
}
</style>
