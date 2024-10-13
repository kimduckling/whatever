import openai
import json
from datetime import datetime, timedelta
import os
import matplotlib.pyplot as plt

# 유저가 직접 API 키를 입력하도록 요청
api_key = input("OpenAI API 키를 입력하세요: ")

# 입력받은 API 키 설정
openai.api_key = api_key

# API 키가 없으면 프로그램 실행 중단
if not openai.api_key:
    raise ValueError("API 키가 입력되지 않았습니다. 프로그램을 종료합니다.")

# AI 사용 여부 (무료 크레딧 소진 시 False로 설정)
ai_enabled = True

# 데이터를 저장할 파일 경로 (실행 파일의 경로 기준으로 절대 경로 생성)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 현재 파일의 절대 경로를 기준으로 설정
DATA_FILE = os.path.join(BASE_DIR, "contacts_data.json")

# 그룹 및 지인 데이터를 JSON 파일로 저장하는 함수
def save_data():
    try:
        data = {
            'groups': [{'name': group.name, 'contact_interval': group.contact_interval, 'tolerance': group.tolerance} for group in groups],
            'contacts': [{
                'name': contact.name,
                'group': contact.group.name,
                'birthday': contact.birthday,
                'gender': contact.gender,
                'residence': contact.residence,
                'hobbies': contact.hobbies,
                'additional_info': contact.additional_info,
                'last_contact_date': contact.last_contact_date.strftime("%Y-%m-%d %H:%M:%S") if contact.last_contact_date else None,
                'contact_history': contact.contact_history
            } for contact in contacts]
        }

        with open(DATA_FILE, 'w') as file:
            json.dump(data, file)
        print("데이터가 성공적으로 저장되었습니다.")
    
    except IOError as e:
        print(f"데이터 저장 중 오류 발생: {e}")

# 프로그램 시작 시 JSON 파일에서 데이터를 불러오는 함수
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as file:
                data = json.load(file)

            # 그룹 데이터를 불러오기
            for group_data in data['groups']:
                group = Group(group_data['name'], group_data['contact_interval'], group_data['tolerance'])
                groups.append(group)

            # 지인 데이터를 불러오기
            for contact_data in data['contacts']:
                group = next((g for g in groups if g.name == contact_data['group']), None)
                if group:
                    contact = Contact(
                        contact_data['name'], group, contact_data['birthday'],
                        contact_data['gender'], contact_data['residence'], contact_data['hobbies']
                    )
                    contact.additional_info = contact_data['additional_info']
                    if contact_data['last_contact_date']:
                        contact.last_contact_date = datetime.strptime(contact_data['last_contact_date'], "%Y-%m-%d %H:%M:%S")
                    contact.contact_history = contact_data['contact_history']
                    contacts.append(contact)
            print("데이터가 성공적으로 불러와졌습니다.")

        except (IOError, json.JSONDecodeError) as e:
            print(f"데이터 불러오기 중 오류 발생: {e}")
    else:
        print("데이터 파일이 존재하지 않습니다. 새로운 데이터를 생성합니다.")

# 프로그램 실행 시 데이터를 불러오기
load_data()

# 그룹 클래스
class Group:
    def __init__(self, name, contact_interval, tolerance):
        self.name = name  # 그룹 이름
        self.contact_interval = contact_interval  # 연락 주기 (일 기준)
        self.tolerance = tolerance  # 오차 범위 (일 기준)

# 지인 클래스
class Contact:
    def __init__(self, name, group, birthday, gender, residence, hobbies):
        self.name = name  # 지인 이름
        self.group = group  # 지인이 속한 그룹
        self.birthday = birthday  # 생일
        self.gender = gender  # 성별
        self.residence = residence  # 거주지
        self.hobbies = hobbies  # 취미
        self.additional_info = ""  # 추가 정보 (메모)
        self.last_contact_date = None  # 최근 연락 날짜
        self.contact_history = []  # 연락 기록 저장

    # 추가 정보를 입력하는 메소드
    def add_additional_info(self, info):
        self.additional_info = info

    # 최근 연락 날짜를 업데이트하는 메소드
    def update_last_contact_date(self):
        self.last_contact_date = datetime.now()

    # 대화 기록을 저장하는 메소드
    def add_conversation(self, date, topics):
        self.contact_history.append({
            'date': date,
            'topics': topics
        })

