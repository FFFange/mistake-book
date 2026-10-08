# -*- coding: utf-8 -*-
"""
错题本（MistakeBook）—— 命令行错题管理工具

记录错题、按科目/标签检索、统计薄弱科目，数据持久化到本地 JSON。

用法示例：
    python mistake_book.py add --subject 数学 --question "二次函数求最值" \
        --wrong "配方符号错了" --correct "先提系数再配方" --tags 函数,代数
    python mistake_book.py list
    python mistake_book.py search --subject 数学
    python mistake_book.py search --tag 函数
    python mistake_book.py stats
    python mistake_book.py remove --id 3
"""

import argparse
import json
import os
import sys
from dataclasses import dataclass, field, asdict
from datetime import date

# 数据文件放在脚本同目录，换电脑也能整体搬走
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mistakes.json")


@dataclass
class Mistake:
    """一道错题的记录。

    用 dataclass 省掉手写 __init__，字段即文档。
    """
    subject: str          # 科目，如 数学 / 物理 / 英语
    question: str         # 题干摘要
    wrong: str            # 我的错误答案或错因
    correct: str          # 正解要点
    tags: list = field(default_factory=list)   # 知识点标签
    date: str = field(default_factory=lambda: date.today().isoformat())
    id: int = 0           # 由 MistakeBook 分配


class MistakeBook:
    """错题本核心类：负责增删查统计和持久化。

    设计说明：数据全部在内存中操作，每次变更后整体写回 JSON。
    对学生数据量（几千条以内）足够快，实现也简单可靠。
    """

    def __init__(self, path=DATA_FILE):
        self.path = path
        self.mistakes = []
        self.load()

    # ---------- 持久化 ----------

    def load(self):
        """从 JSON 读入全部错题；文件不存在就当空本。"""
        if not os.path.exists(self.path):
            return
        with open(self.path, "r", encoding="utf-8") as f:
            for item in json.load(f):
                self.mistakes.append(Mistake(**item))

    def save(self):
        """整体写回 JSON。ensure_ascii=False 保证中文可读。"""
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump([asdict(m) for m in self.mistakes],
                      f, ensure_ascii=False, indent=2)

    # ---------- 增删查 ----------

    def add(self, subject, question, wrong, correct, tags=None):
        """新增一道错题，返回带 id 的 Mistake 对象。"""
        next_id = max((m.id for m in self.mistakes), default=0) + 1
        m = Mistake(subject=subject, question=question, wrong=wrong,
                    correct=correct, tags=tags or [], id=next_id)
        self.mistakes.append(m)
        self.save()
        return m

    def remove(self, mid):
        """按 id 删除，返回是否删成功。"""
        before = len(self.mistakes)
        self.mistakes = [m for m in self.mistakes if m.id != mid]
        changed = len(self.mistakes) != before
        if changed:
            self.save()
        return changed

    def search(self, keyword=None, subject=None, tag=None):
        """多条件组合查询，条件之间是“与”的关系。"""
        result = self.mistakes
        if subject:
            result = [m for m in result if m.subject == subject]
        if tag:
            result = [m for m in result if tag in m.tags]
        if keyword:
            kw = keyword.lower()
            result = [m for m in result
                      if kw in m.question.lower() or kw in m.correct.lower()]
        return result

    def stats(self):
        """按科目统计错题数，返回 {科目: 数量}，降序排列——错得最多的就是最薄弱的。"""
        counter = {}
        for m in self.mistakes:
            counter[m.subject] = counter.get(m.subject, 0) + 1
        return dict(sorted(counter.items(), key=lambda kv: kv[1], reverse=True))


# ---------- 命令行界面 ----------

def print_mistakes(mistakes):
    """把错题列表打印成易读格式。"""
    if not mistakes:
        print("（没有匹配的错题）")
        return
    for m in mistakes:
        tags = " ".join("#" + t for t in m.tags)
        print("[#{}] 【{}】{}".format(m.id, m.subject, m.question))
        print("    错因: {}".format(m.wrong))
        print("    正解: {}".format(m.correct))
        if tags:
            print("    标签: {}".format(tags))
        print("    日期: {}".format(m.date))


def build_parser():
    """定义命令行参数结构（argparse 子命令模式）。"""
    parser = argparse.ArgumentParser(description="错题本：记录、查询、统计你的错题")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="添加一道错题")
    p_add.add_argument("--subject", required=True, help="科目，如 数学")
    p_add.add_argument("--question", required=True, help="题干摘要")
    p_add.add_argument("--wrong", required=True, help="错因/错误答案")
    p_add.add_argument("--correct", required=True, help="正解要点")
    p_add.add_argument("--tags", default="", help="知识点标签，逗号分隔，如 函数,代数")

    sub.add_parser("list", help="列出全部错题")

    p_search = sub.add_parser("search", help="按条件查询")
    p_search.add_argument("--keyword", help="题干/正解里的关键词")
    p_search.add_argument("--subject", help="科目")
    p_search.add_argument("--tag", help="标签")

    sub.add_parser("stats", help="按科目统计错题数")

    p_rm = sub.add_parser("remove", help="按 id 删除")
    p_rm.add_argument("--id", type=int, required=True)

    return parser


def main():
    # Windows 中文控制台默认 GBK（代码页 936），直接打印 UTF-8 中文会乱码。
    # 先把控制台切到 UTF-8 代码页，再强制 stdout 用 UTF-8 输出。
    if sys.platform == "win32":
        os.system("chcp 65001 >NUL")
        sys.stdout.reconfigure(encoding="utf-8")
    args = build_parser().parse_args()
    book = MistakeBook()

    if args.command == "add":
        tags = [t.strip() for t in args.tags.split(",") if t.strip()]
        m = book.add(args.subject, args.question, args.wrong, args.correct, tags)
        print("已添加错题 #{}（{}）".format(m.id, m.subject))
    elif args.command == "list":
        print_mistakes(book.mistakes)
    elif args.command == "search":
        print_mistakes(book.search(keyword=args.keyword,
                                   subject=args.subject, tag=args.tag))
    elif args.command == "stats":
        for subject, count in book.stats().items():
            print("{}: {} 道".format(subject, count))
        if not book.mistakes:
            print("错题本还是空的，先 add 一道吧。")
    elif args.command == "remove":
        ok = book.remove(args.id)
        print("已删除 #{}".format(args.id) if ok else "没有找到 #{}".format(args.id))


if __name__ == "__main__":
    main()
