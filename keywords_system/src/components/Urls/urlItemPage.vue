<template>
<div class="Url-itemPage">
    <i-modal v-model="urlItemWindowShow" :title="urlItemPageTitle" width="60" :closable="false" :mask-closable="false" :styles="{top: '20px'}" :scrollable="true">

        <div class="Url-itemPage-form">

            <i-form ref="formCustom" :model="formCustom" :label-width="50">
                <div v-for="(item1, index1) in formCustom.Items" :key="index1">
                    <div class="urlNewPageOutloop">
                        <i-formItem :label="'url' + (index1 + 1)" :prop="'Items.' +  index1 +'.rootUrl'" :rules="ruleCustom.rootUrl">

                            <div class="together">
                                <i-input class="management-newProject-name-input" type="text" v-model="item1.rootUrl" placeholder="请输入名称"></i-input>
                                <i-button size="small" type="error" @click="handleRemoveItem(index1)">删除整项</i-button>
                            </div>
                        </i-formItem>
                        <div class="Url-itemPage-form-urlIncludePath">
                            <div v-for="(item2, index2) in item1.urlIncludePath" :key="index2">

                                <i-row>
                                    <i-col class="Url-itemPage-form-urlIncludePath-inputs">
                                        <label class="xlabel">{{'允许路径' + (parseInt(index2) + 1) + ' '}}</label>
                                        <i-formItem class="Url-itemPage-form-urlIncludePath-inputs-input" :prop=" 'Items.' + index1 + '.urlIncludePath.' +  index2  + '.path'" :rules="ruleCustom.path">
                                            <i-input type="text" v-model="item2.path" placeholder="请输入允许路径"></i-input>
                                        </i-formItem>
                                        <i-formItem class="Url-itemPage-form-urlIncludePath-inputs-select" :prop=" 'Items.' + index1 + '.urlIncludePath.' +  index2  + '.type'" :rules="ruleCustom.type">
                                            <i-select v-model="item2.type">
                                                <i-option v-for="(item3,index3) in urlIncludePathSets" :value="item3" :key="index3">{{ item3 }}</i-option>
                                            </i-select>
                                        </i-formItem>
                                        <i-button class="Url-itemPage-form-urlIncludePath-inputs-delete" size="small" type="error" @click="handleRemove('include',index1,index2)">删除</i-button>
                                    </i-col>
                                </i-row>

                            </div>
                            <i-row>
                                <i-col class="addl" offset="8" span="12">
                                    <i-button type="dashed" long @click="handleAdd(index1,'include')" icon="md-add">添加允许路径项</i-button>
                                </i-col>
                            </i-row>
                        </div>
                        <div class="Url-itemPage-form-urlExcludePath">
                            <div v-for="(item4, index4) in item1.urlExcludePath" :key="index4">
                                <i-row>
                                    <i-col class="Url-itemPage-form-urlExcludePath-inputs">
                                        <label class="xlabel">{{'排除路径' + (parseInt(index4) + 1) + ' '}}</label>
                                        <i-formItem class="Url-itemPage-form-urlExcludePath-inputs-input" :prop=" 'Items.' + index1 + '.urlExcludePath.' +  index4  + '.path'" :rules="ruleCustom.path">
                                            <i-input type="text" v-model="item4.path" placeholder="请输入排除路径"></i-input>
                                        </i-formItem>

                                        <i-formItem class="Url-itemPage-form-urlExcludePath-inputs-select" :prop=" 'Items.' + index1 + '.urlExcludePath.' +  index4  + '.type'" :rules="ruleCustom.type">
                                            <i-select v-model="item4.type">
                                                <i-option v-for="(item5,index5) in urlIncludePathSets" :value="item5" :key="index5">{{ item5 }}</i-option>
                                            </i-select>
                                        </i-formItem>
                                        <i-button class="Url-itemPage-form-urlExcludePath-inputs-delete" size="small" type="error" @click="handleRemove('exclude',index1,index4)">删除</i-button>
                                    </i-col>
                                </i-row>

                            </div>

                            <i-row>
                                <i-col class="addl" offset="8" span="12">
                                    <i-button type="dashed" long @click="handleAdd(index1,'exclude')" icon="md-add">添加排除路径项</i-button>
                                </i-col>
                            </i-row>

                        </div>
                        <i-formItem :prop=" 'Items.' + index1 + '.category'" :rules="ruleCustom.category">
                            <div class="Url-itemPage-form-category-inside">
                                <label class="Url-itemPage-form-category-label">分类(可多选)</label>

                                <i-select class="Url-itemPage-form-category-select" multiple v-model="item1.category">
                                    <i-option v-for="item6 in rowCategoies" :value="item6" :key="item6">{{ item6 }}</i-option>
                                </i-select>
                            </div>
                        </i-formItem>
                    </div>
                </div>
                <i-formItem>
                    <i-row>
                        <i-col span="12">
                            <i-button v-show="formCustom.uid === ''" type="default" long @click="handleAddItem()" icon="md-add">添加Url</i-button>
                        </i-col>
                    </i-row>
                </i-formItem>
            </i-form>
        </div>
        <div slot="footer">
            <i-button v-show="formCustom.uid" class="Url-itemPage-delete-button" type="error" size="default" @click="modalDelete()">删除</i-button>
            <i-button type="default" size="large" @click="modalCancel('formCustom')">取消</i-button>
            <i-button :disabled="this.finalCount === 0" type="primary" size="large" @click="modalOk('formCustom')">提交</i-button>
        </div>
    </i-modal>
