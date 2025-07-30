import unittest
from integrations.third_party.functions.actions.ExtractIocs import (
    get_urls,
    clean_found_url,
    extract_domains_from_urls,
    extract_ips,
    extract_emails,
)


class TestIOCExtraction(unittest.TestCase):
    def test_get_urls(self):
        input_text = (
            "Visit https://example.com and http://test.org/index.html. Check ip http://8.8.8.8"
        )
        urls = get_urls(input_text)
        self.assertIn("https://example.com", urls)
        self.assertIn("http://test.org/index.html", urls)
        self.assertIn("http://8.8.8.8", urls)



    def test_clean_found_url(self):
        dirty_url = "\"https://example.com/page.html\r\n"
        cleaned = clean_found_url(dirty_url)
        self.assertEqual(cleaned, "https://example.com/page.html")

        no_tld_url = "http://localhost"
        self.assertIsNone(clean_found_url(no_tld_url))

        js_url = "http://example.com/script.js"
        self.assertIsNone(clean_found_url(js_url))

        empty_url = "http://"
        self.assertIsNone(clean_found_url(empty_url))

    def test_extract_domains_from_urls(self):
        urls = ["https://sub.example.com/path", "http://test.org"]
        domains = extract_domains_from_urls(urls)
        self.assertIn("example.com", domains)
        self.assertIn("test.org", domains)

    def test_extract_ips(self):
        input_text = "Valid IPs: 8.8.8.8 and ::1. Private: 192.168.1.1"

        ips = extract_ips(input_text, include_internal=False)
        self.assertIn("8.8.8.8", ips)
        self.assertNotIn("192.168.1.1", ips)
        self.assertNotIn("::1", ips)


        ips_all = extract_ips(input_text, include_internal=True)
        self.assertIn("192.168.1.1", ips_all)
        self.assertIn("8.8.8.8", ips_all)

    def test_extract_emails(self):
        text = "Valid: user@example.com, admin@sub.domain.co.uk. Invalid: user@com"
        emails = extract_emails(text)
        self.assertIn("user@example.com", emails)
        self.assertIn("admin@sub.domain.co.uk", emails)
        self.assertNotIn("user@com", emails)


if __name__ == "__main__":
    unittest.main()
