from flask import Flask, render_template, request
from playwright.sync_api import sync_playwright
import threading

app = Flask(__name__)

# Keep the original simulation function
def run_simulation(search_term=""):
    """
    Launches a browser, navigates to Google, and performs a search.
    Args:
        search_term (str): The term to search for.
    """
    print(f"Simulation started for search term: '{search_term}'")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
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

    print(f"Received request to start simulation with term: '{search_term}'")

    # Pass the search term to the simulation function
    simulation_thread = threading.Thread(target=run_simulation, args=(search_term,))
    simulation_thread.start()

    return f"Simulation started for '{search_term}'!"

if __name__ == '__main__':
    # Running in debug mode is fine for development.
    # Host='0.0.0.0' makes it accessible from the local network.
    app.run(debug=True, host='0.0.0.0', port=5001)
