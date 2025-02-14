import google.generativeai as genai
from textblob import TextBlob
import Data_retrieval  

# Configure Gemini API
from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)


def get_gemini_sentiment(text):
    """
    Uses Gemini API to analyze sentiment.
    """
    prompt = f"Analyze the sentiment of the following text and return the counts for positive, neutral, and negative sentiments.\n\nText: {text}\n\nFormat your response as:\nPositive: X\nNeutral: Y\nNegative: Z"
    
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)

    # Parse the response
    gemini_sentiment = {"positive": 0, "neutral": 0, "negative": 0}
    
    if response and response.text:
        lines = response.text.split("\n")
        for line in lines:
            if "Positive:" in line:
                gemini_sentiment["positive"] = int(line.split(":")[1].strip())
            elif "Neutral:" in line:
                gemini_sentiment["neutral"] = int(line.split(":")[1].strip())
            elif "Negative:" in line:
                gemini_sentiment["negative"] = int(line.split(":")[1].strip())

    return gemini_sentiment

def get_textblob_sentiment(text):
    """
    Uses TextBlob for sentiment analysis.
    """
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity  # -1 to 1 scale

    if polarity > 0:
        return {"positive": 1, "neutral": 0, "negative": 0}
    elif polarity < 0:
        return {"positive": 0, "neutral": 0, "negative": 1}
    else:
        return {"positive": 0, "neutral": 1, "negative": 0}

def ensemble_sentiment_analysis(text):
    """
    Combines Gemini and TextBlob sentiment scores using an averaging method.
    """
    # Get sentiment outputs
    gemini_output = get_gemini_sentiment(text)
    textblob_output = get_textblob_sentiment(text)

    # Normalize Gemini scores to percentages
    total_gemini = sum(gemini_output.values()) or 1  # Avoid division by zero
    gemini_normalized = {k: v / total_gemini for k, v in gemini_output.items()}

    # Normalize TextBlob scores to percentages
    total_textblob = sum(textblob_output.values()) or 1
    textblob_normalized = {k: v / total_textblob for k, v in textblob_output.items()}

    # Combine by averaging
    final_sentiment = {
        "positive": (gemini_normalized["positive"] + textblob_normalized["positive"]) / 2,
        "neutral": (gemini_normalized["neutral"] + textblob_normalized["neutral"]) / 2,
        "negative": (gemini_normalized["negative"] + textblob_normalized["negative"]) / 2
    }

    # Convert to percentages
    final_sentiment_percentage = {k: round(v * 100, 2) for k, v in final_sentiment.items()}

    return final_sentiment_percentage

def main():
    """
    Main function to get earnings call transcript from PDF and analyze sentiment.
    """
    pdf_path = input("Enter the path to the earnings call transcript PDF: ")
    transcript_text = Data_retrieval.extract_text_from_pdf(pdf_path)

    if not transcript_text:
        print("Error: No text extracted from the document.")
        return

    sentiment_result = ensemble_sentiment_analysis(transcript_text)

    print("\nEarnings Call Transcript Sentiment Analysis:")
    print(f"Positive: {sentiment_result['positive']:.2f}%")
    print(f"Neutral: {sentiment_result['neutral']:.2f}%")
    print(f"Negative: {sentiment_result['negative']:.2f}%")

if __name__ == "__main__":
    main()
