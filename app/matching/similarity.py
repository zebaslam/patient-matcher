"""String similarity algorithms for patient matching."""

def levenshtein_distance(s1, s2):
    """Basic Levenshtein distance calculation."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

def similarity_ratio(s1, s2):
    """Similarity ratio based on edit distance."""
    max_len = max(len(s1), len(s2))
    return 1.0 if max_len == 0 else 1.0 - levenshtein_distance(s1, s2) / max_len

def token_overlap_score(s1, s2):
    """Token-based overlap score."""
    tokens1 = set(s1.split())
    tokens2 = set(s2.split())
    return len(tokens1 & tokens2) / len(tokens1 | tokens2) if tokens1 and tokens2 else 0.0

def jaro_similarity(s1: str, s2: str) -> float:
    """Calculate Jaro similarity between two strings."""
    if not s1 or not s2:
        return 0.0
    
    if s1 == s2:
        return 1.0
    
    len1, len2 = len(s1), len(s2)
    
    # Calculate the match window
    match_window = max(len1, len2) // 2 - 1
    if match_window < 0:
        match_window = 0
    
    # Track matches and transpositions
    s1_matches = [False] * len1
    s2_matches = [False] * len2
    matches = 0
    transpositions = 0
    
    # Find matches
    for i in range(len1):
        start = max(0, i - match_window)
        end = min(i + match_window + 1, len2)
        
        for j in range(start, end):
            if s2_matches[j] or s1[i] != s2[j]:
                continue
            s1_matches[i] = s2_matches[j] = True
            matches += 1
            break
    
    if matches == 0:
        return 0.0
    
    # Count transpositions
    k = 0
    for i in range(len1):
        if not s1_matches[i]:
            continue
        while not s2_matches[k]:
            k += 1
        if s1[i] != s2[k]:
            transpositions += 1
        k += 1
    
    jaro = (matches / len1 + matches / len2 + (matches - transpositions / 2) / matches) / 3
    return jaro

def jaro_winkler_similarity(s1: str, s2: str, prefix_scale: float = 0.1) -> float:
    """Calculate Jaro-Winkler similarity with prefix bonus."""
    jaro = jaro_similarity(s1, s2)
    
    if jaro < 0.7:
        return jaro
    
    # Calculate common prefix length (up to 4 characters)
    prefix_len = 0
    for i in range(min(len(s1), len(s2), 4)):
        if s1[i] == s2[i]:
            prefix_len += 1
        else:
            break
    
    return jaro + (prefix_len * prefix_scale * (1 - jaro))