# 대화 기록 추가 함수
def record_conversation(contact):
    date = input("대화를 나눈 날짜를 입력하세요 (예: 2024-09-20): ")

    categories = ['일', '학업', '취미', '친목', '연애', '건강', '기타']
    conversation = {}

    # 카테고리별 대화 내용 및 중요도 입력
    for category in categories:
        discussed = input(f"'{category}'에 대한 이야기를 나눴습니까? (y/n): ").lower()
        if discussed == 'y':
            importance = int(input(f"'{category}'에 대한 중요도를 입력하세요 (1~5): "))
            details = input(f"'{category}'에 대한 대화 내용을 입력하세요: ")
            conversation[category] = {
                'importance': importance,
                'details': details
            }

    contact.add_conversation(date, conversation)
    print(f"대화 기록이 성공적으로 저장되었습니다!")

# 대화 기록 수정 함수
def edit_conversation():
    if not contacts:
        print("등록된 지인이 없습니다.")
        return
    
    # 지인 목록 표시
    print("대화 기록을 수정할 지인을 선택하세요:")
    for idx, contact in enumerate(contacts, start=1):
        print(f"[{idx}] {contact.name}")
    
    contact_choice = int(input("지인 번호를 선택하세요: ")) - 1
    contact = contacts[contact_choice]
    
    if not contact.contact_history:
        print(f"{contact.name}과의 대화 기록이 없습니다.")
        return
    
    # 대화 목록 표시
    print(f"\n{contact.name}과의 대화 기록 목록:")
    for idx, record in enumerate(contact.contact_history, start=1):
        print(f"[{idx}] 날짜: {record['date']}, 내용: {record['topics']}")
    
    conversation_choice = int(input("수정할 대화의 번호를 선택하세요: ")) - 1
    conversation = contact.contact_history[conversation_choice]
    
    # 대화 수정
    date = input(f"기존 날짜: {conversation['date']} (수정하지 않으려면 엔터를 누르세요): ").strip()
    if date:
        conversation['date'] = date

    for category, details in conversation['topics'].items():
        print(f"카테고리: {category}, 중요도: {details['importance']}, 내용: {details['details']}")
        new_importance = input(f"카테고리 '{category}'의 새로운 중요도를 입력하세요 (1~5) (수정하지 않으려면 엔터): ").strip()
        if new_importance:
            conversation['topics'][category]['importance'] = int(new_importance)
        
        new_details = input(f"카테고리 '{category}'의 새로운 내용을 입력하세요 (수정하지 않으려면 엔터): ").strip()
        if new_details:
            conversation['topics'][category]['details'] = new_details
    
    print("대화 기록이 성공적으로 수정되었습니다!")

# AI 대화 주제를 추천하는 함수
def suggest_conversation_topic(contact):
    global ai_enabled

    # AI 기능이 비활성화되었으면 대화 주제를 추천하지 않음
    if not ai_enabled:
        return None  # AI 기능 비활성화 시 None 반환

    # None 값이 있는 경우 기본 값을 사용하거나 메시지를 생략하는 방식으로 처리
    birthday = contact.birthday if contact.birthday else "모름"
    residence = contact.residence if contact.residence else "모름"
    hobbies = contact.hobbies if contact.hobbies else "모름"

    # 대화 기록에서 가장 최근 대화 또는 중요도가 높은 대화들을 가져오기
    recent_conversations = []
    if contact.contact_history:
        # 최근 3개의 대화를 가져오도록 설정 (필요에 따라 조정 가능)
        recent_conversations = sorted(contact.contact_history, key=lambda x: x['date'], reverse=True)[:3]

    # 대화 기록을 프롬프트에 추가
    conversation_summary = ""
    for conv in recent_conversations:
        conversation_summary += f"Date: {conv['date']}, Topics: {', '.join([f'{topic}: {details['importance']}' for topic, details in conv['topics'].items()])}. "

    if not conversation_summary:
        conversation_summary = "No recent conversations available."

    # AI에 전달할 메시지 생성
    messages = [
        {"role": "system", "content": "You are a helpful assistant that suggests conversation topics."},
        {"role": "user", "content": f"Generate a conversation topic for {contact.name}. They were born on {birthday}, they live in {residence}, and their hobbies include {hobbies}. Recent conversation history: {conversation_summary}. Additional notes: {contact.additional_info}."}
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=100
        )
        conversation_topic = response.choices[0].message['content'].strip()
        return conversation_topic
    except Exception as e:
        # API 호출 실패 시 AI 기능 비활성화
        print(f"AI 대화 주제 추천을 사용할 수 없습니다. (오류: {e})")
        ai_enabled = False
        return None

