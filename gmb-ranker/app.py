from flask import Flask, render_template, request
from playwright.sync_api import sync_playwright
import threading

app = Flask(__name__)

# Keep the original simulation function
def run_simulation(search_term="", proxy_server=None):
    """
    Launches a browser, navigates to Google, and performs a search.
    Args:
        search_term (str): The term to search for.
        proxy_server (str, optional): The URL of the proxy server. Defaults to None.
    """
    print(f"Simulation started for search term: '{search_term}' with proxy: '{proxy_server}'")
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
            page = browser.new_page()
            page.goto("https://www.google.com")

            search_bar = page.query_selector('textarea[name="q"]')
            if search_bar:
                search_bar.fill(search_term)
                page.press('textarea[name="q"]', 'Enter')
                print(f"Search submitted for '{search_term}'.")
            else:
                print("Search bar not found.")
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
    proxy_server = data.get('proxy_server', None) # Get the proxy server, default to None

    print(f"Received request to start simulation with term: '{search_term}' and proxy: '{proxy_server}'")

    # Pass both arguments to the simulation function
    simulation_thread = threading.Thread(target=run_simulation, args=(search_term, proxy_server))
    simulation_thread.start()

    return f"Simulation started for '{search_term}'!"

if __name__ == '__main__':
    # Running in debug mode is fine for development.
    # Host='0.0.0.0' makes it accessible from the local network.
    app.run(debug=True, host='0.0.0.0', port=5001)
