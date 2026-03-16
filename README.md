# 📊 每日早报

每日自动生成的金融天气日报，包含重点城市天气、全球股市指数、基金动态和热点资讯。

## 🌐 在线访问

**GitHub Pages**: https://你的用户名.github.io/daily-report/

## 📋 日报内容

- **🌤️ 天气**: 武汉、东莞、光山三城市的天气、温度、湿度、空气质量、紫外线
- **📈 美股**: 道琼斯、纳斯达克、标普500
- **🌏 亚太**: 恒生指数、中证500
- **📊 基金**: 热门ETF净值追踪
- **🔥 资讯**: 全球财经热点

## 🚀 部署指南

### 1. Fork 或创建仓库

将代码推送到你的 GitHub 仓库。

### 2. 配置 Secrets

在仓库 Settings → Secrets and variables → Actions 中添加:

| Secret | 说明 | 获取方式 |
|--------|------|---------|
| `QWEATHER_API_KEY` | 和风天气API密钥 | https://dev.qweather.com/ |
| `NEWSAPI_KEY` | 新闻API密钥(可选) | https://newsapi.org/ |

### 3. 启用 GitHub Pages

Settings → Pages → Source 选择 "GitHub Actions"。

### 4. 手动触发

Actions → Daily Report Generator → Run workflow

## ⏰ 自动更新

每天北京时间 8:00 自动刷新数据。

## 🛠️ 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export QWEATHER_API_KEY="your_api_key"
export QWEATHER_BASE_URL="your_custom_domain"  # 如果使用自定义域名
export NEWSAPI_KEY="your_api_key"

# (可选) 启用 AI 分析功能
export ANTHROPIC_API_KEY="your_anthropic_key"

# 生成日报
python main.py

# 查看结果
open docs/index.html
```

## 📁 项目结构

```
daily-report/
├── .github/workflows/    # GitHub Actions 配置
├── docs/                 # GitHub Pages 源文件
│   ├── index.html       # 主页面（自动生成）
│   └── archive/         # 历史归档
├── src/                  # 源代码
│   ├── weather_fetcher.py
│   ├── finance_fetcher.py
│   ├── news_fetcher.py
│   └── report_generator.py
├── config.json          # 配置文件
├── main.py              # 主程序
└── requirements.txt     # 依赖
```

## 🤖 AI 能力（可选）

日报支持集成 Claude API，提供智能分析：

| 功能 | 说明 |
|------|------|
| **新闻摘要** | 为热点新闻生成一句话摘要 |
| **市场点评** | 基于股市数据生成趋势分析 |
| **天气建议** | 根据天气生成出行/穿衣建议 |
| **每日亮点** | 自动提炼今日最重要看点 |

### 启用 AI 功能

1. 获取 Anthropic API Key: https://console.anthropic.com/
2. 设置环境变量:
   ```bash
   export ANTHROPIC_API_KEY="your_key"
   export ANTHROPIC_MODEL="claude-sonnet-4-6"  # 可选，默认 claude-sonnet-4-6
   ```
3. 编辑 `config.json` 启用功能:
   ```json
   {
     "ai": {
       "enabled": true,
       "features": {
         "news_summary": true,
         "market_trend": true,
         "weather_advice": true,
         "daily_insight": true
       }
     }
   }
   ```

## 📝 自定义配置

编辑 `config.json`:

```json
{
  "weather": {
    "cities": [
      {"name": "城市名", "id": "城市代码"}
    ]
  },
  "finance": {
    "indices": [
      {"name": "指数名", "symbol": "代码", "market": "us/hk/cn"}
    ],
    "funds": [
      {"name": "基金名", "code": "基金代码"}
    ]
  }
}
```

城市代码查询: https://dev.qweather.com/docs/resource/glossary/#locationid

## 📄 License

MIT
