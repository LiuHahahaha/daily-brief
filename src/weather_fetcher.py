"""
天气数据获取模块 - 和风天气 API
"""
import os
import requests
from typing import Dict, List, Optional


class WeatherFetcher:
    """和风天气数据获取器"""

    # 标准端点
    DEFAULT_BASE_URL = "https://devapi.qweather.com/v7"
    GEO_URL = "https://geoapi.qweather.com/v2"

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.getenv("QWEATHER_API_KEY")
        if not self.api_key:
            raise ValueError("需要提供和风天气 API Key")

        # 支持自定义域名，或使用环境变量 QWEATHER_BASE_URL
        custom_url = base_url or os.getenv("QWEATHER_BASE_URL")
        if custom_url:
            self.base_url = custom_url.rstrip("/")
            # 自定义域名需要添加 /v7 路径
            if not self.base_url.endswith("/v7"):
                self.base_url = f"{self.base_url}/v7"
            print(f"✅ 使用自定义 API 端点: {self.base_url}")
        else:
            self.base_url = self.DEFAULT_BASE_URL

    def get_current_weather(self, location_id: str) -> Dict:
        """获取实时天气"""
        url = f"{self.base_url}/weather/now"
        params = {
            "location": location_id,
            "key": self.api_key
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("code") != "200":
            raise Exception(f"API错误: {data.get('code')}")

        now = data.get("now", {})
        return {
            "temp": now.get("temp"),
            "feels_like": now.get("feelsLike"),
            "weather": now.get("text"),
            "weather_icon": now.get("icon"),
            "wind_dir": now.get("windDir"),
            "wind_scale": now.get("windScale"),
            "humidity": now.get("humidity"),
            "pressure": now.get("pressure"),
            "visibility": now.get("vis")
        }

    def get_air_quality(self, location_id: str) -> Dict:
        """获取空气质量"""
        url = f"{self.base_url}/air/now"
        params = {
            "location": location_id,
            "key": self.api_key
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("code") != "200":
            return {"aqi": "-", "category": "-", "pm25": "-"}

        air = data.get("now", {})
        return {
            "aqi": air.get("aqi"),
            "category": air.get("category"),
            "pm25": air.get("pm2p5"),
            "pm10": air.get("pm10")
        }

    def get_uv_index(self, location_id: str) -> Dict:
        """获取紫外线指数"""
        url = f"{self.base_url}/indices/1d"
        params = {
            "location": location_id,
            "key": self.api_key,
            "type": "5"  # 紫外线指数
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("code") != "200" or not data.get("daily"):
            return {"uv": "-", "category": "-"}

        daily = data["daily"][0]
        return {
            "uv": daily.get("level"),
            "category": daily.get("category")
        }

    def get_daily_forecast(self, location_id: str) -> Dict:
        """获取当日预报（最高/最低温度）"""
        url = f"{self.base_url}/weather/3d"
        params = {
            "location": location_id,
            "key": self.api_key
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("code") != "200" or not data.get("daily"):
            return {"temp_max": "-", "temp_min": "-"}

        today = data["daily"][0]
        return {
            "temp_max": today.get("tempMax"),
            "temp_min": today.get("tempMin"),
            "day_weather": today.get("textDay"),
            "night_weather": today.get("textNight")
        }

    def get_city_weather(self, city_name: str, location_id: str) -> Dict:
        """获取单个城市的完整天气信息"""
        errors = []

        # 获取实时天气（必需）
        try:
            current = self.get_current_weather(location_id)
        except Exception as e:
            return {
                "name": city_name,
                "error": f"实时天气获取失败: {e}",
                "success": False
            }

        # 获取预报（可选）
        try:
            forecast = self.get_daily_forecast(location_id)
        except Exception as e:
            forecast = {"temp_max": "-", "temp_min": "-"}
            errors.append(f"预报: {e}")

        # 获取空气质量（可选，部分订阅不支持）
        try:
            air = self.get_air_quality(location_id)
        except Exception as e:
            air = {"aqi": "-", "category": "暂无数据", "pm25": "-"}
            errors.append(f"空气质量: {e}")

        # 获取紫外线（可选）
        try:
            uv = self.get_uv_index(location_id)
        except Exception as e:
            uv = {"uv": "-", "category": "-"}
            errors.append(f"紫外线: {e}")

        result = {
            "name": city_name,
            "current": current,
            "forecast": forecast,
            "air": air,
            "uv": uv,
            "success": True
        }

        if errors:
            result["warnings"] = errors

        return result

    def get_all_cities_weather(self, cities: List[Dict]) -> List[Dict]:
        """获取所有城市的天气"""
        results = []
        for city in cities:
            weather = self.get_city_weather(city["name"], city["id"])
            results.append(weather)
        return results
