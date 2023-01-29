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


def JSON_to_emotionDict(response) -> dict:
    emotionDict = {"Fear": [], "Bored": [], "Excited": [], "Angry": [], "Happy": [], "Sad": []}
    for dicts in response["emotion"]:
        for key, value in dicts.items():
            emotionDict[key].append(value)

    return emotionDict


def check_grammar(text) -> int:
    tool = language_tool_python.LanguageTool('en-US')
    return len(tool.check(text))


def writeToTXT(text, grammarErrors, keyWordDict, intentDict, emotionDict):
    with open("data.txt", "w") as f:
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

def main():
    # API key
    paralleldots.set_api_key("2BD2GHXk4JCZdQHphGuUYZEXXkhoxFRqjbqbRK5M4YA")

    # Example text
    text = [
<<<<<<< HEAD:texttocsvdata.py
        "Dear XXXX, Our security system has detected some irregular activity connected to your account.",
        "you will be unable to send and recieve emails until this issue has been resolved CLICK HERE TO VALIDATE NOW."
    ]
    

    # Test for Check_Grammar
    sample = "A sentence with a error in the Hitchhiker's Guide to the Galaxy. A sentence with an error i the Hhiker's Guide to the Galaxy. A sentence with an errr in the Hitchhiker's Guide to the Galaxy. A sentence with an error in the Hitchhiker's Guide to the Galaxy."
    
    # Result should be 3 mistakes
    print(Check_Grammar(sample))
=======
        "Dear recipient, We have received your cancellation request and you are no longer subscribed to "
        "security.berkeley.edu. If you did not request cancellation, kindly click below to reactivate your account."]
>>>>>>> 9bc45fc2d5e21ec48f0659352ae40a12cc936e29:texttodata.py

    errors = check_grammar(" ".join(text))
    response = paralleldots.batch_keywords(text)
    keywordDict = JSON_to_keywordDict(response)

    response = paralleldots.batch_intent(text)
    intentDict = JSON_to_intentDict(response)

    response = paralleldots.batch_emotion(text)
    emotionDict = JSON_to_emotionDict(response)

    writeToTXT(" ".join(text), errors, keywordDict, intentDict, emotionDict)


if __name__ == "__main__":
    main()
