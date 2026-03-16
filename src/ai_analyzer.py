"""
AI 分析模块 - 基于 Claude API 的智能分析
可扩展功能：新闻摘要、股票趋势分析、天气提醒、市场洞察等
"""
import os
import requests
from typing import Dict, List, Optional
from datetime import datetime


class AIAnalyzer:
    """AI 分析器 - 调用 Claude API 进行数据分析"""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.base_url = (base_url or os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com")).rstrip("/")
        self.model = model or os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
        self.enabled = bool(self.api_key)

        if not self.enabled:
            print("⚠️ AI 分析未启用：未配置 ANTHROPIC_API_KEY")

    def _call_api(self, system_prompt: str, user_prompt: str, max_tokens: int = 2000) -> str:
        """调用 Claude API"""
        if not self.enabled:
            return ""

        url = f"{self.base_url}/v1/messages"
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
            "Anthropic-Version": "2023-06-01"
        }
        data = {
            "model": self.model,
            "max_tokens": max_tokens,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}]
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=(30, 60))
            response.raise_for_status()
            result = response.json()
            return result["content"][0]["text"]
        except requests.exceptions.Timeout:
            print("⚠️ AI API 调用超时")
            return ""
        except requests.exceptions.HTTPError as e:
            print(f"⚠️ AI API HTTP 错误: {e.response.status_code}")
            return ""
        except Exception as e:
            print(f"⚠️ AI API 调用失败: {e}")
            return ""

    # ==================== 可扩展的 AI 功能 ====================

    def analyze_news(self, news_items: List[Dict], max_summary: int = 3) -> List[Dict]:
        """
        AI 新闻摘要分析
        为每条新闻生成一句话摘要，提取关键信息
        """
        if not self.enabled or not news_items:
            return news_items

        system_prompt = """你是财经新闻分析师。请为每条新闻生成简洁的一句话摘要，突出关键信息。
要求：
- 摘要控制在 30 字以内
- 突出数字、时间点、影响范围
- 使用中性客观的语气"""

        news_text = "\n".join([f"{i+1}. {n['title']} (来源: {n['source']})"
                               for i, n in enumerate(news_items[:max_summary])])

        user_prompt = f"""请为以下新闻生成摘要：

{news_text}

请按以下格式返回（每行一条）：
1. [摘要内容]
2. [摘要内容]
..."""

        response = self._call_api(system_prompt, user_prompt)

        # 解析响应，更新新闻项
        if response:
            summaries = [line.strip() for line in response.strip().split("\n") if line.strip()]
            for i, news in enumerate(news_items[:max_summary]):
                if i < len(summaries):
                    # 移除序号前缀
                    summary = summaries[i]
                    if ". " in summary[:3]:
                        summary = summary.split(". ", 1)[1]
                    news["ai_summary"] = summary

        return news_items

    def analyze_market_trend(self, indices: Dict, funds: List[Dict]) -> str:
        """
        AI 市场趋势分析
        基于指数和基金数据生成简短的市场点评
        """
        if not self.enabled:
            return ""

        system_prompt = """你是市场分析师。基于提供的股市数据，生成 2-3 句话的市场点评。
要求：
- 指出主要趋势（涨/跌/震荡）
- 提及关键数据支撑
- 语气专业但易懂
- 控制在 100 字以内"""

        # 构建数据描述
        market_data = []
        for market, items in indices.items():
            for item in items:
                if item.get("success"):
                    trend = "涨" if item.get("change", 0) > 0 else "跌"
                    market_data.append(f"{item['name']}: {item.get('price')} ({trend}{item.get('change_pct')}%)")

        if funds:
            fund_summary = [f"{f['name']}: {f.get('daily_change', '-')}" for f in funds[:2] if f.get("success")]
            market_data.extend(fund_summary)

        user_prompt = f"""今日市场数据：
{chr(10).join(market_data)}

请生成市场趋势点评。"""

        return self._call_api(system_prompt, user_prompt)

    def weather_advice(self, weather_data: List[Dict]) -> str:
        """
        AI 天气提醒
        基于天气数据生成穿衣/出行建议
        """
        if not self.enabled or not weather_data:
            return ""

        system_prompt = """你是生活助手。基于天气数据生成简短的出行/穿衣建议。
要求：
- 针对城市天气特点
- 给出实用建议（穿衣、带伞、防晒等）
- 语气亲切友好
- 控制在 50 字以内"""

        weather_desc = []
        for city in weather_data:
            if city.get("success"):
                current = city.get("current", {})
                weather_desc.append(
                    f"{city['name']}: {current.get('weather')} {current.get('temp')}°C, "
                    f"湿度{current.get('humidity')}%, 紫外线{city.get('uv', {}).get('category', '-')}")

        user_prompt = f"""今日天气：
{chr(10).join(weather_desc)}

请生成出行建议。"""

        return self._call_api(system_prompt, user_prompt)

    def generate_daily_insight(self, report_data: Dict) -> Dict:
        """
        生成日报 AI 洞察
        整合所有数据，生成关键洞察（可展示在日报中）
        """
        insights = {
            "market_comment": "",
            "weather_advice": "",
            "highlight": "",
            "enabled": self.enabled
        }

        if not self.enabled:
            return insights

        print("\n🤖 AI 分析中...")

        # 1. 市场趋势
        market_comment = self.analyze_market_trend(
            report_data.get("indices", {}),
            report_data.get("funds", [])
        )
        if market_comment:
            insights["market_comment"] = market_comment
            print("✅ 市场趋势分析完成")

        # 2. 天气建议
        weather_advice = self.weather_advice(report_data.get("weather", []))
        if weather_advice:
            insights["weather_advice"] = weather_advice
            print("✅ 天气建议生成完成")

        # 3. 今日亮点（可选）
        system_prompt = """你是财经编辑。基于今日数据，选出最重要的一个看点，用一句话概括。
要求：30字以内，抓人眼球但客观。"""

        highlight_prompt = f"""日期: {report_data.get('date')}
天气: {len(report_data.get('weather', []))} 个城市数据
股市: {len(report_data.get('indices', {}).get('us', []))} 个美股指数, {len(report_data.get('indices', {}).get('hk', []))} 个港股指数
新闻: {len(report_data.get('news', []))} 条热点

请生成今日亮点。"""

        highlight = self._call_api(system_prompt, highlight_prompt, max_tokens=100)
        if highlight:
            insights["highlight"] = highlight.strip()
            print("✅ 今日亮点生成完成")

        return insights
