#!/usr/bin/env python3
"""
互联网洞察日报 · 每日自动生成脚本（RSS版）
由 熏儿 自动维护
无需 API Key，直接抓取 RSS 新闻源
聚焦国内互联网大厂·中厂·小厂动态
"""

import os, sys, re, json, datetime
import urllib.request, urllib.error
from pathlib import Path
from xml.etree import ElementTree as ET
from urllib.parse import quote

REPO_ROOT = Path(__file__).parent.parent
INDEX_PATH = REPO_ROOT / "index.html"

WEEKDAYS = ["周一","周二","周三","周四","周五","周六","周日"]

RSS_SOURCES = [
    {"url": "https://www.36kr.com/feed", "name": "36氪", "tags": ["字节","腾讯","阿里","美团","拼多多","百度","快手","小红书","京东","滴滴","网易","互联网","AI","裁员","融资","上市","外卖","电商","短剧","大模型"]},
    {"url": "https://www.qbitai.com/feed", "name": "量子位", "tags": ["AI","大模型","豆包","通义","文心","元宝","DeepSeek","Kimi"]},
    {"url": "https://rsshub.app/36kr/motif/bDzMsO6", "name": "36氪·创投", "tags": ["融资","投资","并购","IPO","上市","估值"]},
    {"url": "https://rsshub.app/ithome/ranking/daily", "name": "IT之家日榜", "tags": ["字节","腾讯","阿里","美团","百度","快手","京东","小红书","互联网","AI","裁员","融资","上市","产品"]},
    {"url": "https://rsshub.app/cls/telegraph", "name": "财联社电报", "tags": ["字节","腾讯","阿里","美团","拼多多","百度","快手","京东","互联网","AI","裁员","融资","上市","外卖","政策"]},
    {"url": "https://rsshub.app/wallstreetcn/live", "name": "华尔街见闻", "tags": ["腾讯","阿里","美团","拼多多","百度","互联网","AI","市值","财报","政策"]},
]

COMPANY_KEYWORDS = {
    "字节跳动": ["字节","ByteDance","抖音","豆包","TikTok","Doubao","可灵","即梦","火山"],
    "腾讯": ["腾讯","Tencent","微信","元宝","混元","QQ","腾讯云"],
    "阿里": ["阿里","Alibaba","淘宝","天猫","通义","阿里云","蚂蚁","支付宝","钉钉"],
    "美团": ["美团","Meituan","外卖","大众点评","即时零售"],
    "拼多多": ["拼多多","PDD","Temu"],
    "百度": ["百度","Baidu","文心","百度网盘","萝卜快跑"],
    "快手": ["快手","Kuaishou","可灵AI","磁力"],
    "京东": ["京东","JD","京东物流","京东外卖"],
    "小红书": ["小红书","Xiaohongshu","RED"],
    "滴滴": ["滴滴","Didi","出行"],
    "网易": ["网易","NetEase"],
    "DeepSeek": ["DeepSeek","深度求索"],
    "携程": ["携程","Ctrip"],
    "B站": ["B站","哔哩哔哩","bilibili"],
    "米哈游": ["米哈游","miHoYo","原神"],
    "SHEIN": ["SHEIN","希音"],
    "宇树科技": ["宇树","Unitree"],
    "微博": ["微博","Weibo"],
}

CO_CSS = {"字节跳动":"co-bd","腾讯":"co-tx","阿里":"co-al","美团":"co-mt","拼多多":"co-pdd","百度":"co-bd2","快手":"co-ks","京东":"co-jd","小红书":"co-xhs","滴滴":"co-dd","网易":"co-tx","DeepSeek":"co-bd2","携程":"co-dd","B站":"co-pdd","米哈游":"co-mt","SHEIN":"co-al","宇树科技":"co-bd2","微博":"co-tx"}

TIERS = {"字节跳动":"T1","腾讯":"T1","阿里":"T1","美团":"T1","拼多多":"T1","蚂蚁":"T1","百度":"T2","快手":"T2","京东":"T2","小红书":"T2","滴滴":"T2","网易":"T2","DeepSeek":"T3","宇树科技":"T3","米哈游":"T3","B站":"T3","SHEIN":"T3","携程":"T3","微博":"T3"}

