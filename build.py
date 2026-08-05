# -*- coding: utf-8 -*-
"""Сборка дашборда Factum Group Tracking.

Тянет два опубликованных CSV Google-таблицы «Менеджеры отчет»
(URL приходят из секретов Actions), извлекает метрики и собирает
index.html из template.html.
"""
import csv
import io
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone, timedelta

CSV_MONTHLY_URL = os.environ["CSV_MONTHLY_URL"]  # вкладка «Аналитика продаж месячная 2026»
CSV_B2B_URL = os.environ["CSV_B2B_URL"]          # вкладка «Аналитика B2B»

MONTH_NUM = {
    "Январь": 1, "Февраль": 2, "Март": 3, "Апрель": 4, "Май": 5, "Июнь": 6,
    "Июль": 7, "Август": 8, "Сентябрь": 9, "Октябрь": 10, "Ноябрь": 11, "Декабрь": 12,
}
MONTH_ABBR = ["Янв", "Фев", "Мар", "Апр", "Май", "Июн", "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"]


def fetch_csv(url):
    with urllib.request.urlopen(url, timeout=60) as r:
        data = r.read().decode("utf-8")
    return list(csv.reader(io.StringIO(data)))


def num(s):
    s = (s or "").strip().replace(" ", "").replace(",", ".")
    if not s:
        return None
    try:
        return round(float(s))
    except ValueError:
        return None


def month_of(label):
    for name, n in MONTH_NUM.items():
        if label.startswith(name):
            return n
    return None


def parse_monthly(rows):
    """{('fact'|'plan', month, 'Депозиты'|'Покупки') -> value} (колонка ВСЕГО)."""
    out = {}
    cur = None
    for row in rows:
        a = (row[0] if len(row) > 0 else "").strip()
        if a and "2026" in a:
            kind = "fact" if "Факт" in a else ("plan" if "План" in a else None)
            m = month_of(a)
            cur = (kind, m) if kind and m else None
            # в строке заголовка блока тоже есть критерий — не пропускаем её
        if cur is None:
            continue
        crit = (row[1] if len(row) > 1 else "").strip()
        if crit.startswith("Депозиты Факт"):
            out[(cur[0], cur[1], "Депозиты чистые")] = num(row[2] if len(row) > 2 else "")
        elif crit in ("Депозиты", "Покупки"):
            out[(cur[0], cur[1], crit)] = num(row[2] if len(row) > 2 else "")
    return out


def parse_b2b(rows):
    """{month -> покупки (Всего)}"""
    out = {}
    cur = None
    for row in rows:
        a = (row[0] if len(row) > 0 else "").strip()
        if a:
            m = month_of(a)
            if m and "Факт" in a:
                cur = m
            elif m:
                cur = None
        crit = (row[1] if len(row) > 1 else "").strip()
        if cur and crit == "Покупки":
            out[cur] = num(row[2] if len(row) > 2 else "")
    return out


def main():
    kyiv = timezone(timedelta(hours=3))
    now = datetime.now(timezone.utc).astimezone(kyiv)
    cm = now.month

    monthly = parse_monthly(fetch_csv(CSV_MONTHLY_URL))
    b2b = parse_b2b(fetch_csv(CSV_B2B_URL))

    months = [MONTH_ABBR[i - 1] for i in range(1, cm + 1)]

    def series(crit):
        return [monthly.get(("fact", m, crit)) for m in range(1, cm + 1)]

    dep_fact = monthly.get(("fact", cm, "Депозиты")) or 0
    buy_fact = monthly.get(("fact", cm, "Покупки")) or 0
    buy_plan = monthly.get(("plan", cm, "Покупки"))
    # выполнение плана по депозитам считается по чистым депозитам («Депозиты Фактические»)
    dep_net_fact = monthly.get(("fact", cm, "Депозиты чистые")) or 0
    dep_net_plan = monthly.get(("plan", cm, "Депозиты чистые"))

    b2b_months_nums = sorted(b2b)
    b2b_months = [MONTH_ABBR[m - 1] for m in b2b_months_nums]
    b2b_series = [b2b[m] for m in b2b_months_nums]
    b2b_fact = b2b.get(cm) or 0

    projects = [
        {
            "name": "Factum Auto", "desc": "Импорт авто под заказ", "demo": False, "span2": True,
            "color": "var(--series-1)",
            "metrics": [
                {"label": "Депозиты", "fact": dep_fact, "plan": dep_net_plan, "planFact": dep_net_fact,
                 "planNote": f"план по чистым депозитам: {dep_net_plan} · факт чистых: {dep_net_fact}" if dep_net_plan else None,
                 "series": series("Депозиты"), "color": "var(--series-1-lt)"},
                {"label": "Покупки", "fact": buy_fact, "plan": buy_plan,
                 "series": series("Покупки"), "color": "var(--series-1)"},
            ],
            "chartTitle": "Факт по месяцам, 2026 (текущий месяц — идёт)",
            "months": months,
        },
        {
            "name": "Operator-EX", "desc": "Экспорт и продажи дилерам", "demo": False, "span2": False,
            "color": "var(--series-2)",
            "metrics": [
                {"label": "Куплено авто дилерами", "fact": b2b_fact, "plan": None,
                 "series": b2b_series, "color": "var(--series-2)"},
            ],
            "chartTitle": "Факт по месяцам (аналитика ведётся с июня; текущий — идёт)",
            "months": b2b_months,
        },
        {
            "name": "СТО", "desc": "Кузовной ремонт и покраска", "demo": True, "span2": False,
            "color": "var(--series-3)",
            "metrics": [
                {"label": "Выдано авто в текущем месяце", "fact": 9, "plan": 12,
                 "series": [6, 7, 7, 8, 8, 9, 8, 9], "color": "var(--series-3)"},
            ],
            "chartTitle": "Факт по месяцам, 2026 (демо)",
            "months": [MONTH_ABBR[i] for i in range(8)],
        },
        {
            "name": "Factum Auto Dealer", "desc": "Продажа авто в наличии", "demo": True, "span2": False,
            "metrics": [
                {"label": "Продано авто", "fact": 12, "plan": 15,
                 "series": [10, 11, 13, 12, 14, 13, 14, 12], "color": "var(--series-4)"},
            ],
            "color": "var(--series-4)",
            "chartTitle": "Факт по месяцам, 2026 (демо)",
            "months": [MONTH_ABBR[i] for i in range(8)],
        },
    ]

    stamp = now.strftime("%d.%m.%Y %H:%M") + " (Киев)"
    tpl = open("template.html", encoding="utf-8").read()
    html = tpl.replace("__DATA_JSON__", json.dumps(projects, ensure_ascii=False))
    html = html.replace("__STAMP__", stamp)
    # заголовок месяца в шапке
    RU_MONTHS = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль",
                 "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
    html = html.replace("Август 2026 ·", f"{RU_MONTHS[cm - 1]} {now.year} ·")
    open("index.html", "w", encoding="utf-8").write(html)
    print("ok:", stamp, "| депозиты", dep_fact, "| покупки", buy_fact, "| b2b", b2b_fact)


if __name__ == "__main__":
    sys.exit(main())
