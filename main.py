import asyncio, json
from pydantic import BaseModel
from crawl4ai import (
    AsyncWebCrawler, BrowserConfig, CrawlerRunConfig,
    CacheMode, LLMConfig, LLMExtractionStrategy
)


condo_name = "Promenade Peak"

query = (
    "Read the markdown of the price-overview-widget and extract:\n"
    "- property_name\n"
    "- sale_price_range (low-high form, include currency symbol)\n"
    "- rental_price_range (low-high form, include currency symbol)\n"
    "Return JSON with exactly these three fields."
)

base_url = "https://www.propertyguru.com.sg/condo-directory"

class PriceOverview(BaseModel):
    property_name: str
    sale_price_range: str
    rental_price_range: str

strategy = LLMExtractionStrategy(
    llm_config = LLMConfig(
            provider="azure/gpt-4.5-preview",
            base_url=" Azure Base URL ", 
            api_token="Your Own API Token"
            ),

    schema=PriceOverview.model_json_schema(),
    extraction_type="schema",
    instruction=query,
    chunk_token_threshold=2000,
    apply_chunking=True,  
    input_format="fit-markdown",
    extra_args={"temperature": 0.0},
    verbose=True
)

run_cfg = CrawlerRunConfig(
    cache_mode=CacheMode.BYPASS,
    extraction_strategy=strategy,
    js_code=[
        f"""
        (async () => {{
            const input = document.querySelector('input[name="freetext"]');
            input.focus();
            input.value = "{condo_name}";
            input.dispatchEvent(new Event("input", {{ bubbles: true }}));
            await new Promise(r => setTimeout(r, 1500));
            const first = document.querySelector('.tt-suggestion');
            if (first) first.click();
            await new Promise(r => setTimeout(r, 500));
            const btn = document.querySelector('button.btn-submit');
            if (btn) btn.click();
            await new Promise(r => setTimeout(r, 2000));
        }})()
        """
    ],
    wait_for = "js:() => window.location.href.includes('/project/promenade-peak-') && document.querySelector('div.price-overview-widget.clearfix')",
    wait_for_timeout=120_000,
    delay_before_return_html=3.0,
    simulate_user=True,
    magic=True,
    screenshot=True,
    screenshot_wait_for=3.0,
)

async def main():
    browser_cfg = BrowserConfig(headless=False, verbose=True)
    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(url=base_url, config=run_cfg)

    if result.success:
        data = json.loads(result.extracted_content)
        print("Extracted info:\n", data)

        md_filename = f"{condo_name.lower().replace(' ', '_')}.md"
        with open(md_filename, "w", encoding="utf-8") as f:
            f.write(result.markdown)
        print(f"Markdown saved to {md_filename}")

        # save screenshot
        if result.screenshot:
            from base64 import b64decode
            with open("page_screenshot.png", "wb") as imgf:
                imgf.write(b64decode(result.screenshot))
            print("Screenshot saved: page_screenshot.png")

    else:
        print(" Extraction failed:", result.error_message)

if __name__ == "__main__":
    asyncio.run(main())