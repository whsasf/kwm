<template>
<div class="Article-see-Url-config">
    <i-modal v-model="showSeeUrlConfig" :closable="false" :mask-closable="false" :scrollable="true">
        <div class="Article-see-Url-config-content" v-if="showSeeUrlConfig && url2SeeData !== ''">
            <h1> URL配置</h1>
            <h3>url: {{url2SeeData.rootUrl}}</h3>
            <br>
            <div class="scrolll">
                <h3>允许路径</h3>
                <ul>
                    <li v-for="(item,index) in url2SeeData.urlIncludePath" :key="index">
                        <span class="seeUrlConfig-path">{{item.path}}</span>
                        <span class="seeUrlConfig-type">{{item.type}}</span>
                    </li>
                </ul>
                <br>
                <h3>排除路径</h3>
                <ul>
                    <li v-for="(item,index) in url2SeeData.urlExcludePath" :key="index">
                        <span class="seeUrlConfig-path">{{item.path}}</span>
                        <span class="seeUrlConfig-type">{{item.type}}</span>
                    </li>
                </ul>
            </div>
        </div>
        <div slot="footer">
            <i-button type="default" size="large" @click="modalCancel()">关闭</i-button>
        </div>
    </i-modal>
</div>
</template>

<script>
import {
    mapState
} from 'vuex'
export default {
    name: 'seeUrlConfig',
    data() {
        return {
            url2SeeData: '',
        }
    },
    props: ['showSeeUrlConfig', 'url2Sees'],
    computed: {
        ...mapState(['baseurl', 'currentComponent']),

    },
    mounted() {
        // 获取 url对应的信息，去Url 表中查找
        this.fetchUrl2See()
    },
    methods: {
        modalCancel: function () {
            //this.showSeeUrlConfig = false
            this.url2SeeData = ''
            this.$emit('update:showSeeUrlConfig', false)

        },
        fetchUrl2See: function () {
            // console.log('landing ...')
            let self = this
            let Params = {
                'urlPart': self.url2Sees
            }
            self.axios({
                    method: 'get',
                    url: self.baseurl + 'Urls/' + self.currentComponent,
                    params: Params
                })
                .then(res => {
                    // .log(res)
                    if (res.data.count === 0) {
                        self.url2SeeData = {
                            'rootUrl': '找不到,请检查!'
                        }
                    } else {
                        self.url2SeeData = res.data.content[0]
                        // console.log(self.url2SeeData)
                    }
                })
                .catch(err => {
                    console.log(err)
                })
        },
    }
}
</script>

<style scoped>
.Article-see-Url-config-content {
    margin: 0px 10%
}

h1 {
    text-align: center
}

li {
    list-style-type: none;
    margin: 10px 10px 10px 0;
}

.seeUrlConfig-path {
    display: inline-block;
    width: 280px;
    max-width: 280px;
    overflow: auto;
    text-overflow: ellipsis;
    white-space: nowrap;
    color: green;
    padding: 5px 10px;
    border: 1px solid #a6b8c4
}

.seeUrlConfig-type {
    display: inline-block;
    text-overflow: ellipsis;
    white-space: nowrap;
    width: 60px;
    max-width: 60px;
    overflow: auto;
    color: green;
    padding: 5px 10px;
    margin-left: 30px;
    border: 1px solid #a6b8c4
}

.scrolll {
    overflow: auto
}
</style>
