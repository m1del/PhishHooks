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


def main():
    # API key
    paralleldots.set_api_key("2BD2GHXk4JCZdQHphGuUYZEXXkhoxFRqjbqbRK5M4YA")

    # Example text
    text = [
        "Dear XXXX, Our security system has detected some irregular activity connected to your account.",
        "you will be unable to send and recieve emails until this issue has been resolved CLICK HERE TO VALIDATE NOW."
    ]

    # returns a JSON object for intent in the text
    response = paralleldots.batch_intent(text)

    print(JSON_to_intentDict(response))


if __name__ == "__main__":
    main()
