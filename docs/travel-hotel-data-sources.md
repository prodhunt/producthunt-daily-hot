# 旅游酒店数据源API指南

## 概述

本文档提供了旅游酒店行业的主要API数据源，涵盖酒店预订、航班信息、景点数据、旅游资讯等多个维度，适用于构建旅游资讯平台、比价网站、旅行规划工具等应用。

## 数据源分类

### 1. 酒店预订API

#### Booking.com API
**数据内容**：全球酒店信息、价格、可用性
- **API类型**：官方合作伙伴API
- **费用**：需要合作伙伴资格，佣金分成模式
- **数据特点**：
  - 全球最大酒店库存
  - 实时价格和可用性
  - 详细酒店信息和评价
- **申请条件**：需要有一定规模的网站流量

#### Expedia Partner Solutions (EPS)
**数据内容**：酒店、机票、租车、活动
- **API地址**：https://developers.expediagroup.com/
- **费用**：合作伙伴模式，佣金分成
- **数据特点**：
  - 综合旅游产品
  - 全球覆盖
  - 包装产品支持

#### Hotels.com API
**数据内容**：酒店预订信息
- **隶属**：Expedia集团
- **特点**：专注酒店预订
- **积分系统**：Hotels.com Rewards

#### Agoda API
**数据内容**：亚洲地区酒店为主
- **特点**：亚洲市场覆盖优秀
- **费用**：合作伙伴模式

### 2. 航班信息API

#### Amadeus API
**数据内容**：航班搜索、预订、机场信息
- **API地址**：https://developers.amadeus.com/
- **费用**：免费层级 + 付费层级
- **免费额度**：每月2000次调用
- **API示例**：
```python
import requests

def search_flights(origin, destination, departure_date):
    url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        'originLocationCode': origin,
        'destinationLocationCode': destination,
        'departureDate': departure_date,
        'adults': 1
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()
```

#### Skyscanner API
**数据内容**：航班比价、价格趋势
- **API地址**：https://partners.skyscanner.net/
- **费用**：需要申请合作伙伴
- **特点**：
  - 强大的比价功能
  - 价格预测
  - 灵活日期搜索

#### Kiwi.com API
**数据内容**：航班搜索、预订
- **API地址**：https://docs.kiwi.com/
- **费用**：免费层级可用
- **特点**：
  - 支持复杂路线
  - 廉价航空覆盖好
  - 虚拟联程

### 3. 地理位置和景点API

#### Google Places API
**数据内容**：景点、餐厅、酒店位置信息
- **API地址**：https://developers.google.com/maps/documentation/places/web-service
- **费用**：按使用量付费，有免费额度
- **API示例**：
```python
def get_nearby_attractions(lat, lng, radius=5000):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        'location': f'{lat},{lng}',
        'radius': radius,
        'type': 'tourist_attraction',
        'key': 'YOUR_API_KEY'
    }
    response = requests.get(url, params=params)
    return response.json()
```

#### Foursquare Places API
**数据内容**：POI数据、用户评价
- **API地址**：https://developer.foursquare.com/
- **费用**：免费层级 + 付费层级
- **特点**：
  - 丰富的POI数据
  - 用户生成内容
  - 实时数据

#### TripAdvisor API
**数据内容**：景点信息、评价、照片
- **API地址**：https://developer-tripadvisor.com/
- **费用**：需要申请，有使用限制
- **特点**：
  - 权威旅游评价
  - 丰富的用户内容
  - 全球景点覆盖

### 4. 旅游内容和评价API

#### Yelp Fusion API
**数据内容**：餐厅、景点、服务评价
- **API地址**：https://www.yelp.com/developers/documentation/v3
- **费用**：免费，有调用限制
- **API示例**：
```python
def search_restaurants(location, term="restaurants"):
    url = "https://api.yelp.com/v3/businesses/search"
    headers = {
        'Authorization': f'Bearer {api_key}'
    }
    params = {
        'location': location,
        'term': term,
        'limit': 20
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()
```

#### GetYourGuide API
**数据内容**：旅游活动、门票、导览
- **API地址**：https://partner.getyourguide.com/
- **费用**：合作伙伴模式
- **特点**：
  - 丰富的旅游活动
  - 门票预订
  - 当地体验

#### Viator API
**数据内容**：旅游活动、一日游
- **隶属**：TripAdvisor集团
- **特点**：全球旅游活动覆盖

### 5. 天气和交通API

#### OpenWeatherMap API
**数据内容**：天气预报、历史天气
- **API地址**：https://openweathermap.org/api
- **费用**：免费层级 + 付费层级
- **API示例**：
```python
def get_weather(city):
    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city,
        'appid': 'YOUR_API_KEY',
        'units': 'metric'
    }
    response = requests.get(url, params=params)
    return response.json()
```

