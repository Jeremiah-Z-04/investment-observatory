var T = {
  'nav.home': {zh:'四因子看板',en:'Dashboard'},
  'nav.review': {zh:'复盘工具',en:'Review'},
  'nav.volume': {zh:'量能监测',en:'Volume'},
  'nav.industry': {zh:'产业逻辑',en:'Industry'},
  'app.title': {zh:'投资观察站',en:'Investment Observatory'},
  'app.subtitle': {zh:'数据驱动 · 实战导向',en:'Data-Driven · Action-Oriented'},
  'status.online': {zh:'实时在线',en:'Online'},
  'status.offline': {zh:'离线模式',en:'Offline'},
  'btn.lang': {zh:'EN',en:'中文'},
  'btn.refresh': {zh:'刷新数据',en:'Refresh'},
  'home.rank_col': {zh:'排名',en:'Rank'},
  'home.thread_col': {zh:'主线',en:'Thread'},
  'home.stage_col': {zh:'阶段',en:'Stage'},
  'home.score_col': {zh:'评分',en:'Score'},
  'home.driver_col': {zh:'核心驱动',en:'Driver'},
  'home.dur_col': {zh:'预期持续时间',en:'Duration'},
  'home.action_col': {zh:'操作建议',en:'Action'},
  'home.northbound': {zh:'北向资金(亿)',en:'Northbound(100M)'},
  'comp.name': {zh:'名称',en:'Name'},
  'comp.code': {zh:'代码',en:'Code'},
  'comp.change': {zh:'涨跌',en:'Change'},
  'comp.sector': {zh:'板块',en:'Sector'},
  'comp.mcap': {zh:'市值(亿)',en:'Mkt Cap(100M)'},
  'comp.search': {zh:'按名称或代码搜索...',en:'Search by name or code...'},
  'comp.note': {zh:'数据需要点击刷新加载',en:'Data loads on refresh.'},
  'close': {zh:'关闭',en:'Close'},
};

