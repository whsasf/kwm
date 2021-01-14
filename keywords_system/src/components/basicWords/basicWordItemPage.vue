<template>
<div class="Url-itemPage">
    <i-modal v-model="basicWordItemShow" :title="operation + '基础词'" width="500" :closable="false" :mask-closable="false" :styles="{top: '20px'}" :scrollable="true">

        <div class="basicWords-itemPage">

            <i-form ref="formCustom" :model="formCustom" :rules="ruleCustom" :label-width="80">

                <div class="basicWords-itemPage-form">
                    <div class="basicWords-itemPage-form-main" v-for="(item, xindex) in formCustom.Items" :key="xindex">
                        <i-formItem :label="'基础词' + (parseInt(xindex) +1)" :prop="'Items.' + xindex +'.value' + '.word'" :rules="ruleCustom.word">
                            <i-row class="basicWords-itemPage-form-main-word">
                                <i-input class="basicWords-itemPage-form-main-word-input" @on-change="searchWordStatus(xindex)" type="text" v-model="item.value.word" placeholder="请输入基础词"></i-input>
                                <i-button v-show="formCustom.uid === ''" class="basicWords-itemPage-form-main-status-delete" type="error" @click="handleRemove(xindex)">删除该项</i-button>
                            </i-row>
                        </i-formItem>

                        <i-formItem class="status" label="状态:" :prop="'Items.' + xindex +'.value' + '.status'" :rules="ruleCustom.status">
                            <i-row class="basicWords-itemPage-form-main-status">
                                <i-input class="xyz" :readonly="true" type="text" v-model="item.value.status" placeholder="状态"></i-input>
                            </i-row>
                        </i-formItem>

                        <!--
                        <i-formItem v-if="item.value.source.split(',').length === 1" class="source" label="来源:">
                            <i-row>
                                <p> {{item.value.source}}</p>
                            </i-row>
                        </i-formItem>

                        <i-formItem v-else class="source" label="来源:">
                            <i-row>
                                <p v-for="(item2, index) in item.value.source.split(',')" :key="index"> {{'(' + (parseInt(index)+1) + ') '   + item2}}</p>
                            </i-row>
                        </i-formItem>
                        -->
                        <i-formItem label="分类" :prop="'Items.' + xindex +'.value' + '.category'" :rules="ruleCustom.category">
                            <i-row class="basicWords-itemPage-form-row special">
                                <i-select class="Url-itemPage-form-category-select" multiple v-model="item.value.category" placeholder="请选择分类">
                                    <i-option v-for="itemx in rawCategories" :value="itemx" :key="itemx">{{ itemx }}</i-option>
                                </i-select>
                            </i-row>
                        </i-formItem>

                    </div>
                </div>
                <i-formItem>
                    <i-row>
                        <i-col span="12">
                            <i-button v-show="formCustom.uid === ''" type="dashed" long @click="handleAdd()" icon="md-add">添加基础词</i-button>
                        </i-col>
                    </i-row>
                </i-formItem>

            </i-form>

        </div>
        <div slot="footer">
            <i-button v-show="formCustom.uid !== ''" class="Url-itemPage-delete-button" type="error" size="default" @click="modalDelete(formCustom.uid)">删除</i-button>
            <i-button type="default" size="large" @click="modalCancel('formCustom')">取消</i-button>
            <i-button :disabled="this.finalCount === 0" type="primary" size="large" @click="modalOk('formCustom')">提交</i-button>
        </div>
    </i-modal>
</div>
</template>

