#!/usr/bin/env python3
"""Rank scraped phone numbers by memorability."""

import argparse
import json
import re
import sys
from collections import Counter

# Phone keypad mapping for vanity word detection
KEYPAD = {
    "2": "abc", "3": "def", "4": "ghi", "5": "jkl",
    "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz",
}
DIGIT_TO_LETTERS = {}
for digit, letters in KEYPAD.items():
    for letter in letters:
        DIGIT_TO_LETTERS[letter] = digit

VANITY_WORDS = {
    "baby", "back", "bail", "bake", "ball", "band", "bank", "bare", "bark",
    "barn", "base", "bass", "bath", "beam", "bean", "bear", "beat", "beef",
    "beer", "bell", "belt", "bend", "best", "bike", "bill", "bird", "bite",
    "blow", "blue", "boat", "body", "bold", "bolt", "bomb", "bond", "bone",
    "book", "boom", "boot", "born", "boss", "bowl", "bulk", "bull", "burn",
    "bush", "busy", "buzz", "cafe", "cage", "cake", "call", "calm", "came",
    "camp", "card", "care", "cart", "case", "cash", "cast", "cave", "chat",
    "chef", "chip", "chop", "city", "clan", "clap", "clip", "club", "clue",
    "coal", "coat", "code", "coin", "cold", "cole", "come", "cook", "cool",
    "cope", "copy", "cord", "core", "corn", "corp", "cost", "coup", "crew",
    "crop", "crow", "cure", "curl", "cute", "dark", "dart", "dash", "data",
    "date", "dawn", "dead", "deaf", "deal", "dean", "dear", "debt", "deck",
    "deed", "deem", "deep", "deer", "demo", "deny", "desk", "dial", "dice",
    "diet", "dirt", "disc", "dish", "dock", "does", "dome", "done", "doom",
    "door", "dose", "down", "drag", "draw", "drop", "drum", "duck", "dude",
    "duke", "dull", "dumb", "dump", "dune", "dust", "duty", "each", "earn",
    "ease", "east", "easy", "edge", "edit", "else", "epic", "euro", "even",
    "ever", "evil", "exam", "exec", "exit", "face", "fact", "fade", "fail",
    "fair", "fake", "fall", "fame", "farm", "fast", "fate", "fear", "feat",
    "feed", "feel", "feet", "fell", "felt", "file", "fill", "film", "find",
    "fine", "fire", "firm", "fish", "fist", "flag", "flat", "fled", "flew",
    "flip", "flow", "foam", "fold", "folk", "fond", "font", "food", "fool",
    "foot", "ford", "fork", "form", "fort", "foul", "four", "free", "from",
    "fuel", "full", "fund", "fury", "fuse", "gain", "gala", "game", "gang",
    "gate", "gave", "gaze", "gear", "gene", "gift", "girl", "give", "glad",
    "glow", "glue", "goat", "goes", "gold", "golf", "gone", "good", "grab",
    "gram", "gray", "grew", "grid", "grin", "grip", "grow", "gulf", "guru",
    "hack", "half", "hall", "halt", "hand", "hang", "hard", "harm", "hash",
    "hate", "haul", "have", "hawk", "haze", "head", "heal", "heap", "hear",
    "heat", "heel", "held", "hell", "help", "herb", "herd", "here", "hero",
    "hide", "high", "hike", "hill", "hint", "hire", "hold", "hole", "holy",
    "home", "hood", "hook", "hope", "horn", "host", "hour", "huge", "hull",
    "hung", "hunt", "hurt", "icon", "idea", "inch", "info", "iron", "isle",
    "item", "jack", "jade", "jail", "jazz", "jean", "jedi", "jerk", "jest",
    "jobs", "join", "joke", "jump", "june", "jury", "just", "keen", "keep",
    "kept", "kick", "kids", "kill", "kind", "king", "kiss", "kite", "knee",
    "knew", "knit", "knob", "knot", "know", "lace", "lack", "lady", "laid",
    "lake", "lamp", "land", "lane", "laps", "last", "late", "lawn", "lead",
    "leaf", "leak", "lean", "leap", "left", "lend", "lens", "lick", "life",
    "lift", "like", "limb", "lime", "limp", "line", "link", "lion", "list",
    "live", "load", "loan", "lock", "logo", "long", "look", "loop", "lord",
    "lore", "lose", "loss", "lost", "loud", "love", "luck", "lump", "lung",
    "lure", "lurk", "lush", "made", "mail", "main", "make", "male", "mall",
    "malt", "many", "maps", "mark", "mars", "mask", "mass", "mate", "maze",
    "meal", "mean", "meat", "meet", "melt", "memo", "menu", "mere", "mesh",
    "mess", "mice", "mild", "milk", "mill", "mind", "mine", "mint", "miss",
    "mist", "moat", "mock", "mode", "mold", "monk", "mood", "moon", "more",
    "moss", "most", "moth", "move", "much", "muse", "must", "myth", "nail",
    "name", "navy", "near", "neat", "neck", "need", "nest", "news", "next",
    "nice", "nine", "node", "none", "noon", "norm", "nose", "note", "noun",
    "null", "numb", "nuts", "oath", "odds", "okay", "once", "only", "onto",
    "open", "oral", "oven", "over", "pace", "pack", "page", "paid", "pain",
    "pair", "pale", "palm", "pane", "para", "park", "part", "pass", "past",
    "path", "peak", "peel", "peer", "pick", "pier", "pile", "pine", "pink",
    "pipe", "plan", "play", "plea", "plot", "plug", "plus", "poem", "poet",
    "poll", "polo", "pond", "pool", "poor", "pope", "pork", "porn", "port",
    "pose", "post", "pour", "pray", "prey", "prop", "pros", "pull", "pump",
    "punk", "pure", "push", "quit", "quiz", "race", "rack", "rage", "raid",
    "rail", "rain", "rank", "rare", "rash", "rate", "rave", "read", "real",
    "rear", "reef", "reel", "rent", "rest", "rice", "rich", "ride", "ring",
    "riot", "rise", "risk", "road", "roam", "roar", "robe", "rock", "rode",
    "role", "roll", "roof", "room", "root", "rope", "rose", "ruin", "rule",
    "rush", "rust", "ruth", "sack", "safe", "sage", "said", "sail", "sake",
    "sale", "salt", "same", "sand", "sane", "sang", "save", "seal", "seam",
    "seas", "seat", "seed", "seek", "seem", "seen", "self", "sell", "semi",
    "send", "sent", "sept", "sewn", "shed", "ship", "shop", "shot", "show",
    "shut", "sick", "side", "sigh", "sign", "silk", "sing", "sink", "site",
    "size", "skip", "slam", "slap", "slid", "slim", "slip", "slot", "slow",
    "snap", "snow", "soak", "soar", "sock", "soft", "soil", "sold", "sole",
    "some", "song", "soon", "sort", "soul", "sour", "span", "spec", "sped",
    "spin", "spit", "spot", "star", "stay", "stem", "step", "stew", "stir",
    "stop", "such", "suit", "sung", "sure", "surf", "swap", "swim", "tabs",
    "taco", "tail", "take", "tale", "talk", "tall", "tank", "tape", "task",
    "taxi", "team", "tear", "teen", "tell", "tend", "tens", "tent", "term",
    "test", "text", "than", "that", "them", "then", "they", "thin", "this",
    "tick", "tide", "tidy", "tied", "tier", "tile", "till", "time", "tiny",
    "tips", "tire", "toad", "toda", "toes", "told", "toll", "tomb", "tone",
    "took", "tool", "tops", "tore", "torn", "toss", "tour", "town", "toys",
    "trap", "tray", "tree", "trim", "trio", "trip", "true", "tube", "tuck",
    "tune", "turn", "twin", "type", "ugly", "undo", "unit", "upon", "urge",
    "used", "user", "vain", "vale", "vast", "verb", "very", "vest", "vibe",
    "view", "vine", "void", "volt", "vote", "wage", "wait", "wake", "walk",
    "wall", "want", "ward", "warm", "warn", "warp", "wary", "wash", "wave",
    "weak", "wear", "weed", "week", "weld", "well", "went", "were", "west",
    "what", "when", "whom", "wide", "wife", "wild", "will", "wilt", "wind",
    "wine", "wing", "wire", "wise", "wish", "with", "woke", "wolf", "wood",
    "wool", "word", "wore", "work", "worm", "worn", "wrap", "yard", "yarn",
    "year", "yoga", "yoke", "your", "zero", "zone", "zoom",
    # common words previously missing
    "bang", "bait", "bags", "mama", "papa", "vary", "mash", "mare", "mayo",
    "maul", "mama", "mint", "mist", "plat", "swell", "space", "judo",
    "snag", "creek", "trail", "beach", "roam", "trek",
    # fun/memorable 3-letter ones
    "ace", "art", "bar", "bat", "bet", "big", "bit", "bot", "box", "bro",
    "bug", "bun", "bus", "buy", "cab", "cam", "cap", "car", "cat", "cop",
    "cow", "cry", "cub", "cup", "cut", "dam", "day", "den", "dew", "dig",
    "dim", "dip", "dog", "dot", "dry", "dub", "dug", "dye", "ear", "eat",
    "egg", "ego", "elk", "elm", "end", "era", "eve", "eye", "fan", "far",
    "fat", "fax", "fig", "fin", "fit", "fix", "fly", "fog", "for", "fox",
    "fry", "fun", "fur", "gag", "gap", "gas", "gem", "get", "gin", "god",
    "got", "gum", "gun", "gut", "guy", "gym", "had", "ham", "hat", "hay",
    "hen", "her", "hid", "him", "hip", "his", "hit", "hog", "hop", "hot",
    "how", "hub", "hue", "hug", "hum", "hut", "ice", "ill", "imp", "ink",
    "inn", "ion", "ivy", "jab", "jam", "jar", "jaw", "jay", "jet", "jig",
    "job", "jog", "joy", "jug", "key", "kid", "kin", "kit", "lab", "lad",
    "lag", "lap", "law", "lay", "led", "leg", "let", "lid", "lip", "lit",
    "log", "lot", "low", "lug", "mad", "man", "map", "mat", "max", "may",
    "men", "met", "mid", "mix", "mob", "mod", "mom", "mop", "mow", "mud",
    "mug", "nag", "nap", "net", "new", "nil", "nip", "nit", "nod", "nor",
    "not", "now", "nun", "nut", "oak", "oar", "oat", "odd", "off", "oil",
    "old", "one", "opt", "orb", "ore", "our", "out", "owe", "owl", "own",
    "pad", "pal", "pan", "paw", "pay", "pea", "peg", "pen", "per", "pet",
    "pie", "pig", "pin", "pit", "ply", "pod", "pop", "pot", "pow", "pro",
    "pub", "pug", "pun", "pup", "put", "rag", "ram", "ran", "rap", "rat",
    "raw", "ray", "red", "ref", "rib", "rid", "rig", "rim", "rip", "rob",
    "rod", "rot", "row", "rub", "rug", "rum", "run", "rut", "rye", "sad",
    "sag", "sap", "sat", "saw", "say", "sea", "set", "sew", "shy", "sin",
    "sip", "sir", "sis", "sit", "six", "ski", "sky", "sly", "sob", "sod",
    "son", "sop", "sot", "sow", "soy", "spa", "spy", "sub", "sue", "sum",
    "sun", "sup", "tab", "tag", "tan", "tap", "tar", "tax", "tea", "ten",
    "the", "tie", "tin", "tip", "toe", "ton", "too", "top", "tot", "tow",
    "toy", "try", "tub", "tug", "two", "urn", "use", "van", "vat", "vet",
    "vex", "via", "vie", "vim", "vow", "wad", "wag", "war", "was", "wax",
    "way", "web", "wed", "wet", "who", "why", "wig", "win", "wit", "woe",
    "wok", "won", "woo", "wow", "yak", "yam", "yap", "yaw", "yea", "yes",
    "yet", "yew", "you", "zap", "zen", "zip", "zoo",
    # custom / brand
    "anytrip",
    # aussie swears
    "shit", "fuck", "cunt", "arse",
}


