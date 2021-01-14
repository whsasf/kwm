<template>
<div class="Myhead">
    <div class="head-part1">
        <h1 @click="gotoProjectView" class="Mymenu-title" name="title">{{ myTitle }}</h1>
        <div class="Mymenu-collpse" name="collpse" v-show="showTogether">
            <span class="Mymenu-collpse-collpse" title="隐藏侧边栏" v-if="collpsed" @click="changeCollpsed(false)">
                <el-icon class="el-icon-s-fold"></el-icon>
            </span>
            <span class="Mymenu-collpse-collpse" title="展开侧边栏" v-else @click="changeCollpsed(true)">
                <el-icon class="el-icon-s-unfold"></el-icon>
            </span>
        </div>
        <span class="Mymenu-collpse-refresh" @click="refresh">
            <i-icon type="md-refresh" title="刷新列表"></i-icon>
        </span>
        <span v-show="showTogether" class="Mymenu-collpse-projectView" @click="gotoProjectView">
            <i-icon type="md-pricetags" title="进入项目设置"></i-icon>
        </span>
    </div>

    <div class="Mymenu-project" name="projecctName">{{ myProject}}</div>

    <i-menu class="Mymenu" mode="horizontal" :theme="theme1" active-name="" @on-select="signout">
        <i-submenu name="user" class="Mymenu-user">
            <template slot="title">
                <i-icon type="ios-contact" />
                {{ myName|getName}}
            </template>
            <i-menuItem class="Mymenu-user-sub Mymenu-user-disable" name="user-department">
                <i-icon type="md-people"></i-icon>
                {{myDepartment}}
            </i-menuItem>
            <!--
            <i-menuItem class="Mymenu-user-sub" name="user-setting">
                <i-icon type="ios-settings"></i-icon>
                设置
            </i-menuItem>
            -->
            <i-menuItem class="Mymenu-user-sub" name="user-signout">
                <i-icon type="md-exit"></i-icon>
                退出登录
            </i-menuItem>
        </i-submenu>
        <div class="dummy"></div>
    </i-menu>
</div>
</template>

<script>
import {
    Icon
} from 'element-ui';
import {
    mapState,
    mapMutations
} from 'vuex'
export default {
    name: 'Myhead',
    data() {
        return {
            theme1: 'light'
        }
    },
    props: {
        myTitle: String,
        myProject: String,
        myName: String,
        myDepartment: String
    },
    computed: {
        ...mapState(['currentComponent', 'collpsed', 'refreshRouteKey']),
        showTogether: function () {
            if (this.currentComponent === '项目管理') {
                return false
            } else {
                return true
            }
        }
    },
    components: {
        'el-icon': Icon
    },
    filters: {
        getName: function (value) {
            if (!value) return ''
            value = value.toString()
            return value.split('@')[0]
        }
    },
    methods: {
        ...mapMutations(['changeCollpsed', 'changeRefreshRouteKey']),
        gotoProjectView: function () {
            // localStorage.removeItem('nav_selected')
            this.$router.push('/Management')
            this.changeCollpsed(true)
        },
        refresh: function () {
            this.changeRefreshRouteKey(this.refreshRouteKey + 1)
            this.changeCollpsed(true)
        },
        signout: function (name) {
            if (name === 'user-signout') {
                // 删除 本地 jwt 和 用户名
                localStorage.removeItem('kwmUser')
                localStorage.removeItem('kwmjWT')
                // localStorage.removeItem('nav_selected')
                this.$Message.success('登出...');
                this.$router.push('/Account/Signin')
                this.changeCollpsed(true)
            }
        }
    }
}
</script>

<style scoped>
.Myhead {
    position: sticky;
    margin: 0;
    top: 0px;
    z-index: 6 !important;
    display: flex;
    height: 60px;
    background-color: #fff;
    align-items: center;
    border-bottom: 1px solid #dcdee2;
}

.head-part1 {
    text-align: left;
    flex: 1;
    margin: 0 15px;
}

.Mymenu-project {
    flex: 1;
    text-align: center;
    font-size: 1.7rem;
    font-weight: bold;
    color: black !important;
    pointer-events: none;
    color: #212891 !important;
    overflow: auto;
    text-overflow: ellipsis;
    white-space: nowrap;
    text-align: center
}

.Mymenu {
    flex: 1;
    font-weight: bold;
    font-size: 1.1rem;
    display: flex;
    justify-content: flex-end;
}

.dummy {
    width: 30px
}

.Mymenu-title {
    flex: 4;
    font-size: 1.7rem;
    color: #212891 !important;
    text-align: left;
    display: inline-block;
    margin-right: 10px;
}

.Mymenu-collpse {
    margin-left: 10px;
    margin-right: 10px;
    flex: 1;
    font-size: 1.5rem;
    color: #057009 !important;
    text-align: left;
    display: inline-block
}

.Mymenu-collpse-collpse {
    font-size: 1.5rem;
    cursor: pointer;
}

.Mymenu-collpse-collpse:hover {
    padding: 5px 0;
    background-color: #e0dbd9;
    box-shadow: 1px 1px 1px #888888;
}

.Mymenu-collpse-refresh {
    margin-left: 10px;
    color: #057009;
    cursor: pointer;
    font-size: 1.5rem;
}

.Mymenu-collpse-refresh:hover {
    padding: 5px 0;
    box-shadow: 1px 1px 1px #888888;
    background-color: #e0dbd9
}

.Mymenu-collpse-projectView {
    margin-left: 20px;
    font-size: 1.5rem;
    cursor: pointer;
    color: #057009;
}

.Mymenu-collpse-projectView:hover {
    padding: 5px 0;
    box-shadow: 1px 1px 1px #888888;
    background-color: #e0dbd9
}

.Mymenu-user-sub {
    text-align: left
}

.Mymenu-user-disable {
    pointer-events: none;
}

.Mymenu-collpse {
    font-size: 1.3rem
}

h1:hover {
    cursor: pointer
}
</style>
