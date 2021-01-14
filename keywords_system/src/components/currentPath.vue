<template>
<div class="currentPath">
    <div class="currentPath-title">
        <i-icon type="ios-compass-outline" size="20"></i-icon>当前位置:
    </div>
    <div class="currentPath-both" v-for="(path,index) in paths" :key="index">
        <div class="normal" v-if="index !== paths.length -1 && index !== paths.length -2" @click="toWhere(index)">{{decodeURI(path) + ' /'}}</div>
        <div class="normal2" v-else-if="index === paths.length -2" @click="toWhere(index)">{{decodeURI(path) + ' /'}}</div>
        <div class="last" v-else>{{mapDdict[decodeURI(path)]}}</div>
    </div>
    <div class="rright" v-if="searchDisplay">
        <p class="aa">当前查询: <span class="cc">{{searchDisplay}}</span></p>
    </div>
</div>
</template>

<script>
import {
    mapState,
    mapMutations
} from 'vuex'

export default {
    name: 'currentPath',
    data() {
        return {
            mapDdict: {
                'Url': 'Url管理',
                'Articles': '查看语料',
                'basicWords': '基础词表',
                'extendedWords-bacicView': '扩展词表-默认视图',
                'extendedWords-topicView': '扩展词表-主题视图',
                'extendedWords-inheritView': '扩展词表-母词视图',
                'stopDict': '停止词典',
                'userDict': '用户词典',
                'usageTag': '用途标签',
                'invalidDict': '无效词典'
            }
        }
    },
    mounted() {},
    computed: {
        ...mapState(['searchDisplay']),
        paths: function () {
            let temp = this.$route.path.slice(1).split('/')
            return temp
        }
    },
    methods: {
        ...mapMutations(['changeCollpsed']),
        toWhere: function (index) {
            // console.log(index,this.paths)
            let newRoute = '/'
            for (let ele in this.paths) {
                if (parseInt(ele) !== index) {
                    newRoute = newRoute + decodeURI(this.paths[ele]) + '/'
                } else {
                    newRoute = newRoute + decodeURI(this.paths[ele])
                    break
                }
            }
            this.changeCollpsed(true)
            this.$router.push({
                'path': newRoute
            })
        }
    }
}
</script>

<style scoped>
.currentPath {
    display: flex;
    align-items: center
}

.currentPath-title {
    font-size: 0.9rem;
    margin-right: 10px
}

.currentPath-both {
    font-size: 1.1;
    font-weight: bold;
    color: #057009
}

.currentPath-both .normal {
    margin-right: 10px;

}

.currentPath-both .normal2 {
    max-width: 200px;
    overflow: auto;
    text-overflow: ellipsis;
    white-space: nowrap;
    text-align: left
}

.currentPath-both .normal:hover {
    cursor: pointer
}

.currentPath-both .normal2:hover {
    cursor: pointer
}

.currentPath-both .last {
    color: #212891;
    margin-left: 5px
}
.rright{
   margin-left: 150px
}

.aa{
    color: #212891
}
.cc{
    color: #057009;
    font-weight: 800
}
</style>
