from urllib.parse import urljoin


class BaseClient:
    def __init__(
        self,
        base_url: str,
        api_key: str,
    ) -> None:
        self.base_url = base_url
        self.headers = {
            "x-api-key": api_key,
        }

    def _build_url(
        self,
        path: str,
    ) -> str:
        return urljoin(self.base_url, path.lstrip("/"))
