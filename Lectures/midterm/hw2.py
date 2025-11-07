# PyQt5를 이용한 파일 입력 및 행정동 입력
import sys
import csv
import datetime
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QFileDialog, 
                             QMessageBox, QTextEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


# 파일 열기 함수 (파일 경로를 입력받음)
def file_open_with_input(file_path1, file_path2):
    try:
        # 1-1. 인구 데이터 파일 읽기
        f = open(file_path1, encoding='utf8')
        data = csv.reader(f)
        next(data)  # 헤더(첫 번째 행) 건너뛰기
        data = list(data)  # CSV 데이터를 리스트로 변환
        
        # 1-2. 행정동 코드 파일 읽기
        f2 = open(file_path2, encoding='utf8')
        code_data = csv.reader(f2)
        next(code_data)  # 첫 번째 헤더 행 건너뛰기
        next(code_data)  # 두 번째 헤더 행 건너뛰기
        code_data = list(code_data)  # CSV 데이터를 리스트로 변환
        
        # 1-3. 데이터타입 변환하기 : 문자 --> 숫자
        # 인구데이터의 각 행을 순회하며 타입 변환
        for row in data:
            # 각 행의 1~31번 인덱스 열을 순회 (0번은 날짜 문자열이므로 제외)
            for i in range(1, 32):
                # 1~2번 인덱스(시간대, 행정동 코드)는 정수로 변환
                if i <= 2:
                    row[i] = int(row[i])
                # 3번 이후 인덱스(인구수 등)는 실수로 변환
                else:
                    row[i] = float(row[i])
        
        # 행정동 코드 데이터의 각 행을 순회하며 타입 변환
        for row in code_data:
            # row[1]: 행정동 코드를 문자열에서 정수로 변환
            row[1] = int(row[1])
        
        # 변환된 인구 데이터와 행정동 코드 데이터 반환
        return data, code_data
    except FileNotFoundError as e:
        return None, None, f"파일을 찾을 수 없습니다: {e}"
    except Exception as e:
        return None, None, f"파일 읽기 오류: {e}"


# 행정동 코드 검색 함수
def dong_search(dong_name, code_data):
    # code_data의 각 행(row)을 순회하며 행정동 이름 검색
    for row in code_data:
        # row[-1]: 행의 마지막 열 = 행정동 이름
        # 입력받은 행정동 이름과 일치하는 행을 찾음
        if row[-1] == dong_name:
            # row[1]: 해당 행의 두 번째 열 = 행정동 코드 (숫자)
            code = row[1]
            # 행정동 코드 반환
            return code
    return None


# 시간대별 평균인구 분석 함수
def analysis1(dong_name, dong_code, data):
    # 3-1. 입력된 행정동의 시간대별 평균인구 구하기
    # 24시간 각 시간대별 인구수를 저장할 리스트 초기화
    population = [0 for i in range(24)]
    
    # data의 각 행(row)을 순회하며 해당 행정동의 데이터만 추출
    for row in data:
        # row[2]: 행정동 코드, 입력받은 행정동 코드와 일치하는지 확인
        if row[2] == dong_code:
            # row[1]: 시간대 (0~23), row[3]: 해당 시간대의 인구수
            time, p = row[1], row[3]
            # 해당 시간대의 인구수를 누적
            population[time] += p
    
    # 12월 31일간의 누적 인구수를 평균으로 변환
    population = [p/31 for p in population]
    
    # 3-2. 3-1에서 구한 평균인구 리스트로 꺾은선 그래프 그리기
    # 그래프 함수에 전달하기 위해 2차원 리스트로 변환
    population = [population]
    labels = ['평균인구']
    title = dong_name + ' 시간대별 평균인구'
    graph_plot(popu_list=population, label_list=labels, graph_title=title)


