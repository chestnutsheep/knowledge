// ==================== Event Data ====================
var EVENTS = [
  // Aug 1
  { day: 1, title: "个贷新规正式施行", cat: "policy", impact: "high",
    desc: "国家金融监督管理总局、央行联合出台《个人贷款业务明示综合融资成本规定》全面施行。工行、农行、中行、建行等国有大行及股份制银行集体公示个人贷款年化综合融资成本上限，终结贷款市场低息引流、隐性收费、息费模糊乱象。",
    sectors: ["银行", "消费金融", "个人信贷"] },
  { day: 1, title: "储能运营管理新规实施", cat: "policy", impact: "medium",
    desc: "新型储能运营管理新规正式实施，利好储能头部企业；可再生能源强制消纳政策同步落地，绿氢赛道迎来政策支撑。",
    sectors: ["储能", "新能源", "绿氢"] },
  { day: 1, title: "MLCC大厂涨价30%", cat: "industry", impact: "medium",
    desc: "三星电机启动MLCC涨价30%，被动元件涨价周期确认。产业链上游材料供应商及国内被动元件厂商有望受益。",
    sectors: ["被动元件", "MLCC", "电子材料"] },
  { day: 1, title: "进口铜50%关税生效", cat: "macro", impact: "high",
    desc: "进口铜50%关税正式生效，直接利好国内铜资源企业。紫金矿业、江西铜业、铜陵有色等铜资源标的受益。",
    sectors: ["有色金属", "铜", "资源"] },
  { day: 1, title: "全国输配电价新政落地", cat: "policy", impact: "medium",
    desc: "全国输配电价新政正式落地，影响电网设备产业链。国电南瑞、思源电气、中国西电等电网设备企业关注度高。",
    sectors: ["电力设备", "电网", "输配电"] },
  { day: 1, title: "香港稳定币牌照申请启动", cat: "policy", impact: "medium",
    desc: "香港稳定币牌照申请正式启动，数字货币、区块链相关概念股受到关注。工业富联、恒生电子、四方精创等标的受益。",
    sectors: ["数字货币", "区块链", "金融科技"] },
  { day: 1, title: "ChinaJoy上海开展", cat: "industry", impact: "low",
    desc: "ChinaJoy上海正式开展，游戏传媒IP经济受关注。游族网络、奥飞娱乐、远望谷等游戏传媒标的受益。",
    sectors: ["游戏", "传媒", "IP经济"] },

  // Aug 3
  { day: 3, title: "浙江荣泰限售解禁", cat: "earnings", impact: "medium",
    desc: "浙江荣泰2.08亿首发限售股上市流通，解禁市值约95.1亿元，为本周最大解禁个股。",
    sectors: ["解禁", "限售股"] },
  { day: 3, title: "OPEC+会议讨论增产", cat: "macro", impact: "high",
    desc: "OPEC+会议讨论增产议题，直接影响国际油价走势。中国石油、中国海油、中国石化等石油板块关注度高。",
    sectors: ["石油", "OPEC+", "能源"] },
  { day: 3, title: "锂电材料涨价", cat: "industry", impact: "medium",
    desc: "湖南裕能上调磷酸铁锂价格2000元/吨，锂电材料产业链涨价信号。",
    sectors: ["锂电池", "磷酸铁锂", "新能源材料"] },

  // Aug 4-5
  { day: 4, title: "AMD/SpaceX发布财报", cat: "earnings", impact: "high",
    desc: "AMD与SpaceX发布财报，海外算力需求风向标。AMD财报数据直接影响全球半导体、AI算力链情绪。",
    sectors: ["半导体", "AI算力", "海外科技"] },
  { day: 4, title: "亚太催化大会", cat: "industry", impact: "low",
    desc: "亚太催化大会召开，循环回收主题。格林美、铜陵有色、楚江新材等催化回收概念关注。",
    sectors: ["催化", "循环回收", "化工"] },

  // Aug 5-7
  { day: 5, title: "西安ICEPT电子封装会议", cat: "industry", impact: "medium",
    desc: "ICEPT电子封装技术国际会议在西安举行，先进封装赛道催化。长电科技、华天科技、通富微电等封装龙头关注度高。",
    sectors: ["先进封装", "半导体", "Chiplet"] },
  { day: 5, title: "印度RBI利率决议", cat: "macro", impact: "medium",
    desc: "印度央行货币政策委员会(MPC)8月3-5日会议，5日公布利率决议。当前回购利率5.25%，市场关注通胀与流动性表态。",
    sectors: ["印度央行", "利率", "新兴市场"] },

  // Aug 6
  { day: 6, title: "大疆扫地机器人新品发布", cat: "tech", impact: "medium",
    desc: "大疆发布扫地机器人新品，机器人板块关注度提升。全志科技等机器人相关芯片供应商受益。",
    sectors: ["机器人", "消费电子", "大疆"] },

  // Aug 9-11
  { day: 9, title: "杭州国际储能大会", cat: "industry", impact: "medium",
    desc: "第十六届中国国际储能大会在杭州举行，储能产业链催化。宁德时代、德业股份、海博思创等储能头部企业关注度高。",
    sectors: ["储能", "新能源", "电池"] },

  // Aug 10
  { day: 10, title: "宇树科技新股申购", cat: "tech", impact: "high",
    desc: "市场定义\"人形机器人第一股\"，宇树科技启动新股申购。直接利好上游减速器、力矩电机、传感器供应商：中大力德、卧龙电驱、绿的谐波等。",
    sectors: ["人形机器人", "减速器", "力矩电机", "传感器"] },
  { day: 10, title: "7月CPI/PPI数据公布", cat: "macro", impact: "high",
    desc: "国家统计局公布7月CPI、PPI经济数据，影响顺周期、消费板块估值。通胀数据直接影响央行后续政策预期。",
    sectors: ["CPI", "PPI", "通胀", "宏观经济"] },

  // Aug 11
  { day: 11, title: "澳洲RBA利率决议", cat: "macro", impact: "medium",
    desc: "澳洲联储8月11日利率决议会议。Q2 CPI数据公布后，市场定价8月降息概率约37%。",
    sectors: ["澳洲央行", "利率", "大宗商品"] },

  // Aug 12
  { day: 12, title: "谷歌Pixel 11发布", cat: "tech", impact: "high",
    desc: "谷歌Pixel 11系列发布，搭载新一代端侧AI芯片。消费电子、存储产业链关注：鸿仕达、佰维存储、则成电子等。",
    sectors: ["消费电子", "AI芯片", "存储", "谷歌"] },
  { day: 12, title: "C919开通国际航线", cat: "industry", impact: "medium",
    desc: "C919开通北京-乌兰巴托首条国际航线，航空零部件产业链催化。中航西飞、宝钛股份、中航高科等受益。",
    sectors: ["航空", "大飞机", "C919"] },

  // Aug 14
  { day: 14, title: "HTC新一代智能眼镜发布", cat: "tech", impact: "medium",
    desc: "HTC推出新一代智能眼镜，VR消费电子板块关注。工业富联、立讯精密、寒武纪等VR/AR概念股受益。",
    sectors: ["VR/AR", "智能眼镜", "消费电子"] },

  // Aug 14-16
  { day: 14, title: "上海具身智能机器人大会", cat: "industry", impact: "medium",
    desc: "上海具身智能机器人产业大会举行，机器人零部件新品集中发布。减速器、3D视觉、力矩电机产业链关注度高。",
    sectors: ["具身智能", "机器人", "零部件"] },

  // Aug 15
  { day: 15, title: "世界人形机器人运动会", cat: "industry", impact: "medium",
    desc: "世界人形机器人运动会举办，机器人产业链持续催化。美的集团、工业富联、海光信息等参与企业关注度高。",
    sectors: ["人形机器人", "AI", "运动控制"] },

  // Aug 19
  { day: 19, title: "美联储FOMC会议纪要", cat: "macro", impact: "high",
    desc: "美联储7月议息会议纪要公布，扰动成长股、贵金属。7月FOMC以9:3维持利率3.50%-3.75%不变，纪要将揭示内部分歧细节，影响降息预期。",
    sectors: ["美联储", "利率", "美元", "贵金属"] },
  { day: 19, title: "2026世界机器人大会", cat: "industry", impact: "high",
    desc: "全年人形机器人最高规格展会在北京举行，300+企业参展，预计超150款机器人新品首发。重点关注灵巧手、谐波减速器、3D视觉、力矩电机产业链。",
    sectors: ["人形机器人", "减速器", "灵巧手", "3D视觉"] },

  // Aug 20
  { day: 20, title: "LPR利率公布", cat: "macro", impact: "high",
    desc: "LPR贷款市场报价利率公布，观察降息预期。若LPR下调，将利好银行、地产、消费等利率敏感板块。",
    sectors: ["LPR", "利率", "银行", "地产"] },

  // Aug 20-21
  { day: 20, title: "南京ICDIA集成电路大会", cat: "industry", impact: "medium",
    desc: "南京ICDIA集成电路设计创新大会举行，Chiplet、先进封装、算力芯片产业链催化。华大九天、广立微、东方算芯等EDA/IP企业关注。",
    sectors: ["半导体", "Chiplet", "EDA", "算力芯片"] },

  // Aug 21
  { day: 21, title: "海南自贸港细则生效", cat: "policy", impact: "medium",
    desc: "海南自贸港相关细则正式生效，海南自贸板块关注。中国中免、海汽集团等海南本地股受益。",
    sectors: ["海南自贸", "免税", "物流"] },

  // Aug 26
  { day: 26, title: "英伟达Q2财报发布", cat: "earnings", impact: "high",
    desc: "英伟达发布二季度财报，全球算力链情绪关键考验。光模块、高速铜箔、金刚石散热、服务器板块联动。寒武纪、中际旭创、新易盛等A股算力标的直接受影响。",
    sectors: ["英伟达", "AI算力", "光模块", "HBM", "服务器"] },
  { day: 26, title: "美国PCE数据公布", cat: "macro", impact: "high",
    desc: "美国7月个人收入与支出(PCE)数据公布，核心PCE为美联储最关注的通胀指标。数据强弱直接影响9月降息预期与美元走势。",
    sectors: ["PCE", "通胀", "美联储", "美元"] },

  // Aug 27-29
  { day: 27, title: "杰克逊霍尔全球央行年会", cat: "macro", impact: "high",
    desc: "本月最大宏观事件。杰克逊霍尔经济政策研讨会8月27-29日举行，主题为\"金融创新：对支付和政策的影响\"。美联储主席Kevin Warsh将于8月28日发表主题演讲，市场紧盯降息节奏信号。偏鹰则成长承压、黄金震荡；偏鸽则科技、贵金属迎来修复。",
    sectors: ["美联储", "全球央行", "美元", "黄金", "北向资金"] },
  { day: 27, title: "绿氢产业大会", cat: "industry", impact: "low",
    desc: "绿氢产业大会召开，新能源板块关注。宁德时代、比亚迪等新能源龙头受益。",
    sectors: ["绿氢", "新能源", "氢能"] },
  { day: 27, title: "东北亚博览会", cat: "industry", impact: "low",
    desc: "东北亚博览会举行，大健康消费板块关注。药明康德、爱尔眼科等医疗健康标的受益。",
    sectors: ["大健康", "消费", "医疗"] },

  // Aug 28
  { day: 28, title: "国际大数据产业博览会", cat: "industry", impact: "medium",
    desc: "国际大数据产业博览会举行，数据要素板块关注。海康威视、立讯精密等大数据相关企业受益。",
    sectors: ["大数据", "数据要素", "数字经济"] },
  { day: 28, title: "亚太生物医药合作峰会", cat: "industry", impact: "medium",
    desc: "亚太生物医药合作峰会举行，创新药板块关注。恒瑞医药、百济神州等创新药龙头受益。",
    sectors: ["创新药", "生物医药", "医药"] },
  { day: 28, title: "钠电池产业论坛", cat: "industry", impact: "medium",
    desc: "钠电池产业论坛举行，电池材料板块关注。格林美、天赐材料等钠电池材料企业受益。",
    sectors: ["钠电池", "电池材料", "新能源"] },

  // Aug 31
  { day: 31, title: "A股半年报披露截止", cat: "earnings", impact: "high",
    desc: "A股2026半年报全部披露收官日。下旬大量业绩承压个股集中\"压哨披露\"，题材进入业绩验真阶段，纯概念容易兑现回落。同时公募基金半年报同步披露。",
    sectors: ["半年报", "业绩", "A股"] },
  { day: 31, title: "无锡CSEAC半导体设备展", cat: "industry", impact: "medium",
    desc: "无锡CSEAC半导体设备材料展举行，半导体设备板块关注。北方华创、中微公司、江丰电子等半导体设备龙头受益。",
    sectors: ["半导体设备", "半导体材料", "国产替代"] },
  { day: 31, title: "上合组织绿色经济会议", cat: "policy", impact: "low",
    desc: "上合组织绿色经济相关会议举行，关注绿色经济、碳中和相关国际合作政策动向。",
    sectors: ["绿色经济", "碳中和", "国际合作"] }
];

