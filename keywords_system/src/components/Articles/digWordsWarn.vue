<template>
<div class="Urls-seeDetail">
    <i-modal v-model="showdigWords" title="挖词警报" :closable="false" :mask-closable="false" :scrollable="true">
        <div class="digWords">
            <div class="part1">
                <h4 v-if="UserDictItemCount ===0 && StopDictItemCount === 0">当前 停用词典 与 用户词典 为空，请确定是否进行挖词</h4>
                <h4 v-else-if="UserDictItemCount ===0 && StopDictItemCount !== 0">当前 用户词典 为空，请确定是否进行挖词</h4>
                <h4 v-else-if="UserDictItemCount !==0 && StopDictItemCount === 0">当前 停用词典 为空，请确定是否进行挖词</h4>
                <h4 v-else></h4>
                <div class="button-group">
                    <i-button class="button-p1" type="default" size="large" @click="modalCancel()">取消</i-button>
                    <i-button class="button-p2" type="success" size="large" @click="modalOk()">确定</i-button>
                </div>
            </div>

            <div class="part2">
                <i-button class="button-p3" type="primary" size="small" @click="goToStopDict()">查看停用词</i-button>
                <i-button class="button-p4" type="primary" size="small" @click="goToUserDict()">查看用户词</i-button>
            </div>
        </div>
        <div slot="footer">
            <i-button type="default" size="large" @click="modalCancel()">关闭</i-button>
        </div>
    </i-modal>
</div>
</template>

<script>
import {
    mapState
} from 'vuex'
export default {
    name: 'digWordsWarn',
    data() {
        return {}
    },
    mounted() {
        // console.log(this.detailIndex,this.pageData)
    },
    props: ['showdigWords', 'UserDictItemCount', 'StopDictItemCount'],
    computed: {
        ...mapState(['currentUserName', 'currentComponent']),
    },
    beforeDestroy() {},
    methods: {
        modalOk: function () {
            //console.log('开始挖词,挖词中...')
            this.$emit('runDig')
            this.$emit('update:showdigWords', false)
        },
        modalCancel: function () {
            //this.showSeeUrlConfig = false
            this.$emit('update:showdigWords', false)
        },
        goToStopDict: function () {
            this.$emit('update:showdigWords', false)
            this.$router.push('/Project/' + this.currentComponent + '/StopDict')
        },
        goToUserDict: function () {
            this.$emit('update:showdigWords', false)
            this.$router.push('/Project/' + this.currentComponent + '/userDict')
        },
    }
}
</script>

<style scoped>
.digWords {
    display: flex;

}

.part1 {
    flex: 6
}

.part2 {
    flex: 2;
    display: flex;
    flex-direction: column;
    align-items: center
}

.button-group {
    margin-top: 30px;
    display: flex
}

.button-p1 {
    flex: 2;
    margin: 10px
}

.button-p2 {
    flex: 2;
    margin: 10px
}

.part2 .button-p3 {
    margin-top: 20px
}

.part2 .button-p4 {
    margin-top: 20px
}
</style>
