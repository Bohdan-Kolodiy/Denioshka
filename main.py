import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import pygame
import time
from google.oauth2 import service_account
from googleapiclient.discovery import build
import io
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
import re

class DifficultyWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Оберіть рівень складності")
        self.difficulty = None
        self.master.geometry("200x200")

        # Create difficulty buttons
        self.easy_button = tk.Button(master, text="Легко", command=self.set_easy)
        self.easy_button.pack()

        self.medium_button = tk.Button(master, text="Середньо", command=self.set_medium)
        self.medium_button.pack()

        self.hard_button = tk.Button(master, text="Складно", command=self.set_hard)
        self.hard_button.pack()

        self.den_button = tk.Button(master, text="Я Денчик", command=self.set_den)
        self.den_button.pack()

    def set_easy(self):
        self.difficulty = "легко"
        self.master.destroy()

    def set_medium(self):
        self.difficulty = "середньо"
        self.master.destroy()

    def set_hard(self):
        self.difficulty = "складно"
        self.master.destroy()

    def set_den(self):
        self.difficulty = "Я Денчик"
        self.master.destroy()

    def get_difficulty(self):
        return self.difficulty


class NicknameWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Введіть свій нікнейм")
        self.nickname = None
        self.master.geometry("200x100")

        self.label = tk.Label(master, text="Нікнейм:")
        self.label.pack()

        self.nickname_entry = tk.Entry(master)
        self.nickname_entry.pack()

        self.confirm_button = tk.Button(master, text="Підтвердити", command=self.set_nickname)
        self.confirm_button.pack()

    def set_nickname(self):
        nickname = self.nickname_entry.get()

        # Перевірка за допомогою регулярного виразу
        if re.match("^[a-zA-Z]+$", nickname):
            self.nickname = nickname
            self.master.destroy()
        else:
            messagebox.showerror("Помилка", "Нікнейм може містити лише літери англійського алфавіту без пробілів та спеціальних символів.")

    def get_nickname(self):
        return self.nickname