// ==================== Category Labels ====================
var CAT_LABELS = {
  macro: "宏观",
  policy: "政策",
  industry: "产业",
  earnings: "财报",
  tech: "科技"
};

var WEEKDAYS = ["日", "一", "二", "三", "四", "五", "六"];

// ==================== State ====================
var activeCats = { macro: true, policy: true, industry: true, earnings: true, tech: true };
var currentView = "calendar";
var ganttChart = null;
var ganttInitialized = false;

// ==================== Init ====================
function init() {
  renderCalendar();
  renderTimeline();
  bindControls();
}

// ==================== Calendar Rendering ====================
function renderCalendar() {
  var grid = document.getElementById("calGrid");
  grid.innerHTML = "";

  // Day name headers
  WEEKDAYS.forEach(function(w) {
    var dn = document.createElement("div");
    dn.className = "cal-day-name";
    dn.textContent = w;
    grid.appendChild(dn);
  });

  // Aug 2026: Aug 1 is a Saturday (index 6)
  var firstDayOffset = 6; // Saturday

  // Empty cells before Aug 1
  for (var i = 0; i < firstDayOffset; i++) {
    var empty = document.createElement("div");
    empty.className = "cal-cell empty";
    grid.appendChild(empty);
  }

  // 31 days
  for (var d = 1; d <= 31; d++) {
    var cell = document.createElement("div");
    cell.className = "cal-cell";
    if (d === 1) cell.classList.add("today"); // Aug 1 is today

    var dayEvents = EVENTS.filter(function(e) { return e.day === d; });
    if (dayEvents.length > 0) cell.classList.add("has-events");

    var dateLabel = document.createElement("div");
    dateLabel.className = "cal-date";
    dateLabel.textContent = d;
    cell.appendChild(dateLabel);

    if (dayEvents.length > 0) {
      var eventsWrap = document.createElement("div");
      eventsWrap.className = "cal-events";

      dayEvents.forEach(function(ev, idx) {
        if (idx >= 3) return; // Max 3 visible
        var tag = document.createElement("div");
        tag.className = "cal-event-tag";
        tag.setAttribute("data-cat", ev.cat);
        tag.textContent = ev.title;
        tag.addEventListener("click", function() { showModal(ev); });
        eventsWrap.appendChild(tag);
      });

      if (dayEvents.length > 3) {
        var more = document.createElement("div");
        more.className = "cal-more";
        more.textContent = "+" + (dayEvents.length - 3) + " 更多";
        more.addEventListener("click", function() {
          // Switch to timeline and scroll to this day
          switchView("timeline");
          var tlDay = document.querySelector('.tl-day[data-day="' + d + '"]');
          if (tlDay) tlDay.scrollIntoView({ behavior: "smooth", block: "center" });
        });
        eventsWrap.appendChild(more);
      }

      cell.appendChild(eventsWrap);
    }

    grid.appendChild(cell);
  }
}

