from flask import Flask, render_template, request
from playwright.sync_api import sync_playwright, TimeoutError
import threading
import random
from urllib.parse import urlparse

app = Flask(__name__)

# Keep the original simulation function
def run_simulation(search_term="", proxy_server=None, user_agent=None, latitude=None, longitude=None, business_name=None, dwell_time=10):
    """
    Launches a browser, navigates to Google, and performs a search.
    Args:
        search_term (str): The term to search for.
        proxy_server (str, optional): The URL of the proxy server. Defaults to None.
        user_agent (str, optional): The user agent to use. Defaults to None.
        latitude (float, optional): The latitude for geolocation spoofing. Defaults to None.
        longitude (float, optional): The longitude for geolocation spoofing. Defaults to None.
        business_name (str, optional): The exact name of the business to find. Defaults to None.
        dwell_time (int, optional): Time in seconds to stay on the website. Defaults to 10.
    """
    print(f"Simulation started for term: '{search_term}', business: '{business_name}'", flush=True)
    try:
        with sync_playwright() as p:
            launch_options = {
                'headless': True,
                'args': ['--no-sandbox']
            }
            if proxy_server:
                launch_options['proxy'] = {
                    'server': proxy_server
                }

            browser = p.chromium.launch(**launch_options)

            # Create a new browser context with the specified user agent and geolocation
            context_options = {}
            if user_agent:
                context_options['user_agent'] = user_agent

            if latitude is not None and longitude is not None:
                # Ensure values are floats
                try:
                    lat = float(latitude)
                    lon = float(longitude)
                    context_options['geolocation'] = {'latitude': lat, 'longitude': lon}
                    context_options['permissions'] = ['geolocation']
                except (ValueError, TypeError):
                    print(f"Invalid latitude or longitude provided: ({latitude}, {longitude}). Skipping geolocation.", flush=True)

            context = browser.new_context(**context_options)
            page = context.new_page()

            page.goto("https://www.google.com/maps")
            print("Navigated to Google Maps.", flush=True)

            # Search on Google Maps
            try:
                search_box = page.locator('input[id="searchboxinput"]')
                search_box.fill(search_term)
                search_box.press('Enter')
                print(f"Searched for '{search_term}' on Google Maps.", flush=True)
            except Exception as e:
                print(f"Error searching on Google Maps: {e}", flush=True)
                browser.close()
                return

            # Wait for search results to appear in the side panel
            try:
                print("Waiting for search results panel...", flush=True)
                page.screenshot(path="debug_after_search.png")

                # Use a more general selector for the results container
                results_container_selector = 'div[aria-label*="Results for"]'
                try:
                    page.wait_for_selector(results_container_selector, timeout=15000)
                    print("Search results container loaded.", flush=True)
                except Exception:
                    print("Could not find primary search results container, trying fallback.", flush=True)
                    page.wait_for_selector('div[role="main"]', timeout=15000)
                    print("Fallback search results container loaded.", flush=True)

                page.screenshot(path="debug_after_results_loaded.png")

                # Find the specific business
                print(f"Searching for business: {business_name}", flush=True)

                # Get all result containers
                results = page.locator("div.Nv2PK").all()
                print(f"Found {len(results)} potential business listings.", flush=True)

                business_found = False
                for i, result in enumerate(results):
                    print(f"Checking result {i+1}...", flush=True)
                    try:
                        # Save HTML and screenshot for each result for debugging
                        with open(f"debug_result_{i+1}.html", "w", encoding="utf-8") as f:
                            f.write(result.inner_html())
                        result.screenshot(path=f'debug_result_{i+1}.png')

                        result_text = result.inner_text()
                        # Simple, robust check
                        if business_name and business_name.lower() in result_text.lower():
                            print(f"Found business '{business_name}' in result {i+1}. Clicking it.", flush=True)
                            result.click(timeout=5000)
                            business_found = True
                            break
                    except Exception as e:
                        print(f"Could not check or click result {i+1}: {e}", flush=True)

                if not business_found:
                    print(f"Could not find business '{business_name}' in the search results.", flush=True)
                    # No need to save the full page again if we have the snippets
                    # page.screenshot(path="maps_debug_page_not_found.png")
                    # with open("maps_debug_page.html", "w", encoding="utf-8") as f:
                    #     f.write(page.content())
                    browser.close()
                    return

            except Exception as e:
                print("Search results panel or business did not load in time.", flush=True)
                try:
                    html_content = page.content()
                    with open("maps_debug_page.html", "w", encoding="utf-8") as f:
                        f.write(html_content)
                    print("Saved Maps search results page HTML to maps_debug_page.html", flush=True)
                except Exception as e:
                    print(f"Could not save Maps debug HTML: {e}", flush=True)
                browser.close()
                return

            page.wait_for_load_state('networkidle')

            # Click the "Directions" button
            try:
                print("Finding and clicking 'Directions' button...", flush=True)
                directions_button = page.locator('button[data-value="Directions"]')
                directions_button.click(timeout=5000)
                print("'Directions' button clicked.", flush=True)
                page.wait_for_timeout(2000) # Wait for any animations
            except TimeoutError:
                print("Could not find 'Directions' button.", flush=True)
                # This might not be a critical failure, so we can continue.

            # Click the "Website" button and handle the new tab
            try:
                print("Finding and clicking 'Website' button...", flush=True)
                # Start waiting for the new page before clicking
                with context.expect_page() as new_page_info:
                    website_button = page.locator('a[data-value="Website"]')
                    website_button.click(timeout=5000)

                website_page = new_page_info.value
                print(f"New tab opened for website: {website_page.url}", flush=True)
                website_page.bring_to_front()
                # Now 'website_page' is the active page for the next steps

            except TimeoutError:
                print("Could not find 'Website' button.", flush=True)
                browser.close()
                return

            # --- On-site Engagement ---
            print(f"Starting engagement on {website_page.url}...", flush=True)
            website_page.wait_for_load_state('networkidle', timeout=15000)

            # Scroll down the page
            for _ in range(3):
                website_page.evaluate("window.scrollBy(0, window.innerHeight)")
                website_page.wait_for_timeout(1000)

            # Click a random internal link
            try:
                # Get the base URL to identify internal links
                base_url = urlparse(website_page.url).netloc
                internal_links = website_page.locator(f'a[href*="{base_url}"]').all()

                if internal_links:
                    random_link = random.choice(internal_links)
                    print(f"Clicking random internal link: {random_link.get_attribute('href')}", flush=True)
                    random_link.click()
                    website_page.wait_for_load_state('networkidle')
                else:
                    print("No internal links found to click.", flush=True)

            except Exception as e:
                print(f"Could not click a random link: {e}", flush=True)

            # Dwell time
            dwell_ms = int(dwell_time) * 1000
            print(f"Dwelling on site for {dwell_time} seconds...", flush=True)
            website_page.wait_for_timeout(dwell_ms)

            website_page.screenshot(path="final_page.png")
            print("Final screenshot saved.", flush=True)

            browser.close()
            print("Simulation finished.", flush=True)
    except Exception as e:
        print(f"An error occurred during simulation: {e}", flush=True)


@app.route('/')
def index():
    """Renders the main dashboard page."""
    return render_template('index.html')

@app.route('/run-simulation', methods=['POST'])
def start_simulation_route():
    """Triggers the simulation in a background thread."""
    data = request.get_json()
    search_term = data.get('search_term', 'Default Search Term')
    proxy_server = data.get('proxy_server', None)
    user_agent = data.get('user_agent', None)
    latitude = data.get('latitude', None)
    longitude = data.get('longitude', None)
    business_name = data.get('business_name', None)
    dwell_time = data.get('dwell_time', 10)

    print(f"Received request to start simulation for business: '{business_name}'")

    # Pass all arguments to the simulation function
    simulation_thread = threading.Thread(target=run_simulation, args=(search_term, proxy_server, user_agent, latitude, longitude, business_name, dwell_time))
    simulation_thread.start()

    return f"Simulation started for '{search_term}'!"

if __name__ == '__main__':
    # Running in debug mode is fine for development.
    # Host='0.0.0.0' makes it accessible from the local network.
    # use_reloader=False is important for background threads to work correctly with Flask's debugger
    app.run(debug=True, host='0.0.0.0', port=5001, use_reloader=False)
