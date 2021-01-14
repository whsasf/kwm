<template>
<div class="Article-see-detail">
    <i-modal v-model="showSeeDetail" :title="'查看详情:  第' + xcurrentPage +  '页，第' + (xindex + 1 )  + '个, 当前共有' + seeSplitWords.length + '个分词'" width="1050px" :closable="false" :mask-closable="false" :scrollable="true">
        <div class="Article-see-detail-content-total" v-if="showSeeDetail && JSON.stringify(articleDetail) !== '[]'">
            <div class="Article-see-detail-content-total1">
                <div class="article-detail-content-p1">
                    {{seeBody}}
                </div>
                <div class="article-detail-content-p2">
                    <li class="liLine header">
                        <div class="p1">词语</div>
                        <div class="p2">操作</div>
                    </li>
                    <li class="liLine main" v-for="(item,index) in this.seeSplitWords" :key="index">
                        <div class="p1">{{item}}</div>
                        <div class="p2" v-if="item !== '...分词中 ...'">
                            <i-button class="Stop" style="color: #54616f;background-color: #e4f5f7;border: 1px solid green; margin-top: 2px; margin-bottom: 2px" size="small" @click="setStopWord(item,index)">设为停止词</i-button>
                            <i-button class="Invalid" style="color: #7b5ae4;background-color: #e4f5f7;border: 1px solid green; margin-top: 2px; margin-bottom: 2px" size="small" @click="setInvalidWord(item,index)">设为无效词</i-button>
                        </div>
                    </li>
                </div>
            </div>
            <div class="Article-see-detail-content-total2">
                <i-button class="xbutton setInvalid" :disabled="this.seeStatus === '无效'" type="warning" size="default" @click="setUrlInvalid('invalid')" icon="md-warning">设为无效</i-button>
                <i-button class="xbutton setValid" :disabled="this.seeStatus !== '无效' " type="warning" size="default" @click="setUrlInvalid('valid')" icon="md-medkit">设为有效</i-button>
                <i-button class="xbutton addUserDict" type="success" size="default" @click="add2UserDict()">增加用户词</i-button>
            </div>
        </div>
        <div slot="footer">
            <i-button type="primary" :disabled="previousDisabled" size="large" shape="circle" @click="PreviousOne()">上一个</i-button>
            <i-button type="primary" :disabled="nextDisabled" size="large" shape="circle" @click="nextOne()">下一个</i-button>
            <i-button type="default" size="large" @click="modalCancel()">关闭</i-button>
        </div>
    </i-modal>
    <adduserDictWindow :addUserDictWindowShow.sync="addUserDictWindowShow" @re-fenci="fenci(seeUid,type='2')"></adduserDictWindow>
</div>
</template>

