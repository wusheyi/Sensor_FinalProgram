import threading
import time
from moto import MotorController
from ultrasonic import UltrasonicController

def monitor_gate(sensor_name, trig_pin, echo_pin, motor_pin):
    sensor = UltrasonicController(trig_pin, echo_pin, threshold_cm=30)
    motor = MotorController(motor_pin)
    has_opened = False  # 是否開門過
    leave_count = 0     # 離開計數器
    enter_count = 0    # 進入計數器

    try:
        print(f"[{sensor_name}] 啟動監測中...")
        while True:
            car_detected = sensor.check_for_car()

            if car_detected:
                leave_count = 0
                if not has_opened:
                    enter_count += 1
                    if enter_count >= 2:
                        print(f"[{sensor_name}] 進入次數：{enter_count}")
                        print(f"[{sensor_name}] 偵測到車輛 → 開啟柵欄")
                        print('輸出API到手機頁面要求拍照')
                        #如果接收回傳的，開門訊號再開門
                        motor.open_gate()
                        has_opened = True
            else:
                enter_count = 0
                if has_opened:
                    leave_count += 1
                    print(f"[{sensor_name}] 離開次數：{leave_count}")
                    if leave_count >= 2:
                        print(f"[{sensor_name}] 車輛離開確認 → 關閉柵欄")
                        motor.close_gate()
                        has_opened = False
                        leave_count = 0

            time.sleep(1)
    except KeyboardInterrupt:
        print(f"[{sensor_name}] 停止監測")
    finally:
        motor.destroy()
        sensor.cleanup()

if __name__ == "__main__":
    gate1 = threading.Thread(target=monitor_gate, args=("入口", 35, 37, 40))  # Ultrasonic 1 + Motor 1 {trig_pin, echo_pin, motor_pin}
    gate2 = threading.Thread(target=monitor_gate, args=("出口", 36, 38, 32))  # Ultrasonic 2 + Motor 2

    gate1.start()
    gate2.start()

    gate1.join()
    gate2.join()
