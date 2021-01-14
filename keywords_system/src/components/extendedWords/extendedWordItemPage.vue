<template>
<div>
    <i-modal v-model="extendedWordItemShow" :title="operation + '拓展词'" width="550" :closable="false" :mask-closable="false" :styles="{top: '20px'}" :scrollable="true">

        <div class="extendedWords-itemPage">

            <i-form ref="formCustom" :model="formCustom" :rules="ruleCustom" :label-width="120">

                <div class="extendedWords-itemPage-form">
                    <div v-for="(item, xindex) in formCustom.Items" :key="xindex">
                        <div class="extendedWords-itemPage-form-main">
                            <i-formItem :label="'拓展词' + (parseInt(xindex)+1)" :prop="'Items.' + xindex + '.word'" :rules="ruleCustom.word">

                                <i-row class="extendedWords-itemPage-form-main-word">
                                    <i-input class="extendedWords-itemPage-form-main-word-input" @on-change="searchWordStatus(xindex)" type="text" v-model="item.word" placeholder="请输入拓展词"></i-input>
                                    <i-button v-show="formCustom.uid === ''" class="extendedWords-itemPage-form-main-status-delete" type="error" @click="handleRemove(xindex)">删除当前项</i-button>
                                </i-row>
                            </i-formItem>

                            <i-formItem class="status" label="存在状态:">
                                <i-row class="extendedWords-itemPage-form-main-status">
                                    <span class="xyz"> {{item.existed}}</span>
                                </i-row>
                            </i-formItem>

                            <i-formItem label="分类:" :prop="'Items.' + xindex + '.category'" :rules="ruleCustom.word">
                                <i-row class="extendedWords-itemPage-form-row special">
                                    <i-select :disabled="item.existed === '已存在' && formCustom.uid === ''" class="Url-itemPage-form-category-select" multiple v-model="item.category" placeholder="请选择分类">
                                        <i-option v-for="itemx in rawCategories" :value="itemx" :key="itemx">{{ itemx }}</i-option>
                                    </i-select>
                                </i-row>
                            </i-formItem>
                            <i-formItem label="母词:" :prop="'Items.' + xindex + '.mword'" :rules="ruleCustom.word">
                                <i-row>
                                    <i-input class="" :disabled="item.existed === '已存在' && formCustom.uid === ''" type="text" v-model="item.mword" placeholder="请输入母词"></i-input>
                                </i-row>
                            </i-formItem>
                            <i-formItem label="主题词:" :prop="'Items.' + xindex + '.topicWord'">
                                <i-row>
                                    <i-input class="" :disabled="item.existed === '已存在' && formCustom.uid === ''" type="text" v-model="item.topicWord" placeholder="请输入主题"></i-input>
                                </i-row>
                            </i-formItem>
                            <div class="together">
                                <i-formItem label="百度指数:" :prop="'Items.' + xindex + '.baiduIndex'" :rules="ruleCustom.floatWord">
                                    <i-row>
                                        <i-input class="" :disabled="item.existed === '已存在' && formCustom.uid === ''" type="text" v-model="item.baiduIndex" placeholder="请输入百度指数,必须为数字"></i-input>
                                    </i-row>
                                </i-formItem>
                                <i-formItem label="百度指数-移动:" :prop="'Items.' + xindex + '.baiduIndexM'" :rules="ruleCustom.floatWord">
                                    <i-row>
                                        <i-input class="" :disabled="item.existed === '已存在' && formCustom.uid === ''" type="text" v-model="item.baiduIndexM" placeholder="请输入百度指数-移动,必须为数字"></i-input>
                                    </i-row>
                                </i-formItem>
                            </div>

                            <div class="together">
                                <i-formItem label="周搜索次数:" :prop="'Items.' + xindex + '.searchCount'" :rules="ruleCustom.intWord">
                                    <i-row>
                                        <i-input class="" :disabled="item.existed === '已存在' && formCustom.uid === ''" type="text" v-model="item.searchCount" placeholder="请输入搜索次数(周),必须为数字"></i-input>
                                    </i-row>
                                </i-formItem>
                                <i-formItem label="周搜索次数-移动:" :prop="'Items.' + xindex + '.searchCountM'" :rules="ruleCustom.intWord">
                                    <i-row>
                                        <i-input class="" :disabled="item.existed === '已存在' && formCustom.uid === ''" type="text" v-model="item.searchCountM" placeholder="请输入搜索次数(周)-移动,必须为数字"></i-input>
                                    </i-row>
                                </i-formItem>
                            </div>
                            <div class="together">
                                <i-formItem label="竞价:" :prop="'Items.' + xindex + '.bidPrice'" :rules="ruleCustom.floatWord">
                                    <i-row>
                                        <i-input class="" :disabled="item.existed === '已存在' && formCustom.uid === ''" type="text" v-model="item.bidPrice" placeholder="请输入竞价,必须为数字"></i-input>
                                    </i-row>

                                </i-formItem>

                                <i-formItem label="竞价-移动:" :prop="'Items.' + xindex + '.bidPriceM'" :rules="ruleCustom.floatWord">
                                    <i-row>
                                        <i-input class="" :disabled="item.existed === '已存在' && formCustom.uid === ''" type="text" v-model="item.bidPriceM" placeholder="请输入竞价-移动,必须为数字"></i-input>
                                    </i-row>
                                </i-formItem>
                            </div>

                            <i-formItem label="百度备注:" :prop="'Items.' + xindex + '.baiduComment'" :rules="ruleCustom.word">
                                <i-row>
                                    <i-input class="" :disabled="item.existed === '已存在' && formCustom.uid === ''" type="text" v-model="item.baiduComment" placeholder="请输入百度备注"></i-input>
                                </i-row>
                            </i-formItem>

                            <i-formItem label="用途标签:" :prop="'Items.' + xindex + '.usageTag'" :rules="ruleCustom.word">
                                <i-row>
                                    <i-select v-if="formCustom.uid === ''" filterable allow-create :disabled="item.existed === '已存在'" class="Url-itemPage-form-category-select" multiple v-model="item.usageTag" placeholder="请输入用途标签">
                                        <i-option v-for="itemx in rawTags" :value="itemx" :key="itemx">{{ itemx }}</i-option>
                                    </i-select>
                                    <i-select v-else filterable allow-create :disabled="item.existed === '已存在'" class="Url-itemPage-form-category-select" multiple v-model="item.usageTag" placeholder="请输入用途标签">
                                        <i-option v-for="itemx in item.usageTag" :value="itemx" :key="itemx">{{ itemx }}</i-option>
                                    </i-select>
                                </i-row>
                            </i-formItem>

                        </div>
                    </div>
                </div>
                <i-formItem>
                    <i-row>
                        <i-col span="12">
                            <i-button v-if="formCustom.uid === ''" type="dashed" long @click="handleAdd()" icon="md-add">添加拓展词</i-button>
                        </i-col>
                    </i-row>
                </i-formItem>

            </i-form>

        </div>
        <div slot="footer">
            <i-button v-show="formCustom.uid !== ''" class="Url-itemPage-delete-button" type="error" size="default" @click="modalDelete(formCustom.uid)">删除</i-button>
            <i-button type="default" size="large" @click="modalCancel('formCustom')">取消</i-button>
            <i-button type="primary" :disabled="this.finalCount === 0||(JSON.stringify(formCustom) !== '{}' &&  formCustom.uid !== '' && formCustom.Items[0].word !== this.oldWord && formCustom.Items[0].existed === '已存在' )" size="large" @click="modalOk('formCustom')">提交</i-button>
        </div>
    </i-modal>
