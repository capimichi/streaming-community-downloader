import math
from typing import List, Optional
from injector import inject
from playwright.async_api import async_playwright
from streamingcommunitydownloader.model.StreamUrl import StreamUrl
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse


class StreamingCommunityClient:

    @inject
    def __init__(self):
        pass        

    async def is_movie(self, url: str) -> bool:
        async with async_playwright() as p:
            browser = await p.webkit.launch()
            page = await browser.new_page()
            await page.goto(url)
            is_movie = await page.evaluate(
                "document.querySelector('#episodes-tab') === null && document.querySelector('.nav-item.episodes') === null"
            )
            await browser.close()
            return is_movie

    async def get_episode_urls(self, url: str, selected_season_number = None, selected_episode_number = None) -> List[StreamUrl]:
        episode_urls = []

        async with async_playwright() as p:
            browser = await p.webkit.launch(
                headless=True,  # Run in headless mode for better performance
            )
            page = await browser.new_page()
            await page.goto(url)
            await page.wait_for_timeout(3000)  # Wait for the page to load completely
            
            if await page.evaluate("document.querySelector('h1.title')") is not None:
                title = await page.text_content("h1.title")
            elif await page.evaluate("document.querySelector('.logo-image')") is not None:
                title = await page.get_attribute(".logo-image", "alt")
            
            if await page.evaluate("document.querySelector('.buttons a.play2')") is not None:
                episode_urls = await self._fetch_episode_urls_with_tt_season(
                    page,
                    title,
                    selected_season_number=selected_season_number,
                    selected_episode_number=selected_episode_number
                )
            elif await page.evaluate("document.querySelector('a.play')") is not None:
                episode_urls = await self._fetch_episode_urls_with_vixcloud(
                    page,
                    title,
                    selected_season_number=selected_season_number,
                    selected_episode_number=selected_episode_number
                )
            
            await browser.close()
        
        return episode_urls
    
    async def _fetch_episode_urls_with_vixcloud(
            self,
            page,
            title: str,
            selected_season_number: Optional[int] = None,
            selected_episode_number: Optional[int] = None
    ):
        captured_urls = []
        
        async def handle_request(request):
            url = request.url
            
            if (
                "/playlist/" in url
                and not "type=" in url
                ):
                captured_urls.append(url)
        page.on("request", handle_request)

        # count .episodes-tab select option
        seasion_count = await page.evaluate(
            "document.querySelectorAll('.episodes-tab select option').length"
        )

        episode_urls: List[StreamUrl] = []

        base_url = page.url

        for season_number in range(1, seasion_count + 1):

            season_url = f"{base_url}/season-{season_number}"

            episode_number = 0
            while True:
                episode_number += 1
                
                await page.goto(season_url)
                await page.wait_for_timeout(3000)  # Wait for the page to load completely

                episode_selector = '.episodes-tab a'
                episode_number_selector = '.episodes-tab a .number'
                right_scroll_selector = '.episodes-tab .slide-right'

                scroll_number = math.ceil(episode_number / 5)
                await page.wait_for_timeout(3000)

                for _ in range(scroll_number):
                    # take a screenshot of the page
                    # screenshot_path = f"/app/scroll_{_}.png"
                    # await self.page.screenshot(path=screenshot_path, full_page=True)
                    
                    # Check if the right scroll button exists before clicking
                    scroll_button_exists = await page.evaluate(
                        f"document.querySelector('{right_scroll_selector}') !== null"
                    )
                    
                    if scroll_button_exists:
                        # Click the right scroll button to load more episodes
                        await page.evaluate(f"document.querySelector('{right_scroll_selector}').click()")
                        await page.wait_for_timeout(2000)
                    else:
                        # No more episodes to scroll, break the loop
                        break
                
                episode_numbers = await page.evaluate(
                        f"""
                        Array.from(document.querySelectorAll('{episode_number_selector}')).map(el => el.textContent.trim())
                        """
                    )
                episode_numbers = [int(num) for num in episode_numbers if num.isdigit()]
                try:
                    episode_index = episode_numbers.index(episode_number)
                except ValueError:
                    # If the episode number is not found, skip to the next season
                    break

                season_url = page.url
                episode_url = season_url 

                retry = 3
                captured_urls = []

                while season_url == episode_url:
                    
                    await page.evaluate(f'document.querySelectorAll(".episodes-tab a")[{episode_index}].click()')
                    await page.wait_for_timeout(2000)
                    episode_url = page.url
                    retry -= 1
                    if retry <= 0:
                        raise EpisodeNotFoundException(f"Failed to select episode {episode_number} after multiple attempts")

                total_wait_time = 0
                while total_wait_time < 7000:
                    if any("lang=" in url for url in captured_urls):
                        break
                    await page.wait_for_timeout(500)
                    total_wait_time += 500

                # make captured_urls unique
                captured_urls = list(set(captured_urls))
                captured_urls.sort(key=lambda url: "lang=" not in url)

                if len(captured_urls) > 0:
                    stream_url = StreamUrl(
                        url=captured_urls[0],
                        title=title,
                        season_number=int(season_number),
                        episode_number=int(episode_number)
                    )

                    add_episode = True
                    if (selected_season_number is not None 
                        and season_number != selected_season_number):
                        add_episode = False
                    
                    if (selected_episode_number is not None 
                        and episode_number != selected_episode_number):
                        add_episode = False

                    if add_episode:
                        episode_urls.append(stream_url)
                        
                        # if both season and episode are selected, break, we found the episode
                        if (selected_season_number is not None 
                            and selected_episode_number is not None):
                            break
        
        return episode_urls

    async def _fetch_episode_urls_with_tt_season(
            self,
            page,
            title: str,
            selected_season_number: Optional[int] = None,
            selected_episode_number: Optional[int] = None
        ):

        # Set up request handler to capture streaming URLs
        captured_urls = []
        
        async def handle_request(request):
            url = request.url

            if "master.m3u8" in url:
                captured_urls.append(url)
        page.on("request", handle_request)
                
        await page.click(".buttons a.play2")
            
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

        return episode_urls
