from flask import Flask, jsonify, request
from flask_cors import CORS
import speedtest
import traceback
import logging

app = Flask(__name__)
CORS(app)

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Initialize global variables for average speeds and count
avg_download_speed = 0.0
avg_upload_speed = 0.0
test_count = 0

@app.route('/test_speed', methods=['GET'])
def test_speed():
    global avg_download_speed, avg_upload_speed, test_count

    try:
        st = speedtest.Speedtest()
        
        # Perform speed tests
        st.download()
        st.upload()

        # Get additional details
        st.get_best_server()

        download_speed = st.results.download / 10**6  # Convert to Mbps
        upload_speed = st.results.upload / 10**6  # Convert to Mbps
        server_name = st.results.server['name']
        server_country = st.results.server['country']
        server_host = st.results.server['host']
        server_ping = st.results.ping

        # Update average speeds
        avg_download_speed = (avg_download_speed * test_count + download_speed) / (test_count + 1)
        avg_upload_speed = (avg_upload_speed * test_count + upload_speed) / (test_count + 1)
        test_count += 1

        # Get user's internal IP address
        user_ip = request.remote_addr

        # Log all details after successful test
        logging.info(f"Download Speed: {download_speed} Mbps")
        logging.info(f"Upload Speed: {upload_speed} Mbps")
        logging.info(f"Server Name: {server_name}")
        logging.info(f"Server Country: {server_country}")
        logging.info(f"Server Host: {server_host}")
        logging.info(f"Server Ping: {server_ping}")
        logging.info(f"User Internal IP: {user_ip}")

        return jsonify({
            'download': round(download_speed, 2),
            'upload': round(upload_speed, 2),
            'server_name': server_name,
            'server_country': server_country,
            'server_host': server_host,
            'server_ping': server_ping,
            'user_internal_ip': user_ip,
            'average_download': round(avg_download_speed, 2),
            'average_upload': round(avg_upload_speed, 2),
            'test_count': test_count
        })

    except Exception as e:
        logging.error(f"Error in speed test: {e}")
        traceback.print_exc()  # Print traceback for debugging
        return jsonify({
            'error': str(e)
        }), 500  # Internal Server Error

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
