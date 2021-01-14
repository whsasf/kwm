<template>
<div>
    <i-modal v-model="userDictItemShow" :title="operation + '用户词'" width="500" :closable="false" :mask-closable="false" :styles="{top: '20px'}" :scrollable="true">

        <div class="userDictWords-itemPage">

            <i-form ref="formCustom" :model="formCustom" :rules="ruleCustom" :label-width="80">

                <div class="userDictWords-itemPage-form">
                    <div v-for="(item, index) in formCustom.Items" :key="index">
                        <div class="userDictWords-itemPage-form-main">

                            <i-formItem :label="'用户词' + (parseInt(index)+1)" :prop="'Items.' + index + '.word'" :rules="ruleCustom.word">
                                <i-row class="userDictWords-itemPage-form-main-word">
                                    <i-input class="userDictWords-itemPage-form-main-word-input" type="text" v-model="item.word" placeholder="请输用户词"></i-input>
                                    <i-button v-show="formCustom.uid === ''" class="userDictWords-itemPage-form-main-status-delete" type="error" @click="handleRemove(index)">删除</i-button>
                                </i-row>
                            </i-formItem>

                            <i-formItem label="出处" :prop="'Items.' + index + '.source'">
                                <i-input class="userDictWords-itemPage-form-main-word-input" type="text" v-model="item.source" placeholder="请输入出处"></i-input>
                            </i-formItem>

                        </div>
                    </div>
                </div>
                <i-formItem>
                    <i-row>
                        <i-col span="12">
                            <i-button v-show="formCustom.uid === ''" type="dashed" long @click="handleAdd()" icon="md-add">添加用户词</i-button>
                        </i-col>
                    </i-row>
                </i-formItem>

            </i-form>

        </div>
        <div slot="footer">
            <i-button v-show="formCustom.uid !== ''" class="userDictWords-itemPage-delete-button" type="error" size="default" @click="modalDelete(formCustom.Items[0].word)">删除</i-button>
            <i-button type="default" size="large" @click="modalCancel('formCustom')">取消</i-button>
            <i-button :disabled="formCustom.Items && formCustom.Items.length === 0" type="primary" size="large" @click="modalOk('formCustom')">提交</i-button>
        </div>
    </i-modal>
</div>
</template>

<script>
import {
    mapState
} from 'vuex'
export default {
    name: 'userDictItemPage',
    data() {
        const validateWord = (rule, value, callback) => {
            if (value.length === 0) {
                callback(new Error('用户词不能为空'));
            } else {
                callback();
            }
        };

        return {
            item_word_bak: '',
            formCustom: {},
            ruleCustom: {
                word: [{
                    validator: validateWord,
                    trigger: 'blur,change'
                }]
            },
        }
    },
    props: ['userDictItemShow', 'formCustom2'],
    computed: {
        ...mapState(['baseurl', 'currentComponent']),
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
            this.$set(this.formCustom, 'uid', this.formCustom2.uid)
            this.$set(this.formCustom, 'itemIndex', this.formCustom2.itemIndex)
            this.$set(this.formCustom, 'Items', this.formCustom2.Items)
            this.dataBak = JSON.parse(JSON.stringify(this.formCustom2.Items[0]))
            this.item_word_bak = JSON.parse(JSON.stringify(this.formCustom2.Items[0].word))
        }
    },
    methods: {
        handleAdd: function () {
            this.formCustom.itemIndex++
            this.formCustom.Items.push({
                word: '',
                source: '',
                //operator: localStorage.getItem('kwmUser'),
            });

        },
        handleRemove: function (index) {
            this.formCustom.Items.splice(index, 1)
        },
        modalOk: function (name) {
            let self = this
            // console.log('验证成功',self.formCustom.Items[0].value.word)
            // check 项目 是否为空
            self.$refs[name].validate((valid) => {
                if (valid) {
                    if (self.formCustom.uid === '') {
                        //console.log('新建模式 ...')
                        //console.log('验证成功', self.formCustom)
                        // 构造最终结果集 , 并回传数据给 父组件，由父组件创建 

                        let result = []
                        for (let ele in self.formCustom.Items) {
                            result.push({
                                'word': self.formCustom.Items[ele].word,
                                'operator': localStorage.getItem('kwmUser'), //self.formCustom.Items[ele].operator,
                                'source': self.formCustom.Items[ele].source
                            })
                        }
                        // 发送创建 基础词  事件

                        if (result.length !== 0) {
                            //只有包含新词时 才上传
                            self.$emit('createUserWords', result)
                            self.$refs[name].resetFields()
                            self.$emit('update:userDictItemShow', false)
                        } else {
                            self.$Message.warning('未创建新用户词!');
                            self.$emit('update:userDictItemShow', false)
                        }
                    } else {
                        //console.log('编辑模式...')
                        // // 只有真的改了，才更新

                        let result = {
                            'word': self.formCustom.Items[0].word,
                            'source': self.formCustom.Items[0].source,
                            'operator': localStorage.getItem('kwmUser'), //self.formCustom.Items[0].operator
                            // 'exStatus': self.formCustom.Items[0].exStatus,
                        }

                        // 对比，之前保存的最初状态，只提交被更改过的字段
                        for (let ele in self.dataBak) {
                            if (JSON.stringify(self.dataBak[ele]) === JSON.stringify(result[ele])) {
                                // 字段没有改变，则从result中移除
                                delete result[ele]
                            }
                        }
                        // 如果 result 为空或 只有 operator， 则 不更新，否则更新
                        if (Object.keys(result).length === 0 || (Object.keys(result).length === 1 && Object.keys(result)[0] === 'operator')) {
                            self.$Message.info('没有任何更新，无须更新!');
                        } else {
                            self.$emit('UpdateUserWords', {
                                'uid': self.formCustom.uid,
                                'data': result
                            })

                        }

                        self.$refs[name].resetFields()
                        self.$emit('update:userDictItemShow', false)
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
            this.$emit('update:userDictItemShow', false)

        },
        modalDelete: function (word) {
            // 触发删除事件 到 父组件
            // console.log('uid',uid)
            this.$emit('deleteUserDictWordItem', [{
                'word': word
            }])
            this.$emit('update:userDictItemShow', false)
        }
    }
}
</script>

<style scoped>
.userDictWords-itemPage {
    height: 400px;
    max-height: 400px;
    overflow: auto
}

.userDictWords-itemPage .userDictWords-itemPage-form-main {
    border: 1px dashed #81b165;
    border-radius: 5px;
    padding: 10px;
    margin-bottom: 10px;
}

.userDictWords-itemPage-form-row {
    margin: 3px 0px;

}

.userDictWords-itemPage-form-main-status.ivu-row {
    width: 330px;
    margin-left: 80px;
}

.userDictWords-itemPage-form-main-word {
    display: flex
}
</style>
