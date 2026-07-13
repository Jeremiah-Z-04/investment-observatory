# -*- coding: utf-8 -*-
"""supabase_service.py -- Supabase optional integration layer (stdlib only)"""

import os, json, time
import urllib.request, urllib.parse, ssl

class SupabaseClient:
    """Minimal Supabase REST API client using Python stdlib only"""

    def __init__(self, url, anon_key, service_role_key=None):
        self.url = url.rstrip('/')
        self.anon_key = anon_key
        self.service_key = service_role_key or anon_key
        self._ctx = ssl.create_default_context()

    def _headers(self, use_service=False):
        key = self.service_key if use_service else self.anon_key
        return {
            'apikey': key,
            'Authorization': 'Bearer ' + key,
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal'
        }

    def _request(self, method, path, data=None, use_service=False):
        url = self.url + '/rest/v1/' + path
        body = None
        if data is not None:
            body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        req = urllib.request.Request(url, data=body, method=method,
                                     headers=self._headers(use_service))
        try:
            resp = urllib.request.urlopen(req, timeout=10, context=self._ctx)
            raw = resp.read().decode('utf-8')
            return json.loads(raw) if raw and resp.status != 204 else None
        except Exception as e:
            print('[supabase] request error: ' + str(e))
            return None

    def insert(self, table, data, use_service=True):
        if isinstance(data, list):
            # Batch insert via POST with Prefer: return=minimal
            return self._request('POST', table, data, use_service)
        return self._request('POST', table, data, use_service)

    def select(self, table, columns='*', filters=None, order=None, limit=100):
        query = table + '?select=' + urllib.parse.quote(columns)
        if filters:
            for k, v in filters.items():
                query += '&' + urllib.parse.quote(k) + '=' + urllib.parse.quote(str(v))
        if order:
            query += '&order=' + urllib.parse.quote(order)
        query += '&limit=' + str(limit)
        return self._request('GET', query, use_service=False)


# --- Global client and state ---
_supabase = None
_connection_state = {"available": False, "checked_at": 0}
_CONN_CHECK_TTL = 30

_sync_state = {
    "last_sync_time": None,
    "last_sync_success": False,
    "consecutive_errors": 0,
    "total_synced": 0
}

def check_connection():
    """Real connection check -- pings Supabase REST API to verify reachability"""
    if _supabase is None:
        return False
    try:
        result = _supabase.select('factor_scores', columns='id', limit=1)
        # result is None on HTTP error, [] on empty table (both OK for connectivity)
        return result is not None
    except Exception:
        return False

def is_available():
    """Check if Supabase is available, with 30s caching to avoid excessive pings"""
    global _connection_state
    now = time.time()
    if now - _connection_state["checked_at"] < _CONN_CHECK_TTL:
        return _connection_state["available"]
    _connection_state["checked_at"] = now
    _connection_state["available"] = check_connection()
    return _connection_state["available"]

def record_sync_result(success):
    """Record sync outcome for health tracking"""
    global _sync_state
    if success:
        _sync_state["last_sync_time"] = time.time()
        _sync_state["last_sync_success"] = True
        _sync_state["consecutive_errors"] = 0
        _sync_state["total_synced"] += 1
    else:
        _sync_state["last_sync_success"] = False
        _sync_state["consecutive_errors"] += 1

def get_status():
    """Get full Supabase connection and sync health status"""
    return {
        "connected": check_connection() if _supabase else False,
        "configured": _supabase is not None,
        "last_sync": time.strftime("%H:%M:%S", time.localtime(_sync_state["last_sync_time"])) if _sync_state["last_sync_time"] else None,
        "last_sync_success": _sync_state["last_sync_success"],
        "consecutive_errors": _sync_state["consecutive_errors"],
        "total_synced": _sync_state["total_synced"]
    }

def init_supabase():
    global _supabase
    if _supabase is not None:
        return check_connection()

    url = os.environ.get('SUPABASE_URL', '')
    anon_key = os.environ.get('SUPABASE_ANON_KEY', '')
    service_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')

    # Try .env file if env vars not set
    if not url:
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
        if os.path.exists(env_path):
            try:
                for line in open(env_path, encoding='utf-8'):
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split('=', 1)
                        if k.strip() == 'SUPABASE_URL':
                            url = v.strip()
                        elif k.strip() == 'SUPABASE_ANON_KEY':
                            anon_key = v.strip()
                        elif k.strip() == 'SUPABASE_SERVICE_ROLE_KEY':
                            service_key = v.strip()
            except Exception:
                pass

    if url and anon_key:
        _supabase = SupabaseClient(url, anon_key, service_key)
        if check_connection():
            print('[supabase] connected and verified: ' + url)
            return True
        else:
            print('[supabase] client created but connection failed, check network')
            _supabase = None
            return False

    print('[supabase] not configured, running without remote database')
    return False


# ====================== Sync Functions ======================

def sync_factor_scores(composite, factors_list, outlook='neutral'):
    """Push factor scores to Supabase"""
    if not is_available():
        return False
    try:
        data = {
            'recorded_at': time.strftime('%Y-%m-%dT%H:%M:%S+08:00'),
            'date': time.strftime('%Y-%m-%d'),
            'composite': round(composite, 2),
            'sentiment': None, 'sector': None, 'chip': None, 'overnight': None,
            'outlook': outlook
        }
        for f in (factors_list or []):
            fid = f.get('id', '')
            score = f.get('score', None)
            if fid in data and score is not None:
                data[fid] = round(float(score), 2)
        _supabase.insert('factor_scores', data)
        record_sync_result(True)
        return True
    except Exception as e:
        print('[supabase] sync_factor_scores error: ' + str(e))
        record_sync_result(False)
        return False


