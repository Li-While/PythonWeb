var chartDom = document.getElementById('chart0');
var myChart = echarts.init(chartDom);
var option;

option = {
    graphic: {
        elements: [
            {
                type: 'text',
                left: 'center',
                top: 'center',
                style: {
                    text: 'Li—Whale    ',
                    fontSize: 65,
                    fontWeight: 'bold',
                    lineDashOffset: 0,
                    fill: '#72afd3',
                    stroke: '#000',
                    lineWidth: 1
                },
                keyframeAnimation: {
                    duration: 3000,
                    loop: true,
                    keyframes: [

                        {
                            percent: 0.6,
                            style: {
                                fill: '#96fbc4',

                            }
                        },

                        {
                            percent: 0.9,
                            style: {
                                fill: 'yellow',
                                lineDashOffset: 200,
                                lineDash: [200, 0]
                            }
                        }
                    ]
                }
            }
        ]
    }
};

option && myChart.setOption(option);
