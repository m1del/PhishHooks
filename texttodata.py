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
    intentDict = {"news": [], "query": [], "spam": [], "marketing": [], "feedback": []}
    for key, value in response["intent"].items():
        intentDict[key].append(value)

    return intentDict


def JSON_to_emotionDict(response) -> dict:
    emotionDict = {"Fear": [], "Bored": [], "Excited": [], "Angry": [], "Happy": [], "Sad": []}
    for key, value in response["emotion"].items():
        emotionDict[key].append(value)

    return emotionDict


def writeToTXT(text, grammarErrors, keyWordDict, intentDict):
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
    text = ["Good day, Please, answer the questions Employee Survey - it won`t take long. Waiting for you to go through this survey ASAP. You can find the survey here: hxxps://docs.google.com/document/d/e/2PACX-1vSjKdTddXL-psR2rYotGSJuwOeBHUKkulbrhy78PHX6VtdJWFurH9mEmeV8PLVm1t4P5W0msKzpCg3N/pub HR Department Analyst Uc Regents;"]
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

    #response = paralleldots.emotion(text)
    #emotionDict = JSON_to_emotionDict(response)
    #t4 = time.time()
    #print(f"Retrieved emotions, took {t4-t3:.2f} seconds")

    writeToTXT(" ".join(text), errors, keywordDict, intentDict)
    print(f"Total time: {(time.time() - t0):.2f} seconds")


if __name__ == "__main__":
    main()
