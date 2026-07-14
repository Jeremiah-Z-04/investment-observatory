/* ============================================================
   投资观察站 · Animation Enhancement Module v2.0
   基于 anime.js · iOS 级非线性动效增强
   
   加载方式: 在 app.js 后添加 <script src="anime-plus.js"></script>
   自动注册到 A 命名空间，扩展动画能力但不覆盖已有方法
   ============================================================ */

(function () {
  'use strict';

  // Wait for A namespace to exist
  var initTimer = setInterval(function () {
    if (typeof A !== 'undefined' && typeof anime !== 'undefined') {
      clearInterval(initTimer);
      init();
    }
  }, 50);

  // Timeout safety net
  setTimeout(function () { clearInterval(initTimer); }, 5000);

  function init() {
    // ===== Card 3D Tilt Effect =====
    A.cardTilt = function (el, intensity) {
      if (!el) return;
      if (typeof el === 'string') el = document.querySelector(el);
      if (!el) return;
      intensity = intensity || 8;

      el.addEventListener('mousemove', function (e) {
        var rect = el.getBoundingClientRect();
        var x = e.clientX - rect.left;
        var y = e.clientY - rect.top;
        var centerX = rect.width / 2;
        var centerY = rect.height / 2;
        var rotateX = ((y - centerY) / centerY) * -intensity;
        var rotateY = ((x - centerX) / centerX) * intensity;

        anime({
          targets: el,
          rotateX: rotateX,
          rotateY: rotateY,
          scale: 1.02,
          easing: 'easeOutExpo',
          duration: 400
        });

        // Light reflection effect
        var pctX = (x / rect.width) * 100;
        var pctY = (y / rect.height) * 100;
        el.style.backgroundImage =
          'radial-gradient(circle at ' + pctX + '% ' + pctY + '%, rgba(79,125,243,0.08) 0%, transparent 60%)';
      });

      el.addEventListener('mouseleave', function () {
        anime({
          targets: el,
          rotateX: 0,
          rotateY: 0,
          scale: 1,
          easing: 'easeOutExpo',
          duration: 600
        });
        el.style.backgroundImage = '';
      });
    };

    // ===== Shimmer Skeleton Loading =====
    A.shimmer = function (container, opts) {
      if (!container) return;
      if (typeof container === 'string') container = document.querySelector(container);
      if (!container) return;
      opts = opts || {};
      var rows = opts.rows || 5;
      var gap = opts.gap || 8;
      var widths = opts.widths || ['100%', '80%', '90%', '60%', '70%'];

      var html = '';
      for (var i = 0; i < rows; i++) {
        var w = widths[i % widths.length];
        html += '<div class="skeleton" style="height:14px;width:' + w + ';margin-bottom:' + gap + 'px"></div>';
      }
      container.innerHTML = html;
    };

    // ===== Counter Up with Easing =====
    A.counterUp = function (el, target, duration) {
      if (!el) return;
      if (typeof el === 'string') el = document.querySelector(el);
      if (!el) return;
      target = target || 0;
      duration = duration || 1500;

      var obj = { val: 0 };
      anime({
        targets: obj,
        val: target,
        round: 1,
        easing: 'easeOutExpo',
        duration: duration,
        update: function () {
          el.textContent = Math.round(obj.val).toLocaleString();
        }
      });
    };

    // ===== Breathe / Pulse (continuous) =====
    A.breathe = function (el, opts) {
      if (!el) return;
      if (typeof el === 'string') el = document.querySelector(el);
      if (!el) return;
      opts = opts || {};
      var scale = opts.scale || 1.05;
      var duration = opts.duration || 2000;

      anime({
        targets: el,
        scale: [1, scale, 1],
        easing: 'easeInOutSine',
        duration: duration,
        loop: true,
        direction: 'alternate'
      });
    };

    // ===== Typewriter Effect =====
    A.typewriter = function (el, text, speed, delay) {
      if (!el) return;
      if (typeof el === 'string') el = document.querySelector(el);
      if (!el) return;
      speed = speed || 40;
      delay = delay || 0;
      el.textContent = '';
      var chars = text.split('');
      var i = 0;

      setTimeout(function () {
        var timer = setInterval(function () {
          if (i < chars.length) {
            el.textContent += chars[i];
            i++;
          } else {
            clearInterval(timer);
          }
        }, speed);
      }, delay);
    };

    // ===== Glitch Effect =====
    A.glitch = function (el, cycles) {
      if (!el) return;
      if (typeof el === 'string') el = document.querySelector(el);
      if (!el) return;
      cycles = cycles || 3;

      var orig = el.textContent;
      var chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&*';
      var current = 0;

      function scramble() {
        if (current >= cycles) {
          el.textContent = orig;
          return;
        }
        var scrambled = '';
        for (var i = 0; i < orig.length; i++) {
          if (Math.random() < 0.3 + current * 0.2) {
            scrambled += orig[i];
          } else {
            scrambled += chars[Math.floor(Math.random() * chars.length)];
          }
        }
        el.textContent = scrambled;
        current++;
        setTimeout(scramble, 80 + current * 40);
      }
      scramble();
    };

    // ===== Draw SVG Path =====
    A.drawPath = function (el, duration) {
      if (!el) return;
      if (typeof el === 'string') el = document.querySelector(el);
      if (!el) return;
      duration = duration || 1500;

      var paths = el.querySelectorAll('path, circle, rect, line, polyline');
      for (var i = 0; i < paths.length; i++) {
        var path = paths[i];
        var len = path.getTotalLength ? path.getTotalLength() : 200;
        path.style.strokeDasharray = len;
        path.style.strokeDashoffset = len;
        anime({
          targets: path,
          strokeDashoffset: [len, 0],
          easing: 'easeInOutSine',
          duration: duration,
          delay: i * 100
        });
      }
    };

    // ===== Wave Animation for Charts =====
    A.waveChart = function (chart, data, duration) {
      if (!chart || !data) return;
      duration = duration || 600;
      var currentOption = chart.getOption();
      if (!currentOption || !currentOption.series || !currentOption.series[0]) return;

      var newData = data;
      if (currentOption.series[0].data && currentOption.series[0].data.length === newData.length) {
        // Animate existing data points
        var startData = currentOption.series[0].data.slice();
        var obj = { progress: 0 };
        anime({
          targets: obj,
          progress: 1,
          easing: 'easeOutExpo',
          duration: duration,
          update: function () {
            var p = obj.progress;
            var interp = startData.map(function (val, i) {
              if (typeof val === 'number' && typeof newData[i] === 'number') {
                return val + (newData[i] - val) * p;
              }
              return newData[i];
            });
            chart.setOption({ series: [{ data: interp }] });
          }
        });
      }
    };

    // ===== Tap Ripple =====
    A.rippleAdvanced = function (e) {
      var target = e.currentTarget;
      var rect = target.getBoundingClientRect();
      var x = e.clientX - rect.left;
      var y = e.clientY - rect.top;
      var size = Math.max(rect.width, rect.height) * 2;

      var ripple = document.createElement('span');
      ripple.style.cssText =
        'position:absolute;left:' + (x - size / 2) + 'px;top:' + (y - size / 2) + 'px;' +
        'width:' + size + 'px;height:' + size + 'px;' +
        'border-radius:50%;background:rgba(79,125,243,0.25);' +
        'transform:scale(0);pointer-events:none;z-index:1;';

      target.style.position = target.style.position || 'relative';
      target.style.overflow = 'hidden';
      target.appendChild(ripple);

      anime({
        targets: ripple,
        scale: [0, 1],
        opacity: [1, 0],
        easing: 'easeOutExpo',
        duration: 600,
        complete: function () { ripple.remove(); }
      });
    };

    // ===== Elastic Scale on Click =====
    A.elasticTap = function (el) {
      if (!el) return;
      if (typeof el === 'string') el = document.querySelector(el);
      if (!el) return;
      anime({
        targets: el,
        scale: [1, 0.94, 1.02, 1],
        easing: 'easeInOutBack',
        duration: 300
      });
    };

    // ===== Infinite Floating Animation =====
    A.float = function (el, opts) {
      if (!el) return;
      if (typeof el === 'string') el = document.querySelector(el);
      if (!el) return;
      opts = opts || {};
      var y = opts.y || 8;
      var duration = opts.duration || 3000;

      anime({
        targets: el,
        translateY: [0, -y, 0],
        easing: 'easeInOutSine',
        duration: duration,
        loop: true
      });
    };

    // ===== Page Reveal (curtain) =====
    A.pageReveal = function (container, direction) {
      if (!container) return;
      if (typeof container === 'string') container = document.querySelector(container);
      if (!container) return;
      direction = direction || 'up';
      var fromY = direction === 'up' ? 30 : direction === 'down' ? -30 : 0;
      var fromX = direction === 'left' ? 30 : direction === 'right' ? -30 : 0;

      var children = container.children;
      anime({
        targets: children,
        opacity: [0, 1],
        translateY: [fromY, 0],
        translateX: [fromX, 0],
        easing: 'easeOutExpo',
        duration: 600,
        delay: anime.stagger(50, { start: 100 })
      });
    };

    // ===== Notification Slide In =====
    A.notify = function (msg, type) {
      type = type || 'info';
      var el = document.createElement('div');
      el.className = 'toast';
      var colors = { info: 'var(--accent)', success: 'var(--down)', warning: 'var(--warn)', error: 'var(--up)' };
      var borderColor = colors[type] || colors.info;
      el.style.cssText =
        'position:fixed;top:80px;right:24px;z-index:3000;' +
        'background:var(--surface-raised);color:var(--text-primary);' +
        'padding:12px 20px;border-radius:12px;' +
        'border:1px solid var(--glass-border);' +
        'border-left:3px solid ' + borderColor + ';' +
        'box-shadow:var(--shadow-lg);font-size:var(--text-sm);font-weight:600;' +
        'max-width:360px;opacity:0;transform:translateX(40px);';

      el.textContent = msg;
      document.body.appendChild(el);

      anime({
        targets: el,
        opacity: [0, 1],
        translateX: [40, 0],
        easing: 'easeOutExpo',
        duration: 400,
        complete: function () {
          setTimeout(function () {
            anime({
              targets: el,
              opacity: [1, 0],
              translateX: [0, 20],
              easing: 'easeInQuart',
              duration: 300,
              complete: function () { el.remove(); }
            });
          }, 3000);
        }
      });
    };

    console.log('[Animation+] Enhanced animation module loaded. ' + Object.keys(A).length + ' animation methods available.');
  }
})();
