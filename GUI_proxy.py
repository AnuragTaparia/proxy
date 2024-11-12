import tkinter as tk
from tkinter import messagebox
from mitmproxy import http, options
from mitmproxy.tools.dump import DumpMaster
from urllib.parse import urlparse, parse_qs
import asyncio
import threading

class InterceptURLs:
    search_query_params = ["q", "query", "search"]

    def __init__(self, blocked_keywords):
        # Initialize with a list of blocked keywords (case-insensitive)
        self.blocked_keywords = [keyword.lower() for keyword in blocked_keywords]

    def add_keywords(self, keywords):
        # Add new keywords to the list dynamically
        self.blocked_keywords.extend(keyword.lower() for keyword in keywords)

    def request(self, flow: http.HTTPFlow):
        # Get the full URL from the request
        url = flow.request.pretty_url

        # Parse the URL to extract components
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)

        # Convert netloc and path to lowercase for case-insensitive matching
        netloc_and_path_lower = (parsed_url.netloc + parsed_url.path).lower()

        # Check if the URL contains any of the blocked keywords (case-insensitive)
        contains_blocked_keyword = any(keyword in netloc_and_path_lower for keyword in self.blocked_keywords)

        # Check if the URL contains common search parameters
        is_search_query = any(param in query_params for param in self.search_query_params)

        # Block the URL if it contains blocked keywords and is not a search query
        if contains_blocked_keyword and not is_search_query:
            # Respond with a custom error message (e.g., 403 Forbidden)
            flow.response = http.Response.make(
                403,  # Status code for Forbidden
                b"Access to this website is blocked due to restricted content.",  # Custom message
                {"Content-Type": "text/html"}  # Headers
            )
            print(f"Blocked access to: {url}")
        else:
            # Allow the request to proceed
            print(f"Connecting to: {url}")

class ProxyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("URL Blocker Configuration")
        self.proxy_thread = None
        self.intercept_addon = None

        # Label and entry for blocked keywords
        label = tk.Label(root, text="Enter blocked keywords (comma-separated):")
        label.pack(pady=10)

        self.entry = tk.Entry(root, width=50)
        self.entry.pack(pady=5)

        # Start button to launch the proxy with specified keywords
        start_button = tk.Button(root, text="Start Proxy", command=self.start_proxy)
        start_button.pack(pady=10)

        # Update button to add keywords while proxy is running
        update_button = tk.Button(root, text="Update Keywords", command=self.update_keywords)
        update_button.pack(pady=10)

    def start_proxy(self):
        blocked_keywords_input = self.entry.get()
        if not blocked_keywords_input:
            messagebox.showerror("Error", "Please enter at least one keyword.")
            return

        # Process keywords into a list
        blocked_keywords = [keyword.strip() for keyword in blocked_keywords_input.split(",")]

        # Start the proxy in a separate thread to avoid blocking the GUI
        self.proxy_thread = threading.Thread(target=self.run_mitmproxy, args=(blocked_keywords,))
        self.proxy_thread.daemon = True
        self.proxy_thread.start()

    def update_keywords(self):
        # Add new keywords from the entry box to the running proxy
        new_keywords = [keyword.strip() for keyword in self.entry.get().split(",")]
        if self.intercept_addon:
            self.intercept_addon.add_keywords(new_keywords)
            messagebox.showinfo("Success", "Keywords updated successfully!")
        else:
            messagebox.showerror("Error", "Proxy is not running. Start the proxy first.")

    def run_mitmproxy(self, blocked_keywords):
        asyncio.run(self.run_proxy_async(blocked_keywords))

    async def run_proxy_async(self, blocked_keywords):
        # Configure mitmproxy options
        opts = options.Options(listen_host='127.0.0.1', listen_port=8080)
        m = DumpMaster(opts)
        self.intercept_addon = InterceptURLs(blocked_keywords)
        
        # Add the intercept addon to mitmproxy
        m.addons.add(self.intercept_addon)

        try:
            # Run mitmproxy until the program is closed
            await m.run()
        except KeyboardInterrupt:
            print("Stopping proxy...")
            m.shutdown()

# Set up tkinter window
root = tk.Tk()
app = ProxyApp(root)
root.mainloop()
