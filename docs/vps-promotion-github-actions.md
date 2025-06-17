# VPS促销信息GitHub Actions自动化方案

## 概述

本文档提供了使用GitHub Actions定时收集VPS促销信息的完整解决方案，包括工作流配置、Python脚本实现、数据存储和通知系统。

## GitHub Actions工作流配置

### 1. 主要工作流文件

创建 `.github/workflows/vps-promotion-collector.yml`：

```yaml
name: VPS Promotion Collector

on:
  schedule:
    # 每15分钟运行一次（促销信息实时性要求）
    - cron: '*/15 * * * *'
    # 每小时运行一次（常规监控）
    - cron: '0 * * * *'
    # 黑五期间每5分钟运行一次
    - cron: '*/5 * * * *'  # 可以通过条件控制

  # 手动触发
  workflow_dispatch:
    inputs:
      mode:
        description: '运行模式'
        required: true
        default: 'normal'
        type: choice
        options:
        - normal
        - black_friday
        - flash_sale

      sources:
        description: '数据源（逗号分隔）'
        required: false
        default: 'lowendbox,twitter,scraping'

  # 推送触发（用于测试）
  push:
    branches: [ main ]
    paths:
      - 'scripts/vps_promotion_collector.py'
      - '.github/workflows/vps-promotion-collector.yml'

env:
  PYTHON_VERSION: '3.9'
  TZ: 'UTC'

jobs:
  collect-promotions:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
      with:
        token: ${{ secrets.GITHUB_TOKEN }}
        fetch-depth: 0

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
        cache: 'pip'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Determine run mode
      id: mode
      run: |
        # 检查是否是黑五期间（11月第四个星期四到下周一）
        current_date=$(date +%Y-%m-%d)
        current_month=$(date +%m)
        current_day=$(date +%d)

        if [ "$current_month" = "11" ] && [ "$current_day" -ge "24" ] && [ "$current_day" -le "30" ]; then
          echo "mode=black_friday" >> $GITHUB_OUTPUT
          echo "frequency=high" >> $GITHUB_OUTPUT
        elif [ "${{ github.event.inputs.mode }}" != "" ]; then
          echo "mode=${{ github.event.inputs.mode }}" >> $GITHUB_OUTPUT
          echo "frequency=manual" >> $GITHUB_OUTPUT
        else
          echo "mode=normal" >> $GITHUB_OUTPUT
          echo "frequency=normal" >> $GITHUB_OUTPUT
        fi

    - name: Collect VPS promotions
      id: collect
      run: |
        python scripts/vps_promotion_collector.py \
          --mode ${{ steps.mode.outputs.mode }} \
          --sources "${{ github.event.inputs.sources || 'lowendbox,twitter,scraping' }}" \
          --output-dir data/promotions \
          --log-level INFO
      env:
        # API密钥从GitHub Secrets获取
        TWITTER_API_KEY: ${{ secrets.TWITTER_API_KEY }}
        TWITTER_API_SECRET: ${{ secrets.TWITTER_API_SECRET }}
        TWITTER_ACCESS_TOKEN: ${{ secrets.TWITTER_ACCESS_TOKEN }}
        TWITTER_ACCESS_TOKEN_SECRET: ${{ secrets.TWITTER_ACCESS_TOKEN_SECRET }}
        TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
        TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
        WEBHOOK_URL: ${{ secrets.WEBHOOK_URL }}

    - name: Process and analyze data
      id: analyze
      run: |
        python scripts/promotion_analyzer.py \
          --input-dir data/promotions \
          --output-file data/promotion_summary.json \
          --mode ${{ steps.mode.outputs.mode }}

    - name: Generate promotion report
      id: report
      run: |
        python scripts/generate_promotion_report.py \
          --data-file data/promotion_summary.json \
          --output-file data/promotion_report.md \
          --template templates/promotion_report_template.md

    - name: Check for high-value promotions
      id: check_alerts
      run: |
        python scripts/check_promotion_alerts.py \
          --data-file data/promotion_summary.json \
          --alert-rules config/alert_rules.json \
          --output-file data/alerts.json

    - name: Send notifications
      if: steps.check_alerts.outputs.has_alerts == 'true'
      run: |
        python scripts/send_notifications.py \
          --alerts-file data/alerts.json \
          --mode ${{ steps.mode.outputs.mode }}
      env:
        TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
        TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
        WEBHOOK_URL: ${{ secrets.WEBHOOK_URL }}
        EMAIL_SMTP_SERVER: ${{ secrets.EMAIL_SMTP_SERVER }}
        EMAIL_USERNAME: ${{ secrets.EMAIL_USERNAME }}
        EMAIL_PASSWORD: ${{ secrets.EMAIL_PASSWORD }}
        EMAIL_TO: ${{ secrets.EMAIL_TO }}

    - name: Commit and push data
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"

        # 添加新数据文件
        git add data/promotions/
        git add data/promotion_summary.json
        git add data/promotion_report.md

        # 检查是否有变更
        if git diff --staged --quiet; then
          echo "No changes to commit"
        else
          git commit -m "Update VPS promotions data - $(date '+%Y-%m-%d %H:%M:%S')"
          git push
        fi

    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: promotion-data-${{ github.run_number }}
        path: |
          data/promotions/
          data/promotion_summary.json
          data/promotion_report.md
          logs/
        retention-days: 30

  # 每日汇总任务
  daily-summary:
    runs-on: ubuntu-latest
    if: github.event.schedule == '0 0 * * *'  # 每天午夜运行
    needs: collect-promotions

    steps:
    - name: Checkout repository
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}

    - name: Generate daily summary
      run: |
        python scripts/generate_daily_summary.py \
          --date $(date +%Y-%m-%d) \
          --input-dir data/promotions \
          --output-file data/daily_summaries/$(date +%Y-%m-%d).md

    - name: Update README with latest promotions
      run: |
        python scripts/update_readme.py \
          --summary-file data/daily_summaries/$(date +%Y-%m-%d).md \
          --readme-file README.md

    - name: Commit daily summary
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add data/daily_summaries/
        git add README.md
        git commit -m "Daily VPS promotions summary - $(date +%Y-%m-%d)" || exit 0
        git push

  # 清理旧数据任务
  cleanup:
    runs-on: ubuntu-latest
    if: github.event.schedule == '0 2 * * 0'  # 每周日凌晨2点运行

    steps:
    - name: Checkout repository
      uses: actions/checkout@v4

    - name: Clean old data
      run: |
        # 删除30天前的促销数据
        find data/promotions -name "*.json" -mtime +30 -delete

        # 删除7天前的日志文件
        find logs -name "*.log" -mtime +7 -delete

        # 压缩旧的汇总数据
        find data/daily_summaries -name "*.md" -mtime +90 -exec gzip {} \;

    - name: Commit cleanup
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add -A
        git commit -m "Cleanup old promotion data - $(date +%Y-%m-%d)" || exit 0
        git push
```

