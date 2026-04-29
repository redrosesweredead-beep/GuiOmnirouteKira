import customtkinter as ctk
import requests
import subprocess
import threading
import os
import time
import tkinter as tk
from tkinter import messagebox, filedialog

class GeminiDeveloperGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- КОНФИГУРАЦИЯ ---
        self.title("Kiro AI | Developer Pro")
        self.geometry("1050x950")
        ctk.set_appearance_mode("dark")
        
        # Цвета Gemini
        self.bg_color = "#0e0e10"
        self.user_bubble = "#1e1f20"
        self.ai_accent = "#8ab4f8"
        self.code_bg = "#131314"
        
        self.api_key = "sk-e9a9b33bd803d1a5-babc81-9d680253"
        self.url = "http://127.0.0.1:20128/v1/chat/completions"
        self.model = "kr/claude-sonnet-4.5"
        self.messages = []

        # Карта расширений для авто-подбора при сохранении
        self.extension_map = {
            "python": ".py", "py": ".py",
            "javascript": ".js", "js": ".js",
            "html": ".html", "css": ".css",
            "json": ".json", "typescript": ".ts",
            "cpp": ".cpp", "c": ".c", "java": ".java",
            "sql": ".sql", "bash": ".sh", "shell": ".sh"
        }

        self.configure(fg_color=self.bg_color)
        self.setup_ui()
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        threading.Thread(target=self.launch_proxy, daemon=True).start()

    def setup_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Скролл-зона чата
        self.chat_frame = ctk.CTkScrollableFrame(
            self, fg_color=self.bg_color, corner_radius=0, scrollbar_button_color="#333"
        )
        self.chat_frame.grid(row=0, column=0, sticky="nsew", padx=5)

        # Нижняя панель ввода
        self.input_wrapper = ctk.CTkFrame(self, fg_color="transparent")
        self.input_wrapper.grid(row=1, column=0, padx=40, pady=(0, 30), sticky="ew")
        self.input_wrapper.grid_columnconfigure(0, weight=1)

        self.user_input = ctk.CTkEntry(
            self.input_wrapper, 
            placeholder_text="Спросите Kiro о коде или проекте...", 
            height=60, 
            corner_radius=30, 
            font=("Segoe UI", 16),
            fg_color="#1e1f20", 
            border_color="#444746",
            border_width=1
        )
        self.user_input.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.user_input.bind("<Return>", lambda e: self.send_message())

        self.send_button = ctk.CTkButton(
            self.input_wrapper, text="✦", command=self.send_message, 
            width=60, height=60, corner_radius=30, fg_color=self.ai_accent, 
            hover_color="#aecbfa", text_color="#000", font=("Segoe UI", 24, "bold"),
            state="disabled"
        )
        self.send_button.grid(row=0, column=1)

    def launch_proxy(self):
        os.environ["CLAUDE_CODE_SKIP_BROWSER_AUTH"] = "1"
        os.environ["ANTHROPIC_AUTH_TOKEN"] = self.api_key
        try:
            subprocess.run("taskkill /f /im node.exe", shell=True, capture_output=True)
            time.sleep(1)
        except: pass
        subprocess.Popen("cmd /c omniroute", shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        for _ in range(15):
            try:
                if requests.get("http://127.0.0.1:20128/v1/models", timeout=2).status_code == 200:
                    self.after(0, self.ready_ui)
                    return
            except: time.sleep(2)

    def ready_ui(self):
        self.user_input.configure(state="normal")
        self.send_button.configure(state="normal")
        self.add_bubble("assistant", "Система готова к работе. Я могу писать код и помогать с его сохранением!")

    def add_bubble(self, role, text):
        align = "e" if role == "user" else "w"
        master_frame = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        master_frame.pack(fill="x", padx=10, pady=15)

        content_frame = ctk.CTkFrame(master_frame, fg_color="transparent")
        content_frame.pack(anchor=align)

        header_text = "● Вы" if role == "user" else "✨ Kiro AI"
        header_color = "#ccc" if role == "user" else self.ai_accent
        
        ctk.CTkLabel(content_frame, text=header_text, font=("Segoe UI", 13, "bold"), text_color=header_color).pack(anchor=align, padx=15, pady=(0, 5))

        if "```" in text and role == "assistant":
            self.render_markdown(content_frame, text)
        else:
            bubble_bg = self.user_bubble if role == "user" else "transparent"
            msg_lbl = ctk.CTkLabel(
                content_frame, text=text, wraplength=750, justify="left",
                fg_color=bubble_bg, corner_radius=20, padx=20, pady=15,
                font=("Segoe UI", 15), text_color="#e3e3e3"
            )
            msg_lbl.pack(anchor=align)

    def render_markdown(self, parent, text):
        parts = text.split("```")
        for i, part in enumerate(parts):
            if i % 2 == 1: # Блок кода
                lines = part.strip().split('\n')
                lang = lines[0].lower().strip() if lines else "txt"
                code = '\n'.join(lines[1:]) if len(lines) > 1 else part
                
                code_box = ctk.CTkFrame(parent, fg_color=self.code_bg, corner_radius=12, border_width=1, border_color="#333")
                code_box.pack(fill="x", pady=10, padx=10)
                
                header = ctk.CTkFrame(code_box, fg_color="#202124", height=40, corner_radius=12)
                header.pack(fill="x", side="top")
                
                ctk.CTkLabel(header, text=lang.upper(), font=("Consolas", 11, "bold"), text_color="#777").pack(side="left", padx=15)
                
                # Кнопка сохранения
                save_btn = ctk.CTkButton(
                    header, text="💾 Сохранить", width=90, height=26, 
                    fg_color="#3c4043", hover_color="#4f5052", font=("Segoe UI", 11),
                    command=lambda c=code, l=lang: self.save_code_to_file(c, l)
                )
                save_btn.pack(side="right", padx=(5, 10), pady=7)

                # Кнопка копирования
                copy_btn = ctk.CTkButton(
                    header, text="📋 Копировать", width=90, height=26, 
                    fg_color="#3c4043", hover_color="#4f5052", font=("Segoe UI", 11),
                    command=lambda c=code: self.copy_to_clipboard(c)
                )
                copy_btn.pack(side="right", padx=5, pady=7)

                txt = tk.Text(code_box, font=("Consolas", 12), bg=self.code_bg, fg="#e8eaed",
                              relief="flat", borderwidth=0, height=min(len(lines), 30), padx=15, pady=10)
                txt.insert("1.0", code)
                txt.config(state="disabled")
                txt.pack(fill="x")
            else:
                if part.strip():
                    lbl = ctk.CTkLabel(parent, text=part.strip(), wraplength=750, justify="left", font=("Segoe UI", 15))
                    lbl.pack(anchor="w", pady=5, padx=15)

    def save_code_to_file(self, code, lang):
        """Метод для скачивания/сохранения кода в файл"""
        ext = self.extension_map.get(lang, ".txt")
        file_path = filedialog.asksaveasfilename(
            defaultextension=ext,
            filetypes=[(f"{lang.upper()} files", f"*{ext}"), ("All files", "*.*")],
            initialfile=f"script{ext}"
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(code)
                messagebox.showinfo("Kiro AI", f"Файл успешно сохранен:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")

    def copy_to_clipboard(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)
        # Маленькое уведомление в углу (опционально)

    def send_message(self):
        text = self.user_input.get().strip()
        if not text: return
        self.add_bubble("user", text)
        self.user_input.delete(0, "end")
        self.messages.append({"role": "user", "content": text})
        self.send_button.configure(state="disabled", text="✦")
        threading.Thread(target=self.fetch_ai, daemon=True).start()

    def fetch_ai(self):
        try:
            r = requests.post(
                self.url, 
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={"model": self.model, "messages": self.messages, "stream": False},
                timeout=180
            )
            data = r.json()
            ans = data['choices'][0]['message']['content'] if 'choices' in data else data['content'][0]['text']
            self.messages.append({"role": "assistant", "content": ans})
            self.after(0, lambda: self.add_bubble("assistant", ans))
        except Exception as e:
            self.after(0, lambda: self.add_bubble("assistant", f"⚠️ Ошибка сети: {str(e)}"))
        finally:
            self.after(0, lambda: self.send_button.configure(state="normal", text="✦"))

    def on_closing(self):
        try: subprocess.run("taskkill /f /im node.exe", shell=True, capture_output=True)
        except: pass
        self.destroy()

if __name__ == "__main__":
    app = GeminiDeveloperGUI()
    app.mainloop()