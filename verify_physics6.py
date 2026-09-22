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

        # Let's print out max values to see if recoil works
        data = await page.evaluate("""() => {
            let maxBend = 0;
            let endBend = precalculatedPhysicsData[999].stickBendB;
            for (let d of precalculatedPhysicsData) {
                if (Math.abs(d.stickBendB) > maxBend) maxBend = Math.abs(d.stickBendB);
            }
            return {maxBend, endBend};
        }""")
        print("Recoil Check:", data)
        await browser.close()

asyncio.run(run())