### 2. 特殊事件工作流

创建 `.github/workflows/black-friday-monitor.yml`：

```yaml
name: Black Friday VPS Monitor

on:
  schedule:
    # 黑五期间每5分钟运行一次
    - cron: '*/5 * * * *'

  workflow_dispatch:

jobs:
  black-friday-monitor:
    runs-on: ubuntu-latest
    # 只在11月24-30日运行
    if: |
      (github.event.schedule &&
       contains('11', format('{0:MM}', github.event.repository.updated_at)) &&
       contains('24,25,26,27,28,29,30', format('{0:dd}', github.event.repository.updated_at))) ||
      github.event_name == 'workflow_dispatch'

    steps:
    - name: Checkout repository
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt

    - name: High-frequency promotion monitoring
      run: |
        python scripts/vps_promotion_collector.py \
          --mode black_friday \
          --sources "lowendbox,twitter,scraping,telegram" \
          --high-frequency \
          --alert-threshold 0.3
      env:
        TWITTER_API_KEY: ${{ secrets.TWITTER_API_KEY }}
        TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
        WEBHOOK_URL: ${{ secrets.WEBHOOK_URL }}

    - name: Immediate alert for flash sales
      run: |
        python scripts/flash_sale_detector.py \
          --input-dir data/promotions \
          --keywords "flash sale,limited time,24 hours,cyber monday"
```

