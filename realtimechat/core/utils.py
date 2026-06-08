import re


def slugify_unique(name, model_class, slug_field="slug"):
    from django.utils.text import slugify
    base_slug = slugify(name)
    slug = base_slug
    counter = 1

    while model_class._default_manager.filter(**{slug_field: slug}).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug


def is_safe_url(url, allowed_host):
    if not url:
        return False
    return url.startswith("/") and not url.startswith("//")


def truncate(text, max_length=80, suffix="…"):
    if len(text) <= max_length:
        return text
    return text[:max_length].rstrip() + suffix