var S = {
  page: "home", online: false, lastTs: "--", charts: {},
  lang: localStorage.getItem("inv_lang") || "zh", server: "",
  reviewTimer: null, volumeTimer: null, volumeData: [], pollTimer: null, homeData: null, mode: "trend",
  reviewStocks: [], _factorDetails: {},

  t: function(k) {
    var e = T[k]; return e ? (e[S.lang] || e.en || k) : k;
  },
  toggleLang: function() {
    S.lang = S.lang === "zh" ? "en" : "zh";
    localStorage.setItem("inv_lang", S.lang);
    var b = document.getElementById("langBtn");
    if (b) b.textContent = S.lang === "zh" ? "EN" : "\u4e2d\u6587";
    S.nav(S.page);
  },

  init: function() {
    var self = this;
    S.server = window.location.protocol + "//" + window.location.host;
    var lb = document.getElementById("langBtn");
    if (lb) lb.textContent = S.lang === "zh" ? "EN" : "\u4e2d\u6587";
    document.querySelectorAll(".nav-item").forEach(function(el) {
      el.addEventListener("click", function() { self.nav(el.dataset.page); });
    });
    S.nav("home");
    fetch(S.server + "/api/ping").then(function(r){return r.json();}).then(function(d){
      if (d.status === "ok") {
        S.online = true; S.setStatus("\u5728\u7ebf", "#00d4aa"); S.lastTs = d.time;
        var ts = document.getElementById("ts");
        if (ts) ts.textContent = d.time;
        S.refresh();
      }
    }).catch(function(){ S.setStatus("\u79bb\u7ebf", "#ff4d6a"); S.refresh(); });
    setInterval(function(){
      fetch(S.server + "/api/ping").then(function(r){return r.json();}).then(function(d){
        if (d.status === "ok") {
          S.online = true; S.setStatus("\u5728\u7ebf", "#00d4aa");
          var ts = document.getElementById("ts");
          if (ts) ts.textContent = d.time;
        }
      }).catch(function(){ S.online = false; S.setStatus("\u79bb\u7ebf", "#ff4d6a"); });
    }, 30000);
  },

  setStatus: function(txt, clr) {
    var st = document.getElementById("st");
    if (st) { st.textContent = "\u25cf " + txt; st.style.color = clr || "#5a6599"; }
  },

  nav: function(p) {
    S.page = p;
    document.querySelectorAll(".nav-item").forEach(function(n){ n.classList.remove("active"); });
    var el = document.querySelector('.nav-item[data-page="' + p + '"]');
    if (el) el.classList.add("active");
    var fn = S["R_" + p];
    if (fn) {
      document.getElementById("main").innerHTML = fn();
      S.afterRender(p);
    }
  },

  afterRender: function(p) {
    S.stopPolling();
    S.stopReviewPolling();
    if (p === "home") {
      setTimeout(function(){ S.renderSentimentTrend(); }, 300);
      S.startPolling();
    } else if (p === "industry") {
      setTimeout(function(){ S.renderIndustryChain(); }, 300);
    } else if (p === "review") {
    } else if (p === "volume") {
      setTimeout(function(){ S.startReviewPolling(); }, 300);
    } else if (p === "review_summary") {
      setTimeout(function(){ S.loadReviewSummary(); }, 200);
    }
  },

  startPolling: function() {
    S.stopPolling();
    S.pollTimer = setInterval(function(){ S.refresh(); }, 10000);
  },
  stopPolling: function() {
    if (S.pollTimer) { clearInterval(S.pollTimer); S.pollTimer = null; }
  },
  startReviewPolling: function() {
    S.stopReviewPolling();
    S.doReviewRefresh();
    S.reviewTimer = setInterval(function(){ S.doReviewRefresh(); }, 10000);
  },
  stopReviewPolling: function() {
    if (S.reviewTimer) { clearInterval(S.reviewTimer); S.reviewTimer = null; }
  },

  refresh: function() {
    if (S.page === "home") {
      fetch(S.server + "/api/factors").then(function(r){return r.json();}).then(function(d){
        S.updateHomeData(d);
      }).catch(function(){});
      fetch(S.server + "/api/factors/history").then(function(r){return r.json();}).then(function(d){
        if (d.success && d.data) S.renderSentimentTrend(d.data);
      }).catch(function(){});
    }
  },

  switchMode: function(m) {
    S.mode = m;
    localStorage.setItem("inv_mode", m);
    var t = document.getElementById("modeTrend");
    var d = document.getElementById("modeDragon");
    if (t) t.className = "btn btn-sm mode-btn " + (m === "trend" ? "btn-a" : "btn-o");
    if (d) d.className = "btn btn-sm mode-btn " + (m === "dragon" ? "btn-a" : "btn-o");
    var ml = document.getElementById("modeLabel");
    if (ml) ml.textContent = "\u5f53\u524d\u6a21\u5f0f: " + (m === "trend" ? "\u8d8b\u52bf\u6ce2\u6bb5" : "\u9f99\u5934\u6253\u677f");
    if (S.homeData) S.updateHomeData(S.homeData);
  },

      // ===== AI复盘助手 =====
  reviewSummaryData: null, currentReviewTab: 'tab1',
  R_review_summary: function() {
    var h = '';
    h += '<div class="flex-between mb16"><div class="section-title">盘后复盘</div>';
    h += '  <div style="font-size:10px;color:var(--muted)">基于固定模板的结构化复盘，纯本地规则计算</div></div>';
    h += '<div class="rs-tabs">';
    h += '  <div class="rs-tab active" data-rs-tab="tab1" onclick="S.switchReviewTab(\'tab1\')">盘后快速复盘</div>';
    h += '  <div class="rs-tab" data-rs-tab="tab2" onclick="S.switchReviewTab(\'tab2\')">次日作战计划</div>';
    h += '  <div class="rs-tab" data-rs-tab="tab3" onclick="S.switchReviewTab(\'tab3\')">盘中突发诊断</div></div>';
    h += '<div class="rs-layout">';
    h += '  <div class="rs-left" id="rsLeft">';
    h += '    <div class="card" id="rsFormCard"><div class="card-header">数据<span id="rsStatus"></span></div>';
    h += '      <div id="rsFormContent">加载中...</div></div></div>';
    h += '  <div class="rs-right" id="rsRight">';
    h += '    <div class="card" id="rsResultCard">';
    h += '      <div class="flex-between"><div class="card-header">生成结果</div>';
    h += '        <button class="btn btn-sm btn-o" onclick="S.copyReviewResult()" id="rsCopyBtn">一键复制</button></div>';
    h += '      <div id="rsResultContent" class="rs-result">点击下方按钮生成复盘内容</div></div></div></div>';
    h += '<div style="text-align:center;margin-top:12px">';
    h += '  <button class="btn btn-a" onclick="S.generateReview()" id="rsGenBtn">生成复盘</button></div>';
    return h;
  },
  switchReviewTab: function(tab) {
    document.querySelectorAll('.rs-tab').forEach(function(n){ n.classList.remove('active'); });
    var el = document.querySelector('.rs-tab[data-rs-tab="' + tab + '"]');
    if (el) el.classList.add('active');
    S.currentReviewTab = tab;
    S.renderReviewForm();
  },
  loadReviewSummary: function() {
    fetch(S.server + '/api/review/summary').then(function(r){return r.json();}).then(function(d){
      if (d.success) {
        S.reviewSummaryData = d;
        S.renderReviewForm();
        var st = document.getElementById('rsStatus');
        if (st) st.textContent = ' (自动计算)';
      }
    }).catch(function(){});
  },
  renderReviewForm: function() {
    var tab = S.currentReviewTab || 'tab1';
    var fc = document.getElementById('rsFormContent');
    if (!fc) return;
    var d = S.reviewSummaryData;
    var m = (d && d.market) ? d.market : {};
    var html = '';
    if (tab === 'tab1') {
      html += '<div class="rs-field"><label>大盘指数 <span class="rs-auto">自动计算</span></label>';
      html += '<div class="rs-val">上证: ' + (m.sh_change !== undefined ? m.sh_change + '%' : '--') + ' | 深证: ' + (m.sz_change !== undefined ? m.sz_change + '%' : '--') + ' | 创业板: ' + (m.cyb_change !== undefined ? m.cyb_change + '%' : '--') + '</div></div>';
      html += '<div class="rs-field"><label>涨跌家数 <span class="rs-auto">自动计算</span></label>';
      html += '<div class="rs-val">上涨 ' + (m.up_count || '--') + ' | 下跌 ' + (m.down_count || '--') + '</div></div>';
      html += '<div class="rs-field"><label>涨跌停 <span class="rs-auto">自动计算</span></label>';
      html += '<div class="rs-val">涨停 ' + (m.limit_up_count || '--') + ' | 跌停 ' + (m.limit_down_count || '--') + ' | 炸板率 ' + (m.bomb_rate !== undefined ? m.bomb_rate + '%' : '--') + '</div></div>';
      html += '<div class="rs-field"><label>情绪阶段 <span class="rs-auto">自动计算</span></label>';
      var stage = d && d.sentiment_stage || '';
      var etype = d && d.effect_type || '';
      var edays = d && d.effect_days || 0;
      if (stage) {
        var pc = (stage === '冰点' || stage === '退潮') ? 'var(--red)' : (stage === '主升' || stage === '高潮') ? 'var(--green)' : 'var(--yellow)';
        html += '<div class="rs-val" style="color:' + pc + '">' + stage + ' (' + etype + '第' + edays + '天)</div></div>';
      } else {
        html += '<div class="rs-val">--</div></div>';
      }
      html += '<div class="rs-field"><label>核心题材 <span class="rs-auto">自动分组</span></label>';
      var sectors = (d && d.core_sectors) || [];
      if (sectors.length > 0) {
        for (var si = 0; si < sectors.length; si++) {
          html += '<div class="rs-val" style="margin-top:2px">' + sectors[si].topic + ': ' + (sectors[si].stocks || []).join(', ') + '</div>';
        }
      } else {
        html += '<div class="rs-val">--</div>';
      }
      html += '</div>';
      html += '<div class="rs-field"><label>风向标 <span class="rs-auto">自动计算</span></label>';
      html += '<div class="rs-val">' + (d && d.wind_vane ? d.wind_vane : '--') + '</div></div>';
      html += '<div class="rs-field"><label>补充信息</label>';
      html += '<textarea id="rsExtraTab1" class="rs-input" rows="2" placeholder="可手动补充题材细节、活口观察等"></textarea></div>';
    } else if (tab === 'tab2') {
      html += '<div class="rs-field"><label>目标股（1-3只，代码或名称，每行一只）</label>';
      html += '<textarea id="rsTargets" class="rs-input" rows="3" placeholder="例：中际旭创&#10;300308&#10;沪电股份"></textarea></div>';
      html += '<div class="rs-field"><label>大盘风控成交额阈值（亿）</label>';
      html += '<input id="rsVolThreshold" class="rs-input" value="' + (m.turnover_total ? Math.round(m.turnover_total) : '7000') + '"></div>';
      html += '<div class="rs-field"><label>当前情绪 <span class="rs-auto">自动计算</span></label>';
      html += '<div class="rs-val">' + (d && d.sentiment_stage ? d.sentiment_stage + ' / ' + (d.effect_type || '') : '--') + '</div></div>';
    } else if (tab === 'tab3') {
      html += '<div class="rs-field"><label>持仓股（代码或名称）</label>';
      html += '<input id="rsHoldCode" class="rs-input" placeholder="例：300308"></div>';
      html += '<div class="rs-field"><label>成本价</label>';
      html += '<input id="rsCostPrice" class="rs-input" type="number" placeholder="0.00"></div>';
      html += '<div class="rs-field"><label>现价</label>';
      html += '<input id="rsNowPrice" class="rs-input" type="number" placeholder="0.00"></div>';
      html += '<div class="rs-field"><label>当前情况</label>';
      html += '<select id="rsSituation" class="rs-select">';
      html += '  <option value="">请选择</option>';
      html += '  <option value="zhaban">炸板</option>';
      html += '  <option value="diepo">跌破均线</option>';
      html += '  <option value="datao">大单出逃</option></select></div>';
      html += '<div class="rs-field"><label>板块内涨停数</label>';
      html += '<input id="rsSectorLimitUp" class="rs-input" type="number" placeholder="0"></div>';
    }
    fc.innerHTML = html;
  },
  generateReview: function() {
    var tab = S.currentReviewTab || 'tab1';
    var rc = document.getElementById('rsResultContent');
    if (!rc) return;
    var d = S.reviewSummaryData;
    var m = (d && d.market) ? d.market : {};
    var output = '';
    var btn = document.getElementById('rsGenBtn');
    if (btn) { btn.textContent = '生成中...'; btn.disabled = true; }
    
    if (tab === 'tab1') {
      var stage = d && d.sentiment_stage || '暂无数据';
      var etype = d && d.effect_type || '';
      var edays = d && d.effect_days || 0;
      output += '【盘后快速复盘】\n\n';
      output += 'A. 当前情绪周期阶段：' + stage + '，今天是 ' + etype + ' 效应第 ' + edays + ' 天。\n\n';
      var sectors = (d && d.core_sectors) || [];
      output += 'B. 核心题材归纳（共 ' + Math.max(sectors.length, 0) + ' 个）：\n';
      if (sectors.length > 0) {
        for (var si = 0; si < sectors.length; si++) {
          var sec = sectors[si];
          var slist = sec.stocks || [];
          output += sec.topic + '\n';
          if (si < 2) {
            output += '├─ 龙头：' + (slist[0] || '暂无') + '\n';
            output += '└─ 跟风：' + (slist.slice(1).join('、') || '暂无') + '\n';
          } else {
            output += '└─ 代表：' + (slist.join('、') || '暂无') + '\n';
          }
        }
        var t0 = sectors[0] && sectors[0].topic || '';
        var t1 = sectors[1] && sectors[1].topic || '';
        var t2 = sectors[2] && sectors[2].topic || '';
        output += '题材逻辑：主线 ' + t0 + ' 带动支线 ' + t1 + '，' + t2 + ' 为补涨方向。\n';
      } else {
        output += '暂无数据\n';
      }
      output += '\nC. 今日活口名单：\n';
      var survivors = (d && d.survivor_stocks) || [];
      if (survivors.length > 0) {
        for (var vi = 0; vi < survivors.length; vi++) {
          output += (vi+1) + '. ' + survivors[vi].name + ' - ' + survivors[vi].uniqueness + '（' + survivors[vi].tag + '）\n';
        }
      } else {
        output += '暂无符合条件的活口股\n';
      }
      output += '\nD. 明天开盘第一眼必须看：' + (d && d.wind_vane ? d.wind_vane : '暂无') + '\n\n';
      output += '※ 以上分析仅供参考，不构成投资建议';
    
    } else if (tab === 'tab2') {
      var targets = (document.getElementById('rsTargets') || {}).value || '未输入目标股';
      var threshold = (document.getElementById('rsVolThreshold') || {}).value || '7000';
      var targetList = targets.split('\n').filter(function(x){return x.trim();});
      output += '=== A. 竞价达标线 ===\n';
      for (var ti2 = 0; ti2 < targetList.length; ti2++) {
        var tgt = targetList[ti2].trim();
        if (tgt) {
          output += '• ' + tgt + ': 高开1%-3%为达标，竞价量需达昨日10%\n';
        }
      }
      if (targetList.length === 0) output += '请先输入目标股代码/名称\n';
      output += '\n=== B. 操作指令 ===\n';
      output += '1) 竞价达标+有助攻: 可轻仓试探\n';
      output += '2) 竞价不达标: 等回调确认再进\n';
      output += '3) 盘中炸板急跌: 减仓或清仓\n';
      output += '\n=== C. 备胎方案 ===\n';
      output += '同板块中军/套利标的待确认\n';
      output += '\n=== D. 强制风控线 ===\n';
      output += '成交额低于' + threshold + '亿时空仓作废\n';
      var currVol = m.turnover_total;
      if (currVol && Number(currVol) < Number(threshold)) {
        output += '⚠ 当前成交额' + Number(currVol).toFixed(0) + '亿，低于阈值，市场偏弱\n';
      }
      output += '\n\n※ 以上分析仅供参考，不构成投资建议';
    
    } else if (tab === 'tab3') {
      var holdCode = (document.getElementById('rsHoldCode') || {}).value || '未输入';
      var costPrice = (document.getElementById('rsCostPrice') || {}).value || '0';
      var nowPrice = (document.getElementById('rsNowPrice') || {}).value || '0';
      var situation = (document.getElementById('rsSituation') || {}).value || '未选择';
      var sectorLimitUp = (document.getElementById('rsSectorLimitUp') || {}).value || '0';
      output += '【盘中突发诊断】\n';
      output += '持仓: ' + holdCode + ' | 成本: ' + costPrice + ' | 现价: ' + nowPrice + '\n';
      var pl = 0;
      if (Number(costPrice) > 0) { pl = (Number(nowPrice) - Number(costPrice)) / Number(costPrice) * 100; }
      output += '损益: ' + (pl >= 0 ? '+' : '') + pl.toFixed(2) + '%\n';
      var sitMap = {'zhaban':'炸板','diepo':'跌破均线','datao':'大单出逃'};
      output += '情况: ' + (sitMap[situation] || situation) + '\n';
      output += '板块涨停: ' + sectorLimitUp + '只\n';
      output += '\n=== 操作建议 ===\n';
      var stage3 = d && d.sentiment_stage || '';
      var isStrong = stage3 === '主升' || stage3 === '高潮';
      var isWeak = stage3 === '冰点' || stage3 === '退潮';
      var hasSectorSupport = Number(sectorLimitUp) >= 3;
      var lossDeep = pl < -5;
      if (isStrong && hasSectorSupport && !lossDeep) {
        output += '建议：格局持有\n理由：当前情绪强劲（' + stage3 + '），板块内涨停' + sectorLimitUp + '只，联动性较强，不宜轻易清仓。';
      } else if (lossDeep || (isWeak && !hasSectorSupport)) {
        output += '建议：清仓\n理由：情绪偏弱（' + stage3 + '），损失' + pl.toFixed(2) + '%，建议及时止损。';
      } else {
        output += '建议：减半仓\n理由：情绪' + stage3 + '，板块内涨停' + sectorLimitUp + '只，建议减仓观望。';
      }
      output += '\n\n※ 以上分析仅供参考，不构成投资建议';
    }
    
    rc.innerHTML = '<pre style="font-family:monospace;font-size:12px;line-height:1.6;color:var(--text);white-space:pre-wrap">' + S._escapeHtml(output) + '</pre>';
    if (btn) { btn.textContent = '生成复盘'; btn.disabled = false; }
  },
  copyReviewResult: function() {
    var rc = document.getElementById('rsResultContent');
    if (!rc || !rc.textContent) return;
    if (navigator.clipboard) {
      navigator.clipboard.writeText(rc.textContent).then(function(){
        var cb = document.getElementById('rsCopyBtn');
        if (cb) { cb.textContent = '已复制'; setTimeout(function(){ cb.textContent = '一键复制'; }, 1500); }
      }).catch(function(){});
    } else {
      var ta = document.createElement('textarea');
      ta.value = rc.textContent;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
    }
  },
  R_volume: function() {
    var h = "";
    h += "<div class=\"flex-between mb16\">";
    h += "  <div class=\"section-title\">\u91cf\u80fd\u76d1\u6d4b</div>";
    h += "  <div style=\"display:flex;gap:6px;align-items:center\">";
    h += "    <span id=\"volumeTs\" style=\"font-size:10px;color:var(--muted)\">--</span>";
    h += "    <span id=\"volumeStatus\" style=\"font-size:10px;padding:2px 6px;border-radius:4px;background:rgba(79,140,255,.1);color:var(--accent)\">\u52a0\u8f7d\u4e2d...</span></div></div>";
    h += "<div id=\"volumeHint\" style=\"font-size:10px;color:var(--muted);margin-bottom:8px;padding:6px 10px;border-radius:6px;display:none\"></div>";
    h += "<div class=\"filter-bar\">";
    h += "  <input id=\"volFilterKeyword\" placeholder=\"\u4ee3\u7801/\u540d\u79f0\" style=\"width:120px\" oninput=\"S.filterVolumeStocks()\">";
    h += "  <input id=\"volFilterRatio\" placeholder=\"\u6700\u4f4e\u653e\u91cf\u500d\u6570\" style=\"width:100px\" type=\"number\" oninput=\"S.filterVolumeStocks()\">";
    h += "  <button class=\"btn btn-sm btn-a\" onclick=\"S.doVolumeRefresh()\">\u5237\u65b0\u6570\u636e</button>";
    h += "  <span id=\"volumeCount\" style=\"font-size:11px;color:var(--muted)\">\u52a0\u8f7d\u4e2d...</span></div>";
    h += "<div class=\"card\" style=\"padding:0;overflow-x:auto\">";
    h += "<table class=\"tbl\" id=\"volumeTable\"><thead><tr>";
    h += "<th>\u4ee3\u7801</th><th>\u540d\u79f0</th><th>\u6700\u65b0\u4ef7</th><th>\u6da8\u8dcc\u5e45%</th><th>\u6210\u4ea4\u91cf(\u4e07\u624b)</th><th>\u653e\u91cf\u500d\u6570</th><th>\u6240\u5c5e\u677f\u5757</th><th>\u89e6\u53d1\u65f6\u95f4</th>";
    h += "</tr></thead><tbody id=\"volumeTbody\">";
    h += "<tr><td colspan=\"8\" style=\"text-align:center;color:var(--muted);padding:30px\">\u52a0\u8f7d\u4e2d...</td></tr>";
    h += "</tbody></table></div>";
    h += "<div style=\"margin-top:8px;font-size:10px;color:var(--muted)\">\u2502 \u653e\u91cf\u500d\u6570 = \u5f53\u65e5\u6210\u4ea4\u91cf / \u524d5\u65e5\u6700\u5c0f\u5355\u65e5\u6210\u4ea4\u91cf \u2502 \u7ea2\u8272\u6807\u8bb0\u4e3a\u653e\u91cf\u8d85\u8fc73\u500d \u2502 \u4eca\u65e5\u89e6\u53d1\u7684\u80a1\u7968\u5c45\u4e0a\u663e\u793a</div>";
    return h;
  },

  R_home: function() {
    var h = "";
    h += "<div class=\"flex-between mb16\">";
    h += "  <div class=\"section-title\">\u56db\u56e0\u5b50\u5b9e\u65f6\u9884\u6d4b\u770b\u677f</div>";
    h += "  <div style=\"display:flex;gap:6px;align-items:center\">";
    h += "    <button class=\"btn btn-o btn-sm\" onclick=\"S.refresh()\">\u5237\u65b0</button>";
    h += "    <span id=\"homeTs\" style=\"font-size:11px;color:var(--muted)\">--</span>";
    h += "    <span id=\"dataSourceLabel\" style=\"font-size:10px;padding:2px 6px;border-radius:4px;background:rgba(79,140,255,.1);color:var(--accent)\">查询中...</span>";
    h += "  </div></div>";

    h += "<div class=\"flex-between mb16\" style=\"gap:8px\">";
    h += "  <div style=\"display:flex;gap:6px\">";
    h += "    <button id=\"modeTrend\" class=\"btn btn-sm mode-btn btn-a\" onclick=\"S.switchMode('trend')\">\u8d8b\u52bf\u6ce2\u6bb5</button>";
    h += "    <button id=\"modeDragon\" class=\"btn btn-sm mode-btn btn-o\" onclick=\"S.switchMode('dragon')\">\u9f99\u5934\u6253\u677f</button>";
    h += "  </div>";
    h += "  <div id=\"modeLabel\" style=\"font-size:11px;color:var(--muted)\">\u5f53\u524d\u6a21\u5f0f: \u8d8b\u52bf\u6ce2\u6bb5</div></div>";

    h += "<div class=\"banner\" style=\"margin-bottom:14px\">";
    h += "<div class=\"bcard\" style=\"flex:1.2;min-width:180px;padding:14px 16px\">";
    h += "  <div style=\"font-size:10px;color:var(--muted);margin-bottom:4px\">\u7efc\u5408\u6982\u7387\u5206 <span id=\"liveBadge\" class=\"tag tag-b\" style=\"font-size:8px;vertical-align:middle\">--</span></div>";
    h += "  <div id=\"compositeScore\" style=\"font-size:36px;font-weight:800;color:var(--yellow);line-height:1.1\">--</div>";
    h += "  <div id=\"outlookText\" style=\"font-size:12px;color:var(--text);margin-top:4px\">\u7b49\u5f85\u6570\u636e...</div>";
    h += "  <div id=\"compChange\" class=\"cmp-line\" style=\"margin-top:2px;font-size:10px\"></div>";
    h += "  <div style=\"margin-top:8px;display:flex;gap:8px;flex-wrap:wrap\">";
    h += "    <span id=\"posAdvice\" style=\"font-size:11px;padding:2px 8px;border-radius:10px;background:rgba(0,212,170,.1);color:var(--green)\">\u4ed3\u4f4d: --</span>";
    h += "    <span id=\"riskLabel\" style=\"font-size:11px;padding:2px 8px;border-radius:10px;background:rgba(255,77,106,.1);color:var(--red)\">\u98ce\u9669: --</span>";
    h += "  </div>";
    h += "  <div id=\"coreAction\" style=\"font-size:11px;color:var(--accent);margin-top:6px;padding-top:6px;border-top:1px solid var(--border)\"></div>";
    h += "  <div id=\"forbiddenAction\" style=\"font-size:10px;color:var(--red);opacity:.7;margin-top:2px\"></div></div>";

    h += "<div style=\"flex:2;display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px\">";
    var mets = [["limitUp","\u6da8\u505c\u6570"],["limitDown","\u8dcc\u505c\u6570"],["bombRate","\u70b8\u677f\u7387"],["turnover","\u6210\u4ea4\u989d(\u4ebf)"],["northBound","\u5317\u5411\u8d44\u91d1(\u4ebf)"],["maxBoard","\u6700\u9ad8\u8fde\u677f"]];
    for (var i=0;i<mets.length;i++) {
      h += "<div class=\"bcard\" style=\"padding:8px 10px;min-width:auto\">";
      h += "  <div class=\"bl\" style=\"font-size:9px\">"+mets[i][1]+"</div>";
      h += "  <div id=\""+mets[i][0]+"\" class=\"bv\" style=\"font-size:15px\">--</div>";
    h += "  <div id=\""+mets[i][0]+"_prev\" class=\"cmp-line\">--</div></div>";
    }
    h += "</div></div>";

    h += "<div class=\"factor-grid\">";
    var facs = [["sentiment","\u60c5\u7eea\u5468\u671f","35%"],["sector","\u677f\u5757\u8054\u52a8","30%"],["chip","\u7b79\u7801\u7ed3\u6784","20%"],["overnight","\u9694\u591c\u9884\u671f","15%"]];
    for (var i=0;i<facs.length;i++) {
      var f=facs[i];
      h += "<div class=\"card card-sm\" id=\"fc_"+f[0]+"\" style=\"cursor:pointer\" onclick=\"S.toggleFactorDetail('"+f[0]+"')\">";
      h += "  <div class=\"flex-between mb8\"><div style=\"display:flex;align-items:center;gap:6px\">";
      h += "    <span style=\"font-size:12px;font-weight:600;color:#fff\">"+f[1]+"</span>";
      h += "    <span id=\"ftag_"+f[0]+"\" class=\"tag tag-b\" style=\"font-size:9px\">--</span></div>";
      h += "    <span style=\"font-size:10px;color:var(--muted)\">\u6743\u91cd "+f[2]+"</span></div>";
      h += "  <div id=\"fscore_"+f[0]+"\" style=\"font-size:28px;font-weight:700;color:var(--yellow);margin-bottom:2px\">--</div>";
      h += "  <div id=\"fdesc_"+f[0]+"\" class=\"text-sm text-muted\">\u7b49\u5f85\u6570\u636e...</div>";
      h += "  <div class=\"progress\" style=\"margin-top:6px\"><div id=\"fbar_"+f[0]+"\" class=\"bar\" style=\"width:0%;background:var(--accent)\"></div></div>";
      h += "  <div id=\"faction_"+f[0]+"\" style=\"font-size:10px;color:var(--muted);margin-top:4px;padding-top:4px;border-top:1px solid rgba(26,35,88,.4)\"></div>";
      h += "  <div id=\"fdetail_"+f[0]+"\" style=\"display:none;margin-top:6px;padding-top:6px;border-top:1px solid var(--border);font-size:11px;color:var(--muted)\"></div></div>";
    }
    h += "</div>";

    h += "<div class=\"card\" style=\"margin-top:6px\"><div class=\"flex-between mb8\"><div class=\"text-lg\" style=\"font-size:13px\">\u60c5\u7eea\u8d8b\u52bf\u56fe</div></div><div id=\"sentimentChart\" style=\"width:100%;height:260px\"></div></div>";

    h += "<div class=\"card card-sm\"><div class=\"text-sm text-muted mb8\">\u9012\u8fdb\u7ea6\u675f\u4f20\u5bfc</div><div id=\"constraintChain\" style=\"display:flex;align-items:center;gap:6px;font-size:11px\"></div><div id=\"constraintDesc\" class=\"text-sm text-muted mt4\"></div></div>";

    h += "<div style=\"font-size:10px;color:var(--muted);text-align:center;padding:10px 0\">\u57fa\u4e8e\u5f53\u524d\u5b9e\u65f6\u6570\u636e\u524d\u77bb\u63a8\u6f14\uff0c\u4e0d\u6784\u6210\u6295\u8d44\u5efa\u8bae | \u6570\u636e\u5237\u65b0\u5468\u671f 10\u79d2</div>";
    return h;
  },

  toggleFactorDetail: function(id) {
    var el = document.getElementById("fdetail_"+id);
    if (el) {
      S._factorDetails[id] = !S._factorDetails[id];
      el.style.display = S._factorDetails[id] ? "block" : "none";
    }
  },

  updateHomeData: function(d) {
    S.homeData = d;
    var _dsl = document.getElementById("dataSourceLabel");
    if (_dsl) {
      if (d.is_live) { _dsl.textContent = "● 实时"; _dsl.style.background = "rgba(0,212,170,.1)"; _dsl.style.color = "var(--green)"; }
      else { _dsl.textContent = "● 收盘数据"; _dsl.style.background = "rgba(90,101,153,.1)"; _dsl.style.color = "var(--muted)"; }
    }
    var ts = document.getElementById("homeTs");
    if (ts && d.ts) ts.textContent = d.ts;
    var score = d.composite;
    var cs = document.getElementById("compositeScore");
    if (cs && score !== null && score !== undefined) {
      cs.textContent = Math.round(score);
      cs.style.color = score >= 75 ? "var(--green)" : score >= 55 ? "var(--yellow)" : "var(--red)";
    }
    // Live badge
    var lb = document.getElementById("liveBadge");
    if (lb) lb.textContent = d.is_live ? "\u5b9e\u65f6" : "\u6628\u6536";
    if (lb) lb.className = "tag " + (d.is_live ? "tag-g" : "tag-b");
    // Composite comparison vs prev day
    var cc = document.getElementById("compChange");
    if (cc) {
      if (d.prev_day && d.prev_day.composite_score !== null && d.prev_day.composite_score !== undefined && score !== null && score !== undefined) {
        var diff = score - d.prev_day.composite_score;
        var arrow = diff > 0 ? "\u2191" : diff < 0 ? "\u2193" : "\u2192";
        cc.textContent = "\u8f83\u6628\u65e5 " + (diff > 0 ? "+" : "") + Math.round(diff) + "\u5206 " + arrow;
        cc.style.color = diff > 0 ? "var(--green)" : diff < 0 ? "var(--red)" : "var(--muted)";
      } else {
        cc.textContent = "";
      }
    }
    var ot = document.getElementById("outlookText");
    if (ot && d.outlook_desc) ot.textContent = d.outlook_desc;

    if (d.advice) {
      var ca = document.getElementById("coreAction");
      if (ca && d.advice.core_action) ca.textContent = "\u6838\u5fc3\u64cd\u4f5c: " + d.advice.core_action;
      var fa = document.getElementById("forbiddenAction");
      if (fa && d.advice.forbidden) fa.textContent = "\u7981\u5fcc: " + d.advice.forbidden;
      var fks = ["sentiment","sector","chip","overnight"];
      for (var i=0;i<fks.length;i++) {
        var el = document.getElementById("faction_"+fks[i]);
        if (el && d.advice.factor_advice && d.advice.factor_advice[fks[i]]) el.textContent = d.advice.factor_advice[fks[i]];
      }
    }

    var pos = document.getElementById("posAdvice");
    var risk = document.getElementById("riskLabel");
    if (score !== null && score !== undefined) {
      var pt = score >= 75 ? "\u91cd\u4ed3(\u226480%)" : score >= 55 ? "\u534a\u4ed3(\u226450%)" : score >= 40 ? "\u8f7b\u4ed3(\u226430%)" : "\u7a7a\u4ed3\u89c2\u671b";
      var rt = score >= 75 ? "\u4f4e\u98ce\u9669" : score >= 55 ? "\u4e2d\u7b49\u98ce\u9669" : score >= 40 ? "\u8f83\u9ad8\u98ce\u9669" : "\u9ad8\u98ce\u9669";
      if (pos) pos.textContent = "\u4ed3\u4f4d: " + pt;
      if (risk) {
        risk.textContent = "\u98ce\u9669: " + rt;
        risk.style.background = score >= 75 ? "rgba(0,212,170,.1)" : score >= 55 ? "rgba(255,176,32,.1)" : "rgba(255,77,106,.1)";
        risk.style.color = score >= 75 ? "var(--green)" : score >= 55 ? "var(--yellow)" : "var(--red)";
      }
    }

    if (d.market) {
      var m = d.market;
      var p = d.prev_day ? d.prev_day.market : null;
      var setVal = function(id, val) {
        var el = document.getElementById(id);
        if (el) el.textContent = (val !== null && val !== undefined) ? val : "--";
      };
      setVal("limitUp", m.limit_up_count);
      setVal("limitDown", m.limit_down_count);
      setVal("bombRate", m.bomb_rate !== undefined ? m.bomb_rate.toFixed(1) + "%" : "--");
      setVal("turnover", m.turnover_total !== undefined ? Number(m.turnover_total).toFixed(1) : "--");
      setVal("northBound", m.northbound_net !== undefined ? Number(m.northbound_net).toFixed(1) : "--");
      setVal("maxBoard", m.max_board_height);
      // Prev day comparison
      var setCmp = function(id, todayVal, prevVal, suffix) {
        var el = document.getElementById(id + "_prev");
        if (!el) return;
        if (prevVal === null || prevVal === undefined || prevVal === "--") {
          el.textContent = "--";
          return;
        }
        if (todayVal === null || todayVal === undefined || todayVal === "--") {
          el.textContent = "";
          return;
        }
        suffix = suffix || "";
        var diff = todayVal - prevVal;
        var arrow = diff > 0 ? "\u2191" : diff < 0 ? "\u2193" : "\u2192";
        var diffStr = (diff > 0 ? "+" : "") + Number(diff).toFixed(diff % 1 === 0 ? 0 : 1);
        el.textContent = "\u6628" + prevVal + suffix + " " + diffStr + arrow;
        el.style.color = diff > 0 ? "var(--green)" : diff < 0 ? "var(--red)" : "var(--muted)";
      };
      if (p) {
        setCmp("limitUp", m.limit_up_count, p.limit_up_count, "");
        setCmp("limitDown", m.limit_down_count, p.limit_down_count, "");
        setCmp("bombRate", m.bomb_rate, p.bomb_rate, "%");
        setCmp("turnover", m.turnover_total, p.turnover_total, "");
        setCmp("northBound", m.northbound_net, p.northbound_net, "");
        setCmp("maxBoard", m.max_board_height, p.max_board_height, "");
      } else {
        var els = document.querySelectorAll("[id$=_prev]");
        for (var i=0;i<els.length;i++) els[i].textContent = "--";
      }
      // Stale indicator
      if (m.data_tip) {
        var lb = document.getElementById("liveBadge");
        if (lb && !d.is_live) lb.textContent = "\u6628\u6536";
      }
    }

    if (d.factors) {
      for (var i=0;i<d.factors.length;i++) {
        var f = d.factors[i];
        var fid = f.id;
        var fs = document.getElementById("fscore_"+fid);
        var fd = document.getElementById("fdesc_"+fid);
        var ft = document.getElementById("ftag_"+fid);
        var fb = document.getElementById("fbar_"+fid);
        if (fs) {
          if (f.score !== null && f.score !== undefined) {
            fs.textContent = Math.round(f.score);
            fs.style.color = f.score >= 70 ? "var(--green)" : f.score >= 40 ? "var(--yellow)" : "var(--red)";
            if (fb) { fb.style.width = f.score + "%"; fb.style.background = f.score >= 70 ? "var(--green)" : f.score >= 40 ? "var(--yellow)" : "var(--red)"; }
          } else { fs.textContent = "N/A"; fs.style.color = "var(--muted)"; }
        }
        if (fd) fd.textContent = f.detail && f.detail.desc ? f.detail.desc : "--";
        if (ft) {
          if (f.score !== null && f.score !== undefined) {
            var lvl = f.score >= 70 ? "\u5f3a" : f.score >= 40 ? "\u4e2d" : "\u5f31";
            ft.textContent = lvl;
            ft.className = "tag " + (f.score >= 70 ? "tag-g" : f.score >= 40 ? "tag-y" : "tag-r");
          } else { ft.textContent = "\u5f85\u66f4\u65b0"; ft.className = "tag tag-b"; }
        }
        var fdet = document.getElementById("fdetail_"+fid);
        if (fdet && f.detail && f.detail.detail && f.detail.detail.scores) {
          var dh = "";
          var dd = f.detail.detail;
          if (dd.scores) { for (var sk in dd.scores) { dh += "<div style=\"display:flex;justify-content:space-between;padding:2px 0\"><span>"+sk+"</span><span>"+dd.scores[sk]+"</span></div>"; } }
          else if (dd.info) { dh += "<div>"+dd.info+"</div>"; }
          fdet.innerHTML = dh;
        }
      }
    }

    var cc = document.getElementById("constraintChain");
    if (cc) {
      var cols = ["#4f8cff","#00d4aa","#ffb020","#a78bfa"];
      var nms = ["\u60c5\u7eea","\u677f\u5757","\u7b79\u7801","\u9694\u591c"];
      var ch = "";
      for (var i=0;i<4;i++) {
        var fs2 = d.factors && d.factors[i] ? d.factors[i].score : null;
        var act = fs2 !== null && fs2 !== undefined;
        ch += "<div style=\"display:flex;flex-direction:column;align-items:center;gap:2px;flex:1\">";
        ch += "<div style=\"width:100%;height:4px;border-radius:2px;background:"+(act?cols[i]:"var(--border)")+";opacity:"+(act?"1":"0.3")+"\"></div>";
        ch += "<span style=\"font-size:10px;color:"+(act?cols[i]:"var(--muted)")+"\">"+nms[i]+"</span></div>";
      }
      cc.innerHTML = ch;
    }
    var cd = document.getElementById("constraintDesc");
    if (cd && d.advice && d.advice.constraint_desc) cd.textContent = d.advice.constraint_desc;
  },

  renderSentimentTrend: function(histData) {
    var dom = document.getElementById("sentimentChart");
    if (!dom) return;
    var chart = echarts.getInstanceByDom(dom);
    if (!chart) chart = echarts.init(dom);
    var dps = (histData && histData.length > 0) ? histData : [];
    if (dps.length === 0) {
      chart.clear();
      chart.setOption({ title: { text: "\u7b49\u5f85\u6570\u636e...", textStyle: { color: "#5a6599", fontSize: 13 }, left: "center", top: "center" }, grid: { top: 20, bottom: 20, left: 40, right: 20 }, backgroundColor: "transparent" });
      return;
    }
    var times = [], vals = [];
    for (var i=0;i<dps.length;i++) { times.push(dps[i].t||""); vals.push(dps[i].v||0); }
    chart.setOption({
      tooltip: { trigger: "axis", backgroundColor: "rgba(15,21,53,.9)", borderColor: "#1a2358", textStyle: { color: "#c8d4e8", fontSize: 11 } },
      grid: { top: 20, bottom: 20, left: 40, right: 16 },
      xAxis: { type: "category", data: times, axisLine: { lineStyle: { color: "#1a2358" } }, axisLabel: { color: "#5a6599", fontSize: 10 } },
      yAxis: { type: "value", min: 0, max: 100, splitLine: { lineStyle: { color: "rgba(26,35,88,.5)" } }, axisLabel: { color: "#5a6599", fontSize: 10 } },
      series: [{ type: "line", data: vals, smooth: true, lineStyle: { color: "#4f8cff", width: 2 }, areaStyle: { color: { type: "linear", x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: "rgba(79,140,255,.3)" }, { offset: 1, color: "rgba(79,140,255,.02)" }] } }, symbol: "circle", symbolSize: 4, itemStyle: { color: "#4f8cff" } }],
      backgroundColor: "transparent"
    });
    S.charts.sentiment = chart;
  },

  // ==================== INDUSTRY PAGE ====================
  R_industry: function() {
    var h = "";
    h += "<div style=\"display:flex;gap:14px;height:calc(100vh - 60px)\">";
    h += "<div style=\"width:160px;min-width:160px;background:var(--card);border-radius:12px;padding:10px;border:1px solid var(--border);overflow-y:auto\">";
    h += "  <div style=\"font-size:12px;font-weight:600;color:#fff;margin-bottom:8px;padding-bottom:6px;border-bottom:1px solid var(--border)\">\u4ea7\u4e1a\u8d5b\u9053</div>";
    h += "  <div id=\"industryList\"></div></div>";
    h += "<div style=\"flex:1;display:flex;flex-direction:column;gap:10px;overflow:hidden\">";
    h += "  <div style=\"display:flex;align-items:center;gap:8px;flex-wrap:wrap\">";
    h += "    <div id=\"industryName\" style=\"font-size:16px;font-weight:700;color:#fff\">AI\u7b97\u529b\u4ea7\u4e1a\u94fe</div>";
    h += "    <span id=\"industryScore\" class=\"tag tag-g\" style=\"font-size:10px\">\u666f\u6c14: --</span>";
    h += "    <div style=\"flex:1\"></div>";
    h += "    <button id=\"viewBtnChain\" class=\"btn btn-sm view-btn btn-a\" onclick=\"S.switchChainView('sankey')\">\u94fe\u72b6\u89c6\u56fe</button>";
    h += "    <button id=\"viewBtnTree\" class=\"btn btn-sm view-btn btn-o\" onclick=\"S.switchChainView('tree')\">\u6811\u72b6\u89c6\u56fe</button>";
    h += "    <span style=\"font-size:10px;color:var(--muted)\">\u79bb\u7ebf\u9884\u7f6e\u6570\u636e</span></div>";
    h += "  <div id=\"chainChart\" style=\"flex:1;min-height:400px;background:var(--card);border-radius:12px;border:1px solid var(--border)\"></div>";
    h += "  <div id=\"nodeDetailPanel\" style=\"display:none;background:var(--card);border-radius:12px;border:1px solid var(--border);padding:12px 14px;max-height:200px;overflow-y:auto\">";
    h += "    <div class=\"flex-between mb8\"><div style=\"display:flex;align-items:center;gap:8px\">";
    h += "      <span id=\"nodeName\" style=\"font-size:14px;font-weight:600;color:#fff\"></span>";
    h += "      <span id=\"nodeLevel\" class=\"tag tag-b\" style=\"font-size:9px\"></span>";
    h += "      <span id=\"nodeScore\" class=\"tag tag-g\" style=\"font-size:9px\"></span></div>";
    h += "      <button class=\"btn btn-o btn-sm\" onclick=\"document.getElementById('" + "nodeDetailPanel').style.display='none'\">\u6536\u8d77 \u2715</button></div>";
    h += "    <div style=\"display:grid;grid-template-columns:1fr 1fr;gap:8px\">";
    h += "      <div><div class=\"text-sm text-muted\">\u4ea7\u4e1a\u903b\u8f91</div><div id=\"nodeLogic\" class=\"text-sm\" style=\"color:var(--text)\"></div></div>";
    h += "      <div><div class=\"text-sm text-muted\">\u6838\u5fc3\u58c1\u5792</div><div id=\"nodeBarrier\" class=\"text-sm\" style=\"color:var(--text)\"></div></div>";
    h += "      <div><div class=\"text-sm text-muted\">\u6838\u5fc3\u6807\u7684</div><div id=\"nodeStocks\" class=\"text-sm\" style=\"color:var(--accent)\"></div></div>";
    h += "      <div><div class=\"text-sm text-muted\">\u8fd1\u671f\u8d44\u8baf</div><div id=\"nodeNews\" class=\"text-sm\" style=\"color:var(--text)\"></div></div></div></div>";
    h += "</div></div>";
    return h;
  },

  chainData: {
    name: "AI\u7b97\u529b\u4ea7\u4e1a\u94fe", score: 82,
    children: [
      { name: "\u4e0a\u6e38 \u4f9b\u7ed9\u7aef", children: [
        { name: "\u80fd\u6e90\u7535\u529b\u914d\u5957", score: 75, logic: "AI\u7b97\u529b\u9ad8\u80fd\u8017\u9a71\u52a8\u6db2\u51b7/UPS\u9700\u6c42\u7206\u53d1", barrier: "\u8ba4\u8bc1\u58c1\u5792\u9ad8, \u5ba2\u6237\u7c98\u6027\u5f3a", stocks: [{code:"300499",name:"\u9ad8\u6f9c\u80a1\u4efd"},{code:"002837",name:"\u82f1\u7ef4\u514b"},{code:"002851",name:"\u9ea6\u683c\u7c73\u7279"}] },
        { name: "\u534a\u5bfc\u4f53\u6838\u5fc3\u6750\u6599", score: 80, logic: "\u56fd\u4ea7\u66ff\u4ee3\u52a0\u901f, HBM/\u5149\u63a9\u819c\u9700\u6c42\u65fa\u76db", barrier: "\u6280\u672f\u58c1\u5792\u6781\u9ad8, \u9a8c\u8bc1\u5468\u671f\u957f", stocks: [{code:"300666",name:"\u6c5f\u4e30\u7535\u5b50"},{code:"002371",name:"\u5317\u65b9\u534e\u521b"}] },
        { name: "\u534a\u5bfc\u4f53\u751f\u4ea7\u8bbe\u5907", score: 85, logic: "\u6676\u5706\u5382\u6269\u4ea7\u9a71\u52a8\u8bbe\u5907\u9700\u6c42\u6301\u7eed\u589e\u957f", barrier: "\u5149\u523b\u673a\u7b49\u6838\u5fc3\u8bbe\u5907\u9ad8\u5ea6\u5782\u65ad", stocks: [{code:"688012",name:"\u4e2d\u5fae\u516c\u53f8"},{code:"002371",name:"\u5317\u65b9\u534e\u521b"},{code:"300604",name:"\u957f\u5ddd\u79d1\u6280"}] },
        { name: "\u6838\u5fc3\u96f6\u90e8\u4ef6", score: 78, logic: "AI\u82af\u7247/800G\u5149\u6a21\u5757\u9700\u6c42\u7206\u53d1", barrier: "\u9ad8\u7aef\u82af\u7247\u8bbe\u8ba1/\u5236\u9020\u58c1\u5792", stocks: [{code:"300308",name:"\u4e2d\u9645\u8bb8\u521b"},{code:"688041",name:"\u6d77\u5149\u4fe1\u606f"}] }
      ]},
      { name: "\u4e2d\u6e38 \u7b97\u529b\u5236\u9020\u8fd0\u8425", children: [
        { name: "\u786c\u4ef6\u5236\u9020", score: 82, logic: "AI\u670d\u52a1\u5668/\u5149\u6a21\u5757\u8ba2\u5355\u9971\u6ee1, \u5148\u8fdb\u5c01\u88c5\u4ea7\u80fd\u7d27\u7f3a", barrier: "\u91cf\u4ea7\u80fd\u529b+\u5ba2\u6237\u8ba4\u8bc1", stocks: [{code:"300308",name:"\u4e2d\u9645\u8bb8\u521b"},{code:"000977",name:"\u6d6a\u6f6e\u4fe1\u606f"},{code:"688256",name:"\u5bd2\u6b66\u7eaa"}] },
        { name: "\u7b97\u529b\u8fd0\u8425", score: 70, logic: "\u667a\u7b97\u4e2d\u5fc3\u5efa\u8bbe\u52a0\u901f, \u7b97\u529b\u79df\u8d41\u6a21\u5f0f\u5174\u8d77", barrier: "\u8d44\u91d1\u58c1\u5792\u9ad8, \u7535\u529b\u8d44\u6e90\u7a00\u7f3a", stocks: [{code:"300442",name:"\u6da6\u6cfd\u79d1\u6280"},{code:"603881",name:"\u6570\u636e\u6e2f"},{code:"000938",name:"\u7d2b\u5149\u80a1\u4efd"}] }
      ]},
      { name: "\u4e0b\u6e38 \u9700\u6c42\u5e94\u7528", children: [
        { name: "\u901a\u7528AI\u5e94\u7528", score: 85, logic: "\u5927\u6a21\u578b\u519b\u5907\u8d5b, Agent/\u751f\u6210\u5f0f\u5e94\u7528\u5feb\u901f\u843d\u5730", barrier: "\u7b97\u6cd5+\u6570\u636e+\u7b97\u529b\u4e09\u91cd\u58c1\u5792", stocks: [{code:"688111",name:"\u91d1\u5c71\u529e\u516c"},{code:"002230",name:"\u79d1\u5927\u8baf\u98de"},{code:"300418",name:"\u6606\u4ed1\u4e07\u7ef4"}] },
        { name: "\u884c\u4e1aAI\u5e94\u7528", score: 75, logic: "\u81ea\u52a8\u9a7e\u9a76/\u5de5\u4e1aAI/\u533b\u7597AI\u591a\u70b9\u5f00\u82b1", barrier: "\u884c\u4e1aknow-how+\u6570\u636e\u79ef\u7d2f", stocks: [{code:"002920",name:"\u5fb7\u8d5b\u897f\u5a01"},{code:"688208",name:"\u9053\u901a\u79d1\u6280"}] }
      ]}
    ]
  },

  currentChainView: "sankey",

  renderIndustryChain: function() {
    S.renderIndustryList();
    S.switchChainView("sankey");
  },

  renderIndustryList: function() {
    var el = document.getElementById("industryList");
    if (!el) return;
    el.innerHTML = "<div class=\"industry-item active\" data-ind=\"chain\" onclick=\"S.selectIndustry('chain')\"><div style=\"font-size:12px;font-weight:600\">AI\u7b97\u529b\u4ea7\u4e1a\u94fe</div><div style=\"font-size:10px;color:var(--green);margin-top:2px\">\u666f\u6c14 82</div></div>";
  },

  selectIndustry: function(id) {
    document.querySelectorAll(".industry-item").forEach(function(el){ el.classList.remove("active"); });
    var sel = document.querySelector(".industry-item[data-ind=\""+id+"\"]");
    if (sel) sel.classList.add("active");
    S.switchChainView(S.currentChainView);
  },

  switchChainView: function(view) {
    S.currentChainView = view;
    var b1 = document.getElementById("viewBtnChain");
    var b2 = document.getElementById("viewBtnTree");
    if (b1) b1.className = "btn btn-sm view-btn " + (view==="sankey"?"btn-a":"btn-o");
    if (b2) b2.className = "btn btn-sm view-btn " + (view==="tree"?"btn-a":"btn-o");
    var ne = document.getElementById("industryName");
    if (ne) ne.textContent = S.chainData.name;
    var se = document.getElementById("industryScore");
    if (se) { var sc = S.chainData.score; se.textContent = "\u666f\u6c14: "+sc; se.className = "tag "+(sc>=70?"tag-g":sc>=40?"tag-y":"tag-r"); }
    if (view === "sankey") S.renderSankeyView();
    else S.renderTreeView();
  },

  renderSankeyView: function() {
    var dom = document.getElementById("chainChart");
    if (!dom) return;
    dom.style.height = "100%";
    var chart = echarts.getInstanceByDom(dom);
    if (!chart) chart = echarts.init(dom);
    var d = S.chainData;
    var nodes = [];
    var links = [];
    var cats = [d.children[0].name, d.children[1].name, d.children[2].name];
    var cols = ["rgba(79,140,255,.15)","rgba(0,212,170,.12)","rgba(167,139,250,.12)"];
    for (var i=0;i<cats.length;i++) {
      nodes.push({name: cats[i], itemStyle: {color: cols[i]}, label: {color: "#c8d4e8", fontWeight: "bold", fontSize: 11}});
      var cat = d.children[i];
      if (cat.children) {
        for (var j=0;j<cat.children.length;j++) {
          var nd = cat.children[j];
          var nc = nd.score >= 70 ? "rgba(0,212,170,.6)" : nd.score >= 40 ? "rgba(255,176,32,.6)" : "rgba(255,77,106,.6)";
          nodes.push({name: nd.name, itemStyle: {color: nc, borderRadius: 4}, label: {color: "#c8d4e8", fontSize: 10}});
          links.push({source: cats[i], target: nd.name, value: 1});
        }
      }
    }
    chart.setOption({
      tooltip: { trigger: "item", formatter: function(p) {
        if (p.dataType === "node") {
          var info = S.findChainNode(p.name);
          return info ? "<b>"+p.name+"</b><br/>\u666f\u6c14\u5ea6: "+(info.score||"--")+"<br/>"+(info.logic||"") : "<b>"+p.name+"</b>";
        }
        return "";
      }, backgroundColor: "rgba(15,21,53,.95)", borderColor: "#1a2358", textStyle: {color: "#c8d4e8", fontSize: 11} },
      series: [{
        type: "sankey", layout: "none", layoutIterations: 0, emphasis: {focus: "adjacency"},
        nodeWidth: 16, nodeGap: 10, data: nodes, links: links,
        lineStyle: {color: "gradient", curveness: 0.5, opacity: 0.2}
      }],
      backgroundColor: "transparent"
    });
    chart.off("click");
    var self = this;
    chart.on("click", function(p) {
      if (p.dataType === "node") {
        var info = self.findChainNode(p.name);
        if (info) self.showNodeDetail(info);
      }
    });
    S.charts.chain = chart;
  },

  renderTreeView: function() {
    var dom = document.getElementById("chainChart");
    if (!dom) return;
    var chart = echarts.getInstanceByDom(dom);
    if (!chart) chart = echarts.init(dom);
    function buildTree(node) {
      var c = node.score >= 70 ? "#00d4aa" : node.score >= 40 ? "#ffb020" : "#ff4d6a";
      var r = {name: node.name + (node.score ? " ("+node.score+")" : ""), itemStyle: {color: c}, label: {color: "#c8d4e8", fontSize: 10}};
      if (node.children && node.children.length > 0) {
        r.children = [];
        for (var i=0;i<node.children.length;i++) r.children.push(buildTree(node.children[i]));
      }
      return r;
    }
    var td = buildTree(S.chainData);
    chart.setOption({
      tooltip: { trigger: "item", formatter: function(p) { return "<b>"+(p.name||"")+"</b>"; }, backgroundColor: "rgba(15,21,53,.95)", borderColor: "#1a2358", textStyle: {color: "#c8d4e8", fontSize: 11} },
      series: [{
        type: "tree", data: [td], layout: "orthogonal", orient: "LR", roam: true, symbolSize: 8,
        lineStyle: {color: "#1a2358", width: 1}, leaves: {label: {position: "right", color: "#c8d4e8", fontSize: 10}},
        expandAndCollapse: true, initialTreeDepth: 2, label: {color: "#c8d4e8", fontSize: 10}
      }],
      backgroundColor: "transparent"
    });
    chart.off("click");
    var self = this;
    chart.on("click", function(p) {
      if (p && p.name) {
        var nm = p.name.replace(/\s*\(\d+\)\s*$/, "");
        var info = self.findChainNode(nm);
        if (info) self.showNodeDetail(info);
      }
    });
    S.charts.chain = chart;
  },

  findChainNode: function(name) {
    function search(node) {
      if (node.name === name || node.name.indexOf(name) === 0) return node;
      if (node.children) {
        for (var i=0;i<node.children.length;i++) {
          var r = search(node.children[i]);
          if (r) return r;
        }
      }
      return null;
    }
    return search(S.chainData);
  },

  showNodeDetail: function(node) {
    var panel = document.getElementById("nodeDetailPanel");
    if (!panel) return;
    panel.style.display = "block";
    var ne = document.getElementById("nodeName");
    if (ne) ne.textContent = node.name;
    var le = document.getElementById("nodeLevel");
    if (le) {
      var lv = "\u4e2d\u6e38";
      if (node.name.indexOf("\u80fd\u6e90")>=0||node.name.indexOf("\u6750\u6599")>=0||node.name.indexOf("\u8bbe\u5907")>=0||node.name.indexOf("\u96f6\u90e8\u4ef6")>=0) lv = "\u4e0a\u6e38";
      else if (node.name.indexOf("\u786c\u4ef6")>=0||node.name.indexOf("\u8fd0\u8425")>=0) lv = "\u4e2d\u6e38";
      else if (node.name.indexOf("\u901a\u7528")>=0||node.name.indexOf("\u884c\u4e1a")>=0) lv = "\u4e0b\u6e38";
      le.textContent = lv;
    }
    var se = document.getElementById("nodeScore");
    if (se && node.score) { se.textContent = "\u666f\u6c14 "+node.score; se.className = "tag "+(node.score>=70?"tag-g":node.score>=40?"tag-y":"tag-r"); }
    var log = document.getElementById("nodeLogic");
    if (log) log.textContent = node.logic || "\u6682\u65e0\u6570\u636e";
    var bar = document.getElementById("nodeBarrier");
    if (bar) bar.textContent = node.barrier || "\u6682\u65e0\u6570\u636e";
    var stk = document.getElementById("nodeStocks");
    if (stk) {
      if (node.stocks && node.stocks.length > 0) {
        var sh = "";
        for (var i=0;i<node.stocks.length;i++) {
          sh += "<span style=\"margin-right:8px;cursor:pointer;color:var(--accent)\" onclick=\"S.nav('review')\">"+node.stocks[i].code+" "+node.stocks[i].name+"</span>";
        }
        stk.innerHTML = sh;
      } else { stk.textContent = "\u6682\u65e0\u6570\u636e"; }
    }
    var nws = document.getElementById("nodeNews");
    if (nws) nws.textContent = "\u6682\u65e0\u6700\u65b0\u8d44\u8baf";
  },

  // ==================== REVIEW PAGE ====================
  R_review: function() {
    var h = "";
    h += "<div class=\"flex-between mb16\">";
    h += "  <div class=\"section-title\">\u76d8\u540e\u590d\u76d8\u5de5\u5177</div>";
    h += "  <div style=\"display:flex;gap:6px;align-items:center\">";
    h += "    <span id=\"reviewSource\" style=\"font-size:10px;color:var(--muted)\"></span>";
    h += "    <span id=\"reviewTs\" style=\"font-size:10px;color:var(--muted)\">--</span>";
    h += "    <button class=\"btn btn-sm btn-a\" onclick=\"S.generateReport()\">\u751f\u6210\u62a5\u544a</button></div></div>";

    h += "<div class=\"filter-bar\">";
    h += "  <input id=\"filterKeyword\" placeholder=\"\u4ee3\u7801/\u540d\u79f0\" style=\"width:140px\" oninput=\"S.filterReviewStocks()\">";
    h += "  <input id=\"filterMinAmount\" placeholder=\"\u6700\u4f4e\u6210\u4ea4\u989d(\u4ebf)\" style=\"width:100px\" type=\"number\" oninput=\"S.filterReviewStocks()\">";
    h += "  <input id=\"filterMinTurnover\" placeholder=\"\u6700\u4f4e\u6362\u624b\u7387(%)\" style=\"width:100px\" type=\"number\" oninput=\"S.filterReviewStocks()\">";
    h += "  <button class=\"btn btn-sm btn-a\" onclick=\"S.doReviewRefresh()\">\u5237\u65b0\u6570\u636e</button>";
    h += "  <span id=\"reviewCount\" style=\"font-size:11px;color:var(--muted)\">\u5171 0 \u53ea</span></div>";

    h += "<div class=\"card\" style=\"padding:0;overflow-x:auto\">";
    h += "<table class=\"tbl\" id=\"reviewTable\"><thead><tr>";
    h += "<th>\u4ee3\u7801</th><th>\u540d\u79f0</th><th>\u6700\u65b0\u4ef7</th><th>\u6da8\u8dcc\u5e45%</th><th>\u6210\u4ea4\u989d(\u4ebf)</th><th>\u6362\u624b\u7387%</th><th>\u6240\u5c5e\u677f\u5757</th>";
    h += "</tr></thead><tbody id=\"reviewTbody\">";
    h += "<tr><td colspan=\"7\" style=\"text-align:center;color:var(--muted);padding:30px\">\u6b63\u5728\u52a0\u8f7d\u6570\u636e...</td></tr>";
    h += "</tbody></table></div>";
    return h;
  },

  doReviewRefresh: function() {
    var ts = document.getElementById("reviewTs");
    if (ts) ts.textContent = new Date().toLocaleTimeString();
    var self = this;
    fetch(S.server + "/api/review/stocks").then(function(r){return r.json();}).then(function(d){
      if (d.success && d.data) {
        S.reviewStocks = d.data;
        var src = document.getElementById("reviewSource");
        if (src && d.data_source) src.textContent = "\u6570\u636e\u6e90: " + d.data_source;
        S.filterReviewStocks();
      }
    }).catch(function(){});
  },

  filterReviewStocks: function() {
    var kw = ((document.getElementById("filterKeyword")||{}).value||"").trim().toUpperCase();
    var minAmt = parseFloat((document.getElementById("filterMinAmount")||{}).value)||0;
    var minTurn = parseFloat((document.getElementById("filterMinTurnover")||{}).value)||0;
    var filtered = [];
    for (var i=0;i<S.reviewStocks.length;i++) {
      var s = S.reviewStocks[i];
      if (kw && s.code.indexOf(kw)<0 && s.name.indexOf(kw)<0) continue;
      if (minAmt>0 && (s.amount||0)<minAmt) continue;
      if (minTurn>0 && (s.turnover||0)<minTurn) continue;
      filtered.push(s);
    }
    var ce = document.getElementById("reviewCount");
    if (ce) ce.textContent = "\u5171 "+filtered.length+" \u53ea";
    var tb = document.getElementById("reviewTbody");
    if (!tb) return;
    if (filtered.length===0) { tb.innerHTML = "<tr><td colspan=\"7\" style=\"text-align:center;color:var(--muted);padding:30px\">\u65e0\u5339\u914d\u6570\u636e</td></tr>"; return; }
    var h = "";
    for (var i=0;i<filtered.length;i++) {
      var s = filtered[i];
      var chg = s.change||0;
      var clr = chg>0 ? "var(--green)" : chg<0 ? "var(--red)" : "var(--muted)";
      h += "<tr><td>"+s.code+"</td><td>"+s.name+"</td><td>"+(s.price!==undefined?s.price.toFixed(2):"--")+"</td>"
        + "<td style=\"color:"+clr+"\">"+(chg>0?"+":"")+chg.toFixed(2)+"%</td>"
        + "<td>"+(s.amount!==undefined?s.amount.toFixed(1):"--")+"</td>"
        + "<td>"+(s.turnover!==undefined?s.turnover.toFixed(1):"--")+"</td>"
        + "<td>"+(s.sector||"--")+"</td></tr>";
    }
    tb.innerHTML = h;
  },

  generateReport: function() {
    var now = new Date();
    var ds = now.getFullYear()+"-"+(now.getMonth()+1).toString().padStart(2,"0")+"-"+now.getDate().toString().padStart(2,"0");
    var ts = now.getHours().toString().padStart(2,"0")+":"+now.getMinutes().toString().padStart(2,"0");
    var csv = "\u4ee3\u7801,\u540d\u79f0,\u6700\u65b0\u4ef7,\u6da8\u8dcc\u5e45(%),\u6210\u4ea4\u989d(\u4ebf),\u6362\u624b\u7387(%),\u6240\u5c5e\u677f\u5757\n";
    for (var i=0;i<S.reviewStocks.length;i++) {
      var s = S.reviewStocks[i];
      csv += s.code+","+s.name+","+(s.price||"")+","+((s.change||0).toFixed(2))+","+(s.amount||"")+","+(s.turnover||"")+","+(s.sector||"")+"\n";
    }
    var blob = new Blob(["\uFEFF"+csv], {type: "text/csv;charset=utf-8"});
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "\u590d\u76d8\u62a5\u544a_"+ds+"_"+ts+".csv";
    a.click();
    URL.revokeObjectURL(a.href);
  },
  startVolumePolling: function() {
    S.stopVolumePolling();
    S.doVolumeRefresh();
    S.volumeTimer = setInterval(function(){ S.doVolumeRefresh(); }, 300000);
  },
  stopVolumePolling: function() {
    if (S.volumeTimer) { clearInterval(S.volumeTimer); S.volumeTimer = null; }
  },
  doVolumeRefresh: function() {
    var ts = document.getElementById("volumeTs");
    if (ts) ts.textContent = new Date().toLocaleTimeString();
    var self = this;
    fetch(S.server + "/api/volume/monitor").then(function(r){return r.json();}).then(function(d){
      if (!d.success && !d.is_trading) return;
      var data = d.data || d;
      var isTrading = d.is_trading || data.is_trading || false;
      var todayList = data.today_list || d.today_list || [];
      var yesterdayList = data.yesterday_list || d.yesterday_list || [];
      S.volumeData = {today_list: todayList, yesterday_list: yesterdayList, is_trading: isTrading};
      var hint = document.getElementById("volumeHint");
      var status = document.getElementById("volumeStatus");
      if (hint) {
        var ds = d.data_status || data.data_status || "";
        if (ds === "live") { hint.style.display = "none"; }
        else if (ds === "close" || ds === "snapshot") { hint.style.display = "block"; hint.style.background = "rgba(90,101,153,.05)"; hint.textContent = "⚪ 收盘数据"; }
        else if (ds === "yesterday") { hint.style.display = "block"; hint.style.background = "rgba(79,140,255,.05)"; hint.textContent = "⚪ 昨日数据"; }
        else if (ds === "no_data" || ds === "fallback") { hint.style.display = "block"; hint.style.background = "rgba(255,176,32,.05)"; hint.textContent = "⚪ 暂无数据"; }
        else { hint.style.display = isTrading ? "none" : "block"; }
      }
      if (status) {
        var ds = d.data_status || data.data_status || "";
        if (ds === "live") {
          status.textContent = "🟢 实时";
          status.style.background = "rgba(0,212,170,.1)";
          status.style.color = "var(--green)";
        } else if (ds === "close" || ds === "snapshot" || ds === "yesterday") {
          status.textContent = "⚪ 收盘数据";
          status.style.background = "rgba(90,101,153,.1)";
          status.style.color = "var(--muted)";
        } else if (ds === "fallback" || ds === "no_data") {
          status.textContent = "⚪ 暂无数据";
          status.style.background = "rgba(255,176,32,.1)";
          status.style.color = "var(--yellow)";
        } else {
          status.textContent = "🟢 实时";
          status.style.background = "rgba(0,212,170,.1)";
          status.style.color = "var(--green)";
        }
      }
      S.filterVolumeStocks();
    }).catch(function(){});
  },