## Python脚本实现

### 1. 主要收集脚本

创建 `scripts/vps_promotion_collector.py`：

```python
#!/usr/bin/env python3
"""
VPS促销信息收集器 - GitHub Actions版本
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import requests
import feedparser
from bs4 import BeautifulSoup
import time
import random

class VPSPromotionCollector:
    def __init__(self, mode='normal', sources=None):
        self.mode = mode
        self.sources = sources or ['lowendbox', 'twitter', 'scraping']
        self.output_dir = Path('data/promotions')
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 设置日志
        self.setup_logging()

        # 初始化会话
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; VPS-Promotion-Bot/1.0)'
        })

    def setup_logging(self):
        """设置日志"""
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / f'promotion_collector_{datetime.now().strftime("%Y%m%d")}.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

    def collect_lowendbox_promotions(self):
        """收集LowEndBox促销信息"""
        try:
            self.logger.info("Collecting LowEndBox promotions...")

            rss_url = "https://lowendbox.com/feed/"
            feed = feedparser.parse(rss_url)

            promotions = []
            for entry in feed.entries:
                promotion = {
                    'source': 'lowendbox',
                    'title': entry.title,
                    'link': entry.link,
                    'published': entry.published,
                    'summary': entry.summary,
                    'tags': [tag.term for tag in entry.tags] if hasattr(entry, 'tags') else [],
                    'collected_at': datetime.now().isoformat(),
                    'is_promotion': self.detect_promotion_keywords(entry.title + ' ' + entry.summary)
                }
                promotions.append(promotion)

            self.logger.info(f"Collected {len(promotions)} LowEndBox items")
            return promotions

        except Exception as e:
            self.logger.error(f"Error collecting LowEndBox promotions: {e}")
            return []

    def collect_twitter_promotions(self):
        """收集Twitter促销信息"""
        try:
            # 这里需要Twitter API v2
            # 由于GitHub Actions的限制，建议使用简化版本或RSS替代
            self.logger.info("Twitter collection skipped in GitHub Actions mode")
            return []

        except Exception as e:
            self.logger.error(f"Error collecting Twitter promotions: {e}")
            return []

    def collect_scraping_promotions(self):
        """网页爬虫收集促销信息"""
        try:
            self.logger.info("Collecting promotions via web scraping...")

            providers = {
                'bandwagonhost': 'https://bandwagonhost.com/vps-hosting.php',
                'racknerd': 'https://www.racknerd.com/',
                'hostdare': 'https://hostdare.com/'
            }

            promotions = []

            for provider, url in providers.items():
                try:
                    # 添加随机延迟避免被封
                    time.sleep(random.uniform(1, 3))

                    response = self.session.get(url, timeout=30)
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # 查找促销关键词
                    page_text = soup.get_text().lower()

                    if self.detect_promotion_keywords(page_text):
                        promotion = {
                            'source': 'scraping',
                            'provider': provider,
                            'url': url,
                            'title': soup.title.string if soup.title else f"{provider} promotions",
                            'content': page_text[:500],  # 前500字符
                            'collected_at': datetime.now().isoformat(),
                            'has_promotion': True
                        }
                        promotions.append(promotion)

                except Exception as e:
                    self.logger.warning(f"Error scraping {provider}: {e}")
                    continue

            self.logger.info(f"Collected {len(promotions)} scraping promotions")
            return promotions

        except Exception as e:
            self.logger.error(f"Error in web scraping: {e}")
            return []

    def detect_promotion_keywords(self, text):
        """检测促销关键词"""
        promotion_keywords = [
            'black friday', 'cyber monday', 'christmas sale',
            'new year sale', 'flash sale', 'limited time',
            'special offer', 'discount', 'promo code',
            'off', '%', 'deal', 'sale'
        ]

        text_lower = text.lower()
        return any(keyword in text_lower for keyword in promotion_keywords)

    def save_promotions(self, promotions, source_name):
        """保存促销数据"""
        if not promotions:
            return

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = self.output_dir / f"{source_name}_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(promotions, f, ensure_ascii=False, indent=2)

        self.logger.info(f"Saved {len(promotions)} promotions to {filename}")

    def run(self):
        """运行收集器"""
        self.logger.info(f"Starting VPS promotion collection in {self.mode} mode")
        self.logger.info(f"Sources: {', '.join(self.sources)}")

        all_promotions = []

        # 根据配置的数据源收集信息
        if 'lowendbox' in self.sources:
            promotions = self.collect_lowendbox_promotions()
            self.save_promotions(promotions, 'lowendbox')
            all_promotions.extend(promotions)

        if 'twitter' in self.sources:
            promotions = self.collect_twitter_promotions()
            self.save_promotions(promotions, 'twitter')
            all_promotions.extend(promotions)

        if 'scraping' in self.sources:
            promotions = self.collect_scraping_promotions()
            self.save_promotions(promotions, 'scraping')
            all_promotions.extend(promotions)

        # 保存汇总数据
        summary = {
            'mode': self.mode,
            'sources': self.sources,
            'total_promotions': len(all_promotions),
            'collected_at': datetime.now().isoformat(),
            'promotions': all_promotions
        }

        summary_file = self.output_dir / f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        self.logger.info(f"Collection completed. Total promotions: {len(all_promotions)}")

        # 设置GitHub Actions输出
        if 'GITHUB_OUTPUT' in os.environ:
            with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
                f.write(f"total_promotions={len(all_promotions)}\n")
                f.write(f"has_promotions={'true' if all_promotions else 'false'}\n")

def main():
    parser = argparse.ArgumentParser(description='VPS Promotion Collector')
    parser.add_argument('--mode', default='normal', choices=['normal', 'black_friday', 'flash_sale'])
    parser.add_argument('--sources', default='lowendbox,scraping')
    parser.add_argument('--output-dir', default='data/promotions')
    parser.add_argument('--log-level', default='INFO')

    args = parser.parse_args()

    # 解析数据源
    sources = [s.strip() for s in args.sources.split(',')]

    # 创建收集器并运行
    collector = VPSPromotionCollector(mode=args.mode, sources=sources)
    collector.run()

if __name__ == '__main__':
    main()
```

