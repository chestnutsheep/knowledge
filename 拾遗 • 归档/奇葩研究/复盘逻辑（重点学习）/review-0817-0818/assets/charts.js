(function() {
  var ink = '#E0DBD2';
  var muted = '#A8A0B8';
  var dim = '#7a7490';
  var bg2 = '#1c1828';
  var bg3 = '#241f33';
  var rule = 'rgba(168,160,184,0.12)';
  var red = '#E07B7B';
  var green = '#7BBA7B';
  var accent = '#D0B468';
  var warn = '#D8A060';
  var accent3 = '#B0A4C8';

  // Chart 1: Volume-Price Cycle
  var chart1 = echarts.init(document.getElementById('chart-vp'));
  var dates = ['8/10', '8/11', '8/12', '8/13', '8/14', '8/17'];
  var shIdx = [3938, 3926, 3946, 3927, 3927, 3983];
  var volume = [2.47, 2.32, 2.15, 2.55, 2.14, 2.40];
  var pctChange = [0.78, -0.31, 0.32, -0.50, 0.01, 1.41];

  chart1.setOption({
    backgroundColor: 'transparent',
    grid: { left: 60, right: 70, top: 70, bottom: 50 },
    legend: {
      data: ['上证指数', '成交额(万亿)', '涨跌幅(%)'],
      top: 10, textStyle: { color: muted, fontSize: 11 },
      itemWidth: 12, itemHeight: 8, itemGap: 15
    },
    xAxis: {
      type: 'category', data: dates,
      axisLabel: { color: dim, fontSize: 12 },
      axisLine: { lineStyle: { color: rule } }, axisTick: { show: false }
    },
    yAxis: [
      { type: 'value', name: '指数', position: 'left', scale: true, min: 3900, max: 4000,
        nameTextStyle: { color: muted, fontSize: 10 }, axisLabel: { color: dim, fontSize: 10 },
        axisLine: { show: false }, splitLine: { lineStyle: { color: rule } } },
      { type: 'value', name: '万亿', position: 'right', min: 1.8, max: 2.8,
        nameTextStyle: { color: muted, fontSize: 10 }, axisLabel: { color: dim, fontSize: 10 },
        axisLine: { show: false }, splitLine: { show: false } },
      { type: 'value', name: '%', position: 'right', offset: 40, min: -1, max: 2,
        nameTextStyle: { color: muted, fontSize: 10 }, axisLabel: { color: dim, fontSize: 10 },
        axisLine: { show: false }, splitLine: { show: false } }
    ],
    tooltip: {
      trigger: 'axis', backgroundColor: bg3, borderColor: rule,
      textStyle: { color: ink, fontSize: 12 },
      formatter: function(params) {
        var idx = params[0].dataIndex;
        var status = ['量价同步', '缩量调整', '⚠顶背离', '天量出清(4跌停)', '缩量真空', '放量暴涨'];
        return '<b style="color:' + ink + '">' + dates[idx] + '</b><br/>' +
          '上证: ' + shIdx[idx] + ' (' + (pctChange[idx] > 0 ? '+' : '') + pctChange[idx] + '%)<br/>' +
          '成交额: ' + volume[idx] + '万亿<br/>' +
          '<span style="color:' + accent + '">' + (status[idx] || '') + '</span>';
      }
    },
    series: [
      { name: '上证指数', type: 'line', yAxisIndex: 0, data: shIdx, smooth: true,
        symbol: 'circle', symbolSize: 8,
        lineStyle: { color: accent, width: 2.5 },
        itemStyle: { color: function(p) {
          var i = p.dataIndex;
          if (i === 2) return warn; if (i === 3) return red; if (i === 4) return warn; if (i === 5) return green;
          return accent;
        }},
        areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [
          { offset: 0, color: 'rgba(208,180,104,0.12)' }, { offset: 1, color: 'rgba(208,180,104,0)' }
        ]}}
      },
      { name: '成交额(万亿)', type: 'bar', yAxisIndex: 1, barWidth: 28,
        data: volume.map(function(v, i) {
          var c = i === 2 ? warn : (i === 3 ? red : (i === 4 ? warn : (i === 5 ? green : 'rgba(208,180,104,0.4)')));
          return { value: v, itemStyle: { color: c, opacity: 0.5, borderRadius: [4, 4, 0, 0] } };
        })
      },
      { name: '涨跌幅(%)', type: 'line', yAxisIndex: 2, data: pctChange,
        symbol: 'diamond', symbolSize: 6,
        lineStyle: { color: green, width: 1.5, type: 'dashed' },
        itemStyle: { color: function(p) { return p.value >= 0 ? green : red; } }
      }
    ],
    graphic: [
      { type: 'text', left: '33%', top: '20%', style: { text: '顶背离', fill: warn, fontSize: 11, fontWeight: 600 } },
      { type: 'text', left: '50%', top: '12%', style: { text: '出清', fill: red, fontSize: 11, fontWeight: 600 } },
      { type: 'text', left: '67%', top: '25%', style: { text: '真空', fill: warn, fontSize: 11, fontWeight: 600 } },
      { type: 'text', left: '82%', top: '8%', style: { text: '暴涨', fill: green, fontSize: 11, fontWeight: 600 } }
    ]
  });

  // Chart 2: Sector Fund Flow
  var chart2 = echarts.init(document.getElementById('chart-flow'));
  var sectors = ['电子', '通信', '电力设备', '有色金属', '医药生物', '机械设备', '计算机', '食品饮料', '传媒', '房地产'];
  var flows = [549, 64.8, 134, 73, 50, 92, -21.45, -11.8, -10.91, -1.5];

  chart2.setOption({
    backgroundColor: 'transparent',
    grid: { left: 80, right: 80, top: 30, bottom: 40 },
    xAxis: {
      type: 'value', axisLabel: { color: dim, fontSize: 10, formatter: '{value}亿' },
      axisLine: { show: false }, splitLine: { lineStyle: { color: rule } }
    },
    yAxis: {
      type: 'category', data: sectors.reverse(),
      axisLabel: { color: muted, fontSize: 12 },
      axisLine: { show: false }, axisTick: { show: false }
    },
    tooltip: {
      trigger: 'axis', backgroundColor: bg3, borderColor: rule,
      textStyle: { color: ink, fontSize: 12 },
      formatter: function(p) { return p[0].name + ': ' + (p[0].value > 0 ? '+' : '') + p[0].value + '亿'; }
    },
    series: [{
      type: 'bar', barWidth: 18,
      data: flows.reverse().map(function(v) {
        return { value: v, itemStyle: { color: v >= 0 ? green : red, opacity: 0.7, borderRadius: v >= 0 ? [0, 4, 4, 0] : [4, 0, 0, 4] } };
      }),
      label: { show: true, position: function(p) { return p.value >= 0 ? 'right' : 'left'; },
        formatter: function(p) { return (p.value > 0 ? '+' : '') + p.value + '亿'; },
        color: ink, fontSize: 11 }
    }]
  });

  window.addEventListener('resize', function() { chart1.resize(); chart2.resize(); });
})();