class MatryoshkaClicker:
    def __init__(self, master):
        self.master = master
        self.master.title("Розколи Дена!")
        self.master.geometry("400x720")

        self.matryoshka_count = 0
        self.max_matryoshka_count = 225
        self.game_over = False
        self.start_time = None
        self.time_limit = None
        self.timer_id = None
        self.record_time = 0
        self.nickname = None
        self.record_nickname = None
        self.record_label = tk.Label(master, text="Рекорд: --- сек")
        self.record_label.pack(side="right")

        self.label = tk.Label(master, text="")
        self.label.pack()

        self.timer_label = tk.Label(master, text="")
        self.timer_label.pack()

        self.matryoshka_images = [
            Image.open(f"photo/matryoshka{i}.png") for i in range(1, 10)
        ]
        self.matryoshka_photos = [ImageTk.PhotoImage(image) for image in self.matryoshka_images]

        self.click_button = tk.Button(master, image=self.matryoshka_photos[0], command=self.click_matryoshka)
        self.click_button.pack()

        self.win_image = Image.open("photo/Win_den.png")
        self.win_photo = ImageTk.PhotoImage(self.win_image)
        self.win_label = tk.Label(master, image=self.win_photo)

        self.lose_image = Image.open("photo/Lose_den.jpg")
        self.lose_photo = ImageTk.PhotoImage(self.lose_image)
        self.lose_label = tk.Label(master, image=self.lose_photo)

        self.update_label()

        pygame.mixer.init()
        self.hit_sound = pygame.mixer.Sound("sound/hit_sound.wav")
        self.break_sound = pygame.mixer.Sound("sound/break_sound.wav")
        self.angry = pygame.mixer.Sound("sound/angry.wav")
        self.opa = pygame.mixer.Sound("sound/opa.wav")

        self.restart_button_image = Image.open("photo/res_but.png")
        self.restart_button_photo = ImageTk.PhotoImage(self.restart_button_image)
        self.restart_button = tk.Button(self.master, image=self.restart_button_photo, command=self.restart_game,
                                        bd=0)

        self.load_records()

        self.nickname_window = tk.Toplevel(self.master)
        self.nickname_window.transient(self.master)  # Робимо вікно вибору складності підвладним вікну гри
        self.nickname_app = NicknameWindow(self.nickname_window)
        self.nickname_window.lift(self.master)  # Піднімаємо вікно введення нікнейму на передній план
        self.master.wait_window(self.nickname_window)
        self.nickname = self.nickname_app.get_nickname()

        self.select_difficulty()

        self.start_time = time.time()
        self.timer()

    def select_difficulty(self):
        difficulty_window = tk.Toplevel(self.master)
        difficulty_window.transient(self.master)
        difficulty_app = DifficultyWindow(difficulty_window)
        difficulty_window.lift(self.master)
        self.master.wait_window(difficulty_window)
        self.difficulty = difficulty_app.get_difficulty()
        if self.difficulty == "легко":
            self.time_limit = 50
        elif self.difficulty == "середньо":
            self.time_limit = 40
        elif self.difficulty == "складно":
            self.time_limit = 35
        elif self.difficulty == "Я Денчик":
            self.time_limit = 30

    def click_matryoshka(self):
        if not self.game_over:
            self.matryoshka_count += 1
            if self.matryoshka_count % 25 == 0 and self.matryoshka_count // 25 < len(self.matryoshka_photos):
                self.break_matryoshka()
            if self.matryoshka_count >= self.max_matryoshka_count:
                self.end_game()
            else:
                self.play_hit_sound()
            self.update_label()

    def break_matryoshka(self):
        index = self.matryoshka_count // 25
        new_image = self.matryoshka_photos[index]
        self.click_button.config(image=new_image)
        self.click_button.image = new_image
        self.play_break_sound()

    def end_game(self):
        self.game_over = True
        self.click_button.pack_forget()
        self.restart_button.pack()
        if self.start_time is not None:
            current_time = int(time.time() - self.start_time)
        else:
            current_time = 0

        if self.matryoshka_count >= self.max_matryoshka_count:
            messagebox.showinfo("Піздєц!", "Ви розкололи Дена!")
            self.play_angry()
            self.win_label.pack()
        else:
            messagebox.showinfo("Піздєц!", "Ви тепер раб Дена!")
            self.play_opa()
            self.lose_label.pack()

        if current_time < self.record_time or self.record_time == 0:
            self.record_time = current_time
            self.record_label.config(text=f"Рекорд: {self.record_time} сек")
            self.save_records(self.nickname, current_time)

        if self.timer_id is not None:
            self.master.after_cancel(self.timer_id)

        if self.nickname:
            self.save_records(self.nickname, current_time)

    def restart_game(self):
        self.matryoshka_count = 0
        self.game_over = False
        self.start_time = time.time()  # Скидаємо лічильник часу
        self.update_label()
        self.win_label.pack_forget()  # Приховуємо переможну картинку
        self.lose_label.pack_forget()  # Приховуємо картинку поразки
        self.restart_button.pack_forget()
        self.click_button.config(image=self.matryoshka_photos[0])
        self.click_button.pack()

        # Оновлення рекорду з нікнеймом
        self.record_label.config(text=f"Рекорд: {self.record_time} сек, Гравець: {self.record_nickname}")

        # Початок відліку часу
        self.timer()

    def update_label(self):
        self.label.config(text=f"Ви в'єбали {self.matryoshka_count} разів!")

    def update_timer_label(self):
        if self.start_time is not None:
            time_left = max(0, self.time_limit - int(time.time() - self.start_time))
            self.timer_label.config(text=f"Час: {time_left} сек")

    def play_hit_sound(self):
        self.hit_sound.play()

    def play_break_sound(self):
        self.break_sound.play()

    def play_angry(self):
        self.angry.play()

    def play_opa(self):
        self.opa.play()

    def timer(self):
        if self.difficulty != None:
            if not self.game_over:
                self.update_timer_label()
                if self.start_time is not None and time.time() - self.start_time >= self.time_limit:
                    self.lose_game()
                else:
                    self.timer_id = self.master.after(1000, self.timer)
            else:
                print("Гра вже завершена, таймер зупинено")

    def lose_game(self):
        self.game_over = True
        self.click_button.pack_forget()
        self.restart_button.pack()
        messagebox.showinfo("Піздєц!", "Ви тепер раб Дена!")
        self.play_opa()
        self.lose_label.pack()
        if self.timer_id is not None:
            self.master.after_cancel(self.timer_id)

    def save_records(self, nickname, time):
        # Креденціали для доступу до Google API
        credentials_file = 'credentials.json'
        credentials = service_account.Credentials.from_service_account_file(credentials_file)
        service = build('drive', 'v3', credentials=credentials)

        # Ідентифікатор каталогу на Google Диску, де знаходиться файл з рекордами
        self.DRIVE_FOLDER_ID = '17Apnf4tN0mr0B6W_sAmmarL7bQ6hlkRi'

        # Пошук файлу з рекордами за його ім'ям у вказаному каталозі
        results = service.files().list(q=f"name='records.txt' and parents in '{self.DRIVE_FOLDER_ID}'",
                                       fields="files(id)").execute()
        items = results.get('files', [])

        # Якщо файл існує, оновлюємо його з новим рекордом
        if items:
            file_id = items[0]['id']
            request = service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            fh.seek(0)
            content = fh.read().decode('utf-8')
            # Перевірка, чи новий рекорд кращий за попередній
            old_time = int(content.split()[1])
            if time < old_time:
                record = f"{nickname} {time}"  # Збираємо рядок для запису
                media = MediaIoBaseUpload(io.BytesIO(bytes(record, 'utf-8')), mimetype='text/plain')
                # Оновлення файлу з рекордами
                file = service.files().update(fileId=file_id, media_body=media).execute()
                self.record_nickname = nickname
        else:
            # Якщо файл не існує, створюємо новий і записуємо в нього новий рекорд
            file_metadata = {
                'name': 'records.txt',  # Ім'я файлу на Google Диск
                'parents': [self.DRIVE_FOLDER_ID]  # Ідентифікатор каталогу, в який завантажувати файл
            }
            record = f"{nickname} {time}"  # Збираємо рядок для запису
            media = MediaIoBaseUpload(io.BytesIO(bytes(record, 'utf-8')), mimetype='text/plain')
            # Виконання запиту на завантаження файлу
            file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            print('File ID:', file.get('id'))

    def load_records(self):
        # Креденціали для доступу до Google API
        credentials_file = 'credentials.json'
        credentials = service_account.Credentials.from_service_account_file(credentials_file)
        service = build('drive', 'v3', credentials=credentials)

        # Ідентифікатор каталогу на Google Диску, де знаходиться файл з рекордами
        self.DRIVE_FOLDER_ID = '17Apnf4tN0mr0B6W_sAmmarL7bQ6hlkRi'

        # Пошук файлу з рекордами за його ім'ям у вказаному каталозі
        results = service.files().list(q=f"name='records.txt' and parents in '{self.DRIVE_FOLDER_ID}'",
                                       fields="files(id)").execute()
        items = results.get('files', [])

        # Якщо файл існує, виконуємо завантаження
        if items:
            file_id = items[0]['id']
            request = service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            fh.seek(0)
            content = fh.read().decode('utf-8')

            # Розбиваємо рядок на нікнейм та час, якщо вони є
            if content:
                nickname, time_str = content.split()
                self.record_nickname = nickname
                self.record_time = int(time_str)
                self.record_label.config(text=f"Рекорд: {self.record_time} сек, Гравець: {self.record_nickname}")
        else:
            print('Файл не знайдено.')

def main():
    root = tk.Tk()
    app = MatryoshkaClicker(root)
    root.mainloop()

if __name__ == "__main__":
    main()
