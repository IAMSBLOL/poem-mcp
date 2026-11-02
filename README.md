# 搜韵诗词 MCP

基于搜韵网开放接口的 FastMCP 服务，通过 stdio 向 MCP 客户端提供诗词检索、韵典查询和歌词素材汇总工具。

## 环境准备

- Python 3.13 或更高版本
- [uv](https://docs.astral.sh/uv/)
- 运行时可访问 `api.sou-yun.cn`

在项目目录安装依赖：

```powershell
uv sync
```

## 启动

MCP 服务使用 stdio，由 MCP 客户端按需启动并管理进程：

```powershell
uv run python .\souyun_mcp.py
```

也可以直接使用项目虚拟环境：

```powershell
.\.venv\Scripts\python.exe .\souyun_mcp.py
```

## MCP 客户端配置

在客户端的 MCP 配置中添加一个 stdio server。将示例中的目录替换为本机项目的绝对路径：

```json
{
  "mcpServers": {
    "souyun-poem": {
      "command": "D:\\path\\to\\1102-mcp\\.venv\\Scripts\\python.exe",
      "args": [
        "D:\\path\\to\\1102-mcp\\souyun_mcp.py"
      ]
    }
  }
}
```

## 可用工具

- `search_poems`: 按关键词检索诗词。`scope` 支持 `All`、`Author`、`Title`、`Sentence` 或数字 `0` 到 `3`；也可按 `dynasty`、`type_`、`rhyme` 和 `pageno` 筛选，`jsontype` 控制 JSON 返回格式。
- `get_poem`: 按 `poem_id` 查询单首诗词详情。
- `rhyme_dictionary`: 按 `char` 查询韵典；`qtype` 为 `0` 查全部、`1` 查韵目、`2` 查词末典故、`3` 查词首、`4` 查词末、`5` 查句末诗例。可通过 `page_no` 翻页。
- `couplet_words`: 查询与 `word` 对仗的词汇。
- `rhyme_category`: 不传 `rhyme` 时查询平水韵总目；传入韵部时查询该韵包含的字。
- `collect_lyrics_material`: 按 `theme` 汇总候选诗词、诗句和韵部建议。可设置 `top_n`、`dynasty`、`type_`；传入 `rhyme_char` 时还会返回相关对仗词和典故。
