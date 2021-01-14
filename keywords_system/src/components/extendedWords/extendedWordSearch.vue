<template>
<div class="url-url-select ivu-select ivu-select-visible ivu-select-single ivu-select-default" style="position: relative">
    <i-input v-model="searchItem" :clearable="true" search placeholder="输入关键词进行模糊查询" @on-change="extendedWordsSearch" @on-search="batchSearch" @on-clear="resetInput" />
    <div ref='urlInputOptions' v-show="searchResult.length !== 0" class="url-url-select-option ivu-select-dropdown" x-placement="bottom-start" style="position: relative">
        <div v-if="this.wordItem === 'topicWord'">
            <i-option @click.native="singleSearch([item['_id']['$oid'],item.highlight.topicWord[0].replace(/<strong>/g,'').replace(/<\/strong>/g,'')])" style="text-align: left" v-for="(item,index) in searchResult" :tag="item['id']" :value="index" :key="index" v-html="index + 1 + ':'  + item.word + '-' +item.highlight.topicWord[0] + '-' + item['_id']['$oid']"></i-option>
        </div>
        <div v-else-if="this.wordItem === 'word'">
            <i-option @click.native="singleSearch([item['_id']['$oid'],item.highlight.word[0].replace(/<strong>/g,'').replace(/<\/strong>/g,'')])" style="text-align: left" v-for="(item,index) in searchResult" :tag="item['_id']['$oid']" :value="index" :key="index" v-html="index + 1 + ': ' + item.highlight.word[0]  + '  -   ' + item['_id']['$oid'] "></i-option>
        </div>
         <div v-else>
            <i-option @click.native="singleSearch([item['_id']['$oid'],item.highlight.word[0].replace(/<strong>/g,'').replace(/<\/strong>/g,'')])" style="text-align: left" v-for="(item,index) in searchResult" :tag="item['_id']['$oid']" :value="index" :key="index" v-html="index + 1 + ': ' + item.highlight.word[0]  + '  -   ' + item['_id']['$oid'] "></i-option>
        </div>
    </div>
</div>
</template>

<script>
import {
    mapState
} from 'vuex'
export default {
    name: 'extendedWordSearch',
    data() {
        return {
            searchItem: '',
            searchResult: []
        }
    },
    computed: {
        ...mapState(['baseurl', 'currentComponent']),
    },
    props: ['wordItem'],
    methods: {
        singleSearch: function (item) {
            this.$emit('single-search', item)
        },
        resetInput: function () {
            // 内外都 reset
            this.searchItem = ''
            this.searchResult = []
            this.$emit('reset-input')
        },
        batchSearch: function () {
            //console.log('this.searchItem', this.searchItem)
            this.$emit('batch-search', this.searchItem)
        },
        extendedWordsSearch: function () {
            // console.log('extended words Search running ...')
            // 实时查询候选 选项
            // 选择特定条目时的动作: 进入 singleSearch
            let self = this
            let query = self.searchItem
            this.$emit('sync-query', query)
            //发往后端，进行查询,如果 query 不为空 
            if (query !== '') {
                // let Params = {'urlPart':query.toLowerCase()}
                // 全部返回，所以 页面设置 为  0，0 
                let showReturn = ''
                let highlight = ''
                let fetch_url = ''
                if (self.wordItem === 'word'){
                    showReturn = encodeURIComponent(['word', '_id'])
                    highlight = encodeURIComponent(['word'])
                    fetch_url = 'extendedWords/es/'
                } else if (self.etype === 'topicWord'){
                    showReturn = encodeURIComponent(['word','topicWord', '_id'])
                    highlight = encodeURIComponent(['word','topicWord'])
                    fetch_url = 'extendedWords/Topic/es/'
                } else{
                    showReturn = encodeURIComponent(['word','mword', '_id'])
                    highlight = encodeURIComponent(['word','mword'])
                    fetch_url = 'extendedWords/Inherit/es/'
                }
                let Params = {
                    'wordPart': self.searchItem.toLowerCase(),
                    'currentPage': 0,
                    'pageSize': 0,
                    //'aggGroupBy': encodeURIComponent(['topicWord']),
                    'showReturn': showReturn,//encodeURIComponent(['word', 'topicWord', '_id']),
                    'highlight': highlight,//encodeURIComponent(['word', 'topicWord']),
                    'wordItem': this.wordItem
                }
                //if (this.wordItem === 'topic') {
                //    url = self.baseurl + 'extendedWords/Topic/es/' + self.currentComponent
                //} else {
                // url = self.baseurl + fetch_url + self.currentComponent
                //}
                // self.fetchItems(Params)
                self.axios({
                        method: 'get',
                        url: self.baseurl + fetch_url + self.currentComponent, //self.baseurl + 'extendedWords/' + self.currentComponent,
                        params: Params
                    })
                    .then(res => {
                        //console.log('res', res)
                        // if (res.data.count !== ''){
                        //   self.projectCount = res.data.count
                        // }
                        self.searchResult = res.data.content
                        // console.log(self.searchResult)
                    })
                    .catch(err => {
                        console.log(err)
                        // self.$Message.error(err.response.data.detail);
                    })
            } else {
                self.searchResult = []
                self.resetInput()
            }
        },
    }
}
</script>

<style>
.url-url-select-option.ivu-select-dropdown strong {
    background-color: yellow
}

.ivu-icon.ivu-icon-ios-search.ivu-input-icon.ivu-input-icon-normal.ivu-input-search-icon,
.ivu-icon.ivu-icon-ios-close-circle.ivu-input-icon.ivu-input-icon-clear.ivu-input-icon-normal {
    padding-top: 16px
}

.url-url-select-option.ivu-select-dropdown {
    max-height: 400px;
    overflow: auto
}
</style>
