import asyncio
from playwright.async_api import async_playwright
import os

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        file_path = f"file://{os.path.abspath('Kickpoint_9.html')}"
        await page.goto(file_path)

        await asyncio.sleep(1)

        # Force a break by setting slider super fast and unchecking never break
        await page.evaluate("""() => {
            const timeSlider = document.getElementById('timeSlider');
            timeSlider.value = 850;
            timeSlider.dispatchEvent(new Event('input'));
        }""")
        await asyncio.sleep(0.5)

        await page.screenshot(path="physics_test_break.png")
        print("Saved physics_test_break.png")

        broken = await page.evaluate("brokenState !== null")
        print("Did break:", broken)

        await browser.close()

asyncio.run(run())
