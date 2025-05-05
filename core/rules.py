# Rules regarding the hints
def check_hint(taboo_list: list[str], guess_word: str, hint: str, level: int, hints_list: list[str] = None, french_translations_dict: dict = None) -> bool:
    """This function checks if the hint respects the rules of the game.
    The rules, ordered by level, are:
    - Level 1: The hint must not contain any of the taboo words (including the guess_word)
    - Level 2: The hint must not contain any of the taboo words (including the guess_word or its french translation)
    - Level 3: The hint must be taken from a prefixed list of hints
    - Level 4: The hint must have at most 5 words, and none of them can be the guess_word or any of the taboo words or be longer than 20 characters

    Args:
        taboo_list (list[str]): The list of taboo words.
        guess_word (str): The word to guess.
        hint (str): The hint to check.
        level (int): The level of the game.
        hints_list (list[str], optional): The list of hints for level 3. Defaults to None.
        french_translations_dict (dict, optional): The dictionary of french translations for level 2. Defaults to None.

    Returns:
        bool: True if the hint respects the rules, False otherwise.
    """

    # Check for validity of the inputs
    if hint is None or not isinstance(hint, str):
        raise ValueError(f"Invalid hint: '{hint}'")
    
    if level not in [1, 2, 3, 4]:
        return False
    
    # Level 3: Check if hint is in the predefined list
    if level == 3:
        return hint in hints_list
    
    # Check if the hint contains any of the taboo words or the guess_word (except for level 3)
    if level in [1,2,4]:

        forbidden_words = taboo_list + [guess_word]

        # Level 2: Add the french translation of the guess_word to the forbidden words
        if level == 2:
            guess_word_translation = french_translations_dict.get(guess_word, None)
            if guess_word_translation:
                forbidden_words.append(guess_word_translation)

        # Check if the hint contains any of the forbidden words
        lowered_hint = hint.lower()
        normalized_hint = ''.join(c for c in lowered_hint if c.isalnum())
        reversed_normalized_hint = normalized_hint[::-1]
        for word in forbidden_words:
            word = word.lower()
            if word in lowered_hint or word in normalized_hint or word in reversed_normalized_hint:
                return False
            

    # Level 4: Additional word count and length restrictions
    if level == 4:
        words = hint.split()
        if len(words) > 5 or any(len(word) > 20 for word in words):
            return False
    
    # Return True if all checks passed
    return True


# Rules regarding the guess
def check_guess(guess_word: str, guess: str, level: int, french_translations_dict: dict):
    """This function checks if the guess is correct, according to the level of the game.
    The rules are:
    - Level 1,3,4: The guess must be equal to the guess_word
    - Level 2: The guess must be equal to the french translation of the guess_word

    Args:
        guess_word (str): The word to guess.
        guess (str): The guess to check.
        level (int): The level of the game.

    Returns:
        bool: True if the guess is correct, False otherwise.
    """
    match level:
        case 1 | 3 | 4:
            # Check if the guess is equal to the guess_word
            return guess.lower() == guess_word.lower()
        case 2:
            # Check if the guess is equal to the french translation of the guess_word
            translation = french_translations_dict.get(guess_word.lower().capitalize(), None)
            return translation is not None and translation.lower() == guess.lower()
        case _:
            # If the level is not recognized, we assume the guess is not valid
            return False
    return True
