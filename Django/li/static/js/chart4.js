var chartDom4 = document.getElementById('chart4');
var myChart4 = echarts.init(chartDom4);
var option4;

const graphData = [
    ['2022-10-01', 240],
    ['2022-10-09', 600],
    ['2022-10-27', 379],
    ['2022-11-13', 847],
    ['2022-11-18', 247],
    ['2022-11-23', 731],
    ['2022-11-30', 985]
];
const links = graphData.map(function (item, idx) {
    return {
        source: idx,
        target: idx + 1
    };
});
links.pop();
function getVirtulData(year) {
    year = year || '2022';
    var date = +echarts.number.parseDate(year + '-01-01');
    var end = +echarts.number.parseDate(+year + 1 + '-01-01');
    var dayTime = 3600 * 24 * 1000;
    var data = [];
    for (var time = date; time < end; time += dayTime) {
        data.push([
            echarts.format.formatTime('yyyy-MM-dd', time),
            Math.floor(Math.random() * 1000)
        ]);
    }
    return data;
}
option4 = {
    tooltip: {},
    calendar: {
        top: 'middle',
        left: 'center',
        orient: 'vertical',
        cellSize: 40,
        yearLabel: {
            margin: 50,
            fontSize: 30
        },
        dayLabel: {
            firstDay: 1,
            nameMap: 'cn'
        },
        monthLabel: {
            nameMap: 'cn',
            margin: 15,
            fontSize: 20,
            color: '#999'
        },
        range: ['2022-10', '2022-11-30']
    },
    visualMap: {
        min: 0,
        max: 1000,
        type: 'piecewise',
        left: 'center',
        bottom: 20,
        inRange: {
            color: ['#5291FF', '#C7DBFF']
        },
        seriesIndex: [1],
        orient: 'horizontal'
    },
    series: [
        {
            type: 'graph',
            edgeSymbol: ['none', 'arrow'],
            coordinateSystem: 'calendar',
            links: links,
            symbolSize: 15,
            calendarIndex: 0,
            itemStyle: {
                color: 'yellow',
                shadowBlur: 9,
                shadowOffsetX: 1.5,
                shadowOffsetY: 3,
                shadowColor: '#555'
            },
            lineStyle: {
                color: '#D10E00',
                width: 1,
                opacity: 1
            },
            data: graphData,
            z: 20
        },
        {
            type: 'heatmap',
            coordinateSystem: 'calendar',
            data: getVirtulData('2022')
        }
    ]
};

option4 && myChart4.setOption(option4);