# 주중/주말 시간대별 평균인구 분석 함수
def analysis2(dong_name, dong_code, data):
    # 4-1. 입력된 행정동의 주중/주말 시간대별 평균인구 구하기
    # 평일(월~금)과 주말(토~일) 24시간 각 시간대별 인구수를 저장할 리스트 초기화
    weekday = [0 for i in range(24)]
    weekend = [0 for i in range(24)]
    
    # data의 각 행(row)을 순회하며 해당 행정동의 데이터만 추출
    for row in data:
        # row[2]: 행정동 코드, 입력받은 행정동 코드와 일치하는지 확인
        if row[2] == dong_code:
            # row[1]: 시간대 (0~23), row[3]: 해당 시간대의 인구수
            time, p = row[1], row[3]
            # row[0]: 날짜 정보 (YYYYMMDD 형식의 문자열)
            # 문자열을 슬라이싱하여 년, 월, 일 추출 후 정수로 변환
            year, mon, day = int(row[0][:4]), int(row[0][4:6]), int(row[0][6:])
            # 해당 날짜의 요일을 숫자로 반환 (0:월요일 ~ 6:일요일)
            num = datetime.date(year, mon, day).weekday()
            # 평일(0~4: 월~금)인 경우
            if num < 5:
                weekday[time] += p
            # 주말(5~6: 토~일)인 경우
            else:
                weekend[time] += p
    
    # 12월 한 달 동안의 평일과 주말 일수를 각각 카운트
    weekday_cnt, weekend_cnt = 0, 0
    for i in range(1, 32):
        # 2019년 12월 각 날짜가 평일인지 주말인지 확인
        if datetime.date(2019, 12, i).weekday() < 5:
            weekday_cnt += 1  # 평일 일수 증가
        else:
            weekend_cnt += 1  # 주말 일수 증가
    
    # 누적된 인구수를 평일/주말 일수로 나누어 평균 계산
    weekday = [w/weekday_cnt for w in weekday]
    weekend = [w/weekend_cnt for w in weekend]
    
    # 4-2. 4-1에서 구한 평균인구 리스트로 꺾은선 그래프 그리기
    # 평일과 주말 데이터를 하나의 리스트로 묶음
    data_set = [weekday, weekend]
    labels = ['평일', '주말']
    title = dong_name + ' 주중/주말 시간대별 평균인구'
    graph_plot(popu_list=data_set, label_list=labels, graph_title=title)


# 그래프 출력 함수
def graph_plot(popu_list, label_list, graph_title):
    plt.figure(dpi=150)
    plt.rc('font', family='Apple SD Gothic Neo')
    plt.title(graph_title)
    for i in range(len(popu_list)):
        plt.plot(range(24), popu_list[i], label=label_list[i])
    plt.legend()
    plt.xlabel('시간대')
    plt.ylabel('평균인구수')
    plt.xticks(range(24), range(24))
    plt.show()