### 2. 促销分析脚本

创建 `scripts/promotion_analyzer.py`：

```python
#!/usr/bin/env python3
"""
促销数据分析器
"""

import argparse
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
import re
from collections import defaultdict

class PromotionAnalyzer:
    def __init__(self, input_dir, mode='normal'):
        self.input_dir = Path(input_dir)
        self.mode = mode
        self.logger = logging.getLogger(__name__)

        # 促销评分权重
        self.scoring_weights = {
            'discount_percentage': 0.4,
            'price_value': 0.3,
            'provider_reputation': 0.2,
            'urgency': 0.1
        }

    def load_recent_promotions(self, hours=24):
        """加载最近的促销数据"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        promotions = []

        for file_path in self.input_dir.glob('*.json'):
            try:
                # 从文件名提取时间戳
                timestamp_str = file_path.stem.split('_')[-2:]
                if len(timestamp_str) == 2:
                    timestamp = datetime.strptime(
                        f"{timestamp_str[0]}_{timestamp_str[1]}",
                        '%Y%m%d_%H%M%S'
                    )

                    if timestamp > cutoff_time:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            if isinstance(data, list):
                                promotions.extend(data)
                            elif isinstance(data, dict) and 'promotions' in data:
                                promotions.extend(data['promotions'])

            except Exception as e:
                self.logger.warning(f"Error loading {file_path}: {e}")

        return promotions

    def extract_discount_percentage(self, text):
        """提取折扣百分比"""
        # 查找百分比折扣
        percentage_match = re.search(r'(\d+)%\s*off', text.lower())
        if percentage_match:
            return int(percentage_match.group(1))

        # 查找其他折扣表达
        discount_patterns = [
            r'save\s+(\d+)%',
            r'(\d+)%\s*discount',
            r'(\d+)%\s*sale'
        ]

        for pattern in discount_patterns:
            match = re.search(pattern, text.lower())
            if match:
                return int(match.group(1))

        return 0

    def extract_price_info(self, text):
        """提取价格信息"""
        # 查找价格
        price_patterns = [
            r'\$(\d+(?:\.\d{2})?)',
            r'(\d+(?:\.\d{2})?)\s*dollars?',
            r'(\d+(?:\.\d{2})?)\s*usd'
        ]

        prices = []
        for pattern in price_patterns:
            matches = re.findall(pattern, text.lower())
            for match in matches:
                try:
                    prices.append(float(match))
                except ValueError:
                    continue

        return {
            'min_price': min(prices) if prices else None,
            'max_price': max(prices) if prices else None,
            'avg_price': sum(prices) / len(prices) if prices else None
        }

    def calculate_promotion_score(self, promotion):
        """计算促销评分"""
        score = 0
        text = f"{promotion.get('title', '')} {promotion.get('summary', '')} {promotion.get('content', '')}"

        # 折扣百分比评分
        discount = self.extract_discount_percentage(text)
        discount_score = min(discount * 2, 100)  # 最高100分
        score += discount_score * self.scoring_weights['discount_percentage']

        # 价格评分
        price_info = self.extract_price_info(text)
        if price_info['min_price']:
            # 价格越低分数越高
            price_score = max(0, 100 - price_info['min_price'])
            score += price_score * self.scoring_weights['price_value']

        # 服务商声誉评分
        provider_scores = {
            'bandwagonhost': 90,
            'racknerd': 85,
            'digitalocean': 95,
            'linode': 90,
            'vultr': 85,
            'hostdare': 75,
            'spartanhost': 70
        }

        provider = promotion.get('provider', '').lower()
        for p, s in provider_scores.items():
            if p in provider:
                score += s * self.scoring_weights['provider_reputation']
                break
        else:
            score += 50 * self.scoring_weights['provider_reputation']  # 默认分数

        # 紧急程度评分
        urgency_keywords = {
            'flash sale': 100,
            'limited time': 90,
            '24 hours': 95,
            '48 hours': 85,
            'today only': 100,
            'ends soon': 80
        }

        urgency_score = 0
        for keyword, keyword_score in urgency_keywords.items():
            if keyword in text.lower():
                urgency_score = max(urgency_score, keyword_score)

        score += urgency_score * self.scoring_weights['urgency']

        return round(score, 2)

    def categorize_promotions(self, promotions):
        """分类促销信息"""
        categories = {
            'black_friday': [],
            'cyber_monday': [],
            'christmas': [],
            'new_year': [],
            'flash_sale': [],
            'regular': []
        }

        category_keywords = {
            'black_friday': ['black friday', 'bf2024', 'black fri'],
            'cyber_monday': ['cyber monday', 'cm2024', 'cyber'],
            'christmas': ['christmas', 'xmas', 'holiday'],
            'new_year': ['new year', 'ny2025', '2025'],
            'flash_sale': ['flash sale', 'limited time', '24 hours', 'today only']
        }

        for promotion in promotions:
            text = f"{promotion.get('title', '')} {promotion.get('summary', '')}".lower()

            categorized = False
            for category, keywords in category_keywords.items():
                if any(keyword in text for keyword in keywords):
                    categories[category].append(promotion)
                    categorized = True
                    break

            if not categorized:
                categories['regular'].append(promotion)

        return categories

    def generate_summary(self, promotions):
        """生成促销汇总"""
        if not promotions:
            return {
                'total_promotions': 0,
                'categories': {},
                'top_promotions': [],
                'statistics': {}
            }

        # 计算评分
        for promotion in promotions:
            promotion['score'] = self.calculate_promotion_score(promotion)

        # 分类
        categories = self.categorize_promotions(promotions)

        # 排序获取Top促销
        top_promotions = sorted(promotions, key=lambda x: x['score'], reverse=True)[:10]

        # 统计信息
        statistics = {
            'total_promotions': len(promotions),
            'avg_score': sum(p['score'] for p in promotions) / len(promotions),
            'high_value_count': len([p for p in promotions if p['score'] > 70]),
            'sources': list(set(p.get('source', 'unknown') for p in promotions)),
            'providers': list(set(p.get('provider', 'unknown') for p in promotions if p.get('provider')))
        }

        return {
            'total_promotions': len(promotions),
            'categories': {k: len(v) for k, v in categories.items()},
            'top_promotions': top_promotions,
            'statistics': statistics,
            'analyzed_at': datetime.now().isoformat()
        }

    def run(self, output_file):
        """运行分析"""
        self.logger.info("Starting promotion analysis...")

        # 根据模式调整分析时间范围
        hours = 24
        if self.mode == 'black_friday':
            hours = 6  # 黑五期间更频繁
        elif self.mode == 'flash_sale':
            hours = 2  # Flash Sale更实时

        promotions = self.load_recent_promotions(hours)
        summary = self.generate_summary(promotions)

        # 保存分析结果
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        self.logger.info(f"Analysis completed. Found {summary['total_promotions']} promotions")

        return summary

def main():
    parser = argparse.ArgumentParser(description='Promotion Analyzer')
    parser.add_argument('--input-dir', required=True)
    parser.add_argument('--output-file', required=True)
    parser.add_argument('--mode', default='normal')

    args = parser.parse_args()

    analyzer = PromotionAnalyzer(args.input_dir, args.mode)
    analyzer.run(args.output_file)

if __name__ == '__main__':
    main()
```