# 지인에게 연락할 때 대화 주제 추천을 포함하는 함수
def check_contact_due_with_topic(contact):
    if contact.last_contact_date is None:
        print(f"{contact.name}에게는 아직 연락한 기록이 없습니다.")
        return

    # 현재 날짜와 최근 연락 날짜의 차이 계산
    days_since_last_contact = (datetime.now() - contact.last_contact_date).days
    contact_interval = contact.group.contact_interval
    tolerance = contact.group.tolerance

    # 연락 주기와 오차 범위에 따른 알림 조건
    if contact_interval - tolerance <= days_since_last_contact <= contact_interval + tolerance:
        print(f"{contact.name}에게 연락할 때가 되었습니다! 마지막 연락으로부터 {days_since_last_contact}일 지났습니다.")
        
        # AI 대화 주제 추천
        if ai_enabled:
            topic = suggest_conversation_topic(contact)
            if topic:
                print(f"추천 대화 주제: {topic}")
            else:
                print("대화 주제 추천을 사용할 수 없습니다.")
        else:
            # AI 기능 비활성화 시 대화 주제 없이 단순 알림
            print("대화 주제 추천 기능이 비활성화되었습니다.")
    else:
        print(f"{contact.name}은 아직 연락할 시간이 되지 않았습니다. 현재 {days_since_last_contact}일 지났습니다.")

# 모든 지인에 대해 연락 주기를 체크하는 함수
def check_all_contacts_due():
    if not contacts:
        print("등록된 지인이 없습니다.")
        return
    for contact in contacts:
        check_contact_due_with_topic(contact)

# 대화 기록을 날짜별로 조회하는 함수
def view_conversations_by_date():
    search_date = input("확인하고 싶은 날짜를 입력하세요 (예: 2024-09-20): ")
    found = False
    for contact in contacts:
        for record in contact.contact_history:
            if record['date'] == search_date:
                print(f"\n[{contact.name}]와의 대화 기록 ({search_date}):")
                for category, details in record['topics'].items():
                    print(f"- {category}: 중요도 {details['importance']}, 내용: {details['details']}")
                found = True
    if not found:
        print("해당 날짜에 대한 기록이 없습니다.")

# 특정 지인의 대화 기록을 확인하는 함수
def view_conversations_by_contact():
    if not contacts:
        print("등록된 지인이 없습니다.")
        return
    for idx, contact in enumerate(contacts, start=1):
        print(f"[{idx}] {contact.name}")
    
    contact_choice = int(input("대화 기록을 확인할 지인의 번호를 선택하세요: ")) - 1
    contact = contacts[contact_choice]
    
    if not contact.contact_history:
        print(f"{contact.name}과(와)의 대화 기록이 없습니다.")
        return
    
    for record in contact.contact_history:
        print(f"\n날짜: {record['date']}")
        for category, details in record['topics'].items():
            print(f"- {category}: 중요도 {details['importance']}, 내용: {details['details']}")

# 지인의 최근 연락 날짜를 수동으로 업데이트하는 함수
def update_contact_date():
    if not contacts:
        print("등록된 지인이 없습니다.")
        return

    # 연락 날짜를 업데이트할 지인을 선택
    for idx, contact in enumerate(contacts, start=1):
        print(f"[{idx}] {contact.name}")
    
    contact_choice = int(input("최근 연락 날짜를 업데이트할 지인의 번호를 선택하세요: ")) - 1
    contact = contacts[contact_choice]

    # 새로운 날짜 입력
    new_date = input(f"{contact.name}의 새로운 최근 연락 날짜를 입력하세요 (예: 2024-09-20): ")
    try:
        contact.last_contact_date = datetime.strptime(new_date, "%Y-%m-%d")
        print(f"{contact.name}의 최근 연락 날짜가 {new_date}로 업데이트되었습니다.")
    except ValueError:
        print("잘못된 날짜 형식입니다. YYYY-MM-DD 형식으로 입력하세요.")

