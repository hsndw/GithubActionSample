# 安装依赖 pip3 install requests html5lib bs4 schedule
import os
import requests
import json
from bs4 import BeautifulSoup
from datetime import date

# 从测试号信息获取
appID = os.environ.get("APP_ID")
appSecret = os.environ.get("APP_SECRET")
openId = os.environ.get("OPEN_ID")
weather_template_id = os.environ.get("TEMPLATE_ID")

# 核心配置：修改为第67天对应的实际日期
START_DATE = date(2025, 10, 8)
INITIAL_DAYS = 67

def get_days_together():
    """计算和瑶瑶在一起的天数（从67天开始累加）"""
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
                        # 提取天气数据并做空值处理
                        high_temp = list(tds[-5].stripped_strings)[0] if tds[-5].stripped_strings else "-"
                        low_temp = list(tds[-2].stripped_strings)[0] if tds[-2].stripped_strings else "-"
                        weather_typ_day = list(tds[-7].stripped_strings)[0] if tds[-7].stripped_strings else "-"
                        weather_type_night = list(tds[-4].stripped_strings)[0] if tds[-4].stripped_strings else "-"
                        
                        wind_day_parts = list(tds[-6].stripped_strings)
                        wind_day = "".join(wind_day_parts[:2]) if wind_day_parts else "--"
                        wind_night_parts = list(tds[-3].stripped_strings)
                        wind_night = "".join(wind_night_parts[:2]) if wind_night_parts else "--"

                        # 数据整合
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
        print("APP_ID或APP_SECRET未配置")
        return None
    try:
        url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appID.strip()}&secret={appSecret.strip()}"
        response = requests.get(url, timeout=10).json()
        print(response)
        return response.get('access_token')
    except Exception as e:
        print(f"获取access_token失败：{e}")
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

def send_weather(access_token, weather):
    """发送微信模板消息，修复缩进并添加参数校验"""
    if not access_token or not weather or any(v is None for v in weather):
        print("参数异常，无法发送消息")
        return
    if not openId or not weather_template_id:
        print("OPEN_ID或TEMPLATE_ID未配置")
        return
    
    today = date.today()
    today_str = today.strftime("%Y年%m月%d日")
    days_together = get_days_together()

    # 严格统一缩进，避免IndentationError
    body = {
        "touser": openId.strip(),
        "template_id": weather_template_id.strip(),
        "url": "https://weixin.qq.com",
        "data": {
            "date": {"value": today_str},
            "region": {"value": weather[0]},
            "weather": {"value": weather[2]},
            "temp": {"value": weather[1]},
            "wind_dir": {"value": weather[3]},
            "today_note": {"value": get_daily_love()},
            "days_together": {"value": days_together}
        }
    }
    try:
        url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}"
        resp = requests.post(
            url, 
            data=json.dumps(body, ensure_ascii=False).encode('utf-8'),
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(resp.text)
    except Exception as e:
        print(f"发送消息失败：{e}")

def weather_report(this_city):
    """主函数，添加流程校验"""
    access_token = get_access_token()
    if not access_token:
        return
    weather = get_weather(this_city)
    print(f"天气信息： {weather}")
    send_weather(access_token, weather)

if __name__ == '__main__':
    # 修改为第67天对应的实际日期
    START_DATE = date(2025, 10, 8)
    weather_report("芜湖")