// ==================== Timeline Rendering ====================
function renderTimeline() {
  var container = document.getElementById("tlContainer");
  // Keep the line element
  var line = container.querySelector(".tl-line");
  container.innerHTML = "";
  container.appendChild(line);

  // Group events by day
  var daysSeen = [];
  EVENTS.forEach(function(ev) {
    if (daysSeen.indexOf(ev.day) === -1) daysSeen.push(ev.day);
  });
  daysSeen.sort(function(a, b) { return a - b; });

  daysSeen.forEach(function(d) {
    var dayEvents = EVENTS.filter(function(e) { return e.day === d; });

    var dayWrap = document.createElement("div");
    dayWrap.className = "tl-day";
    dayWrap.setAttribute("data-day", d);

    // Dot (use first event's category color)
    var dot = document.createElement("div");
    dot.className = "tl-dot";
    dot.setAttribute("data-cat", dayEvents[0].cat);
    dayWrap.appendChild(dot);

    // Date label
    var dateLabel = document.createElement("div");
    dateLabel.className = "tl-date-label";
    var wd = new Date(2026, 7, d).getDay();
    dateLabel.innerHTML = "8月" + d + "日 <span class=\"weekday\">周" + WEEKDAYS[wd] + "</span>";
    dayWrap.appendChild(dateLabel);

    // Cards
    var cardsWrap = document.createElement("div");
    cardsWrap.className = "tl-cards";

    dayEvents.forEach(function(ev) {
      var card = document.createElement("div");
      card.className = "tl-card";
      card.setAttribute("data-cat", ev.cat);

      var head = document.createElement("div");
      head.className = "tl-card-head";

      var badge = document.createElement("div");
      badge.className = "tl-cat-badge";
      badge.setAttribute("data-cat", ev.cat);
      badge.textContent = CAT_LABELS[ev.cat];
      head.appendChild(badge);

      var title = document.createElement("div");
      title.className = "tl-card-title";
      title.textContent = ev.title;
      head.appendChild(title);

      var impact = document.createElement("div");
      impact.className = "tl-card-impact " + ev.impact;
      impact.textContent = ev.impact === "high" ? "★★★" : ev.impact === "medium" ? "★★" : "★";
      head.appendChild(impact);

      card.appendChild(head);

      var desc = document.createElement("div");
      desc.className = "tl-card-desc";
      desc.textContent = ev.desc.length > 80 ? ev.desc.substring(0, 80) + "..." : ev.desc;
      card.appendChild(desc);

      card.addEventListener("click", function() { showModal(ev); });
      cardsWrap.appendChild(card);
    });

    dayWrap.appendChild(cardsWrap);
    container.appendChild(dayWrap);
  });
}

