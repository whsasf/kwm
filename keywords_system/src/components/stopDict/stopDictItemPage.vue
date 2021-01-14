<template>
<div>
    <i-modal v-model="stopDictItemShow" :title="operation + '停止词'" width="500" :closable="false" :mask-closable="false" :styles="{top: '20px'}" :scrollable="true">

        <div class="stopWords-itemPage">

            <i-form ref="formCustom" :model="formCustom" :rules="ruleCustom" :label-width="80">

                <div class="stopWords-itemPage-form">
                    <div v-for="(item, index) in formCustom.Items" :key="index">
                        <div class="stopWords-itemPage-form-main">

                            <i-formItem :label="'停止词' + (parseInt(index)+1)" :prop="'Items.' + index + '.word'" :rules="ruleCustom.word">
                                <i-row class="stopWords-itemPage-form-main-word">
                                    <i-input class="stopWords-itemPage-form-main-word-input" type="text" v-model="item.word" placeholder="请输入停止词"></i-input>
                                    <i-button v-show="formCustom.uid === ''" class="stopWords-itemPage-form-main-status-delete" type="error" @click="handleRemove(index)">删除</i-button>
                                </i-row>
                            </i-formItem>

                        </div>
                    </div>
                </div>
                <i-formItem>
                    <i-row>
                        <i-col span="12">
                            <i-button v-show="formCustom.uid === ''" type="dashed" long @click="handleAdd()" icon="md-add">添加停止词</i-button>
                        </i-col>
                    </i-row>
                </i-formItem>

            </i-form>

        </div>
        <div slot="footer">
            <i-button v-show="formCustom.uid !== ''" class="stopWords-itemPage-delete-button" type="error" size="default" @click="modalDelete(formCustom.Items[0].word)">删除</i-button>
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
    name: 'stopDictItemPage',
    data() {
        const validateWord = (rule, value, callback) => {
            if (value.length === 0) {
                callback(new Error('停止词不能为空'));
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
    props: ['stopDictItemShow', 'formCustom2'],
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
            this.item_word_bak = JSON.parse(JSON.stringify(this.formCustom2.Items[0].word))
        }
    },
    methods: {
        handleAdd: function () {
            this.formCustom.itemIndex++
            this.formCustom.Items.push({
                word: '',
                operator: localStorage.getItem('kwmUser'),
                source: '手动添加'
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
                        // console.log(self.shownformCustomItems)
                        let result = []
                        for (let ele in self.formCustom.Items) {
                            result.push({
                                'word': self.formCustom.Items[ele].word,
                                'operator': localStorage.getItem('kwmUser'), //self.formCustom.Items[ele].operator,
                                'source': '手动添加',
                                'exStatus': ''
                            })
                        }
                        // 发送创建 基础词  事件

                        if (result.length !== 0) {
                            //只有包含新词时 才上传
                            self.$emit('createStopWords', result)
                            self.$refs[name].resetFields()
                            self.$emit('update:stopDictItemShow', false)
                        } else {
                            self.$Message.warning('未创建新停止词!');
                            self.$emit('update:stopDictItemShow', false)
                        }
                    } else {
                        //console.log('编辑模式...')
                        // 只有真的改了，才更新
                        if (self.item_word_bak === self.formCustom.Items[0].word) {
                            // 没有改，什么也不做
                            self.$Message.info('未修改!');
                        } else {
                            let result = {
                                'word': self.formCustom.Items[0].word,
                                'operator': localStorage.getItem('kwmUser'), //self.formCustom.Items[0].operator,
                                // 'exStatus': self.formCustom.Items[0].exStatus,
                            }
                            self.$emit('UpdateStopWords', {
                                'uid': self.formCustom.uid,
                                'data': result
                            })
                        }
                        self.$refs[name].resetFields()
                        self.$emit('update:stopDictItemShow', false)
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
            this.$emit('update:stopDictItemShow', false)

        },
        modalDelete: function (word) {
            // 触发删除事件 到 父组件
            // console.log('uid',uid)
            this.$emit('deleteStopWordItem', {
                'word': word
            })
            this.$emit('update:stopDictItemShow', false)
        }
    }
}
</script>

<style scoped>
.stopWords-itemPage {
    height: 400px;
    max-height: 400px;
    overflow: auto
}

.stopWords-itemPage .stopWords-itemPage-form-main {
    border: 1px dashed #81b165;
    border-radius: 5px;
    padding: 10px;
    margin-bottom: 10px;
}

.stopWords-itemPage-form-row {
    margin: 3px 0px;

}

.stopWords-itemPage-form-main-status.ivu-row {
    width: 330px;
    margin-left: 80px;
}

.stopWords-itemPage-form-main-word {
    display: flex
}
</style>
