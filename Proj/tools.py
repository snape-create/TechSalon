import os
import json
import requests
import sqlite3
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('api_key')
BASE_URL = os.getenv('url')

TZ = timezone(timedelta(hours=8))




def fetch_weather_data(city, location) -> dict | None:
    """返回指定城市的天气

    Args:
        city (_type_): 城市
        location (_type_): 城市代码

    Returns:
        dict | None: 天气字典
    """
    headers = {"X-QW-Api-Key": API_KEY}
    url = f"{BASE_URL}?location={location}"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        # requests 已自动处理 gzip，直接解析文本即可
        return json.loads(response.text)
    except requests.RequestException as e:
        print(f"请求 {city} 天气数据失败: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"{city} JSON 解析错误: {e}, 响应内容: {response.text[:500]}...")
        return None



def store_weather_data(conn, cursor, city, data):
    """将和风平台天气数据存储到 SQLite 数据库中

    Args:
        conn: sqlite3.Connection 对象
        cursor: sqlite3.Cursor 对象
        city (str): 城市
        data (dict): 城市对应的天气数据
    """
    if not data or data.get('code') != "200":
        print(f'❌{city}数据无效')
        return None

    # 确保表存在；(city, fx_date) 主键用于 UPSERT 冲突判定
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS weather_data (
        city TEXT NOT NULL,
        fx_date TEXT NOT NULL,
        sunrise TEXT, sunset TEXT, moonrise TEXT, moonset TEXT,
        moon_phase TEXT, moon_phase_icon TEXT,
        temp_max TEXT, temp_min TEXT,
        icon_day TEXT, text_day TEXT, icon_night TEXT, text_night TEXT,
        wind360_day TEXT, wind_dir_day TEXT, wind_scale_day TEXT, wind_speed_day TEXT,
        wind360_night TEXT, wind_dir_night TEXT, wind_scale_night TEXT, wind_speed_night TEXT,
        precip TEXT, uv_index TEXT, humidity TEXT, pressure TEXT, vis TEXT, cloud TEXT,
        update_time TEXT,
        PRIMARY KEY (city, fx_date)
    )
    """)

    # 获取 daily 数据
    daily_data = data.get("daily", [])
    update_time = datetime.fromisoformat(data["updateTime"]).replace(tzinfo=TZ)

    # 除 (city, fx_date) 之外的字段，冲突时逐一更新
    columns = [
        "sunrise", "sunset", "moonrise", "moonset",
        "moon_phase", "moon_phase_icon", "temp_max", "temp_min",
        "icon_day", "text_day", "icon_night", "text_night",
        "wind360_day", "wind_dir_day", "wind_scale_day", "wind_speed_day",
        "wind360_night", "wind_dir_night", "wind_scale_night", "wind_speed_night",
        "precip", "uv_index", "humidity", "pressure", "vis", "cloud", "update_time",
    ]
    placeholders = ", ".join(["?"] * (2 + len(columns)))
    updates = ", ".join(f"{col} = excluded.{col}" for col in columns)
    insert_query = f"""
    INSERT INTO weather_data (city, fx_date, {', '.join(columns)})
    VALUES ({placeholders})
    ON CONFLICT(city, fx_date) DO UPDATE SET {updates}
    """

    for day in daily_data:
        fx_date = datetime.strptime(day["fxDate"], "%Y-%m-%d").date()
        values = (
            city, fx_date,
            day.get("sunrise"), day.get("sunset"),
            day.get("moonrise"), day.get("moonset"),
            day.get("moonPhase"), day.get("moonPhaseIcon"),
            day.get("tempMax"), day.get("tempMin"),
            day.get("iconDay"), day.get("textDay"),
            day.get("iconNight"), day.get("textNight"),
            day.get("wind360Day"), day.get("windDirDay"), day.get("windScaleDay"), day.get("windSpeedDay"),
            day.get("wind360Night"), day.get("windDirNight"), day.get("windScaleNight"), day.get("windSpeedNight"),
            day.get("precip"), day.get("uvIndex"),
            day.get("humidity"), day.get("pressure"),
            day.get("vis"), day.get("cloud"),
            update_time
        )
        try:
            cursor.execute(insert_query, values)
            print(f"{city} {fx_date} 数据插入/更新成功: {day.get('textDay')}, 影响行数: {cursor.rowcount}")
        except sqlite3.Error as e:
            print(f"{city} {fx_date} 数据库错误: {e}")

    conn.commit()
    print(f"{city} 事务提交完成。")




city_code_dict = {
    "北京": "101010100",
    "上海": "101020100",
    "广州": "101280101",
    "深圳": "101280601",
    "杭州": "101210101",
    "成都": "101270101",
    "重庆": "101040100",
    "武汉": "101200101",
    "西安": "101110101",
    "南京": "101190101",
    "苏州": "101190401",
    "长沙": "101250101",
    "郑州": "101180101",
    "青岛": "101120501",
    "天津": "101030100"
}


if __name__ == '__main__':
    city_name = '西安'
   
    code  = city_code_dict[city_name]
    data  = fetch_weather_data(city_name,code)
    conn = sqlite3.connect("weather.sqlite3")
    cursor = conn.cursor()
    store_weather_data(conn, cursor, city_name, data)