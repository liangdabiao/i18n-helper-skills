# 术语表（Glossary）

翻译前**必读**。以下术语在译文中必须统一，避免同词异译造成混乱。
分两类：**A 类 = 不翻译**（保持原文）、**B 类 = 锁定译法**（按表统一）。

> 本表基于 PostHog 用户行为分析手册提炼；翻译其他站点时可按需增补。
> 原则：技术产品名、协议、代码标识符一律不译；业务概念词锁定一种译法。

---

## A 类：保持原文，绝不翻译

| 术语 | 说明 |
|------|------|
| PostHog | 产品名，大小写严格（**不写** Posthog / posthog） |
| GA4 / Google Analytics | 产品名 |
| Mixpanel | 产品名 |
| 神策 / Sensors Data | 中文语境公司名，英文版用 Sensors Data |
| RFM | 模型缩写 |
| LTV | 生命周期价值缩写 |
| Docker | 技术名 |
| SQL / HogQL | SQL 保留；HogQL 是 PostHog 方言，保留 |
| API / SDK / HTTP / CDP / Webhook | 协议/技术缩写 |
| Autocapture | PostHog 功能名 |
| Markdown / JSON / YAML | 格式名 |
| §01 §02 ... / Part 1 ... Part 5 | 章节锚点编号，保留 |
| GA / GA4（文中简称） | 保留 |

> 章节锚点 `§编号`、`Part N` 必须保留：它们是跨页面导航与目录的标识符。

---

## B 类：锁定译法（按目标语言查表）

### 业务概念词

| 中文 (zh-CN) | 英文 (en-US) | 繁中 (zh-TW) | 日文 (ja-JP) |
|------|------|------|------|
| 埋点 | event tracking / tracking | 埋點 | （イベント）トラッキング実装 |
| 埋点体系 | tracking schema | 埋點體系 | トラッキング設計 |
| 用户画像 | user profile | 使用者畫像 | ユーザーペルソナ |
| 画像 | profile | 畫像 | ペルソナ |
| 留存 | retention | 留存 | リテンション |
| 留存率 | retention rate | 留存率 | リテンション率 |
| 转化 | conversion | 轉換 | コンバージョン |
| 转化率 | conversion rate | 轉換率 | コンバージョン率 |
| 漏斗 | funnel | 漏斗 | ファネル |
| 同期群 | cohort | 同期群 | コホート |
| 归因 | attribution | 歸因 | アトリビューション |
| 归类 | clustering / classification | 分類 | クラスタリング |
| 分群 | segmentation | 分群 | セグメンテーション |
| 活跃（用户） | active (user) | 活躍 | アクティブ（ユーザー） |
| 日活 / 月活 / 周活 | DAU / MAU / WAU | 日活 / 月活 / 週活 | DAU / MAU / WAU |
| 渠道 | channel | 渠道 | チャネル |
| 指标 | metric | 指標 | 指標 / メトリック |
| 指标体系 | metric system | 指標體系 | 指標体系 |
| 数据仓库 | data warehouse | 資料倉儲 | データウェアハウス |
| 独立站 | independent site / DTC store | 獨立站 | 独立サイト |
| 可视化 | visualization | 視覺化 | 可視化 |
| 标签 | tag / label | 標籤 | タグ |
| 事件 | event | 事件 | イベント |
| 行为 | behavior / behavioural | 行為 | 行動 |
| 行为分析 | behavioral analytics | 行為分析 | 行動分析 |
| 生命周期价值 | lifetime value | 生命週期價值 | ライフタイムバリュー |
| 复购率 | repurchase rate | 回購率 | リピート率 |
| 跳出率 | bounce rate | 跳出率 | 直帰率 |
| 热力图 | heatmap | 熱力圖 | ヒートマップ |
| 录屏 | session recording | 螢幕錄製 | セッション録画 |
| 私有化部署 | self-hosted deployment | 私有化部署 | セルフホスト（ deployment） |
| 大模型 | large language model (LLM) | 大模型 | 大規模言語モデル (LLM) |
| 回归模型 | regression model | 回歸模型 | 回帰モデル |
| 价值打分 | value scoring | 價值評分 | 価値スコアリング |
| 采集 | collection / capture | 採集 | 収集 / キャプチャ |
| 触发 | trigger | 觸發 | トリガー |
| 自动化 | automation | 自動化 | 自動化 |

### 导航词（common key，全站统一）

| 中文 (zh-CN) | 英文 (en-US) | 繁中 (zh-TW) | 日文 (ja-JP) |
|------|------|------|------|
| 目录 | Contents | 目錄 | 目次 |
| 上一章 | Previous | 上一章 | 前の章 |
| 下一章 | Next | 下一章 | 次の章 |
| 返回目录 | Back to Contents | 返回目錄 | 目次に戻る |
| 阅读指南 | Reading Guide | 閱讀指南 | 読み方ガイド |
| 附录 | Appendix | 附錄 | 付録 |

> 箭头 `←` `→` 与符号 `§` `※` `·` 一律保留，不翻译。

---

## 使用方法

1. 翻译每批前，先对照本表把涉及的术语圈出
2. 填译文时逐个套用对应语言的锁定译法
3. 同一批内若出现同词多次，必须用同一个译法
4. 若发现高频新术语未列入本表，**先补表再继续翻译**（避免风格漂移）

## 容易翻错的点

- 「埋点」英文用 **event tracking**（而非埋点直译 instrumentation，后者偏技术实现）
- 「独立站」英文用 **DTC store / independent site**，不要译成 standalone station
- 「日活/月活」英文直接用缩写 **DAU/MAU**，业内通用
- 大小写：**PostHog** 首字母大写 H（产品官方写法）；**GA4** 不写 ga4