filterVolumeStocks: function() {
    var kw = ((document.getElementById("volFilterKeyword")||{}).value||"").trim().toUpperCase();
    var minRatio = parseFloat((document.getElementById("volFilterRatio")||{}).value)||0;
    var filtered = [];
    var combined = [];
    // 合并今日+昨日数据，今日置�?
    if (S.volumeData.today_list) {
      for (var t=0;t<S.volumeData.today_list.length;t++) {
        var s = S.volumeData.today_list[t];
        s._is_today = true;
        combined.push(s);
      }
    }
    if (S.volumeData.yesterday_list) {
      for (var y=0;y<S.volumeData.yesterday_list.length;y++) {
        var s = S.volumeData.yesterday_list[y];
        s._is_today = false;
        combined.push(s);
      }
    }
    // 去重（今日已触发的不再显示昨日数据）
    var seen = {};
    for (var i=0;i<combined.length;i++) {
      var s = combined[i];
      if (seen[s.code]) continue;
      seen[s.code] = true;
      if (kw && s.code.indexOf(kw)<0 && s.name.indexOf(kw)<0) continue;
      if (minRatio>0 && (s.ratio||0)<minRatio) continue;
      filtered.push(s);
    }
    var ce = document.getElementById("volumeCount");
    if (ce) ce.textContent = "\u5171 "+filtered.length+" \u53ea";
    var tb = document.getElementById("volumeTbody");
    if (!tb) return;
    if (filtered.length===0) { tb.innerHTML = "<tr><td colspan=\"8\" style=\"text-align:center;color:var(--muted);padding:30px\">\u65e0\u5339\u914d\u6570\u636e</td></tr>"; return; }
    var h = "";
    for (var i=0;i<filtered.length;i++) {
      var s = filtered[i];
      var chg = s.change||0;
      var clr = chg>0 ? "var(--green)" : chg<0 ? "var(--red)" : "var(--muted)";
      var ratioCls = (s.ratio||0)>=3 ? " style=\"color:var(--red);font-weight:700\"" : "";
      var todayTag = s._is_today ? "<span class=\"tag tag-r\" style=\"font-size:8px;margin-right:4px\">\u4eca\u65e5</span>" : "";
      h += "<tr onclick=\"S.toggleVolumeDetail(this,\u0027"+s.code+"\u0027)\">"
        + "<td>"+s.code+"</td><td>"+todayTag+s.name+"</td><td>"+(s.price!==undefined?s.price.toFixed(2):"--")+"</td>"
        + "<td style=\"color:"+clr+"\">"+(chg>0?"+":"")+chg.toFixed(2)+"%</td>"
        + "<td>"+(s.volume!==undefined?s.volume.toFixed(1):"--")+"</td>"
        + "<td"+ratioCls+">"+(s.ratio||"--")+"x</td>"
        + "<td>"+(s.sector||"--")+"</td>"
        + "<td>"+(s.trigger_time||"--")+"</td></tr>";
    }
    tb.innerHTML = h;
  },
  searchStock: function() {
    var inp = document.getElementById("reviewSearchInput");
    if (!inp) return;
    var kw = inp.value.trim();
    var dd = document.getElementById("reviewSearchDrop");
    if (!dd) return;
    if (kw.length < 1) { dd.style.display = "none"; return; }
    var self = this;
    if (S.staticMode) {
      fetch(S.apiUrl("stock/search")).then(function(r){return r.json();}).then(function(d){
        if (d.success && d.list) {
          var kwu = kw.toUpperCase();
          var filtered = d.list.filter(function(s){ return s.code.indexOf(kwu) >= 0 || (s.name || "").indexOf(kw) >= 0; }).slice(0, 20);
          var existing = {};
          if (S.reviewStocks) { for (var i=0;i<S.reviewStocks.length;i++) { existing[S.reviewStocks[i].code] = true; } }
          var hh = "<div style=\"position:absolute;top:0;left:0;background:var(--card);border:1px solid var(--border);border-radius:6px;max-height:200px;overflow-y:auto;z-index:100;width:300px\">";
          for (var i=0;i<filtered.length;i++) {
            var s = filtered[i];
            if (existing[s.code]) {
              hh += "<div style=\"display:flex;justify-content:space-between;padding:6px 10px;border-bottom:1px solid rgba(26,35,88,.3)\"><span>"+s.code+" "+s.name+"</span><span style=\"color:var(--muted);font-size:10px\"> \u5df2\u6dfb\u52a0</span></div>";
            } else {
              hh += '<div style="display:flex;justify-content:space-between;padding:6px 10px;border-bottom:1px solid rgba(26,35,88,.3)"><span>'+s.code+' '+s.name+'</span><button class="btn btn-xs btn-a" onclick="S.addToWatchlist(\u0027'+s.code+'\u0027)">\u6dfb\u52a0</button></div>';
            }
          }
          if (filtered.length === 0) { hh += "<div style=\"padding:6px 10px;color:var(--muted)\">\u65e0\u7b26\u5408\u6761\u4ef6\u7684\u80a1\u7968</div>"; }
          hh += "</div>";
          dd.innerHTML = hh;
          dd.style.display = "block";
        } else { dd.style.display = "none"; }
      }).catch(function(){ dd.style.display = "none"; });
    } else {
    var url = S.server + "/api/stock/search?keyword=" + encodeURIComponent(kw);
    fetch(url).then(function(r){return r.json();}).then(function(d){
      if (d.success && d.data && d.data.length > 0) {
        var existing = {};
        if (S.reviewStocks) { for (var i=0;i<S.reviewStocks.length;i++) { existing[S.reviewStocks[i].code] = true; } }
        var hh = "<div style=\"position:absolute;top:0;left:0;background:var(--card);border:1px solid var(--border);border-radius:6px;max-height:200px;overflow-y:auto;z-index:100;width:300px\">";
        for (var i=0;i<d.data.length;i++) {
          var s = d.data[i];
          if (existing[s.code]) {
            hh += "<div style=\"display:flex;justify-content:space-between;padding:6px 10px;border-bottom:1px solid rgba(26,35,88,.3)\"><span>"+s.code+" "+s.name+"</span><span style=\"color:var(--muted);font-size:10px\"> \u5df2\u6dfb\u52a0</span></div>";
          } else {
            hh += '<div style="display:flex;justify-content:space-between;padding:6px 10px;border-bottom:1px solid rgba(26,35,88,.3)"><span>'+s.code+' '+s.name+'</span><button class="btn btn-xs btn-a" onclick="S.addToWatchlist(\u0027'+s.code+'\u0027)">\u6dfb\u52a0</button></div>';
          }
        }
        hh += "</div>";
        dd.innerHTML = hh;
        dd.style.display = "block";
      } else { dd.style.display = "none"; }
    }).catch(function(){ dd.style.display = "none"; });
    }
  },  addToWatchlist: function(code, name) {
    var self = this;
    if (S.staticMode) {
      var wl = JSON.parse(localStorage.getItem("inv_watchlist") || "[]");
      if (wl.indexOf(code) < 0) { wl.push(code); localStorage.setItem("inv_watchlist", JSON.stringify(wl)); }
      S.doReviewRefresh();
    } else {
    fetch(S.server + "/api/review/watchlist/add?code=" + code).then(function(r){return r.json();}).then(function(d){ if (d.success) { S.doReviewRefresh(); } }).catch(function(){});
    }
    var dd = document.getElementById("reviewSearchDrop"); if (dd) dd.style.display = "none";
  },
  removeFromWatchlist: function(code) {
    if (!confirm("\u786e\u5b9a\u5220\u9664\u8be5\u80a1\u7968\u5417\uff1f")) return;
    var self = this;
    if (S.staticMode) {
      var wl = JSON.parse(localStorage.getItem("inv_watchlist") || "[]");
      var idx = wl.indexOf(code);
      if (idx >= 0) { wl.splice(idx, 1); localStorage.setItem("inv_watchlist", JSON.stringify(wl)); }
      S.doReviewRefresh();
    } else {
    fetch(S.server + "/api/review/watchlist/remove?code=" + code).then(function(r){return r.json();}).then(function(d){ if (d.success) { S.doReviewRefresh(); } }).catch(function(){});
    }
  },
};

document.addEventListener("DOMContentLoaded", function(){ S.init(); });
