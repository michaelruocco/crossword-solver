from urllib.parse import urlparse


class UrlConverter:
    def to_filename(self, value: str) -> str:
        path = urlparse(value).path
        return path[path.rfind("/") + 1 :]

    def to_filename_excluding_extension(self, value: str) -> str:
        filename = self.to_filename(value)
        return filename[: filename.rfind(".")]

    def to_extension(self, value: str) -> str:
        filename = self.to_filename(value)
        return filename[filename.rfind(".") :]