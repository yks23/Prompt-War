import tkinter as tk
from tkinter import messagebox
from src.call_llm import get_chat_completion
import re

class PromptDefenseGame:
    def __init__(self, root):
        self.root = root
        self.root.title("提示词攻防游戏")
        self.root.geometry("900x750")
        self.root.configure(bg="#f0f4f7")

        self.keyword = ""
        self.total_tokens = 0
        self.time_left = 0
        self.timer_running = False
        self.phase = "setup"  # setup -> defense -> attack
        self.round_time = 60
        self.defense_time = 15 * 60
        self.attack_history = []

        title_label = tk.Label(root, text="⚔️ 提示词攻防游戏 ⚔️", font=("Helvetica", 18, "bold"), bg="#f0f4f7")
        title_label.pack(pady=10)

        form_frame = tk.Frame(root, bg="#f0f4f7")
        form_frame.pack(pady=5)

        tk.Label(form_frame, text="设置关键词（防守目标）:", bg="#f0f4f7").grid(row=0, column=0, sticky="w", padx=10)
        self.keyword_entry = tk.Entry(form_frame, width=30)
        self.keyword_entry.grid(row=0, column=1, columnspan=2, pady=5, sticky="w")

        tk.Label(form_frame, text="防守方提示词:", bg="#f0f4f7").grid(row=1, column=0, sticky="w", padx=10)
        self.defense_entry = tk.Entry(form_frame, width=60)
        self.defense_entry.grid(row=1, column=1, columnspan=2, pady=5)

        tk.Label(form_frame, text="攻击方提示词:", bg="#f0f4f7").grid(row=2, column=0, sticky="w", padx=10)
        self.attack_entry = tk.Entry(form_frame, width=60)
        self.attack_entry.grid(row=2, column=1, columnspan=2, pady=5)

        self.action_button = tk.Button(form_frame, text="设置关键词", command=self.handle_button, bg="#2196F3", fg="white", font=("Arial", 10, "bold"))
        self.action_button.grid(row=3, column=0, pady=10)

        self.stop_timer_button = tk.Button(form_frame, text="停止计时", command=self.stop_timer, bg="#FF9800", fg="white", font=("Arial", 10, "bold"))
        self.stop_timer_button.grid(row=3, column=1, pady=10)

        self.timer_label = tk.Label(form_frame, text="剩余时间: --", font=("Arial", 12), bg="#f0f4f7", fg="red")
        self.timer_label.grid(row=3, column=2)

        self.token_label = tk.Label(root, text="总 token 数: 0", font=("Arial", 10, "bold"), bg="#f0f4f7", fg="green")
        self.token_label.pack()

        self.result_text = tk.Text(root, height=15, width=100, wrap=tk.WORD, bg="#ffffff", relief=tk.GROOVE, bd=2)
        self.result_text.pack(padx=10, pady=10)

        history_frame = tk.Frame(root, bg="#e9f0f5")
        history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(history_frame, text="攻击历史记录", font=("Arial", 12, "bold"), bg="#e9f0f5").pack(anchor="w")
        self.history_listbox = tk.Listbox(history_frame, height=6)
        self.history_listbox.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(history_frame, orient="vertical")
        scrollbar.config(command=self.history_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.history_listbox.config(yscrollcommand=scrollbar.set)

    def handle_button(self):
        if self.phase == "setup":
            self.keyword = self.keyword_entry.get().strip()
            if not self.keyword:
                messagebox.showwarning("输入不完整", "请填写关键词")
                return
            self.phase = "defense"
            self.time_left = self.defense_time
            self.timer_running = True
            self.result_text.insert(tk.END, "关键词设置成功，进入防守阶段！请在 15 分钟内设置防守提示词。\n")
            self.update_timer()
            self.action_button.config(text="提交防守提示词")

        elif self.phase == "defense":
            defense = self.defense_entry.get().strip()
            if not defense:
                messagebox.showwarning("提示词缺失", "请填写防守方提示词")
                return
            self.timer_running = False
            self.phase = "attack"
            self.result_text.insert(tk.END, f"已保存防守提示词：{defense}\n点击按钮开始攻击阶段。\n")
            self.action_button.config(text="开始攻击")

        elif self.phase == "attack":
            if self.action_button.cget("text") == "开始攻击":
                self.time_left = self.round_time
                self.timer_running = True
                self.result_text.insert(tk.END, "进入攻击阶段，每轮 60 秒。\n")
                self.update_timer()
                self.action_button.config(text="提交攻击提示词")
                return

            self.result_text.delete(1.0, tk.END)
            defense = self.defense_entry.get().strip()
            attack = self.attack_entry.get().strip()

            if not attack:
                messagebox.showwarning("输入不完整", "请填写攻击提示词")
                return

            for char in self.keyword:
                if char in attack:
                    messagebox.showerror("非法攻击提示", f"攻击提示不能包含关键词的任意字：'{char}'")
                    return

            result = get_chat_completion(defense, attack)
            if isinstance(result, tuple):
                content, tokens = result
            else:
                content, tokens = result, None

            keyword_present = self.keyword in content
            self.result_text.insert(tk.END, f"模型输出：\n{content}\n\n")
            self.result_text.insert(tk.END, f"关键词 \"{self.keyword}\" {'出现 ✅ 攻击成功' if keyword_present else '未出现 ❌ 防守成功'}\n")
            if tokens:
                self.total_tokens += tokens
                self.result_text.insert(tk.END, f"本次生成 token 数：{tokens}\n")
                self.token_label.config(text=f"总 token 数: {self.total_tokens}")

            history_result = f"攻击词: {attack} -> {'成功 ✅' if keyword_present else '失败 ❌'}"
            self.history_listbox.insert(tk.END, history_result)

            self.time_left = self.round_time
            self.timer_running = False
            self.update_timer()

    def stop_timer(self):
        self.timer_running = not self.timer_running
        if self.timer_running == False:
            self.result_text.insert(tk.END, "⏸️ 计时已停止\n")
            self.stop_timer_button.config(text="恢复计时")
        else:
            self.result_text.insert(tk.END, "▶️ 计时恢复\n")
            self.update_timer()
            self.stop_timer_button.config(text="停止计时")

    def update_timer(self):
        if self.timer_running and self.time_left > 0:
            minutes = self.time_left // 60
            seconds = self.time_left % 60
            self.timer_label.config(text=f"剩余时间: {minutes:02d}:{seconds:02d}")
            self.time_left -= 1
            self.root.after(1000, self.update_timer)
        elif self.time_left == 0:
            self.timer_label.config(text="时间到 ⏰")
            if self.phase == "defense":
                self.phase = "attack"
                self.timer_running = True
                self.time_left = self.round_time
                self.result_text.insert(tk.END, "防守阶段时间结束，进入攻击阶段。\n")
                self.action_button.config(text="提交攻击提示词")
                self.update_timer()
            elif self.phase == "attack":
                self.result_text.insert(tk.END, "攻击本轮时间结束。可以继续下一轮攻击。\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = PromptDefenseGame(root)
    root.mainloop()
