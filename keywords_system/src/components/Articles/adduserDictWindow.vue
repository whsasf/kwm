<template>
<div class="Url-itemPage">
    <i-modal v-model="addUserDictWindowShow" title="添加用户词" :closable="false" :mask-closable="false" :scrollable="true">

        <div class="Url-itemPage-form">

            <i-form ref="formCustom" :model="formCustom" :rules="ruleCustom" :label-width="100">

                <i-formItem label="用户词" prop="word">
                    <i-input class="management-newProject-name-input" @on-change="searchUserWordStatus(formCustom.word)" type="text" v-model="formCustom.word" placeholder="请输入用户词"></i-input>
                </i-formItem>

                <i-formItem class="status" label="状态:">
                    <i-row class="status-check">
                        <span class="xyz">{{status}}</span>
                    </i-row>
                </i-formItem>
            </i-form>

        </div>
        <div slot="footer">
            <i-button type="default" size="large" @click="modalCancel('formCustom')">取消</i-button>
            <i-button :disabled="submitAllow" type="primary" size="large" @click="modalOk('formCustom')">提交</i-button>
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
    name: 'adduserDictWindow',
    data() {
        const validateUserWord = (rule, value, callback) => {
            if (value === '') {
                callback(new Error('用户词不能为空'));

            } else {
                callback();
            }
        };
        return {
            submitAllow: true,
            status: '状态',
            formCustom: {
                word: ''
            },
            ruleCustom: {
                word: [{
                    validator: validateUserWord,
                    trigger: 'blur'
                }]
            },
        }
    },
    props: ['addUserDictWindowShow'],
    computed: {
        ...mapState(['baseurl', 'currentComponent']),
    },
    beforeDestroy() {},
    mounted() {},
    methods: {
        ...mapMutations(['changeUrlItemWindowShow']),
        searchUserWordStatus: function (wordPart) {

            //  从用户词典，停止词典，无效词典，中 ，搜索。如果找到 （第一个），显示 对应 状态，否则，状态为新，只有状态为新的 词 才能够 加入 用户词表
            // console.log('wordPart', wordPart)
            if (wordPart.replace(/ /g, '')) { // 空格不会激活 搜索
                this.status = '查询中 ...'
                this.checkIfExist(wordPart)
            }

        },
        checkIfExist: function (target) {
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
                        //self.$set(self.formCustom.Items[xindex].value, 'status', '停止 ' + '(' + res.data.content[0].modifiedTime + ')')
                        self.submitAllow = true
                        self.status = '已是 停止词'
                    } else {
                        // 没有从 StopDict 中 找到，现在寻找 InvalidDict 
                        // console.log('not StopDict')
                        let Params = {
                            'searchItem': target,
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
                                    //self.$set(self.formCustom.Items[xindex].value, 'status', '无效 ' + '(' + res.data.content[0].modifiedTime + ')')
                                    self.submitAllow = true
                                    self.status = '已是 无效词'
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
                                                //self.$set(self.formCustom.Items[xindex].value, 'status', '用户 ' + '(' + res.data.content[0].modifiedTime + ')')
                                                self.submitAllow = true
                                                self.status = '已是 用户词'
                                            } else {
                                                // 没有在 用户词典中 找到 ，需要搜索基础拓展词表
                                                // console.log('not userDict')
                                                self.status = '允许添加为 用户词'
                                                self.submitAllow = false
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
        modalOk: function (name) {
            let self = this
            // check 项目 是否为空
            self.$refs[name].validate((valid) => {
                if (valid) {
                    console.log('验证成功')
                    // 构造最终结果集
                    let userDictInfo = {}
                    userDictInfo['word'] = self.formCustom.word
                    userDictInfo['operator'] = localStorage.getItem('kwmUser')
                    // console.log(userDictInfo)

                    // 发送创建
                    self.axios({
                            method: 'post',
                            url: self.baseurl + 'UserDict/' + self.currentComponent,
                            data: [userDictInfo]
                        })
                        .then(() => {
                            //console.log(res)
                            self.$Message.success('增加用户词成功!');
                            self.$refs[name].resetFields()

                            // 重新分词
                            self.$emit('re-fenci')
                            self.$emit('update:addUserDictWindowShow', false)
                        })
                        .catch(err => {
                            console.log(err)
                            //self.$Message.error('增加用户词失败!');
                            self.$emit('update:addUserDictWindowShow', false)
                            self.$Message.error({
                                content: JSON.stringify(err.response.data.detail),
                                duration: 0,
                                closable: true
                            });
                        })

                } else {
                    self.$Message.error('提交失败');
                }
            })
        },
        modalCancel: function (name) {
            this.$refs[name].resetFields()
            this.$emit('update:addUserDictWindowShow', false)

        }
    }
}
</script>

<style scoped>
.xyz {
    background-color: yellow
}
</style>
