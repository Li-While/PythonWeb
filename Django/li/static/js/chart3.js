var chartDom3 = document.getElementById('chart3');
var myChart3 = echarts.init(chartDom3);
var option3;

myChart3.showLoading();
// $.getJSON('les-miserables.json', function (graph) {
// var graph = {{ graph| safe}}
myChart3.hideLoading();
option3 = {
    tooltip: {},
    legend: [
        {
            data: graph.categories.map(function (a) {
                return a.name;
            })
        }
    ],
    series: [
        {
            name: 'Les Miserables',
            type: 'graph',
            layout: 'none',
            data: graph.nodes,
            links: graph.links,
            categories: graph.categories,
            roam: true,
            label: {
                show: true,
                position: 'right',
                formatter: '{b}'
            },
            labelLayout: {
                hideOverlap: true
            },
            scaleLimit: {
                min: 0.4,
                max: 2
            },
            lineStyle: {
                color: 'source',
                curveness: 0.3
            }
        }
    ]
};
myChart3.setOption(option3);
// });

option3 && myChart3.setOption(option3);

