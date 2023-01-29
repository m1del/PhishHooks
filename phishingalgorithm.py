import csv
import paralleldots
import time
import language_tool_python

SPAMWORDS_FILENAME = "spamwords.csv"
AVG_SPAM_COEFF = 0.082


def JSON_to_keywordDict(response) -> dict:
    keywordDict = {}
    for dicts in response["keywords"]:
        keywordDict[dicts["keyword"]] = dicts["confidence_score"]
    return keywordDict


def JSON_to_intentDict(response) -> dict:
    intentDict = {"news": 0, "query": 0, "spam": 0, "marketing": 0, "feedback": 0}
    for key, value in response["intent"].items():
        intentDict[key] = value

    return intentDict


def import_spam_keywords() -> dict:
    spam_words_dict = {}
    with open(SPAMWORDS_FILENAME, "r") as csvfile:
        reader = csv.reader(csvfile)

        for row in reader:
            if row:
                spam_words_dict[row[0]] = row[1]

    return spam_words_dict


def determine_keyword_coefficient(text, spam_words_dict, keywordDict) -> float:
    # Split string to a list of words
    words = text.split()
    total = 0.0

    # Find the max confidence score of the keywords
    maxKeyWordConfidence = max(keywordDict.values())

    for word in words:
        lower_word = word.lower()
        # If the word is a delineated spam word
        if lower_word in spam_words_dict:
            keywordDictConfidence = 0
            spam_coefficient = float(spam_words_dict[lower_word])
            # Check each keyword in the keyword dict
            for key in keywordDict:
                # If the spam word is a substring of the keyword (which may be a phrase)
                if lower_word in key.lower():
                    # Maintain the largest confidence score from the keywords the spam word may be a substring of
                    keywordDictConfidence = max(keywordDictConfidence, keywordDict[key])
            multiplier = 1
            if keywordDictConfidence != 0:
                # Add to the multiplier of 1 the proportion of the confidence score with the max confidence score
                multiplier += (keywordDictConfidence / maxKeyWordConfidence)

            total += (spam_coefficient * multiplier)

    keyword_coefficient = total / AVG_SPAM_COEFF / len(words)
    # 0.0 - 0.20 seems typical of a normal email, >>0.20 seems to indicate phishing emails
    return keyword_coefficient


def check_grammar(text) -> int:
    tool = language_tool_python.LanguageTool('en-US', config={ 'cacheSize': 10000, 'pipelineCaching': True })
    return len(tool.check(text))


def intent_weights(intentDict) -> int:
    # int of 0, 1, 2
    # Check for highest 2 categories, if they are spam + marketing = 2, and on and on

    weight = 0
    highest = 0.0
    secondHighest = -1.0

    biggestIntent = "empty"
    secondBiggestIntent = "empty"

    for key, value in intentDict.items():
        if type(value) is dict:
            break

        if value > highest:
            secondBiggestIntent = biggestIntent
            biggestIntent = key
            secondHighest = highest
            highest = value
        elif value > secondHighest:
            secondBiggestIntent = key
            secondHighest = value

    if biggestIntent == "spam" or biggestIntent == "marketing":
        weight += 1
    if secondBiggestIntent == "marketing" or secondBiggestIntent == "spam":
        weight += 1

    return weight


def main():
    # API key
    paralleldots.set_api_key("2BD2GHXk4JCZdQHphGuUYZEXXkhoxFRqjbqbRK5M4YA")

    text = "Dear Student, Your access to your library account is expiring soon due to inactivity. To continue to have " \
           "access to the library services, you must reactivate your account. For this purpose, click the web address " \
           "below or copy and paste it into your web browser. A successful login will activate your account and you " \
           "will be redirected to your library profile. (link " \
           "is external) If you are not able to login, please contact at xxxxx@berkeley.edu(link sends e-mail) for " \
           "immediate assistance. "

    spam_words_dict = import_spam_keywords()

    t0 = time.time()
    errors = check_grammar(text)
    t1 = time.time()
    print(f"Checked grammar, took {t1 - t0:.2f} seconds")

    response = paralleldots.keywords(text)
    keywordDict = JSON_to_keywordDict(response)
    t2 = time.time()
    print(f"Retrieved keywords, took {t2 - t1:.2f} seconds")

    response = paralleldots.intent(text)
    intentDict = JSON_to_intentDict(response)
    t3 = time.time()
    print(f"Retrieved intents, took {t3 - t2:.2f} seconds")

    print(f"Keyword Coefficient: {determine_keyword_coefficient(text, spam_words_dict, keywordDict)}")
    print(f"Grammatical Errors: {errors}")
    print(f"Intent Weights: {intent_weights(intentDict)}")


if __name__ == "__main__":
    main()
