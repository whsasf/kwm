<template>
<div class="content-box">
    <h1 style="text-align:left">用途标签云</h1>
    <!-- vue的ref可以通过this.$refs.获取到DOM节点 -->
    <!-- echart容器div必须设置高度，否则不显示 -->
    <div ref="keyWords" class="mainc"></div>
</div>
</template>

<script>
import {
    mapState
} from "vuex";
export default {
    name: 'usageTag',
    data: function () {
        return {
            words: [],
            myChart: ''
        }
    },
    computed: {
        ...mapState([
            "baseurl",
            "currentComponent",
        ]),
    },
    mounted() {
        //this.$nextTick(() => {
        this.fetchData()
        // this.initEchart();
        //});
    },
    created() {

    },
    methods: {
        fetchData() {
            let self = this
            let words = []
            self.axios({
                    method: "get",
                    url: self.baseurl + "UsageTag/" + self.currentComponent,
                })
                .then((res) => {
                    words = JSON.parse(JSON.stringify(res.data))
                    self.initEchart(words)
                })
                .catch((err) => {
                    console.log(err);
                });
        },
        initEchart(words) {
            //获取DOM节点并初始化
            //console.log(words)
            let self = this
            self.myChart = self.$echarts.init(self.$refs.keyWords);
            let option = {
                tooltip: {
                    show: true
                },
                series: [{
                    name: "",
                    type: "wordCloud",
                    size: ["100%", "100%"],
                    textPadding: 0,
                    rotationRange: [0, 0],
                    autoSize: {
                        enable: true,
                        minSize: 10
                    },
                    textStyle: {
                        normal: {
                            color: function () {
                                return (
                                    "rgb(" +
                                    Math.round(Math.random() * 255) +
                                    ", " +
                                    Math.round(Math.random() * 255) +
                                    ", " +
                                    Math.round(Math.random() * 255) +
                                    ")"
                                );
                            }
                        }
                    },
                    data: words
                }]
            };

            //设置图表的参数
            self.myChart.setOption(option);
            self.myChart.on('click', function (params) {
                self.$router.push('/Project/' + (self.currentComponent) + '/extendedWords-bacicView?tagName=' + encodeURIComponent(params.data.name))
            });
        },
    }
}
</script>

<style scoped>
.mainc{
    min-height:500px;
    border:1px solid #777;
    over-flow: auto
}
.content-box {
    margin: 20px;
}
</style>
