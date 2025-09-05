from flask import Flask, render_template, request
from playwright.sync_api import sync_playwright, TimeoutError
import threading

app = Flask(__name__)

# Keep the original simulation function
def run_simulation(search_term="", proxy_server=None, user_agent=None):
    """
    Launches a browser, navigates to Google, and performs a search.
    Args:
        search_term (str): The term to search for.
        proxy_server (str, optional): The URL of the proxy server. Defaults to None.
        user_agent (str, optional): The user agent to use. Defaults to None.
    """
    print(f"Simulation started for term: '{search_term}', proxy: '{proxy_server}', user_agent: '{user_agent}'")
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

            # Create a new browser context with the specified user agent
            context_options = {}
            if user_agent:
                context_options['user_agent'] = user_agent

            context = browser.new_context(**context_options)
            page = context.new_page()

            page.goto("https://www.google.com")

            # Handle potential cookie consent form
            try:
                print("Checking for cookie consent button...")
                accept_button = page.locator('button:has-text("Accept all")')
                accept_button.click(timeout=3000)
                print("Cookie consent button clicked.")
            except TimeoutError:
                print("Cookie consent button not found or timed out, continuing...")

            try:
                # Based on debug HTML, the correct selector is input[name="q"]
                search_bar_selector = 'input[name="q"]'
                search_bar = page.wait_for_selector(search_bar_selector, timeout=5000)
                search_bar.fill(search_term)
                page.press(search_bar_selector, 'Enter')
                print(f"Search submitted for '{search_term}'.")
            except TimeoutError:
                print("Search bar not found within the timeout period.")
                try:
                    html_content = page.content()
                    with open("debug_page.html", "w", encoding="utf-8") as f:
                        f.write(html_content)
                    print("Saved failing page HTML to debug_page.html")
                except Exception as e:
                    print(f"Could not save debug HTML: {e}")
                browser.close()
                return

            page.wait_for_load_state('networkidle')
            print("Navigated to search results.")

            browser.close()
            print("Simulation finished.")
    except Exception as e:
        print(f"An error occurred during simulation: {e}")


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
    user_agent = data.get('user_agent', None) # Get the user agent, default to None

    print(f"Received request to start simulation with term: '{search_term}', proxy: '{proxy_server}', user_agent: '{user_agent}'")

    # Pass all arguments to the simulation function
    simulation_thread = threading.Thread(target=run_simulation, args=(search_term, proxy_server, user_agent))
    simulation_thread.start()

    return f"Simulation started for '{search_term}'!"

if __name__ == '__main__':
    # Running in debug mode is fine for development.
    # Host='0.0.0.0' makes it accessible from the local network.
    app.run(debug=True, host='0.0.0.0', port=5001)
