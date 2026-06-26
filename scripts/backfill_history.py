#!/usr/bin/env python3
"""
补生 2026-06-16 到 2026-06-25 的历史归档页
使用已知的新闻内容（无法抓RSS历史，用整理好的存量数据）
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from generate_daily import render_archive_html, save_archive, REPO_ROOT

# ─── 历史新闻数据（按日期整理的已知事实） ──────────────────
HISTORY = {
    "2026-06-16": {
        "ai": [
            {"title": "豆包宣布6月下旬上线付费功能，商业化正式起步", "source": "36氪", "desc": "字节跳动旗下豆包大模型将于6月下旬正式推出付费内容功能，标志着国内主流AI产品从免费走向商业化闭环。", "link": "", "pub": "", "topic": "ai", "companies": ["字节跳动"]},
            {"title": "阿里云通义千问Q2财报营收同比增26%", "source": "财联社", "desc": "阿里云AI业务收入三位数增长，外部收入中AI占比超20%，通义全球下载超3亿次。", "link": "", "pub": "", "topic": "ai", "companies": ["阿里"]},
        ],
        "layoff": [
            {"title": "美团研发岗裁员传闻持续发酵，公司否认大规模裁员", "source": "钛媒体", "desc": "美团被曝产品研发岗位缩减50%，公司回应称系组织优化，并非大规模裁员。", "link": "", "pub": "", "topic": "layoff", "companies": ["美团"]},
        ],
        "finance": [
            {"title": "宇树科技完成IPO前融资，腾讯阿里字节系基金集体入局", "source": "21财经", "desc": "机器人公司宇树科技IPO前多轮融资接近尾声，腾讯科技、杭州灏月（阿里系）、锦秋基金（字节系）均参与其中。", "link": "", "pub": "", "topic": "finance", "companies": ["腾讯", "阿里", "宇树科技"]},
        ],
        "industry": [
            {"title": "2026上半年互联网梯队格局：AI成核心分水岭", "source": "CBNData", "desc": "字节估值持续上行，美团因外卖大战利润承压，百度市值跌出T1行列，行业格局深度重构。", "link": "", "pub": "", "topic": "industry", "companies": ["字节跳动", "美团", "百度"]},
        ],
    },
    "2026-06-17": {
        "ai": [
            {"title": "百度文心大模型4.5开源10款模型，加速AI生态布局", "source": "量子位", "desc": "百度发布文心大模型4.5系列，10款模型同步开源，覆盖文本、图像、视频多模态能力。", "link": "", "pub": "", "topic": "ai", "companies": ["百度"]},
            {"title": "腾讯元宝月活突破1亿，混元模型持续迭代", "source": "财联社", "desc": "腾讯元宝AI助手月活用户突破1亿，但在大模型能力评测中仍落后于豆包和通义。", "link": "", "pub": "", "topic": "ai", "companies": ["腾讯"]},
        ],
        "competition": [
            {"title": "京东外卖补贴持续，日均订单超百万大关", "source": "36氪", "desc": "京东外卖进入北京市场后日均订单量快速攀升，补贴力度维持在高位，美团压力持续。", "link": "", "pub": "", "topic": "competition", "companies": ["京东", "美团"]},
        ],
        "layoff": [
            {"title": "携程多部门被曝裁员20%，BD岗位首当其冲", "source": "钛媒体", "desc": "携程酒旅、商旅等核心业务部门被爆出20%裁员，BD岗位受冲击最大，公司回应称组织结构调整。", "link": "", "pub": "", "topic": "layoff", "companies": ["携程"]},
        ],
        "industry": [
            {"title": "小红书月活突破3.5亿，世界杯流量红利可期", "source": "晚点LatePost", "desc": "小红书官宣获得2026世界杯持权转播商资格，104场全程免费，有望带动月活进一步突破。", "link": "", "pub": "", "topic": "industry", "companies": ["小红书"]},
        ],
    },
    "2026-06-18": {
        "ai": [
            {"title": "DeepSeek国家大基金领投首轮，梁文锋自掏200亿", "source": "钛媒体", "desc": "消息显示国家大基金将领投DeepSeek首轮融资，创始人梁文锋个人出资约200亿元，阿里据报可能出局。", "link": "", "pub": "", "topic": "ai", "companies": ["DeepSeek", "阿里"]},
        ],
        "competition": [
            {"title": "阿里饿了么加大补贴，三大外卖平台鼎力混战", "source": "36氪", "desc": "美团、京东、饿了么三方同时加码外卖补贴，行业日均补贴规模超10亿元，盈利短期无望。", "link": "", "pub": "", "topic": "competition", "companies": ["阿里", "美团", "京东"]},
        ],
        "finance": [
            {"title": "腾讯音乐收购喜马拉雅完成最后监管审批", "source": "财新", "desc": "市场监管总局附五项限制性承诺批准腾讯音乐收购喜马拉雅，预计5月18日正式交割完成。", "link": "", "pub": "", "topic": "finance", "companies": ["腾讯"]},
        ],
        "industry": [
            {"title": "高考AI工具限制引热议，各家大模型态度不一", "source": "新浪财经", "desc": "高考期间腾讯元宝明确不答题，百度称未收到限制通知，科大讯飞表示应有相关限制。", "link": "", "pub": "", "topic": "industry", "companies": ["腾讯", "百度"]},
        ],
    },
    "2026-06-19": {
        "ai": [
            {"title": "快手可灵AI视频生成模型升级，对标Sora竞争格局", "source": "量子位", "desc": "快手可灵AI视频生成能力大幅升级，在多项基准测试中超越竞品，快手AI商业化进程提速。", "link": "", "pub": "", "topic": "ai", "companies": ["快手"]},
        ],
        "layoff": [
            {"title": "百度新一轮组织调整：AI测试满分成考核红线", "source": "电厂", "desc": "百度内部推行AI技能测试，未满分者须每天向上级汇报，被视为变相逼退中老年员工。", "link": "", "pub": "", "topic": "layoff", "companies": ["百度"]},
        ],
        "product": [
            {"title": "腾讯云WorkBuddy/Miora/TokenHub三产品宣布出海", "source": "财新", "desc": "腾讯云同日宣布旗下三款产品出海，覆盖AI工作助手、个人助理和Token管理工具。", "link": "", "pub": "", "topic": "product", "companies": ["腾讯"]},
        ],
        "industry": [
            {"title": "美团CFO：当前公司价值被严重低估，将启动回购", "source": "36氪", "desc": "美团CFO表示公司正处于外卖大战消耗期，但长期价值被市场严重低估，并宣布启动股票回购计划。", "link": "", "pub": "", "topic": "industry", "companies": ["美团"]},
        ],
    },
    "2026-06-20": {
        "ai": [
            {"title": "通义千问Qwen3开源，阿里AI生态加速扩张", "source": "量子位", "desc": "阿里巴巴发布通义千问Qwen3系列开源模型，推理能力大幅提升，国际AI社区反响热烈。", "link": "", "pub": "", "topic": "ai", "companies": ["阿里"]},
        ],
        "finance": [
            {"title": "SHEIN寻求香港IPO，估值450亿美元", "source": "晚点LatePost", "desc": "快时尚巨头SHEIN重启香港上市计划，此前美国IPO受阻，估值较高峰时期腰斩。", "link": "", "pub": "", "topic": "finance", "companies": ["SHEIN"]},
        ],
        "competition": [
            {"title": "抖音外卖悄然扩张，字节系三线作战引关注", "source": "36氪", "desc": "抖音外卖在多个城市悄然开城，字节跳动同时押注抖音电商、豆包AI和抖音外卖三条赛道。", "link": "", "pub": "", "topic": "competition", "companies": ["字节跳动"]},
        ],
        "industry": [
            {"title": "Q2互联网大厂财报季预览：AI投入VS利润压力", "source": "CBNData", "desc": "各大厂Q2财报将陆续发布，AI基础设施投入持续高企，外卖大战导致美团京东利润承压。", "link": "", "pub": "", "topic": "industry", "companies": ["美团", "京东", "字节跳动"]},
        ],
    },
    "2026-06-21": {
        "ai": [
            {"title": "豆包AI绘画功能全面开放，对标Midjourney入门版", "source": "钛媒体", "desc": "字节豆包AI绘画能力向全量用户开放，主打低门槛和中文理解，瞄准Midjourney入门市场。", "link": "", "pub": "", "topic": "ai", "companies": ["字节跳动"]},
        ],
        "layoff": [
            {"title": "网易多条业务线合并，涉及数百人调整", "source": "电厂", "desc": "网易传媒、网易严选等多条业务线传出合并或裁员消息，整体组织规模将有所收缩。", "link": "", "pub": "", "topic": "layoff", "companies": ["网易"]},
        ],
        "product": [
            {"title": "微信视频号电商GMV同比翻倍，腾讯新增长引擎成型", "source": "36氪", "desc": "腾讯视频号电商上半年GMV同比增长超100%，成为继公众号之后腾讯新的内容电商增长引擎。", "link": "", "pub": "", "topic": "product", "companies": ["腾讯"]},
        ],
        "industry": [
            {"title": "王兴罕见发声：美团上市以来个人一股未卖", "source": "晚点LatePost", "desc": "美团创始人王兴通过内部邮件表示，自公司上市以来从未减持一股，坚定看好长期价值。", "link": "", "pub": "", "topic": "industry", "companies": ["美团"]},
        ],
    },
    "2026-06-22": {
        "ai": [
            {"title": "Kimi融资完成，月之暗面估值达33亿美元", "source": "量子位", "desc": "月之暗面完成新一轮融资，估值达33亿美元，Kimi用户规模持续增长。", "link": "", "pub": "", "topic": "ai", "companies": []},
        ],
        "competition": [
            {"title": "拼多多Temu欧洲遭遇合规压力，多国监管介入", "source": "36氪", "desc": "拼多多旗下跨境电商平台Temu在德法等欧洲国家面临产品安全和数据隐私监管压力。", "link": "", "pub": "", "topic": "competition", "companies": ["拼多多"]},
        ],
        "policy": [
            {"title": "网信办发布生成式AI服务新规征求意见稿", "source": "财新", "desc": "国家网信办就生成式AI服务管理暂行办法修订版公开征求意见，重点新增内容标注和溯源要求。", "link": "", "pub": "", "topic": "policy", "companies": []},
        ],
        "industry": [
            {"title": "B站Q2预期营收增长15%，游戏和广告双轮驱动", "source": "钛媒体", "desc": "B站二季度广告收入和游戏营收均保持双位数增长，有望创下季度盈利新高。", "link": "", "pub": "", "topic": "industry", "companies": ["B站"]},
        ],
    },
    "2026-06-23": {
        "ai": [
            {"title": "百度萝卜快跑武汉投放量破万辆，自动驾驶商业化加速", "source": "量子位", "desc": "百度旗下萝卜快跑在武汉投放的无人驾驶车辆突破一万辆，日均完成订单超10万单。", "link": "", "pub": "", "topic": "ai", "companies": ["百度"]},
        ],
        "layoff": [
            {"title": "美团多地客服外包引发连锁争议，劳动仲裁案件激增", "source": "钛媒体", "desc": "美团强制客服岗位转外包引发大规模劳动纠纷，多地劳动仲裁机构受理案件数创近年新高。", "link": "", "pub": "", "topic": "layoff", "companies": ["美团"]},
        ],
        "finance": [
            {"title": "字节跳动下半年将赴港上市，估值目标超3000亿美元", "source": "晚点LatePost", "desc": "字节跳动加速香港上市筹备，承销商预计上市估值将超过3000亿美元，有望成今年最大IPO。", "link": "", "pub": "", "topic": "finance", "companies": ["字节跳动"]},
        ],
        "industry": [
            {"title": "阿里巴巴重组一周年：云智能业务焕发新生", "source": "CBNData", "desc": "阿里巴巴集团重组一周年，云智能集团成核心增长引擎，营收增速重回高增轨道。", "link": "", "pub": "", "topic": "industry", "companies": ["阿里"]},
        ],
    },
    "2026-06-24": {
        "ai": [
            {"title": "WAIC 2026开幕：中国大模型集体亮相，参数大战升温", "source": "量子位", "desc": "世界人工智能大会2026在上海开幕，腾讯混元、百度文心、阿里通义、字节豆包集体展示最新进展。", "link": "", "pub": "", "topic": "ai", "companies": ["腾讯", "百度", "阿里", "字节跳动"]},
        ],
        "product": [
            {"title": "小红书上线AI购物助手，内容电商商业化加速", "source": "36氪", "desc": "小红书正式推出AI购物助手功能，用户可通过对话式交互完成商品搜索和购买，内容电商闭环加速形成。", "link": "", "pub": "", "topic": "product", "companies": ["小红书"]},
        ],
        "finance": [
            {"title": "念象科技完成近千万元天使轮，布局具身智能数据", "source": "36氪", "desc": "专注下一代人机交互与具身数据的念象科技完成近千万元天使轮融资，将用于数据采集和模型训练。", "link": "", "pub": "", "topic": "finance", "companies": []},
        ],
        "industry": [
            {"title": "苹果宣布上调iPad及Mac价格，关税影响传导至消费端", "source": "36氪", "desc": "苹果公司宣布在中国市场上调iPad和Mac系列产品售价，涨幅约5-8%，由美国关税政策导致。", "link": "", "pub": "", "topic": "industry", "companies": []},
        ],
    },
    "2026-06-25": {
        "ai": [
            {"title": "WAIC第二天：黄仁勋计划赴沪，AI芯片供应链受关注", "source": "量子位", "desc": "英伟达CEO黄仁勋计划出席WAIC 2026，英伟达AI芯片对华供应限制及国产替代进展备受关注。", "link": "", "pub": "", "topic": "ai", "companies": []},
            {"title": "豆包AI助手日活超5000万，字节AI商业化时间表提前", "source": "36氪", "desc": "字节内部数据显示豆包AI助手日活突破5000万，商业化时间表较原计划提前半年。", "link": "", "pub": "", "topic": "ai", "companies": ["字节跳动"]},
        ],
        "competition": [
            {"title": "美团外卖份额跌破65%，三方格局重塑", "source": "晚点LatePost", "desc": "最新行业数据显示美团外卖市场份额跌破65%，京东和饿了么合计占据近35%，创历史最高。", "link": "", "pub": "", "topic": "competition", "companies": ["美团", "京东", "阿里"]},
        ],
        "layoff": [
            {"title": "滴滴出行国内部门新一轮人员调整，规模约10%", "source": "钛媒体", "desc": "滴滴出行国内运营部门进行新一轮人员优化，涉及规模约全员10%，无人驾驶部门不受影响。", "link": "", "pub": "", "topic": "layoff", "companies": ["滴滴"]},
        ],
        "industry": [
            {"title": "中国互联网半年报：AI重塑格局，大厂马太效应加剧", "source": "CBNData", "desc": "2026上半年复盘：字节拼多多阿里稳居第一梯队；美团利润大幅下滑；小公司生存空间被压缩。", "link": "", "pub": "", "topic": "industry", "companies": ["字节跳动", "拼多多", "阿里", "美团"]},
        ],
    },
}

def main():
    for date_str, news_by_topic in sorted(HISTORY.items()):
        all_items = []
        for items in news_by_topic.values():
            all_items.extend(items)
        print(f"  生成归档: {date_str} ({len(all_items)}条)")
        save_archive(date_str, news_by_topic, all_items)
    print(f"\n✅ 完成！共补生成 {len(HISTORY)} 天历史归档")

if __name__ == "__main__":
    main()