#### Rome2Rio API
**数据内容**：多模式交通路线规划
- **API地址**：https://www.rome2rio.com/documentation/
- **费用**：免费层级 + 付费层级
- **特点**：
  - 综合交通方式
  - 全球路线规划
  - 价格估算

### 6. 汇率和货币API

#### ExchangeRate-API
**数据内容**：实时汇率
- **API地址**：https://exchangerate-api.com/
- **费用**：免费层级 + 付费层级
- **API示例**：
```python
def get_exchange_rate(base_currency, target_currency):
    url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
    response = requests.get(url)
    data = response.json()
    return data['rates'].get(target_currency)
```

#### Fixer.io API
**数据内容**：汇率、历史汇率
- **API地址**：https://fixer.io/
- **费用**：免费层级 + 付费层级

## 旅游资讯和内容源

### 1. 旅游博客和媒体RSS
```python
TRAVEL_RSS_SOURCES = {
    'lonely_planet': 'https://www.lonelyplanet.com/news/feed',
    'travel_leisure': 'https://www.travelandleisure.com/syndication/feed',
    'conde_nast': 'https://www.cntraveler.com/feed/rss',
    'national_geographic': 'https://www.nationalgeographic.com/travel/rss/',
    'fodors': 'https://www.fodors.com/news/rss.xml',
    'travel_weekly': 'https://www.travelweekly.com/rss.xml',
    'skift': 'https://skift.com/feed/',
    'tnooz': 'https://www.tnooz.com/feed/'
}
```

### 2. 社交媒体旅游内容
#### Instagram API
**数据内容**：旅游照片、地理标签
- **特点**：视觉内容丰富
- **用途**：目的地营销、用户生成内容

#### YouTube Data API
**数据内容**：旅游视频、Vlog
- **API地址**：https://developers.google.com/youtube/v3
- **用途**：旅游视频内容聚合

### 3. 政府和官方旅游局API
```python
OFFICIAL_TOURISM_APIS = {
    'visit_britain': 'https://www.visitbritain.org/trade-api',
    'tourism_australia': 'https://www.tourism.australia.com/en/industry/digital-toolkit.html',
    'japan_tourism': 'https://www.jnto.go.jp/eng/ttp/sta/',
    'singapore_tourism': 'https://www.stb.gov.sg/content/stb/en/trade/digital-marketing-toolkit.html'
}
```

## 数据整合架构

### 旅游数据聚合器
```python
class TravelDataAggregator:
    def __init__(self):
        self.apis = {
            'hotels': HotelAPI(),
            'flights': FlightAPI(),
            'attractions': AttractionAPI(),
            'weather': WeatherAPI(),
            'reviews': ReviewAPI()
        }

    def get_destination_info(self, destination):
        result = {
            'destination': destination,
            'hotels': self.apis['hotels'].search(destination),
            'attractions': self.apis['attractions'].get_nearby(destination),
            'weather': self.apis['weather'].get_forecast(destination),
            'reviews': self.apis['reviews'].get_destination_reviews(destination)
        }
        return result

    def get_travel_deals(self, origin, destination, dates):
        deals = {
            'flights': self.apis['flights'].search_deals(origin, destination, dates),
            'hotels': self.apis['hotels'].get_deals(destination, dates),
            'packages': self.combine_deals()
        }
        return deals
```

### 内容分类系统
```python
TRAVEL_CATEGORIES = {
    '🏨 酒店住宿': {
        'sources': ['booking', 'expedia', 'hotels_com'],
        'data_types': ['prices', 'availability', 'reviews', 'amenities']
    },
    '✈️ 航班信息': {
        'sources': ['amadeus', 'skyscanner', 'kiwi'],
        'data_types': ['schedules', 'prices', 'routes', 'airlines']
    },
    '🗺️ 景点活动': {
        'sources': ['tripadvisor', 'getyourguide', 'viator'],
        'data_types': ['attractions', 'tours', 'tickets', 'experiences']
    },
    '🍽️ 餐饮美食': {
        'sources': ['yelp', 'zomato', 'opentable'],
        'data_types': ['restaurants', 'reviews', 'menus', 'reservations']
    },
    '🌤️ 天气交通': {
        'sources': ['openweather', 'rome2rio', 'google_maps'],
        'data_types': ['weather', 'routes', 'traffic', 'transport']
    },
    '💰 价格汇率': {
        'sources': ['exchangerate_api', 'fixer'],
        'data_types': ['exchange_rates', 'price_trends', 'cost_estimates']
    }
}
```

## 推荐组合方案

