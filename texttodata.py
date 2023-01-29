import paralleldots
import language_tool_python
import time

def JSON_to_keywordDict(response) -> dict:
    keywordDict = {}
    for lists in response["keywords"]:
        if lists:
            for dicts in lists:
                keywordDict[dicts["keyword"]] = dicts["confidence_score"]
    return keywordDict


def JSON_to_intentDict(response) -> dict:
    intentDict = {"news": [], "query": [], "spam": [], "marketing": [], "feedback": []}
    for dicts in response["intent"]:
        if dicts:
            innerDict = dicts["intent"]
            for key, value in innerDict.items():
                intentDict[key].append(value)

    return intentDict


def JSON_to_emotionDict(response) -> dict:
    emotionDict = {"Fear": [], "Bored": [], "Excited": [], "Angry": [], "Happy": [], "Sad": []}
    for dicts in response["emotion"]:
        for key, value in dicts.items():
            emotionDict[key].append(value)

    return emotionDict


def writeToTXT(text, grammarErrors, keyWordDict, intentDict, emotionDict):
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
        f.write("Emotions:\n")
        for key, value in emotionDict.items():
            f.write(f"{key}: {value}\n")


def check_grammar(text) -> int:
    tool = language_tool_python.LanguageTool('en-US')
    return len(tool.check(text))

def main():
    # API key
    paralleldots.set_api_key("2BD2GHXk4JCZdQHphGuUYZEXXkhoxFRqjbqbRK5M4YA")

    # Example text
    text = [
        "Hello, Are you currently in the US? Here is an opportunity for you to work part time after classes and earn "
        "$500 weekly. The job is completely done online and can be completed anytime in the evening/night at home and "
        "won't take much of your time daily, you don't have to be online all day and don't need any professional "
        "skill to do the job, all you need is just come online before going to bed to forward all order of the day "
        "made by agents to the supplier and you are done for the day."]

    t0 = time.time()
    errors = check_grammar(" ".join(text))
    t1 = time.time()
    print(f"Checked grammar, took {t1-t0:.2f} seconds")

    response = paralleldots.batch_keywords(text)
    keywordDict = JSON_to_keywordDict(response)
    t2 = time.time()
    print(f"Retrieved keywords, took {t2-t1:.2f} seconds")

    response = paralleldots.batch_intent(text)
    intentDict = JSON_to_intentDict(response)
    t3 = time.time()
    print(f"Retrieved intents, took {t3-t2:.2f} seconds")

    response = paralleldots.batch_emotion(text)
    emotionDict = JSON_to_emotionDict(response)
    t4 = time.time()
    print(f"Retrieved emotions, took {t4-t3:.2f} seconds")

    writeToTXT(" ".join(text), errors, keywordDict, intentDict, emotionDict)
    print(f"Total time: {(time.time() - t0):.2f} seconds")


if __name__ == "__main__":
    main()
