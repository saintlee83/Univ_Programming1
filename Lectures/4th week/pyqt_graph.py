import sys
import csv
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QTextEdit, QMessageBox, QGroupBox, QSplitter)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# 전역 변수로 데이터 저장 (본인 데이터로 교체 필요)
code_data = []  # 행정동 코드 데이터
data = []  # 인구 데이터

with open("./data/LOCAL_PEOPLE_DONG_201912.csv", encoding="utf-8-sig") as f:
  data = csv.reader(f)
  next(data)
  data = list(data)

with open("./data/dong_code.csv", encoding="utf-8-sig") as f1:
  code_data = csv.reader(f1)
  next(code_data)
  next(code_data)
  code_data = list(code_data)

for row in data:
  for i in range(1, 32):
    if i <= 2:
      row[i] = int(row[i])
    else:
      row[i] = float(row[i])

for row in code_data:
  row[1] = int(row[1])


class MplCanvas(FigureCanvas):
  def __init__(self, parent=None, width=5, height=4, dpi=100):
    self.fig = Figure(figsize=(width, height), dpi=dpi)
    self.axes = self.fig.add_subplot(111)
    super(MplCanvas, self).__init__(self.fig)


class PopulationAnalysisApp(QMainWindow):
  def __init__(self):
    super().__init__()
    self.canvas = None
    self.init_ui()

  def init_ui(self):
    # 윈도우 설정
    self.setWindowTitle('행정동 인구 비교 분석')
    self.setGeometry(100, 100, 1200, 700)

    # 중앙 위젯 설정
    central_widget = QWidget()
    self.setCentralWidget(central_widget)

    # 메인 레이아웃
    main_layout = QVBoxLayout()
    main_layout.setSpacing(15)
    main_layout.setContentsMargins(20, 20, 20, 20)

    # 제목
    title_label = QLabel('시간대별 평균인구 비교 분석')
    title_font = QFont('Arial', 18, QFont.Bold)
    title_label.setFont(title_font)
    title_label.setAlignment(Qt.AlignCenter)
    title_label.setStyleSheet("color: #2c3e50; margin: 10px 0;")
    main_layout.addWidget(title_label)

    # 입력 그룹박스
    input_group = QGroupBox("행정동 입력")
    input_group.setStyleSheet("""
            QGroupBox {
                font-size: 13px;
                font-weight: bold;
                color: #2c3e50;
                border: 2px solid #3498db;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
    input_layout = QVBoxLayout()

    # 안내 레이블
    instruction_label = QLabel('비교할 행정동을 공백문자로 구분하여 입력하세요:')
    instruction_label.setStyleSheet(
        "color: #34495e; font-size: 11px; border: none;")
    input_layout.addWidget(instruction_label)

    # 입력 필드
    self.entry = QLineEdit()
    self.entry.setPlaceholderText("예: 강남구 서초구 송파구")
    self.entry.setFont(QFont('Arial', 12))
    self.entry.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
                color: #000000;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
    self.entry.returnPressed.connect(self.analyze_and_plot)
    input_layout.addWidget(self.entry)

    # 버튼 레이아웃
    button_layout = QHBoxLayout()

    # 분석 버튼
    self.analyze_button = QPushButton('분석 및 그래프 보기')
    self.analyze_button.setFont(QFont('Arial', 11, QFont.Bold))
    self.analyze_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
    self.analyze_button.clicked.connect(self.analyze_and_plot)
    button_layout.addWidget(self.analyze_button)

    # 초기화 버튼
    self.clear_button = QPushButton('초기화')
    self.clear_button.setFont(QFont('Arial', 11))
    self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
    self.clear_button.clicked.connect(self.clear_input)
    button_layout.addWidget(self.clear_button)

    button_layout.addStretch()
    input_layout.addLayout(button_layout)

    input_group.setLayout(input_layout)
    main_layout.addWidget(input_group)

    # 스플리터로 결과와 그래프 영역 분할
    splitter = QSplitter(Qt.Horizontal)

    # 결과 그룹박스 (왼쪽)
    result_group = QGroupBox("분석 결과")
    result_group.setStyleSheet("""
            QGroupBox {
                font-size: 13px;
                font-weight: bold;
                color: #2c3e50;
                border: 2px solid #9b59b6;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
    result_layout = QVBoxLayout()

    # 결과 텍스트 영역
    self.result_text = QTextEdit()
    self.result_text.setReadOnly(True)
    self.result_text.setFont(QFont('Courier', 10))
    self.result_text.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 10px;
            }
        """)
    result_layout.addWidget(self.result_text)
    result_group.setLayout(result_layout)

    # 그래프 그룹박스 (오른쪽)
    graph_group = QGroupBox("그래프")
    graph_group.setStyleSheet("""
            QGroupBox {
                font-size: 13px;
                font-weight: bold;
                color: #2c3e50;
                border: 2px solid #e67e22;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
    self.graph_layout = QVBoxLayout()

    # 초기 안내 메시지
    self.placeholder_label = QLabel("분석을 실행하면 여기에 그래프가 표시됩니다.")
    self.placeholder_label.setAlignment(Qt.AlignCenter)
    self.placeholder_label.setStyleSheet(
        "color: #95a5a6; font-size: 14px; border: none;")
    self.graph_layout.addWidget(self.placeholder_label)

    graph_group.setLayout(self.graph_layout)

    # 스플리터에 위젯 추가
    splitter.addWidget(result_group)
    splitter.addWidget(graph_group)
    splitter.setSizes([400, 700])  # 초기 크기 비율

    main_layout.addWidget(splitter)

    # 하단 안내 메시지
    hint_label = QLabel('💡 Tip: 입력 후 Enter 키를 눌러도 분석이 실행됩니다')
    hint_label.setStyleSheet(
        "color: #7f8c8d; font-size: 10px; font-style: italic;")
    hint_label.setAlignment(Qt.AlignCenter)
    main_layout.addWidget(hint_label)

    central_widget.setLayout(main_layout)

    # 윈도우 스타일
    self.setStyleSheet("""
            QMainWindow {
                background-color: #ecf0f1;
            }
        """)

  def analyze_and_plot(self):
    # 입력값 가져오기
    input_text = self.entry.text().strip()

    if not input_text:
      QMessageBox.warning(self, "입력 오류", "행정동 이름을 입력해주세요!")
      return

    # 행정동 이름 파싱
    dong_name = input_text.split()

    # code_data와 data가 비어있는지 확인
    if not code_data or not data:
      QMessageBox.critical(self, "데이터 오류",
                           "데이터가 로드되지 않았습니다.\n"
                           "code_data와 data 변수를 먼저 로드해주세요!")
      return

    # 행정동 코드 찾기
    dong_code = []
    for i in range(len(dong_name)):
      found = False
      for row in code_data:
        if row[-1] == dong_name[i]:
          dong_code.append(int(row[1]))
          found = True
          break
      if not found:
        QMessageBox.critical(self, "오류",
                             f"'{dong_name[i]}'을(를) 찾을 수 없습니다!")
        return

    # populations 리스트 초기화
    populations = [[0 for i in range(24)] for _ in range(len(dong_name))]

    # 데이터 집계
    for row in data:
      # 핫플레이스가 있는 행정동인 경우
      if row[2] in dong_code:
        dong_idx = dong_code.index(row[2])
        time = int(row[1])  # 시간을 정수로 변환
        p = int(row[3])  # 인구를 정수로 변환
        populations[dong_idx][time] += p

    # 31일로 나누어 평균 계산
    for i in range(len(populations)):
      populations[i] = [p/31 for p in populations[i]]

    # 결과 출력 영역에 표시
    self.result_text.clear()
    result_html = "<h3 style='color: #2c3e50;'>시간대별 평균 인구 데이터</h3>"
    result_html += "<hr style='border: 1px solid #bdc3c7;'>"

    for i, name in enumerate(dong_name):
      result_html += f"<h4 style='color: #3498db;'>📍 {name}</h4>"
      result_html += "<table style='width: 100%; border-collapse: collapse; margin-bottom: 20px;'>"

      # 데이터를 보기 좋게 포맷
      for j in range(0, 24, 6):
        time_range = f"{j:02d}~{j+5:02d}시"
        result_html += f"<tr><td style='padding: 5px; background-color: #ecf0f1; font-weight: bold; color: #2c3e50;'>{time_range}</td>"

        for k in range(j, min(j+6, 24)):
          value = populations[i][k]
          result_html += f"<td style='padding: 5px; text-align: center; color: #000000;'>{value:.1f}</td>"
        result_html += "</tr>"

      result_html += "</table>"

    self.result_text.setHtml(result_html)

    # 기존 캔버스 제거
    if self.canvas is not None:
      self.graph_layout.removeWidget(self.canvas)
      self.canvas.deleteLater()
      self.canvas = None

    # placeholder 레이블 숨기기
    self.placeholder_label.hide()

    # 새 캔버스 생성 및 그래프 그리기
    self.canvas = MplCanvas(self, width=8, height=6, dpi=100)

    # 한글 폰트 설정
    try:
      plt.rcParams['font.family'] = 'Apple SD Gothic Neo'
    except:
      try:
        plt.rcParams['font.family'] = 'Malgun Gothic'
      except:
        pass

    plt.rcParams['axes.unicode_minus'] = False

    # 그래프 그리기
    self.canvas.axes.clear()
    self.canvas.axes.set_title(
        '시간대별 평균인구 비교', fontsize=14, fontweight='bold', pad=15)

    # 여러 행정동을 동적으로 그래프에 추가
    colors = ['#9b59b6', '#e74c3c', '#3498db', '#2ecc71', '#f39c12',
              '#1abc9c', '#e67e22', '#34495e']
    for i in range(len(dong_name)):
      self.canvas.axes.plot(range(24), populations[i],
                            color=colors[i % len(colors)],
                            label=dong_name[i],
                            marker='o',
                            linewidth=2.5,
                            markersize=6)

    self.canvas.axes.legend(fontsize=10, loc='best', framealpha=0.9)
    self.canvas.axes.set_xlabel('시간대 (시)', fontsize=11, fontweight='bold')
    self.canvas.axes.set_ylabel('평균인구수 (명)', fontsize=11, fontweight='bold')
    self.canvas.axes.set_xticks(range(24))
    self.canvas.axes.grid(True, alpha=0.3, linestyle='--')
    self.canvas.fig.tight_layout()

    # 캔버스를 레이아웃에 추가
    self.graph_layout.addWidget(self.canvas)

    QMessageBox.information(self, "완료", "분석이 완료되었습니다!")

  def clear_input(self):
    self.entry.clear()
    self.result_text.clear()

    # 그래프 캔버스 제거
    if self.canvas is not None:
      self.graph_layout.removeWidget(self.canvas)
      self.canvas.deleteLater()
      self.canvas = None

    # placeholder 레이블 다시 표시
    self.placeholder_label.show()

    self.entry.setFocus()


def main():
  app = QApplication(sys.argv)

  # 애플리케이션 스타일 설정
  app.setStyle('Fusion')

  window = PopulationAnalysisApp()
  window.show()

  sys.exit(app.exec_())


if __name__ == '__main__':
  main()
