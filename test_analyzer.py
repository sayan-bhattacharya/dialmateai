# test_analyzer.py
import asyncio
from src.services.text_analyzer import TextAnalyzer

async def test_analyzer():
    analyzer = TextAnalyzer()

    # Test text (sample conversation)
    test_text = """
    Person A: I really appreciate your help with this project.
    Person B: No problem! I enjoy working together on these challenges.
    Person A: Wait, let me finish explaining my idea...
    Person B: Sorry, I got excited. Please continue.
    Person A: I think we should focus on the user experience first.
    Person B: That's a great point. I understand your perspective.
    """

    try:
        analysis = await analyzer.analyze_text(test_text)
        print("\nAnalysis Results:")
        for category, results in analysis.items():
            print(f"\n{category.upper()}:")
            if isinstance(results, dict):
                for key, value in results.items():
                    print(f"  {key}: {value}")
            else:
                print(f"  {results}")
    except Exception as e:
        print(f"Error during analysis: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_analyzer())