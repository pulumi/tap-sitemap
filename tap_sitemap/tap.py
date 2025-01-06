"""Sitemap tap class."""

from __future__ import annotations

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

# TODO: Import your custom stream types here:
from tap_sitemap import streams


class TapSitemap(Tap):
    """Sitemap tap class."""

    name = "tap-sitemap"

    # TODO: Update this section with the actual config values you expect:
    config_jsonschema = th.PropertiesList(
        
        th.Property(
            "url_base",
            th.StringType,
            title="Base URL",
            default="https://www.example.com",
            description="Base URL where the Sitemap is located",
        ),
        th.Property(
            "sitemap_index",
            th.StringType,
            title="Sitemap Index",
            default="/sitemap-index.xml",
            description="The url for the Sitemap index",
        ),
        th.Property(
            "user_agent",
            th.StringType,
            description=(
                "A custom User-Agent header to send with each request. Default is "
                "'<tap_name>/<tap_version>'"
            ),
        ),
    ).to_dict()

    def discover_streams(self) -> list[streams.SitemapStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        return [
            streams.SitemapIndexStream(self),
            streams.SitemapFromIndexStream(self),
        ]


if __name__ == "__main__":
    TapSitemap.cli()
