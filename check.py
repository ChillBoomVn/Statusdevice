from flask import Flask, abort, flash, jsonify, redirect, url_for, render_template, request, session
from datetime import datetime, timedelta, timezone
from flask_sqlalchemy import SQLAlchemy
from os import path

from sqlalchemy import func
app = Flask(__name__)  # Khởi tạo đối tượng Flask
app.config["SECRET_KEY"] = "asdfghjkl"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///status.db"
db = SQLAlchemy(app)

# Model để lưu dữ liệu
class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    deviceID = db.Column(db.String(100))
    cpu = db.Column(db.String(100))
    ram = db.Column(db.String(100))
    cpuTemp = db.Column(db.String(100))
    ticket_id = db.Column(db.String(100))
    detect_in = db.Column(db.String(100))
    uptime = db.Column(db.String(100))
    db_size = db.Column(db.String(100))
    IP = db.Column(db.String(100))
    MAC = db.Column(db.String(100))
    note = db.Column(db.String(100))
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
def __init__(self, deviceID,cpu,ram,cpuTemp,ticket_id,uptime,db_size,IP,MAC,note,updated_at):
        self.deviceID = deviceID
        self.cpu = cpu
        self.ram = ram
        self.cpuTemp = cpuTemp
        self.ticket_id = ticket_id
        self.uptime = uptime
        self.db_size = db_size
        self.IP = IP
        self.MAC = MAC
        self.note = note
        self.updated_at = updated_at

@app.route('/device_records/<deviceID>', methods=['GET'])
def get_device_records(deviceID):
    # Truy vấn để lấy tất cả các bản ghi cho deviceID cụ thể
    records = Data.query.filter_by(deviceID=deviceID).order_by(Data.updated_at.desc()).all()

    # Nếu không có bản ghi nào, trả về thông báo lỗi
    if not records:
        return jsonify({"error": "No records found for the given deviceID"}), 404

    # Chuyển đổi các bản ghi thành danh sách từ điển
    records_list = [
        {
            "deviceID": record.deviceID,
            "cpu": record.cpu,
            "ram": record.ram,
            "cpuTemp": record.cpuTemp,
            "ticket_id": record.ticket_id,
            "detect_in": record.detect_in,
            "uptime": record.uptime,
            "db_size": record.db_size,
            "IP": record.IP,
            "MAC": record.MAC,
            "note": record.note,
            "updated_at": record.updated_at.strftime('%H:%M %d-%m-%Y')
        }
        for record in records
    ]

    return jsonify(records_list)

# @app.route('/')
# def home():
#     # Truy vấn bản ghi có thời gian updated_at mới nhất
#     all_data = Data.query.order_by(Data.updated_at.desc()).first()
#     # all_data = Data.query.order_by()
#     return render_template('home.html', data=all_data)

@app.route('/')
def latest_records():
     # Lấy số trang từ query parameters (mặc định là 1 nếu không có)
    page = request.args.get('page', 1, type=int)

    # Truy vấn để lấy bản ghi mới nhất cho mỗi deviceID
    subquery = db.session.query(
        Data.deviceID,
        func.max(Data.updated_at).label('latest_update')
    ).group_by(Data.deviceID).subquery()

    latest_records_query = db.session.query(Data).join(
        subquery,
        (Data.deviceID == subquery.c.deviceID) &
        (Data.updated_at == subquery.c.latest_update)
    )

    # Thực hiện phân trang với mỗi trang có 50 bản ghi
    pagination = latest_records_query.paginate(page=page, per_page=50)

    # Truyền các giá trị cần thiết đến template
    return render_template('home.html', items=pagination.items, pagination=pagination)
   
@app.route("/logout")
def log_out():
    session.pop("user", None)
    return redirect(url_for("home"))

