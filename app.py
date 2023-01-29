import streamlit as st
import csv
import paralleldots
import time
import language_tool_python
import pandas as pd


SPAMWORDS_FILENAME = "spamwords.csv"
AVG_SPAM_COEFF = 0.082


def JSON_to_keywordDict(response) -> dict:
    keywordDict = {}
    for dicts in response["keywords"]:
        keywordDict[dicts["keyword"]] = dicts["confidence_score"]
    return keywordDict


def JSON_to_intentDict(response) -> dict:
    intentDict = {"news": 0, "query": 0,
                  "spam": 0, "marketing": 0, "feedback": 0}
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
                    keywordDictConfidence = max(
                        keywordDictConfidence, keywordDict[key])
            multiplier = 1
            if keywordDictConfidence != 0:
                # Add to the multiplier of 1 the proportion of the confidence score with the max confidence score
                multiplier += (keywordDictConfidence / maxKeyWordConfidence)

            total += (spam_coefficient * multiplier)

    keyword_coefficient = total / AVG_SPAM_COEFF / len(words)
    # 0.0 - 0.20 seems typical of a normal email, >>0.20 seems to indicate phishing emails
    return keyword_coefficient


def check_grammar(text) -> int:
    tool = language_tool_python.LanguageTool(
        'en-US', config={'cacheSize': 10000, 'pipelineCaching': True})
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


# Returns a decision coefficient centered around the value of 50, with >>50 indicating likely phishing
def generate_decision_coefficient(keyword_coefficient, errors, intent_weight):
    decision_coefficient = 50
    change = 0
    keyword_distribution_value = 0
    if keyword_coefficient < 0.20:
        keyword_distribution_value = abs(keyword_coefficient - 0.20) / 0.20
        change -= (keyword_distribution_value * 100)
    elif keyword_coefficient > 0.20:
        keyword_distribution_value = (keyword_coefficient - 0.20) / 0.80
        change += (keyword_distribution_value * 100)
    if intent_weight == 0:
        change -= (10 * (1 - keyword_distribution_value))
    elif intent_weight == 2:
        change += (20 * (1 - keyword_distribution_value))
    if errors == 0:
        change -= (10 * (1 - keyword_distribution_value))
    elif errors > 1:
        maxErrors = max(5, errors)
        change += (5 * maxErrors * (1 - keyword_distribution_value))

    return decision_coefficient + change


def DisplayGraph(decision_coefficient):
    if decision_coefficient > 100:
        decision_coefficient = 100
    if decision_coefficient < 0:
        decision_coefficient = 0

    chart_data = pd.DataFrame([decision_coefficient],
    columns=["Phishing Likliehood"])
    st.bar_chart(chart_data)

def RankDecision(decision_coefficient):
    if decision_coefficient > 100:
        decision_coefficient = 100
    if decision_coefficient < 0:
        decision_coefficient = 0

    if decision_coefficient >=0 and decision_coefficient < 20:
        st.write("No Warnings")
    elif decision_coefficient >= 20 and decision_coefficient < 40:
        st.write("Safe")
    elif decision_coefficient >= 40 and decision_coefficient < 60:
        st.write("Caution")
    elif decision_coefficient >=60 and decision_coefficient < 80:
        st.write("Danger")
    else:
        st.write("Most likely a phishing attempt")



def main():
    # API key
    paralleldots.set_api_key("2BD2GHXk4JCZdQHphGuUYZEXXkhoxFRqjbqbRK5M4YA")

    st.title("PhishHooks!")
    st.write("The bigger the phish, the bigger the hook!")

    spam_words_dict = import_spam_keywords()

    text = st.text_input('Email Body:')
    if not text:
        st.warning('Please input text')
        st.stop()
    st.success('Thank you for inputting text')

    with st.spinner('Analyzing...'):
        errors = check_grammar(text)
        response = paralleldots.keywords(text)
        keyWordDict = JSON_to_keywordDict(response)

        response = paralleldots.intent(text)
        intentDict = JSON_to_intentDict(response)

        keyWordCoefficient = determine_keyword_coefficient(text, spam_words_dict, keyWordDict)
        intentWeights = intent_weights(intentDict)

        decicision = generate_decision_coefficient(keyWordCoefficient, errors, intentWeights)
        RankDecision(decicision)
        DisplayGraph(decicision)
    st.success('Done!')


if __name__ == "__main__":
    main()
