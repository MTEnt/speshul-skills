"""Page registry built on slug helpers."""

from slugs import mk_slug, mk_slugs


def page_path(title: str) -> str:
    return "/" + mk_slug(title)


def page_paths(titles: list[str]) -> list[str]:
    return ["/" + slug for slug in mk_slugs(titles)]
