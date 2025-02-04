from flask import Flask, request, jsonify, render_template
import paho.mqtt.publish as publish
import json

app = Flask(__name__)

# Địa chỉ IP của MQTT Broker
MQTT_BROKER = "192.168.0.100"  # Thay thế bằng địa chỉ IP của MQTT Broker của bạn


@app.route('/')
def index():
    return render_template('index1.html')  # Lấy trang HTML


@app.route('/send', methods=['POST'])
def send_message():
    data = request.json
    message = data.get("message")
    if not message:
        return jsonify({"error": "No message provided"}), 400

    try:
        # Chuyển đối tượng message thành chuỗi JSON
        message_json = json.dumps(message)

        # Gửi tin nhắn đến MQTT broker
        publish.single("MQTT_DongCo_DCs2", message_json, hostname=MQTT_BROKER)

        # Trả về phản hồi thành công
        return jsonify({"success": True, "message": "Message sent!"})

    except Exception as e:
        return jsonify({"error": f"Failed to send message: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)