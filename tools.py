"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import config  # noqa: F401 — you'll use this in search_listings
import json
import re
from generate import generate
from utils.data_loader import load_listings


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    This is the tool that doesn't call the model, which makes it the easiest one
    to test and the one to move onto MCP in unit 4.

    Args:
        description: keywords describing what the user wants
                     (e.g. "vintage graphic tee").
        size:        a size string to filter by, or None to skip size filtering.
                     Match case-insensitively — "M" should match "S/M".

                     ⚠️ Read the sizes in the data before you reach for a plain
                     substring test. `"s" in "us 9"` is True, and so is
                     `"l" in "xl"`. A filter that returns shoes when someone
                     asked for a small top reads like a broken search, and it
                     will quietly cost you in unit 4 when you test criterion 1.
                     What counts as a size match is part of your spec — decide
                     it and write it into your Tool Inventory.
        max_price:   maximum price, inclusive, or None to skip price filtering.

    Returns:
        A list of matching listing dicts, best match first.
        **Returns an empty list when nothing matches — an empty list, not None,
        and not an exception.** Your loop branches on this.

    Each listing dict has these fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand (str or None), platform

    Note that `brand` is None for most listings. That is deliberate and
    realistic — thrift listings often have no brand. If something you write
    assumes a brand is always there, you will find out in unit 4.

    TODO:
        1. Load every listing with load_listings().
        2. Filter by max_price and by size, when each is provided.
        3. Score what's left by keyword overlap with `description`.
        4. Drop anything scoring zero.
        5. Sort by score, highest first, and return the listing dicts —
           at most config.SEARCH_RESULT_LIMIT of them.

    Test it from a terminal before you move on:
        python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
    """
    def words(text: str) -> set[str]:
        return set(re.findall(r"\w+", text.casefold()))

    query_words = words(description)
    if not query_words:
        return []

    requested_size = " ".join(size.casefold().split()) if size is not None else None
    ranked: list[tuple[int, dict]] = []

    for listing in load_listings():
        if max_price is not None and listing["price"] > max_price:
            continue

        if requested_size is not None:
            listing_size = " ".join(listing["size"].casefold().split())
            base_size = re.sub(r"\s*\([^)]*\)", "", listing_size).strip()
            size_labels = {listing_size, base_size}
            size_labels.update(part.strip() for part in listing_size.split("/"))
            size_labels.update(part.strip() for part in base_size.split("/"))
            if requested_size not in size_labels:
                continue

        searchable_text = " ".join(
            [listing["title"], listing["description"], *listing["style_tags"]]
        )
        score = len(query_words & words(searchable_text))
        if score:
            ranked.append((score, listing))

    ranked.sort(key=lambda result: -result[0])
    return [listing for _, listing in ranked[:config.SEARCH_RESULT_LIMIT]]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.

    This one calls the model, through `generate()`. You don't need to think
    about rate limits — the adapter handles pacing for you.

    Args:
        new_item: a listing dict — the item the user is considering.
        wardrobe: a wardrobe dict with an 'items' key holding a list of items.
                  **It may be empty.** Handle that.

    Returns:
        A non-empty string with outfit suggestions.
        With an empty wardrobe, return general styling advice rather than
        raising or returning "". Unit 4 has you trigger the empty wardrobe on
        purpose, so decide now what it should do.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If it is, ask the model for general styling ideas for this item.
        3. If it isn't, format the wardrobe items into the prompt and ask for
           specific combinations naming pieces the user already owns.
        4. Return the model's response.

    Test it from a terminal before you move on:
        python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
    """
    wardrobe_items = wardrobe.get("items") or []
    item_details = json.dumps(new_item, ensure_ascii=False, indent=2)

    if wardrobe_items:
        system = (
            "Suggest one or two wearable outfits featuring the new item. "
            "Use and name pieces from the supplied wardrobe, and do not claim "
            "the user owns anything that is not listed. Keep the advice concise."
        )
        wardrobe_details = json.dumps(wardrobe_items, ensure_ascii=False, indent=2)
        prompt = (
            f"New item:\n{item_details}\n\n"
            f"The user's wardrobe:\n{wardrobe_details}\n\n"
            "Suggest outfit combinations using the new item and these wardrobe pieces."
        )
    else:
        system = (
            "Give general styling advice for the new item without assuming the "
            "user owns any other specific pieces. Suggest useful types of pieces, "
            "colors, or layers. Keep the advice concise."
        )
        prompt = (
            f"New item:\n{item_details}\n\n"
            "The user's wardrobe is empty. Give general ideas for styling this item."
        )

    suggestion = generate(prompt, system=system).strip()
    if suggestion:
        return suggestion

    item_title = new_item.get("title", "this item")
    if wardrobe_items:
        owned_piece = wardrobe_items[0].get("name", "a piece from your wardrobe")
        return f"Try building an outfit around {item_title} and {owned_piece}."
    return f"Try styling {item_title} with complementary colors and balanced proportions."


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.

    This calls the model too.

    Args:
        outfit:   the outfit suggestion string from suggest_outfit().
        new_item: the listing dict for the item.

    Returns:
        A two-to-four sentence caption.
        If `outfit` is empty or whitespace, return a descriptive message rather
        than raising.

    The caption should read like a real post rather than a product description,
    mention the item and its price and platform once each, and be specific about
    the vibe.

    It should also come out **differently for different inputs**. If you run
    this three times on the same item and get three word-for-word identical
    strings, it's one of two things, and both are near the top of `config.py`:

        • CACHE_ENABLED — the adapter handed back an answer it already had
        • TEMPERATURE   — at 0.0 the model gives the same words every time

    TODO:
        1. Guard against an empty or whitespace-only `outfit`.
        2. Build a prompt with the item details and the outfit.
        3. Call generate() and return the response.

    Test it from a terminal before you move on:
        python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
    """
    title = new_item.get("title", "This item")
    price = new_item.get("price")
    price_text = f"${price:.2f}" if isinstance(price, (int, float)) else "an unlisted price"
    platform = new_item.get("platform", "an unknown platform")
    colors = ", ".join(new_item.get("colors") or []) or "its listed"
    fallback = (
        f"{title} is listed for {price_text} on {platform}. "
        f"Style it with pieces that complement {colors} colors."
    )

    if not outfit.strip():
        return fallback

    system = (
        "Write a natural social-media fit caption in exactly 2 sentences, not "
        "a product description. In sentence 1, use the item's exact title once "
        "and describe its vibe. In sentence 2, use the outfit suggestion and "
        "state the exact listed price and platform once each. Do not repeat the "
        "title, price, or platform, and do not invent item details."
    )
    prompt = (
        f"Listing:\n{json.dumps(new_item, ensure_ascii=False, indent=2)}\n\n"
        f"Outfit suggestion:\n{outfit.strip()}\n\n"
        "Write the caption now."
    )
    caption = generate(prompt, system=system).strip()
    return caption or fallback
