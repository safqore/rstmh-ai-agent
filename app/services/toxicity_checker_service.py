from openai import OpenAI

class ToxicityChecker:
    @staticmethod
    def check_toxicity(content):
        """
        Checks the content for toxicity using OpenAI's Moderation API.
        Returns a tuple: (is_toxic, categories) where:
          - is_toxic: True if flagged as toxic
          - categories: List of categories flagged (e.g., hate, sexual, violence)
        """
        try:
            client = OpenAI()
            response = client.moderations.create(
                model="omni-moderation-latest",
                input=content,
            )
            results = response.results[0]
            categories = results.categories
            return results.flagged, {category: value for category, value in categories.__dict__.items()}
        except Exception as e:
            print(f"Error checking toxicity: {e}")
            return False, {}