@app.route("/add_data", methods=["POST", "GET"])
def add_data():
    if request.method == "POST":
        # Lấy dữ liệu từ POST request
        deviceID = request.form.get('deviceID')
        cpu = request.form.get('cpu')
        ram = request.form.get('ram')
        cpuTemp = request.form.get('cpuTemp')
        ticket_id = request.form.get('ticket_id')
        detect_in = request.form.get('detect_in')
        uptime = request.form.get('uptime')
        db_size = request.form.get('db_size')
        IP = request.form.get('IP')
        MAC = request.form.get('MAC')
        note = request.form.get('note')

        # Kiểm tra xem có dữ liệu với deviceID này trong cơ sở dữ liệu hay không
        existing_data = Data.query.filter_by(deviceID=deviceID).first()
        if existing_data:
            flash(f"ID {deviceID} already exists! Data not added.")
            return render_template('add.html')  # Hiển thị lại trang 'add.html' với thông báo lỗi

        # Nếu deviceID không tồn tại, thêm dữ liệu mới
        new_data = Data(deviceID=deviceID, cpu=cpu, ram=ram, cpuTemp=cpuTemp,
                        ticket_id=ticket_id, detect_in=detect_in, uptime=uptime,
                        db_size=db_size, IP=IP, MAC=MAC, note=note)
        db.session.add(new_data)
        db.session.commit()

        flash("Data added successfully!")
        session.permanent = True
        session["user"] = deviceID

        return redirect(url_for('home'))  # Chuyển hướng về trang chủ
    return render_template("add.html")

#ADD device từ postman
@app.route('/device_info', methods=['POST'])
def add_device_info():
    try:
        # Lấy dữ liệu từ yêu cầu POST
        data = request.get_json(force=True)
        if not data:
            return jsonify({"error": "No JSON data received"}), 400

        # # Kiểm tra xem deviceID đã tồn tại trong cơ sở dữ liệu chưa
        # existing_device = Data.query.filter_by(deviceID=data.get('deviceID')).first()
        # if existing_device:
        #     return jsonify({"error": "DeviceID already exists!"}), 400

        # Tạo đối tượng DeviceInfo từ dữ liệu POST
        new_device = Data(
            deviceID=data.get('deviceID'),
            cpu=data.get('cpu'),
            ram=data.get('ram'),
            cpuTemp=data.get('cpuTemp'),
            ticket_id=data.get('ticket_id'),
            detect_in=data.get('detect_in'),
            uptime=data.get('uptime'),
            db_size=data.get('db_size'),
            IP=data.get('IP'),
            MAC=data.get('MAC'),
            note=data.get('note')
        )

        # Thêm đối tượng vào session và commit để lưu vào database
        db.session.add(new_device)
        db.session.commit()
        return jsonify({"message": "Device info added successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
    
# Hàm lấy thông tin của một hàng dựa trên ID
@app.route('/api/get_data/id=<int:data_id>', methods=['POST'])
def get_data(data_id):
    # Truy vấn cơ sở dữ liệu để lấy hàng với ID cụ thể
    data = Data.query.get(data_id)
    
    if data is None:
        # Nếu không tìm thấy, trả về mã lỗi 404
        response = {
             abort(404, description=f"Data with ID {data_id} not found.")   
        }
    
    # Nếu tìm thấy, trả về thông tin dưới dạng JSON
    response = {
        'DeviceID': data.diviceID,
        'CPU': data.name,
        'ram': data.cpu,
        'CpuTemp': data.temp,
        'ticket_id': data.mac,
        'detect_in': data.ip,
        'uptime': data.status,
        'db_size': data.db_size,
        'IP': data.status,
        'MAC': data.status,
        'note': data.status
    }
    
    return jsonify(response), 200  # Trả về dữ liệu với mã trạng thái HTTP 200 (OK)


if __name__ == "__main__":
    # Kiểm tra xem file status.db đã tồn tại hay chưa
    if not path.exists("status.db"):
        with app.app_context():  # Tạo ngữ cảnh ứng dụng
            db.create_all()  # Tạo tất cả các bảng trong cơ sở dữ liệu
            print("Created database!")
    else:
        print("Database already exis  ts. Skipping creation.")

    app.run(host='0.0.0.0', port=2000, debug=True)
    
    
    
