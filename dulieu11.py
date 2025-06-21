import threading
import time
import string
from zlapi import ZaloAPI, ThreadType, Message
from config import API_KEY, SECRET_KEY, IMEI, SESSION_COOKIES
from collections import defaultdict

class Bot(ZaloAPI):
    def __init__(self, api_key, secret_key, imei=None, session_cookies=None):
        super().__init__(api_key, secret_key, imei, session_cookies)
        self.running = False

    def fetchGroupInfo(self):
        try:
            all_groups = self.fetchAllGroups()
            group_list = []
            for group_id, _ in all_groups.gridVerMap.items():
                group_info = super().fetchGroupInfo(group_id)
                group_name = group_info.gridInfoMap[group_id]["name"]
                group_list.append({'id': group_id, 'name': group_name})
            return group_list
        except Exception as e:
            print(f"Lỗi khi lấy danh sách nhóm: {e}")
            return []

    def display_group_menu(self):
        groups = self.fetchGroupInfo()
        if not groups:
            print("Không tìm thấy nhóm nào.")
            return None

        grouped = defaultdict(list)
        for group in groups:
            first_char = group['name'][0].upper()
            if first_char not in string.ascii_uppercase:
                first_char = '#'
            grouped[first_char].append(group)

        print("\nDanh sách các nhóm:")
        index_map = {}
        idx = 1
        for letter in sorted(grouped.keys()):
            print(f"\nNhóm {letter}:")
            for group in grouped[letter]:
                print(f"{idx}. {group['name']} (ID: {group['id']})")
                index_map[idx] = group['id']
                idx += 1
        return index_map

    def select_group(self):
        index_map = self.display_group_menu()
        if not index_map:
            return None
        while True:
            try:
                choice = int(input("Nhập số thứ tự của nhóm: ").strip())
                if choice in index_map:
                    return index_map[choice]
                print("Số không hợp lệ.")
            except ValueError:
                print("Vui lòng nhập số hợp lệ.")

    def send_reo_input(self, thread_id):
        self.running = True
        print("\n✅ Bắt đầu gửi tin nhắn.")
        print("Gõ nội dung và nhấn Enter để gửi.")
        print("Gõ `exit` để dừng.\n")

        def input_loop():
            while self.running:
                try:
                    user_input = input("> ").strip()
                    if user_input.lower() == 'exit':
                        self.stop_sending()
                        break
                    if user_input:
                        message = Message(text=user_input)
                        self.send(message, thread_id=thread_id, thread_type=ThreadType.GROUP)
                        print("✅ Đã gửi.")
                except Exception as e:
                    print(f"❌ Lỗi khi gửi: {e}")

        thread = threading.Thread(target=input_loop)
        thread.daemon = True
        thread.start()

        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_sending()

    def stop_sending(self):
        self.running = False
        print("⛔ Đã dừng gửi tin nhắn.")

def run_tool():
    print("TOOL GỬI NỘI DUNG TRỰC TIẾP KHÔNG TAG - KHÔNG DELAY")
    print("[1] Gửi nội dung trực tiếp vào nhóm")
    print("[0] Thoát")
    choice = input("Nhập lựa chọn: ").strip()

    if choice != '1':
        print("Đã thoát tool.")
        return

    client = Bot(API_KEY, SECRET_KEY, IMEI, SESSION_COOKIES)
    thread_id = client.select_group()
    if not thread_id:
        return

    client.send_reo_input(thread_id=thread_id)

if __name__ == "__main__":
    run_tool()
