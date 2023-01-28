import paralleldots
import language_tool_python


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

def Check_Grammar(text) -> int:
    tool = language_tool_python.LanguageTool('en-US')
    return len(tool.check(text))


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
        "Dear XXXX, Our security system has detected some irregular activity connected to your account.",
        "you will be unable to send and recieve emails until this issue has been resolved CLICK HERE TO VALIDATE NOW."
    ]
    

    # Test for Check_Grammar
    sample = "A sentence with a error in the Hitchhiker's Guide to the Galaxy. A sentence with an error i the Hhiker's Guide to the Galaxy. A sentence with an errr in the Hitchhiker's Guide to the Galaxy. A sentence with an error in the Hitchhiker's Guide to the Galaxy."
    
    # Result should be 3 mistakes
    print(Check_Grammar(sample))



    # returns a JSON object for emotion in the text
    response = paralleldots.batch_emotion(text)

    print(JSON_to_emotionDict(response))


if __name__ == "__main__":
    main()