// ==================== Filter Logic ====================
function applyFilters() {
  // Calendar tags
  document.querySelectorAll(".cal-event-tag").forEach(function(tag) {
    var cat = tag.getAttribute("data-cat");
    if (activeCats[cat]) {
      tag.classList.remove("hidden");
    } else {
      tag.classList.add("hidden");
    }
  });

  // Timeline cards
  document.querySelectorAll(".tl-card").forEach(function(card) {
    var cat = card.getAttribute("data-cat");
    if (activeCats[cat]) {
      card.classList.remove("hidden");
    } else {
      card.classList.add("hidden");
    }
  });

  // Hide empty days in timeline
  document.querySelectorAll(".tl-day").forEach(function(day) {
    var visibleCards = day.querySelectorAll(".tl-card:not(.hidden)");
    if (visibleCards.length === 0) {
      day.classList.add("hidden");
    } else {
      day.classList.remove("hidden");
    }
  });
}

// ==================== View Switching ====================
function switchView(view) {
  currentView = view;
  document.querySelectorAll(".view-btn").forEach(function(btn) {
    btn.classList.toggle("active", btn.getAttribute("data-view") === view);
  });
  document.getElementById("calendarView").classList.toggle("visible", view === "calendar");
  document.getElementById("timelineView").classList.toggle("visible", view === "timeline");
  document.getElementById("ganttView").classList.toggle("visible", view === "gantt");
  document.getElementById("stockmapView").classList.toggle("visible", view === "stockmap");

  // Lazy-init gantt chart when first viewed
  if (view === "gantt" && !ganttInitialized) {
    ganttInitialized = true;
    // Use setTimeout to ensure the container is visible and has dimensions
    setTimeout(function() { renderGantt(); }, 100);
  }
  // Resize chart if already initialized
  if (view === "gantt" && ganttChart) {
    setTimeout(function() { ganttChart.resize(); }, 100);
  }
}

