(function() {
  var style = getComputedStyle(document.documentElement);
  var accent = style.getPropertyValue('--accent').trim();
  var accent2 = style.getPropertyValue('--accent2').trim();
  var ink = style.getPropertyValue('--ink').trim();
  var muted = style.getPropertyValue('--muted').trim();
  var rule = style.getPropertyValue('--rule').trim();
  var bg2 = style.getPropertyValue('--bg2').trim();
  var green = style.getPropertyValue('--green').trim();
  var red = style.getPropertyValue('--red').trim();
  var orange = style.getPropertyValue('--orange').trim();

  // --- Chart 1: Overall Accuracy Comparison ---
  var chart1 = echarts.init(document.getElementById('chart-overall'), null, { renderer: 'svg' });
  chart1.setOption({
    animation: false,
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      appendToBody: true,
      formatter: function(params) {
        var p = params[0];
        return p.name + '<br/>准确率: <b>' + p.value + '%</b>';
      }
    },
    grid: { left: '30%', right: '12%', top: 30, bottom: 30 },
    xAxis: {
      type: 'value',
      max: 100,
      axisLabel: { color: muted, formatter: '{value}%' },
      splitLine: { lineStyle: { color: rule, type: 'dashed' } },
      axisLine: { lineStyle: { color: rule } }
    },
    yAxis: {
      type: 'category',
      data: ['高盛(A股)', '摩根士丹利(A股)', '摩根大通(A股)', '中信证券(估)', 'A股券商整体', '国信证券', '中金公司', '长城证券', '兴业证券', '国泰君安', '银河证券'],
      axisLabel: { color: ink, fontSize: 11 },
      axisLine: { lineStyle: { color: rule } },
      axisTick: { show: false }
    },
    series: [{
      type: 'bar',
      data: [
        { value: 37, itemStyle: { color: red } },
        { value: 42, itemStyle: { color: red + 'cc' } },
        { value: 50, itemStyle: { color: orange } },
        { value: 42, itemStyle: { color: red + 'aa' } },
        { value: 43, itemStyle: { color: red + '99' } },
        { value: 51, itemStyle: { color: accent2 + 'cc' } },
        { value: 51, itemStyle: { color: accent2 + 'cc' } },
        { value: 64, itemStyle: { color: accent + 'cc' } },
        { value: 64, itemStyle: { color: accent + 'cc' } },
        { value: 75, itemStyle: { color: green + 'cc' } },
        { value: 75, itemStyle: { color: green } }
      ],
      barWidth: '55%',
      label: { show: true, position: 'right', color: muted, fontSize: 11, formatter: '{c}%' },
      markLine: {
        silent: true,
        symbol: 'none',
        data: [{
          xAxis: 50,
          lineStyle: { color: accent, type: 'dashed', width: 2 },
          label: { formatter: '50% 随机基准', color: accent, fontSize: 10, position: 'insideEndTop' }
        }]
      }
    }]
  });
  window.addEventListener('resize', function() { chart1.resize(); });

  // --- Chart 2: Rating Accuracy ---
  var chart2 = echarts.init(document.getElementById('chart-ratings'), null, { renderer: 'svg' });
  chart2.setOption({
    animation: false,
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      appendToBody: true
    },
    grid: { left: '15%', right: '10%', top: 30, bottom: 30 },
    xAxis: {
      type: 'value',
      max: 100,
      axisLabel: { color: muted, formatter: '{value}%' },
      splitLine: { lineStyle: { color: rule, type: 'dashed' } },
      axisLine: { lineStyle: { color: rule } }
    },
    yAxis: {
      type: 'category',
      data: ['"买入"评级', '"中性"评级', '"卖出"评级', '"增持"评级'],
      axisLabel: { color: ink, fontSize: 12 },
      axisLine: { lineStyle: { color: rule } },
      axisTick: { show: false }
    },
    series: [{
      type: 'bar',
      data: [
        { value: 1.39, itemStyle: { color: red } },
        { value: 10.04, itemStyle: { color: red + '99' } },
        { value: 70.83, itemStyle: { color: green + 'cc' } },
        { value: 84.56, itemStyle: { color: green } }
      ],
      barWidth: '50%',
      label: { show: true, position: 'right', color: ink, fontSize: 12, formatter: '{c}%' }
    }]
  });
  window.addEventListener('resize', function() { chart2.resize(); });

  // --- Chart 3: Domestic Broker Ranking ---
  var chart3 = echarts.init(document.getElementById('chart-domestic'), null, { renderer: 'svg' });
  chart3.setOption({
    animation: false,
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      appendToBody: true
    },
    grid: { left: '25%', right: '12%', top: 30, bottom: 30 },
    xAxis: {
      type: 'value',
      max: 100,
      axisLabel: { color: muted, formatter: '{value}%' },
      splitLine: { lineStyle: { color: rule, type: 'dashed' } },
      axisLine: { lineStyle: { color: rule } }
    },
    yAxis: {
      type: 'category',
      data: ['A股券商整体', '中信证券(估)', '申银万国', '国信证券', '中金公司', '长城证券', '兴业证券', '国泰君安', '银河证券', '东莞证券'],
      axisLabel: { color: ink, fontSize: 11 },
      axisLine: { lineStyle: { color: rule } },
      axisTick: { show: false }
    },
    series: [{
      type: 'bar',
      data: [
        { value: 43, itemStyle: { color: red + '99' } },
        { value: 42, itemStyle: { color: red + 'aa' } },
        { value: 51, itemStyle: { color: accent2 + 'cc' } },
        { value: 51, itemStyle: { color: accent2 + 'cc' } },
        { value: 51, itemStyle: { color: accent2 + 'cc' } },
        { value: 64, itemStyle: { color: accent + 'cc' } },
        { value: 64, itemStyle: { color: accent + 'cc' } },
        { value: 75, itemStyle: { color: green + 'cc' } },
        { value: 75, itemStyle: { color: green + 'cc' } },
        { value: 79, itemStyle: { color: green } }
      ],
      barWidth: '55%',
      label: { show: true, position: 'right', color: muted, fontSize: 11, formatter: '{c}%' },
      markLine: {
        silent: true,
        symbol: 'none',
        data: [{
          xAxis: 43,
          lineStyle: { color: orange, type: 'dashed', width: 2 },
          label: { formatter: '行业平均43%', color: orange, fontSize: 10, position: 'insideEndTop' }
        }]
      }
    }]
  });
  window.addEventListener('resize', function() { chart3.resize(); });

  // --- Chart 4: Analyst Win Rate Distribution ---
  var chart4 = echarts.init(document.getElementById('chart-analyst'), null, { renderer: 'svg' });
  chart4.setOption({
    animation: false,
    tooltip: {
      trigger: 'item',
      appendToBody: true,
      formatter: '{b}<br/>占比: <b>{c}%</b>'
    },
    legend: { show: false },
    grid: { left: '15%', right: '10%', top: 30, bottom: 30 },
    xAxis: {
      type: 'value',
      max: 70,
      axisLabel: { color: muted, formatter: '{value}%' },
      splitLine: { lineStyle: { color: rule, type: 'dashed' } },
      axisLine: { lineStyle: { color: rule } }
    },
    yAxis: {
      type: 'category',
      data: ['70%-80%', '80%以上', '50%-70%', '50%以下'],
      axisLabel: { color: ink, fontSize: 12 },
      axisLine: { lineStyle: { color: rule } },
      axisTick: { show: false }
    },
    series: [{
      type: 'bar',
      data: [
        { value: 6, itemStyle: { color: accent + '99' } },
        { value: 15, itemStyle: { color: green + 'cc' } },
        { value: 16, itemStyle: { color: accent2 + '99' } },
        { value: 63, itemStyle: { color: red } }
      ],
      barWidth: '50%',
      label: { show: true, position: 'right', color: ink, fontSize: 12, formatter: '{c}%' }
    }]
  });
  window.addEventListener('resize', function() { chart4.resize(); });
})();
