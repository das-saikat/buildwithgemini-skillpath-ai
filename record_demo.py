import asyncio
import os
import shutil
from playwright.async_api import async_playwright

async def record_demo():
    output_dir = "/config/Desktop/Session1/skillpath-ai/recordings"
    os.makedirs(output_dir, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(
            record_video_dir=output_dir,
            record_video_size={"width": 1280, "height": 720},
            viewport={"width": 1280, "height": 720}
        )
        page = await context.new_page()

        print("Navigating to SkillPath AI frontend...")
        await page.goto("http://localhost:8080/", wait_until="networkidle")
        await page.wait_for_timeout(3000)

        # 1. Ask primary prompt (what app does best: personalized roadmap)
        print("Submitting prompt 1: Generate Python roadmap...")
        await page.fill("#input", "Generate a 4-week Python Data Science roadmap")
        await page.click('#form button[type="submit"]')
        await page.wait_for_timeout(10000)

        # 2. Toggle Dark Mode
        print("Toggling Dark Mode...")
        await page.click("#theme-btn")
        await page.wait_for_timeout(2000)

        # 3. Ask second, richer prompt (tool call, database lookup, generated image)
        print("Submitting prompt 2: Generate module badge image and recommend books...")
        await page.fill("#input", "Generate a visual achievement badge for my Python Data Science module and recommend books")
        await page.click('#form button[type="submit"]')
        await page.wait_for_timeout(14000)

        # 4. Open Analytics Drawer to show off dashboard
        print("Opening Analytics Drawer...")
        await page.click("#drawer-toggle-btn")
        await page.wait_for_timeout(3000)

        print("Closing context to save video...")
        await page.close()
        await context.close()
        await browser.close()

        # Find saved video and rename to final demo_video.webm / mp4
        files = os.listdir(output_dir)
        video_files = [f for f in files if f.endswith(".webm")]
        if video_files:
            src_video = os.path.join(output_dir, video_files[0])
            dest_webm = "/config/Desktop/Session1/demo_video.webm"
            dest_mp4 = "/config/Desktop/Session1/demo_video.mp4"
            shutil.copy(src_video, dest_webm)
            print(f"Video saved to {dest_webm}")
            
            # Convert to mp4 using ffmpeg
            os.system(f"ffmpeg -y -i {dest_webm} -pix_fmt yuv420p {dest_mp4}")
            print(f"Converted mp4 saved to {dest_mp4}")

if __name__ == "__main__":
    asyncio.run(record_demo())
