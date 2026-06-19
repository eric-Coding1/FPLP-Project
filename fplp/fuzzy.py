"""FPLP Language - Fuzzy matching & auto-correction utilities."""

from .lexer import KEYWORDS, IDENT


# ---------------------------------------------------------------------------
# Levenshtein distance (iterative, O(n*m))
# ---------------------------------------------------------------------------

def levenshtein(a, b):
    """Compute Levenshtein edit distance between two strings."""
    if len(a) < len(b):
        a, b = b, a
    if not b:
        return len(a)

    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a):
        curr = [i + 1]
        for j, cb in enumerate(b):
            cost = 0 if ca == cb else 1
            curr.append(min(
                curr[j] + 1,       # deletion
                prev[j + 1] + 1,   # insertion
                prev[j] + cost     # substitution
            ))
        prev = curr
    return prev[-1]


# ---------------------------------------------------------------------------
# Keyword auto-correction
# ---------------------------------------------------------------------------

def suggest_keyword(word, max_distance=2):
    """Find the closest matching keyword for a misspelled word.

    Returns (suggested_keyword, distance) or (None, None) if nothing close.
    """
    if not word or len(word) < 3:
        return None, None

    # Words containing digits or uppercase are not keyword typos
    if any(c.isdigit() for c in word):
        return None, None
    if word[0].isupper():
        return None, None

    # Words that are common short builtins or very common identifiers:
    # perfect match for some keyword by distance, but clearly not a typo.
    _SHORT_COMMON = {'len', 'add', 'sub', 'div', 'mod', 'abs', 'min', 'max',
                     'pow', 'str', 'int', 'obj', 'key', 'val', 'log', 'exp',
                     'sin', 'cos', 'tan', 'pid', 'uid', 'txt', 'hex', 'dec',
                     'lib', 'dir', 'etc', 'app', 'end'}
    if word in _SHORT_COMMON:
        return None, None

    # Scale max_distance by word length
    if len(word) <= 3:
        scaled_max = 1  # very short words: max 1 edit
    elif len(word) <= 5:
        scaled_max = min(max_distance, 2)  # short words: allow transpositions
    else:
        scaled_max = max_distance

    best_word = None
    best_dist = scaled_max + 1

    for kw in KEYWORDS:
        # Length filter: ignore words that differ too much in length
        if abs(len(kw) - len(word)) > max(1, len(word) // 2):
            continue
        # For words <= 4 chars, allow at most ±1 length difference
        if len(word) <= 4 and abs(len(kw) - len(word)) > 1:
            continue
        # First-letter match requirement: prefer same starting letter
        if len(word) >= 3 and kw[0] != word[0]:
            # Allow different first letter only if the word is long enough (>5 chars)
            # or the distance penalty is worth it
            base_dist = levenshtein(word, kw)
            if base_dist + 1 > scaled_max:
                continue
            dist = base_dist + 1  # extra penalty for different first letter
        else:
            dist = levenshtein(word, kw)

        if dist < best_dist:
            best_dist = dist
            best_word = kw

    if best_word and best_dist <= scaled_max:
        return best_word, best_dist
    return None, None


def correct_keyword(word):
    """Auto-correct a keyword typo. Returns corrected keyword or None."""
    # First check common typos dictionary (exact match)
    result = fast_correct(word)
    if result:
        # If it's a multi-word suggestion like "else if", only use the first word
        return result.split()[0] if ' ' in result else result

    # Fall back to Levenshtein-based fuzzy matching
    suggested, dist = suggest_keyword(word)
    if suggested and dist <= 2:
        return suggested
    return None


# ---------------------------------------------------------------------------
# Variable name auto-correction
# ---------------------------------------------------------------------------

def suggest_variable(name, known_names, max_distance=3):
    """Find the closest known variable name.

    Args:
        name: The misspelled variable name
        known_names: Iterable of valid variable names
        max_distance: Maximum edit distance for a suggestion

    Returns (suggested_name, distance) or (None, None).
    """
    if not name or not known_names:
        return None, None

    best_name = None
    best_dist = max_distance + 1

    for kn in known_names:
        dist = levenshtein(name, kn)
        if dist < best_dist:
            best_dist = dist
            best_name = kn

    if best_name and best_dist <= max_distance:
        return best_name, best_dist
    return None, None


# ---------------------------------------------------------------------------
# Typo database — common misspellings for instant lookup
# ---------------------------------------------------------------------------

COMMON_TYPOS = {
    "flase": "false",
    "fasle": "false",
    "fals": "false",
    "ture": "true",
    "treu": "true",
    "tru": "true",
    "nill": "nil",
    "nul": "nil",
    "elsse": "else",
    "esle": "else",
    "els": "else",
    "whlie": "loop",
    "whille": "loop",
    "whle": "loop",
    "whil": "while",
    "looop": "loop",
    "lopp": "loop",
    "loot": "loop",
    "lewt": "let",
    "lett": "let",
    "lte": "let",
    "retrun": "return",
    "retunr": "return",
    "reutrn": "return",
    "retur": "return",
    "functon": "fn",
    "funct": "fn",
    "func": "fn",
    "fun": "fn",
    "fucntion": "fn",
    "fro": "for",
    "fpor": "for",
    "fr": "for",
    "breka": "break",
    "braek": "break",
    "brke": "break",
    "contiue": "continue",
    "contnue": "continue",
    "contiune": "continue",
    "cotnue": "continue",
    "cointinue": "continue",
    "elsif": "else if",
    "elseif": "else if",
    "elif": "else if",
    "def": "fn",
    "defn": "fn",
    "define": "fn",
    "const": "let",
    "var": "let",
    "prnt": "print",
    "prtin": "print",
    "prtinln": "print",
    "prin": "print",
}

def fast_correct(word):
    """Look up a word in the common typos dictionary."""
    return COMMON_TYPOS.get(word)