def word_to_digits(word: str) -> str:
    return "".join(DIGIT_TO_LETTERS.get(c, "") for c in word.lower())


# --- Dictionary loading ---
_VOWELS = set("aeiou")
_WORD_RE = re.compile(r"^[a-z]{3,8}$")
_DICT_PATHS = [
    "/usr/share/dict/british-english",
    "/usr/share/dict/american-english",
    "/usr/share/dict/words",
    "/usr/share/cracklib/cracklib-small",
]

def _load_dictionary() -> set[str]:
    """Load filtered word list from system dictionaries, trying largest first."""
    for path in _DICT_PATHS:
        try:
            with open(path) as f:
                words = set()
                for line in f:
                    w = line.strip().lower()
                    if _WORD_RE.match(w) and _VOWELS & set(w):
                        words.add(w)
                if words:
                    print(f"Loaded {len(words)} words from {path}", file=sys.stderr)
                    return words
        except OSError:
            continue
    print("Warning: no system dictionary found, "
          "using built-in vanity word list only", file=sys.stderr)
    return set()

DICTIONARY_WORDS = _load_dictionary()


# --- Word quality scoring ---
# Premium words: travel/adventure themed — get extra boost
PREMIUM_WORDS = {
    # travel/adventure
    "bush", "map", "maps", "hike", "trip", "camp", "trek", "trail",
    "roam", "wild", "park", "path", "lake", "reef", "surf", "sand",
    "boat", "fish", "dive", "land", "road", "tour", "anytrip",
    # aussie swears — memorable vanity numbers
    "shit", "fuck", "crap", "damn", "arse", "cunt", "dick", "piss",
    "tits", "bong", "root", "slag", "slut",
}