TOPIC_KEYWORDS = {
    "ai": ["AI","大模型","豆包","通义","文心","元宝","DeepSeek","Kimi","LLM","GPT","人工智能","智能体","Agent","AIGC","推理","模型"],
    "layoff": ["裁员","优化","降本","人员调整","待岗","外包","N+1","离职","精简","组织调整","缩减","重组"],
    "competition": ["外卖大战","补贴","价格战","竞争","抢夺","市场份额","即时零售","版权","转播"],
    "finance": ["融资","投资","并购","IPO","上市","估值","收购","领投","对价","交割","备案","基金"],
    "product": ["发布","上线","推出","出海","新产品","功能更新","版本","付费","收费","商业化"],
    "policy": ["监管","政策","备案","反垄断","网信办","个人信息","隐私","行政指导","法规"],
    "industry": ["市值","估值","梯队","财报","营收","利润","亏损","增长","下滑","排名","座次"],
}

TOPIC_META = {
    "ai": ("🤖","AI产品动态","tk-orange"),
    "layoff": ("🔥","裁员/人事","tk-red"),
    "competition": ("⚔️","业务竞争","tk-pink"),
    "finance": ("💰","融资/并购","tk-green"),
    "product": ("🆕","新产品/出海","tk-blue"),
    "policy": ("📋","政策监管","tk-purple"),
    "industry": ("🏆","行业格局","tk-orange"),
}

def today_cn():
    return datetime.datetime.utcnow() + datetime.timedelta(hours=8)

def format_date(dt): return dt.strftime("%Y-%m-%d")

