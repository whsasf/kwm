<template>
<div class="">
    <i-modal v-model="toStopConfirmShow" title="任性添加确认" width="50" :closable="false" :mask-closable="false" :scrollable="true">

        <div slot="footer">
            <i-button type="default" size="large" @click="modalCancel()">取消</i-button>
            <i-button type="primary" size="large" @click="modalOk()">确定</i-button>
        </div>

    </i-modal>
</div>
</template>

<script>
import {
    mapState
} from 'vuex'
export default {
    name: 'toStopConfirm',
    data() {
        return {}
    },
    mounted() {},

    props: ['toStopConfirmShow'],
    computed: {
        ...mapState(['baseurl', 'currentComponent']),
    },
    beforeDestroy() {},
    methods: {
        modalOk() {
            this.$emit('update:toStopConfirmShow', false)
        },
        modalCancel() {
            //this.changeDetailWindowShow(false)
            this.$emit('update:toStopConfirmShow', false)
        }
    }
}
</script>

<style scoped>

</style>