### 3. 告警检查脚本

创建 `scripts/check_promotion_alerts.py`：

```python
#!/usr/bin/env python3
"""
促销告警检查器
"""

import argparse
import json
import logging
import os
from datetime import datetime
from pathlib import Path

class PromotionAlertChecker:
    def __init__(self, alert_rules_file):
        self.logger = logging.getLogger(__name__)

        # 加载告警规则
        with open(alert_rules_file, 'r', encoding='utf-8') as f:
            self.alert_rules = json.load(f)

    def check_alerts(self, summary_data):
        """检查告警条件"""
        alerts = []

        for rule_name, rule in self.alert_rules.items():
            triggered_promotions = []

            for promotion in summary_data.get('top_promotions', []):
                if self.matches_rule(promotion, rule):
                    triggered_promotions.append(promotion)

            if triggered_promotions:
                alert = {
                    'rule_name': rule_name,
                    'rule': rule,
                    'triggered_promotions': triggered_promotions,
                    'count': len(triggered_promotions),
                    'urgency': rule.get('urgency', 'normal'),
                    'triggered_at': datetime.now().isoformat()
                }
                alerts.append(alert)

        return alerts

    def matches_rule(self, promotion, rule):
        """检查促销是否匹配规则"""
        # 检查评分阈值
        if 'min_score' in rule:
            if promotion.get('score', 0) < rule['min_score']:
                return False

        # 检查关键词
        if 'keywords' in rule:
            text = f"{promotion.get('title', '')} {promotion.get('summary', '')}".lower()
            if not any(keyword.lower() in text for keyword in rule['keywords']):
                return False

        # 检查服务商
        if 'providers' in rule:
            provider = promotion.get('provider', '').lower()
            if not any(p.lower() in provider for p in rule['providers']):
                return False

        # 检查来源
        if 'sources' in rule:
            source = promotion.get('source', '')
            if source not in rule['sources']:
                return False

        return True

    def run(self, summary_file, output_file):
        """运行告警检查"""
        self.logger.info("Checking promotion alerts...")

        # 加载汇总数据
        with open(summary_file, 'r', encoding='utf-8') as f:
            summary_data = json.load(f)

        # 检查告警
        alerts = self.check_alerts(summary_data)

        # 保存告警结果
        alert_data = {
            'has_alerts': len(alerts) > 0,
            'alert_count': len(alerts),
            'alerts': alerts,
            'checked_at': datetime.now().isoformat()
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(alert_data, f, ensure_ascii=False, indent=2)

        # 设置GitHub Actions输出
        if 'GITHUB_OUTPUT' in os.environ:
            with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
                f.write(f"has_alerts={'true' if alerts else 'false'}\n")
                f.write(f"alert_count={len(alerts)}\n")

        self.logger.info(f"Alert check completed. Found {len(alerts)} alerts")

        return alert_data

def main():
    parser = argparse.ArgumentParser(description='Promotion Alert Checker')
    parser.add_argument('--data-file', required=True)
    parser.add_argument('--alert-rules', required=True)
    parser.add_argument('--output-file', required=True)

    args = parser.parse_args()

    checker = PromotionAlertChecker(args.alert_rules)
    checker.run(args.data_file, args.output_file)

if __name__ == '__main__':
    main()
```