def _word_quality(word: str) -> float:
    """Return quality score: premium > tier 1 > tier 2."""
    if word in PREMIUM_WORDS:
        return 1.5
    if word in VANITY_WORDS:
        return 1.0
    return 0.6  # tier 2: recognisable dictionary word


# Length bonus: longer single words are disproportionately impressive
# A 6-letter word should rival two 3-letter words; an 8-letter word should be best
_LENGTH_MULT = {3: 1.0, 4: 1.2, 5: 1.8, 6: 2.8, 7: 3.5, 8: 4.5}

def _word_score(word: str) -> float:
    length_mult = _LENGTH_MULT.get(len(word), 4.5)
    return len(word) * _word_quality(word) * length_mult


# --- Digit trie ---
class TrieNode:
    __slots__ = ("children", "words")
    def __init__(self):
        self.children: dict[str, TrieNode] = {}
        self.words: list[tuple[str, float]] = []


def _build_digit_trie() -> TrieNode:
    """Build a trie keyed by digit sequences, storing (word, score) at leaves."""
    root = TrieNode()
    all_words = (DICTIONARY_WORDS | VANITY_WORDS) if DICTIONARY_WORDS else VANITY_WORDS
    for word in all_words:
        digits = word_to_digits(word)
        if len(digits) != len(word):  # skip words with non-alpha chars
            continue
        node = root
        for d in digits:
            if d not in node.children:
                node.children[d] = TrieNode()
            node = node.children[d]
        score = _word_score(word)
        node.words.append((word, score))
    # Sort each node's words by score descending, then alphabetically for stability
    def _sort_trie(node: TrieNode):
        if node.words:
            node.words.sort(key=lambda x: (-x[1], x[0]))
        for child in node.children.values():
            _sort_trie(child)
    _sort_trie(root)
    return root

