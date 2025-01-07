from typing import Optional
import requests as rq


def get_wordlist() -> list[str]:
    try:
        wordlist = open("valid-wordle-words.txt").read().split("\n")
    except FileNotFoundError:
        wordlist = rq.get(
            "https://gist.githubusercontent.com/dracos/dd0668f281e685bad51479e5acaadb93/raw/6bfa15d263d6d5b63840a8e5b64e04b382fdb079/valid-wordle-words.txt"
        ).text.split("\n")
        if wordlist[-1] == "":
            wordlist = wordlist[:-1]
        with open("valid-wordle-words.txt", "w") as f:
            f.write("\n".join(wordlist))
    return wordlist


def get_possible_solutions() -> list[str]:
    try:
        wordlist = open("valid-wordle-solutions.txt").read().split("\n")
    except FileNotFoundError:
        wordlist = rq.get(
            "https://gist.githubusercontent.com/cfreshman/a03ef2cba789d8cf00c08f767e0fad7b/raw/45c977427419a1e0edee8fd395af1e0a4966273b/wordle-answers-alphabetical.txt"
        ).text.split("\n")
        if wordlist[-1] == "":
            wordlist = wordlist[:-1]
        with open("valid-wordle-solutions.txt", "w") as f:
            f.write("\n".join(wordlist))
    return wordlist


def get_unique_word(
    wordlist: list[str],
    green: Optional[dict[int, str]] = None,
    yellow: Optional[dict[int, str]] = None,
    guessed_words: list[str] = [],
    index: int = 0,
) -> tuple[list[str], str]:
    word = wordlist[index]
    if len(set(word)) != 5:
        return get_unique_word(wordlist, green, yellow, guessed_words, index + 1)
    wordlist.remove(word)
    return (wordlist, word)


def get_starter_word() -> tuple[list[str], list[str]]:
    wordlist: list[str] = get_possible_solutions()
    letter_frequency: dict[str, int] = {}
    for word in wordlist:
        for letter in word:
            if letter in letter_frequency:
                letter_frequency[letter] += 1
            else:
                letter_frequency[letter] = 1
    wordlist = sorted(
        wordlist,
        key=lambda x: sum([letter_frequency[letter] for letter in x]),
        reverse=True,
    )

    wordlist, guess = get_unique_word(wordlist)

    return wordlist, [guess]


def get_letters(error: bool = False) -> list[str]:
    if error:
        print("Invalid input. Please enter 5 letters.")
    letters = input()
    if len(letters) != 5 and letters != "":
        return get_letters(True)
    return [letter.upper() for letter in letters]


def get_discovered_letters() -> tuple[dict[int, str], dict[int, str]]:
    green_map: dict[int, str] = {}
    yellow_map: dict[int, str] = {}
    print("Enter the letters you have discovered so far:")
    print("First enter the green letters, ex. a___t:")
    green_letters: list[str] = get_letters()
    print("Enter the yellow letters:")
    yellow_letters: list[str] = get_letters()
    if len(green_letters) == 5:
        for index, letter in enumerate(green_letters):
            if letter == "_":
                continue
            else:
                green_map[index] = letter.lower()
    if len(yellow_letters) == 5:
        for index, letter in enumerate(yellow_letters):
            if letter == "_":
                continue
            else:
                yellow_map[index] = letter.lower()
    return green_map, yellow_map


def narrow_down_wordlist(
    green: dict[int, str],
    yellow: dict[int, str],
    guessed_words: list[str],
    wordlist: list[str],
) -> list[str]:
    for green_letter in green.items():
        wordlist = [
            word for word in wordlist if word[green_letter[0]] == green_letter[1]
        ]
    for yellow_letter in yellow.items():
        wordlist = [
            word
            for word in wordlist
            if word[yellow_letter[0]] != yellow_letter[1] and yellow_letter[1] in word
        ]
    gray_letters: list[str] = []
    for word in guessed_words:
        for letter in word:
            if letter not in green.values() and letter not in yellow.values():
                gray_letters.append(letter)

    for gray_letter in gray_letters:
        wordlist = [word for word in wordlist if gray_letter not in word]

    if len(wordlist) == 1:
        print_separator("The word is")
        print(wordlist[0])
        exit()

    return wordlist


def get_most_common_letters(
    green: dict[int, str], wordlist: list[str]
) -> dict[str, int]:
    green_indices = list(green.keys())
    letters: dict[str, int] = {}
    for word in wordlist:
        for index, letter in enumerate(word):
            if index in green_indices:
                continue
            if letter in letters:
                letters[letter] += 1
            else:
                letters[letter] = 1
    return letters


def print_separator(word: str = "") -> None:
    print("=" * ((64 - len(word)) // 2), end="")
    print(word, end="")
    print("=" * ((64 - len(word)) // 2 + len(word) % 2))


def sort_and_print_wordlist(
    green: dict[int, str], wordlist: list[str]
) -> tuple[list[str], str]:
    print("Calculating most common characters not guessed yet...")
    letter_freq: dict[str, int] = get_most_common_letters(green, wordlist)
    print("Ordering words by frequency of letters not guessed yet...")
    wordlist = sorted(
        wordlist,
        key=lambda x: sum(
            [letter_freq[letter] for letter in x if letter in letter_freq]
        ),
        reverse=True,
    )
    print_separator("Most likely words to guess next")
    if len(wordlist) > 5:
        for word in wordlist[:5]:
            print(word)
    else:
        for word in wordlist:
            print(word)
    guessed_word: str = input("Enter the word you guessed: ").lower()
    while guessed_word not in wordlist:
        print("Invalid guess. Please enter a valid word.")
        guessed_word = input().lower()
    wordlist.remove(guessed_word)
    return (wordlist, guessed_word)


def read_guess_loop(
    wordlist: list[str], guessed_words: list[str]
) -> tuple[list[str], list[str]]:
    print_separator()
    print("Enter U to get another unique guess.")
    print("Otherwise, enter anything else.")
    choice: str = input()
    print_separator()
    green, yellow = get_discovered_letters()
    wordlist = narrow_down_wordlist(green, yellow, guessed_words, wordlist)
    if choice.lower() == "u":
        wordlist, guess = get_unique_word(wordlist, green, yellow, guessed_words)
        print_separator()
        print("Unique guess:\n", guess, sep="")
    else:
        wordlist, guess = sort_and_print_wordlist(green, wordlist)
    guessed_words.append(guess)
    return wordlist, guessed_words


def main() -> None:
    print_separator("Wordle Solver")
    print("Start with this word:")
    wordlist, guessed_words = get_starter_word()
    print(guessed_words[0])
    for _ in range(5):
        wordlist, guessed_words = read_guess_loop(wordlist, guessed_words)


if __name__ == "__main__":
    main()