<script>
import {
    mapState
} from 'vuex'
import adduserDictWindow from '@/components/Articles/adduserDictWindow.vue'
export default {
    name: 'seeDetails',
    data() {
        return {
            xindex: JSON.parse(JSON.stringify(this.currentIndex)),
            xcurrentPage: JSON.parse(JSON.stringify(this.currentPage)),
            xpageSize: JSON.parse(JSON.stringify(this.pageSize)),
            xtotalItems: 0,
            articleDetail: [],
            nextDisabled: false,
            previousDisabled: false,
            addUserDictWindowShow: false,
            splitWords: []
        }
    },
    components: {
        adduserDictWindow
    },
    props: ['showSeeDetail', 'currentIndex', 'currentPage', 'pageSize'],
    mounted() {
        // console.log('mounted .....')
        let self = this
        if (self.showSeeDetail) {
            let Params = {
                'currentPage': self.xcurrentPage,
                'pageSize': self.xpageSize
            }
            self.fetchItem(Params)

        }
    },
    computed: {
        ...mapState(['baseurl', 'currentComponent']),
        xtotalPages: function () {
            if (JSON.stringify(this.articleDetail) !== '[]') {
                return Math.ceil(this.xtotalItems / this.xpageSize)
            } else {
                return 0
            }
        },
        seeStatus: function () {
            if (JSON.stringify(this.articleDetail) !== '[]' && this.xindex < this.currentPagetotalCount && this.xindex >= 0) {
                return this.articleDetail[this.xindex].status
            } else {
                return ''
            }
        },
        seeBody: function () {
            if (JSON.stringify(this.articleDetail) !== '[]' && this.xindex < this.currentPagetotalCount && this.xindex >= 0) {
                return this.articleDetail[this.xindex].body
            } else {
                return ''
            }
        },
        seeSplitWords: {
            get: function () {
                if (JSON.stringify(this.articleDetail) !== '[]' && this.xindex < this.currentPagetotalCount && this.xindex >= 0) {
                    if (this.articleDetail[this.xindex].status === '已添加' && (!this.articleDetail[this.xindex].splitWords || this.articleDetail[this.xindex].splitWords === '' || this.articleDetail[this.xindex]['splitWords'].length === 0)) {
                        // 尚未分词，需要 强制分词
                        //console.log('尚未分词，需要 强制分词')
                        // 只要 状态是 
                        // 分词 
                        this.fenci(this.articleDetail[this.xindex]['_id']['$oid'])
                        //console.log('result', result)
                        return ['...分词中 ...']
                    } else {
                        return Array.from(new Set(this.articleDetail[this.xindex].splitWords))
                    }
                } else {
                    return []
                }
            },

            set: function (realData) {
                let self = this
                //return realData
                //this.seeSplitWords = realData
                //this.articleDetail[this.xindex].splitWords = realData
                self.$set(self.articleDetail[self.xindex], 'splitWords', realData)
                //console.log('this.articleDetail88', self.articleDetail)
            }
        },
        seeUid: function () {
            if (JSON.stringify(this.articleDetail) !== '[]' && this.xindex < this.currentPagetotalCount && this.xindex >= 0) {
                return this.articleDetail[this.xindex]['_id']['$oid']
            } else {
                return ''
            }
        },
        currentPagetotalCount: function () {
            return this.articleDetail.length
        }

    },

    methods: {
        fenci: function (uid, type = '1') {
            let self = this
            //console.log('uid', uid)
            self.axios({
                    method: 'get',
                    url: self.baseurl + 'Articles/fenci/' + self.currentComponent,
                    params: {
                        'uid': uid
                    }
                })
                .then(res => {
                    //console.log(res)
                    //return res.data.splitWords
                    self.splitWords = res.data.splitWords
                    self.seeSplitWords = self.splitWords

                    if (type === '1') {
                        self.deleteFromSplitWords(0, 0, 'x') // 保存当前 的 分词数据
                    } else if (type === '2') {
                        self.deleteFromSplitWords(0, 0, 'y') // 保存当前 的 分词数据
                    }

                })
                .catch(err => {
                    console.log(err)
                    // self.$Message.error(err.response.data.detail);
                })
        },
        fetchItem: function (Params) {
            let self = this
            self.axios({
                    method: 'get',
                    url: self.baseurl + 'Articles/' + self.currentComponent,
                    params: Params
                })
                .then(res => {
                    //console.log(res)
                    if (res.data.count !== '') {
                        self.xtotalItems = res.data.count
                    }
                    self.articleDetail = res.data.content
                    // 如果点开的是 所有数据的第一个 或 最后一个， 直接禁用掉 相应的按钮
                    if (self.xindex === self.currentPagetotalCount - 1 && self.xcurrentPage === self.xtotalPages) {
                        self.nextDisabled = true
                    }
                    if (self.xindex === 0 && self.xcurrentPage === 1) {
                        self.previousDisabled = true
                    }

                })
                .catch(err => {
                    console.log(err)
                    // self.$Message.error(err.response.data.detail);
                })
        },
        add2UserDict: function () {
            let self = this
            //  往用户词中添加 词语
            // 构造 formCustom
            self.addUserDictWindowShow = true

        },
        setStopWord: function (word, index) {
            //console.log(word, index)
            let self = this
            // 要想添加到 停止词，需要先检查 该词是否已存在在 无效词和用户词？ 如果已 存在于 两者中任何一个，则弹窗提示，是否 强力插入，如果是，则从 前者中 删除该词，并 插入到无效词。
            // 如果否，则跳过对该词的操作。如此看来， 需要单个词进行 循环操作，比较 麻烦

            // 2 - 首先 查看该词是否在无效词
            let Params = {
                'searchItem': word.trim(),
                'fullMatch': true
            }
            self.axios({
                    method: 'get',
                    url: self.baseurl + 'InvalidDict/' + self.currentComponent,
                    params: Params
                })
                .then(res => {
                    //console.log(res)
                    if (res.data.count > 0) {
                        // 存在于 无效词典中 
                        //console.log(word + ' 存在于 无效词中')
                        //console.log('确认添加!')

                        // 首先从 无效词典中，删除该词
                        self
                            .axios({
                                method: "delete",
                                url: self.baseurl + "InvalidDict/" + self.currentComponent,
                                data: [word],
                            })
                            .then(() => {
                                //console.log('从无效词中删除成功,下面添加到 停止词中')

                                // 然后，将该词添加到 停止词
                                let xdata = [{
                                    'word': word,
                                    'operator': localStorage.getItem('kwmUser'),
                                    'source': '语料分词',
                                    'exStatus': '已分词'
                                }]
                                self.axios({
                                        method: 'post',
                                        url: self.baseurl + 'StopDict/',
                                        data: xdata
                                    })
                                    .then(() => {
                                        //console.log('添加到 停止词成功!')

                                        // 然后哦，从当前分词 列表中 删除 该 词
                                        // 2- 将 该词 从 原始记录中删除
                                        self.deleteFromSplitWords(index, 1, '停止')

                                    })
                                    .catch(err => {
                                        //console.log(err)
                                        //console.log('添加到 停止词失败!')
                                        self.$Message.error(err.response.data.detail);
                                        //console.log('c' + err.response.data.detail + 'c')
                                        if (err.response.data.detail.indexOf('停止词已存在') !== -1) {
                                            //console.log('chongu')
                                            // 2- 将 该词 从 原始记录中删除
                                            self.deleteFromSplitWords(index, 1, '停止')
                                        }

                                    })

                            })
                            .catch((err) => {
                                console.log(err);
                                self.$Message.error('从无效词典删除' + word + '失败!');
                            });
                    } else {
                        //console.log('不存在于 无效词典中，继续搜索用户词典')

                        // 接着查看是否 存在于 用户词中 
                        let Params = {
                            'keyword': word,
                            'fullMatch': true
                        }
                        self.axios({
                                method: 'get',
                                url: self.baseurl + 'UserDict/' + self.currentComponent,
                                params: Params
                            })
                            .then(res => {
                                if (res.data.count > 0) {
                                    // 存在于 用户词典中
                                    self
                                        .axios({
                                            method: "delete",
                                            url: self.baseurl + "UserDict/" + self.currentComponent,
                                            data: [{
                                                'word': word
                                            }],
                                        })
                                        .then(() => {
                                            //console.log('从用户词中删除成功,下面添加到 停止词中')

                                            // 然后，将该词添加到 停止词
                                            let xdata = [{
                                                'word': word,
                                                'operator': localStorage.getItem('kwmUser'),
                                                'source': '语料分词',
                                                'exStatus': '已分词'
                                            }]
                                            self.axios({
                                                    method: 'post',
                                                    url: self.baseurl + 'StopDict/',
                                                    data: xdata
                                                })
                                                .then(() => {
                                                    //console.log('添加到 停止词成功!')

                                                    // 2- 将 该词 从 原始记录中删除
                                                    self.deleteFromSplitWords(index, 1, '停止')
                                                })
                                                .catch(err => {
                                                    console.log(err.response.data.detail)
                                                    // self.$Message.error(err.response.data.detail);
                                                    if (err.response.data.detail.indexOf('停止词已存在') !== -1) {
                                                        //console.log('重复，直接从分词中删除')
                                                        // 2- 将 该词 从 原始记录中删除
                                                        self.deleteFromSplitWords(index, 1, '停止')
                                                    }
                                                })

                                        })
                                        .catch((err) => {
                                            console.log(err);
                                            self.$Message.error("删除失败");
                                        });
                                } else {
                                    // 不存在于用户词典中
                                    // 那么，接下来直接往 停止词典里面插入，不管存不存在，如果存在，会自动报错跳过
                                    // 然后，将该词添加到 停止词
                                    let xdata = [{
                                        'word': word,
                                        'operator': localStorage.getItem('kwmUser'),
                                        'source': '语料分词',
                                        'exStatus': '已分词'
                                    }]
                                    self.axios({
                                            method: 'post',
                                            url: self.baseurl + 'StopDict/',
                                            data: xdata
                                        })
                                        .then(() => {
                                            //console.log('添加到 停止词成功!')

                                            // 2- 将 该词 从 原始记录中删除
                                            self.deleteFromSplitWords(index, 1, '停止')
                                        })
                                        .catch(err => {
                                            //console.log(err)
                                            // self.$Message.error(err.response.data.detail);
                                            if (err.response.data.detail.indexOf('停止词已存在') !== -1) {
                                                //console.log('已存在,直接从分析表中删除!')
                                                // 2- 将 该词 从 原始记录中删除
                                                self.deleteFromSplitWords(index, 1, '停止')
                                            }
                                        })

                                }
                            })
                            .catch(err => {
                                console.log(err)
                            })
                    }
                })
                .catch(err => {
                    console.log(err)
                })

        },
        deleteFromSplitWords: function (index, num, type) {
            let self = this
            let temp = JSON.parse(JSON.stringify(self.seeSplitWords))
            temp.splice(index, num)
            let myData = {
                'splitWords': temp,
                'status': '已分词'
            }
            let Params = {
                'currentPage': self.xcurrentPage,
                'pageSize': self.xpageSize
            }
            //console.log('uid', self.seeUid)
            // 更新 Article 后端，从 article 数据库中，删除 停止词
            self.axios({
                    method: 'patch',
                    url: self.baseurl + 'Articles/' + self.currentComponent + '/' + self.seeUid,
                    data: myData,
                    params: Params
                })
                .then(res => {
                    //console.log('yyy',res)
                    //self.seeSplitWords.splice(index,1)
                    if (res.data.count !== '') {
                        self.xtotalItems = res.data.count
                    }
                    self.articleDetail = res.data.content
                    if (type === 'x') {
                        self.$Message.success('初次分词成功');
                    } else if (type === 'y') {
                        self.$Message.success('重新分词成功');
                    } else {
                        self.$Message.success('设为' + type + '词成功!');
                    }
                })
                .catch(err => {
                    //console.log(err)
                    self.$Message.error({
                        content: JSON.stringify(err.response.data.detail),
                        duration: 0,
                        closable: true
                    });

                })
        },
        setInvalidWord: function (word, index) {
            let self = this
            // 要想添加到 无效词，需要先检查 该词是否已存在在 停止词和用户词？ 如果已 存在于 两者中任何一个，则弹窗提示，是否 强力插入，如果是，则从 前者中 删除该词，并 插入停止词。
            // 如果否，则跳过对该词的操作。如此看来， 需要单个词进行 循环操作，比较 麻烦。

            // 1 - 首先 查看该词是否在停止词中
            let Params = {
                'keyword': word,
                'fullMatch': true
            }
            self.axios({
                    method: 'get',
                    url: self.baseurl + 'StopDict/',
                    params: Params
                })
                .then(res => {
                    //console.log(res)
                    if (res.data.count > 0) {
                        // 存在于 停止词典中 
                        console.log(word + ' 存在于 停止词中')

                        // 首先从 停止词典中，删除该词
                        self
                            .axios({
                                method: "delete",
                                url: self.baseurl + "StopDict/",
                                data: [word],
                            })
                            .then(() => {
                                console.log('从停止词中删除成功,下面添加到 无效词中')

                                // 然后，将该词添加到 无效词典
                                let xdata = [{
                                    'word': word,
                                    'operator': localStorage.getItem('kwmUser'),
                                    'source': '语料分词',
                                    'exStatus': '已分词'
                                }]
                                self.axios({
                                        method: 'post',
                                        url: self.baseurl + 'InvalidDict/' + self.currentComponent,
                                        data: xdata
                                    })
                                    .then(() => {
                                        //console.log('添加到 无效词成功!')

                                        self.deleteFromSplitWords(index, 1, '无效')
                                    })
                                    .catch(() => {
                                        //console.log(err)
                                        // self.$Message.error(err.response.data.detail);
                                        self.deleteFromSplitWords(index, 1, '无效')
                                    })

                            })
                            .catch((err) => {
                                console.log(err);
                                self.$Message.error("删除失败");
                            });
                    } else {
                        //console.log('不存在于 停止词典中，继续搜索用户词典')

                        // 接着查看是否 存在于 用户词中 
                        let Params = {
                            'keyword': word,
                            'fullMatch': true
                        }
                        self.axios({
                                method: 'get',
                                url: self.baseurl + 'UserDict/' + self.currentComponent,
                                params: Params
                            })
                            .then(res => {
                                if (res.data.count > 0) {
                                    //console.log('存在于 用户词典中')
                                    //        // 首先从 用户词典中，删除该词
                                    self
                                        .axios({
                                            method: "delete",
                                            url: self.baseurl + "UserDict/" + self.currentComponent,
                                            data: [{
                                                'word': word
                                            }],
                                        })
                                        .then(() => {
                                            //console.log('从用户词中删除成功,下面添加到 无效词中')

                                            // 然后，将该词添加到 无效词
                                            let xdata = [{
                                                'word': word,
                                                'operator': localStorage.getItem('kwmUser'),
                                                'source': '语料分词',
                                                'exStatus': '已分词'
                                            }]
                                            self.axios({
                                                    method: 'post',
                                                    url: self.baseurl + 'InvalidDict/' + self.currentComponent,
                                                    data: xdata
                                                })
                                                .then(() => {
                                                    //console.log('添加到 无效词成功!')

                                                    // 然后哦，更改 在基础词中的状态
                                                    self.deleteFromSplitWords(index, 1, '无效')
                                                })
                                                .catch(err => {
                                                    //console.log(err)
                                                    self.$Message.error(err.response.data.detail);
                                                    self.deleteFromSplitWords(index, 1, '无效')
                                                })

                                        })
                                        .catch((err) => {
                                            console.log(err);
                                            self.$Message.error("删除失败");
                                        });
                                } else {
                                    // 不存在于用户词典中
                                    // 那么，接下来直接往 无效词典里面插入，不管存不存在，如果存在，会自动报错跳过
                                    // 然后，将该词添加到 无效词
                                    //console.log('不存在于 用户词典中')
                                    let xdata = [{
                                        'word': word,
                                        'operator': localStorage.getItem('kwmUser'),
                                        'source': '语料分词',
                                        'exStatus': '已分词'
                                    }]
                                    self.axios({
                                            method: 'post',
                                            url: self.baseurl + 'InvalidDict/' + self.currentComponent,
                                            data: xdata
                                        })
                                        .then(() => {
                                            //console.log('添加到 无效词成功!')

                                            // 然后哦，更改 在基础词中的状态
                                            self.deleteFromSplitWords(index, 1, '无效')
                                        })
                                        .catch(() => {
                                            //console.log(err)
                                            // self.$Message.error(err.response.data.detail);
                                            self.deleteFromSplitWords(index, 1, '无效')
                                        })
                                }
                            })
                            .catch(err => {
                                console.log(err)
                            })
                    }
                })
                .catch(err => {
                    console.log(err)
                })
        },
        setUrlInvalid: function (flag) {
            // 把当前 url 所在行 uid 发送到 后端 ，将该行 的 status 设置为 无效
            let self = this
            // 发送数据
            let myData = {}
            let operation = ''
            if (flag === 'invalid') {
                myData = {
                    'status': '无效',
                    'source': '语料分词'
                }
                operation = "无效"
            } else if (flag === 'valid') {
                // 判断有没有分词
                let xstatus = ''
                if (self.seeSplitWords){
                    xstatus = '已分词'
                }else{
                    xstatus = '已添加'
                }
                myData = {
                    'status': xstatus,
                    'source': '语料分词'
                }
                operation = "有效"
            }

            let Params = {
                'currentPage': self.xcurrentPage,
                'pageSize': self.xpageSize
            }
            // console.log(myData)
            self.axios({
                    method: 'patch',
                    url: self.baseurl + 'Articles/' + self.currentComponent + '/' + self.seeUid,
                    data: myData,
                    params: Params
                })
                .then(res => {
                    if (res.data.count !== '') {
                        self.xtotalItems = res.data.count
                    }
                    self.articleDetail = res.data.content
                    self.$Message.success('当前语料设为' + operation + '成功!');
                })
                .catch(err => {
                    console.log(err)
                    self.$Message.error('当前语料设为' + operation + '失败!');
                })

        },
        PreviousOne: function () {
            let self = this
            // console.log(self.seeUid)
            self.nextDisabled = false
            self.xindex = self.xindex - 1
            if (self.xindex < 0) {
                // 已经到达当前第一行数据
                // 1- 页码切换到上一页:
                if (self.xcurrentPage > 1) {
                    // 可以继续进行
                    self.xindex = self.xpageSize - 1 //从上一页 最后一个 开始显示
                    self.xcurrentPage = self.xcurrentPage - 1
                    let Params = {
                        'currentPage': self.xcurrentPage,
                        'pageSize': self.xpageSize
                    }
                    self.fetchItem(Params)
                } else {
                    // 否则， 已经遍历完成。按钮设成禁用状态
                    self.previousDisabled = true
                }
            } else {
                // self.xindex = self.xindex + 1
                if (self.xindex === 0 && self.xcurrentPage === 1) {
                    self.previousDisabled = true
                }
            }
        },
        nextOne: function () {
            let self = this
            // console.log(self.seeUid)
            self.previousDisabled = false
            self.xindex = self.xindex + 1
            if (self.xindex === self.currentPagetotalCount) {
                // 已经到达当前页面数据 最低端，需要拉取新的数据
                // 1- 页码切换到下一页:
                if (self.xcurrentPage < self.xtotalPages) {
                    // 可以继续进行
                    self.xindex = 0 //从下一页第一个开始显示
                    self.xcurrentPage = self.xcurrentPage + 1
                    let Params = {
                        'currentPage': self.xcurrentPage,
                        'pageSize': self.xpageSize
                    }
                    self.fetchItem(Params)
                } else {
                    // 否则， 已经遍历完成。按钮设成禁用状态
                    self.nextDisabled = true
                }
            } else {
                // self.xindex = self.xindex + 1
                if (self.xindex === self.currentPagetotalCount - 1 && self.xcurrentPage === self.xtotalPages) {
                    self.nextDisabled = true
                }
            }
        },
        modalCancel: function () {
            //this.showSeeUrlConfig = false
            this.$emit('force-refresh', this.xcurrentPage)
            this.$emit('update:showSeeDetail', false)

        }
    }
}
</script>