# 그룹 리스트
groups = []

# 그룹을 추가하는 함수 (에러 처리 포함)
def add_group():
    group_name = input("추가할 그룹의 이름을 입력하세요: ")
    
    # 숫자가 아닌 값이 입력될 경우에 대한 에러 처리
    while True:
        try:
            contact_interval = int(input("그룹의 연락 주기를 입력하세요 (일 기준): "))
            tolerance = int(input("그룹의 연락 주기에 대한 오차 범위를 입력하세요 (일 기준): "))
            break
        except ValueError:
            print("잘못된 입력입니다. 숫자를 입력하세요.")

    # 새로운 그룹 객체 생성
    group = Group(group_name, contact_interval, tolerance)
    
    # 그룹 리스트에 추가
    groups.append(group)
    print(f"{group_name} 그룹이 성공적으로 추가되었습니다!")

# 그룹 정보를 수정하는 함수
def edit_group():
    if not groups:
        print("수정할 그룹이 없습니다.")
        return
    
    # 수정할 그룹 선택
    print("수정할 그룹을 선택하세요:")
    for idx, group in enumerate(groups, start=1):
        print(f"[{idx}] {group.name} (연락 주기: {group.contact_interval}일, 오차 범위: {group.tolerance}일)")
    
    try:
        group_choice = int(input("그룹 번호를 입력하세요: ")) - 1
        if group_choice < 0 or group_choice >= len(groups):
            print("잘못된 선택입니다.")
            return
        group = groups[group_choice]
    except (ValueError, IndexError):
        print("잘못된 선택입니다.")
        return

    # 수정할 그룹 정보 입력
    new_name = input(f"그룹 이름을 수정하세요 (현재: {group.name}) [비워두면 수정하지 않음]: ").strip()
    new_contact_interval = input(f"연락 주기를 수정하세요 (현재: {group.contact_interval}) [비워두면 수정하지 않음]: ").strip()
    new_tolerance = input(f"오차 범위를 수정하세요 (현재: {group.tolerance}) [비워두면 수정하지 않음]: ").strip()

    if new_name:
        group.name = new_name
    if new_contact_interval:
        try:
            group.contact_interval = int(new_contact_interval)
        except ValueError:
            print("연락 주기는 숫자여야 합니다.")
    if new_tolerance:
        try:
            group.tolerance = int(new_tolerance)
        except ValueError:
            print("오차 범위는 숫자여야 합니다.")
    
    print(f"{group.name} 그룹 정보가 수정되었습니다!")

# 지인 리스트
contacts = []

# 지인 정보를 입력하는 함수 (에러 처리 포함, 공란 허용)
def add_contact():
    name = input("지인의 이름을 입력하세요: ").strip()
    if not name:
        print("지인의 이름은 필수 항목입니다.")
        return

    # 생성된 그룹이 없으면 지인을 추가할 수 없음
    if not groups:
        print("먼저 그룹을 추가해야 합니다.")
        return

    # 그룹 선택
    print("사용할 그룹을 선택하세요:")
    for idx, group in enumerate(groups, start=1):
        print(f"[{idx}] {group.name} (연락 주기: {group.contact_interval}일, 오차 범위: {group.tolerance}일)")

    # 잘못된 그룹 선택에 대한 에러 처리
    while True:
        try:
            group_choice = int(input("그룹 번호를 입력하세요: ")) - 1
            if group_choice < 0 or group_choice >= len(groups):
                raise IndexError
            break
        except (ValueError, IndexError):
            print("잘못된 그룹 선택입니다. 다시 시도하세요.")

    group = groups[group_choice]

    # 생일, 성별, 거주지, 취미 입력 (공란 허용)
    birthday = input("지인의 생일을 입력하세요 (예: 1990-01-01) (비워둘 수 있습니다): ").strip()
    if not birthday:
        birthday = None

    gender = input("지인의 성별을 입력하세요 (비워둘 수 있습니다): ").strip()
    if not gender:
        gender = None

    residence = input("지인의 거주지를 입력하세요 (비워둘 수 있습니다): ").strip()
    if not residence:
        residence = None

    hobbies = input("지인의 취미를 입력하세요 (비워둘 수 있습니다): ").strip()
    if not hobbies:
        hobbies = None

    # 지인 생성
    contact = Contact(name, group, birthday, gender, residence, hobbies)

    additional_info = input("지인에 대한 추가 정보를 입력하세요 (메모) (비워둘 수 있습니다): ").strip()
    contact.add_additional_info(additional_info)

    # 지인 리스트에 추가
    contacts.append(contact)
    print(f"{name}이(가) 성공적으로 추가되었습니다!")

