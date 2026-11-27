"""RED/GREEN：data/topics_index.json 預設不註冊，明確指出才註冊。

2026-11-26：D2 規則已搬移至 quantum-website；本檔改讀新技能，
同時鎖住本輪範圍：toolkit-viz 的 app.py 規則與實體檔都不得被移除。
"""

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
TV_SKILL = ROOT / "SKILL.md"
NEW_SKILL = Path("/home/sam/.opencode/skills/quantum-website/SKILL.md")


class TopicIndexDefaultNoRegister(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = NEW_SKILL.read_text(encoding="utf-8")
        cls.tv_text = TV_SKILL.read_text(encoding="utf-8")
        cls.d2 = cls.text.split("## D2. 同源同步閘門", 1)[1].split("## D3. Git", 1)[0]

    def test_old_mandatory_registration_rule_is_gone(self):
        # 只檢查現行規則段落；Logic check 歷史行保留原文，不改寫歷史。
        self.assertNotIn("`topics_index.json` 必須包含所有蒸餾主題", self.d2)

    def test_default_no_register_is_declared(self):
        self.assertIn("預設不註冊", self.text)

    def test_explicit_request_enables_registration(self):
        self.assertIn("明確指出", self.text)
        self.assertIn("data/topics_index.json", self.text)

    def test_independent_demo_reads_source_directly(self):
        self.assertIn("直接讀蒸餾來源目錄", self.text)

    def test_app_py_rule_and_file_are_untouched(self):
        self.assertIn("app.py", self.tv_text)
        self.assertTrue((ROOT / "app.py").is_file())


if __name__ == "__main__":
    unittest.main(verbosity=2)
