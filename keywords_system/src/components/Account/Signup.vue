<template>
<div class="singnup">
    <i-form ref="formInline" :model="formInline" :rules="ruleInline">
        <i-formItem prop="account">
            <i-input type="email" v-model="formInline.account" placeholder="用户名须为公司邮箱" :clearable=true>
                <i-icon type="ios-mail-outline" slot="prepend"></i-icon>
            </i-input>
        </i-formItem>
        <i-formItem prop="password1">
            <i-input type="password" v-model="formInline.password1" placeholder="密码" :clearable=true>
                <i-icon type="ios-lock-outline" slot="prepend"></i-icon>
            </i-input>
        </i-formItem>
        <i-formItem prop="password2">
            <i-input type="password" v-model="formInline.password2" placeholder="密码" :clearable=true>
                <i-icon type="ios-lock-outline" slot="prepend"></i-icon>
            </i-input>
        </i-formItem>
        <i-formItem prop="department" class="depart">
            <div class="department-icon">
                <i-icon type="md-people"></i-icon>
            </div>
            <i-select class="departSelect" v-model="formInline.department" placeholder="请选择所属部门" :filterable=true>
                <i-option v-for="item in departments" :key="item" :value="item">{{ item }}</i-option>
            </i-select>
        </i-formItem>
        <i-formItem>
            <i-button type="primary" @click="handleSubmit('formInline')">注册</i-button>
            <div class="singnin-signup">
                <p>已经有账户？</p>
                <router-link to='/Account/Signin'>登录</router-link>
            </div>
        </i-formItem>
    </i-form>
</div>
</template>

<script>
import {
    mapState
} from 'vuex'
import sha1 from 'sha1'
export default {
    name: 'Signup',
    data() {
        const validatePass = (rule, value, callback) => {
            if (value === '') {
                callback(new Error('请输入密码'));
            } else if (value.length < 6) {
                callback(new Error('密码长度须大于6'));
            } else {
                if (this.formInline.password2 !== '') {
                    // 对第二个密码框单独验证
                    this.$refs.formInline.validateField('password2');
                }
                callback();
            }
        };
        const validatePass2 = (rule, value, callback) => {
            if (value === '') {
                callback(new Error('请再次输入密码'));
            } else if (value.length < 6) {
                callback(new Error('密码长度须大于6'));
            } else if (value !== this.formInline.password1) {
                callback(new Error('两次密码不匹配'));
            } else {
                callback();
            }
        };
        return {
            ct: null,
            departments: [
                '技术部',
                '产品部',
                '淘宝运营部',
                '货源部',
                '流量中心-推广一部',
                '流量中心-推广二部',
                '流量中心-增长一部',
                '流量中心-增长二部',
                '销售部',
                '客服部',
                '品牌部',
                'APP运营部',
                '内容规划',
                '核算',
                '人事行政部',
                '优翔广告部'
            ],
            formInline: {
                account: '',
                password1: '',
                password2: '',
                department: ''
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
                password1: [{
                    validator: validatePass,
                    trigger: 'blur'
                }],
                password2: [{
                    validator: validatePass2,
                    trigger: 'blur'
                }],
                department: [{
                    required: true,
                    message: '部门不能为空',
                    trigger: 'change'
                }],
            }
        }
    },
    computed: {
        ...mapState(['baseurl'])
    },
    beforeDestroy() {
        clearTimeout(this.ct)
    },
    methods: {
        handleSubmit(name) {
            let self = this
            self.$refs[name].validate((valid) => {
                if (valid) {
                    console.log('验证成功')
                    //注册
                    let payLoad = {
                        'account': self.formInline.account,
                        'shadow': sha1(self.formInline.password1),
                        'department': self.formInline.department
                    }
                    self.axios({
                            method: 'post',
                            url: self.baseurl + 'Account/Signup',
                            data: payLoad
                        })
                        .then(res => {
                            //console.log(res)
                            self.$Message.success(res.data.detail);
                            self.ct = setTimeout(() => {
                                self.$router.push('/Account/Signin')
                            }, 2)
                        })
                        .catch(err => {
                            //console.log(err)
                            self.$Message.error(err.response.data.detail);
                            // console.log(err)
                        })
                } else {
                    self.$Message.error('注册失败!');
                }
            })
        }
    }
}
</script>

<style scoped>

.depart .department-icon {
    display: flex;
    border-bottom-right-radius: 0 !important;
    border-top-right-radius: 0 !important;
    padding: 4px 7px;
    font-size: inherit;
    font-weight: 400;
    line-height: 1;
    color: #515a6e;
    text-align: center;
    background-color: #f8f8f9;
    border: 1px solid #dcdee2;
    border-right: 0;
    border-radius: 4px;
    align-items: center
}
</style>