# 지인 정보를 수정하는 함수
def edit_contact():
    if not contacts:
        print("수정할 지인이 없습니다.")
        return

    # 수정할 지인 선택
    print("수정할 지인을 선택하세요:")
    for idx, contact in enumerate(contacts, start=1):
        print(f"[{idx}] {contact.name}")
    
    try:
        contact_choice = int(input("지인 번호를 입력하세요: ")) - 1
        if contact_choice < 0 or contact_choice >= len(contacts):
            print("잘못된 선택입니다.")
            return
        contact = contacts[contact_choice]
    except (ValueError, IndexError):
        print("잘못된 선택입니다.")
        return

    # 수정할 지인 정보 입력
    new_name = input(f"이름을 수정하세요 (현재: {contact.name}) [비워두면 수정하지 않음]: ").strip()
    new_birthday = input(f"생일을 수정하세요 (현재: {contact.birthday}) [비워두면 수정하지 않음]: ").strip()
    new_gender = input(f"성별을 수정하세요 (현재: {contact.gender}) [비워두면 수정하지 않음]: ").strip()
    new_residence = input(f"거주지를 수정하세요 (현재: {contact.residence}) [비워두면 수정하지 않음]: ").strip()
    new_hobbies = input(f"취미를 수정하세요 (현재: {contact.hobbies}) [비워두면 수정하지 않음]: ").strip()
    new_additional_info = input(f"추가 정보를 수정하세요 (현재: {contact.additional_info}) [비워두면 수정하지 않음]: ").strip()

    # 정보 업데이트
    if new_name:
        contact.name = new_name
    if new_birthday:
        contact.birthday = new_birthday
    if new_gender:
        contact.gender = new_gender
    if new_residence:
        contact.residence = new_residence
    if new_hobbies:
        contact.hobbies = new_hobbies
    if new_additional_info:
        contact.add_additional_info(new_additional_info)
    
    print(f"{contact.name}의 정보가 수정되었습니다!")

# 모든 지인 정보를 출력하는 함수
def display_contacts():
    if not contacts:
        print("등록된 지인이 없습니다.")
        return
    for idx, contact in enumerate(contacts, start=1):
        birthday = contact.birthday if contact.birthday else "정보 없음"
        residence = contact.residence if contact.residence else "정보 없음"
        hobbies = contact.hobbies if contact.hobbies else "정보 없음"
        print(f"\n[{idx}] {contact.name} - 그룹: {contact.group.name}")
        print(f"생일: {birthday}, 성별: {contact.gender}, 거주지: {residence}, 취미: {hobbies}")
        print(f"추가 정보: {contact.additional_info}")
        print(f"최근 연락 날짜: {contact.last_contact_date if contact.last_contact_date else '기록 없음'}")

# -----------------------
# 대시보드 시각화 기능 추가
# -----------------------

