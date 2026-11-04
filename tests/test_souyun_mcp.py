import unittest
from unittest.mock import patch

from souyun_mcp import _collect_lyrics_material


class CollectLyricsMaterialTests(unittest.TestCase):
    @patch("souyun_mcp._search_poems", return_value=None)
    def test_none_search_response_returns_empty_material(self, _search_poems):
        result = _collect_lyrics_material("江南", top_n=20)

        self.assertEqual(
            result,
            {
                "theme": "江南",
                "candidate_poems": [],
                "candidate_lines": [],
                "rhyme_suggestions": {},
            },
        )

    @patch(
        "souyun_mcp._search_poems",
        return_value={
            "ShiData": [
                None,
                {
                    "Id": 1,
                    "Title": {"Content": "江南春"},
                    "Author": "杜牧",
                    "Dynasty": "唐",
                    "Type": "七绝",
                    "Rhyme": "下平一先",
                    "Clauses": [{"Content": "千里莺啼绿映红"}],
                },
            ]
        },
    )
    def test_null_poem_rows_are_skipped(self, _search_poems):
        result = _collect_lyrics_material("江南", top_n=20)

        self.assertEqual(len(result["candidate_poems"]), 1)
        self.assertEqual(result["candidate_poems"][0]["title"], "江南春")
        self.assertEqual(result["candidate_lines"], ["千里莺啼绿映红"])
        self.assertEqual(result["rhyme_suggestions"], {"下平一先": 1})


if __name__ == "__main__":
    unittest.main()
