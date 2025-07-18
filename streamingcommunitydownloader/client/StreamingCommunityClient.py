from typing import List
from injector import inject
from playwright.async_api import async_playwright
from streamingcommunitydownloader.model.StreamUrl import StreamUrl


class StreamingCommunityClient:

    @inject
    def __init__(self):
        pass
    
    async def get_title(self, url: str) -> str:
        async with async_playwright() as p:
            browser = await p.webkit.launch()
            page = await browser.new_page()
            await page.goto(url)
            title = await page.text_content("h1.title")
            await browser.close()
            return title if title else "Title not found"
        

    async def is_movie(self, url: str) -> bool:
        async with async_playwright() as p:
            browser = await p.webkit.launch()
            page = await browser.new_page()
            await page.goto(url)
            is_movie = await page.evaluate("document.querySelector('#episodes-tab') === null")
            await browser.close()
            return is_movie

    async def get_episode_urls(self, url: str, selected_season_number = None, selected_episode_number = None) -> List[StreamUrl]:
        async with async_playwright() as p:
            browser = await p.webkit.launch(
                headless=True,  # Run in headless mode for better performance
            )
            page = await browser.new_page()
            await page.goto(url)
            await page.wait_for_load_state("networkidle")
            await page.wait_for_selector("h1.title")
            title = await page.text_content("h1.title")
            # .buttons a.play2
            await page.wait_for_selector(".buttons a.play2")
            # click
            await page.click(".buttons a.play2")
            # await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(3000)  # Wait for the page to load completely
            
            # Set up request handler to capture streaming URLs
            captured_urls = []
            
            async def handle_request(request):
                url = request.url
                # Capture relevant streaming URLs (adjust the condition based on the actual URL patterns)
                if any(pattern in url for pattern in ['master.m3u8']):
                    captured_urls.append(url)
            
            page.on("request", handle_request)
            
            # seasons .tt_season a
            season_numbers = await page.evaluate(
                "Array.from(document.querySelectorAll('.tt_season a')).map(a => a.textContent.trim())"
            )
            # episode_numbers = await page.evaluate(
            #     "Array.from(document.querySelectorAll('.tt_series a')).map(a => a.textContent.trim() if a.textContent else '')"
            # )

            episode_urls: List[StreamUrl] = []

            for season_number in season_numbers:
                if (selected_season_number and (int(season_number) != selected_season_number)):
                    continue

                # click on the season
                await page.click(f".tt_season a:has-text('{season_number}')")
                # await page.wait_for_load_state("networkidle")
                await page.wait_for_timeout(3000)

                episode_numbers = await page.evaluate(
                    f"Array.from(document.querySelectorAll('#season-{season_number} a')).map(a => a.textContent.trim())"
                )
                # filter where is digit
                episode_numbers = [ep for ep in episode_numbers if ep.isdigit()]

                for episode_number in episode_numbers:
                    if (selected_episode_number and (int(episode_number) != selected_episode_number)):
                        continue

                    captured_urls = []

                    # await page.click(f"a[data-num='{season_number}x{episode_number}']")
                    # evaluate click
                    await page.evaluate(f"document.querySelector('a[data-num=\"{season_number}x{episode_number}\"]').click()")
                    # await page.wait_for_load_state("networkidle")
                    await page.wait_for_timeout(3000)
                    
                    if len(captured_urls) > 0:
                        stream_url = StreamUrl(
                            url=captured_urls[0],
                            title=title,
                            season_number=int(season_number),
                            episode_number=int(episode_number)
                        )
                        episode_urls.append(stream_url)

            await browser.close()
            return episode_urls
