import paralleldots


def JSON_to_keywordDict(response) -> dict:
    keywordDict = {}
    for lists in response["keywords"]:
        if lists:
            for dicts in lists:
                keywordDict[dicts["keyword"]] = dicts["confidence_score"]
    return keywordDict


def main():
    # API key
    paralleldots.set_api_key("2BD2GHXk4JCZdQHphGuUYZEXXkhoxFRqjbqbRK5M4YA")

    # Example text
    text = [
        "Dear XXXX, Our security system has detected some irregular activity connected to your account.",
        "you will be unable to send and recieve emails until this issue has been resolved CLICK HERE TO VALIDATE NOW."
    ]

    # returns a JSON object for keywords in the text
    response = paralleldots.batch_keywords(text)

    print(JSON_to_keywordDict(response))


if __name__ == "__main__":
    main()
