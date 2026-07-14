/* ============================================================
   投资观察站 · 前端核心 v2.0
   Apple iOS 级动效 · anime.js 驱动
   ============================================================ */

// ===== Supabase Client (browser-side direct connection) =====
var supabaseClient = null;
(function () {
  if (typeof supabase !== 'undefined' && supabase.createClient) {
    try {
      supabaseClient = supabase.createClient(
        'https://clmfuugvprbrxdycczta.supabase.co',
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNsbWZ1dWd2cHJicnhkeWNjenRhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODM5NTIwNTAsImV4cCI6MjA5OTUyODA1MH0.iVMayRd41Gv6N4j9qa8m4OxhOI-vVg36_wYNKONGKac'
      );
    } catch (e) {
      console.warn('Supabase client init failed:', e);
    }
  }
})();

// ===== Translations =====
var T = {
  'nav.home': { zh: '四因子看板', en: 'Dashboard' },
  'nav.review': { zh: '复盘工具', en: 'Review' },
  'nav.volume': { zh: '量能监测', en: 'Volume' },
  'nav.industry': { zh: '产业逻辑', en: 'Industry' },
  'nav.review_summary': { zh: '盘后复盘', en: 'Post-Market' },
  'nav.history': { zh: '历史数据', en: 'History' },
  'app.title': { zh: '投资观察站', en: 'Investment Observatory' },
  'app.subtitle': { zh: '汕头游资专用', en: 'Shantou Trading Desk' },
  'status.online': { zh: '实时在线', en: 'Online' },
  'status.offline': { zh: '离线模式', en: 'Offline' },
  'btn.lang': { zh: 'EN', en: '中文' },
  'btn.refresh': { zh: '刷新数据', en: 'Refresh' },
  'home.rank_col': { zh: '排名', en: 'Rank' },
  'home.thread_col': { zh: '主线', en: 'Thread' },
  'home.stage_col': { zh: '阶段', en: 'Stage' },
  'home.score_col': { zh: '评分', en: 'Score' },
  'home.driver_col': { zh: '核心驱动', en: 'Driver' },
  'home.dur_col': { zh: '预期持续时间', en: 'Duration' },
  'home.action_col': { zh: '操作建议', en: 'Action' },
  'home.northbound': { zh: '北向资金(亿)', en: 'Northbound(100M)' },
  'comp.name': { zh: '名称', en: 'Name' },
  'comp.code': { zh: '代码', en: 'Code' },
  'comp.change': { zh: '涨跌', en: 'Change' },
  'comp.sector': { zh: '板块', en: 'Sector' },
  'comp.mcap': { zh: '市值(亿)', en: 'Mkt Cap(100M)' },
  'comp.search': { zh: '按名称或代码搜索...', en: 'Search by name or code...' },
  'comp.note': { zh: '数据需要点击刷新加载', en: 'Data loads on refresh.' },
  'close': { zh: '关闭', en: 'Close' },
  'history.title': { zh: '历史数据中心', en: 'Historical Data' },
};

// ===== Animation Engine (anime.js wrapper) =====
var A = {
  // Entrance: fade + slide up
  enter: function (el, delay, duration) {
    if (!el) return;
    if (typeof el === 'string') el = document.querySelector(el);
    if (!el) return;
    anime({
      targets: el,
      opacity: [0, 1],
      translateY: [16, 0],
      easing: 'easeOutExpo',
      duration: duration || 500,
      delay: delay || 0
    });
  },

  // Staggered children entrance
  stagger: function (container, selector, baseDelay) {
    if (!container) return;
    if (typeof container === 'string') container = document.querySelector(container);
    if (!container) return;
    var children = selector ? container.querySelectorAll(selector) : container.children;
    anime({
      targets: children,
      opacity: [0, 1],
      translateY: [16, 0],
      easing: 'easeOutExpo',
      duration: 500,
      delay: anime.stagger(60, { start: baseDelay || 0 })
    });
  },

  // Fade in only
  fadeIn: function (el, delay, duration) {
    if (!el) return;
    if (typeof el === 'string') el = document.querySelector(el);
    if (!el) return;
    anime({
      targets: el,
      opacity: [0, 1],
      easing: 'easeOutQuart',
      duration: duration || 300,
      delay: delay || 0
    });
  },

  // Scale in (for modals, cards)
  scaleIn: function (el, delay) {
    if (!el) return;
    if (typeof el === 'string') el = document.querySelector(el);
    if (!el) return;
    anime({
      targets: el,
      opacity: [0, 1],
      scale: [0.92, 1],
      translateY: [20, 0],
      easing: 'easeOutExpo',
      duration: 500,
      delay: delay || 0
    });
  },

  // Number rolling animation
  number: function (el, from, to, duration, suffix) {
    if (!el) return;
    if (typeof el === 'string') el = document.querySelector(el);
    if (!el) return;
    from = from === null || from === undefined ? 0 : Number(from);
    to = to === null || to === undefined ? 0 : Number(to);
    var obj = { val: from };
    anime({
      targets: obj,
      val: to,
      round: 1,
      easing: 'easeOutExpo',
      duration: duration || 800,
      update: function () {
        el.textContent = obj.val + (suffix || '');
      }
    });
  },

  // Number with decimal
  numberFloat: function (el, from, to, decimals, duration, suffix) {
    if (!el) return;
    if (typeof el === 'string') el = document.querySelector(el);
    if (!el) return;
    from = from === null || from === undefined ? 0 : Number(from);
    to = to === null || to === undefined ? 0 : Number(to);
    var obj = { val: from };
    var pow = Math.pow(10, decimals || 1);
    anime({
      targets: obj,
      val: to,
      easing: 'easeOutExpo',
      duration: duration || 800,
      update: function () {
        el.textContent = (Math.round(obj.val * pow) / pow).toFixed(decimals) + (suffix || '');
      }
    });
  },

  // Soft pulse to indicate live update
  pulse: function (el) {
    if (!el) return;
    if (typeof el === 'string') el = document.querySelector(el);
    if (!el) return;
    anime({
      targets: el,
      scale: [1, 1.02, 1],
      opacity: [1, 0.8, 1],
      easing: 'easeOutQuart',
      duration: 600
    });
  },

  // Flash background on value change
  flash: function (el) {
    if (!el) return;
    if (typeof el === 'string') el = document.querySelector(el);
    if (!el) return;
    el.classList.remove('flash-update');
    void el.offsetWidth; // reflow
    el.classList.add('flash-update');
    setTimeout(function () { el.classList.remove('flash-update'); }, 600);
  },

  // Button press feedback
  press: function (el) {
    if (!el) return;
    anime({
      targets: el,
      scale: [1, 0.96, 1],
      easing: 'easeOutBack(1.4)',
      duration: 180
    });
  },

  // Page content transition
  pageTransition: function (outEl, inEl) {
    if (!outEl || !inEl) return;
    anime({
      targets: outEl,
      opacity: [1, 0],
      translateY: [0, -8],
      easing: 'easeInQuart',
      duration: 200,
      complete: function () {
        anime({
          targets: inEl,
          opacity: [0, 1],
          translateY: [16, 0],
          easing: 'easeOutExpo',
          duration: 400
        });
      }
    });
  },

  // Tab indicator slide
  tabIndicator: function (indicator, targetEl, containerEl) {
    if (!indicator || !targetEl || !containerEl) return;
    var cRect = containerEl.getBoundingClientRect();
    var tRect = targetEl.getBoundingClientRect();
    anime({
      targets: indicator,
      left: tRect.left - cRect.left,
      width: tRect.width,
      easing: 'easeOutExpo',
      duration: 320
    });
  }
};

// ===== UI Helpers =====
var UI = {
  tag: function (text, type) {
    type = type || 'blue';
    return '<span class="tag tag-' + type + '">' + UI.escape(text) + '</span>';
  },

  tagWithDot: function (text, type) {
    type = type || 'blue';
    return '<span class="tag tag-' + type + '"><span class="tag-dot"></span>' + UI.escape(text) + '</span>';
  },

  metric: function (label, value, change, opts) {
    opts = opts || {};
    var valueClass = 'metric-value';
    if (opts.valueClass) valueClass += ' ' + opts.valueClass;
    var changeHtml = '';
    if (change !== undefined && change !== null && change !== '') {
      var changeClass = change > 0 ? 'up' : change < 0 ? 'down' : 'neutral';
      changeHtml = '<div class="metric-change ' + changeClass + '">' + (change > 0 ? '+' : '') + change + '</div>';
    }
    return '<div class="metric-card">' +
      '<div class="metric-label">' + UI.escape(label) + '</div>' +
      '<div class="' + valueClass + '" ' + (opts.id ? 'id="' + opts.id + '"' : '') + '>' + (value || '--') + '</div>' +
      changeHtml + '</div>';
  },

  card: function (title, content, opts) {
    opts = opts || {};
    var header = '';
    if (title) {
      header = '<div class="card-header">' +
        '<div class="card-title">' + title + '</div>' +
        (opts.headerAction || '') + '</div>';
    }
    return '<div class="card ' + (opts.className || '') + '"' + (opts.id ? ' id="' + opts.id + '"' : '') + '>' +
      header + content + '</div>';
  },

  tableWrap: function (headers, rowsHtml, opts) {
    opts = opts || {};
    var h = '<div class="table-wrap"' + (opts.id ? ' id="' + opts.id + '"' : '') + '><table><thead><tr>';
    for (var i = 0; i < headers.length; i++) {
      h += '<th>' + headers[i] + '</th>';
    }
    h += '</tr></thead><tbody>' + rowsHtml + '</tbody></table></div>';
    return h;
  },

  button: function (text, type, onclick, opts) {
    opts = opts || {};
    type = type || 'secondary';
    return '<button class="btn btn-' + type + ' ' + (opts.className || '') + '"' +
      ' onclick="A.press(this); ' + onclick + '"' +
      (opts.id ? ' id="' + opts.id + '"' : '') +
      (opts.title ? ' title="' + opts.title + '"' : '') + '>' + text + '</button>';
  },

  input: function (opts) {
    opts = opts || {};
    return '<input class="input ' + (opts.className || '') + '"' +
      ' type="' + (opts.type || 'text') + '"' +
      (opts.id ? ' id="' + opts.id + '"' : '') +
      (opts.placeholder ? ' placeholder="' + opts.placeholder + '"' : '') +
      (opts.value !== undefined ? ' value="' + opts.value + '"' : '') +
      (opts.oninput ? ' oninput="' + opts.oninput + '"' : '') +
      (opts.style ? ' style="' + opts.style + '"' : '') + '>';
  },

  tabs: function (items, activeKey, onchange) {
    var h = '<div class="tabs"' + (onchange ? ' onchange="' + onchange + '"' : '') + '>';
    h += '<div class="tab-indicator"></div>';
    for (var i = 0; i < items.length; i++) {
      var it = items[i];
      var active = it.key === activeKey ? ' active' : '';
      h += '<button class="tab' + active + '" data-tab="' + it.key + '" onclick="UI.switchTab(this, \'' + (onchange || '') + '\')">' + it.label + '</button>';
    }
    h += '</div>';
    return h;
  },

  switchTab: function (btn, onchange) {
    var container = btn.closest('.tabs');
    if (!container) return;
    var tabs = container.querySelectorAll('.tab');
    var indicator = container.querySelector('.tab-indicator');
    var key = btn.dataset.tab;
    tabs.forEach(function (t) { t.classList.remove('active'); });
    btn.classList.add('active');
    A.tabIndicator(indicator, btn, container);
    if (onchange) {
      try {
        var parts = onchange.split('.');
        var fn = window;
        for (var i = 0; i < parts.length; i++) {
          fn = fn[parts[i]];
          if (!fn) break;
        }
        if (typeof fn === 'function') {
          fn(key);
        }
      } catch (e) { console.error('switchTab callback:', e); }
    }
  },

  // Initialize tab indicator after render
  initTabs: function (container) {
    if (typeof container === 'string') container = document.querySelector(container);
    if (!container) return;
    var active = container.querySelector('.tab.active');
    var indicator = container.querySelector('.tab-indicator');
    if (active && indicator) {
      A.tabIndicator(indicator, active, container);
    }
  },

  escape: function (str) {
    if (str === null || str === undefined) return '';
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(String(str)));
    return div.innerHTML;
  },

  // Chinese market semantic color helpers
  upClass: function (val) {
    val = Number(val) || 0;
    return val > 0 ? 'up' : val < 0 ? 'down' : 'neutral';
  },

  upSign: function (val) {
    val = Number(val) || 0;
    return (val > 0 ? '+' : '') + val;
  }
};

