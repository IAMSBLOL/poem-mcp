"""FastMCP server for the Souyun open poem APIs."""

import json
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from fastmcp import FastMCP

API_BASE = "https://api.sou-yun.cn/open"
REQUEST_TIMEOUT_SECONDS = 25

mcp = FastMCP("搜韵诗词")


def _get(path: str, params: dict[str, Any]) -> Any:
    query = urlencode(
        {key: value for key, value in params.items() if value is not None}
    )
    request = Request(
        f"{API_BASE}{path}?{query}",
        headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"},
    )
    with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        return json.loads(response.read().decode("utf-8"))


def _text(node: Any) -> str:
    if isinstance(node, dict):
        return node.get("Content") or node.get("content") or ""
    if isinstance(node, str):
        return node
    return ""


def _search_poems(
    keyword: str,
    scope: str | int = "All",
    dynasty: str | None = None,
    type_: str | None = None,
    rhyme: str | None = None,
    pageno: int = 0,
    jsontype: bool = True,
) -> Any:
    params: dict[str, Any] = {
        "key": keyword,
        "scope": scope,
        "jsontype": str(jsontype).lower(),
        "pageno": pageno,
    }
    if dynasty:
        params["dynasty"] = dynasty
    if type_:
        params["type"] = type_
    if rhyme:
        params["rhyme"] = rhyme
    return _get("/poem", params)


def _rhyme_dictionary(char: str, qtype: int = 0, page_no: int = 0) -> Any:
    return _get("/rhymeDictionary", {"id": char, "qtype": qtype, "pageNo": page_no})


def _couplet_words(word: str) -> Any:
    return _get("/coupletwords", {"id": word})


def _rhyme_category(rhyme: str | None = None) -> Any:
    if rhyme:
        return _get("/RhymeCategory", {"id": rhyme})
    return _get("/RhymeCategory", {"list": ""})


def _collect_lyrics_material(
    theme: str,
    top_n: int = 8,
    rhyme_char: str | None = None,
    dynasty: str | None = None,
    type_: str | None = None,
) -> dict[str, Any]:
    poems = _search_poems(theme, scope="All", dynasty=dynasty, type_=type_, pageno=0)
    poem_rows = (poems.get("ShiData") or [])[:top_n]

    candidate_poems = []
    candidate_lines = []
    rhyme_count: dict[str, int] = {}
    for poem in poem_rows:
        candidate_poems.append(
            {
                "id": poem.get("Id"),
                "title": _text(poem.get("Title")),
                "author": poem.get("Author"),
                "dynasty": poem.get("Dynasty"),
                "type": poem.get("Type"),
                "rhyme": poem.get("Rhyme"),
            }
        )
        rhyme = poem.get("Rhyme")
        if rhyme:
            rhyme_count[rhyme] = rhyme_count.get(rhyme, 0) + 1
        for clause in poem.get("Clauses") or []:
            line = _text(clause)
            if line:
                candidate_lines.append(line)

    result: dict[str, Any] = {
        "theme": theme,
        "candidate_poems": candidate_poems,
        "candidate_lines": candidate_lines,
        "rhyme_suggestions": rhyme_count,
    }
    if rhyme_char:
        result["couplet_words"] = _couplet_words(rhyme_char)
        dictionary = _rhyme_dictionary(rhyme_char)
        result["allusions"] = (
            dictionary.get("Allusions") if isinstance(dictionary, dict) else None
        )
    return result


@mcp.tool
def search_poems(
    keyword: str,
    scope: str | int = "All",
    dynasty: str | None = None,
    type_: str | None = None,
    rhyme: str | None = None,
    pageno: int = 0,
    jsontype: bool = True,
) -> Any:
    """按关键词检索诗词；scope 可选 All、Author、Title、Sentence 或 0 到 3。"""
    return _search_poems(keyword, scope, dynasty, type_, rhyme, pageno, jsontype)


@mcp.tool
def get_poem(poem_id: str) -> Any:
    """按诗词 ID 获取单首详情。"""
    return _get("/poem", {"key": poem_id, "jsontype": "true"})


@mcp.tool
def rhyme_dictionary(char: str, qtype: int = 0, page_no: int = 0) -> Any:
    """查询韵典；qtype 为 0 查全部，1 查韵目，2 查词末典故，3/4 查词首/词末，5 查句末诗例。"""
    return _rhyme_dictionary(char, qtype, page_no)


@mcp.tool
def couplet_words(word: str) -> Any:
    """查询与输入字词对仗的词汇参考。"""
    return _couplet_words(word)


@mcp.tool
def rhyme_category(rhyme: str | None = None) -> Any:
    """查询平水韵总目，或查询指定韵部包含的字。"""
    return _rhyme_category(rhyme)


@mcp.tool
def collect_lyrics_material(
    theme: str,
    top_n: int = 8,
    rhyme_char: str | None = None,
    dynasty: str | None = None,
    type_: str | None = None,
) -> dict[str, Any]:
    """汇总主题相关诗词、诗句、韵部建议，可选附加对仗词和典故。"""
    return _collect_lyrics_material(theme, top_n, rhyme_char, dynasty, type_)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
