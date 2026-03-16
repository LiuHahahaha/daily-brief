"""
金融数据获取模块 - 纯 yfinance 版本
支持美股、港股、美股 ETF/基金
"""
import yfinance as yf
from typing import Dict, List, Optional
from datetime import datetime


class FinanceFetcher:
    """金融数据获取器（基于 yfinance）"""

    def __init__(self):
        pass

    def get_ticker_data(self, symbol: str, name: str, market: str = "us") -> Dict:
        """
        获取股票/指数/ETF 数据
        通用方法，支持所有 yfinance 支持的 ticker
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d")

            if len(hist) < 1:
                return {"name": name, "symbol": symbol, "error": "无数据", "success": False}

            latest = hist.iloc[-1]
            prev = hist.iloc[-2] if len(hist) >= 2 else latest

            current = latest["Close"]
            prev_close = prev["Close"]
            change = current - prev_close
            change_pct = (change / prev_close) * 100 if prev_close > 0 else 0

            return {
                "name": name,
                "symbol": symbol,
                "price": round(current, 2),
                "change": round(change, 2),
                "change_pct": round(change_pct, 2),
                "market": market,
                "success": True
            }
        except Exception as e:
            return {"name": name, "symbol": symbol, "error": str(e), "success": False}

    def get_etf_data(self, symbol: str, name: str) -> Dict:
        """
        获取 ETF 数据（美股 ETF）
        """
        data = self.get_ticker_data(symbol, name, market="us")
        if data.get("success"):
            data["type"] = "ETF"
        return data

    def get_all_indices(self, indices: List[Dict]) -> Dict[str, List[Dict]]:
        """
        获取所有指数数据
        支持: us(美股), hk(港股), cn(中概股)
        """
        results = {
            "us": [],
            "hk": [],
            "cn": []
        }

        for idx in indices:
            market = idx.get("market", "us")
            symbol = idx["symbol"]
            name = idx["name"]

            data = self.get_ticker_data(symbol, name, market)

            if market in results:
                results[market].append(data)
            else:
                # 默认放入 us
                results["us"].append(data)

        return results

    def get_all_funds(self, funds: List[Dict]) -> List[Dict]:
        """
        获取所有基金/ETF 数据
        美股 ETF 如 SPY, QQQ, VOO 等
        """
        results = []
        for fund in funds:
            data = self.get_etf_data(fund["symbol"], fund["name"])
            results.append(data)
        return results

    def get_market_summary(self) -> Dict:
        """
        获取市场概要数据
        包括主要指数和一些重要 ETF
        """
        # 核心指数
        core_indices = [
            {"name": "标普500", "symbol": "^GSPC", "market": "us"},
            {"name": "纳斯达克", "symbol": "^IXIC", "market": "us"},
            {"name": "道琼斯", "symbol": "^DJI", "market": "us"},
            {"name": "恒生指数", "symbol": "^HSI", "market": "hk"},
            {"name": "日经225", "symbol": "^N225", "market": "hk"},
        ]

        # 重要 ETF
        key_etfs = [
            {"name": "标普500 ETF", "symbol": "SPY"},
            {"name": "纳斯达克100 ETF", "symbol": "QQQ"},
            {"name": "中概股 ETF", "symbol": "KWEB"},
            {"name": "恒生科技 ETF", "symbol": "3033.HK"},
        ]

        summary = {
            "indices": [],
            "etfs": [],
            "updated_at": datetime.now().strftime("%H:%M")
        }

        for idx in core_indices:
            data = self.get_ticker_data(idx["symbol"], idx["name"], idx["market"])
            if data.get("success"):
                summary["indices"].append(data)

        for etf in key_etfs:
            data = self.get_etf_data(etf["symbol"], etf["name"])
            if data.get("success"):
                summary["etfs"].append(data)

        return summary