</div>
</template>

<script>
import {
    mapState
} from 'vuex'
export default {
    name: 'extendedWordItemPage',
    data() {
        const validateWord = (rule, value, callback) => {
            if (value.length === 0) {
                callback(new Error('不能为空'));
            } else {
                callback();
            }
        };
        const validateFloatWord = (rule, value, callback) => {
            if (value.length === 0) {
                callback(new Error('不能为空'));
            } else if (isNaN(parseFloat(value))) {
                callback(new Error('必须为数字'));
            } else {
                callback();
            }
        };
        const validateIntWord = (rule, value, callback) => {
            if (value.length === 0) {
                callback(new Error('不能为空'));
            } else if (isNaN(parseInt(value))) {
                callback(new Error('必须为数字'));
            } else {
                callback();
            }
        };

        return {
            oldTopicWord: '',
            dataBak: '',
            finalCount: 1,
            oldWord: '',
            oldStatus: '',
            formCustom: {},
            ruleCustom: {
                word: [{
                    validator: validateWord,
                    trigger: 'blur,change'
                }],
                floatWord: [{
                    validator: validateFloatWord,
                    trigger: 'blur,change'
                }],
                intWord: [{
                    validator: validateIntWord,
                    trigger: 'blur,change'
                }]
            },
        }
    },
    props: ['extendedWordItemShow', 'formCustom2', 'rawCategories', 'rawTags'],
    computed: {
        ...mapState(['currentUserName', 'baseurl', 'currentComponent']),
        operation: function () {
            if (this.formCustom.uid === '') {
                return '添加'
            } else {
                return '编辑'
            }
        }
    },
    beforeDestroy() {},
    mounted() {
        //console.log(this.formCustom2)
        if (JSON.stringify(this.formCustom2) !== "{}") {
            this.$set(this.formCustom, 'uid', this.formCustom2.uid)
            //this.$set(this.formCustom, 'itemIndex', this.formCustom2.itemIndex)
            this.$set(this.formCustom, 'Items', this.formCustom2.Items)

            // 保存一份 初始值的 副本，用来比较哪些字段进行了修改
            this.dataBak = JSON.parse(JSON.stringify(this.formCustom2.Items[0]))
            //console.log('初始:' + JSON.stringify(this.dataBak))
            //this.oldTopicWord = JSON.parse(JSON.stringify(this.formCustom2.Items[0].topicWord))
            this.oldTopicWord = this.dataBak.topicWord
            this.oldMword = this.dataBak.mword
            //console.log('this.oldTopicWord', this.oldTopicWord)
            this.oldWord = JSON.parse(JSON.stringify(this.formCustom2.Items[0].word)) // 如果word 被修改，需要 修改对应 停止或 无效词典中的状态
            this.oldStatus = JSON.parse(JSON.stringify(this.formCustom2.Items[0].status)) // 如果word 被修改，需要 修改对应 停止或 无效词典中的状态
            // console.log(this.formCustom,'yyy')
        }
    },
    methods: {
        searchWordStatus: function (xindex) {
            //console.log(this.formCustom.Items[xindex].word)
            // let checkWord = this.shownformCustomItems[xindex].value.word
            if (this.formCustom.Items[xindex].word.replace(/ /g, '')) { // 空格不会激活 搜索
                // this.formCustom.Items[xindex].value.status = '查询中 ...'
                this.$set(this.formCustom.Items[xindex], 'existed', '查询中 ...')
                this.checkIfExist(this.formCustom.Items[xindex].word, xindex)
            } else {
                this.formCustom.Items[xindex].existed = '状态'
            }

        },
        checkIfExist: function (target, xindex) {
            let self = this
            let Params = {
                'wordPart': target,
                'fullMatch': true
            } // 必须使用 完全匹配，不能用正则，否则会找到一堆包含该项的词
            self.axios({
                    method: 'get',
                    url: self.baseurl + 'extendedWords/' + self.currentComponent,
                    params: Params
                })
                .then(res => {
                    //console.log(res)
                    if (res.data.count > 0) {
                        // 存在，不会添加
                        self.$set(self.formCustom.Items[xindex], 'existed', '已存在')
                    } else {
                        self.$set(self.formCustom.Items[xindex], 'existed', '新加')
                    }
                })
                .catch(err => {
                    console.log(err)
                    // self.$Message.error(err.response.data.detail);
                })

        },
        handleAdd: function () {
            //this.formCustom.itemIndex++
            this.formCustom.Items.push({
                // index: this.formCustom.itemIndex,
                status: '',
                existed: '状态',
                word: '',
                category: [],
                mword: '',
                topicWord: '',
                baiduIndex: '',
                searchCount: '',
                bidPrice: '',
                baiduIndexM: '',
                searchCountM: '',
                bidPriceM: '',
                baiduComment: '',
                usageTag: []
            });
            this.finalCount = 1

        },
        handleRemove: function (index) {
            //this.formCustom.Items[index].status = 0
            this.formCustom.Items.splice(index, 1)
            if (this.formCustom.Items.length === 0) {
                this.finalCount = 0
            }

        },
        modalOk: function (name) {
            let self = this
            // console.log('验证成功',self.formCustom.Items[0].value.word)
            // check 项目 是否为空
            self.$refs[name].validate((valid) => {
                if (valid) {
                    if (self.formCustom.uid === '') {
                        console.log('新建模式 ...')
                        console.log('验证成功', self.formCustom)
                        // 构造最终结果集 , 并回传数据给 父组件，由父组件创建 
                        // console.log(self.shownformCustomItems)
                        let result = []
                        for (let ele in self.formCustom.Items) {
                            //if (self.formCustom.Items[ele].status === 1 && self.formCustom.Items[ele].existed === '新加') {
                            if (self.formCustom.Items[ele].existed === '新加') {
                                result.push({
                                    'status': self.formCustom.Items[ele].status,
                                    'source': '手动添加',
                                    'word': self.formCustom.Items[ele].word,
                                    'category': self.formCustom.Items[ele].category,
                                    'mword': self.formCustom.Items[ele].mword,
                                    'topicWord': self.formCustom.Items[ele].topicWord,
                                    'baiduIndex': parseFloat(self.formCustom.Items[ele].baiduIndex),
                                    'searchCount': parseInt(self.formCustom.Items[ele].searchCount),
                                    'bidPrice': parseFloat(self.formCustom.Items[ele].bidPrice),
                                    'baiduIndexM': parseFloat(self.formCustom.Items[ele].baiduIndexM),
                                    'searchCountM': parseInt(self.formCustom.Items[ele].searchCountM),
                                    'bidPriceM': parseFloat(self.formCustom.Items[ele].bidPriceM),
                                    'baiduComment': self.formCustom.Items[ele].baiduComment,
                                    'usageTag': self.formCustom.Items[ele].usageTag
                                })
                            }
                        }
                        // 发送创建 基础词  事件

                        if (result.length !== 0) {
                            //只有包含新词时 才上传
                            self.$emit('createExtendedWords', result)
                            self.$refs[name].resetFields()
                            self.$emit('update:extendedWordItemShow', false)
                        } else {
                            self.$Message.warning('已经存在,无需提交!');
                            self.$emit('update:extendedWordItemShow', false)
                        }
                    } else {
                        console.log('编辑模式...')
                        let result = {
                            'oldTopicWord': self.oldTopicWord,
                            'oldMword': self.oldMword,
                            'word': self.formCustom.Items[0].word,
                            // 'status': newStatus, //self.formCustom.Items[0].word,
                            'category': self.formCustom.Items[0].category,
                            'mword': self.formCustom.Items[0].mword,
                            'topicWord': self.formCustom.Items[0].topicWord,
                            'baiduIndex': self.formCustom.Items[0].baiduIndex,
                            'searchCount': self.formCustom.Items[0].searchCount,
                            'bidPrice': self.formCustom.Items[0].bidPrice,
                            'baiduIndexM': self.formCustom.Items[0].baiduIndexM,
                            'searchCountM': self.formCustom.Items[0].searchCountM,
                            'bidPriceM': self.formCustom.Items[0].bidPriceM,
                            'baiduComment': self.formCustom.Items[0].baiduComment,
                            'usageTag': self.formCustom.Items[0].usageTag
                        }
                        // 对比，之前保存的最初状态，只提交被更改过的字段
                        for (let ele in self.dataBak) {
                            if (JSON.stringify(self.dataBak[ele]) === JSON.stringify(result[ele])) {
                                // 字段没有改变，则从result中移除 
                                delete result[ele]
                            }
                        }

                        // 只有 存在被改变的字段，才更新
                        if (Object.keys(result).length > 0) {
                            if (self.formCustom.Items[0].id) {
                                result['id'] = self.formCustom.Items[0].id
                            }
                            console.log('result', result)
                            self.$emit('UpdateExtendedWords', {
                                'uid': self.formCustom.uid,
                                'data': result
                            })

                            // 如果word被修改，则更新 关联词典信息
                            if (self.oldWord.trim() !== self.formCustom.Items[0].word.trim()) {

                                // word 发生改变
                                console.log(self.oldStatus)
                                if (self.oldStatus.indexOf('停止') !== -1) {
                                    // 停止词典
                                    console.log('停止词典')
                                    // 去停止词里面 更新 
                                    self.axios({
                                            method: "patch",
                                            url: self.baseurl + "StopDict/" + self.oldWord,
                                            data: {
                                                'word': self.formCustom.Items[0].word,
                                                'operator': localStorage.getItem('kwmUser')
                                            },
                                            params: {
                                                'flag': 'word'
                                            }
                                        })
                                        .then((res) => {
                                            if (res.data == 'item exist') {
                                                self.$Message.info("该停止词已存在!");
                                            } else {
                                                //if (res.data.count !== "") {
                                                //    self.itemCount = res.data.count;
                                                //}
                                                //self.StopDictItemData = res.data.content;
                                                self.$Message.success("修改成功!");
                                            }
                                        })
                                        .catch((err) => {
                                            console.log(err);
                                            //self.$Message.error("修改失败!");
                                            self.$Message.error({
                                                content: JSON.stringify(err.response.data.detail),
                                                duration: 0,
                                                closable: true
                                            });
                                        });
                                } else if (self.oldStatus.indexOf('无效') !== -1) {
                                    // 无效词典
                                    console.log('无效词典')
                                    // 去 无效词里面更新
                                    self.axios({
                                            method: "patch",
                                            url: self.baseurl + "InvalidDict/" + self.currentComponent + "/" + self.oldWord,
                                            data: {
                                                'word': self.formCustom.Items[0].word,
                                                'operator': localStorage.getItem('kwmUser')
                                            },
                                            params: {
                                                'flag': 'word'
                                            }
                                        })
                                        .then((res) => {
                                            if (res.data == 'item exist') {
                                                self.$Message.info("该无效已存在!");
                                            } else {
                                                // if (res.data.count !== "") {
                                                //    self.itemCount = res.data.count;
                                                // }
                                                //self.InvalidDictItemData = res.data.content;
                                                self.$Message.success("修改成功!");
                                            }
                                        })
                                        .catch((err) => {
                                            console.log(err);
                                            //self.$Message.error("修改失败!");
                                            self.$Message.error({
                                                content: JSON.stringify(err.response.data.detail),
                                                duration: 0,
                                                closable: true
                                            });
                                        });

                                }

                            }
                            self.$refs[name].resetFields()
                            self.$emit('update:extendedWordItemShow', false)
                        } else {
                            self.$Message.info('没有任何更新，无须更新!');
                        }
                    }
                } else {
                    // console.log('验证失败')
                    self.$Message.error('提交失败');
                    // self.modal1 = true
                }
            })
        },
        modalCancel: function (name) {
            this.$refs[name].resetFields()
            this.$emit('update:extendedWordItemShow', false)

        },
        modalDelete: function (uid) {
            // 触发删除事件 到 父组件
            // console.log('uid',uid)
            // 如果存在id属性，则 应该返回该 id，供 母页面刷新 使用
            //let myid = ''
            //if (this.formCustom.Items[0].id) {
            //    myid = this.formCustom.Items[0].id
            //}
            //this.$emit('deleteExtendedWordItem', {
            //    'uid': uid,
            //    'id': myid
            //})
            let self = this
            self.$Modal.confirm({
                title: '删除确认',
                content: '<p>删除后不可恢复,如果确定删除,请确认</p>',
                onOk: () => {
                    //this.deleteItems()

                    self.$emit('deleteExtendedWordItem', [{
                        'uid': uid,
                        'topicWord': self.oldTopicWord,
                        'mword': self.oldMword
                        //'id': self.formCustom.Items[0].id
                    }])
                    self.$emit('update:extendedWordItemShow', false)

                },
                onCancel: () => {
                    //this.$Message.info('已取消');
                }
            });

        }
    }
}
</script>

<style scoped>
.extendedWords-itemPage {
    max-height: 590px;
    overflow: auto
}

.extendedWords-itemPage .extendedWords-itemPage-form-main {
    border: 1px dashed #81b165;
    border-radius: 5px;
    padding: 10px;
    padding-bottom: 25px;
    margin-bottom: 10px;
}

.extendedWords-itemPage-form-row {
    margin: 3px 0px;

}

.extendedWords-itemPage-form-main-word {
    display: flex
}

.xyz {
    background-color: yellow
}

.status.ivu-form-item {
    margin-bottom: 0
}

.ivu-form-item:last-of-type {
    margin-bottom: 0
}

.extendedWords-itemPage-form-main-status-delete {
    margin-left: 5px
}

.together {
    display: flex;
    justify-content: space-between
}
</style>