DIGIT_TRIE = _build_digit_trie()


# --- Trie-based vanity word finding ---
def find_vanity_words(digits: str) -> list[tuple[int, int, str, float]]:
    """Walk the trie from each starting position in the digit string.

    Returns list of (start, length, best_word, word_score) tuples.
    Only the best-scoring word per digit sequence is returned.
    """
    results = []
    n = len(digits)
    for start in range(n):
        node = DIGIT_TRIE
        for offset in range(n - start):
            d = digits[start + offset]
            if d not in node.children:
                break
            node = node.children[d]
            if node.words:
                best_word, best_score = node.words[0]
                results.append((start, offset + 1, best_word, best_score))
    return results


def find_all_vanity_words(digits: str) -> list[tuple[str, int]]:
    """Find all unique vanity words at any position in the digit string.

    Returns list of (word, first_start_position) sorted by word.
    """
    seen: dict[str, int] = {}
    n = len(digits)
    for start in range(n):
        node = DIGIT_TRIE
        for offset in range(n - start):
            d = digits[start + offset]
            if d not in node.children:
                break
            node = node.children[d]
            for word, _ in node.words:
                if word not in seen:
                    seen[word] = start
    return sorted(seen.items())


# --- Multi-word coverage via DP ---
def _best_coverage(matches: list[tuple[int, int, str, float]], n: int) -> tuple[int, float, list[tuple[int, int, str]]]:
    """Right-to-left DP to find best non-overlapping word placement.

    Optimizes for max digit coverage first, then max quality score as tiebreaker.
    Returns (digits_covered, total_score, [(start, length, word), ...]).
    """
    # dp[i] = (digits_covered, total_score, placements) for positions i..n-1
    dp = [(0, 0.0, [])] * (n + 1)

    # Index matches by start position
    by_start: dict[int, list[tuple[int, int, str, float]]] = {}
    for start, length, word, score in matches:
        by_start.setdefault(start, []).append((start, length, word, score))

    for i in range(n - 1, -1, -1):
        # Option 1: skip this position
        best = dp[i + 1]

        # Option 2: place a word starting here
        if i in by_start:
            for start, length, word, score in by_start[i]:
                end = start + length
                if end <= n:
                    future_covered, future_score, future_placements = dp[end]
                    total_covered = length + future_covered
                    total_score = score + future_score
                    if (total_covered, total_score) > (best[0], best[1]):
                        best = (total_covered, total_score, [(start, length, word)] + future_placements)

        dp[i] = best

    return dp[0]