# 1. 전체적으로 어떤 카테고리의 대화가 중요도가 높았는지 분석
def visualize_category_importance():
    category_importance = {}
    for contact in contacts:
        for record in contact.contact_history:
            for category, details in record['topics'].items():
                if category not in category_importance:
                    category_importance[category] = details['importance']
                else:
                    category_importance[category] += details['importance']
    
    # 데이터가 없는 경우 처리
    if not category_importance:
        print("기록된 대화가 없습니다. 시각화할 데이터가 없습니다.")
        return

    # 데이터가 있는 경우 그래프 생성
    categories = list(category_importance.keys())
    importance_values = list(category_importance.values())
    plt.bar(categories, importance_values, color='lightblue')
    plt.title("카테고리별 대화 중요도")
    plt.xlabel("카테고리")
    plt.ylabel("중요도 합계")
    plt.show()

# 2. 지인별 대화 주제 빈도 및 중요도 시각화
def visualize_contact_conversations(contact):
    topic_counts = {}
    importance_counts = {}

    for record in contact.contact_history:
        for category, details in record['topics'].items():
            # 카테고리별 대화 빈도 계산
            if category not in topic_counts:
                topic_counts[category] = 1
            else:
                topic_counts[category] += 1

            # 카테고리별 중요도 합계 계산
            if category not in importance_counts:
                importance_counts[category] = details['importance']
            else:
                importance_counts[category] += details['importance']

    # 데이터가 없는 경우 처리
    if not topic_counts:
        print(f"{contact.name}과의 기록된 대화가 없습니다. 시각화할 데이터가 없습니다.")
        return

    # 대화 빈도 그래프
    categories = list(topic_counts.keys())
    counts = list(topic_counts.values())
    plt.bar(categories, counts, color='lightgreen')
    plt.title(f"{contact.name}과(와)의 대화 카테고리 빈도")
    plt.xlabel('카테고리')
    plt.ylabel('대화 빈도')
    plt.show()

    # 중요도 그래프
    if not importance_counts:
        print(f"{contact.name}과의 중요한 대화가 없습니다. 중요도 데이터를 시각화할 수 없습니다.")
        return

    categories = list(importance_counts.keys())
    importance_values = list(importance_counts.values())
    plt.bar(categories, importance_values, color='salmon')
    plt.title(f"{contact.name}과(와)의 대화 중요도")
    plt.xlabel('카테고리')
    plt.ylabel('중요도 합계')
    plt.show()

# 3. 중요도가 높은 대화 주제 시각화
def visualize_important_conversations(contact):
    important_conversations = {}
    for record in contact.contact_history:
        for category, details in record['topics'].items():
            if details['importance'] >= 4:  # 중요도가 4 이상인 대화 주제
                if category not in important_conversations:
                    important_conversations[category] = [details['details']]
                else:
                    important_conversations[category].append(details['details'])

    # 중요도가 높은 대화 주제를 출력
    if important_conversations:
        for category, details in important_conversations.items():
            print(f"카테고리: {category}, 중요 대화 내용: {details}")
    else:
        print(f"{contact.name}과의 중요한 대화 내용이 없습니다.")

# 4. 날짜별 연락 내역 시각화
def visualize_contact_history():
    contact_dates = {}
    for contact in contacts:
        for record in contact.contact_history:
            if record['date'] not in contact_dates:
                contact_dates[record['date']] = 1
            else:
                contact_dates[record['date']] += 1

    # 데이터가 없는 경우 처리
    if not contact_dates:
        print("연락 내역이 없습니다. 시각화할 데이터가 없습니다.")
        return

    # 데이터가 있는 경우 그래프 생성
    dates = list(contact_dates.keys())
    frequencies = list(contact_dates.values())
    plt.bar(dates, frequencies, color='purple')
    plt.title("날짜별 연락 내역")
    plt.xlabel("날짜")
    plt.ylabel("연락 빈도")
    plt.show()

# 5. 연락 주기 및 예정 시각화
def visualize_contact_schedule(contact):
    if contact.last_contact_date:
        days_since_last_contact = (datetime.now() - contact.last_contact_date).days
        contact_interval = contact.group.contact_interval
        next_contact_in = contact_interval - days_since_last_contact

        # 연락 주기가 초과되었는지 확인
        if next_contact_in < 0:
            next_contact_in = 0  # 음수일 경우 0으로 처리
            print(f"{contact.name}의 연락 주기가 초과되었습니다! 가능한 빨리 연락해야 합니다.")

        labels = ['마지막 연락', '다음 연락까지 남은 일수']
        values = [days_since_last_contact, next_contact_in]

        plt.bar(labels, values, color=['lightcoral', 'lightgreen'])
        plt.title(f"{contact.name}의 연락 상태")
        plt.ylabel('일')
        plt.show()
    else:
        print(f"{contact.name}의 최근 연락 기록이 없습니다.")

