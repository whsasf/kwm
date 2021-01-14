<template>
<div class="singnin">
    <i-form ref="formInline" :model="formInline" :rules="ruleInline">
        <i-formItem prop="account">
            <i-input type="text" v-model="formInline.account" placeholder="用户名为公司邮箱" :clearable=true>
                <i-icon type="ios-mail-outline" slot="prepend"></i-icon>
            </i-input>
        </i-formItem>
        <i-formItem prop="shadow">
            <i-input type="password" v-model="formInline.shadow" placeholder="密码" :clearable=true>
                <i-icon type="ios-lock-outline" slot="prepend"></i-icon>
            </i-input>
        </i-formItem>
        <i-formItem>
            <i-button type="primary" @click="handleSubmit('formInline')">登录</i-button>
            <div class="singnin-signup">
                <p>还没有账户？</p>
                <router-link to='/Account/Signup'>注册账户</router-link>
            </div>
        </i-formItem>
    </i-form>
</div>
</template>

<script>
import {
    mapState,
    mapMutations
} from 'vuex'
import sha1 from 'sha1'
export default {
    name: 'Signin',
    data() {
        return {
            formInline: {
                account: '',
                shadow: ''
            },
            ruleInline: {
                account: [{
                        required: true,
                        message: '用户名不能为空',
                        trigger: 'blur'
                    },
                    {
                        type: 'email',
                        message: '邮箱格式不正确',
                        trigger: 'blur'
                    }
                ],
                shadow: [{
                        required: true,
                        message: '请输入密码',
                        trigger: 'blur'
                    },
                    {
                        type: 'string',
                        min: 6,
                        message: '密码长度要大于6',
                        trigger: 'blur'
                    }
                ]
            }
        }
    },
    computed: {
        ...mapState(['baseurl'])
    },
    methods: {
        ...mapMutations(['changeCollpsed']),
        handleSubmit(name) {
            let self = this
            self.$refs[name].validate((valid) => {
                if (valid) {
                    // 发送
                    let payLoad = {
                        'account': self.formInline.account,
                        'shadow': sha1(self.formInline.shadow)
                    }
                    self.axios({
                            method: 'post',
                            url: self.baseurl + 'Account/Signin',
                            data: payLoad
                        })
                        .then(res => {
                            // console.log(res)
                            if (res){
                                self.$Message.success('登录成功!')
                            }else{
                                self.$Message.error('登录失败!')
                            }
                            // 保存jwt  和  用户名 到localstroage
                            localStorage.setItem('kwmdepart', res.data.department)
                            localStorage.setItem('kwmjWT', res.data.access_token)
                            localStorage.setItem('kwmUser', res.data.username)
                            //localStorage.removeItem('nav_selected')
                            self.changeCollpsed(true)
                            setTimeout(() => {
                                self.$router.push('/')
                            }, 2)
                        })
                        .catch(err => {
                            self.$Message.error(err.response.data.detail);
                            // console.log(err)
                        })
                } else {
                    self.$Message.error('登录失败!');
                }
            })
        }
    }
}
</script>

<style scoped>

</style>
