MARKETPLACE_CATEGORIES = {
    "yahoo": {
        "all": {
            "label": "All categories",
            "category_id": None,
        },
        "camera_sample": {
            "label": "Camera sample",
            "category_id": None,
        },
    },
    "mercari": {
        "all": {
            "label": "All categories",
            "category_id": None,
        },
        "camera_sample": {
            "label": "Camera sample",
            "category_id": None,
        },
    },
}


def available_category_keys(source):
    categories = MARKETPLACE_CATEGORIES.get(source, {})

    return sorted(categories.keys())


def resolve_category_id(source, category_key=None, category_id=None):
    if category_id is not None:
        return category_id

    if category_key is None:
        return None

    categories = MARKETPLACE_CATEGORIES.get(source)

    if categories is None:
        raise ValueError(f"unknown marketplace for category: {source}")

    category = categories.get(category_key)

    if category is None:
        available_keys = ", ".join(available_category_keys(source))
        raise ValueError(
            f"unknown category key for {source}: {category_key}. "
            f"Available keys: {available_keys}"
        )

    return category["category_id"]
