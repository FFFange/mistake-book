# MistakeBook 错题本

一个命令行错题管理工具：记录错题、按科目/标签/关键词检索、统计薄弱环节，数据保存在本地 JSON。

> 源于真实需求：错题记在纸上容易丢、难检索，于是给自己写了个工具。

## 功能

- **记录错题**：科目、题干、错因、正解、知识点标签、日期
- **组合检索**：按科目 / 标签 / 关键词任意组合查询
- **薄弱统计**：按科目统计错题数，错得最多的一眼可见
- **数据持久化**：全部数据存在本地 JSON，无需数据库，换电脑整体搬走
- **单元测试覆盖**：核心逻辑 6 个测试用例全绿

## 快速开始

零依赖，只需要 Python 3.8+：

```bash
# 添加一道错题
python mistake_book.py add --subject 数学 --question "二次函数求最值" \
    --wrong "配方符号错了" --correct "先提系数再配方" --tags 函数,代数

# 查看全部
python mistake_book.py list

# 组合查询
python mistake_book.py search --subject 数学 --tag 函数

# 薄弱科目统计
python mistake_book.py stats

# 删除
python mistake_book.py remove --id 3
```

## 运行测试

```bash
python -m unittest test_mistake_book.py -v
```

## 项目结构

```
mistake-book/
├── mistake_book.py        # 主程序：数据模型 + 业务逻辑 + CLI
├── test_mistake_book.py   # 单元测试（标准库 unittest，零依赖）
└── README.md
```

## 技术要点

- **OOP 设计**：`Mistake`（dataclass 数据模型）与 `MistakeBook`（业务逻辑）分离
- **持久化**：JSON 文件读写，`ensure_ascii=False` 处理中文
- **CLI**：`argparse` 子命令模式（add / list / search / stats / remove）
- **测试**：`unittest` + `tempfile` 隔离测试数据，不污染真实数据文件
- **健壮性**：删除不存在的 id、空库统计等边界情况均有处理

## 路线图

- [ ] 复习提醒（基于艾宾浩斯遗忘曲线）
- [ ] 导出为 Anki 牌组 / Markdown
- [ ] Web 界面（Flask）
