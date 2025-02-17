try:
    from importlib.metadata import PackageNotFoundError, version
except (ImportError, ModuleNotFoundError):  # pragma:nocover
    from importlib_metadata import (  # type: ignore[assignment,no-redef,unused-ignore]
        PackageNotFoundError,
        version,
    )

try:
    __version__ = version("rapporto")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
