# 安装依赖 pip3 install requests html5lib bs4 schedule
import os
import requests
import json
from bs4 import BeautifulSoup
from datetime import date

# 从环境变量读取配置，并添加读取失败的提示
def get_env_var(var_name):
    """获取环境变量，若不存在则打印提示并返回None"""
    value = os.environ.get(var_name)
    if not value:
        print(f"❌ 环境变量{var_name}未配置或读取失败")
    return value

# 从测试号信息获取
appID = get_env_var("APP_ID")
appSecret = get_env_var("APP_SECRET")
OPEN_ID_1 = get_env_var("OPEN_ID_1")
OPEN_ID_2 = get_env_var("OPEN_ID_2")
# 配置多个收件人OpenID，过滤空值
open_ids = [oid for oid in [OPEN_ID_1, OPEN_ID_2] if oid]
weather_template_id = get_env_var("TEMPLATE_ID")

# 核心配置：改为真实恋爱起始日期（根据昨天是第67天反推），INITIAL_DAYS设为0
# 假设昨天是2025-12-13且是第67天，起始日期就是 2025-12-13 往前推67天 = 2025-10-07
# 你需要根据实际情况替换这个日期！
START_DATE = date(2025, 10, 7)
INITIAL_DAYS = 0

def get_days_together():
    """计算恋爱天数"""
    today = date.today()
    days_passed = (today - START_DATE).days
    total_days = INITIAL_DAYS + days_passed
    return f"❤️ 和瑶瑶在一起的第 {total_days} 天 ❤️"

def get_weather(my_city):
    """爬取天气数据，添加请求头和异常处理"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    urls = [
        "http://www.weather.com.cn/textFC/hb.shtml",
        "http://www.weather.com.cn/textFC/db.shtml",
        "http://www.weather.com.cn/textFC/hd.shtml",
        "http://www.weather.com.cn/textFC/hz.shtml",
        "http://www.weather.com.cn/textFC/hn.shtml",
        "http://www.weather.com.cn/textFC/xb.shtml",
        "http://www.weather.com.cn/textFC/xn.shtml"
    ]
    for url in urls:
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            resp.encoding = "utf-8"
            soup = BeautifulSoup(resp.text, 'html5lib')
            div_conMidtab = soup.find("div", class_="conMidtab")
            if not div_conMidtab:
                continue
            tables = div_conMidtab.find_all("table")
            for table in tables:
                trs = table.find_all("tr")[2:]
                for tr in trs:
                    tds = tr.find_all("td")
                    if len(tds) < 8:
                        continue
                    city_td = tds[-8]
                    this_city = list(city_td.stripped_strings)[0] if city_td.stripped_strings else ""
                    if this_city == my_city:
                        high_temp = list(tds[-5].stripped_strings)[0] if tds[-5].stripped_strings else "-"
                        low_temp = list(tds[-2].stripped_strings)[0] if tds[-2].stripped_strings else "-"
                        weather_typ_day = list(tds[-7].stripped_strings)[0] if tds[-7].stripped_strings else "-"
                        weather_type_night = list(tds[-4].stripped_strings)[0] if tds[-4].stripped_strings else "-"
                        
                        wind_day_parts = list(tds[-6].stripped_strings)
                        wind_day = "".join(wind_day_parts[:2]) if wind_day_parts else "--"
                        wind_night_parts = list(tds[-3].stripped_strings)
                        wind_night = "".join(wind_night_parts[:2]) if wind_night_parts else "--"

                        temp = f"{low_temp}——{high_temp}摄氏度" if high_temp != "-" else f"{low_temp}摄氏度"
                        weather_typ = weather_typ_day if weather_typ_day != "-" else weather_type_night
                        wind = wind_day if wind_day != "--" else wind_night
                        return this_city, temp, weather_typ, wind
        except Exception as e:
            print(f"爬取天气失败：{e}")
            continue
    return None, None, None, None

def get_access_token():
    """获取微信access_token，添加异常处理"""
    if not appID or not appSecret:
        print("❌ APP_ID或APP_SECRET未配置，无法获取token")
        return None
    try:
        url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appID.strip()}&secret={appSecret.strip()}"
        response = requests.get(url, timeout=10).json()
        if "errcode" in response and response["errcode"] != 0:
            print(f"❌ 获取token失败：{response['errmsg']}")
            return None
        print("✅ 获取token成功")
        return response.get('access_token')
    except Exception as e:
        print(f"❌ 获取access_token异常：{e}")
        return None

def get_daily_love():
    """获取每日情话，添加异常处理"""
    try:
        url = "https://api.lovelive.tools/api/SweetNothings/Serialization/Json"
        r = requests.get(url, timeout=10)
        return json.loads(r.text)['returnObj'][0]
    except Exception as e:
        print(f"获取情话失败：{e}")
        return "愿你今天事事顺心～"

def send_weather(access_token, weather, open_id):
    """给单个收件人发送模板消息"""
    if not access_token:
        print("❌ 无有效access_token，跳过发送")
        return
    if not weather or any(v is None for v in weather):
        print("❌ 天气数据获取失败，跳过发送")
        return
    if not open_id:
        print("❌ OpenID为空，跳过发送")
        return
    if not weather_template_id:
        pr
