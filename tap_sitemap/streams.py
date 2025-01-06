"""Stream type classes for tap-sitemap."""

from __future__ import annotations

import typing as t
from importlib import resources

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_sitemap.client import SitemapExtractorStream
import requests
from xml.etree import ElementTree

if t.TYPE_CHECKING:
    import requests
    from singer_sdk.helpers.types import Context
    from typing import Dict, Optional

class SitemapIndexStream(SitemapExtractorStream):
    name = "sitemaps"
    
    @property
    def path(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        return self.config['sitemap_index']
    primary_keys: t.ClassVar[list[str]] = ["sitemap_url"]
    replication_key = None
    schema = th.PropertiesList(
        th.Property("sitemap_url", th.StringType)
    ).to_dict()
    
    
    def request_records(self, context: Context | None) -> t.Iterable[dict]:
        res = requests.get(self.url_base + self.path)
        root = ElementTree.fromstring(res.content)
        
        for url in root.findall('{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap'):
            loc = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text
            yield {'sitemap_url': loc}
            
    def get_child_context(self, record: Dict, context: Optional[Dict]) -> dict:
        return {
            "sitemap_url": record["sitemap_url"],
        }
        
class SitemapFromIndexStream(SitemapExtractorStream):
    name = "sitemap_urls"
    
    parent_stream_type = SitemapIndexStream
    primary_keys: t.ClassVar[list[str]] = ["sitemap_url", "page_url"]
    schema = th.PropertiesList(
        th.Property("sitemap_url", th.StringType),
        th.Property("page_url", th.StringType),
        th.Property("last_mod", th.DateTimeType),
    ).to_dict()
    
    def request_records(self, context: Context | None) -> t.Iterable[dict]:
        headers = self.http_headers
        res = requests.get(context['sitemap_url'], headers=headers)
        root = ElementTree.fromstring(res.content)
        
        for url in root.findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
            loc = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text
            last_mod_elem = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod')
            last_mod = None
            if last_mod_elem:
                last_mod = last_mod_elem.text
            yield {'sitemap_url': context['sitemap_url'], 'page_url': loc, 'last_mod': last_mod}