<script>
import {
    mapState,
    mapMutations
} from 'vuex'
export default {
    name: 'basicWordItemPage',
    data() {
        const validateWord = (rule, value, callback) => {
            if (value === '') {
                callback(new Error('基础词不能为空'));
            } else {
                callback();
            }
        };
        const validateStatus = (rule, value, callback) => {
            if (value.trim() !== '新加') {
                callback(new Error('只允许添加"新加"状态的词'));
            } else {
                callback();
            }

        };
        const validateCategory = (rule, value, callback) => {
            if (value.length === 0) {
                //console.log('category empty')
                callback(new Error('分类不能为空'));
            } else {
                //for (let ele in value) {
                //    if (this.rawCategories.indexOf(value[ele]) === -1) {
                //        callback(new Error('包含未定义分类:' + value[ele]));
                //    }
                //}
                callback();
            }
        };
        return {
            finalCount: 1,
            category_bak: '',
            formCustom: {},
            oldWord: '',
            oldStatus: '',
            ruleCustom: {
                word: [{
                    validator: validateWord,
                    trigger: 'blur'
                }],
                status: [{
                    validator: validateStatus,
                    //trigger: 'blur,change'
                }],
                category: [{
                    validator: validateCategory,
                    trigger: 'blur,change'
                }]
            },
        }
    },
    props: ['basicWordItemShow', 'formCustom2', 'rawCategories'],
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
        // console.log(this.formCustom2)
        if (JSON.stringify(this.formCustom2) !== "{}") {
            //this.$set(this.formCustom,'itemIndex',this.formCustom2.itemIndex)
            this.$set(this.formCustom, 'Items', this.formCustom2.Items)
            this.$set(this.formCustom, 'uid', this.formCustom2.uid)
            this.category_bak = this.formCustom2.Items[0].value.category.join(',')
            this.oldWord = JSON.parse(JSON.stringify(this.formCustom2.Items[0].value.word)) // 如果word 被修改，需要 修改对应 停止或 无效词典中的状态
            this.oldStatus = JSON.parse(JSON.stringify(this.formCustom2.Items[0].value.status)) // 如果word 被修改，需要 修改对应 停止或 无效词典中的状态
            //console.log(this.category_bak)
            // console.log(this.formCustom,'yyy')
            // 如果是 从文件加载的，需要 启动 基础词状态检查，

            //if (this.formCustom.Items[0].value.source === '手动添加') {
            for (let ele in this.formCustom.Items) {
                //找到word
                let word = this.formCustom.Items[ele].value.word
                //console.log('wwwword', word)
                if (word) {
                    this.checkIfExist(word, ele)
                }
            }
            //}
        }
    },
    methods: {
        ...mapMutations(['changeUrlItemWindowShow']),
        searchWordStatus: function (xindex) {
            // console.log(this.formCustom.Items[xindex].value.word)
            // let checkWord = this.shownformCustomItems[xindex].value.word
            //  从停止词典，用户词典，无效词典，基础、拓展词表中 ，搜索。如果找到 （第一个），显示 对应 状态，否则，状态为新，只有状态为新的 词 才能够 加入 基础拓展词表
            if (this.formCustom.Items[xindex].value.word.replace(/ /g, '')) { // 空格不会激活 搜索
                // this.formCustom.Items[xindex].value.status = '查询中 ...'
                this.$set(this.formCustom.Items[xindex].value, 'status', '查询中 ...')
                this.checkIfExist(this.formCustom.Items[xindex].value.word, xindex)
            } else {
                this.formCustom.Items[xindex].value.status = ''
            }

        },
        checkIfExist: function (target, xindex) {
            let self = this
            let Params = {
                'searchItem': target,
                'fullMatch': true
            } // 必须使用 完全匹配，不能用正则，否则会找到一堆包含该项的词
            self.axios({
                    method: 'get',
                    url: self.baseurl + 'StopDict/',
                    params: Params
                })
                .then(res => {
                    // console.log('StopDict ...',res)
                    // 如果返回为空，继续搜索下一个 词典
                    if (res.data.count > 0) {
                        // 已经找到，可以返回了
                        // self.formCustom.Items[xindex].value.status = '停止 ' + '(' + res.data.content[0].modifiedTime + ')'
                        self.$set(self.formCustom.Items[xindex].value, 'status', '停止 ' + '(' + res.data.content[0].modifiedTime + ')')
                    } else {
                        // 没有从 StopDict 中 找到，现在寻找 InvalidDict 
                        // console.log('not StopDict')
                        let Params = {
                            'keyword': target,
                            'fullMatch': true
                        }
                        self.axios({
                                method: 'get',
                                url: self.baseurl + 'InvalidDict/' + self.currentComponent,
                                params: Params
                            })
                            .then(res => {
                                // console.log('invalidDict ...',res)
                                if (res.data.count > 0) {
                                    // 在 无效词典中发现
                                    //self.formCustom.Items[xindex].value.status = '无效 ' + '(' + res.data.content[0].modifiedTime + ')'
                                    self.$set(self.formCustom.Items[xindex].value, 'status', '无效 ' + '(' + res.data.content[0].modifiedTime + ')')
                                } else {
                                    // 没有在 无效词典中找到, 则继续寻找  用户词典
                                    // console.log('not invalidDict')
                                    let Params = {
                                        'searchItem': target,
                                        'fullMatch': true
                                    }
                                    self.axios({
                                            method: 'get',
                                            url: self.baseurl + 'UserDict/' + self.currentComponent,
                                            params: Params
                                        })
                                        .then(res => {
                                            // console.log('userDict ...',res)
                                            if (res.data.count > 0) {
                                                // 在 用户词典中发现
                                                //self.formCustom.Items[xindex].value.status = '用户 ' + '(' + res.data.content[0].modifiedTime + ')'
                                                self.$set(self.formCustom.Items[xindex].value, 'status', '用户 ' + '(' + res.data.content[0].modifiedTime + ')')
                                            } else {
                                                // 没有在 用户词典中 找到 ，需要搜索基础拓展词表
                                                // console.log('not userDict')
                                                let Params = {
                                                    'wordPart': target,
                                                    'fullMatch': true
                                                }
                                                self.axios({
                                                        method: 'get',
                                                        url: self.baseurl + 'basicWords/' + self.currentComponent,
                                                        params: Params
                                                    })
                                                    .then(res => {
                                                        // console.log('basicWords ...',res)
                                                        if (res.data.count > 0) {
                                                            //self.formCustom.Items[xindex].value.status = res.data.content[0].status  +  '(' + res.data.content[0].timestamp +')'
                                                            self.$set(self.formCustom.Items[xindex].value, 'status', res.data.content[0].status + '(' + res.data.content[0].timestamp + ')')

                                                        } else {
                                                            // 以上表 都没找到，则显示为 新加
                                                            // console.log('not basicWords')
                                                            // self.formCustom.Items[xindex].value.status = '新加'
                                                            self.$set(self.formCustom.Items[xindex].value, 'status', '新加')
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
                                }
                            })
                            .catch(err => {
                                console.log(err)
                            })
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
                value: {
                    'word': '',
                    'category': [],
                    'status': '待查询...',
                    'source': '手动添加'
                },
                //index: this.formCustom.itemIndex
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
                        //console.log('新建')
                        // 构造最终结果集 , 并回传数据给 父组件，由父组件创建 
                        // console.log(self.shownformCustomItems)
                        let result = []
                        for (let ele in self.formCustom.Items) {
                            // if (self.formCustom.Items[ele].status === 1 && self.formCustom.Items[ele].value.status === '新加'){
                            //if (self.formCustom.Items[ele].status === 1 ){

                            // let temp = self.formCustom.Items[ele].value

                            // 判断是 手动添加 还是从 文件 添加
                            // 现在规定，在basicWords 界面 ，两种添加方式 都为:  手动添加
                            // if (self.formCustom.Items[0].value.source === '本地文件'){
                            //     console.log('本地文件')
                            //     
                            //     result.push({'word':self.formCustom.Items[ele].value.word, 'category':self.formCustom.Items[ele].value.category,'source':'手动添加'}) 
                            // }else {
                            //console.log('手动添加')
                            result.push({
                                'word': self.formCustom.Items[ele].value.word,
                                'category': self.formCustom.Items[ele].value.category,
                                'source': self.formCustom.Items[ele].value.source
                            })
                            //}
                            //}
                        }
                        // 发送创建 基础词  事件
                        //console.log('result',result)
                        if (result.length !== 0) {
                            // 只有包含新词时 才上传
                            self.$emit('createBasicWords', result)
                            self.$refs[name].resetFields()
                            self.$emit('update:basicWordItemShow', false)
                        } else {
                            self.$Message.warning('提交为空!');
                            self.$emit('update:basicWordItemShow', false)
                        }
                    } else {
                        //console.log('编辑')
                        //console.log(self.formCustom)
                        //let result = 
                        // 只有做了更改(基础词被修改 或 分类 被修改)，才更新
                        if (self.formCustom.Items[0].value.status.indexOf('新加') !== -1 || self.category_bak.split(',') !== self.formCustom.Items[0].value.category) {
                            let result = {
                                'word': self.formCustom.Items[0].value.word,
                                'category': self.formCustom.Items[0].value.category
                            }
                            self.$emit('UpdateBasicWords', {
                                'uid': self.formCustom.uid,
                                'data': result
                            })

                            // 更新 状态关联 词典信息 
                            if (self.formCustom.Items[0].value.status.indexOf('新加') !== -1 && (self.oldStatus.indexOf('停止') !== -1 || self.oldStatus.indexOf('无效') !== -1)) {
                                if (self.oldStatus.indexOf('停止') !== -1) {
                                    // 去停止词里面 更新 
                                    self.axios({
                                            method: "patch",
                                            url: self.baseurl + "StopDict/" + self.oldWord,
                                            data: {
                                                'word': self.formCustom.Items[0].value.word,
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
                                                if (res.data.count !== "") {
                                                    self.itemCount = res.data.count;
                                                }
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
                                    // 去 无效词里面更新
                                    self.axios({
                                            method: "patch",
                                            url: self.baseurl + "InvalidDict/" + self.currentComponent + "/" + self.oldWord,
                                            data: {
                                                'word': self.formCustom.Items[0].value.word,
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
                                                if (res.data.count !== "") {
                                                    self.itemCount = res.data.count;
                                                }
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
                        } else {
                            self.$Message.info('未做更改,无需更新!');
                        }
                        self.$refs[name].resetFields()
                        self.$emit('update:basicWordItemShow', false)
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
            this.$emit('update:basicWordItemShow', false)

        },
        modalDelete: function (uid) {
            // 触发删除事件 到 父组件
            // console.log('uid',uid)
            this.$emit('deletebasicWordItem', {
                'uid': uid
            })
            this.$emit('update:basicWordItemShow', false)
        }
    }
}
</script>

<style scoped>
.basicWords-itemPage {
    height: 500px;
    max-height: 550px;
    overflow: auto
}

.basicWords-itemPage .basicWords-itemPage-form-main {
    border: 1px dashed #81b165;
    border-radius: 5px;
    padding: 10px;
    margin-bottom: 10px;
}

.basicWords-itemPage-form-row {
    margin: 3px 0px;

}

.basicWords-itemPage-form-main-word {
    display: flex
}

.xyz {
    border: none !important
}

>>>.status .ivu-input.ivu-input-default {
    border: none !important
}

>>>.status .ivu-input.ivu-input-default:focus {
    outline: none;
    box-shadow: 0 0 0 0px
}

.basicWords-itemPage-form-main-status-delete {
    margin-left: 5px
}

.status.ivu-form-item,
.source.ivu-form-item {
    margin-bottom: 20px
}
</style>