# PyQt5 GUI 클래스
class PopulationAnalysisApp(QWidget):
    def __init__(self):
        super().__init__()
        self.data = None
        self.code_data = None
        self.init_ui()
    
    def init_ui(self):
        # 윈도우 설정
        self.setWindowTitle('행정동 인구 분석 프로그램')
        self.setGeometry(300, 300, 700, 500)
        
        # 레이아웃 생성
        layout = QVBoxLayout()
        
        # 제목 라벨
        title_label = QLabel('📈 행정동 인구 분석 프로그램')
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 설명 라벨
        desc_label = QLabel('파일을 선택하고 행정동 이름을 입력한 후 분석 버튼을 클릭하세요.')
        desc_label.setStyleSheet('color: gray;')
        desc_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc_label)
        
        layout.addSpacing(20)
        
        # 파일 1 선택 (인구 데이터)
        file1_layout = QHBoxLayout()
        file1_label = QLabel('인구 데이터 파일:')
        file1_label.setMinimumWidth(120)
        self.file1_input = QLineEdit()
        self.file1_input.setPlaceholderText('data/LOCAL_PEOPLE_DONG_201912.csv')
        file1_btn = QPushButton('파일 선택')
        file1_btn.clicked.connect(self.select_file1)
        file1_layout.addWidget(file1_label)
        file1_layout.addWidget(self.file1_input)
        file1_layout.addWidget(file1_btn)
        layout.addLayout(file1_layout)
        
        # 파일 2 선택 (행정동 코드)
        file2_layout = QHBoxLayout()
        file2_label = QLabel('행정동 코드 파일:')
        file2_label.setMinimumWidth(120)
        self.file2_input = QLineEdit()
        self.file2_input.setPlaceholderText('data/dong_code.csv')
        file2_btn = QPushButton('파일 선택')
        file2_btn.clicked.connect(self.select_file2)
        file2_layout.addWidget(file2_label)
        file2_layout.addWidget(self.file2_input)
        file2_layout.addWidget(file2_btn)
        layout.addLayout(file2_layout)
        
        layout.addSpacing(10)
        
        # 행정동 입력
        dong_layout = QHBoxLayout()
        dong_label = QLabel('행정동 이름:')
        dong_label.setMinimumWidth(120)
        self.dong_input = QLineEdit()
        self.dong_input.setPlaceholderText('예: 압구정동')
        dong_layout.addWidget(dong_label)
        dong_layout.addWidget(self.dong_input)
        layout.addLayout(dong_layout)
        
        layout.addSpacing(20)
        
        # 분석 시작 버튼
        self.analyze_btn = QPushButton('분석 시작')
        self.analyze_btn.setStyleSheet('''
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        ''')
        self.analyze_btn.clicked.connect(self.start_analysis)
        layout.addWidget(self.analyze_btn)
        
        layout.addSpacing(10)
        
        # 결과 출력 영역
        result_label = QLabel('결과:')
        layout.addWidget(result_label)
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setMaximumHeight(150)
        layout.addWidget(self.result_text)
        
        # 레이아웃 설정
        self.setLayout(layout)
    
    def select_file1(self):
        """인구 데이터 파일 선택"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            '인구 데이터 파일 선택', 
            '', 
            'CSV Files (*.csv);;All Files (*)'
        )
        if file_path:
            self.file1_input.setText(file_path)
    
    def select_file2(self):
        """행정동 코드 파일 선택"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            '행정동 코드 파일 선택', 
            '', 
            'CSV Files (*.csv);;All Files (*)'
        )
        if file_path:
            self.file2_input.setText(file_path)
    
    def start_analysis(self):
        """분석 시작"""
        self.result_text.clear()
        
        # 입력값 가져오기
        file_path1 = self.file1_input.text().strip()
        file_path2 = self.file2_input.text().strip()
        dong_name = self.dong_input.text().strip()
        
        # 입력값 검증
        if not file_path1 or not file_path2:
            QMessageBox.warning(self, '경고', '파일 경로를 모두 입력해주세요.')
            return
        
        if not dong_name:
            QMessageBox.warning(self, '경고', '행정동 이름을 입력해주세요.')
            return
        
        # 파일 로드
        self.result_text.append('📁 파일을 불러오는 중...')
        result = file_open_with_input(file_path1, file_path2)
        
        if len(result) == 3:
            # 에러 발생
            self.result_text.append(f'❌ {result[2]}')
            QMessageBox.critical(self, '오류', result[2])
            return
        
        self.data, self.code_data = result
        self.result_text.append('✅ 파일 로드 완료!')
        
        # 행정동 코드 검색
        input_code = dong_search(dong_name, self.code_data)
        
        if input_code is None:
            error_msg = f"'{dong_name}' 행정동을 찾을 수 없습니다."
            self.result_text.append(f'❌ {error_msg}')
            QMessageBox.warning(self, '경고', error_msg)
            return
        
        self.result_text.append(f'{dong_name} - {input_code} 를 분석합니다!')
        self.result_text.append('\n📊 분석을 시작합니다...')
        
        try:
            # 분석: 시간대별 평균인구
            self.result_text.append('\n📊 시간대별 평균인구 분석')
            analysis1(dong_name=dong_name, dong_code=input_code, data=self.data)
            
            self.result_text.append('\n✅ 분석 완료!')
            QMessageBox.information(self, '완료', '분석이 완료되었습니다!')
        except Exception as e:
            error_msg = f'분석 중 오류 발생: {str(e)}'
            self.result_text.append(f'\n❌ {error_msg}')
            QMessageBox.critical(self, '오류', error_msg)


# 메인 실행 코드
def run_app():
    app = QApplication(sys.argv)
    window = PopulationAnalysisApp()
    window.show()
    app.exec_()

# 앱 실행
run_app()
