from flask import Flask, request
import threading
import time

def get_access_token_from_redirect(port=8080, route_path='/oauth', parameter_name='code'):
    app = Flask(__name__)
    access_token = None
    server_thread = None
    token_captured = threading.Event()

    @app.route(route_path)
    def oauth_callback():
        nonlocal access_token
        token_value = request.args.get(parameter_name)
        if token_value:
            access_token = token_value
            token_captured.set()
            return f"<h1>Access Token Captured!</h1><p>You may now close this page.</p>"
        else:
            return "<h1>Error: No access token found in the redirect URL.</h1>"

    def run_server():
        app.run(port=port, debug=False, use_reloader=False)

    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

    print(f"Starting local web server on http://localhost:{port}{route_path}...")

    token_captured.wait()

    print("\nAccess Token successfully captured!")

    return access_token

if __name__ == '__main__':
    print("Starting default test:")
    captured_token = get_access_token_from_redirect()

    if captured_token:
        print(f"\nCaptured Access Token: {captured_token}")
    else:
        print("\nFailed to capture access token.")

    print("\n\nExample with custom port, route, and parameter name:")
    custom_token = get_access_token_from_redirect(port=8081, route_path='/callback', parameter_name='token')
    if custom_token:
        print(f"\nCaptured Custom Token: {custom_token}")
    else:
        print("\nFailed to capture custom token.")

    print("\n\nTo test, open a browser and go to:")
    print("http://localhost:8080/oauth?code=YOUR_ACCESS_CODE  (for default test)")
    print("http://localhost:8081/callback?token=YOUR_CUSTOM_TOKEN (for custom test)")
    print("Replace YOUR_ACCESS_CODE and YOUR_CUSTOM_TOKEN with actual values.")