</div>
</template>

<script>
import {
    mapState
} from 'vuex'
export default {
    name: 'itemPage',
    data() {
        const validateUrl = (rule, value, callback) => {
            if (value === '') {
                callback(new Error('url不能为空'));
            } else if (!value.toLowerCase().startsWith('https://') && !value.toLowerCase().startsWith('http://')) {
                callback(new Error('url应以http://或https://开头'));
            } else {
                callback();
            }
        };
        const validatePath = (rule, value, callback) => {
            if (value === '') {
                callback(new Error('路径不能为空'));
            } //else if (!value.toLowerCase().startsWith('https://') && !value.toLowerCase().startsWith('http://')) {
            //  callback(new Error('路径应以http://或https://开头'));
            //} 
            else {
                callback();
            }
        };
        const validateType = (rule, value, callback) => {
            if (value === '') {
                callback(new Error('type不能为空'));
            } else if (value.toLowerCase() !== 'regex' && value.toLowerCase() !== '包含') {
                callback(new Error('type只能是\'regex\' 或 \'包含\''));
            } else {
                callback();
            }
        };

        const validateCategory = (rule, value, callback) => {
            if (value.length === 0) {
                //console.log('category empty')
                callback(new Error('分类不能为空'));
            } else {
                for (let ele in value) {
                    if (this.rowCategoies.indexOf(value[ele]) === -1) {
                        callback(new Error('包含未定义分类:' + value[ele]));
                    }
                }
                callback();
            }
        };
        return {
            finalCount: 1,
            formCustom: {},
            urlIncludePathSets: [
                'regex',
                '包含'
            ],

            ruleCustom: {
                rootUrl: [{
                    validator: validateUrl,
                    trigger: 'blur'
                }],
                path: [{
                    validator: validatePath,
                    trigger: 'blur'
                }],
                type: [{
                    validator: validateType,
                    trigger: 'blur,change'
                }],
                category: [{
                    validator: validateCategory,
                    trigger: 'blur,change'
                }]
            },
        }
    },
    props: ['urlItemPageTitle', 'urlItemWindowShow', 'formCustom2', 'rowCategoies'],
    computed: {
        ...mapState(['currentUserName', 'baseurl', 'currentComponent'])
    },
    beforeDestroy() {},
    mounted() {
        // console.log('mounted')
        if (JSON.stringify(this.formCustom2) !== "{}" && this.urlItemWindowShow === true) {
            this.$set(this.formCustom, 'itemIndex', this.formCustom2.itemIndex)
            this.$set(this.formCustom, 'uid', this.formCustom2.uid)
            this.$set(this.formCustom, 'Items', this.formCustom2.Items)
            // setTimeout(() => this.preSubmit('formCustom'), 2000) // 预提交，显示错误
            this.$nextTick(() => {
                if (this.formCustom2.uid === '' && this.formCustom2.Items[0].rootUrl !== '') {
                    this.preSubmit('formCustom')
                }

            });
        }
        // console.log(this.formCustom, '0000')
    },
    methods: {
        handleRemoveItem: function (index) {
            this.formCustom.Items.splice(index, 1)
            if (this.formCustom.Items.length === 0) {
                this.finalCount = 0
            }
        },
        handleAddItem: function () {
            this.formCustom.itemIndex++
            // 如果 items为空，则category 也只能为空
            let xcategory = ''
            if (this.formCustom.Items.length === 0) {
                xcategory = []
            } else {
                xcategory = this.formCustom.Items[0].category
            }
            this.formCustom.Items.push({

                index: this.formCustom.itemIndex,
                rootUrl: '',
                //category: [],
                //category: this.rowCategoies,
                category: xcategory,
                statusEdit: '未开始',
                urlIncludeIndex: 0,
                urlExcludeIndex: 0,
                urlIncludePath: [],
                urlExcludePath: []
            });
            this.finalCount = 1

        },
        handleAdd: function (index, type) {
            let self = this
            if (type === 'include') {
                //this.$set(this.formCustom, 'urlIncludeIndex', this.formCustom.urlIncludeIndex++);
                self.formCustom.urlIncludeIndex++
                self.formCustom.Items[index].urlIncludePath.push({
                        'path': '',
                        type: 'regex'
                    }
                    //index: self.formCustom.urlIncludeIndex,
                );
            } else if (type === 'exclude') {
                self.formCustom.urlExcludeIndex++
                self.formCustom.Items[index].urlExcludePath.push({
                        'path': '',
                        type: 'regex'
                    }
                    //index: self.formCustom.urlExcludeIndex,
                );
            }
        },
        handleRemove: function (urlType, index, index2) {
            //console.log(index)
            if (urlType === 'include') {
                this.formCustom.Items[index].urlIncludePath.splice(index2, 1)
                // console.log(this.formCustom.urlIncludePath)
            } else if (urlType === 'exclude') {
                this.formCustom.Items[index].urlExcludePath.splice(index2, 1)
            }
        },
        preSubmit: function (name) {
            // 为了显示存在的出错误，所以先提交一次， 内容不会提交到后端
            this.modalOk(name)
        },
        modalOk: function (name) {
            let self = this
            // check 项目 是否为空
            self.$refs[name].validate((valid) => {
                if (valid) {
                    console.log('验证成功')
                    // console.log('valid',self.formCustom)
                    // 构造最终结果集,循环
                    let final = []
                    for (let ele in self.formCustom.Items) {
                        let dataline = self.formCustom.Items[ele]
                        let itemInfo = {}
                        itemInfo['rootUrl'] = dataline.rootUrl
                        itemInfo['category'] = dataline.category
                        itemInfo['status'] = '未开始'
                        let tempurlIncludePath = []
                        let tempurlExcludePath = []
                        for (let indexy in dataline.urlIncludePath) {
                            tempurlIncludePath.push(dataline.urlIncludePath[indexy])
                        }
                        for (let indexy in dataline.urlExcludePath) {
                            tempurlExcludePath.push(dataline.urlExcludePath[indexy])
                        }
                        itemInfo['urlIncludePath'] = tempurlIncludePath
                        itemInfo['urlExcludePath'] = tempurlExcludePath
                        final.push(itemInfo)
                    }
                    // console.log(final,'final')

                    // 得到 项目添加的有效数据，并返回到父组件
                    // 判断是新建还是  编辑， formCustom 中包含 uid的是编辑
                    if (!self.formCustom.uid) {
                        //console.log('新建urls')
                        //新建
                        self.$emit('createUrlNewItem', {
                            'uid': '',
                            'data': final
                        })
                    } else {
                        // 编辑模式，此时需要将uid传递回去
                        //console.log(final)
                        self.$emit('createUrlNewItem', {
                            'uid': self.formCustom.uid,
                            'data': final
                        })
                    }
                    self.$emit('update:urlItemWindowShow', false)

                } else {
                    // console.log('验证失败')
                    self.$Message.error('提交失败');
                    // self.modal1 = true
                }
            })
        },
        modalCancel: function (name) {
            this.$refs[name].resetFields()
            this.$emit('update:urlItemWindowShow', false)

        },
        modalDelete: function () {
            // 触发删除事件 到 父组件
            this.$emit('deleteUrlNewItem', {
                'uid': this.formCustom.uid
            })
            this.$emit('update:urlItemWindowShow', false)
        }
    }
}
</script>