# 프로그램 실행 시 대시보드 선택 메뉴 추가
while True:
    print("\n1. 그룹 추가")
    print("2. 지인 추가")
    print("3. 지인 목록 보기")
    print("4. 모든 지인에 대해 연락 주기 체크")
    print("5. 대화 기록 추가")
    print("6. 날짜별 대화 기록 보기")
    print("7. 지인별 대화 기록 보기")
    print("8. 대시보드: 카테고리별 중요도 분석")
    print("9. 대시보드: 지인별 대화 주제 및 중요도 분석")
    print("10. 대시보드: 중요한 대화 내용 분석")
    print("11. 대시보드: 날짜별 연락 내역")
    print("12. 대시보드: 연락 주기 및 상태")
    print("13. 그룹 정보 수정")  # 그룹 수정 메뉴 추가
    print("14. 지인 정보 수정")  # 지인 수정 메뉴 추가
    print("15. 대화 기록 수정")  # 대화 기록 수정 메뉴 추가
    print("16. 최근 연락 날짜 업데이트")  # 최근 연락 날짜 업데이트 메뉴 추가
    print("17. 종료 (데이터 저장)")

    choice = input("선택: ")

    if choice == "1":
        add_group()
    elif choice == "2":
        add_contact()
    elif choice == "3":
        display_contacts()
    elif choice == "4":
        check_all_contacts_due()
    elif choice == "5":
        if contacts:
            print("대화를 기록할 지인을 선택하세요:")
            for idx, contact in enumerate(contacts, start=1):
                print(f"[{idx}] {contact.name}")
            contact_choice = int(input("지인 번호를 선택하세요: ")) - 1
            record_conversation(contacts[contact_choice])
        else:
            print("등록된 지인이 없습니다.")
    elif choice == "6":
        view_conversations_by_date()
    elif choice == "7":
        view_conversations_by_contact()
    elif choice == "8":
        visualize_category_importance()
    elif choice == "9":
        if contacts:
            print("대화를 시각화할 지인을 선택하세요:")
            for idx, contact in enumerate(contacts, start=1):
                print(f"[{idx}] {contact.name}")
            contact_choice = int(input("지인 번호를 선택하세요: ")) - 1
            visualize_contact_conversations(contacts[contact_choice])
        else:
            print("등록된 지인이 없습니다.")
    elif choice == "10":
        if contacts:
            print("중요한 대화를 시각화할 지인을 선택하세요:")
            for idx, contact in enumerate(contacts, start=1):
                print(f"[{idx}] {contact.name}")
            contact_choice = int(input("지인 번호를 선택하세요: ")) - 1
            visualize_important_conversations(contacts[contact_choice])
        else:
            print("등록된 지인이 없습니다.")
    elif choice == "11":
        visualize_contact_history()
    elif choice == "12":
        if contacts:
            print("연락 주기를 시각화할 지인을 선택하세요:")
            for idx, contact in enumerate(contacts, start=1):
                print(f"[{idx}] {contact.name}")
            contact_choice = int(input("지인 번호를 선택하세요: ")) - 1
            visualize_contact_schedule(contacts[contact_choice])
        else:
            print("등록된 지인이 없습니다.")
    elif choice == "13":
        edit_group()  # 그룹 정보 수정 기능 호출
    elif choice == "14":
        edit_contact()  # 지인 정보 수정 기능 호출
    elif choice == "15":
        edit_conversation()  # 대화 기록 수정 기능 호출
    elif choice == "16":
        update_contact_date()  # 최근 연락 날짜 업데이트 기능 호출
    elif choice == "17":
        save_data()  # 프로그램 종료 시 데이터 저장
        print("프로그램을 종료합니다.")
        break
    else:
        print("잘못된 선택입니다.")
