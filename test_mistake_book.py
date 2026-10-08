# -*- coding: utf-8 -*-
"""MistakeBook 的单元测试。

运行方式（不需要安装任何第三方库）：
    python -m unittest test_mistake_book.py -v

测试用临时文件做数据落盘，不会污染你真正的 mistakes.json。
"""

import os
import tempfile
import unittest

from mistake_book import MistakeBook


class MistakeBookTest(unittest.TestCase):
    """每个测试方法都跑在独立、干净的临时错题本上。"""

    def setUp(self):
        # 在系统临时目录建一个独立的数据文件，测试互不干扰
        self.tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8")
        self.tmp.close()
        os.remove(self.tmp.name)          # 删掉空文件，让 load 走“不存在”分支
        self.book = MistakeBook(path=self.tmp.name)

    def tearDown(self):
        if os.path.exists(self.tmp.name):
            os.remove(self.tmp.name)

    def test_add_assigns_increasing_ids(self):
        m1 = self.book.add("数学", "题1", "错因1", "正解1")
        m2 = self.book.add("英语", "题2", "错因2", "正解2")
        self.assertEqual(m1.id, 1)
        self.assertEqual(m2.id, 2)
        self.assertEqual(len(self.book.mistakes), 2)

    def test_data_survives_reload(self):
        """写入后重新打开文件，数据应该原样读回来（持久化正确）。"""
        self.book.add("物理", "浮力计算", "公式记错", "F=ρgV", tags=["力学"])
        reopened = MistakeBook(path=self.tmp.name)
        self.assertEqual(len(reopened.mistakes), 1)
        self.assertEqual(reopened.mistakes[0].subject, "物理")
        self.assertIn("力学", reopened.mistakes[0].tags)

    def test_remove(self):
        m = self.book.add("化学", "配平", "系数错", "先定氧")
        self.assertTrue(self.book.remove(m.id))
        self.assertEqual(len(self.book.mistakes), 0)
        self.assertFalse(self.book.remove(999))   # 删不存在的 id 返回 False

    def test_search_by_subject_and_tag(self):
        self.book.add("数学", "二次函数", "配方错", "提系数", tags=["函数"])
        self.book.add("数学", "立体几何", "辅助线错", "找中点", tags=["几何"])
        self.book.add("英语", "时态填空", "时态混", "看时间状语", tags=["语法"])

        self.assertEqual(len(self.book.search(subject="数学")), 2)
        self.assertEqual(len(self.book.search(tag="函数")), 1)
        self.assertEqual(len(self.book.search(subject="数学", tag="几何")), 1)

    def test_search_by_keyword_is_case_insensitive(self):
        self.book.add("英语", "virtual 的用法", "词性记错", "adj. 虚拟的")
        self.assertEqual(len(self.book.search(keyword="VIRTUAL")), 1)

    def test_stats_sorted_descending(self):
        self.book.add("数学", "题a", "错", "对")
        self.book.add("数学", "题b", "错", "对")
        self.book.add("英语", "题c", "错", "对")
        result = self.book.stats()
        self.assertEqual(result, {"数学": 2, "英语": 1})
        # 第一名必须是错题最多的科目
        self.assertEqual(list(result.keys())[0], "数学")


if __name__ == "__main__":
    unittest.main()