// ==================== Stock Map Expandable Cards ====================
function toggleECard(headEl) {
  var card = headEl.parentElement;
  card.classList.toggle("expanded");
}

// ==================== Modal ====================
function showModal(ev) {
  var overlay = document.getElementById("modalOverlay");

  var badge = document.getElementById("modalCatBadge");
  badge.innerHTML = "";
  var b = document.createElement("div");
  b.className = "tl-cat-badge";
  b.setAttribute("data-cat", ev.cat);
  b.textContent = CAT_LABELS[ev.cat];
  b.style.fontSize = "0.7rem";
  b.style.padding = "3px 10px";
  badge.appendChild(b);

  var wd = new Date(2026, 7, ev.day).getDay();
  document.getElementById("modalTitle").textContent = ev.title;
  document.getElementById("modalDate").textContent = "2026年8月" + ev.day + "日 · 周" + WEEKDAYS[wd] + " · 影响等级: " + (ev.impact === "high" ? "高" : ev.impact === "medium" ? "中" : "低");
  document.getElementById("modalDesc").textContent = ev.desc;

  var sectorsEl = document.getElementById("modalSectors");
  sectorsEl.innerHTML = "";
  ev.sectors.forEach(function(s) {
    var chip = document.createElement("div");
    chip.className = "modal-sector";
    chip.textContent = s;
    sectorsEl.appendChild(chip);
  });

  overlay.classList.add("show");
}

