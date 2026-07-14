# -*- coding: utf-8 -*-
"""Unit tests for scoring.py - 五维量化打分引擎"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import scoring


class TestGapRate:
    def test_high_gap(self):
        assert scoring.score_gap_rate(35) == 100

    def test_medium_high_gap(self):
        assert scoring.score_gap_rate(25) == 85

    def test_medium_gap(self):
        assert scoring.score_gap_rate(15) == 70

    def test_low_gap(self):
        assert scoring.score_gap_rate(5) == 50

    def test_negative_gap(self):
        assert scoring.score_gap_rate(-10) == 30


class TestOrderBacklog:
    def test_very_long(self):
        assert scoring.score_order_backlog(20) == 100

    def test_long(self):
        assert scoring.score_order_backlog(15) == 85

    def test_medium(self):
        assert scoring.score_order_backlog(8) == 70

    def test_short(self):
        assert scoring.score_order_backlog(5) == 50

    def test_none(self):
        assert scoring.score_order_backlog(1) == 30


class TestSpotPrice:
    def test_high_inflation(self):
        assert scoring.score_spot_price_mom(15) == 100

    def test_medium_inflation(self):
        assert scoring.score_spot_price_mom(7) == 85

    def test_flat(self):
        assert scoring.score_spot_price_mom(2) == 70

    def test_slight_deflation(self):
        assert scoring.score_spot_price_mom(-2) == 50

    def test_deflation(self):
        assert scoring.score_spot_price_mom(-10) == 30


class TestOrderRevenue:
    def test_very_high(self):
        assert scoring.score_order_revenue_ratio(4) == 100

    def test_high(self):
        assert scoring.score_order_revenue_ratio(2.5) == 85

    def test_medium(self):
        assert scoring.score_order_revenue_ratio(1.5) == 70

    def test_low(self):
        assert scoring.score_order_revenue_ratio(0.6) == 50

    def test_very_low(self):
        assert scoring.score_order_revenue_ratio(0.2) == 30


class TestCustomerConcentration:
    def test_low_concentration(self):
        assert scoring.score_customer_concentration(30) == 100

    def test_medium_low(self):
        assert scoring.score_customer_concentration(60) == 85

    def test_medium_high(self):
        assert scoring.score_customer_concentration(80) == 70

    def test_high(self):
        assert scoring.score_customer_concentration(95) == 50


class TestOverseasRevenue:
    def test_high_overseas(self):
        assert scoring.score_overseas_revenue(60) == 100

    def test_medium_overseas(self):
        assert scoring.score_overseas_revenue(35) == 85

    def test_low_overseas(self):
        assert scoring.score_overseas_revenue(15) == 70

    def test_domestic(self):
        assert scoring.score_overseas_revenue(5) == 30


class TestProfitGrowth:
    def test_explosive_growth(self):
        assert scoring.score_profit_growth(250) == 100

    def test_strong_growth(self):
        assert scoring.score_profit_growth(120) == 85

    def test_medium_growth(self):
        assert scoring.score_profit_growth(60) == 70

    def test_modest_growth(self):
        assert scoring.score_profit_growth(35) == 50

    def test_weak_growth(self):
        assert scoring.score_profit_growth(10) == 30


class TestPEG:
    def test_cheap(self):
        assert scoring.score_peg(0.3) == 100

    def test_fair(self):
        assert scoring.score_peg(0.8) == 85

    def test_slightly_high(self):
        assert scoring.score_peg(1.2) == 70

    def test_high(self):
        assert scoring.score_peg(1.8) == 50

    def test_very_high(self):
        assert scoring.score_peg(2.5) == 30


class TestEarningsSurprise:
    def test_big_surprise(self):
        assert scoring.score_earnings_surprise(40) == 100

    def test_moderate_surprise(self):
        assert scoring.score_earnings_surprise(15) == 85

    def test_inline(self):
        assert scoring.score_earnings_surprise(5) == 70

    def test_slight_miss(self):
        assert scoring.score_earnings_surprise(-5) == 50

    def test_big_miss(self):
        assert scoring.score_earnings_surprise(-20) == 30


class TestNationalStrategy:
    def test_yes(self):
        assert scoring.score_national_strategy(True) == 100

    def test_no(self):
        assert scoring.score_national_strategy(False) == 50


class TestLocalizationGap:
    def test_huge_gap(self):
        assert scoring.score_localization_gap(80) == 100

    def test_large_gap(self):
        assert scoring.score_localization_gap(60) == 85

    def test_medium_gap(self):
        assert scoring.score_localization_gap(40) == 70

    def test_small_gap(self):
        assert scoring.score_localization_gap(20) == 50


class TestNorthbound:
    def test_strong_inflow(self):
        assert scoring.score_northbound_monthly(3) == 100

    def test_positive_inflow(self):
        assert scoring.score_northbound_monthly(1.5) == 85

    def test_flat(self):
        assert scoring.score_northbound_monthly(0.2) == 70

    def test_slight_outflow(self):
        assert scoring.score_northbound_monthly(-0.5) == 50

    def test_outflow(self):
        assert scoring.score_northbound_monthly(-2) == 30


class TestETFGrowth:
    def test_strong_etf(self):
        assert scoring.score_etf_growth(15) == 100

    def test_positive_etf(self):
        assert scoring.score_etf_growth(7) == 85

    def test_flat_etf(self):
        assert scoring.score_etf_growth(2) == 70

    def test_slight_outflow(self):
        assert scoring.score_etf_growth(-2) == 50

    def test_outflow(self):
        assert scoring.score_etf_growth(-10) == 30
