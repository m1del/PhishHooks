import paralleldots
import language_tool_python
import time

def JSON_to_keywordDict(response) -> dict:
    # list[dict] key = word, val = 
    keywordDict = {}
    for dicts in response["keywords"]:
        keywordDict[dicts["keyword"]] = dicts["confidence_score"]
    return keywordDict


def JSON_to_intentDict(response) -> dict:
    intentDict = {"news": 0, "query": 0, "spam": 0, "marketing": 0, "feedback": 0}
    for key, value in response["intent"].items():
        intentDict[key] = value

    return intentDict


def JSON_to_emotionDict(response) -> dict:
    emotionDict = {"Fear": [], "Bored": [], "Excited": [], "Angry": [], "Happy": [], "Sad": []}
    for key, value in response["emotion"].items():
        emotionDict[key].append(value)

    return emotionDict


def writeToTXT(text, grammarErrors, keyWordDict, intentDict, weights):
    with open("data.txt", "a") as f:
        f.write(f"Text: {text}\n")
        f.write(f"Grammar Errors: {grammarErrors}\n")
        f.write("Keywords: ")
        for key in keyWordDict:
            f.write(key + " ")
        f.write("\n")
        f.write("Intents:\n")
        for key, value in intentDict.items():
            f.write(f"{key}: {value}\n")
        f.write(f"Number of Intents Weighted: {weights}\n")


def check_grammar(text) -> int:
    tool = language_tool_python.LanguageTool('en-US', config={ 'cacheSize': 10000, 'pipelineCaching': True })
    return len(tool.check(text))

def intent_Weights(intentDict) -> int:
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

    # Example text
    text = ["Dear Student, Your access to your library account is expiring soon due to inactivity. To continue to have access to the library services, you must reactivate your account. For this purpose, click the web address below or copy and paste it into your web browser. A successful login will activate your account and you will be redirected to your library profile. https://auth.berkeley.edu/cas/login?service=https%3a%2f%(link is external). If you are not able to login, please contact at xxxxx@berkeley.edu(link sends e-mail) for immediate assistance."]
    t0 = time.time()
    errors = check_grammar(" ".join(text))
    t1 = time.time()
    print(f"Checked grammar, took {t1-t0:.2f} seconds")

    response = paralleldots.keywords(text)
    keywordDict = JSON_to_keywordDict(response)
    t2 = time.time()
    print(f"Retrieved keywords, took {t2-t1:.2f} seconds")

    response = paralleldots.intent(text)
    intentDict = JSON_to_intentDict(response)
    t3 = time.time()
    print(f"Retrieved intents, took {t3-t2:.2f} seconds")

    t4 = time.time()
    weights = intent_Weights(intentDict)
    print(f"Retrieved intent weights, took {t4-t3:.2f} seconds")

    #response = paralleldots.emotion(text)
    #emotionDict = JSON_to_emotionDict(response)
    #t4 = time.time()
    #print(f"Retrieved emotions, took {t4-t3:.2f} seconds")

    writeToTXT(" ".join(text), errors, keywordDict, intentDict, weights)
    print(f"Total time: {(time.time() - t0):.2f} seconds")


if __name__ == "__main__":
    main()