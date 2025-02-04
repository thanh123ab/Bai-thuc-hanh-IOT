import paho.mqtt.client as mqtt
import json
from flask import Flask, render_template, jsonify, request
from threading import Thread

app = Flask(__name__)

# Dữ liệu ban đầu là một biến toàn cục, sẽ được cập nhật khi có tin nhắn MQTT
data = {}

BROKER = "192.168.0.100"
PORT = 1883
TOPIC = "MQTT_DongCo_DCs2"


# Hàm callback khi kết nối thành công
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Kết nối MQTT Broker thành công!")
        client.subscribe(TOPIC)  # Đăng ký lắng nghe topic
    else:
        print(f"Kết nối thất bại. Lỗi mã: {rc}")


# Hàm callback khi nhận tin nhắn
def on_message(client, userdata, msg):
    global data
    try:
        # Giải mã chuỗi JSON
        data = json.loads(msg.payload.decode())  # Cập nhật dữ liệu từ MQTT
        print(f"Nhận từ {msg.topic}: {data}")
    except json.JSONDecodeError:
        print("Không thể giải mã chuỗi JSON!")


# Tạo client MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message


# Kết nối tới broker
def start_mqtt():
    client.connect(BROKER, PORT, 60)
    client.loop_forever()  # Bắt đầu vòng lặp nhận tin nhắn


# Tạo thread chạy MQTT
mqtt_thread = Thread(target=start_mqtt)
mqtt_thread.daemon = True
mqtt_thread.start()


# API trả về dữ liệu JSON
@app.route('/data')
def get_data():
    return jsonify(data)


# API cập nhật tên thành viên
@app.route('/update_member', methods=['POST'])
def update_member():
    global data
    thanh_vien_1 = request.form.get('ThanhVien1')
    thanh_vien_2 = request.form.get('ThanhVien2')

    # Cập nhật dữ liệu thành viên
    if thanh_vien_1:
        data["ThanhVien1"] = thanh_vien_1
    if thanh_vien_2:
        data["ThanhVien2"] = thanh_vien_2

    # Gửi cập nhật qua MQTT
    client.publish(TOPIC, json.dumps(data))

    return jsonify({"success": True, "data": data})
@app.route('/send_mqtt', methods=['POST'])
def send_mqtt():
    global data
    message = request.form.get('message')  # Nhận dữ liệu từ textbox

    if message:
        # Gửi dữ liệu qua topic riêng
        topic = "MQTT_DongCo_DCs2"  # Topic riêng biệt cho dữ liệu
        client.publish(topic, json.dumps({"status": message}))

        # Cập nhật dữ liệu và trả về kết quả
        data["status"] = message
        return jsonify({"success": True, "data": data})
    else:
        return jsonify({"success": False, "error": "Không có dữ liệu gửi"})


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)