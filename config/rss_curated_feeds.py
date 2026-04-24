"""精选 RSS 列表（每日抓取用）

由编辑整理；通过 `config/sources.py` 的 `curated_ai_daily_rss` 并入主 SOURCES。
维护说明：
- 仅填 **RSS/Atom URL**；API、HTML 话题页勿放入（feedparser 无法当 RSS 解析）。
- 已存在于其它分组且 URL 完全相同的条目会在此 **去重省略**，请到对应分组把 `enabled` 打开。
- 抓取失败时用 feedparser 单独测：`feedparser.parse(url)` 看 `entries` 是否 > 0。

未纳入本列表（需另做抓取或换真实 Feed）：
- Papers With Code `.../api/v1/latest/`（JSON API，非 RSS）
- 知乎 / 掘金 / SegmentFault 话题页（一般为 HTML，非 Feed）
"""

# 下列条目默认 enabled=True；个别「可能不是标准 RSS」的站点为 False，验证后可改
CURATED_RSS_GROUP: list[dict] = [
    # --- AI 资讯 · 国际 ---
    {"name": "openai_root_feed", "type": "rss", "url": "https://openai.com/feed/", "enabled": True, "value": "OpenAI 主 Feed"},
    {"name": "google_research_blog", "type": "rss", "url": "https://research.google/blog/rss.xml", "enabled": True, "value": "Google Research Blog"},
    {"name": "deepmind_blog", "type": "rss", "url": "https://deepmind.google/blog/rss.xml", "enabled": True, "value": "DeepMind Blog"},
    {"name": "anthropic_root_rss", "type": "rss", "url": "https://www.anthropic.com/rss", "enabled": True, "value": "Anthropic 根 RSS"},
    {"name": "venturebeat_ai", "type": "rss", "url": "https://venturebeat.com/category/ai/feed/", "enabled": True, "value": "VentureBeat AI"},
    {"name": "deeplearning_ai", "type": "rss", "url": "https://www.deeplearning.ai/feed/", "enabled": True, "value": "DeepLearning.AI"},
    {"name": "towards_data_science", "type": "rss", "url": "https://towardsdatascience.com/feed", "enabled": True, "value": "Towards Data Science"},
    {"name": "machinelearningmastery", "type": "rss", "url": "https://machinelearningmastery.com/feed/", "enabled": True, "value": "Machine Learning Mastery"},
    {"name": "anthropic_alignment", "type": "rss", "url": "https://alignment.anthropic.com/feed/", "enabled": True, "value": "Anthropic Alignment Blog"},
    # --- 中文 ---
    {"name": "jiqizhixin", "type": "rss", "url": "https://www.jiqizhixin.com/rss", "enabled": True, "value": "机器之心"},
    {"name": "qbitai", "type": "rss", "url": "https://www.qbitai.com/feed", "enabled": True, "value": "量子位"},
    {"name": "aitechtalk", "type": "rss", "url": "https://www.aitechtalk.com/feed/", "enabled": True, "value": "AI 科技评论"},
    {"name": "hyper_ai", "type": "rss", "url": "https://hyper.ai/rss", "enabled": True, "value": "HyperAI 超神经"},
    {"name": "paperweekly", "type": "rss", "url": "https://www.paperweekly.site/rss", "enabled": True, "value": "PaperWeekly"},
    # --- arXiv ---
    {"name": "arxiv_cs_ai", "type": "rss", "url": "http://export.arxiv.org/rss/cs.AI", "enabled": True, "value": "arXiv cs.AI"},
    {"name": "arxiv_cs_lg", "type": "rss", "url": "http://export.arxiv.org/rss/cs.LG", "enabled": True, "value": "arXiv cs.LG"},
    {"name": "arxiv_cs_cl", "type": "rss", "url": "http://export.arxiv.org/rss/cs.CL", "enabled": True, "value": "arXiv cs.CL"},
    {"name": "arxiv_cs_cv", "type": "rss", "url": "http://export.arxiv.org/rss/cs.CV", "enabled": True, "value": "arXiv cs.CV"},
    {"name": "github_trends_ai", "type": "rss", "url": "https://github-trends.com/rss/ai", "enabled": True, "value": "GitHub Trends AI"},
    {"name": "openreview_rss", "type": "rss", "url": "https://openreview.net/rss", "enabled": True, "value": "OpenReview"},
    # --- Newsletter ---
    {"name": "deeplearning_the_batch", "type": "rss", "url": "https://www.deeplearning.ai/the-batch/rss/", "enabled": True, "value": "The Batch"},
    {"name": "jack_clark_import_ai", "type": "rss", "url": "https://jack-clark.net/feed/", "enabled": True, "value": "Import AI (Jack Clark)"},
    {"name": "ai_snake_oil", "type": "rss", "url": "https://www.aisnakeoil.com/feed", "enabled": True, "value": "AI Snake Oil"},
    {"name": "exponential_view", "type": "rss", "url": "https://www.exponentialview.co/p/feed", "enabled": True, "value": "Exponential View"},
    {"name": "bens_bites_rss", "type": "rss", "url": "https://bensbites.beehiiv.com/rss", "enabled": True, "value": "Ben's Bites (rss)"},
    {"name": "the_neuron", "type": "rss", "url": "https://theneuron.ai/rss", "enabled": True, "value": "The Neuron"},
    {"name": "superhuman_beehiiv", "type": "rss", "url": "https://superhuman.beehiiv.com/rss", "enabled": True, "value": "Superhuman"},
    {"name": "tldr_ai_rss", "type": "rss", "url": "https://tldr.tech/rss/ai", "enabled": True, "value": "TLDR AI"},
    # --- AI × 设计 ---
    {"name": "runway_blog", "type": "rss", "url": "https://runwayml.com/blog/feed/", "enabled": True, "value": "Runway ML Blog"},
    {"name": "midjourney_blog", "type": "rss", "url": "https://midjourney.com/blog/feed/", "enabled": True, "value": "Midjourney Blog"},
    {"name": "stability_blog", "type": "rss", "url": "https://stability.ai/blog/feed", "enabled": True, "value": "Stability AI Blog"},
    {"name": "adobe_firefly_blog", "type": "rss", "url": "https://blog.adobe.com/en/topics/firefly", "enabled": False, "value": "Adobe Firefly（多为 HTML 专题页，需验证是否可解析为 RSS）"},
    {"name": "ai_art_weekly", "type": "rss", "url": "https://aiartweekly.substack.com/feed", "enabled": True, "value": "AI Art Weekly"},
    {"name": "prompting_guide", "type": "rss", "url": "https://www.promptingguide.ai/rss", "enabled": True, "value": "Prompt Engineering Guide"},
    {"name": "figma_blog_tag_ai", "type": "rss", "url": "https://www.figma.com/blog/tag/ai/", "enabled": False, "value": "Figma AI 标签页（建议优先用全站 /blog/feed/）"},
    {"name": "canva_learn", "type": "rss", "url": "https://www.canva.com/learn/feed/", "enabled": True, "value": "Canva Design School"},
    {"name": "creative_bloq_ai", "type": "rss", "url": "https://www.creativebloq.com/tag/ai/feed", "enabled": True, "value": "Creative Bloq AI"},
    {"name": "lexica_feed", "type": "rss", "url": "https://lexica.art/feed", "enabled": True, "value": "Lexica Art"},
    {"name": "civitai_rss", "type": "rss", "url": "https://civitai.com/api/v1/rss", "enabled": True, "value": "Civitai"},
    {"name": "playground_ai_blog", "type": "rss", "url": "https://playgroundai.com/blog/feed", "enabled": True, "value": "Playground AI Blog"},
    # --- AI 工具 / 媒体 ---
    {"name": "producthunt_ai_topic", "type": "rss", "url": "https://www.producthunt.com/rss/topics/artificial-intelligence", "enabled": True, "value": "Product Hunt · AI 主题"},
    {"name": "theresanaiforthat", "type": "rss", "url": "https://theresanaiforthat.com/rss/", "enabled": True, "value": "There's An AI For That"},
    {"name": "futuretools_rss", "type": "rss", "url": "https://www.futuretools.io/rss/", "enabled": True, "value": "FutureTools RSS"},
    {"name": "aitoolreport", "type": "rss", "url": "https://aitoolreport.com/feed/", "enabled": True, "value": "AI Tool Report"},
    {"name": "superpower_ai", "type": "rss", "url": "https://superpower.ai/rss", "enabled": True, "value": "Superpower AI"},
    {"name": "gartner_ai", "type": "rss", "url": "https://www.gartner.com/en/topics/artificial-intelligence/rss", "enabled": True, "value": "Gartner AI"},
    {"name": "verge_ai_alt_path", "type": "rss", "url": "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml", "enabled": True, "value": "The Verge AI（备用路径）"},
    {"name": "langchain_blog", "type": "rss", "url": "https://blog.langchain.dev/rss/", "enabled": True, "value": "LangChain Blog"},
    {"name": "llamaindex_blog", "type": "rss", "url": "https://www.llamaindex.ai/blog/rss.xml", "enabled": True, "value": "LlamaIndex Blog"},
    {"name": "wandb_blog", "type": "rss", "url": "https://wandb.ai/site/blog/rss.xml", "enabled": True, "value": "Weights & Biases"},
    {"name": "fullstack_dl", "type": "rss", "url": "https://fullstackdeeplearning.com/rss/", "enabled": True, "value": "Full Stack Deep Learning"},
    # --- 播客（RSS 含音频 enclosure）---
    {"name": "lex_fridman_podcast", "type": "rss", "url": "https://lexfridman.com/feed/podcast/", "enabled": True, "value": "Lex Fridman Podcast"},
    {"name": "twiml_podcast", "type": "rss", "url": "https://twimlai.com/shows/feed/", "enabled": True, "value": "TWIML AI Podcast"},
    {"name": "practical_ai_podcast", "type": "rss", "url": "https://changelog.com/practicalai/feed", "enabled": True, "value": "Practical AI Podcast"},
]
