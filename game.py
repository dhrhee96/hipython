import random
import tkinter as tk
from tkinter import messagebox

class Minesweeper:
    def __init__(self, root):
        self.root = root
        self.root.title("지뢰찾기 - 난이도 설정")
        
        # 기본 설정 (초급)
        self.rows = 9
        self.cols = 9
        self.total_mines = 10
        
        # UI 구성
        self.setup_ui()
        
        self.buttons = []
        self.mine_positions = set()
        self.revealed = set()
        self.flagged = set()
        self.game_over = False

        # 첫 게임 시작
        self.reset_game()

    def setup_ui(self):
        """상단 컨트롤 패널 및 설정 UI 구성"""
        self.control_frame = tk.Frame(self.root, pady=10)
        self.control_frame.pack()

        # --- 난이도 선택 버튼 ---
        difficulty_frame = tk.Frame(self.control_frame)
        difficulty_frame.pack()

        tk.Button(difficulty_frame, text="초급", width=8, command=lambda: self.apply_settings(9, 9, 10)).pack(side=tk.LEFT, padx=2)
        tk.Button(difficulty_frame, text="중급", width=8, command=lambda: self.apply_settings(16, 16, 40)).pack(side=tk.LEFT, padx=2)
        tk.Button(difficulty_frame, text="고급", width=8, command=lambda: self.apply_settings(16, 30, 99)).pack(side=tk.LEFT, padx=2)

        # --- 커스텀 설정 입력 ---
        custom_frame = tk.Frame(self.control_frame, pady=5)
        custom_frame.pack()

        tk.Label(custom_frame, text="행:").pack(side=tk.LEFT)
        self.row_entry = tk.Entry(custom_frame, width=3)
        self.row_entry.insert(0, "10")
        self.row_entry.pack(side=tk.LEFT, padx=2)

        tk.Label(custom_frame, text="열:").pack(side=tk.LEFT)
        self.col_entry = tk.Entry(custom_frame, width=3)
        self.col_entry.insert(0, "10")
        self.col_entry.pack(side=tk.LEFT, padx=2)

        tk.Label(custom_frame, text="지뢰:").pack(side=tk.LEFT)
        self.mine_entry = tk.Entry(custom_frame, width=3)
        self.mine_entry.insert(0, "15")
        self.mine_entry.pack(side=tk.LEFT, padx=2)

        tk.Button(custom_frame, text="커스텀 적용", command=self.apply_custom_settings).pack(side=tk.LEFT, padx=5)

        # --- 상태 표시 및 다시 시작 ---
        status_frame = tk.Frame(self.control_frame, pady=5)
        status_frame.pack()

        self.status_text = tk.StringVar()
        self.status_label = tk.Label(status_frame, textvariable=self.status_text, font=("Arial", 10, "bold"))
        self.status_label.pack(side=tk.LEFT, padx=10)

        self.restart_button = tk.Button(status_frame, text="다시 시작", command=self.reset_game)
        self.restart_button.pack(side=tk.LEFT)

        # 게임 판 프레임
        self.board_frame = tk.Frame(self.root)
        self.board_frame.pack(padx=10, pady=10)

    def apply_settings(self, r, c, m):
        """프리셋 난이도 적용"""
        self.rows = r
        self.cols = c
        self.total_mines = m
        self.reset_game()

    def apply_custom_settings(self):
        """입력창의 값을 읽어 커스텀 설정 적용"""
        try:
            r = int(self.row_entry.get())
            c = int(self.col_entry.get())
            m = int(self.mine_entry.get())
            
            if m >= r * c:
                messagebox.showwarning("설정 오류", "지뢰가 칸 수보다 많거나 같을 수 없습니다.")
                return
            
            self.apply_settings(r, c, m)
        except ValueError:
            messagebox.showerror("입력 오류", "숫자만 입력해주세요.")

    def reset_game(self):
        """게임 데이터 초기화 및 보드 재생성"""
        self.game_over = False
        self.revealed.clear()
        self.flagged.clear()
        self.mine_positions.clear()
        self.status_text.set(f"지뢰: {self.total_mines}")

        # 기존 버튼 제거
        for widget in self.board_frame.winfo_children():
            widget.destroy()

        self.buttons = [[None for _ in range(self.cols)] for _ in range(self.rows)]

        # 지뢰 배치
        all_positions = [(r, c) for r in range(self.rows) for c in range(self.cols)]
        self.mine_positions = set(random.sample(all_positions, self.total_mines))

        # 버튼 생성
        for r in range(self.rows):
            for c in range(self.cols):
                btn = tk.Button(self.board_frame, width=2, height=1, font=("Arial", 10, "bold"), relief=tk.RAISED)
                btn.grid(row=r, column=c)
                btn.bind("<Button-1>", lambda e, r=r, c=c: self.left_click(r, c))
                btn.bind("<Button-3>", lambda e, r=r, c=c: self.right_click(r, c))
                self.buttons[r][c] = btn
        
        # 창 크기 자동 조절
        self.root.geometry("") 

    def neighbors(self, row, col):
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0: continue
                nr, nc = row + dr, col + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    yield nr, nc

    def adjacent_mines(self, row, col):
        return sum((nr, nc) in self.mine_positions for nr, nc in self.neighbors(row, col))

    def left_click(self, row, col):
        if self.game_over or (row, col) in self.flagged or (row, col) in self.revealed:
            return

        if (row, col) in self.mine_positions:
            self.game_over = True
            self.reveal_all_mines()
            self.buttons[row][col].config(bg="red")
            self.status_text.set("게임 오버! 💥")
            messagebox.showinfo("지뢰찾기", "지뢰를 밟았습니다!")
            return

        self.reveal_cell(row, col)
        self.check_win()

    def right_click(self, row, col):
        if self.game_over or (row, col) in self.revealed:
            return

        btn = self.buttons[row][col]
        if (row, col) in self.flagged:
            self.flagged.remove((row, col))
            btn.config(text="", bg="SystemButtonFace")
        else:
            self.flagged.add((row, col))
            btn.config(text="🚩", fg="red")

        self.status_text.set(f"지뢰: {self.total_mines - len(self.flagged)}")

    def reveal_cell(self, row, col):
        if (row, col) in self.revealed or (row, col) in self.flagged:
            return

        self.revealed.add((row, col))
        btn = self.buttons[row][col]
        btn.config(relief=tk.SUNKEN, state=tk.DISABLED, bg="#e6e6e6")

        count = self.adjacent_mines(row, col)
        if count > 0:
            colors = {1: "blue", 2: "green", 3: "red", 4: "purple", 5: "maroon", 6: "turquoise", 7: "black", 8: "gray"}
            btn.config(text=str(count), disabledforeground=colors.get(count, "black"))
        else:
            for nr, nc in self.neighbors(row, col):
                self.reveal_cell(nr, nc)

    def reveal_all_mines(self):
        for r, c in self.mine_positions:
            self.buttons[r][c].config(text="💣", bg="#ffd9d9")

    def check_win(self):
        if len(self.revealed) == (self.rows * self.cols - self.total_mines):
            self.game_over = True
            self.status_text.set("승리! 🎉")
            messagebox.showinfo("지뢰찾기", "축하합니다! 승리하셨습니다.")

if __name__ == "__main__":
    root = tk.Tk()
    Minesweeper(root)
    root.mainloop()
