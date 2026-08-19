import unittest
from bs4 import BeautifulSoup

class TestQuoteParser(unittest.TestCase):
    def test_quote_extraction(self):
        # Fake HTML snippet mimicking the target site
        sample_html = """
        <div class="quote">
            <span class="text">“Test quote text”</span>
            <small class="author">Test Author</small>
            <a class="tag">testing</a>
        </div>
        """
        soup = BeautifulSoup(sample_html, "html.parser")
        block = soup.find("div", class_="quote")
        
        text = block.find("span", class_="text").get_text(strip=True)
        author = block.find("small", class_="author").get_text(strip=True)
        
        self.assertEqual(text, "“Test quote text”")
        self.assertEqual(author, "Test Author")

if __name__ == "__main__":
    unittest.main()