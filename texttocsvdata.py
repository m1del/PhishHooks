import paralleldots


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


def main():
    # API key
    paralleldots.set_api_key("2BD2GHXk4JCZdQHphGuUYZEXXkhoxFRqjbqbRK5M4YA")

    # Example text
    text = [
        "I like eating bacon.",
        "Why is John taking so long?"]

    # returns a JSON object for emotion in the text
    response = paralleldots.batch_emotion(text)

    print(JSON_to_emotionDict(response))


if __name__ == "__main__":
    main()