# --- Vanity-annotated number display ---
def format_vanity_number(raw: str, words: list[tuple[int, int, str]]) -> str:
    """Build a display string where matched digit ranges are replaced with words.

    Placements are relative to local[1:] (area code 2nd digit + subscriber = 9 chars).
    Uses the same XX XXXX XXXX spacing as format_au_number().
    """
    if raw.startswith("61"):
        local = "0" + raw[2:]
    else:
        local = raw
    if len(local) != 10:
        return local

    # Build 9-char array: area code 2nd digit + 8 subscriber digits
    chars = list(local[1:])
    for start, length, word in words:
        for j, ch in enumerate(word.upper()):
            if start + j < len(chars):
                chars[start + j] = ch

    # Reconstruct: 0 + chars[0] (area) + space + chars[1:5] + space + chars[5:]
    return f"{local[0]}{chars[0]} {''.join(chars[1:5])} {''.join(chars[5:])}"


# --- Main vanity scoring ---
def score_vanity(subscriber: str) -> tuple[int, str, list[tuple[int, int, str]] | None]:
    """Score vanity words in subscriber digits.

    Returns (points, reason_string, placements_or_None).
    """
    matches = find_vanity_words(subscriber)
    if not matches:
        return 0, "", None

    digits_covered, total_score, placements = _best_coverage(matches, len(subscriber))

    if not placements:
        return 0, "", None

    # Coverage multiplier — flat curve; word quality matters more than coverage
    n = len(subscriber)
    coverage_ratio = digits_covered / n if n else 0
    if coverage_ratio >= 1.0:
        coverage_mult = 1.3
    elif coverage_ratio >= 6 / 8:
        coverage_mult = 1.15
    elif coverage_ratio >= 4 / 8:
        coverage_mult = 1.0
    else:
        coverage_mult = 0.85

    # Alignment bonus: reward words that fit the XX XXXX XXXX display boundaries
    boundary = 5  # position of the subscriber group split in the 9-digit vanity string
    aligned = all(
        (start + length <= boundary) or (start >= boundary)
        for start, length, _ in placements
    )
    alignment_mult = 1.15 if aligned else 1.0

    pts = min(int(total_score * coverage_mult * alignment_mult * 2.0), 30)
    if pts <= 0:
        return 0, "", None

    # Build display strings
    word_names = [w for _, _, w in placements]
    display = "-".join(w.upper() for w in word_names)
    reason = f"vanity: {display} ({digits_covered}/{n} digits, {pts}pts)"

    return pts, reason, placements


def format_au_number(raw: str) -> str:
    if raw.startswith("61"):
        local = "0" + raw[2:]
    else:
        local = raw
    if len(local) == 10:
        return f"{local[:2]} {local[2:6]} {local[6:]}"
    return local


