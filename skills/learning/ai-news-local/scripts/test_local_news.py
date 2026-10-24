"""Offline regression checks for portable article storage; no network calls."""
from pathlib import Path
import tempfile
import unittest
import importlib.util
import article
import reading

BODY = """# 2026年10月24日 AI资讯日报
*统计时间：2026-10-24（北京时间）*

## 今日导读
- 🟠 1. 验证条目

## 🟠 行业资讯
### 1. 验证条目
仅用于验证保存，不是真实新闻。
[来源](https://example.com/)

## 🔵 实践工具
暂无条目。
## 🟣 方法启发
暂无条目。
## 🟢 跨界发现
暂无条目。
"""
QA = "\n---\n\n## 延伸问答\n\n### Q1｜测试问题\n> 中文问题\n\n保留已有回答。\n"

class LocalNewsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="local-news-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.target = self.root / "中文输出" / "2026-10-24-AI资讯日报.md"
        self.draft = self.root / "draft.md"
        self.draft.write_text(BODY, encoding="utf-8")

    def test_create_directory_without_cover(self):
        article.save(self.draft, self.target)
        self.assertEqual(self.target.read_text(encoding="utf-8"), BODY)

    def test_regenerate_preserves_qa(self):
        article.save(self.draft, self.target)
        self.target.write_text(BODY + QA, encoding="utf-8")
        self.draft.write_text(BODY.replace("仅用于", "更新正文；仅用于"), encoding="utf-8")
        article.save(self.draft, self.target)
        text = self.target.read_text(encoding="utf-8")
        self.assertIn("更新正文", text)
        self.assertIn(QA.strip(), text)
        self.assertEqual(text.count("## 延伸问答"), 1)

    def test_conflicting_qa_does_not_overwrite(self):
        article.save(self.draft, self.target)
        self.target.write_text(BODY + QA, encoding="utf-8")
        original = self.target.read_bytes()
        self.draft.write_text(BODY + QA.replace("保留已有回答", "不应覆盖旧回答"), encoding="utf-8")
        with self.assertRaises(ValueError):
            article.save(self.draft, self.target)
        self.assertEqual(self.target.read_bytes(), original)

    def test_invalid_date_and_sequence(self):
        with self.assertRaises(ValueError):
            article.check_article(BODY, self.target.with_name("2026-10-23-AI资讯日报.md"))
        with self.assertRaises(ValueError):
            article.check_article(BODY.replace("### 1.", "### 2."), self.target)

    def test_missing_image_rejected(self):
        with self.assertRaises(ValueError):
            article.check_article(BODY + "\n![封面](_assets/missing.png)\n", self.target)

    @unittest.skipUnless(importlib.util.find_spec("markdown"), "Optional Python Markdown not installed")
    def test_chinese_html_and_qa(self):
        article.save(self.draft, self.target)
        self.target.write_text(BODY + QA, encoding="utf-8")
        output = reading.render(self.target).read_text(encoding="utf-8")
        self.assertIn("<h1>", output)
        self.assertIn("中文问题", output)
        self.assertIn("保留已有回答", output)
        self.assertIn('<section class="qa">', output)

if __name__ == "__main__":
    unittest.main(verbosity=2)
