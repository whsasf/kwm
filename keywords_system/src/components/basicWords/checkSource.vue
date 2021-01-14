<template>
<div class="checkSource">
    <i-modal v-model="checkSourceShow" :title="'查看基础词出处:  '+ '[' +  dataRequired[0] + ']'" width="800" :closable="false" :mask-closable="false" :scrollable="true">

        <div class="both">
            <div class="left">
                <h2>出处</h2>
                <div class="body">
                    <div class="ll" v-for="(item,index) in dataRequired[1]" :key="index" v-bind:class="{ selected: index === currentShow }" @click.prevent="fetchBody(index)">
                        <a>{{(index +1 )+ ' : ' +item}}</a>
                    </div>
                </div>
            </div>
            <div class="right">
                <h2>语料</h2>
                <div class="body" v-html="'<p>' + body[currentShow] + '</p>'">
                </div>
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
    name: 'checkSource',
    data() {
        return {
            body: {
                0: ''
            },
            currentShow: 0, // 默认显示第一个
            isActive: false
        }
    },
    computed: {
        ...mapState(['baseurl', 'currentComponent']),
    },
    mounted() {
        // 拉取第一个 出处的 body数据
        if (this.dataRequired) {
            this.fetchBody(0)
        }
    },
    props: ['checkSourceShow', 'dataRequired'],
    methods: {
        modalCancel: function () {
            this.$emit('update:checkSourceShow', false)
        },
        fetchBody: function (index) {
            let self = this
            // console.log('获取第' + index + '个!')
            // console.log(index,'oooo',self.dataRequired[1])
            if (self.body[index] && self.body[index] !== '') {
                // 已经获取过，直接返回
                self.currentShow = index
            } else {
                // 如果不存在，才获取
                let target = self.dataRequired[1][index]
                // console.log(target)
                if (target === '手动添加') {
                    // 无需远端查询，直接显示该词
                    self.body[index] = '<strong style="background-color: yellow; color:red">' + self.dataRequired[0] + '</strong>'
                    self.currentShow = index
                } else {
                    // 出处是 本地文件 或 url ，处理逻辑一致
                    let papams = {
                        'urlItem': target.trim(),
                        'word': self.dataRequired[0]
                    }
                    // console.log('papams',papams)
                    self.basicFetch(index, papams)
                }
            }

        },
        basicFetch: function (index, Params) {
            let self = this
            self.axios({
                    method: 'get',
                    url: self.baseurl + 'Articles/body/es/' + self.currentComponent,
                    params: Params
                })
                .then(res => {
                    //console.log(res)
                    self.body[index] = res.data[0].highlight.body[0]
                    self.currentShow = index
                })
                .catch(err => {
                    console.log(err)
                })
        }
    }
}
</script>

<style scoped>
a {
    color: black
}

.both {
    display: flex;
    justify-content: center;
    height: 400px;
    max-height: 400px;
}

.left {
    width: 300px;
}

.left .body {
    border: 1px solid red;
    overflow: auto;
    height: 360px;
}

.left .body .ll {
    margin: 5px
}

.left .body .selected {
    background-color: #5fd063
}

.right {
    margin-left: 10px;
    width: 400px;
}

strong {
    display: block;
    background-color: yellow
}

.right .body {
    color: #057009;
    border: 1px solid green;
    overflow: auto;
    height: 360px;
}
</style>