// ===== App State & Logic =====
var S = {
  page: 'home',
  online: false,
  lastTs: '--',
  charts: {},
  lang: localStorage.getItem('inv_lang') || 'zh',
  server: '',
  reviewTimer: null,
  volumeTimer: null,
  volumeData: [],
  pollTimer: null,
  homeData: null,
  mode: 'trend',
  reviewStocks: [],
  _factorDetails: {},
  staticMode: false,
  supabaseAvailable: false,
  currentHistoryTab: 'factors',
  reviewSummaryData: null,
  currentReviewTab: 'tab1',

  _apiMap: {
    'ping': 'data/ping.json',
    'factors': 'data/factors.json',
    'factors/history': 'data/factors_history.json',
    'volume/monitor': 'data/volume_monitor.json',
    'review/summary': 'data/review_summary.json',
    'review/stocks': 'data/review_stocks.json',
    'stock/search': 'data/stock_search.json',
    'industry/chain': 'industry_chain_config.json',
    'history/factors': 'data/history_factors.json',
    'history/volume': 'data/history_volume.json',
    'history/snapshots': 'data/history_snapshots.json',
    'history/sectors': 'data/history_sectors.json'
  },

  apiUrl: function (path) {
    if (this.staticMode) {
      var mapped = this._apiMap[path] || ('data/' + path.replace(/\//g, '_') + '.json');
      return './' + mapped;
    }
    return this.server + '/api/' + path;
  },

  _escapeHtml: function (str) {
    if (!str) return '';
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
  },

  _debounce: function (fn, delay) {
    var timer = null;
    return function () {
      var ctx = this, args = arguments;
      clearTimeout(timer);
      timer = setTimeout(function () { fn.apply(ctx, args); }, delay);
    };
  },

  filterVolumeStocksDebounced: null,
  filterReviewStocksDebounced: null,

  _initDebounce: function () {
    if (!S.filterVolumeStocksDebounced) {
      S.filterVolumeStocksDebounced = S._debounce(function () { S.filterVolumeStocks(); }, 250);
    }
    if (!S.filterReviewStocksDebounced) {
      S.filterReviewStocksDebounced = S._debounce(function () { S.filterReviewStocks(); }, 250);
    }
  },

  t: function (k) {
    var e = T[k];
    return e ? (e[S.lang] || e.en || k) : k;
  },

  toggleLang: function () {
    S.lang = S.lang === 'zh' ? 'en' : 'zh';
    localStorage.setItem('inv_lang', S.lang);
    var b = document.getElementById('langBtn');
    if (b) b.textContent = S.lang === 'zh' ? 'EN' : '中文';
    S.nav(S.page);
  },

  init: function () {
    var self = this;
    S.server = window.location.protocol + '//' + window.location.host;
    if (window.location.hostname.indexOf('github.io') >= 0 || window.location.protocol === 'file:' || window.location.hostname.indexOf('pages.dev') >= 0) {
      S.staticMode = true;
    }

    var lb = document.getElementById('langBtn');
    if (lb) lb.textContent = S.lang === 'zh' ? 'EN' : '中文';

    var tb = document.getElementById('themeBtn');
    if (tb) {
      tb.addEventListener('click', function () {
        A.press(tb);
        document.body.classList.toggle('light-theme');
        localStorage.setItem('inv_theme', document.body.classList.contains('light-theme') ? 'light' : 'dark');
      });
      if (localStorage.getItem('inv_theme') === 'light') document.body.classList.add('light-theme');
    }

    if (lb) {
      lb.addEventListener('click', function () { S.toggleLang(); });
    }

    document.querySelectorAll('.nav-item, .mobile-nav-item').forEach(function (el) {
      el.addEventListener('click', function () { self.nav(el.dataset.page); });
    });

    S.nav('home');
    S._initDebounce();
    S.checkSupabaseStatus();

    if (S.staticMode) {
      if (S.supabaseAvailable) {
        S.setStatus('云端在线', '#22C55E');
        S.online = true;
      } else {
        S.setStatus('云端数据', '#378ADD');
      }
      S._pollMarketData();
      setTimeout(function () { S.refresh(); }, 100);
    } else {
      fetch(S.server + '/api/ping').then(function (r) { return r.json(); }).then(function (d) {
        if (d.status === 'ok') {
          S.online = true;
          S.setStatus('服务器在线', '#22C55E');
          S.lastTs = d.time;
          var ts = document.getElementById('ts');
          if (ts) ts.textContent = d.time;
          S.refresh();
        }
      }).catch(function () {
        S.setStatus('服务器离线', '#FF4D4F');
        S.refresh();
      });
    }

    setInterval(function () {
      if (!S.staticMode) {
        fetch(S.server + '/api/ping').then(function (r) { return r.json(); }).then(function (d) {
          if (d.status === 'ok') {
            S.online = true;
            S.setStatus('服务器在线', '#22C55E');
            var ts = document.getElementById('ts');
            if (ts) ts.textContent = d.time;
          }
        }).catch(function () {
          S.online = false;
          S.setStatus('服务器离线', '#FF4D4F');
        });
      } else if (S.supabaseAvailable) {
        S.setStatus('云端在线', '#22C55E');
        S._pollMarketData();
      }
      S.checkSupabaseStatus();
    }, 30000);
  },

  setStatus: function (txt, clr) {
    var st = document.getElementById('st');
    if (st) {
      st.textContent = txt;
      st.style.color = clr || '#64748B';
    }
    var icon = document.getElementById('dbIcon');
    if (icon) {
      icon.className = 'status-dot';
      if (clr === '#22C55E') icon.classList.add('online');
      else if (clr === '#FF4D4F') icon.classList.add('offline');
      else icon.classList.add('idle');
    }
  },

  _marketDataCache: null,
  _lastMarketFetch: 0,

  _pollMarketData: function () {
    var now = Date.now();
    if (now - S._lastMarketFetch < 60000) return;
    S._lastMarketFetch = now;
    var tsEl = document.getElementById('ts');
    var nowStr = new Date().toTimeString().substring(0, 8);
    try {
      var script = document.createElement('script');
      var callbackName = '_sinaCb' + now;
      window[callbackName] = function (data) {
        try {
          var indices = [];
          var names = { sh000001: '上证指数', sz399001: '深证成指', sz399006: '创业板指' };
          for (var i = 0; i < data.length; i++) {
            var parts = data[i].split(',');
            if (parts.length > 3) {
              indices.push({
                name: names[parts[0]] || parts[0],
                price: parseFloat(parts[3]),
                change: parseFloat(parts[3]) - parseFloat(parts[2]),
                changePct: ((parseFloat(parts[3]) - parseFloat(parts[2])) / parseFloat(parts[2]) * 100).toFixed(2)
              });
            }
          }
          S._marketDataCache = { indices: indices, ts: nowStr };
          if (tsEl) tsEl.textContent = nowStr;
          S._updateMarketDisplay();
        } catch (e) {
          if (tsEl) tsEl.textContent = nowStr;
        }
        delete window[callbackName];
      };
      script.src = 'https://hq.sinajs.cn/list=sh000001,sz399001,sz399006&_=' + now;
      script.onerror = function () {
        if (tsEl) tsEl.textContent = nowStr;
        delete window[callbackName];
      };
      document.head.appendChild(script);
      setTimeout(function () { if (script.parentNode) script.parentNode.removeChild(script); }, 2000);
    } catch (e) {
      if (tsEl) tsEl.textContent = nowStr;
    }
  },

  _updateMarketDisplay: function () {
    if (!S._marketDataCache || !S._marketDataCache.indices) return;
    var indices = S._marketDataCache.indices;
    var sourceLabel = document.getElementById('dataSourceLabel');
    if (sourceLabel) {
      var tag = indices.length > 0 ? '实时指数' : '云端缓存';
      var cls = indices.length > 0 ? 'tag tag-green' : 'tag tag-blue';
      sourceLabel.className = cls;
      sourceLabel.innerHTML = '<span class="tag-dot"></span>' + tag;
    }
    var homeTs = document.getElementById('homeTs');
    if (homeTs && S._marketDataCache) {
      homeTs.textContent = '更新: ' + S._marketDataCache.ts;
    }
  },

  nav: function (p) {
    // Dispose ECharts instances before destroying DOM
    for (var key in S.charts) {
      if (S.charts[key] && S.charts[key].dispose) { S.charts[key].dispose(); }
    }
    S.charts = {};
    S.page = p;

    document.querySelectorAll('.nav-item, .mobile-nav-item').forEach(function (n) { n.classList.remove('active'); });
    var el = document.querySelector('.nav-item[data-page="' + p + '"]');
    if (el) el.classList.add('active');
    var mel = document.querySelector('.mobile-nav-item[data-page="' + p + '"]');
    if (mel) mel.classList.add('active');

    var pageTitle = document.getElementById('pageTitle');
    var pageSubtitle = document.getElementById('pageSubtitle');
    var titles = {
      home: ['四因子看板', '实时监控市场情绪、流动性、周期与龙头'],
      industry: ['产业逻辑', '产业链上下游关系与景气度追踪'],
      review: ['复盘工具', '盘后个股诊断与数据筛选'],
      volume: ['量能监测', '实时成交量异常监控'],
      review_summary: ['盘后复盘', '结构化复盘与次日作战计划'],
      history: ['历史数据', '因子趋势与历史行情回溯']
    };
    if (pageTitle) pageTitle.textContent = titles[p] ? titles[p][0] : '';
    if (pageSubtitle) pageSubtitle.textContent = titles[p] ? titles[p][1] : '';

    var fn = S['R_' + p];
    var content = document.getElementById('mainContent');
    var headerActions = document.getElementById('headerActions');
    if (headerActions) headerActions.innerHTML = '';

    if (fn && content) {
      content.innerHTML = fn();
      S.afterRender(p);
    }

    // Animate page entrance
    A.fadeIn('#mainContent', 50, 300);
    A.stagger('#mainContent', '.card, .metric-card, .score-card, .table-wrap', 80);
  },

  afterRender: function (p) {
    S.stopPolling();
    S.stopReviewPolling();
    S.stopVolumePolling();
    if (p === 'home') {
      setTimeout(function () { S.renderSentimentTrend(); }, 300);
      S.startPolling();
    } else if (p === 'industry') {
      setTimeout(function () { S.renderIndustryChain(); }, 300);
    } else if (p === 'volume') {
      setTimeout(function () { S.startVolumePolling(); }, 300);
    } else if (p === 'review_summary') {
      setTimeout(function () { S.loadReviewSummary(); }, 200);
    } else if (p === 'history') {
      S.checkSupabaseStatus();
      setTimeout(function () { S.setDefaultHistoryDates(); }, 300);
    }
  },

  startPolling: function () {
    S.stopPolling();
    S.pollTimer = setInterval(function () { S.refresh(); }, 10000);
  },
  stopPolling: function () {
    if (S.pollTimer) { clearInterval(S.pollTimer); S.pollTimer = null; }
  },
  startReviewPolling: function () {
    S.stopReviewPolling();
    S.doReviewRefresh();
    S.reviewTimer = setInterval(function () { S.doReviewRefresh(); }, 10000);
  },
  stopReviewPolling: function () {
    if (S.reviewTimer) { clearInterval(S.reviewTimer); S.reviewTimer = null; }
  },
  stopVolumePolling: function () {
    if (S.volumeTimer) { clearInterval(S.volumeTimer); S.volumeTimer = null; }
  },

  refresh: function () {
    if (S.page === 'home') {
      fetch(S.apiUrl('factors')).then(function (r) { return r.json(); }).then(function (d) {
        S.updateHomeData(d);
      }).catch(function (e) { console.error('refresh factors failed', e); });
      fetch(S.apiUrl('factors/history')).then(function (r) { return r.json(); }).then(function (d) {
        if (d.success && d.data) S.renderSentimentTrend(d.data);
      }).catch(function (e) { console.error('refresh history failed', e); });
    }
    var rb = document.getElementById('refreshBtn');
    if (rb) {
      rb.classList.add('spinning');
      setTimeout(function () { rb.classList.remove('spinning'); }, 1000);
    }
  },

  switchMode: function (m) {
    S.mode = m;
    localStorage.setItem('inv_mode', m);
    var t = document.getElementById('modeTrend');
    var d = document.getElementById('modeDragon');
    if (t) t.className = 'btn btn-sm ' + (m === 'trend' ? 'btn-primary' : 'btn-secondary');
    if (d) d.className = 'btn btn-sm ' + (m === 'dragon' ? 'btn-primary' : 'btn-secondary');
    var ml = document.getElementById('modeLabel');
    if (ml) ml.textContent = '当前模式: ' + (m === 'trend' ? '趋势波段' : '龙头打板');
    if (S.homeData) S.updateHomeData(S.homeData);
  },

  // ===== HOME PAGE =====
  R_home: function () {
    var mode = S.mode || 'trend';
    var h = '';

    // Header actions: mode toggle + data source badge
    var headerActions = document.getElementById('headerActions');
    if (headerActions) {
      headerActions.innerHTML =
        '<div class="btn-group">' +
        '<button id="modeTrend" class="btn btn-sm ' + (mode === 'trend' ? 'active' : '') + '" onclick="S.switchMode(\'trend\')">趋势波段</button>' +
        '<button id="modeDragon" class="btn btn-sm ' + (mode === 'dragon' ? 'active' : '') + '" onclick="S.switchMode(\'dragon\')">龙头打板</button>' +
        '</div>' +
        '<span id="dataSourceLabel" class="tag tag-gray"><span class="tag-dot"></span>查询中...</span>' +
        '<span id="homeTs" class="text-sm text-tertiary text-tabular">--</span>';
    }

    h += '<div class="dashboard-grid">';

    // Left: Hero score card
    h += '<div class="score-card">' +
      '<div class="score-label">综合概率分</div>' +
      '<div class="score-value" id="compositeScore" style="color:var(--accent-light)">--</div>' +
      '<div id="liveBadge" class="score-badges"></div>' +
      '<div class="score-desc" id="outlookText">等待数据...</div>' +
      '<div id="compChange" class="text-sm text-secondary mt-3"></div>' +
      '<div class="score-badges" id="posRiskBadges"></div>' +
      '<div id="coreAction" class="text-sm text-accent mt-3" style="border-top:1px solid var(--glass-border);padding-top:var(--space-3)"></div>' +
      '<div id="forbiddenAction" class="text-xs text-up mt-2"></div>' +
      '</div>';

    // Right column
    h += '<div class="flex-col gap-4">';

    // Metrics grid
    h += '<div class="dashboard-metrics">';
    var mets = [
      ['limitUp', '涨停数'],
      ['limitDown', '跌停数'],
      ['bombRate', '炸板率'],
      ['turnover', '成交额(亿)'],
      ['northBound', '北向资金(亿)'],
      ['maxBoard', '最高连板']
    ];
    for (var i = 0; i < mets.length; i++) {
      h += '<div class="metric-card">' +
        '<div class="metric-label">' + mets[i][1] + '</div>' +
        '<div class="metric-value" id="' + mets[i][0] + '">--</div>' +
        '<div class="metric-change neutral" id="' + mets[i][0] + '_prev">--</div>' +
        '</div>';
    }
    h += '</div>';

    // Four factors
    h += '<div class="factor-grid">';
    var facs = [['sentiment', '情绪周期', '35%'], ['sector', '板块联动', '30%'], ['chip', '筹码结构', '20%'], ['overnight', '隔夜预期', '15%']];
    for (var i = 0; i < facs.length; i++) {
      var f = facs[i];
      h += '<div class="card pressed" id="fc_' + f[0] + '" onclick="S.toggleFactorDetail(\'' + f[0] + '\')">' +
        '<div class="card-header" style="margin-bottom:var(--space-3)">' +
        '<div class="card-title">' + f[1] + ' <span id="ftag_' + f[0] + '">' + UI.tag('等待') + '</span></div>' +
        '<div class="text-xs text-tertiary">权重 ' + f[2] + '</div>' +
        '</div>' +
        '<div class="flex items-center justify-between mb-3">' +
        '<div class="metric-value" style="font-size:var(--text-3xl)" id="fscore_' + f[0] + '">--</div>' +
        '<div class="text-sm text-secondary" id="faction_' + f[0] + '"></div>' +
        '</div>' +
        '<div class="text-sm text-secondary mb-3" id="fdesc_' + f[0] + '">等待数据...</div>' +
        '<div class="progress"><div class="progress-fill" id="fbar_' + f[0] + '" style="width:0%"></div></div>' +
        '<div id="fdetail_' + f[0] + '" style="display:none;margin-top:var(--space-3);padding-top:var(--space-3);border-top:1px solid var(--glass-border);font-size:var(--text-sm);color:var(--text-secondary)"></div>' +
        '</div>';
    }
    h += '</div>';

    // Constraint chain
    h += UI.card('递进约束传导', '<div id="constraintChain" class="flex items-center gap-2 flex-wrap text-sm"></div><div id="constraintDesc" class="text-sm text-secondary mt-3"></div>', { className: 'card-flat' });

    // Sentiment chart
    h += UI.card('情绪趋势图', '<div id="sentimentChart" class="chart-container" style="height:280px"></div>', { className: 'chart-card' });

    h += '</div></div>';
    h += '<div class="text-xs text-tertiary text-center mt-6">基于当前实时数据前瞻推演，不构成投资建议 | 数据刷新周期 10 秒</div>';
    return h;
  },

  toggleFactorDetail: function (id) {
    var el = document.getElementById('fdetail_' + id);
    if (!el) return;
    S._factorDetails[id] = !S._factorDetails[id];
    if (S._factorDetails[id]) {
      el.style.display = 'block';
      A.enter(el, 0, 200);
    } else {
      el.style.display = 'none';
    }
  },

  updateHomeData: function (d) {
    S.homeData = d;

    var dsl = document.getElementById('dataSourceLabel');
    if (dsl) {
      if (d.is_live) {
        dsl.innerHTML = '<span class="tag-dot"></span>实时';
        dsl.className = 'tag tag-green';
      } else {
        dsl.innerHTML = '<span class="tag-dot"></span>收盘数据';
        dsl.className = 'tag tag-gray';
      }
    }

    var ts = document.getElementById('homeTs');
    if (ts && d.ts) ts.textContent = d.ts;

    var score = d.composite;
    var cs = document.getElementById('compositeScore');
    if (cs && score !== null && score !== undefined) {
      var scoreColor = score >= 75 ? 'var(--down)' : score >= 55 ? 'var(--warn)' : 'var(--up)';
      cs.style.color = scoreColor;
      A.number(cs, Number(cs.textContent) || 0, Math.round(score), 800);
      A.pulse(cs);
    }

    var lb = document.getElementById('liveBadge');
    if (lb) {
      lb.innerHTML = d.is_live ? UI.tagWithDot('实时', 'green') : UI.tagWithDot('昨收', 'blue');
    }

    var cc = document.getElementById('compChange');
    if (cc) {
      if (d.prev_day && d.prev_day.composite_score !== null && d.prev_day.composite_score !== undefined && score !== null && score !== undefined) {
        var diff = score - d.prev_day.composite_score;
        var arrow = diff > 0 ? '↑' : diff < 0 ? '↓' : '→';
        var cl = diff > 0 ? 'text-down' : diff < 0 ? 'text-up' : 'text-secondary';
        cc.innerHTML = '<span class="text-tertiary">较昨日</span> <span class="' + cl + '">' + (diff > 0 ? '+' : '') + Math.round(diff) + '分 ' + arrow + '</span>';
      } else {
        cc.textContent = '';
      }
    }

    var ot = document.getElementById('outlookText');
    if (ot && d.outlook_desc) ot.textContent = d.outlook_desc;

    var posBadge = '', riskBadge = '', core = '', forbid = '';
    if (score !== null && score !== undefined) {
      var pos = score >= 75 ? '重仓(≤80%)' : score >= 55 ? '半仓(≤50%)' : score >= 40 ? '轻仓(≤30%)' : '空仓观望';
      var risk = score >= 75 ? '低风险' : score >= 55 ? '中等风险' : score >= 40 ? '较高风险' : '高风险';
      var posType = score >= 55 ? 'green' : score >= 40 ? 'yellow' : 'red';
      var riskType = score >= 75 ? 'green' : score >= 55 ? 'yellow' : 'red';
      posBadge = UI.tag('仓位: ' + pos, posType);
      riskBadge = UI.tag('风险: ' + risk, riskType);
    }
    if (d.advice) {
      if (d.advice.core_action) core = '核心操作: ' + d.advice.core_action;
      if (d.advice.forbidden) forbid = '禁忌: ' + d.advice.forbidden;
    }
    var prb = document.getElementById('posRiskBadges');
    if (prb) prb.innerHTML = posBadge + riskBadge;
    var ca = document.getElementById('coreAction');
    if (ca) ca.textContent = core;
    var fa = document.getElementById('forbiddenAction');
    if (fa) fa.textContent = forbid;

    if (d.market) {
      var m = d.market;
      var p = d.prev_day ? d.prev_day.market : null;
      var setVal = function (id, val) {
        var el = document.getElementById(id);
        if (el) el.textContent = (val !== null && val !== undefined) ? val : '--';
      };
      setVal('limitUp', m.limit_up_count);
      setVal('limitDown', m.limit_down_count);
      setVal('bombRate', m.bomb_rate !== undefined ? m.bomb_rate.toFixed(1) + '%' : '--');
      setVal('turnover', m.turnover_total !== undefined ? Number(m.turnover_total).toFixed(1) : '--');
      setVal('northBound', m.northbound_net !== undefined ? Number(m.northbound_net).toFixed(1) : '--');
      setVal('maxBoard', m.max_board_height);

      var setCmp = function (id, todayVal, prevVal, suffix) {
        var el = document.getElementById(id + '_prev');
        if (!el) return;
        if (prevVal === null || prevVal === undefined || prevVal === '--') { el.textContent = '--'; el.className = 'metric-change neutral'; return; }
        if (todayVal === null || todayVal === undefined || todayVal === '--') { el.textContent = ''; return; }
        suffix = suffix || '';
        var diff = todayVal - prevVal;
        var arrow = diff > 0 ? '↑' : diff < 0 ? '↓' : '→';
        var diffStr = (diff > 0 ? '+' : '') + Number(diff).toFixed(diff % 1 === 0 ? 0 : 1);
        el.textContent = '昨' + prevVal + suffix + ' ' + diffStr + arrow;
        el.className = 'metric-change ' + (diff > 0 ? 'up' : diff < 0 ? 'down' : 'neutral');
      };
      if (p) {
        setCmp('limitUp', m.limit_up_count, p.limit_up_count, '');
        setCmp('limitDown', m.limit_down_count, p.limit_down_count, '');
        setCmp('bombRate', m.bomb_rate, p.bomb_rate, '%');
        setCmp('turnover', m.turnover_total, p.turnover_total, '');
        setCmp('northBound', m.northbound_net, p.northbound_net, '');
        setCmp('maxBoard', m.max_board_height, p.max_board_height, '');
      }
    }

    if (d.factors) {
      for (var i = 0; i < d.factors.length; i++) {
        var f = d.factors[i];
        var fid = f.id;
        var fs = document.getElementById('fscore_' + fid);
        var fd = document.getElementById('fdesc_' + fid);
        var ft = document.getElementById('ftag_' + fid);
        var fb = document.getElementById('fbar_' + fid);
        var fa = document.getElementById('faction_' + fid);
        if (fs && f.score !== null && f.score !== undefined) {
          var fColor = f.score >= 70 ? 'var(--down)' : f.score >= 40 ? 'var(--warn)' : 'var(--up)';
          fs.style.color = fColor;
          A.number(fs, Number(fs.textContent) || 0, Math.round(f.score), 600);
          if (fb) {
            fb.style.width = f.score + '%';
            fb.style.background = fColor;
          }
        }
        if (fd) fd.textContent = f.detail && f.detail.desc ? f.detail.desc : '--';
        if (ft) {
          if (f.score !== null && f.score !== undefined) {
            var lvl = f.score >= 70 ? '强' : f.score >= 40 ? '中' : '弱';
            var type = f.score >= 70 ? 'green' : f.score >= 40 ? 'yellow' : 'red';
            ft.innerHTML = UI.tag(lvl, type);
          } else {
            ft.innerHTML = UI.tag('待更新', 'blue');
          }
        }
        if (fa && d.advice && d.advice.factor_advice && d.advice.factor_advice[fid]) {
          fa.textContent = d.advice.factor_advice[fid];
        }
        var fdet = document.getElementById('fdetail_' + fid);
        if (fdet && f.detail && f.detail.detail && f.detail.detail.scores) {
          var dh = '';
          var dd = f.detail.detail;
          if (dd.scores) {
            for (var sk in dd.scores) {
              dh += '<div class="flex justify-between" style="padding:2px 0"><span>' + sk + '</span><span class="text-tabular">' + dd.scores[sk] + '</span></div>';
            }
          }
          fdet.innerHTML = dh;
        }
      }
    }

    var chain = document.getElementById('constraintChain');
    if (chain) {
      var cols = ['var(--accent-light)', 'var(--down)', 'var(--warn)', 'var(--info)'];
      var nms = ['情绪', '板块', '筹码', '隔夜'];
      var ch = '';
      for (var i = 0; i < nms.length; i++) {
        ch += '<span style="display:inline-flex;align-items:center;gap:4px;padding:4px 10px;border-radius:var(--radius-pill);background:var(--glass);border:1px solid var(--glass-border);font-size:var(--text-xs);color:' + cols[i] + '">' + nms[i] + '</span>';
        if (i < nms.length - 1) ch += '<span style="color:var(--text-tertiary)">→</span>';
      }
      chain.innerHTML = ch;
    }
    var cdesc = document.getElementById('constraintDesc');
    if (cdesc) cdesc.textContent = '情绪→板块→筹码→隔夜，约束逐级传导。任一环节走弱将压制整体评分。';
  },

  // ===== VOLUME PAGE =====
  R_volume: function () {
    var headerActions = document.getElementById('headerActions');
    if (headerActions) {
      headerActions.innerHTML =
        '<span id="volumeStatus" class="tag tag-blue">加载中...</span>' +
        '<span id="volumeTs" class="text-sm text-tertiary text-tabular">--</span>';
    }
    var h = '';
    h += '<div class="flex items-center gap-3 mb-4 flex-wrap">';
    h += UI.input({ id: 'volFilterKeyword', placeholder: '代码/名称', style: 'width:140px', oninput: 'S.filterVolumeStocksDebounced()' });
    h += UI.input({ id: 'volFilterRatio', type: 'number', placeholder: '最低放量倍数', style: 'width:140px', oninput: 'S.filterVolumeStocksDebounced()' });
    h += UI.button('刷新数据', 'primary', 'S.doVolumeRefresh()');
    h += '<span id="volumeCount" class="text-sm text-tertiary">加载中...</span>';
    h += '</div>';

    h += UI.tableWrap(
      ['代码', '名称', '最新价', '涨跌幅%', '成交量(万手)', '放量倍数', '所属板块', '触发时间'],
      '<tr><td colspan="8" style="text-align:center;padding:40px;color:var(--text-tertiary)">加载中...</td></tr>',
      { id: 'volumeTable' }
    );

    h += '<div class="text-xs text-tertiary mt-3">放量倍数 = 当日成交量 / 前5日最小单日成交量 | 放量超过3倍高亮显示 | 今日触发的股票置顶显示</div>';

    h += '<div id="volumeHint" class="alert alert-yellow mt-4 hidden"></div>';
    return h;
  },

  doVolumeRefresh: function () {
    var ts = document.getElementById('volumeTs');
    if (ts) ts.textContent = new Date().toLocaleTimeString();
    fetch(S.apiUrl('volume/monitor')).then(function (r) { return r.json(); }).then(function (d) {
      if (!d.success && !d.is_trading) return;
      var data = d.data || d;
      var isTrading = d.is_trading || data.is_trading || false;
      var todayList = data.today_list || d.today_list || [];
      var yesterdayList = data.yesterday_list || d.yesterday_list || [];
      S.volumeData = { today_list: todayList, yesterday_list: yesterdayList, is_trading: isTrading };

      var hint = document.getElementById('volumeHint');
      var status = document.getElementById('volumeStatus');
      var ds = d.data_status || data.data_status || '';
      if (hint) {
        hint.classList.remove('hidden');
        if (ds === 'live') { hint.classList.add('hidden'); }
        else if (ds === 'close' || ds === 'snapshot') { hint.className = 'alert alert-yellow mt-4'; hint.textContent = '⚪ 收盘数据'; }
        else if (ds === 'yesterday') { hint.className = 'alert alert-blue mt-4'; hint.textContent = '⚪ 昨日数据'; }
        else if (ds === 'no_data' || ds === 'fallback') { hint.className = 'alert alert-yellow mt-4'; hint.textContent = '⚪ 暂无数据'; }
        else { hint.classList.add('hidden'); }
      }
      if (status) {
        if (ds === 'live') { status.className = 'tag tag-green'; status.innerHTML = '<span class="tag-dot"></span>实时'; }
        else if (ds === 'close' || ds === 'snapshot' || ds === 'yesterday') { status.className = 'tag tag-gray'; status.innerHTML = '<span class="tag-dot"></span>收盘数据'; }
        else if (ds === 'fallback' || ds === 'no_data') { status.className = 'tag tag-yellow'; status.innerHTML = '<span class="tag-dot"></span>暂无数据'; }
        else { status.className = 'tag tag-green'; status.innerHTML = '<span class="tag-dot"></span>实时'; }
      }
      S.filterVolumeStocks();
    }).catch(function (e) { console.error('fetch error', e); });
  },

  filterVolumeStocks: function () {
    var kw = ((document.getElementById('volFilterKeyword') || {}).value || '').trim().toUpperCase();
    var minRatio = parseFloat((document.getElementById('volFilterRatio') || {}).value) || 0;
    var filtered = [];
    var combined = [];
    if (S.volumeData.today_list) {
      for (var t = 0; t < S.volumeData.today_list.length; t++) {
        var s = S.volumeData.today_list[t];
        s._is_today = true;
        combined.push(s);
      }
    }
    if (S.volumeData.yesterday_list) {
      for (var y = 0; y < S.volumeData.yesterday_list.length; y++) {
        var s = S.volumeData.yesterday_list[y];
        s._is_today = false;
        combined.push(s);
      }
    }
    var seen = {};
    for (var i = 0; i < combined.length; i++) {
      var s = combined[i];
      if (seen[s.code]) continue;
      seen[s.code] = true;
      if (kw && s.code.indexOf(kw) < 0 && s.name.indexOf(kw) < 0) continue;
      if (minRatio > 0 && (s.ratio || 0) < minRatio) continue;
      filtered.push(s);
    }
    var ce = document.getElementById('volumeCount');
    if (ce) ce.textContent = '共 ' + filtered.length + ' 只';

    var table = document.getElementById('volumeTable');
    if (!table) return;
    var tb = table.querySelector('tbody');
    if (!tb) return;
    if (filtered.length === 0) {
      tb.innerHTML = '<tr><td colspan="8" style="text-align:center;padding:40px;color:var(--text-tertiary)">无匹配数据</td></tr>';
      return;
    }
    var h = '';
    for (var i = 0; i < filtered.length; i++) {
      var s = filtered[i];
      var chg = s.change || 0;
      var cl = chg > 0 ? 'up' : chg < 0 ? 'down' : 'neutral';
      var ratioClass = (s.ratio || 0) >= 3 ? 'up' : 'neutral';
      var todayTag = s._is_today ? UI.tag('今日', 'red') : '';
      h += '<tr>' +
        '<td>' + s.code + '</td>' +
        '<td>' + todayTag + UI.escape(s.name) + '</td>' +
        '<td class="num">' + (s.price !== undefined ? s.price.toFixed(2) : '--') + '</td>' +
        '<td class="num ' + cl + '">' + (chg > 0 ? '+' : '') + chg.toFixed(2) + '%</td>' +
        '<td class="num">' + (s.volume !== undefined ? s.volume.toFixed(1) : '--') + '</td>' +
        '<td class="num ' + ratioClass + '">' + (s.ratio || '--') + 'x</td>' +
        '<td>' + (s.sector || '--') + '</td>' +
        '<td>' + (s.trigger_time || '--') + '</td>' +
        '</tr>';
    }
    tb.innerHTML = h;
    A.stagger(tb, 'tr', 0);
  },

  toggleVolumeDetail: function (tr, code) {
    // Placeholder for future detail expansion
  },

  // ===== REVIEW PAGE =====
  R_review: function () {
    var headerActions = document.getElementById('headerActions');
    if (headerActions) {
      headerActions.innerHTML =
        '<span id="reviewSource" class="text-sm text-tertiary"></span>' +
        '<span id="reviewTs" class="text-sm text-tertiary text-tabular">--</span>' +
        UI.button('生成报告', 'primary', 'S.generateReport()');
    }
    var h = '<div class="flex items-center gap-3 mb-4 flex-wrap">';
    h += UI.input({ id: 'filterKeyword', placeholder: '代码/名称', style: 'width:140px', oninput: 'S.filterReviewStocksDebounced()' });
    h += UI.input({ id: 'filterMinAmount', type: 'number', placeholder: '最低成交额(亿)', style: 'width:140px', oninput: 'S.filterReviewStocksDebounced()' });
    h += UI.input({ id: 'filterMinTurnover', type: 'number', placeholder: '最低换手率(%)', style: 'width:140px', oninput: 'S.filterReviewStocksDebounced()' });
    h += UI.button('刷新数据', 'primary', 'S.doReviewRefresh()');
    h += '<span id="reviewCount" class="text-sm text-tertiary">共 0 只</span>';
    h += '</div>';

    h += UI.tableWrap(
      ['代码', '名称', '最新价', '涨跌幅%', '成交额(亿)', '换手率%', '所属板块'],
      '<tr><td colspan="7" style="text-align:center;padding:40px;color:var(--text-tertiary)">正在加载数据...</td></tr>',
      { id: 'reviewTable' }
    );
    return h;
  },

  doReviewRefresh: function () {
    var ts = document.getElementById('reviewTs');
    if (ts) ts.textContent = new Date().toLocaleTimeString();
    fetch(S.apiUrl('review/stocks')).then(function (r) { return r.json(); }).then(function (d) {
      if (d.success && d.data) {
        S.reviewStocks = d.data;
        var src = document.getElementById('reviewSource');
        if (src && d.data_source) src.textContent = '数据源: ' + d.data_source;
        S.filterReviewStocks();
      }
    }).catch(function (e) { console.error('fetch error', e); });
  },

  filterReviewStocks: function () {
    var kw = ((document.getElementById('filterKeyword') || {}).value || '').trim().toUpperCase();
    var minAmt = parseFloat((document.getElementById('filterMinAmount') || {}).value) || 0;
    var minTurn = parseFloat((document.getElementById('filterMinTurnover') || {}).value) || 0;
    var filtered = [];
    for (var i = 0; i < S.reviewStocks.length; i++) {
      var s = S.reviewStocks[i];
      if (kw && s.code.indexOf(kw) < 0 && s.name.indexOf(kw) < 0) continue;
      if (minAmt > 0 && (s.amount || 0) < minAmt) continue;
      if (minTurn > 0 && (s.turnover || 0) < minTurn) continue;
      filtered.push(s);
    }
    var ce = document.getElementById('reviewCount');
    if (ce) ce.textContent = '共 ' + filtered.length + ' 只';

    var table = document.getElementById('reviewTable');
    if (!table) return;
    var tb = table.querySelector('tbody');
    if (!tb) return;
    if (filtered.length === 0) {
      tb.innerHTML = '<tr><td colspan="7" style="text-align:center;padding:40px;color:var(--text-tertiary)">无匹配数据</td></tr>';
      return;
    }
    var h = '';
    for (var i = 0; i < filtered.length; i++) {
      var s = filtered[i];
      var chg = s.change || 0;
      var cl = chg > 0 ? 'up' : chg < 0 ? 'down' : 'neutral';
      h += '<tr>' +
        '<td>' + s.code + '</td>' +
        '<td>' + UI.escape(s.name) + '</td>' +
        '<td class="num">' + (s.price !== undefined ? s.price.toFixed(2) : '--') + '</td>' +
        '<td class="num ' + cl + '">' + (chg > 0 ? '+' : '') + chg.toFixed(2) + '%</td>' +
        '<td class="num">' + (s.amount !== undefined ? s.amount.toFixed(1) : '--') + '</td>' +
        '<td class="num">' + (s.turnover !== undefined ? s.turnover.toFixed(1) : '--') + '</td>' +
        '<td>' + (s.sector || '--') + '</td>' +
        '</tr>';
    }
    tb.innerHTML = h;
    A.stagger(tb, 'tr', 0);
  },

  generateReport: function () {
    var now = new Date();
    var ds = now.getFullYear() + '-' + (now.getMonth() + 1).toString().padStart(2, '0') + '-' + now.getDate().toString().padStart(2, '0');
    var ts = now.getHours().toString().padStart(2, '0') + ':' + now.getMinutes().toString().padStart(2, '0');
    var csv = '代码,名称,最新价,涨跌幅(%),成交额(亿),换手率(%),所属板块\n';
    for (var i = 0; i < S.reviewStocks.length; i++) {
      var s = S.reviewStocks[i];
      csv += s.code + ',' + s.name + ',' + (s.price || '') + ',' + ((s.change || 0).toFixed(2)) + ',' + (s.amount || '') + ',' + (s.turnover || '') + ',' + (s.sector || '') + '\n';
    }
    var blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8' });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = '复盘报告_' + ds + '_' + ts + '.csv';
    a.click();
    URL.revokeObjectURL(a.href);
  },

  startVolumePolling: function () {
    S.stopVolumePolling();
    S.doVolumeRefresh();
    S.volumeTimer = setInterval(function () { S.doVolumeRefresh(); }, 300000);
  },

  searchStock: function () {
    var inp = document.getElementById('reviewSearchInput');
    if (!inp) return;
    var kw = inp.value.trim();
    var dd = document.getElementById('reviewSearchDrop');
    if (!dd) return;
    if (kw.length < 1) { dd.style.display = 'none'; return; }
    var url = S.apiUrl('stock/search') + (S.staticMode ? '' : '?keyword=' + encodeURIComponent(kw));
    fetch(url).then(function (r) { return r.json(); }).then(function (d) {
      var list = [];
      if (d.success && d.list) list = d.list;
      else if (d.success && d.data) list = d.data;
      var kwu = kw.toUpperCase();
      var filtered = list.filter(function (s) { return s.code.indexOf(kwu) >= 0 || (s.name || '').indexOf(kw) >= 0; }).slice(0, 20);
      var existing = {};
      if (S.reviewStocks) { for (var i = 0; i < S.reviewStocks.length; i++) { existing[S.reviewStocks[i].code] = true; } }
      var hh = '<div style="position:absolute;top:0;left:0;background:var(--surface-raised);border:1px solid var(--glass-border);border-radius:var(--radius-md);max-height:200px;overflow-y:auto;z-index:100;width:300px;box-shadow:var(--shadow-lg)">';
      for (var i = 0; i < filtered.length; i++) {
        var s = filtered[i];
        if (existing[s.code]) {
          hh += '<div class="flex items-center justify-between" style="padding:8px 12px;border-bottom:1px solid var(--glass-border)"><span>' + s.code + ' ' + s.name + '</span><span class="text-xs text-tertiary">已添加</span></div>';
        } else {
          hh += '<div class="flex items-center justify-between" style="padding:8px 12px;border-bottom:1px solid var(--glass-border)"><span>' + s.code + ' ' + s.name + '</span>' + UI.button('添加', 'primary', 'S.addToWatchlist(\'' + s.code + '\')', { className: 'btn-sm' }) + '</div>';
        }
      }
      if (filtered.length === 0) hh += '<div style="padding:8px 12px;color:var(--text-tertiary)">无符合条件股票</div>';
      hh += '</div>';
      dd.innerHTML = hh;
      dd.style.display = 'block';
    }).catch(function () { if (dd) dd.style.display = 'none'; });
  },

  addToWatchlist: function (code) {
    if (S.staticMode) {
      var wl = JSON.parse(localStorage.getItem('inv_watchlist') || '[]');
      if (wl.indexOf(code) < 0) { wl.push(code); localStorage.setItem('inv_watchlist', JSON.stringify(wl)); }
      S.doReviewRefresh();
    } else {
      fetch(S.server + '/api/review/watchlist/add?code=' + code).then(function (r) { return r.json(); }).then(function (d) { if (d.success) S.doReviewRefresh(); }).catch(function (e) { console.error('fetch error', e); });
    }
    var dd = document.getElementById('reviewSearchDrop');
    if (dd) dd.style.display = 'none';
  },

  removeFromWatchlist: function (code) {
    if (!confirm('确定删除该股票吗？')) return;
    if (S.staticMode) {
      var wl = JSON.parse(localStorage.getItem('inv_watchlist') || '[]');
      var idx = wl.indexOf(code);
      if (idx >= 0) { wl.splice(idx, 1); localStorage.setItem('inv_watchlist', JSON.stringify(wl)); }
      S.doReviewRefresh();
    } else {
      fetch(S.server + '/api/review/watchlist/remove?code=' + code).then(function (r) { return r.json(); }).then(function (d) { if (d.success) S.doReviewRefresh(); }).catch(function (e) { console.error('fetch error', e); });
    }
  },

  // ===== INDUSTRY PAGE =====
  R_industry: function () {
    var headerActions = document.getElementById('headerActions');
    if (headerActions) {
      headerActions.innerHTML =
        '<div class="btn-group">' +
        '<button id="viewBtnChain" class="btn btn-sm active" onclick="S.switchChainView(\'sankey\')">链状视图</button>' +
        '<button id="viewBtnTree" class="btn btn-sm" onclick="S.switchChainView(\'tree\')">树状视图</button>' +
        '</div>' +
        '<span class="text-xs text-tertiary">离线预置数据</span>';
    }
    var h = '<div class="flex gap-4" style="height:calc(100dvh - 140px);min-height:500px;overflow:hidden">';
    h += '<div class="card" style="width:200px;min-width:200px;display:flex;flex-direction:column;overflow:hidden">';
    h += '<div class="card-title mb-3">产业赛道</div>';
    h += '<div id="industryList" class="overflow-auto flex-1"></div>';
    h += '</div>';
    h += '<div class="flex-col flex-1 gap-4" style="overflow:hidden">';
    h += '<div class="flex items-center gap-3 flex-wrap">';
    h += '<div class="text-xl" style="font-weight:700;" id="industryName">AI算力产业链</div>';
    h += '<span id="industryScore">' + UI.tag('景气: --', 'green') + '</span>';
    h += '</div>';
    h += '<div id="chainChart" class="card" style="flex:1;min-height:400px;padding:0;overflow:hidden"></div>';
    h += '<div id="nodeDetailPanel" class="card hidden" style="max-height:220px;overflow-y:auto">';
    h += '<div class="card-header"><div class="card-title" id="nodeName"></div><button class="btn btn-sm btn-secondary" onclick="S.hideNodeDetail()">收起 ✕</button></div>';
    h += '<div class="grid gap-3" style="grid-template-columns:1fr 1fr">';
    h += '<div><div class="text-xs text-tertiary mb-1">产业逻辑</div><div id="nodeLogic" class="text-sm"></div></div>';
    h += '<div><div class="text-xs text-tertiary mb-1">核心壁垒</div><div id="nodeBarrier" class="text-sm"></div></div>';
    h += '<div><div class="text-xs text-tertiary mb-1">核心标的</div><div id="nodeStocks" class="text-sm text-accent"></div></div>';
    h += '<div><div class="text-xs text-tertiary mb-1">近期资讯</div><div id="nodeNews" class="text-sm"></div></div>';
    h += '</div></div>';
    h += '</div></div>';
    return h;
  },

  chainData: {
    name: 'AI算力产业链',
    score: 82,
    children: []
  },

  industryConfig: null,
  currentIndustryId: 'ai_compute',

  loadIndustryConfig: function (callback) {
    if (S.industryConfig) {
      if (callback) callback();
      return;
    }
    fetch(S.apiUrl('industry/chain')).then(function (r) { return r.json(); }).then(function (d) {
      var config = d;
      if (d.success && d.data) config = d.data;
      else if (d.industries) config = d;
      S.industryConfig = config;
      S.convertIndustryConfig();
      if (callback) callback();
    }).catch(function (e) {
      console.error('industry config load failed', e);
      S.industryConfig = { industries: [] };
      if (callback) callback();
    });
  },

  convertIndustryConfig: function () {
    var industries = (S.industryConfig && S.industryConfig.industries) || [];
    if (industries.length === 0) return;
    var ind = null;
    for (var i = 0; i < industries.length; i++) {
      if (industries[i].id === S.currentIndustryId) { ind = industries[i]; break; }
    }
    if (!ind) ind = industries[0];
    if (!ind || !ind.nodes) return;

    var map = {};
    for (var i = 0; i < ind.nodes.length; i++) {
      map[ind.nodes[i].id] = ind.nodes[i];
    }

    function buildTree(node) {
      var children = [];
      var childIds = node.children || [];
      for (var i = 0; i < childIds.length; i++) {
        var child = map[childIds[i]];
        if (child) children.push(buildTree(child));
      }
      var r = {
        id: node.id,
        name: node.name,
        score: node.boom_score || 0,
        logic: node.logic || '',
        barrier: node.barrier || '',
        stocks: node.stocks || [],
        news: node.news || [],
        children: children
      };
      return r;
    }

    var root = null;
    for (var i = 0; i < ind.nodes.length; i++) {
      if (!ind.nodes[i].parent_id || ind.nodes[i].level === 'root') { root = ind.nodes[i]; break; }
    }
    if (!root) root = ind.nodes[0];

    S.chainData = buildTree(root);
    S.chainData.name = ind.name;
    S.chainData.score = ind.boom_score || S.chainData.score;
  },

  currentChainView: 'sankey',

  renderIndustryChain: function () {
    S.loadIndustryConfig(function () {
      S.renderIndustryList();
      S.switchChainView('sankey');
    });
  },

  renderIndustryList: function () {
    var el = document.getElementById('industryList');
    if (!el) return;
    var industries = (S.industryConfig && S.industryConfig.industries) || [];
    if (industries.length === 0) {
      el.innerHTML = '<div class="industry-item active" data-ind="ai_compute" onclick="S.selectIndustry(\'ai_compute\')">' +
        '<div style="font-size:var(--text-sm);font-weight:600">AI算力产业链</div>' +
        '<div class="text-xs" style="color:var(--down);margin-top:2px">景气 82</div>' +
        '</div>';
      return;
    }
    var h = '';
    for (var i = 0; i < industries.length; i++) {
      var ind = industries[i];
      var active = ind.id === S.currentIndustryId ? ' active' : '';
      var sc = ind.boom_score || 0;
      var c = sc >= 70 ? 'var(--down)' : sc >= 40 ? 'var(--warn)' : 'var(--up)';
      h += '<div class="industry-item' + active + '" data-ind="' + ind.id + '" onclick="S.selectIndustry(\'' + ind.id + '\')">' +
        '<div style="font-size:var(--text-sm);font-weight:600">' + UI.escape(ind.name) + '</div>' +
        '<div class="text-xs" style="color:' + c + ';margin-top:2px">景气 ' + sc + '</div>' +
        '</div>';
    }
    el.innerHTML = h;
  },

  selectIndustry: function (id) {
    S.currentIndustryId = id;
    S.convertIndustryConfig();
    document.querySelectorAll('.industry-item').forEach(function (el) { el.classList.remove('active'); });
    var sel = document.querySelector('.industry-item[data-ind="' + id + '"]');
    if (sel) sel.classList.add('active');
    S.switchChainView(S.currentChainView);
  },

  switchChainView: function (view) {
    S.currentChainView = view;
    var b1 = document.getElementById('viewBtnChain');
    var b2 = document.getElementById('viewBtnTree');
    if (b1) b1.className = 'btn btn-sm ' + (view === 'sankey' ? 'active' : '');
    if (b2) b2.className = 'btn btn-sm ' + (view === 'tree' ? 'active' : '');
    var ne = document.getElementById('industryName');
    if (ne) ne.textContent = S.chainData.name;
    var se = document.getElementById('industryScore');
    if (se) {
      var sc = S.chainData.score;
      se.innerHTML = UI.tag('景气: ' + sc, sc >= 70 ? 'green' : sc >= 40 ? 'yellow' : 'red');
    }
    if (view === 'sankey') S.renderSankeyView();
    else S.renderTreeView();
  },

  renderSankeyView: function () {
    var dom = document.getElementById('chainChart');
    if (!dom) return;
    dom.style.height = '100%';
    var chart = echarts.getInstanceByDom(dom);
    if (!chart) chart = echarts.init(dom);
    var d = S.chainData;
    var nodes = [];
    var links = [];
    var cats = [d.children[0].name, d.children[1].name, d.children[2].name];
    var cols = ['rgba(79,125,243,.15)', 'rgba(34,197,94,.12)', 'rgba(245,158,11,.12)'];
    for (var i = 0; i < cats.length; i++) {
      nodes.push({ name: cats[i], itemStyle: { color: cols[i] }, label: { color: '#E2E8F0', fontWeight: 'bold', fontSize: 11 } });
      var cat = d.children[i];
      if (cat.children) {
        for (var j = 0; j < cat.children.length; j++) {
          var nd = cat.children[j];
          var nc = nd.score >= 70 ? 'rgba(34,197,94,.6)' : nd.score >= 40 ? 'rgba(245,158,11,.6)' : 'rgba(255,77,79,.6)';
          nodes.push({ name: nd.name, itemStyle: { color: nc, borderRadius: 4 }, label: { color: '#E2E8F0', fontSize: 10 } });
          links.push({ source: cats[i], target: nd.name, value: 1 });
        }
      }
    }
    chart.setOption({
      tooltip: {
        trigger: 'item',
        formatter: function (p) {
          if (p.dataType === 'node') {
            var info = S.findChainNode(p.name);
            return info ? '<b>' + p.name + '</b><br/>景气度: ' + (info.score || '--') + '<br/>' + (info.logic || '') : '<b>' + p.name + '</b>';
          }
          return '';
        },
        backgroundColor: 'rgba(17,24,39,.95)',
        borderColor: 'rgba(255,255,255,.1)',
        textStyle: { color: '#E2E8F0', fontSize: 11 }
      },
      series: [{
        type: 'sankey', layout: 'none', layoutIterations: 0, emphasis: { focus: 'adjacency' },
        nodeWidth: 16, nodeGap: 10, data: nodes, links: links,
        lineStyle: { color: 'gradient', curveness: 0.5, opacity: 0.2 }
      }],
      backgroundColor: 'transparent'
    });
    chart.off('click');
    chart.on('click', function (p) {
      if (p.dataType === 'node') {
        var info = S.findChainNode(p.name);
        if (info) S.showNodeDetail(info);
      }
    });
    S.charts.chain = chart;
  },

  renderTreeView: function () {
    var dom = document.getElementById('chainChart');
    if (!dom) return;
    var chart = echarts.getInstanceByDom(dom);
    if (!chart) chart = echarts.init(dom);
    function buildTree(node) {
      var c = node.score >= 70 ? '#22C55E' : node.score >= 40 ? '#F59E0B' : '#FF4D4F';
      var r = { name: node.name + (node.score ? ' (' + node.score + ')' : ''), itemStyle: { color: c }, label: { color: '#E2E8F0', fontSize: 10 } };
      if (node.children && node.children.length > 0) {
        r.children = [];
        for (var i = 0; i < node.children.length; i++) r.children.push(buildTree(node.children[i]));
      }
      return r;
    }
    var td = buildTree(S.chainData);
    chart.setOption({
      tooltip: { trigger: 'item', formatter: function (p) { return '<b>' + (p.name || '') + '</b>'; }, backgroundColor: 'rgba(17,24,39,.95)', borderColor: 'rgba(255,255,255,.1)', textStyle: { color: '#E2E8F0', fontSize: 11 } },
      series: [{
        type: 'tree', data: [td], layout: 'orthogonal', orient: 'LR', roam: true, symbolSize: 8,
        lineStyle: { color: 'rgba(255,255,255,.1)', width: 1 }, leaves: { label: { position: 'right', color: '#E2E8F0', fontSize: 10 } },
        expandAndCollapse: true, initialTreeDepth: 2, label: { color: '#E2E8F0', fontSize: 10 }
      }],
      backgroundColor: 'transparent'
    });
    chart.off('click');
    chart.on('click', function (p) {
      if (p && p.name) {
        var nm = p.name.replace(/\s*\(\d+\)\s*$/, '');
        var info = S.findChainNode(nm);
        if (info) S.showNodeDetail(info);
      }
    });
    S.charts.chain = chart;
  },

  findChainNode: function (name) {
    function search(node) {
      if (node.name === name || node.name.indexOf(name) === 0) return node;
      if (node.children) {
        for (var i = 0; i < node.children.length; i++) {
          var r = search(node.children[i]);
          if (r) return r;
        }
      }
      return null;
    }
    return search(S.chainData);
  },

  showNodeDetail: function (node) {
    var panel = document.getElementById('nodeDetailPanel');
    if (!panel) return;
    panel.classList.remove('hidden');
    A.enter(panel, 0, 300);
    var ne = document.getElementById('nodeName');
    if (ne) ne.textContent = node.name;
    var le = document.getElementById('nodeLevel');
    var lv = '中游';
    if (node.name.indexOf('能源') >= 0 || node.name.indexOf('材料') >= 0 || node.name.indexOf('设备') >= 0 || node.name.indexOf('零部件') >= 0) lv = '上游';
    else if (node.name.indexOf('应用') >= 0) lv = '下游';
    if (ne) ne.innerHTML = UI.escape(node.name) + ' ' + UI.tag(lv, 'blue');
    var se = document.getElementById('nodeScore');
    if (!se) {
      se = document.createElement('span');
      se.id = 'nodeScore';
    }
    if (node.score) {
      se.innerHTML = UI.tag('景气 ' + node.score, node.score >= 70 ? 'green' : node.score >= 40 ? 'yellow' : 'red');
    }
    var log = document.getElementById('nodeLogic');
    if (log) log.textContent = node.logic || '暂无数据';
    var bar = document.getElementById('nodeBarrier');
    if (bar) bar.textContent = node.barrier || '暂无数据';
    var stk = document.getElementById('nodeStocks');
    if (stk) {
      if (node.stocks && node.stocks.length > 0) {
        var sh = '';
        for (var i = 0; i < node.stocks.length; i++) {
          sh += '<span class="text-accent cursor-pointer" style="margin-right:8px" onclick="S.nav(\'review\')">' + node.stocks[i].code + ' ' + node.stocks[i].name + '</span>';
        }
        stk.innerHTML = sh;
      } else { stk.textContent = '暂无数据'; }
    }
    var nws = document.getElementById('nodeNews');
    if (nws) nws.textContent = '暂无最新资讯';
  },

  hideNodeDetail: function () {
    var panel = document.getElementById('nodeDetailPanel');
    if (panel) panel.classList.add('hidden');
  },

  // ===== REVIEW SUMMARY PAGE =====
  R_review_summary: function () {
    var headerActions = document.getElementById('headerActions');
    if (headerActions) {
      headerActions.innerHTML = '<span class="text-xs text-tertiary">基于固定模板的结构化复盘，纯本地规则计算</span>';
    }
    var h = '';
    h += UI.tabs([
      { key: 'tab1', label: '盘后快速复盘' },
      { key: 'tab2', label: '次日作战计划' },
      { key: 'tab3', label: '盘中突发诊断' }
    ], S.currentReviewTab || 'tab1', 'S.switchReviewTab');

    h += '<div class="grid gap-4 mt-4" style="grid-template-columns:380px 1fr">';
    h += '<div id="rsLeft">' + UI.card('数据', '<div id="rsFormContent">加载中...</div>', { id: 'rsFormCard' }) + '</div>';
    h += '<div id="rsRight">' + UI.card('生成结果',
      '<div class="flex items-center justify-between mb-3"><span class="text-xs text-tertiary">结构化复盘</span>' + UI.button('一键复制', 'secondary', 'S.copyReviewResult()') + '</div>' +
      '<div id="rsResultContent" class="text-sm" style="line-height:1.8;white-space:pre-wrap;font-family:var(--font-mono);min-height:200px;color:var(--text-secondary)">点击下方按钮生成复盘内容</div>',
      { id: 'rsResultCard' }) + '</div>';
    h += '</div>';
    h += '<div class="text-center mt-4">' + UI.button('生成复盘', 'primary', 'S.generateReview()', { id: 'rsGenBtn' }) + '</div>';
    return h;
  },

  switchReviewTab: function (tab) {
    S.currentReviewTab = tab;
    document.querySelectorAll('.tab').forEach(function (n) { n.classList.remove('active'); });
    var el = document.querySelector('.tab[data-tab="' + tab + '"]');
    if (el) el.classList.add('active');
    UI.initTabs('.tabs');
    S.renderReviewForm();
  },

  loadReviewSummary: function () {
    fetch(S.apiUrl('review/summary')).then(function (r) { return r.json(); }).then(function (d) {
      if (d.success) {
        S.reviewSummaryData = d;
        S.renderReviewForm();
        var st = document.getElementById('rsStatus');
        if (st) st.textContent = ' (自动计算)';
        UI.initTabs('.tabs');
      }
    }).catch(function (e) { console.error('fetch error', e); });
  },

  renderReviewForm: function () {
    var tab = S.currentReviewTab || 'tab1';
    var fc = document.getElementById('rsFormContent');
    if (!fc) return;
    var d = S.reviewSummaryData;
    var m = (d && d.market) ? d.market : {};
    var html = '';

    function field(label, value, auto) {
      return '<div class="card-flat mb-3">' +
        '<div class="text-xs text-tertiary mb-1">' + label + (auto ? ' <span class="text-xs text-down">' + auto + '</span>' : '') + '</div>' +
        '<div class="text-sm">' + value + '</div>' +
        '</div>';
    }

    if (tab === 'tab1') {
      html += field('大盘指数',
        '上证: ' + (m.sh_change !== undefined ? m.sh_change + '%' : '--') + ' | 深证: ' + (m.sz_change !== undefined ? m.sz_change + '%' : '--') + ' | 创业板: ' + (m.cyb_change !== undefined ? m.cyb_change + '%' : '--'),
        '自动计算');
      html += field('涨跌家数', '上涨 ' + (m.up_count || '--') + ' | 下跌 ' + (m.down_count || '--'), '自动计算');
      html += field('涨跌停', '涨停 ' + (m.limit_up_count || '--') + ' | 跌停 ' + (m.limit_down_count || '--') + ' | 炸板率 ' + (m.bomb_rate !== undefined ? m.bomb_rate + '%' : '--'), '自动计算');
      var stage = d && d.sentiment_stage || '';
      var etype = d && d.effect_type || '';
      var edays = d && d.effect_days || 0;
      var stageColor = (stage === '冰点' || stage === '退潮') ? 'var(--up)' : (stage === '主升' || stage === '高潮') ? 'var(--down)' : 'var(--warn)';
      html += field('情绪阶段', stage ? '<span style="color:' + stageColor + '">' + stage + ' (' + etype + '第' + edays + '天)</span>' : '--', '自动计算');
      var sectors = (d && d.core_sectors) || [];
      var sectorHtml = '--';
      if (sectors.length > 0) {
        sectorHtml = '';
        for (var si = 0; si < sectors.length; si++) {
          sectorHtml += '<div class="text-sm mb-1">' + UI.escape(sectors[si].topic) + ': ' + UI.escape((sectors[si].stocks || []).join(', ')) + '</div>';
        }
      }
      html += field('核心题材', sectorHtml, '自动分组');
      html += field('风向标', d && d.wind_vane ? d.wind_vane : '--', '自动计算');
      html += '<div class="text-xs text-tertiary mb-1">补充信息</div>';
      html += '<textarea id="rsExtraTab1" class="input" rows="2" placeholder="可手动补充题材细节、活口观察等"></textarea>';
    } else if (tab === 'tab2') {
      html += '<div class="text-xs text-tertiary mb-1">目标股（1-3只，代码或名称，每行一只）</div>';
      html += '<textarea id="rsTargets" class="input mb-3" rows="3" placeholder="例：中际旭创&#10;300308&#10;沪电股份"></textarea>';
      html += '<div class="text-xs text-tertiary mb-1">大盘风控成交额阈值（亿）</div>';
      html += '<input id="rsVolThreshold" class="input mb-3" value="' + (m.turnover_total ? Math.round(m.turnover_total) : '7000') + '">';
      html += field('当前情绪', d && d.sentiment_stage ? d.sentiment_stage + ' / ' + (d.effect_type || '') : '--', '自动计算');
    } else if (tab === 'tab3') {
      html += '<div class="text-xs text-tertiary mb-1">持仓股（代码或名称）</div>';
      html += '<input id="rsHoldCode" class="input mb-3" placeholder="例：300308">';
      html += '<div class="text-xs text-tertiary mb-1">成本价</div>';
      html += '<input id="rsCostPrice" class="input mb-3" type="number" placeholder="0.00">';
      html += '<div class="text-xs text-tertiary mb-1">现价</div>';
      html += '<input id="rsNowPrice" class="input mb-3" type="number" placeholder="0.00">';
      html += '<div class="text-xs text-tertiary mb-1">当前情况</div>';
      html += '<select id="rsSituation" class="input mb-3"><option value="zhaban">炸板</option><option value="diepo">跌破均线</option><option value="datao">大单出逃</option></select>';
      html += '<div class="text-xs text-tertiary mb-1">所属板块涨停数</div>';
      html += '<input id="rsSectorLimitUp" class="input" value="0">';
    }
    fc.innerHTML = html;
  },

  generateReview: function () {
    var tab = S.currentReviewTab || 'tab1';
    var rc = document.getElementById('rsResultContent');
    if (!rc) return;
    var d = S.reviewSummaryData;
    var m = (d && d.market) ? d.market : {};
    var output = '';

    if (tab === 'tab1') {
      var stage = d && d.sentiment_stage || '暂无数据';
      var etype = d && d.effect_type || '';
      var edays = d && d.effect_days || 0;
      output += '【一、情绪周期】\n';
      output += '当前阶段：' + stage + ' (' + etype + '第' + edays + '天)\n';
      output += '综合评分：' + (d && d.composite_score ? Math.round(d.composite_score) : '--') + '\n\n';
      output += '【二、市场数据】\n';
      output += '上证: ' + (m.sh_change !== undefined ? m.sh_change + '%' : '--') + ' / 深证: ' + (m.sz_change !== undefined ? m.sz_change + '%' : '--') + ' / 创业板: ' + (m.cyb_change !== undefined ? m.cyb_change + '%' : '--') + '\n';
      output += '涨跌家数：涨 ' + (m.up_count || '--') + ' / 跌 ' + (m.down_count || '--') + '\n';
      output += '涨跌停：' + (m.limit_up_count || '--') + ' / ' + (m.limit_down_count || '--') + '，炸板率 ' + (m.bomb_rate !== undefined ? m.bomb_rate + '%' : '--') + '\n\n';
      output += '【三、核心题材】\n';
      var sectors = (d && d.core_sectors) || [];
      for (var si = 0; si < sectors.length; si++) {
        output += sectors[si].topic + ': ' + (sectors[si].stocks || []).join(', ') + '\n';
      }
      output += '\n【四、风向标】\n' + (d && d.wind_vane ? d.wind_vane : '--') + '\n';
      var extra = document.getElementById('rsExtraTab1');
      if (extra && extra.value.trim()) output += '\n【补充】\n' + extra.value.trim();
    } else if (tab === 'tab2') {
      var targets = (document.getElementById('rsTargets') || {}).value || '未输入目标股';
      var threshold = (document.getElementById('rsVolThreshold') || {}).value || '7000';
      var targetList = targets.split('\n').filter(function (x) { return x.trim(); });
      output += '【次日作战计划】\n';
      output += '目标股：\n';
      for (var ti = 0; ti < targetList.length; ti++) output += '- ' + targetList[ti].trim() + '\n';
      output += '\n当前情绪：' + (d && d.sentiment_stage ? d.sentiment_stage : '--') + '\n';
      output += '成交额阈值：' + threshold + '亿\n';
      var currVol = m.turnover_total;
      output += '当前成交额：' + (currVol !== undefined ? currVol.toFixed(0) + '亿' : '--') + '，' + (currVol && currVol >= threshold ? '满足阈值' : '低于阈值，谨慎') + '\n';
    } else if (tab === 'tab3') {
      var holdCode = (document.getElementById('rsHoldCode') || {}).value || '未输入';
      var costPrice = parseFloat((document.getElementById('rsCostPrice') || {}).value) || 0;
      var nowPrice = parseFloat((document.getElementById('rsNowPrice') || {}).value) || 0;
      var situation = (document.getElementById('rsSituation') || {}).value || '未选择';
      var sectorLimitUp = parseInt((document.getElementById('rsSectorLimitUp') || {}).value) || 0;
      var pl = 0;
      if (costPrice > 0 && nowPrice > 0) pl = ((nowPrice - costPrice) / costPrice) * 100;
      var sitMap = { zhaban: '炸板', diepo: '跌破均线', datao: '大单出逃' };
      var stage3 = d && d.sentiment_stage || '';
      var isStrong = stage3 === '主升' || stage3 === '高潮';
      var isWeak = stage3 === '冰点' || stage3 === '退潮';
      var hasSectorSupport = sectorLimitUp >= 3;
      var lossDeep = pl < -5;
      output += '【盘中突发诊断】\n';
      output += '持仓：' + holdCode + '\n';
      output += '成本：' + costPrice.toFixed(2) + ' / 现价：' + nowPrice.toFixed(2) + ' / 盈亏：' + (pl >= 0 ? '+' : '') + pl.toFixed(2) + '%\n';
      output += '当前情况：' + sitMap[situation] + '\n';
      output += '板块涨停数：' + sectorLimitUp + '\n';
      if (isWeak || lossDeep) output += '建议：风险偏高，优先控仓/止损。\n';
      else if (isStrong && hasSectorSupport) output += '建议：情绪+板块共振，可观察承接。\n';
      else output += '建议：结合分时承接，分批处理。\n';
    }

    rc.textContent = output;
    A.enter(rc, 0, 300);
  },

  copyReviewResult: function () {
    var rc = document.getElementById('rsResultContent');
    if (!rc) return;
    var text = rc.textContent;
    if (navigator.clipboard) {
      navigator.clipboard.writeText(text).then(function () {
        S.showToast('已复制复盘内容');
      });
    } else {
      var ta = document.createElement('textarea');
      ta.value = text;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
      S.showToast('已复制复盘内容');
    }
  },

  showToast: function (msg) {
    var t = document.createElement('div');
    t.className = 'toast';
    t.textContent = msg;
    t.style.cssText = 'position:fixed;bottom:100px;left:50%;transform:translateX(-50%);background:var(--surface-raised);color:var(--text-primary);padding:10px 20px;border-radius:var(--radius-md);border:1px solid var(--glass-border);box-shadow:var(--shadow-lg);z-index:2000;font-size:var(--text-sm);font-weight:600;';
    document.body.appendChild(t);
    A.scaleIn(t, 0);
    setTimeout(function () {
      A.fadeIn(t, 0, 200); // reuse fade for reverse opacity
      anime({ targets: t, opacity: 0, translateY: 10, easing: 'easeInQuart', duration: 200, complete: function () { t.remove(); } });
    }, 1800);
  },

  // ===== HISTORY PAGE =====
  R_history: function () {
    var headerActions = document.getElementById('headerActions');
    if (headerActions) {
      headerActions.innerHTML = '<span id="historySource" class="text-sm text-tertiary">' + (S.supabaseAvailable ? '数据来源: Supabase' : '数据来源: 本地缓存') + '</span>';
    }
    var h = '';
    h += UI.tabs([
      { key: 'factors', label: '因子趋势' },
      { key: 'volume', label: '量能异动' },
      { key: 'snapshots', label: '市场快照' },
      { key: 'sectors', label: '板块排行' }
    ], S.currentHistoryTab || 'factors', 'S.switchHistoryTab');

    h += '<div class="flex items-center gap-3 mt-4 mb-4 flex-wrap">';
    h += '<span class="text-sm text-tertiary">日期范围:</span>';
    h += '<input type="date" id="hDateFrom" class="input" style="width:140px" onchange="S.loadHistoryData()">';
    h += '<span class="text-sm text-tertiary">至</span>';
    h += '<input type="date" id="hDateTo" class="input" style="width:140px" onchange="S.loadHistoryData()">';
    h += UI.button('查询', 'primary', 'S.loadHistoryData()');
    h += '</div>';

    h += '<div id="historyContent"><div style="text-align:center;padding:40px;color:var(--text-tertiary)">选择日期范围后点击查询</div></div>';
    h += '<div id="historyChart" class="card hidden" style="height:400px;margin-top:var(--space-4)"><div id="historyChartInner" class="chart-container" style="height:360px"></div></div>';
    return h;
  },

  checkSupabaseStatus: function () {
    if (supabaseClient) {
      S.supabaseAvailable = true;
      var icon = document.getElementById('dbIcon');
      var dbStatus = document.getElementById('dbStatus');
      if (icon) icon.className = 'status-dot online';
      if (dbStatus) dbStatus.textContent = '数据库在线';
      if (S.staticMode) S.setStatus('云端在线', '#22C55E');
      return;
    }
    if (S.staticMode) return;
    fetch(S.server + '/api/supabase/status').then(function (r) { return r.json(); }).then(function (d) {
      if (!d.success) return;
      S.supabaseAvailable = d.connected;
      var icon = document.getElementById('dbIcon');
      var dbStatus = document.getElementById('dbStatus');
      if (!icon || !dbStatus) return;
      if (d.connected) {
        icon.className = 'status-dot online';
        var txt = '数据库在线';
        if (d.last_sync) txt += ' · ' + d.last_sync;
        if (d.total_synced) txt += ' · ' + d.total_synced + '次';
        dbStatus.textContent = txt;
      } else if (d.configured) {
        icon.className = 'status-dot idle';
        dbStatus.textContent = '数据库断开 (' + (d.consecutive_errors || 0) + '次失败)';
        S.supabaseAvailable = false;
      } else {
        icon.className = 'status-dot idle';
        dbStatus.textContent = '数据库未配置';
        S.supabaseAvailable = false;
      }
    }).catch(function () {
      var icon = document.getElementById('dbIcon');
      var dbStatus = document.getElementById('dbStatus');
      if (icon) icon.className = 'status-dot offline';
      if (dbStatus) dbStatus.textContent = '数据库无响应';
      S.supabaseAvailable = false;
    });
  },

  setDefaultHistoryDates: function () {
    var now = new Date();
    var weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
    var fromEl = document.getElementById('hDateFrom');
    var toEl = document.getElementById('hDateTo');
    if (fromEl) fromEl.value = weekAgo.toISOString().substring(0, 10);
    if (toEl) toEl.value = now.toISOString().substring(0, 10);
    S.loadHistoryData();
  },

  switchHistoryTab: function (tab) {
    S.currentHistoryTab = tab;
    document.querySelectorAll('.tab').forEach(function (n) { n.classList.remove('active'); });
    var labels = { factors: '因子', volume: '量能', snapshots: '快照', sectors: '板块' };
    document.querySelectorAll('.tab').forEach(function (n) {
      if (n.textContent.indexOf(labels[tab] || '') >= 0) n.classList.add('active');
    });
    UI.initTabs('.tabs');
    S.loadHistoryData();
  },

  loadHistoryData: function () {
    var fromEl = document.getElementById('hDateFrom');
    var toEl = document.getElementById('hDateTo');
    var from = fromEl ? fromEl.value : '';
    var to = toEl ? toEl.value : '';
    var content = document.getElementById('historyContent');
    var chartWrap = document.getElementById('historyChart');
    if (!content) return;
    content.innerHTML = '<div style="text-align:center;padding:20px;color:var(--text-tertiary)">加载中...</div>';
    var tab = S.currentHistoryTab;

    if (supabaseClient) {
      S._loadHistoryFromSupabase(tab, from, to);
      return;
    }

    var apiPath = ''; var params = '';
    if (tab === 'factors') { apiPath = 'history/factors'; if (from) params += '&from=' + from; if (to) params += '&to=' + to; }
    else if (tab === 'volume') { apiPath = 'history/volume'; if (to) params += '&date=' + to; }
    else if (tab === 'snapshots') { apiPath = 'history/snapshots'; params += '&days=30'; }
    else if (tab === 'sectors') { apiPath = 'history/sectors'; if (to) params += '&date=' + to; }
    var url = S.apiUrl(apiPath) + (params ? '?' + params.substring(1) : '');
    fetch(url).then(function (r) { return r.json(); }).then(function (d) {
      if (d.success && d.data) { S.renderHistoryContent(tab, d.data, d.source || '本地缓存'); }
      else { content.innerHTML = '<div style="text-align:center;padding:40px;color:var(--text-tertiary)">暂无数据</div>'; if (chartWrap) chartWrap.classList.add('hidden'); }
    }).catch(function (e) {
      content.innerHTML = '<div style="text-align:center;padding:40px;color:var(--up)">加载失败: ' + UI.escape(e.message) + '</div>';
    });
  },

  _loadHistoryFromSupabase: function (tab, from, to) {
    var content = document.getElementById('historyContent');
    var chartWrap = document.getElementById('historyChart');
    var query;
    if (tab === 'factors') {
      query = supabaseClient.from('factor_scores').select('*').order('recorded_at', { ascending: true }).limit(500);
      if (from) query = query.gte('recorded_at', from + 'T00:00:00');
      if (to) query = query.lte('date', to);
    } else if (tab === 'volume') {
      query = supabaseClient.from('volume_alerts').select('*').order('ratio', { ascending: false }).limit(200);
      if (to) query = query.eq('date', to);
    } else if (tab === 'snapshots') {
      query = supabaseClient.from('market_snapshots').select('*').order('snapshot_time', { ascending: false }).limit(200);
    } else if (tab === 'sectors') {
      query = supabaseClient.from('sector_rankings').select('*').order('ranking', { ascending: true }).limit(100);
      if (to) query = query.eq('date', to);
    } else {
      content.innerHTML = '<div style="text-align:center;padding:40px;color:var(--text-tertiary)">不支持的数据类型</div>';
      return;
    }
    query.then(function (result) {
      var data = result.data || [];
      if (result.error) throw result.error;
      if (data.length > 0) {
        S.renderHistoryContent(tab, data, 'Supabase');
      } else {
        content.innerHTML = '<div style="text-align:center;padding:40px;color:var(--text-tertiary)">暂无数据，请先等待数据采集（每5分钟一次）</div>';
        if (chartWrap) chartWrap.classList.add('hidden');
      }
    }).catch(function (err) {
      console.error('Supabase 查询失败:', err);
      S.supabaseAvailable = false;
      var dbStatus = document.getElementById('dbStatus');
      if (dbStatus) dbStatus.textContent = '数据库查询失败，回退本地数据';
      S.loadHistoryData();
    });
  },

  renderHistoryContent: function (tab, data, source) {
    var content = document.getElementById('historyContent');
    var chartWrap = document.getElementById('historyChart');
    if (!content) return;
    if (tab === 'factors') {
      var h = '<div class="text-sm text-tertiary mb-3">共 ' + data.length + ' 条记录 | 来源: ' + source + '</div>';
      var rows = '';
      var sliced = data.slice(-100);
      for (var i = sliced.length - 1; i >= 0; i--) {
        var r = sliced[i]; var ts = r.recorded_at || r.ts || '';
        rows += '<tr><td>' + (ts.length > 16 ? ts.substring(11, 19) : ts) + '</td>';
        rows += '<td class="num" style="font-weight:700;color:' + (r.composite >= 60 ? 'var(--down)' : r.composite >= 40 ? 'var(--warn)' : 'var(--up)') + '">' + r.composite + '</td>';
        rows += '<td>' + (r.sentiment || '-') + '</td><td>' + (r.sector || '-') + '</td><td>' + (r.chip || '-') + '</td><td>' + (r.overnight || '-') + '</td>';
        rows += '<td>' + (r.outlook || '-') + '</td></tr>';
      }
      h += UI.tableWrap(['时间', '综合', '情绪', '板块', '筹码', '隔夜', '展望'], rows);
      content.innerHTML = h;
      if (chartWrap) { chartWrap.classList.remove('hidden'); setTimeout(function () { S.renderHistoryFactorChart(data); }, 200); }
    } else if (tab === 'volume') {
      var h = '<div class="text-sm text-tertiary mb-3">共 ' + data.length + ' 条记录 | 来源: ' + source + '</div>';
      var rows = '';
      for (var i = 0; i < Math.min(data.length, 80); i++) {
        var r = data[i]; var chgCls = (r.change || 0) >= 0 ? 'up' : 'down';
        rows += '<tr><td>' + (r.trigger_time || r.alert_time || '').substring(0, 10) + '</td>';
        rows += '<td>' + r.code + '</td><td>' + UI.escape(r.name) + '</td><td class="num">' + r.price + '</td>';
        rows += '<td class="num ' + chgCls + '">' + ((r.change || 0) >= 0 ? '+' : '') + r.change + '%</td>';
        rows += '<td class="num">' + r.volume + '</td>';
        rows += '<td class="num" style="color:var(--warn)">' + (r.ratio ? r.ratio.toFixed(1) + 'x' : '-') + '</td>';
        rows += '<td>' + (r.sector || '-') + '</td></tr>';
      }
      h += UI.tableWrap(['时间', '代码', '名称', '价格', '涨跌', '成交量', '量比', '板块'], rows);
      content.innerHTML = h;
      if (chartWrap) chartWrap.classList.add('hidden');
    } else if (tab === 'snapshots') {
      var h = '<div class="text-sm text-tertiary mb-3">共 ' + data.length + ' 条记录 | 来源: ' + source + '</div>';
      var rows = '';
      for (var i = 0; i < Math.min(data.length, 60); i++) {
        var r = data[i]; var date = (r.snapshot_time || '').substring(0, 10);
        rows += '<tr><td>' + date + '</td>';
        rows += '<td class="num ' + ((r.sh_change || 0) >= 0 ? 'up' : 'down') + '">' + r.sh_change + '%</td>';
        rows += '<td class="num ' + ((r.sz_change || 0) >= 0 ? 'up' : 'down') + '">' + r.sz_change + '%</td>';
        rows += '<td class="num ' + ((r.cyb_change || 0) >= 0 ? 'up' : 'down') + '">' + r.cyb_change + '%</td>';
        rows += '<td class="num">' + (r.turnover_total ? (r.turnover_total / 1).toFixed(0) + '亿' : '-') + '</td>';
        rows += '<td class="num up">' + r.limit_up_count + '</td><td class="num down">' + r.limit_down_count + '</td>';
        rows += '<td class="num">' + r.bomb_rate + '%</td><td class="num">' + (r.northbound_net || '-') + '</td></tr>';
      }
      h += UI.tableWrap(['日期', '上证%', '深证%', '创业板%', '成交额', '涨停', '跌停', '炸板率', '北向'], rows);
      content.innerHTML = h;
      if (chartWrap) chartWrap.classList.add('hidden');
    } else if (tab === 'sectors') {
      var h = '<div class="text-sm text-tertiary mb-3">共 ' + data.length + ' 条记录 | 来源: ' + source + '</div>';
      var rows = '';
      for (var i = 0; i < Math.min(data.length, 50); i++) {
        var r = data[i];
        rows += '<tr><td>' + (r.ranking || i + 1) + '</td><td>' + UI.escape(r.sector_name || '-') + '</td>';
        rows += '<td class="num ' + ((r.change_pct || 0) >= 0 ? 'up' : 'down') + '">' + r.change_pct + '%</td>';
        rows += '<td class="num">' + (r.net_amount || '-') + '</td><td class="num">' + (r.stock_count || '-') + '</td></tr>';
      }
      h += UI.tableWrap(['排名', '板块', '涨跌%', '净流入', '股票数'], rows);
      content.innerHTML = h;
      if (chartWrap) chartWrap.classList.add('hidden');
    }
    A.stagger(content, 'tr', 0);
  },

  renderHistoryFactorChart: function (data) {
    var chartDom = document.getElementById('historyChartInner');
    if (!chartDom || !data || data.length === 0) return;
    if (S.charts.historyFactor) S.charts.historyFactor.dispose();
    var chart = echarts.init(chartDom); S.charts.historyFactor = chart;

    var compData = [], sentData = [], sectData = [], chipData = [], overData = [];
    for (var i = 0; i < data.length; i++) {
      var d = data[i];
      var ts = d.recorded_at || d.ts || '';
      if (typeof ts === 'string' && ts.length > 16) ts = ts.substring(0, 16).replace('T', ' ');
      var t = new Date(ts);
      compData.push([t, d.composite || 50]);
      sentData.push([t, d.sentiment !== undefined ? d.sentiment : 50]);
      sectData.push([t, d.sector !== undefined ? d.sector : 50]);
      chipData.push([t, d.chip !== undefined ? d.chip : 50]);
      overData.push([t, d.overnight !== undefined ? d.overnight : 50]);
    }

    chart.setOption({
      tooltip: { trigger: 'axis', backgroundColor: 'rgba(17,24,39,.95)', borderColor: 'rgba(255,255,255,.1)', textStyle: { color: '#E2E8F0', fontSize: 11 } },
      legend: {
        data: ['综合评分', '情绪', '板块', '筹码', '隔夜'],
        bottom: 0, textStyle: { color: '#94A3B8', fontSize: 10 },
        itemWidth: 12, itemHeight: 8,
        selected: { '情绪': false, '板块': false, '筹码': false, '隔夜': false }
      },
      grid: { left: 50, right: 20, top: 15, bottom: 40 },
      xAxis: {
        type: 'time', axisLabel: { color: '#64748B', fontSize: 10 }, axisLine: { lineStyle: { color: 'rgba(255,255,255,.1)' } },
        splitLine: { show: false }
      },
      yAxis: { type: 'value', min: 0, max: 100, axisLabel: { color: '#64748B', fontSize: 10 }, splitLine: { lineStyle: { color: 'rgba(255,255,255,.06)' } } },
      dataZoom: [
        { type: 'slider', bottom: 20, height: 16, start: 0, end: 100,
          borderColor: 'rgba(255,255,255,.08)', backgroundColor: 'rgba(255,255,255,.03)',
          dataBackground: { lineStyle: { color: 'rgba(79,125,243,.3)' }, areaStyle: { color: 'rgba(79,125,243,.08)' } },
          selectedDataBackground: { lineStyle: { color: '#4F7DF3' }, areaStyle: { color: 'rgba(79,125,243,.15)' } },
          handleStyle: { color: '#4F7DF3' }, textStyle: { color: '#64748B', fontSize: 9 }
        },
        { type: 'inside' }
      ],
      series: [
        { name: '综合评分', type: 'line', data: compData, lineStyle: { color: '#4F7DF3', width: 2.5 }, areaStyle: { color: new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'rgba(79,125,243,.25)'},{offset:1,color:'rgba(79,125,243,.02)'}])}, symbol: 'none', smooth: true },
        { name: '情绪', type: 'line', data: sentData, lineStyle: { color: '#F59E0B', width: 1.5, type: 'dashed' }, symbol: 'none', smooth: true },
        { name: '板块', type: 'line', data: sectData, lineStyle: { color: '#10B981', width: 1.5, type: 'dashed' }, symbol: 'none', smooth: true },
        { name: '筹码', type: 'line', data: chipData, lineStyle: { color: '#EF4444', width: 1.5, type: 'dashed' }, symbol: 'none', smooth: true },
        { name: '隔夜', type: 'line', data: overData, lineStyle: { color: '#8B5CF6', width: 1.5, type: 'dashed' }, symbol: 'none', smooth: true }
      ]
    });
  },

  // ===== SENTIMENT TREND CHART =====
  renderSentimentTrend: function (dps) {
    var dom = document.getElementById('sentimentChart');
    if (!dom) return;
    var chart = echarts.getInstanceByDom(dom);
    if (!chart) chart = echarts.init(dom);
    if (!dps || dps.length === 0) {
      chart.clear();
      chart.setOption({
        title: { text: '等待数据...', textStyle: { color: '#64748B', fontSize: 13 }, left: 'center', top: 'center' },
        backgroundColor: 'transparent'
      });
      return;
    }

    var times = [], compVals = [], sentVals = [], sectVals = [], chipVals = [], overVals = [];
    for (var i = 0; i < dps.length; i++) {
      var d = dps[i];
      var ts = d.recorded_at ? new Date(d.recorded_at) : (d.ts ? new Date(d.ts) : new Date());
      times.push(ts);
      var f = d.factors || [];
      var factorsMap = {};
      for (var j = 0; j < f.length; j++) { factorsMap[f[j].id] = f[j].score; }
      compVals.push([ts, d.composite !== undefined ? d.composite : 50]);
      sentVals.push([ts, factorsMap.sentiment !== undefined ? factorsMap.sentiment : (d.sentiment || 50)]);
      sectVals.push([ts, factorsMap.sector !== undefined ? factorsMap.sector : (d.sector || 50)]);
      chipVals.push([ts, factorsMap.chip !== undefined ? factorsMap.chip : (d.chip || 50)]);
      overVals.push([ts, factorsMap.overnight !== undefined ? factorsMap.overnight : (d.overnight || 50)]);
    }

    var timeRange = times.length > 1 ? (times[times.length - 1] - times[0]) : 3600000;
    var minSpanPct = Math.max(1, Math.round(1800000 / timeRange * 100));
    var maxSpanPct = Math.min(100, Math.round(86400000 / timeRange * 100));

    chart.setOption({
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(17,24,39,.95)',
        borderColor: 'rgba(255,255,255,.1)',
        textStyle: { color: '#E2E8F0', fontSize: 11 }
      },
      legend: {
        data: ['综合', '情绪', '板块', '筹码', '隔夜'],
        bottom: 0,
        textStyle: { color: '#94A3B8', fontSize: 10 },
        itemWidth: 12, itemHeight: 8,
        selected: { '情绪': false, '板块': false, '筹码': false, '隔夜': false }
      },
      grid: { top: 10, bottom: 40, left: 45, right: 20 },
      xAxis: {
        type: 'time',
        axisLine: { lineStyle: { color: 'rgba(255,255,255,.1)' } },
        axisLabel: { color: '#64748B', fontSize: 10, formatter: function (v) {
          var d = new Date(v);
          return (d.getMonth() + 1) + '/' + d.getDate() + ' ' + d.getHours().toString().padStart(2,'0') + ':' + d.getMinutes().toString().padStart(2,'0');
        }},
        splitLine: { show: false }
      },
      yAxis: {
        type: 'value', min: 0, max: 100,
        splitLine: { lineStyle: { color: 'rgba(255,255,255,.06)' } },
        axisLabel: { color: '#64748B', fontSize: 10 }
      },
      dataZoom: [
        {
          type: 'slider', bottom: 20, height: 16,
          start: 0, end: 100,
          minSpan: minSpanPct, maxSpan: maxSpanPct,
          borderColor: 'rgba(255,255,255,.08)',
          backgroundColor: 'rgba(255,255,255,.03)',
          dataBackground: {
            lineStyle: { color: 'rgba(79,125,243,.3)', width: 1 },
            areaStyle: { color: 'rgba(79,125,243,.08)' }
          },
          selectedDataBackground: {
            lineStyle: { color: '#4F7DF3', width: 1.5 },
            areaStyle: { color: 'rgba(79,125,243,.15)' }
          },
          handleStyle: { color: '#4F7DF3', borderColor: '#4F7DF3' },
          textStyle: { color: '#64748B', fontSize: 9 },
          moveHandleSize: 6, handleSize: '80%'
        },
        { type: 'inside', minSpan: minSpanPct, maxSpan: maxSpanPct }
      ],
      series: [
        {
          name: '综合', type: 'line', data: compVals, smooth: true,
          lineStyle: { color: '#4F7DF3', width: 2.5 },
          areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [{ offset: 0, color: 'rgba(79,125,243,.25)' }, { offset: 1, color: 'rgba(79,125,243,.02)' }] } },
          symbol: 'none'
        },
        {
          name: '情绪', type: 'line', data: sentVals, smooth: true,
          lineStyle: { color: '#F59E0B', width: 1.5, type: 'dashed' }, symbol: 'none'
        },
        {
          name: '板块', type: 'line', data: sectVals, smooth: true,
          lineStyle: { color: '#10B981', width: 1.5, type: 'dashed' }, symbol: 'none'
        },
        {
          name: '筹码', type: 'line', data: chipVals, smooth: true,
          lineStyle: { color: '#EF4444', width: 1.5, type: 'dashed' }, symbol: 'none'
        },
        {
          name: '隔夜', type: 'line', data: overVals, smooth: true,
          lineStyle: { color: '#8B5CF6', width: 1.5, type: 'dashed' }, symbol: 'none'
        }
      ],
      backgroundColor: 'transparent'
    });
    S.charts.sentiment = chart;
  }
};

document.addEventListener('DOMContentLoaded', function () { S.init(); });
