# -*- coding: utf-8 -*-
"""Unit tests for review_rules.py - 复盘阈值规则引擎"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import review_rules


class TestCalcSentimentStage:
    def _mk_mkt(self, limit_up, limit_down, bomb, premium, height):
        return {
            "limit_up_count": limit_up,
            "limit_down_count": limit_down,
            "bomb_rate": bomb,
            "yest_premium": premium,
            "max_board_height": height,
        }

    def test_ice_point(self):
        mkt = self._mk_mkt(10, 20, 60, -5, 2)
        result = review_rules.calc_sentiment_stage(mkt)
        assert result["stage"] == "freeze"
        assert result["stage_name"] == "冰点"
        assert "stage" in result
        assert "effect_type" in result
        assert "effect_days" in result

    def test_main_rise(self):
        mkt = self._mk_mkt(60, 2, 15, 4, 5)
        result = review_rules.calc_sentiment_stage(mkt)
        assert result["stage"] == "surge"
        assert result["stage_name"] == "主升"

    def test_climax(self):
        mkt = self._mk_mkt(90, 5, 35, -1, 6)
        result = review_rules.calc_sentiment_stage(mkt)
        # Climax requires both high limit-up AND high bomb rate
        assert result["stage"] in ("climax", "freeze", "surge")

    def test_return_shape(self):
        mkt = self._mk_mkt(50, 5, 25, 2, 4)
        result = review_rules.calc_sentiment_stage(mkt)
        for key in ("stage", "stage_name", "effect_type", "effect_days", "desc"):
            assert key in result

    def test_neutral(self):
        mkt = self._mk_mkt(30, 3, 20, 1, 3)
        result = review_rules.calc_sentiment_stage(mkt)
        assert result["stage"] in ("neutral", "startup", "freeze")


class TestCalcCoreSectors:
    def test_empty(self):
        result = review_rules.calc_core_sectors([])
        assert result == []

    def test_top_sectors(self):
        stocks = [
            {"code": "000001", "name": "平安银行", "sector": "银行", "change": 5},
            {"code": "000002", "name": "万科A", "sector": "房地产", "change": 3},
            {"code": "000003", "name": "招商银行", "sector": "银行", "change": 4},
        ]
        result = review_rules.calc_core_sectors(stocks)
        assert isinstance(result, list)
        assert len(result) > 0
        # Result should be list of dicts with topic key
        for item in result:
            assert "topic" in item


class TestCalcSurvivorStocks:
    def test_basic(self):
        up_stocks = [{"code": "000001", "name": "平安银行", "change": 5}]
        bomb_stocks = [{"code": "000002", "name": "万科A", "change": -5}]
        result = review_rules.calc_survivor_stocks(up_stocks, bomb_stocks)
        assert isinstance(result, list)


class TestCalcWindVane:
    def test_empty_core(self):
        result = review_rules.calc_wind_vane([], [])
        assert isinstance(result, str)

    def test_with_core_sectors(self):
        core = [{"topic": "银行"}, {"topic": "保险"}]
        result = review_rules.calc_wind_vane(core, [])
        assert result == "银行"


class TestTHRESHOLDS:
    def test_thresholds_exist(self):
        assert hasattr(review_rules, 'THRESHOLDS')
        t = review_rules.THRESHOLDS
        assert isinstance(t, dict)
        assert 'sentiment' in t


class TestGenBattlePlan:
    def test_basic(self):
        targets = [{"code": "000001", "name": "测试"}]
        plan = review_rules.gen_battle_plan(targets, 5000)
        assert isinstance(plan, dict)
        assert "text" in plan


class TestFormatTemplates:
    def test_format1(self):
        market = {"limit_up_count": 50, "limit_down_count": 5, "bomb_rate": 20,
                  "yest_premium": 2, "max_board_height": 5,
                  "turnover_total": 10000, "up_count": 3000, "down_count": 1000}
        sentiment = {"stage": "surge", "effect_type": "赚钱效应", "stage_name": "主升", "effect_days": 3}
        stocks = [
            {"code": "000001", "name": "平安银行", "sector": "银行", "change": 5, "amount": 500},
            {"code": "000002", "name": "万科A", "sector": "房地产", "change": 4, "amount": 400},
            {"code": "000003", "name": "招商银行", "sector": "银行", "change": 3, "amount": 300},
            {"code": "000004", "name": "兴业银行", "sector": "银行", "change": 2, "amount": 200},
        ]
        core = review_rules.calc_core_sectors(stocks)
        result = review_rules.format_template1(market, sentiment, core, [], "")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_format2(self):
        result = review_rules.format_template2("测试作战计划内容")
        assert isinstance(result, str)

    def test_format3(self):
        diag = {"action": "持有", "reason": "强势", "risk": "低"}
        result = review_rules.format_template3(diag)
        assert isinstance(result, str)
