import requests
import time
from threading import Thread
import spotifyApp
app = None
def run_command():
    input()

    # Example: Send a POST request to pause playback
    response = requests.get('http://localhost:5000/pause')
    print(response)


# Example usage
if __name__ == '__main__':
    app = spotifyApp.app
    thread = Thread(target=run_command)
    thread.start()


    app.run(host='0.0.0.0')