### 4. 通知发送脚本

创建 `scripts/send_notifications.py`：

```python
#!/usr/bin/env python3
"""
通知发送器
"""

import argparse
import json
import logging
import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

class NotificationSender:
    def __init__(self, mode='normal'):
        self.mode = mode
        self.logger = logging.getLogger(__name__)

    def send_telegram_notification(self, message):
        """发送Telegram通知"""
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')

        if not bot_token or not chat_id:
            self.logger.warning("Telegram credentials not configured")
            return False

        try:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            }

            response = requests.post(url, data=data, timeout=30)
            response.raise_for_status()

            self.logger.info("Telegram notification sent successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to send Telegram notification: {e}")
            return False

    def send_webhook_notification(self, data):
        """发送Webhook通知"""
        webhook_url = os.getenv('WEBHOOK_URL')

        if not webhook_url:
            self.logger.warning("Webhook URL not configured")
            return False

        try:
            response = requests.post(webhook_url, json=data, timeout=30)
            response.raise_for_status()

            self.logger.info("Webhook notification sent successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to send webhook notification: {e}")
            return False

    def send_email_notification(self, subject, body):
        """发送邮件通知"""
        smtp_server = os.getenv('EMAIL_SMTP_SERVER')
        username = os.getenv('EMAIL_USERNAME')
        password = os.getenv('EMAIL_PASSWORD')
        to_email = os.getenv('EMAIL_TO')

        if not all([smtp_server, username, password, to_email]):
            self.logger.warning("Email credentials not configured")
            return False

        try:
            msg = MIMEMultipart()
            msg['From'] = username
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain', 'utf-8'))

            server = smtplib.SMTP(smtp_server, 587)
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
            server.quit()

            self.logger.info("Email notification sent successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to send email notification: {e}")
            return False

    def format_alert_message(self, alert):
        """格式化告警消息"""
        promotions = alert['triggered_promotions']

        message = f"""
🚨 **VPS促销告警** - {alert['rule_name'].upper()}

📊 **触发数量**: {alert['count']}个促销
⚡ **紧急程度**: {alert['urgency']}
⏰ **检测时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**热门促销**:
"""

        for i, promo in enumerate(promotions[:3], 1):
            message += f"""
{i}. **{promo.get('title', 'No title')[:50]}**
   💰 评分: {promo.get('score', 0):.1f}
   🏷️ 来源: {promo.get('source', 'unknown')}
   🔗 链接: {promo.get('link', promo.get('url', 'No link'))}
"""

        if len(promotions) > 3:
            message += f"\n... 还有 {len(promotions) - 3} 个促销"

        message += f"\n\n#{alert['rule_name']} #VPSDeals"

        return message.strip()

    def run(self, alerts_file):
        """运行通知发送"""
        self.logger.info("Sending notifications...")

        # 加载告警数据
        with open(alerts_file, 'r', encoding='utf-8') as f:
            alert_data = json.load(f)

        if not alert_data.get('has_alerts'):
            self.logger.info("No alerts to send")
            return

        alerts = alert_data['alerts']

        for alert in alerts:
            message = self.format_alert_message(alert)

            # 根据紧急程度选择通知方式
            if alert['urgency'] == 'high':
                # 高优先级：所有通知方式
                self.send_telegram_notification(message)
                self.send_email_notification(
                    f"🚨 高优先级VPS促销告警 - {alert['rule_name']}",
                    message
                )
                self.send_webhook_notification(alert)
            elif alert['urgency'] == 'medium':
                # 中优先级：Telegram + Webhook
                self.send_telegram_notification(message)
                self.send_webhook_notification(alert)
            else:
                # 普通优先级：仅Webhook
                self.send_webhook_notification(alert)

        self.logger.info(f"Notifications sent for {len(alerts)} alerts")

def main():
    parser = argparse.ArgumentParser(description='Notification Sender')
    parser.add_argument('--alerts-file', required=True)
    parser.add_argument('--mode', default='normal')

    args = parser.parse_args()

    sender = NotificationSender(args.mode)
    sender.run(args.alerts_file)

if __name__ == '__main__':
    main()
```

