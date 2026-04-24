# 输入形态示例（虚构）

**完整输入/输出对照**见 [good-output.md](good-output.md) 第一节（推荐直接读该文件）。

以下为同款 JSON，便于单独跳转：

```json
{
  "title": "示例：PixelMeld 发布 2.0（AI 布局助手）",
  "url": "https://example.com/product",
  "category": "new_tool",
  "key_facts": [
    "2.0 支持 Figma 内一键生成多屏线框，自称较 1.0 延迟降低约 40%",
    "定价：Pro 12 USD/月，团队席按席位另计",
    "官方文档写明输出为建议稿，需人工确认后交付客户"
  ],
  "entities": ["PixelMeld", "Figma"],
  "notes": "社区有帖讨论「是否替代初级 UI」，未见第三方基准测试"
}
```

写稿时：**key_facts** 可直引或改写；**notes** 中未证实说法须在对话里标明不确定，不可写成定论。