def score_number(raw: str) -> dict:
    """Score a phone number on memorability. Higher = better."""
    if raw.startswith("61"):
        local = "0" + raw[2:]
    else:
        local = raw

    # Score the subscriber digits (after area code)
    subscriber = local[2:] if len(local) == 10 else local
    score = 0
    reasons = []

    # --- 1. Repeating digit runs (max 30 pts) ---
    max_run = 1
    cur_run = 1
    for i in range(1, len(subscriber)):
        if subscriber[i] == subscriber[i - 1]:
            cur_run += 1
            max_run = max(max_run, cur_run)
        else:
            cur_run = 1
    if max_run >= 3:
        pts = (max_run - 2) * 10
        score += pts
        reasons.append(f"repeat run of {max_run} ({pts}pts)")

    # --- 2. Unique digit count (max 15 pts) ---
    unique = len(set(subscriber))
    if unique <= 3:
        pts = 15
    elif unique <= 4:
        pts = 10
    elif unique <= 5:
        pts = 5
    else:
        pts = 0
    if pts:
        score += pts
        reasons.append(f"{unique} unique digits ({pts}pts)")

    # --- 3. Trailing pattern (max 15 pts) ---
    trailing_zeros = len(subscriber) - len(subscriber.rstrip("0"))
    if trailing_zeros >= 3:
        pts = 15
        score += pts
        reasons.append(f"trailing {'0' * trailing_zeros} ({pts}pts)")
    elif trailing_zeros == 2:
        pts = 8
        score += pts
        reasons.append(f"trailing 00 ({pts}pts)")

    if trailing_zeros == 0:
        trail_digit = subscriber[-1]
        trail_count = 0
        for c in reversed(subscriber):
            if c == trail_digit:
                trail_count += 1
            else:
                break
        if trail_count >= 3:
            pts = 12
            score += pts
            reasons.append(f"trailing {trail_digit * trail_count} ({pts}pts)")
        elif trail_count == 2:
            pts = 5
            score += pts
            reasons.append(f"trailing {trail_digit * trail_count} ({pts}pts)")

    # --- 4. Sequential runs (max 12 pts) ---
    def find_sequential(s, ascending=True):
        best = 1
        cur = 1
        for i in range(1, len(s)):
            diff = int(s[i]) - int(s[i - 1])
            if diff == (1 if ascending else -1):
                cur += 1
                best = max(best, cur)
            else:
                cur = 1
        return best

    asc = find_sequential(subscriber, ascending=True)
    desc = find_sequential(subscriber, ascending=False)
    seq = max(asc, desc)
    if seq >= 4:
        pts = 12
        score += pts
        direction = "ascending" if asc >= desc else "descending"
        reasons.append(f"sequential run of {seq} {direction} ({pts}pts)")
    elif seq == 3:
        pts = 5
        score += pts
        direction = "ascending" if asc >= desc else "descending"
        reasons.append(f"sequential run of {seq} {direction} ({pts}pts)")

    # --- 5. Repeating pairs/patterns (max 10 pts) ---
    for i in range(len(subscriber) - 3):
        chunk = subscriber[i:i + 4]
        if chunk[0] != chunk[1] and chunk[0] == chunk[2] and chunk[1] == chunk[3]:
            pts = 8
            score += pts
            reasons.append(f"repeating pair {chunk} ({pts}pts)")
            break

    for i in range(len(subscriber) - 3):
        chunk = subscriber[i:i + 4]
        if chunk[0] == chunk[1] and chunk[2] == chunk[3] and chunk[0] != chunk[2]:
            pts = 6
            score += pts
            reasons.append(f"double pair {chunk} ({pts}pts)")
            break

    # --- 6. Palindrome in subscriber (max 10 pts) ---
    for length in range(6, 3, -1):
        for i in range(len(subscriber) - length + 1):
            chunk = subscriber[i:i + length]
            if chunk == chunk[::-1] and len(set(chunk)) > 1:
                pts = length * 2
                score += pts
                reasons.append(f"palindrome {chunk} ({pts}pts)")
                break
        else:
            continue
        break

    # --- 7. Vanity words (max 30 pts) ---
    # Include area code 2nd digit so vanity words can bridge into it
    vanity_digits = local[1:] if len(local) == 10 else subscriber
    vanity_pts, vanity_reason, vanity_placements = score_vanity(vanity_digits)
    if vanity_pts:
        score += vanity_pts
        reasons.append(vanity_reason)

    # --- 8. Digit frequency dominance (max 8 pts) ---
    freq = Counter(subscriber)
    most_common_freq = freq.most_common(1)[0][1]
    dominance = most_common_freq / len(subscriber)
    if dominance >= 0.5:
        pts = 8
        score += pts
        reasons.append(f"dominant digit ({pts}pts)")
    elif dominance >= 0.375:
        pts = 4
        score += pts
        reasons.append(f"semi-dominant digit ({pts}pts)")

    result = {
        "score": score,
        "vanity_score": vanity_pts,
        "reasons": reasons,
        "formatted": format_au_number(raw),
    }
    if vanity_placements:
        result["vanity_display"] = format_vanity_number(raw, vanity_placements)
    return result