## 配置文件

### 1. 告警规则配置

创建 `config/alert_rules.json`：

```json
{
  "high_value_deals": {
    "min_score": 80,
    "urgency": "high",
    "description": "高价值促销（评分80+）"
  },

  "black_friday_deals": {
    "keywords": ["black friday", "bf2024", "black fri"],
    "min_score": 60,
    "urgency": "high",
    "description": "黑色星期五促销"
  },

  "flash_sales": {
    "keywords": ["flash sale", "limited time", "24 hours", "today only"],
    "urgency": "high",
    "description": "限时抢购"
  },

  "premium_providers": {
    "providers": ["bandwagonhost", "racknerd", "digitalocean", "linode"],
    "min_score": 50,
    "urgency": "medium",
    "description": "知名服务商促销"
  },

  "low_price_deals": {
    "keywords": ["$", "dollar"],
    "min_score": 40,
    "urgency": "normal",
    "description": "低价促销"
  }
}
```

### 2. 依赖文件

创建 `requirements.txt`：

```
requests>=2.28.0
beautifulsoup4>=4.11.0
feedparser>=6.0.0
lxml>=4.9.0
python-dateutil>=2.8.0
```

## 使用说明

### 1. 设置GitHub Secrets

在GitHub仓库设置中添加以下Secrets：

```
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
WEBHOOK_URL=your_webhook_url
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_TO=recipient@example.com
```

### 2. 目录结构

```
your-repo/
├── .github/
│   └── workflows/
│       ├── vps-promotion-collector.yml
│       └── black-friday-monitor.yml
├── scripts/
│   ├── vps_promotion_collector.py
│   ├── promotion_analyzer.py
│   ├── check_promotion_alerts.py
│   └── send_notifications.py
├── config/
│   └── alert_rules.json
├── data/
│   ├── promotions/
│   └── daily_summaries/
├── logs/
├── requirements.txt
└── README.md
```

### 3. 运行模式

- **normal**: 常规监控（每小时）
- **black_friday**: 黑五模式（每5分钟）
- **flash_sale**: 闪购模式（高频监控）

这个GitHub Actions方案完全免费，自动化程度高，非常适合VPS促销信息的收集和监控！
```