function closeModal() {
  document.getElementById("modalOverlay").classList.remove("show");
}

// ==================== Bind Controls ====================
function bindControls() {
  // View toggle
  document.querySelectorAll(".view-btn").forEach(function(btn) {
    btn.addEventListener("click", function() {
      switchView(btn.getAttribute("data-view"));
    });
  });

  // Category filters
  document.querySelectorAll(".filter-chip").forEach(function(chip) {
    chip.addEventListener("click", function() {
      var cat = chip.getAttribute("data-cat");
      activeCats[cat] = !activeCats[cat];
      chip.classList.toggle("active", activeCats[cat]);
      applyFilters();
    });
  });

  // Modal close
  document.getElementById("modalClose").addEventListener("click", closeModal);
  document.getElementById("modalOverlay").addEventListener("click", function(e) {
    if (e.target === this) closeModal();
  });

  // ESC to close modal
  document.addEventListener("keydown", function(e) {
    if (e.key === "Escape") closeModal();
  });
}

// ==================== Gantt Chart Rendering ====================
function renderGantt() {
  var dom = document.getElementById("ganttChart");
  if (!dom || typeof echarts === "undefined") return;

  ganttChart = echarts.init(dom, null, { renderer: "canvas" });

  // --- Color helpers ---
  var C = {
    rhythm: "#00e5ff",
    policy: "#ff2d92",
    rotation: "#00ff9d",
    mainline: "#ff9500",
    event: "#b14dff",
    position: "#ffd700",
    muted: "#7878a0",
    ink: "#d8d8f0",
    rule: "rgba(120,120,180,0.15)"
  };

  function catColor(cat) {
    var map = { rhythm: C.rhythm, policy: C.policy, rotation: C.rotation, mainline: C.mainline, event: C.event, position: C.position };
    return map[cat] || C.muted;
  }

  function catRgba(cat, a) {
    var h = catColor(cat);
    var r = parseInt(h.slice(1,3),16), g = parseInt(h.slice(3,5),16), b = parseInt(h.slice(5,7),16);
    return "rgba(" + r + "," + g + "," + b + "," + a + ")";
  }

  // --- Gantt data: [startDay, endDay, label, sublabel, cat] ---
  // Groups with their items
  var groups = [
    {
      name: "大盘节奏", cat: "rhythm",
      items: [
        { s: 1, e: 31, label: "反弹窗口期", sub: "全年最佳分批建仓窗口" },
        { s: 1, e: 10, label: "震荡分化筑底", sub: "ETF净流入创新高" },
        { s: 10, e: 17, label: "数据验证+结构行情", sub: "CPI/PPI+经济数据" },
        { s: 18, e: 24, label: "产业催化爆发", sub: "三会齐发·AI+机器人+芯片" },
        { s: 25, e: 31, label: "中报避雷防御", sub: "压哨披露·闷雷风险" }
      ]
    },
    {
      name: "政策驱动(7·30政治局会议)", cat: "policy",
      items: [
        { s: 1, e: 31, label: "AI基础设施(人工智能+)", sub: "光模块·AI服务器·算力链" },
        { s: 1, e: 31, label: "反内卷利润修复", sub: "光伏·钢铁·化工" },
        { s: 1, e: 31, label: "资本市场改革信心", sub: "LPR(8/20)+MLF(8/25)" }
      ]
    },
    {
      name: "景气长牛赛道轮动", cat: "rotation",
      items: [
        { s: 1, e: 10, label: "电力·创新药·先进封装", sub: "反内卷+健康中国+AI算力" },
        { s: 10, e: 20, label: "消费电子·存储芯片", sub: "MLCC涨价+新品备货" },
        { s: 20, e: 31, label: "创新药·储能·消费", sub: "CXO业绩+储能新规+暑运" }
      ]
    },
    {
      name: "机构四大主线", cat: "mainline",
      items: [
        { s: 1, e: 31, label: "AI算力+半导体国产替代", sub: "催化峰值 8/18-20" },
        { s: 10, e: 25, label: "人形机器人+低空经济", sub: "催化峰值 8/19" },
        { s: 1, e: 20, label: "涨价周期链", sub: "MLCC涨价30%·锂电·稀土" },
        { s: 1, e: 31, label: "贵金属+高股息+创新药", sub: "催化峰值 8/25杰克逊霍尔" }
      ]
    },
    {
      name: "关键事件窗口", cat: "event",
      items: [
        { s: 1, e: 31, label: "中报披露窗口", sub: "高峰 8/25-31 避雷关键期" },
        { s: 9, e: 17, label: "经济数据密集期", sub: "CPI/PPI+国民经济数据" },
        { s: 18, e: 20, label: "产业大会催化期", sub: "AI+机器人+芯片三会" },
        { s: 25, e: 29, label: "杰克逊霍尔年会", sub: "美联储降息预期博弈" }
      ]
    },
    {
      name: "仓位建议", cat: "position",
      items: [
        { s: 1, e: 10, label: "逢低布局期", sub: "仓位6-7成" },
        { s: 10, e: 20, label: "持仓观察期", sub: "仓位7-8成·催化期加仓" },
        { s: 25, e: 31, label: "防御减仓期", sub: "仓位5-6成·提高现金" }
      ]
    }
  ];

  // --- Build y-axis categories (reversed for top-down order) ---
  var yCats = [];
  var groupRanges = []; // {start, end, name, cat} for each group's y-index range
  groups.forEach(function(g) {
    var startIdx = yCats.length;
    g.items.forEach(function(item) {
      yCats.push(item.label);
    });
    var endIdx = yCats.length - 1;
    groupRanges.push({ start: startIdx, end: endIdx, name: g.name, cat: g.cat });
  });
  yCats.reverse(); // ECharts y-axis goes bottom-up, we want top-down
  // Recalculate group ranges after reversal
  var totalItems = yCats.length;
  groupRanges.forEach(function(gr) {
    gr.start = totalItems - 1 - gr.end;
    gr.end = totalItems - 1 - gr.start;
    var tmp = gr.start;
    gr.start = gr.end;
    gr.end = tmp;
  });

  // --- Build series data ---
  // For each item, we create a "spacer" (transparent) bar from 0 to start,
  // and a "bar" (colored) from start to end.
  var spacerData = [];
  var barData = [];

  groups.forEach(function(g, gi) {
    g.items.forEach(function(item, ii) {
      // Calculate the y-index after reversal
      var originalIdx = 0;
      for (var i = 0; i < gi; i++) {
        originalIdx += groups[i].items.length;
      }
      originalIdx += ii;
      var yIdx = totalItems - 1 - originalIdx;

      // Spacer (transparent, from day 0 to start)
      spacerData.push({
        value: [item.s, yIdx],
        itemStyle: { color: "transparent" }
      });

      // Actual bar (from start to end)
      var duration = item.e - item.s;
      barData.push({
        value: [duration, yIdx],
        name: item.label,
        cat: g.cat,
        sub: item.sub,
        startDay: item.s,
        endDay: item.e,
        itemStyle: {
          color: catRgba(g.cat, 0.65),
          borderColor: catColor(g.cat),
          borderWidth: 1,
          borderRadius: 4,
          shadowBlur: 8,
          shadowColor: catRgba(g.cat, 0.3)
        },
        label: {
          show: true,
          position: "insideRight",
          formatter: item.sub ? item.sub : "",
          color: "#fff",
          fontSize: 9,
          fontFamily: "GeistMono, monospace",
          textShadow: "0 0 4px rgba(0,0,0,0.8)"
        }
      });
    });
  });

  // --- X-axis day labels ---
  var xDays = [];
  for (var d = 1; d <= 31; d++) {
    xDays.push(d);
  }

  // --- Mark lines for key dates ---
  var markLineData = [
    { xAxis: 9, name: "CPI/PPI" },
    { xAxis: 17, name: "经济数据" },
    { xAxis: 18, name: "AI大会" },
    { xAxis: 19, name: "机器人" },
    { xAxis: 20, name: "芯片+LPR" },
    { xAxis: 25, name: "杰克逊霍尔" },
    { xAxis: 31, name: "中报截止" }
  ];

  // --- Weekend mark areas ---
  // Aug 2026: Aug 1=Fri, so Sat=2, Sun=3, Sat=9, Sun=10, etc.
  var weekendAreas = [];
  var aug1Wd = 5; // 0=Sun..5=Fri, 6=Sat. Aug 1 is Friday (5)
  for (var day = 1; day <= 31; day++) {
    var wd = (aug1Wd + day - 1) % 7;
    if (wd === 6 || wd === 0) {
      // Saturday or Sunday
      weekendAreas.push([{ xAxis: day - 0.5 }, { xAxis: day + 0.5 }]);
    }
  }

  var option = {
    backgroundColor: "transparent",
    title: {
      text: "2026年8月A股波段操作甘特图",
      subtext: "横轴=日期 · 纵轴=波段条目 · 整合机构研报+景气长牛赛道+政治局会议政策",
      left: "center",
      top: 5,
      textStyle: { color: C.ink, fontSize: 15, fontWeight: 700, fontFamily: "GeistMono, monospace" },
      subtextStyle: { color: C.muted, fontSize: 10 }
    },
    tooltip: {
      trigger: "item",
      backgroundColor: "rgba(6,6,20,0.95)",
      borderColor: "rgba(0,229,255,0.3)",
      borderWidth: 1,
      textStyle: { color: C.ink, fontSize: 12 },
      formatter: function(params) {
        var d = params.data;
        if (!d || !d.cat) return "";
        var dayRange = d.startDay === d.endDay
          ? "8月" + d.startDay + "日"
          : "8月" + d.startDay + "日 - " + d.endDay + "日";
        var cc = catColor(d.cat);
        return '<div style="font-weight:700;color:' + cc + ';margin-bottom:4px;">' + d.name + "</div>" +
               '<div style="color:' + C.muted + ';font-size:11px;margin-bottom:4px;">' + dayRange + "</div>" +
               (d.sub ? '<div style="color:' + C.ink + ';font-size:12px;">' + d.sub + "</div>" : "");
      }
    },
    grid: {
      left: 180,
      right: 40,
      top: 55,
      bottom: 50
    },
    xAxis: {
      type: "value",
      min: 0,
      max: 32,
      interval: 1,
      axisLabel: {
        color: C.muted,
        fontSize: 10,
        fontFamily: "GeistMono, monospace",
        formatter: function(val) {
          if (val >= 1 && val <= 31) return Math.floor(val);
          return "";
        }
      },
      axisLine: { lineStyle: { color: C.rule } },
      splitLine: { show: true, lineStyle: { color: C.rule, type: "dashed" } },
      axisTick: { show: false }
    },
    yAxis: {
      type: "category",
      data: yCats,
      axisLabel: {
        color: C.ink,
        fontSize: 10,
        fontFamily: "Outfit, sans-serif",
        fontWeight: 600,
        formatter: function(val) {
          return val.length > 14 ? val.substring(0, 13) + "\u2026" : val;
        }
      },
      axisLine: { lineStyle: { color: C.rule } },
      axisTick: { show: false },
      splitLine: { show: true, lineStyle: { color: C.rule, type: "dashed" } }
    },
    series: [
      {
        name: "spacer",
        type: "bar",
        stack: "gantt",
        barWidth: 18,
        silent: true,
        data: spacerData,
        animation: false,
        markArea: {
          silent: true,
          itemStyle: { color: "rgba(120,120,180,0.04)" },
          data: weekendAreas.length > 0 ? weekendAreas : []
        },
        markLine: {
          symbol: ["none", "none"],
          lineStyle: { color: "rgba(177,77,255,0.25)", type: "dashed", width: 1 },
          label: {
            color: C.event,
            fontSize: 9,
            fontFamily: "GeistMono, monospace",
            position: "insideEndTop"
          },
          data: markLineData.map(function(ml) {
            return { xAxis: ml.xAxis, label: { formatter: ml.name } };
          })
        }
      },
      {
        name: "bar",
        type: "bar",
        stack: "gantt",
        barWidth: 18,
        data: barData,
        animation: true,
        animationDuration: 800,
        animationDelay: function(idx) { return idx * 50; },
        emphasis: {
          itemStyle: {
            color: function(params) {
              var d = params.data;
              return d.cat ? catRgba(d.cat, 0.9) : "transparent";
            },
            shadowBlur: 15
          }
        }
      }
    ]
  };

  // --- Add group background bands via graphic ---
  var graphicElements = [];
  groupRanges.forEach(function(gr) {
    graphicElements.push({
      type: "text",
      left: 12,
      top: 0, // will be approximated
      z: 100,
      style: {
        text: gr.name,
        fill: catRgba(gr.cat, 0.7),
        fontSize: 10,
        fontWeight: 700,
        fontFamily: "GeistMono, monospace"
      }
    });
  });

  option.graphic = graphicElements;

  ganttChart.setOption(option);

  // Resize on window resize
  window.addEventListener("resize", function() {
    if (ganttChart) ganttChart.resize();
  });
}

// ==================== Boot ====================
init();