def rank_all(results: dict, top_n: int = 20, vanity_only: bool = False) -> list[dict]:
    scored = []
    for state, cities in results.items():
        for city, numbers in cities.items():
            for entry in numbers:
                info = score_number(entry["number"])
                if vanity_only and not info["vanity_score"]:
                    continue
                item = {
                    "number": entry["number"],
                    "formatted": info["formatted"],
                    "state": state,
                    "city": city,
                    "score": info["score"],
                    "vanity_score": info["vanity_score"],
                    "reasons": info["reasons"],
                    "channels": entry["channels"],
                    "setup_cost": entry["setup_cost"],
                    "monthly_cost": entry["monthly_cost"],
                }
                if "vanity_display" in info:
                    item["vanity_display"] = info["vanity_display"]
                scored.append(item)
    sort_key = (lambda x: x["vanity_score"]) if vanity_only else (lambda x: x["score"])
    scored.sort(key=sort_key, reverse=True)
    return scored[:top_n] if top_n else scored


def export_explorer(results: dict) -> None:
    """Export all numbers as compact JSON for the web explorer."""
    import os
    records = []
    total = 0
    for state, cities in results.items():
        for city, numbers in cities.items():
            for entry in numbers:
                total += 1
                raw = entry["number"]
                info = score_number(raw)
                rec = {
                    "n": raw,
                    "s": state,
                    "c": city,
                    "sc": info["score"],
                }
                # Extract all vanity words with positions
                local = "0" + raw[2:] if raw.startswith("61") else raw
                vanity_digits = local[1:] if len(local) == 10 else local
                all_matches = find_all_vanity_words(vanity_digits)
                if all_matches:
                    rec["vw"] = all_matches
                records.append(rec)
                if total % 5000 == 0:
                    print(f"  Processed {total} numbers...", file=sys.stderr)

    # Sort by score descending for default view
    records.sort(key=lambda r: r["sc"], reverse=True)

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "explorer_data.js")
    with open(out_path, "w") as f:
        f.write("const DATA = ")
        json.dump(records, f, separators=(",", ":"))
        f.write(";\n")

    print(f"Exported {len(records)} numbers to {out_path}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Rank scraped phone numbers by memorability")
    parser.add_argument(
        "input",
        help="Input JSON file from scraper.py",
    )
    parser.add_argument(
        "--top", "-t",
        type=int,
        default=20,
        help="Show top N ranked numbers (default: 20, 0 for all)",
    )
    parser.add_argument(
        "--output", "-o",
        help="Save ranked results to JSON file",
    )
    parser.add_argument(
        "--state", "-s",
        help="Filter to specific state(s). Comma-separated.",
    )
    parser.add_argument(
        "--vanity", "-v",
        action="store_true",
        help="Show only vanity numbers, ranked by vanity score",
    )
    parser.add_argument(
        "--export",
        choices=["explorer"],
        help="Export data for web explorer (generates explorer_data.js)",
    )
    args = parser.parse_args()

    with open(args.input) as f:
        results = json.load(f)

    # Filter by state if requested
    if args.state:
        states = {s.strip().upper() for s in args.state.split(",")}
        results = {k: v for k, v in results.items() if k in states}

    if args.export == "explorer":
        export_explorer(results)
        return

    top_n = args.top or 0
    ranked = rank_all(results, top_n=top_n, vanity_only=args.vanity)

    total = sum(
        len(nums)
        for cities in results.values()
        for nums in cities.values()
    )
    show = min(args.top, len(ranked)) if args.top else len(ranked)

    label = "VANITY NUMBERS" if args.vanity else "NUMBERS"
    print(f"Ranking {total} numbers from {args.input}")
    print(f"\n{'=' * 60}")
    print(f" TOP {show} {label}")
    print(f"{'=' * 60}\n")

    for i, entry in enumerate(ranked[:show], 1):
        display = entry.get("vanity_display", entry["formatted"])
        print(f"  #{i:>2}  {display}  (score: {entry['score']})")
        if "vanity_display" in entry:
            print(f"       {entry['formatted']}")
        print(f"       {entry['state']} / {entry['city']}")
        if entry["reasons"]:
            print(f"       {', '.join(entry['reasons'])}")
        print()

    if args.output:
        with open(args.output, "w") as f:
            json.dump(ranked, f, indent=2)
        print(f"Ranked list saved to {args.output}")


if __name__ == "__main__":
    main()
