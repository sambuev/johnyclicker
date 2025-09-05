from flask import Flask, render_template
from playwright.sync_api import sync_playwright
import threading

app = Flask(__name__)

# Keep the original simulation function
def run_simulation():
    # This function is long-running and will block the server.
    # We will need to run it in a separate thread in the future.
    print("Simulation started...")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
            page = browser.new_page()
            page.goto("https://www.google.com")

            search_bar = page.query_selector('textarea[name="q"]')
            if search_bar:
                search_bar.fill("Google My Business")
                page.press('textarea[name="q"]', 'Enter')
                print("Search submitted.")
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
    # The template 'index.html' will be created in the next step.
    return render_template('index.html')

@app.route('/run-simulation', methods=['POST'])
def start_simulation_route():
    """Triggers the simulation in a background thread."""
    print("Received request to start simulation.")
    simulation_thread = threading.Thread(target=run_simulation)
    simulation_thread.start()
    return "Simulation started successfully in the background!"

if __name__ == '__main__':
    # Running in debug mode is fine for development.
    # Host='0.0.0.0' makes it accessible from the local network.
    app.run(debug=True, host='0.0.0.0', port=5001)
