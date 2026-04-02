import os
import hashlib
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, scrolledtext


MASTER_FILE = "master.hash"
PASSWORDS_FILE = "passwords.txt"
LOG_FILE = "log.txt"


def write_log(text: str) -> None:
    now = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(f"{now} - {text}\n")


def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def init_master_password():
    if not os.path.exists(MASTER_FILE):
        default_password = "admin123"
        with open(MASTER_FILE, "w", encoding="utf-8") as file:
            file.write(hash_text(default_password))
        write_log("Создан мастер-пароль по умолчанию")


def check_master_password(password: str) -> bool:
    if not os.path.exists(MASTER_FILE):
        init_master_password()

    with open(MASTER_FILE, "r", encoding="utf-8") as file:
        saved_hash = file.read().strip()

    return hash_text(password) == saved_hash


def load_passwords():
    records = []

    if os.path.exists(PASSWORDS_FILE):
        with open(PASSWORDS_FILE, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if line:
                    parts = line.split(" | ")
                    if len(parts) == 3:
                        site = parts[0].replace("site: ", "")
                        login = parts[1].replace("login: ", "")
                        password = parts[2].replace("password: ", "")
                        records.append((site, login, password))

    return records


def save_passwords(records):
    with open(PASSWORDS_FILE, "w", encoding="utf-8") as file:
        for site, login, password in records:
            file.write(f"site: {site} | login: {login} | password: {password}\n")


class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure Password Manager - Вход")
        self.root.geometry("420x220")
        self.root.resizable(False, False)

        init_master_password()
        self.create_widgets()

    def create_widgets(self):
        title_label = tk.Label(
            self.root,
            text="Secure Password Manager",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=20)

        info_label = tk.Label(
            self.root,
            text="Введите мастер-пароль",
            font=("Arial", 11)
        )
        info_label.pack(pady=5)

        self.password_entry = tk.Entry(self.root, show="*", font=("Arial", 12), width=25)
        self.password_entry.pack(pady=10)

        login_button = tk.Button(
            self.root,
            text="Войти",
            width=18,
            height=2,
            command=self.login
        )
        login_button.pack(pady=10)

        hint_label = tk.Label(
            self.root,
            text="Пароль по умолчанию: admin123",
            font=("Arial", 9),
            fg="gray"
        )
        hint_label.pack(pady=5)

    def login(self):
        password = self.password_entry.get().strip()

        if not password:
            messagebox.showwarning("Предупреждение", "Введите мастер-пароль.")
            write_log("Ошибка входа: пустой мастер-пароль")
            return

        if check_master_password(password):
            write_log("Успешный вход в программу")
            self.root.destroy()

            new_root = tk.Tk()
            PasswordManagerWindow(new_root)
            new_root.mainloop()
        else:
            messagebox.showerror("Ошибка", "Неверный мастер-пароль.")
            write_log("Неуспешная попытка входа в программу")


class PasswordManagerWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure Password Manager")
        self.root.geometry("820x550")
        self.root.resizable(False, False)

        self.records = load_passwords()

        self.create_widgets()
        self.refresh_text_area()

    def create_widgets(self):
        title_label = tk.Label(
            self.root,
            text="Менеджер паролей",
            font=("Arial", 18, "bold")
        )
        title_label.pack(pady=10)

        form_frame = tk.Frame(self.root)
        form_frame.pack(fill="x", padx=15, pady=10)

        tk.Label(form_frame, text="Сайт:", font=("Arial", 11)).grid(row=0, column=0, sticky="w", pady=5)
        self.site_entry = tk.Entry(form_frame, font=("Arial", 11), width=45)
        self.site_entry.grid(row=0, column=1, pady=5, padx=10)

        tk.Label(form_frame, text="Логин:", font=("Arial", 11)).grid(row=1, column=0, sticky="w", pady=5)
        self.login_entry = tk.Entry(form_frame, font=("Arial", 11), width=45)
        self.login_entry.grid(row=1, column=1, pady=5, padx=10)

        tk.Label(form_frame, text="Пароль:", font=("Arial", 11)).grid(row=2, column=0, sticky="w", pady=5)
        self.password_entry = tk.Entry(form_frame, font=("Arial", 11), width=45)
        self.password_entry.grid(row=2, column=1, pady=5, padx=10)

        buttons_frame = tk.Frame(self.root)
        buttons_frame.pack(pady=15)

        add_button = tk.Button(
            buttons_frame,
            text="Добавить запись",
            width=18,
            height=2,
            command=self.add_record
        )
        add_button.grid(row=0, column=0, padx=8)

        delete_button = tk.Button(
            buttons_frame,
            text="Удалить запись",
            width=18,
            height=2,
            command=self.delete_record
        )
        delete_button.grid(row=0, column=1, padx=8)

        show_button = tk.Button(
            buttons_frame,
            text="Обновить список",
            width=18,
            height=2,
            command=self.refresh_text_area
        )
        show_button.grid(row=0, column=2, padx=8)

        history_button = tk.Button(
            buttons_frame,
            text="История действий",
            width=18,
            height=2,
            command=self.show_history
        )
        history_button.grid(row=0, column=3, padx=8)

        clear_button = tk.Button(
            buttons_frame,
            text="Очистить поля",
            width=18,
            height=2,
            command=self.clear_fields
        )
        clear_button.grid(row=0, column=4, padx=8)

        info_label = tk.Label(
            self.root,
            text="Сохранённые записи:",
            font=("Arial", 12, "bold")
        )
        info_label.pack(anchor="w", padx=15, pady=(10, 5))

        self.text_area = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            font=("Consolas", 10),
            width=95,
            height=18
        )
        self.text_area.pack(padx=15, pady=5)

        delete_info = tk.Label(
            self.root,
            text="Чтобы удалить запись, введите сайт точно так же, как он записан в списке, и нажмите 'Удалить запись'.",
            font=("Arial", 9),
            fg="gray"
        )
        delete_info.pack(pady=5)

    def add_record(self):
        site = self.site_entry.get().strip()
        login = self.login_entry.get().strip()
        password = self.password_entry.get().strip()

        if not site or not login or not password:
            messagebox.showwarning("Предупреждение", "Заполните все поля.")
            write_log("Ошибка: попытка добавить запись с пустыми полями")
            return

        self.records.append((site, login, password))
        save_passwords(self.records)
        self.refresh_text_area()
        self.clear_fields()

        messagebox.showinfo("Успех", "Запись успешно добавлена.")
        write_log(f"Добавлена запись для сайта {site}")

    def delete_record(self):
        site_to_delete = self.site_entry.get().strip()

        if not site_to_delete:
            messagebox.showwarning("Предупреждение", "Введите сайт для удаления записи.")
            write_log("Ошибка: попытка удалить запись без указания сайта")
            return

        new_records = []
        deleted = False

        for site, login, password in self.records:
            if site == site_to_delete and not deleted:
                deleted = True
                continue
            new_records.append((site, login, password))

        if deleted:
            self.records = new_records
            save_passwords(self.records)
            self.refresh_text_area()
            self.clear_fields()

            messagebox.showinfo("Успех", f"Запись для сайта {site_to_delete} удалена.")
            write_log(f"Удалена запись для сайта {site_to_delete}")
        else:
            messagebox.showerror("Ошибка", "Запись с таким сайтом не найдена.")
            write_log(f"Ошибка: запись для сайта {site_to_delete} не найдена")

    def refresh_text_area(self):
        self.text_area.config(state="normal")
        self.text_area.delete("1.0", tk.END)

        if not self.records:
            self.text_area.insert(tk.END, "Записей пока нет.\n")
        else:
            for index, (site, login, password) in enumerate(self.records, start=1):
                self.text_area.insert(
                    tk.END,
                    f"{index}. Сайт: {site}\n   Логин: {login}\n   Пароль: {password}\n\n"
                )

        self.text_area.config(state="disabled")

    def clear_fields(self):
        self.site_entry.delete(0, tk.END)
        self.login_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)

    def show_history(self):
        history_window = tk.Toplevel(self.root)
        history_window.title("История действий")
        history_window.geometry("760x400")

        history_area = scrolledtext.ScrolledText(
            history_window,
            wrap=tk.WORD,
            font=("Consolas", 10)
        )
        history_area.pack(fill="both", expand=True, padx=10, pady=10)

        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r", encoding="utf-8") as file:
                history_area.insert(tk.END, file.read())
        else:
            history_area.insert(tk.END, "История пока пуста.")

        history_area.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()