def fetch_rss(url, timeout=15):
    try:
        encoded_url = quote(url, safe='/:?=&')
        req = urllib.request.Request(encoded_url, headers={"User-Agent": "Mozilla/5.0 Internet-Insight-Bot/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read()
    except Exception as e:
        print(f"  WARN: fetch failed {url}: {e}")
        return None

def parse_rss(xml_bytes):
    items = []
    try:
        root = ET.fromstring(xml_bytes)
        for item in root.iter("item"):
            title = item.findtext("title","").strip()
            desc = item.findtext("description","").strip()
            link = item.findtext("link","").strip()
            pub = item.findtext("pubDate","").strip()
            if title: items.append({"title":title,"desc":desc[:300],"link":link,"pub":pub})
        if not items:
            ns = "{http://www.w3.org/2005/Atom}"
            for entry in root.iter(f"{ns}entry"):
                title = entry.findtext(f"{ns}title","").strip()
                summary = entry.findtext(f"{ns}summary","").strip()
                link_el = entry.find(f"{ns}link")
                link = link_el.get("href","") if link_el is not None else ""
                published = entry.findtext(f"{ns}published","").strip()
                items.append({"title":title,"desc":summary[:300],"link":link,"pub":published})
    except Exception as e:
        print(f"  WARN: parse RSS failed: {e}")
    return items

def parse_pub_date(pub_str):
    if not pub_str: return None
    for fmt in ["%a, %d %b %Y %H:%M:%S %z","%a, %d %b %Y %H:%M:%S","%Y-%m-%dT%H:%M:%S%z","%Y-%m-%dT%H:%M:%SZ","%Y-%m-%dT%H:%M:%S","%Y-%m-%d %H:%M:%S","%Y-%m-%d"]:
        try: return datetime.datetime.strptime(pub_str.strip(), fmt)
        except ValueError: continue
    return None

def is_related(title, tags):
    t = title.lower()
    return any(kw.lower() in t for kw in tags)

def classify_topic(title):
    t = title.lower()
    for cat, kws in TOPIC_KEYWORDS.items():
        if any(k.lower() in t for k in kws): return cat
    return "industry"

def identify_companies(title):
    found = []
    for co, kws in COMPANY_KEYWORDS.items():
        if any(kw.lower() in title.lower() for kw in kws): found.append(co)
    return found

def clean_html(text):
    return re.sub(r"<[^>]+>","",text or "").strip()[:200]

def shorten_title(title, max_len=30):
    t = re.sub(r"\s+"," ",title or "").strip()
    return t[:max_len].rstrip()+"…" if len(t)>max_len else t

def collect_news(date_str):
    dt = datetime.datetime.strptime(date_str,"%Y-%m-%d")
    cutoff_date = dt - datetime.timedelta(days=3)
    news_by_topic = {}
    all_items = []
    for src in RSS_SOURCES:
        print(f"  Fetching {src['name']}...")
        xml = fetch_rss(src["url"])
        if not xml: continue
        items = parse_rss(xml)
        count = 0
        for item in items[:60]:
            if not is_related(item["title"], src["tags"]): continue
            pub_dt = parse_pub_date(item["pub"])
            if pub_dt is not None:
                pub_naive = pub_dt.replace(tzinfo=None) if pub_dt.tzinfo else pub_dt
                if pub_naive < cutoff_date: continue
            cat = classify_topic(item["title"])
            companies = identify_companies(item["title"])
            entry = {"title":item["title"],"source":src["name"],"link":item.get("link",""),"desc":clean_html(item["desc"]),"pub":item.get("pub",""),"topic":cat,"companies":companies}
            if cat not in news_by_topic: news_by_topic[cat] = []
            if len(news_by_topic[cat]) < 8:
                news_by_topic[cat].append(entry)
                all_items.append(entry)
                count += 1
        print(f"     -> {count} internet related")
    return news_by_topic, all_items

def build_ticker_items(all_items, max_count=10):
    items = []
    seen = set()
    queues = {}
    priority = ["layoff","ai","competition","finance","product","policy","industry"]
    for cat in priority: queues[cat] = [i for i in all_items if i["topic"]==cat][:3]
    while len(items) < max_count:
        added = False
        for cat in priority:
            if not queues[cat]: continue
            item = queues[cat].pop(0)
            t = item["title"].strip()
            if not t or t in seen: continue
            seen.add(t)
            tag_class = TOPIC_META.get(cat,("🏆","行业","tk-orange"))[2]
            tag_label = TOPIC_META.get(cat,("🏆","行业","tk-orange"))[1].split("/")[0].split("·")[0]
            items.append({"tag_class":tag_class,"tag_label":tag_label,"text":shorten_title(t)})
            added = True
            if len(items) >= max_count: break
        if not added: break
    return items

def build_news_cards(news_by_topic):
    topic_order = ["ai","layoff","competition","finance","product","policy","industry"]
    html_parts = []
    for cat in topic_order:
        if cat not in news_by_topic or not news_by_topic[cat]: continue
        icon, title, _ = TOPIC_META[cat]
        items = news_by_topic[cat]
        cards_html = ""
        for item in items[:6]:
            co_tags = ""
            for co in item["companies"][:3]:
                css = CO_CSS.get(co,"co-bd2")
                co_tags += f'<span class="ni-co {css}">{co[:2]}</span>'
            date_str = ""
            pub_dt = parse_pub_date(item["pub"])
            if pub_dt: date_str = pub_dt.strftime("%m-%d")
            is_hot = "🔥" if item == items[0] else ""
            cards_html += f"""
            <div class="news-item">
              <div class="ni-top">{f'<span class="ni-hot">{is_hot}</span>' if is_hot else ''}{co_tags}<span class="ni-date">{date_str}</span></div>
              <div class="ni-title">{item['title']}</div>
              <div class="ni-desc">{item['desc'][:120]}</div>
              <div class="ni-src">来源：{item['source']}</div>
            </div>"""
        html_parts.append(f"""
          <div class="news-grid">
            <div class="news-cat-head">{icon} {title}</div>
            {cards_html}
          </div>""")
    return "\n".join(html_parts)

def build_company_cards(news_by_topic):
    co_news = {}
    for cat, items in news_by_topic.items():
        for item in items:
            for co in item["companies"]:
                if co not in co_news: co_news[co] = []
                co_news[co].append(item)
    if not co_news: return ""
    sorted_cos = sorted(co_news.items(), key=lambda x: -len(x[1]))
    cards = ""
    for co, items in sorted_cos[:8]:
        tier = TIERS.get(co,"T3")
        css = CO_CSS.get(co,"co-bd2")
        bullets = ""
        for item in items[:4]:
            t = item["title"][:40]
            if len(item["title"]) > 40: t += "…"
            bullets += f"<li>{t}</li>"
        cards += f"""
        <div class="co-card">
          <div class="co-head"><span class="co-name">{co}</span><span class="co-tier {css}">{tier}</span></div>
          <div class="co-body"><ul>{bullets}</ul></div>
        </div>"""
    return f'<div class="co-grid">{cards}</div>'

def build_topic_distribution(news_by_topic, all_items):
    topic_counts = {}
    for cat, items in news_by_topic.items(): topic_counts[cat] = len(items)
    total = sum(topic_counts.values()) or 1
    fills = {"ai":"fill-o","layoff":"fill-r","competition":"fill-pk","finance":"fill-g","product":"fill-b","policy":"fill-v","industry":"fill-o"}
    rows = ""
    for cat in ["layoff","ai","competition","finance","product","policy"]:
        if cat not in topic_counts: continue
        icon, name, _ = TOPIC_META[cat]
        count = topic_counts[cat]
        pct = round(count / total * 100)
        fill_cls = fills.get(cat,"fill-o")
        rows += f'<div class="topic-row"><span class="topic-ico">{icon}</span><span class="topic-name">{name}</span><div class="topic-bar-bg"><div class="topic-fill {fill_cls}" style="width:{pct}%"></div></div><span class="topic-pct">{pct}%</span></div>'
    return rows

def build_hot_companies(news_by_topic):
    co_news = {}
    for cat, items in news_by_topic.items():
        for item in items:
            for co in item["companies"]:
                if co not in co_news: co_news[co] = []
                co_news[co].append(item)
    sorted_cos = sorted(co_news.items(), key=lambda x: -len(x[1]))[:6]
    if not sorted_cos: return ""
    co_count_css = {"字节跳动":"co-bd","腾讯":"co-tx","美团":"co-mt","阿里":"co-al","小红书":"co-xhs","百度":"co-bd2","拼多多":"co-pdd"}
    rows = ""
    for co, items in sorted_cos:
        cnt = len(items)
        short = co[:2]
        desc = shorten_title(items[0]["title"], 14)
        css = co_count_css.get(co,"co-bd2")
        rows += f"""<div style="display:flex;align-items:center;gap:8px;padding:6px 10px;background:var(--bg);border-radius:8px;">
            <span style="font-weight:700;width:56px">{short}</span>
            <span style="color:var(--text-2);flex:1;font-size:11px">{desc}</span>
            <span style="font-size:10px;padding:2px 6px;border-radius:3px;" class="ni-co {css}">{cnt}条</span>
        </div>"""
    return rows

def render_archive_html(date_str, news_by_topic, all_items):
    """生成独立归档页 HTML"""
    dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    weekday = WEEKDAYS[dt.weekday()]
    news_cards = build_news_cards(news_by_topic)
    co_cards = build_company_cards(news_by_topic)
    topic_rows = build_topic_distribution(news_by_topic, all_items)
    total = len(all_items)

    # 上一天/下一天链接
    prev_dt = dt - datetime.timedelta(days=1)
    next_dt = dt + datetime.timedelta(days=1)
    prev_link = f"../{prev_dt.strftime('%Y-%m')}/{prev_dt.strftime('%Y-%m-%d')}.html"
    next_link = f"../{next_dt.strftime('%Y-%m')}/{next_dt.strftime('%Y-%m-%d')}.html"

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{date_str} 互联网洞察日报</title>
<style>
:root{{--bg:#f5f6f8;--card:#fff;--text-1:#111827;--text-2:#6b7280;--text-3:#9ca3af;--green:#10b981;--purple:#8b5cf6;--blue:#3b82f6;--red:#ef4444;--orange:#f59e0b;--pink:#ec4899;--r:12px;--shadow:0 2px 8px rgba(0,0,0,.06)}}
.dark{{--bg:#0f172a;--card:#1e293b;--text-1:#f1f5f9;--text-2:#94a3b8;--text-3:#64748b}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei',sans-serif;background:var(--bg);color:var(--text-1);line-height:1.5}}
a{{color:var(--purple);text-decoration:none}}
.header{{background:linear-gradient(135deg,#059669,#7c3aed 60%,#2563eb);padding:24px;position:relative}}
.dark .header{{background:linear-gradient(135deg,#065f46,#4c1d95 60%,#1e3a5f)}}
.header-inner{{max-width:960px;margin:auto;position:relative;z-index:1}}
.nav-row{{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px}}
.back-link{{color:rgba(255,255,255,.8);font-size:13px;display:flex;align-items:center;gap:6px}}
.back-link:hover{{color:#fff}}
.date-badge{{font-size:28px;font-weight:800;color:#fff}}
.date-sub{{font-size:14px;color:rgba(255,255,255,.75);margin-top:4px}}
.nav-btns{{display:flex;gap:8px}}
.nav-btn{{padding:6px 14px;border-radius:20px;background:rgba(255,255,255,.2);color:#fff;font-size:12px}}
.nav-btn:hover{{background:rgba(255,255,255,.35)}}
.main{{max-width:960px;margin:20px auto;padding:0 16px;display:flex;flex-direction:column;gap:16px}}
.card{{background:var(--card);border-radius:var(--r);box-shadow:var(--shadow);overflow:hidden}}
.card-head{{padding:12px 16px;font-size:14px;font-weight:700;border-bottom:1px solid var(--bg)}}
.card-body{{padding:16px}}
.news-grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}
.news-cat-head{{font-size:13px;font-weight:700;padding:8px 0 4px;display:flex;align-items:center;gap:6px;grid-column:1/-1}}
.news-item{{background:var(--bg);border-radius:10px;padding:12px}}
.ni-top{{display:flex;align-items:center;gap:6px;margin-bottom:4px}}
.ni-hot{{font-size:10px;padding:1px 6px;border-radius:3px;background:var(--red);color:#fff;font-weight:600}}
.ni-co{{font-size:10px;padding:1px 6px;border-radius:3px;font-weight:600}}
.co-bd{{background:#fef2f2;color:#dc2626}}.co-tx{{background:#eff6ff;color:#2563eb}}.co-al{{background:#fff7ed;color:#d97706}}.co-mt{{background:#ecfdf5;color:#059669}}.co-pdd{{background:#fdf2f8;color:#db2777}}.co-bd2{{background:#f5f3ff;color:#7c3aed}}.co-xhs{{background:#fff1f2;color:#e11d48}}.co-dd{{background:#f0fdf4;color:#16a34a}}.co-ks{{background:#fff1f2;color:#f43f5e}}.co-jd{{background:#dbeafe;color:#1d4ed8}}
.dark .co-bd{{background:#7f1d1d;color:#fca5a5}}.dark .co-tx{{background:#1e3a5f;color:#93c5fd}}.dark .co-al{{background:#78350f;color:#fbbf24}}.dark .co-mt{{background:#064e3b;color:#6ee7b7}}
.ni-date{{font-size:10px;color:var(--text-3)}}
.ni-title{{font-size:13px;font-weight:600;margin-bottom:3px;line-height:1.4}}
.ni-desc{{font-size:12px;color:var(--text-2);line-height:1.4}}
.ni-src{{font-size:10px;color:var(--text-3);margin-top:4px}}
.co-grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}
.co-card{{background:var(--bg);border-radius:10px;padding:12px}}
.co-head{{display:flex;align-items:center;gap:6px;margin-bottom:6px}}
.co-name{{font-size:14px;font-weight:700}}.co-tier{{font-size:10px;padding:1px 6px;border-radius:3px;font-weight:600}}
.co-body{{font-size:12px;color:var(--text-2);line-height:1.5}}.co-body li{{margin-left:14px;margin-bottom:2px}}
.topic-row{{display:flex;align-items:center;gap:8px;margin-bottom:8px;font-size:12px}}
.topic-ico{{width:18px;text-align:center}}.topic-name{{min-width:64px}}
.topic-bar-bg{{flex:1;height:14px;background:var(--bg);border-radius:7px;overflow:hidden}}
.topic-fill{{height:100%;border-radius:7px}}
.fill-r{{background:linear-gradient(90deg,#ef4444,#dc2626)}}.fill-o{{background:linear-gradient(90deg,#f59e0b,#d97706)}}.fill-pk{{background:linear-gradient(90deg,#ec4899,#db2777)}}.fill-g{{background:linear-gradient(90deg,#10b981,#059669)}}.fill-b{{background:linear-gradient(90deg,#3b82f6,#2563eb)}}.fill-v{{background:linear-gradient(90deg,#8b5cf6,#7c3aed)}}
.topic-pct{{min-width:28px;text-align:right;color:var(--text-2)}}
.footer{{max-width:960px;margin:24px auto;padding:16px;text-align:center;font-size:12px;color:var(--text-3);border-top:1px solid var(--bg)}}
@media(max-width:640px){{.news-grid,.co-grid{{grid-template-columns:1fr}}}}
</style>
</head>
<body>
<div class="header">
  <div class="header-inner">
    <div class="nav-row">
      <a class="back-link" href="../../index.html">← 返回首页</a>
      <div class="nav-btns">
        <a class="nav-btn" href="{prev_link}">← 前一天</a>
        <a class="nav-btn" href="{next_link}">后一天 →</a>
      </div>
    </div>
    <div class="date-badge">🔬 {dt.year}年{dt.month}月{dt.day}日 · {weekday}</div>
    <div class="date-sub">互联网洞察日报 · 共收录 {total} 条互联网相关新闻</div>
  </div>
</div>

<div class="main">
  <div class="card"><div class="card-head">📰 今日新闻</div><div class="card-body">
    {news_cards if news_cards else '<p style="color:var(--text-3);font-size:13px">暂无抓取到新闻</p>'}
  </div></div>

  {f'<div class="card"><div class="card-head">🏢 重点公司动态</div><div class="card-body">{co_cards}</div></div>' if co_cards else ''}

  {f'<div class="card"><div class="card-head">📊 话题分布</div><div class="card-body">{topic_rows}</div></div>' if topic_rows else ''}
</div>

<div class="footer">互联网洞察日报 · {date_str} · <a href="../../index.html">返回首页</a> · <a href="https://github.com/daniel-xiaoyan/internet-insight-daily" target="_blank">GitHub</a></div>
</body>
</html>"""


def save_archive(date_str, news_by_topic, all_items):
    """保存独立归档页"""
    dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    month_str = dt.strftime("%Y-%m")
    archive_dir = REPO_ROOT / "daily-reports" / month_str
    archive_dir.mkdir(parents=True, exist_ok=True)
    archive_path = archive_dir / f"{date_str}.html"
    html = render_archive_html(date_str, news_by_topic, all_items)
    archive_path.write_text(html, encoding="utf-8")
    print(f"  OK archive saved: daily-reports/{month_str}/{date_str}.html")
    return archive_path


def scan_archive_dates():
    """扫描已有归档文件，返回 {month_str: [day_int, ...]} 字典"""
    reports_dir = REPO_ROOT / "daily-reports"
    result = {}
    if not reports_dir.exists():
        return result
    for month_dir in sorted(reports_dir.iterdir()):
        if not month_dir.is_dir(): continue
        days = []
        for f in sorted(month_dir.glob("*.html")):
            try:
                day = int(f.stem.split("-")[2])
                days.append(day)
            except: pass
        if days:
            result[month_dir.name] = sorted(days)
    return result


def update_index(date_str, news_by_topic, all_items):
    content = INDEX_PATH.read_text(encoding="utf-8")
    dt = datetime.datetime.strptime(date_str,"%Y-%m-%d")
    content = re.sub(r'🔥 TODAY · \d+月\d+日', f'🔥 TODAY · {dt.month}月{dt.day}日', content)
    content = re.sub(r'\d{4}年\d+月\d+日 更新', f'{dt.year}年{dt.month}月{dt.day}日 更新', content)
    content = re.sub(r'\d{4}年\d+月\d+日 互联网洞察日报', f'{dt.year}年{dt.month}月{dt.day}日 互联网洞察日报', content)
    ticker_items = build_ticker_items(all_items)
    if ticker_items:
        ticker_html = ""
        for it in ticker_items: ticker_html += f'<div class="tk-item"><span class="tk-tag {it["tag_class"]}">{it["tag_label"]}</span>{it["text"]}</div>\n'
        ticker_dup = ticker_html + ticker_html
        content = re.sub(r'(<div class="ticker-scroll">)[\s\S]*?(</div>\s*</div>\s*</div>)', f'\\g<1>\n{ticker_dup}      \\g<2>', content, count=1)
    news_cards = build_news_cards(news_by_topic)
    if news_cards:
        content = re.sub(r'(<div class="tabpanel active" id="tab-daily">)[\s\S]*?(</div>\s*<!-- END DAILY TAB -->)', f'\\g<1>\n          {news_cards}\n        \\g<2>', content, count=1)
    topic_rows = build_topic_distribution(news_by_topic, all_items)
    if topic_rows:
        content = re.sub(r'(<!-- topic -->)[\s\S]*?(<!-- end topic -->)', f'\\g<1>\n                    {topic_rows}\n              \\g<2>', content, count=1)
    hot_cos = build_hot_companies(news_by_topic)
    if hot_cos:
        content = re.sub(r'(<!-- Hot Companies -->[\s\S]*?<div style="display:flex;flex-direction:column;gap:8px;">)[\s\S]*?(</div>\s*</div>\s*</div>\s*<!-- end hot companies -->)', f'\\g<1>\n                    {hot_cos}\n                \\g<2>', content, count=1)
    co_cards = build_company_cards(news_by_topic)
    if co_cards:
        content = re.sub(r'(<div class="tabpanel" id="tab-tracker">)[\s\S]*?(</div>\s*<!-- END TRACKER TAB -->)', f'\\g<1>\n          {co_cards}\n        \\g<2>', content, count=1)

    # 更新日历 - 先清除所有 today 标记，再标注今天
    content = re.sub(r' today"', '"', content)  # 移除所有today class
    content = re.sub(rf'(class="cal-d(?:[^"]*)?)">({dt.day})</div>', f'\\g<1> today">\\g<2></div>', content, count=1)
    # 扫描归档，更新日历上的 has-d 标记
    archive_dates = scan_archive_dates()
    month_str = dt.strftime("%Y-%m")
    if month_str in archive_dates:
        for day in archive_dates[month_str]:
            archive_link = f"daily-reports/{month_str}/{month_str}-{day:02d}.html"
            content = re.sub(
                rf'(class="cal-d(?:[^"]*)?")(>{day}</div>)',
                f'\\g<1>\\g<2>',
                content, count=1
            )
        # 为有归档的日期加上 has-d 和链接
        def mark_has_d(m):
            full = m.group(0)
            # 提取日期数字
            day_match = re.search(r'>(\d+)</div>$', full)
            if not day_match: return full
            day_num = int(day_match.group(1))
            if day_num in archive_dates.get(month_str, []):
                link = f"daily-reports/{month_str}/{month_str}-{day_num:02d}.html"
                # Replace <div class="cal-d...">N</div> with <a href="..." class="cal-d has-d...">N</a>
                classes = re.search(r'class="(cal-d[^"]*)"', full)
                cls = classes.group(1) if classes else "cal-d"
                if "has-d" not in cls:
                    cls = cls + " has-d"
                return f'<a href="{link}" class="{cls}">{day_num}</a>'
            return full
        content = re.sub(r'<(?:div|a)[^>]*class="cal-d[^"]*"[^>]*>\d+</(?:div|a)>', mark_has_d, content)

    summary_parts = []
    for cat in ["ai","layoff","competition","finance"]:
        if cat in news_by_topic and news_by_topic[cat]:
            t = shorten_title(news_by_topic[cat][0]["title"],12)
            summary_parts.append(t)
    if summary_parts:
        dc_sum = "·".join(summary_parts[:3])+"→"
        content = re.sub(r'(<div class="dc-sum">)[^<]*(</div>)', f'\\g<1>{dc_sum}\\g<2>', content, count=1)

    # 更新今日日报卡片链接
    archive_link = f"daily-reports/{dt.strftime('%Y-%m')}/{date_str}.html"
    content = re.sub(r'(<div class="daily-card"[^>]*>)', f'<a href="{archive_link}" style="text-decoration:none;color:inherit"><div class="daily-card">', content, count=1)
    content = re.sub(r'(</div>\s*<!-- end daily-card -->)', f'</div></a>\\g<1>', content, count=1)

    # 更新累计日报数
    total_archives = sum(len(v) for v in scan_archive_dates().values())
    content = re.sub(r'📅 \d+</div><div class="ts-lab">累计日报', f'📅 {total_archives}</div><div class="ts-lab">累计日报', content, count=1)

    INDEX_PATH.write_text(content, encoding="utf-8")
    print(f"  OK index.html updated ({date_str})")


def main(target_date=None):
    dt = datetime.datetime.strptime(target_date,"%Y-%m-%d") if target_date else today_cn()
    date_str = format_date(dt)
    print(f"\nGenerating {date_str} Internet Insight Daily (RSS mode)")
    news_by_topic, all_items = collect_news(date_str)
    total = len(all_items)
    print(f"  Total: {total} internet related news")
    if total == 0:
        print("  WARN: no news found, skip update")
        return
    save_archive(date_str, news_by_topic, all_items)
    update_index(date_str, news_by_topic, all_items)
    print(f"Done! {date_str} Internet Insight Daily updated with {total} news\n")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
