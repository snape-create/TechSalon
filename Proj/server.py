"""把 weather.sqlite3 的查询能力封装为 MCP Server（默认 stdio 传输）。"""

import logging
import os
import sqlite3
import sys
import time
from pathlib import Path

from fastmcp import FastMCP


logger = logging.getLogger("weather-db")
logger.setLevel(logging.INFO)
if not logger.handlers:
    _handler = logging.StreamHandler(sys.stderr)
    _handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
    )
    logger.addHandler(_handler)
logger.propagate = False


DB_PATH = Path(
    os.getenv("WEATHER_DB", Path(__file__).resolve().parent.parent / "weather.sqlite3")
)

mcp = FastMCP("weather-db")

ALL_COLUMNS = [
    "city", "fx_date", "sunrise", "sunset", "moonrise", "moonset",
    "moon_phase", "moon_phase_icon", "temp_max", "temp_min",
    "icon_day", "text_day", "icon_night", "text_night",
    "wind360_day", "wind_dir_day", "wind_scale_day", "wind_speed_day",
    "wind360_night", "wind_dir_night", "wind_scale_night", "wind_speed_night",
    "precip", "uv_index", "humidity", "pressure", "vis", "cloud", "update_time",
]

BRIEF_COLUMNS = [
    "city", "fx_date", "temp_max", "temp_min", "text_day", "text_night",
    "wind_dir_day", "wind_scale_day", "humidity", "precip", "uv_index",
    "sunrise", "sunset", "update_time",
]


def _fetch(sql: str, params: tuple = ()) -> list[dict]:
    """执行只读查询并把每行转成 dict；每次调用独立连接，避免并发问题。"""
    if not DB_PATH.exists():
        logger.error("数据库文件不存在: %s", DB_PATH)
        raise FileNotFoundError(f"数据库不存在: {DB_PATH}")
    started = time.perf_counter()
    sql_brief = " ".join(sql.split())[:160]
    logger.info("SQL: %s | params=%s", sql_brief, params)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        rows = [dict(row) for row in conn.execute(sql, params).fetchall()]
        elapsed = (time.perf_counter() - started) * 1000
        logger.info("查询完成 %.1f ms，返回 %d 行", elapsed, len(rows))
        return rows
    except sqlite3.Error as exc:
        logger.exception("SQL 执行失败: %s", exc)
        raise
    finally:
        conn.close()


@mcp.tool
def list_cities() -> list[dict]:
    """列出数据库中已存储的所有城市、记录天数和日期范围。

    调用其他按城市查询的工具前，可先用本工具确认可用的城市名称。
    """
    logger.info("工具调用: list_cities")
    return _fetch("""
        SELECT city,
               COUNT(*) AS days,
               MIN(fx_date) AS first_date,
               MAX(fx_date) AS last_date
        FROM weather_data
        GROUP BY city
        ORDER BY city
    """)


@mcp.tool
def get_forecast(city: str, days: int = 7) -> list[dict]:
    """查询某城市从最早日期开始的天气预报（按日期升序）。

    Args:
        city: 城市名称，需与库中的名称一致（可先调用 list_cities）。
        days: 返回的天数，默认 7，最大 30。
    """
    days = max(1, min(int(days), 30))
    logger.info("工具调用: get_forecast | city=%s days=%d", city, days)
    cols = ", ".join(BRIEF_COLUMNS)
    return _fetch(
        f"SELECT {cols} FROM weather_data WHERE city = ? ORDER BY fx_date ASC LIMIT ?",
        (city, days),
    )


@mcp.tool
def get_weather_by_date(city: str, date: str) -> dict:
    """查询某城市指定日期的完整天气记录。

    Args:
        city: 城市名称。
        date: 日期，格式 YYYY-MM-DD，例如 2026-11-21。
    """
    logger.info("工具调用: get_weather_by_date | city=%s date=%s", city, date)
    rows = _fetch(
        "SELECT * FROM weather_data WHERE city = ? AND fx_date = ?", (city, date)
    )
    if not rows:
        return {"found": False, "city": city, "date": date, "message": "未找到对应记录"}
    return {"found": True, **rows[0]}


@mcp.tool
def query_weather_range(city: str, start_date: str, end_date: str) -> list[dict]:
    """查询某城市一段日期范围内的天气记录（按日期升序）。

    Args:
        city: 城市名称。
        start_date: 起始日期，格式 YYYY-MM-DD。
        end_date: 结束日期，格式 YYYY-MM-DD。
    """
    logger.info(
        "工具调用: query_weather_range | city=%s %s ~ %s",
        city, start_date, end_date,
    )
    cols = ", ".join(BRIEF_COLUMNS)
    return _fetch(
        f"SELECT {cols} FROM weather_data "
        "WHERE city = ? AND fx_date BETWEEN ? AND ? ORDER BY fx_date",
        (city, start_date, end_date),
    )


@mcp.resource("weather://schema")
def weather_schema() -> str:
    """weather_data 表的字段说明，供构造查询时参考。"""
    logger.info("资源读取: weather://schema")
    return (
        "表 weather_data：每行是某城市某一天的天气预报，主键为 (city, fx_date)。\n"
        "字段：" + ", ".join(ALL_COLUMNS) + "。\n"
        "fx_date 格式为 YYYY-MM-DD；temp_max/temp_min 等为字符串形式的数字。"
    )


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    transport = os.getenv("MCP_TRANSPORT", "stdio").lower()
    logger.info("启动 weather-db | transport=%s | db=%s", transport, DB_PATH)
    if transport == "http":
        host = os.getenv("MCP_HOST", "127.0.0.1")
        port = int(os.getenv("MCP_PORT", "8000"))
        logger.info("HTTP 端点: http://%s:%d/mcp", host, port)
        mcp.run(transport="http", host=host, port=port)
    else:
        mcp.run()
