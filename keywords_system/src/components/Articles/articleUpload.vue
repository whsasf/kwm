<template>
<div>
    <i-modal v-model="ArticleWindowShow" title="批量上传编辑" width="60" :closable="false" :mask-closable="false" :styles="{top: '20px'}" :scrollable="true">

        <div class="articleitemPage">

            <i-form ref="Alldata" :model="Alldata" :label-width="100">

                <div v-for="(item, index) in Alldata.data" :key="index">
                    <div class="loop">
                        <i-formItem :label="'来源' + (parseInt(index) + 1)">
                            <i-input type="text" v-model="item.root" placeholder="请输入root"></i-input>
                        </i-formItem>

                        <i-formItem :label="'url'">
                            <i-input type="text" v-model="item.url" placeholder="请输入url"></i-input>
                        </i-formItem>

                        <i-formItem :label="'title'">
                            <i-input type="text" v-model="item.title" placeholder="请输入title"></i-input>
                        </i-formItem>
                        <div class="flexs">
                            <label class="mylabel">关键词</label>
                            <i-select v-model="item.keywords" multiple filterable allow-create>
                                <i-option v-for="(item2,index2) in item.keywords" :value="item2" :key="index2">{{ item2 }}</i-option>
                            </i-select>
                        </div>

                        <i-formItem label="desciption">
                            <i-input type="text" v-model="item.desciption" placeholder="请输入desciption"></i-input>
                        </i-formItem>
                        <i-formItem label="rawContent">
                            <i-input type="text" v-model="item.rawContent" placeholder="请输入rawContent"></i-input>
                        </i-formItem>
                        <i-formItem label="body">
                            <i-input type="text" v-model="item.body" placeholder="请输入body"></i-input>
                        </i-formItem>
                        <div class="flexs">
                            <label class="mylabel">目录</label>
                            <i-select v-model="item.category" multiple>
                                <i-option v-for="(item3,index3) in rowCategoies" :value="item3" :key="index3">{{ item3 }}</i-option>
                            </i-select>
                        </div>
                    </div>
                </div>
            </i-form>
        </div>
        <div slot="footer">
            <i-button type="default" size="large" @click="modalCancel('Alldata')">取消</i-button>
            <i-button type="primary" size="large" @click="modalOk('Alldata')">提交</i-button>
        </div>

    </i-modal>
</div>
</template>

<script>
import {
    mapState
} from 'vuex'
export default {
    name: 'articleUpload',
    data() {
        return {}
    },
    props: ['ArticleWindowShow', 'rowCategoies', 'Alldata'],
    computed: {
        ...mapState(['baseurl', 'currentComponent'])
    },
    beforeDestroy() {},
    mounted() {
        //if (JSON.stringify(this.Alldata) !== '{}'){
        //    console.log(this.Alldata.data)
        //}
    },
    methods: {
        modalOk: function (name) {
            let self = this
            let final = self.Alldata.data
            // console.log(final)
            self.$emit('uploadArticlesnewItem', final)
            self.$refs[name].resetFields()
            self.$emit('update:ArticleWindowShow', false)
        },
        modalCancel: function (name) {
            this.$refs[name].resetFields()
            this.$emit('update:ArticleWindowShow', false)

        }
    }
}
</script>

<style scoped>
.articleitemPage {
    height: 500px;
    max-height: 550px;
    overflow: auto
}

.mylabel {
    width: 112px;
    text-align: right;
    padding: 10px 12px
}

.flexs {
    display: flex
}

.loop {
    border: 1px solid red;
    border-radius: 5px;
    padding: 20px 10px;
    margin-bottom: 10px;
}
</style>