### 方案1：酒店比价平台
**适用场景**：酒店预订和比价网站
```python
HOTEL_FOCUSED_STACK = {
    'core_apis': [
        'booking_com',      # 主要酒店库存
        'expedia_eps',      # 补充库存
        'hotels_com'        # 专业酒店数据
    ],
    'supporting_apis': [
        'google_places',    # 位置和评价
        'tripadvisor',      # 用户评价
        'openweather'       # 天气信息
    ],
    'content_sources': [
        'travel_rss_feeds', # 旅游资讯
        'hotel_blogs'       # 酒店评测
    ]
}
```

### 方案2：综合旅游平台
**适用场景**：一站式旅游服务平台
```python
COMPREHENSIVE_TRAVEL_STACK = {
    'booking_apis': [
        'expedia_eps',      # 酒店+机票+租车
        'amadeus',          # 航班信息
        'getyourguide'      # 活动门票
    ],
    'content_apis': [
        'tripadvisor',      # 景点评价
        'yelp',             # 餐厅信息
        'foursquare'        # POI数据
    ],
    'utility_apis': [
        'google_maps',      # 地图导航
        'openweather',      # 天气预报
        'exchangerate_api'  # 汇率转换
    ]
}
```

### 方案3：旅游资讯媒体
**适用场景**：旅游内容和资讯平台
```python
CONTENT_FOCUSED_STACK = {
    'content_sources': [
        'travel_rss_feeds', # 主流旅游媒体
        'youtube_api',      # 旅游视频
        'instagram_api',    # 旅游照片
        'travel_blogs'      # 个人游记
    ],
    'data_apis': [
        'tripadvisor',      # 目的地信息
        'google_places',    # 景点数据
        'openweather',      # 天气数据
    ],
    'social_apis': [
        'twitter_api',      # 实时旅游话题
        'reddit_travel'     # 旅游社区讨论
    ]
}
```

### 方案4：商务旅行平台
**适用场景**：企业差旅管理
```python
BUSINESS_TRAVEL_STACK = {
    'booking_apis': [
        'amadeus',          # 企业航班预订
        'booking_com',      # 商务酒店
        'enterprise_car'    # 租车服务
    ],
    'management_apis': [
        'expense_apis',     # 费用管理
        'calendar_apis',    # 行程管理
        'approval_apis'     # 审批流程
    ],
    'reporting_apis': [
        'analytics_apis',   # 差旅分析
        'compliance_apis'   # 合规检查
    ]
}
```

## 实施建议

### API集成优先级
```python
INTEGRATION_PHASES = {
    'phase_1_foundation': {
        'priority': 'high',
        'apis': [
            'google_places',    # 免费，基础地理数据
            'openweather',      # 免费，天气信息
            'exchangerate_api', # 免费，汇率数据
            'travel_rss_feeds'  # 免费，内容源
        ],
        'timeline': '1-2周'
    },

    'phase_2_core_services': {
        'priority': 'medium',
        'apis': [
            'amadeus',          # 有免费层，航班数据
            'yelp',             # 免费，餐厅评价
            'tripadvisor',      # 需申请，权威评价
        ],
        'timeline': '2-4周'
    },

    'phase_3_premium_services': {
        'priority': 'low',
        'apis': [
            'booking_com',      # 需合作伙伴资格
            'expedia_eps',      # 需合作伙伴资格
            'skyscanner'        # 需合作伙伴资格
        ],
        'timeline': '1-3个月'
    }
}
```

### 成本预算规划
```python
API_COST_ESTIMATES = {
    'free_tier': {
        'monthly_cost': 0,
        'apis': ['google_places', 'openweather', 'yelp', 'rss_feeds'],
        'limitations': '调用次数限制，功能受限'
    },

    'startup_tier': {
        'monthly_cost': '$100-500',
        'apis': ['amadeus_paid', 'google_places_paid', 'premium_weather'],
        'benefits': '更高调用限制，更多功能'
    },

    'enterprise_tier': {
        'monthly_cost': '$1000+',
        'apis': ['booking_partner', 'expedia_partner', 'custom_apis'],
        'benefits': '无限调用，专属支持，佣金分成'
    }
}
```

### 数据质量控制
```python
class TravelDataValidator:
    def __init__(self):
        self.required_fields = {
            'hotel': ['name', 'location', 'price', 'rating'],
            'flight': ['airline', 'departure', 'arrival', 'price'],
            'attraction': ['name', 'location', 'rating', 'description']
        }

    def validate_hotel_data(self, hotel_data):
        errors = []

        # 检查必需字段
        for field in self.required_fields['hotel']:
            if field not in hotel_data or not hotel_data[field]:
                errors.append(f"Missing required field: {field}")

        # 检查价格合理性
        if 'price' in hotel_data:
            price = hotel_data['price']
            if price < 10 or price > 10000:  # 异常价格范围
                errors.append(f"Suspicious price: {price}")

        # 检查评分范围
        if 'rating' in hotel_data:
            rating = hotel_data['rating']
            if rating < 0 or rating > 5:
                errors.append(f"Invalid rating: {rating}")

        return len(errors) == 0, errors

    def clean_and_standardize(self, data, data_type):
        """数据清洗和标准化"""
        if data_type == 'hotel':
            # 标准化价格格式
            if 'price' in data:
                data['price'] = float(data['price'])

            # 标准化评分
            if 'rating' in data:
                data['rating'] = round(float(data['rating']), 1)

        return data
```

