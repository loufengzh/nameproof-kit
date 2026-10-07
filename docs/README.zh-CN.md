# Nameproof Kit

从简短产品想法得到品牌候选名，再生成保留来源和未知项的初步核查报告。Python 3.10+，无运行时依赖。主文档和完整字段说明见 [English README](../README.md)。

## 让 AI 智能体安装

在项目中打开你的编程智能体，粘贴下面这段：

```text
请在当前项目中安装 https://github.com/loufengzh/nameproof-kit 。
先阅读 README 和 docs/INSTALL.md，为我正在使用的智能体安装 nameproof
技能并保留 Python CLI 仓库。只使用项目内文件，覆盖已有文件前先询问。
运行离线冒烟测试，报告安装路径和结果。不要配置 API 密钥、MCP、
Logo 服务或付费服务。
```

支持 Claude Code、Codex、Cursor、Antigravity 和 Grok Build（普通 Grok 聊天不等于本地工具）。需要 Git、Python 3.10+ 和终端/文件访问权限。见[各智能体的准确命令与无需 Node 的方案](INSTALL.md)。无需 pip 安装；技能和 CLI 仓库都要保留。已验证安装路径和离线 CLI，未认证所有应用内的自动发现。

## 开始使用

在仓库根目录运行：

```sh
python -m nameproof propose --brief examples/brief.json
python -m nameproof report --brief examples/brief.json --candidates examples/candidates.json --format markdown
python -m nameproof domain example.com --live
python -m nameproof screen --name QuillNest --countries US,EU,VN --classes 9,42
python -m nameproof logo-brief --name QuillNest --brief examples/brief.json
python -m unittest discover -s tests -v
```

可选本地安装：`python -m pip install .`。未声称已发布到 PyPI。默认离线；`--live` 会向公开 IANA/RDAP 服务发送查询域名，不购买域名或注册商标。

## 能力和边界

- 本地候选生成是基于英文关键词和隐喻的基线。通过宿主智能体生成更有创意的多语言候选，再用 `--candidates` 输入含 `name`、`rationale` 的数组。拼写分数不代表语义适配、市场成功或法律安全。
- 简报使用 `idea`、`audience`、`tone`、`keywords`、`countries`、`nice_classes`、`tlds`、`max_length`、`avoid`。默认国家与类别只是明确列出的假设。长度上限是硬过滤；`avoid` 排除规范化后的子字符串。
- RDAP 只区分已有注册记录、无记录和未知。无记录不等于可购买。保留时间、来源、失败和限流信息。可导入注册商收据，但会标记为用户提供、未独立验证；15 分钟前或超过未来 30 秒的收据不更新购买状态。矛盾证据显示冲突。
- 商标核查仅比较实际导入的记录，提供美国、欧盟、英国、越南、中国、德国、俄罗斯、新加坡的官方人工检索入口。公司登记、网络使用和商标权是不同问题。没有记录意味着未核查；子集没有命中不代表无冲突。
- 支持 Unicode 文本近似匹配，但不能替代发音、语义、图形、音译和普通法权利调查。不同尼斯类别、无效或失效状态也不会自动排除风险。欧盟与德国记录会交叉提示，其他欧盟成员国仍有覆盖缺口。
- IDN 使用保守的 Python 内置 IDNA 支持；若编码会改变原始拼写则拒绝，必要时核实明确的 ASCII/punycode 域名。并非完整 IDNA2008 实现。
- Logo 输出只是简报，不是已生成作品。用户指定的 op7418/logo-generator-skill 以固定版本链接，不打包、不自动执行、不读取密钥。远程上传、收费和调用次数须单独确认，见 [LOGO.md](LOGO.md)。

## 智能体接入

复制完整的 `skills/nameproof` 目录到项目技能目录，并保留 CLI 仓库。Claude Code、Codex、Cursor、Antigravity 和 Grok Build 的官方格式与路径见 [HARNESSES.md](HARNESSES.md)。这些是文档格式兼容性，不是每个产品的端到端认证；Grok 聊天不等于本地 CLI。

`python -m nameproof mcp` 提供 stdio JSON-RPC 的四个只读工具，不开启 HTTP 端口：候选名、域名、商标记录筛查、Logo 简报。实时查询必须显式开启。

导入商标记录必须包含 `mark,jurisdiction,classes,source_url,observed_at,record_id,status`；URL 不构成真实性认证。WIPO 禁止自动查询，工具不会抓取。详见 [来源和替代工具](SOURCES.md)。正式采用名称前，应进行相关司法辖区的专业审查，并由注册商确认域名。

MIT 许可只覆盖本仓库原创代码。CI 检查 Python 3.10–3.13；网络测试使用模拟响应，实际线上核查结果应单独注明。

## 获取指定 Logo 指令

运行 `python -m nameproof logo-source --output /path/to/new-directory --fetch` 可下载固定版本的三个纯文本文件并校验 SHA-256。目录必须新建；不覆盖文件、不安装技能、不下载或执行脚本。读取 `UPSTREAM_SKILL.md` 和设计参考，由宿主创建原创 SVG 概念；收费展示图仍需另行授权。省略 `--fetch` 只输出清单。见 [完整示例](WALKTHROUGH.md)。