def sync_volume_alerts(alert_list):
    """Batch push volume alerts"""
    if not is_available() or not alert_list:
        return False
    try:
        now = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
        batch = []
        for a in alert_list[:50]:
            batch.append({
                'alert_time': now,
                'date': time.strftime('%Y-%m-%d'),
                'code': str(a.get('code', '')),
                'name': str(a.get('name', '')),
                'price': a.get('price'),
                'change': a.get('change'),
                'volume': a.get('volume'),
                'amount': a.get('amount'),
                'sector': str(a.get('sector', '')),
                'ratio': a.get('ratio'),
                'trigger_time': str(a.get('trigger_time', ''))
            })
        if batch:
            _supabase.insert('volume_alerts', batch)
        record_sync_result(True)
        return True
    except Exception as e:
        print('[supabase] sync_volume_alerts error: ' + str(e))
        record_sync_result(False)
        return False


def sync_market_snapshot(market_data):
    """Push market overview snapshot"""
    if not is_available() or not market_data:
        return False
    try:
        data = {
            'snapshot_time': time.strftime('%Y-%m-%dT%H:%M:%S+08:00'),
            'date': time.strftime('%Y-%m-%d'),
            'sh_change': market_data.get('sh_change'),
            'sz_change': market_data.get('sz_change'),
            'cyb_change': market_data.get('cyb_change'),
            'turnover_total': market_data.get('turnover_total'),
            'rise_count': market_data.get('up_count') or market_data.get('riseCount'),
            'fall_count': market_data.get('down_count') or market_data.get('fallCount'),
            'limit_up_count': market_data.get('limit_up_count'),
            'limit_down_count': market_data.get('limit_down_count'),
            'bomb_rate': market_data.get('bomb_rate'),
            'northbound_net': market_data.get('northbound_net'),
            'composite_score': market_data.get('composite_score'),
            'max_board_height': market_data.get('max_board_height')
        }
        _supabase.insert('market_snapshots', data)
        record_sync_result(True)
        return True
    except Exception as e:
        print('[supabase] sync_market_snapshot error: ' + str(e))
        record_sync_result(False)
        return False


def sync_sector_rankings(sectors_list):
    """Batch push sector rankings"""
    if not is_available() or not sectors_list:
        return False
    try:
        now = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
        batch = []
        for i, s in enumerate(sectors_list[:50]):
            batch.append({
                'recorded_at': now,
                'date': time.strftime('%Y-%m-%d'),
                'sector_name': str(s.get('name', s.get('sector', ''))),
                'sector_code': str(s.get('code', '')),
                'change_pct': s.get('change'),
                'net_amount': s.get('net_amount'),
                'ranking': i + 1,
                'stock_count': s.get('count')
            })
        if batch:
            _supabase.insert('sector_rankings', batch)
        record_sync_result(True)
        return True
    except Exception as e:
        print('[supabase] sync_sector_rankings error: ' + str(e))
        record_sync_result(False)
        return False


# ====================== Query Functions ======================

def query_factor_history(date_from=None, date_to=None, limit=500):
    """Query historical factor scores"""
    if not is_available():
        return []
    try:
        filters = {}
        if date_from:
            filters['recorded_at'] = 'gte.' + str(date_from)
        if date_to:
            filters['date'] = 'lte.' + str(date_to)
        order = 'recorded_at.asc'
        result = _supabase.select('factor_scores',
            columns='recorded_at,date,composite,sentiment,sector,chip,overnight,outlook',
            filters=filters, order=order, limit=limit)
        return result or []
    except Exception as e:
        print('[supabase] query_factor_history error: ' + str(e))
        return []


def query_volume_alerts(date=None, limit=200):
    """Query volume alerts by date"""
    if not is_available():
        return []
    try:
        filters = {}
        if date:
            filters['date'] = 'eq.' + str(date)
        order = 'ratio.desc'
        result = _supabase.select('volume_alerts',
            columns='*', filters=filters, order=order, limit=limit)
        return result or []
    except Exception as e:
        print('[supabase] query_volume_alerts error: ' + str(e))
        return []


def query_market_snapshots(days=30, limit=200):
    """Query recent market snapshots"""
    if not is_available():
        return []
    try:
        from datetime import datetime, timedelta
        cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        filters = {'date': 'gte.' + cutoff}
        order = 'snapshot_time.desc'
        result = _supabase.select('market_snapshots',
            columns='*', filters=filters, order=order, limit=limit)
        return result or []
    except Exception as e:
        print('[supabase] query_market_snapshots error: ' + str(e))
        return []


def query_sector_rankings(date=None, limit=100):
    """Query sector rankings"""
    if not is_available():
        return []
    try:
        filters = {}
        if date:
            filters['date'] = 'eq.' + str(date)
        order = 'ranking.asc'
        result = _supabase.select('sector_rankings',
            columns='*', filters=filters, order=order, limit=limit)
        return result or []
    except Exception as e:
        print('[supabase] query_sector_rankings error: ' + str(e))
        return []