## 注意事项和最佳实践

### 1. 法律合规要求
```python
COMPLIANCE_CHECKLIST = {
    'data_usage': [
        '遵守API使用条款',
        '正确标注数据来源',
        '不得缓存敏感价格数据超过规定时间',
        '遵守GDPR等隐私法规'
    ],

    'business_model': [
        '了解佣金分成模式',
        '避免价格操纵',
        '透明显示所有费用',
        '遵守消费者保护法'
    ],

    'technical': [
        '实施适当的安全措施',
        '保护用户支付信息',
        '确保数据传输加密',
        '定期安全审计'
    ]
}
```

### 2. 性能优化策略
```python
class TravelAPIOptimizer:
    def __init__(self):
        self.cache_ttl = {
            'hotel_search': 300,    # 5分钟
            'flight_search': 180,   # 3分钟
            'attraction_info': 3600, # 1小时
            'weather_data': 1800,   # 30分钟
            'exchange_rates': 3600  # 1小时
        }

    def batch_api_calls(self, requests_list):
        """批量API调用优化"""
        results = []

        # 按API类型分组
        grouped_requests = self.group_by_api_type(requests_list)

        # 并发调用不同API
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for api_type, requests in grouped_requests.items():
                future = executor.submit(self.call_api_batch, api_type, requests)
                futures.append(future)

            for future in as_completed(futures):
                results.extend(future.result())

        return results

    def implement_circuit_breaker(self, api_name):
        """熔断器模式，防止API故障影响整体服务"""
        failure_threshold = 5
        timeout_duration = 60  # 秒

        # 实现熔断逻辑
        pass
```

### 3. 用户体验优化
```python
UX_OPTIMIZATION_STRATEGIES = {
    'search_experience': {
        'auto_complete': '使用Google Places API实现地点自动补全',
        'smart_defaults': '基于用户位置和历史偏好设置默认值',
        'progressive_loading': '分步加载搜索结果，优先显示核心信息'
    },

    'booking_flow': {
        'price_transparency': '清晰显示所有费用组成',
        'real_time_updates': '实时更新价格和可用性',
        'mobile_optimization': '优化移动端预订体验'
    },

    'content_discovery': {
        'personalization': '基于用户偏好推荐内容',
        'visual_content': '整合Instagram等视觉内容',
        'local_insights': '提供当地人推荐和小贴士'
    }
}
```

## 监控和分析

### API性能监控
```python
class TravelAPIMonitor:
    def __init__(self):
        self.metrics = {
            'response_times': {},
            'error_rates': {},
            'data_quality_scores': {},
            'cost_tracking': {}
        }

    def track_api_performance(self, api_name, response_time, success):
        """跟踪API性能指标"""
        if api_name not in self.metrics['response_times']:
            self.metrics['response_times'][api_name] = []

        self.metrics['response_times'][api_name].append(response_time)

        # 计算错误率
        if api_name not in self.metrics['error_rates']:
            self.metrics['error_rates'][api_name] = {'total': 0, 'errors': 0}

        self.metrics['error_rates'][api_name]['total'] += 1
        if not success:
            self.metrics['error_rates'][api_name]['errors'] += 1

    def generate_health_report(self):
        """生成API健康状况报告"""
        report = {}

        for api_name in self.metrics['response_times']:
            avg_response_time = sum(self.metrics['response_times'][api_name]) / len(self.metrics['response_times'][api_name])
            error_rate = self.metrics['error_rates'][api_name]['errors'] / self.metrics['error_rates'][api_name]['total']

            report[api_name] = {
                'avg_response_time': avg_response_time,
                'error_rate': error_rate,
                'status': 'healthy' if error_rate < 0.05 and avg_response_time < 2000 else 'warning'
            }

        return report
```

## 总结

旅游酒店行业的API生态系统非常丰富，从免费的基础服务到高级的合作伙伴API都有覆盖。

### 快速启动建议
1. **第一步**：集成免费API（Google Places、OpenWeather、Yelp）
2. **第二步**：申请Amadeus等有免费层的专业API
3. **第三步**：根据业务发展申请合作伙伴API

### 成功关键因素
- **数据质量**：实施严格的数据验证和清洗
- **用户体验**：优化搜索和预订流程
- **合规运营**：遵守行业法规和API使用条款
- **成本控制**：合理规划API使用和成本

通过合理组合这些数据源，可以构建功能完整、数据丰富的旅游服务平台。
```
