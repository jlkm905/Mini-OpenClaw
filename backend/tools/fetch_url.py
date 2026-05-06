import html2text
import httpx
from langchain.tools import BaseTool


class FetchURLTool(BaseTool):
    name: str = "fetch_url"
    description: str = (
        "Fetch a URL and return its content as clean Markdown text. "
        "Input: a valid URL string."
    )

    def _run(self, url: str) -> str:
        response = httpx.get(url, follow_redirects=True, timeout=15)
        response.raise_for_status()
        return _to_markdown(response.text)

    async def _arun(self, url: str) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, follow_redirects=True, timeout=15)
            response.raise_for_status()
        return _to_markdown(response.text)


def _to_markdown(html: str) -> str:
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = True
    h.body_width = 0
    return h.handle(html)