<style scoped>
.Url-itemPage {}

.Url-itemPage-form {
    height: 570px;
    max-height: 570px;
    overflow: auto
}

.Url-itemPage-form-urlIncludePath,
.Url-itemPage-form-urlExcludePath {
    margin-left: 50px;
    border: 1px dashed #81b165;
    border-radius: 5px;
    padding: 5px;
    margin-bottom: 5px;
    margin-top: 25px
}

.Url-itemPage-form-urlIncludePath-inputs,
.Url-itemPage-form-urlExcludePath-inputs {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
}

.Url-itemPage-form-urlIncludePath-inputs-input,
.Url-itemPage-form-urlExcludePath-inputs-input {
    flex: 5;
}

.Url-itemPage-form-urlIncludePath-inputs-select,
.Url-itemPage-form-urlExcludePath-inputs-select {
    flex: 4;
    margin-left: 5px
}

.Url-itemPage-form-urlIncludePath-inputs-delete,
.Url-itemPage-form-urlExcludePath-inputs-delete {
    flex: 1;
    margin-left: 5px
}

.Url-itemPage-form-urlIncludePath .ivu-form-item,
.Url-itemPage-form-urlExcludePath .ivu-form-item {
    margin-bottom: 20px;
}

.Url-itemPage-form-category-inside,
.Url-itemPage-form-status-inside {
    display: flex
}

.Url-itemPage-form-category-label,
.Url-itemPage-form-status-label {
    flex: 1
}

.Url-itemPage-form-category-select,
.Url-itemPage-form-status-input {
    flex: 4
}

.Url-itemPage-form .Url-itemPage-form-category>>>.ivu-form-item-content,
.Url-itemPage-form .Url-itemPage-form-status>>>.ivu-form-item-content {
    margin-left: 10px !important
}

.ivu-form-item {
    margin-bottom: 5px
}

.Url-itemPage-delete-button {
    margin-right: 80px
}

.urlNewPageOutloop {
    border: 1px solid red;
    border-radius: 5px;
    padding: 2px 10px 15px 10px;
}

.together {
    display: flex;
    align-items: center
}

>>>.ivu-form-item-content {
    margin-left: 0 !important
}

>>>.ivu-select-dropdown {}

.xlabel {
    margin-right: 5px
}

.addl {
    margin-top: 5px
}
</style>