<style scoped>
.Article-see-detail {
    height: 500px
}

.Article-see-detail-content-total {
    display: flex;
    max-height: 450px;
    padding: 5px
}

.Article-see-detail-content-total1 {
    flex: 7;
    display: flex;
    overflow: auto
}

.article-detail-content-p1 {
    flex: 4;
    overflow: auto;
    color: green
}

.article-detail-content-p1:hover {
    background-color: #d7e1e8
}

.article-detail-content-p2 {
    flex: 4;
    overflow: auto
}

.Article-see-detail-content-total2 {
    flex: 1
}

li {
    list-style-type: none;
    padding: 0px !important
}

.xbutton {
    margin-left: 10px;
    margin-bottom: 10px
}

.liLine {
    display: flex;
    align-items: center;
    padding: 3px;
}

.liLine.header {
    border-bottom: 1px solid red;
    background-color: #f7e2e2;
    position: sticky;
    top: 0
}

.liLine.main {
    display: flex;
    border-top: 1px solid red
}

.liLine .p1 {
    flex: 5;
    padding: 0px;
    border-right: 1px solid red;
}

.liLine.main .p1 {
    color: blue
}

.liLine.main .p1:hover {
    background-color: #d7e1e8
}

.liLine .p2 {
    flex: 4;
    justify-content: flex-end
}

.article-detail-content-p1 {
    border-top: 1px solid red;
    border-bottom: 1px solid red;
    border-left: 1px solid red;
}

.article-detail-content-p2 {
    border: 1px solid red;
}

.Invalid,
.Stop {
    margin-left: 10px
}
</style>
