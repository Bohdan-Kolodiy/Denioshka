import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import pygame
import time
import os.path


class DifficultyWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Оберіть рівень складності")
        self.difficulty = None
        self.master.geometry("200x200")

        # Create difficulty buttons
        self.easy_button = tk.Button(master, text="Daneasy", command=self.set_easy)
        self.easy_button.pack()

        self.medium_button = tk.Button(master, text="Danedium", command=self.set_medium)
        self.medium_button.pack()

        self.hard_button = tk.Button(master, text="Hardancore", command=self.set_hard)
        self.hard_button.pack()

        self.hard_button = tk.Button(master, text="I`m Den", command=self.set_den)
        self.hard_button.pack()

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

class MatryoshkaClicker:
    def __init__(self, master):
        self.master = master
        self.master.title("Розколи Дена!")
        self.master.geometry("400x720")  # Фіксований розмір вікна

        self.matryoshka_count = 0
        self.max_matryoshka_count = 225  # Максимальна кількість Денів
        self.game_over = False
        self.start_time = None  # Час початку гри (None, поки гра не почалася)
        self.time_limit = None  # Час для гри (None, поки гравець не вибрав складність)
        self.timer_id = None
        self.record_time = 0  # Рекорд часу для перемоги

        self.record_label = tk.Label(master, text="Рекорд: --- сек")
        self.record_label.pack(side="right")

        # Створюємо мітку для відображення кількості кліків
        self.label = tk.Label(master, text="")
        self.label.pack()

        # Мітка для відображення таймера
        self.timer_label = tk.Label(master, text="")
        self.timer_label.pack()

        self.matryoshka_images = [
            Image.open(f"photo/matryoshka{i}.png") for i in range(1, 10)
        ]
        self.matryoshka_photos = [ImageTk.PhotoImage(image) for image in self.matryoshka_images]

        self.click_button = tk.Button(master, image=self.matryoshka_photos[0], command=self.click_matryoshka)
        self.click_button.pack()

        # Мітка для переможної картинки
        self.win_image = Image.open("photo/Win_den.png")
        self.win_photo = ImageTk.PhotoImage(self.win_image)
        self.win_label = tk.Label(master, image=self.win_photo)

        # Мітка для картинки поразки
        self.lose_image = Image.open("photo/Lose_den.jpg")
        self.lose_photo = ImageTk.PhotoImage(self.lose_image)
        self.lose_label = tk.Label(master, image=self.lose_photo)

        self.update_label()

        # Ініціалізуємо звуки
        pygame.mixer.init()
        self.hit_sound = pygame.mixer.Sound("sound/hit_sound.wav")
        self.break_sound = pygame.mixer.Sound("sound/break_sound.wav")
        self.angry = pygame.mixer.Sound("sound/angry.wav")
        self.opa = pygame.mixer.Sound("sound/opa.wav")

        # Кнопка для рестарту гри
        self.restart_button_image = Image.open("photo/res_but.png")  # Завантажуємо зображення кнопки рестарту
        self.restart_button_photo = ImageTk.PhotoImage(self.restart_button_image)  # Створюємо фото зображення
        self.restart_button = tk.Button(self.master, image=self.restart_button_photo, command=self.restart_game,
                                        bd=0)  # Створюємо кнопку з фото

        # Завантаження рекордів з файлу
        self.load_records()

        self.select_difficulty()

        self.start_time = time.time()
        # Початок відліку часу
        self.timer()

    def select_difficulty(self):
        difficulty_window = tk.Toplevel(self.master)
        difficulty_window.transient(self.master)  # Робимо вікно вибору складності підвладним вікну гри
        difficulty_app = DifficultyWindow(difficulty_window)
        difficulty_window.lift(self.master)  # Піднімаємо вікно складності на передній план
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
                self.play_hit_sound()  # Відтворення звуку удару
            self.update_label()

    def break_matryoshka(self):
        index = self.matryoshka_count // 25
        new_image = self.matryoshka_photos[index]
        self.click_button.config(image=new_image)
        self.click_button.image = new_image
        self.play_break_sound()  # Відтворення звуку розколу

    def end_game(self):
        self.game_over = True

        # Видаляємо кнопку для кліку та показуємо кнопку "Почати знову"
        self.click_button.pack_forget()
        self.restart_button.pack()

        # Підрахунок часу, затраченого на цю гру
        if self.start_time is not None:  # Додана перевірка на None
            current_time = int(time.time() - self.start_time)
        else:
            current_time = 0

        # Показуємо повідомлення про перемогу або поразку
        if self.matryoshka_count >= self.max_matryoshka_count:
            messagebox.showinfo("Піздєц!", "Ви розкололи Дена!")
            self.play_angry()
            self.win_label.pack()
        else:
            messagebox.showinfo("Піздєц!", "Ви тепер раб Дена!")
            self.play_opa()
            self.lose_label.pack()

        # Оновлення рекорду, якщо цей час є новим рекордом
        if current_time < self.record_time or self.record_time == 0:
            self.record_time = current_time
            self.record_label.config(text=f"Рекорд: {self.record_time} сек")
            # Збереження нового рекорду у файлі
            self.save_records()

        # Зупиняємо таймер
        if self.timer_id is not None:
            self.master.after_cancel(self.timer_id)

    def restart_game(self):
        # Скидаємо стан гри, оновлюємо відображення та показуємо кнопку для кліку
        self.matryoshka_count = 0
        self.game_over = False
        self.start_time = time.time()  # Скидаємо лічильник часу
        self.update_label()
        self.win_label.pack_forget()  # Приховуємо переможну картинку
        self.lose_label.pack_forget()  # Приховуємо картинку поразки
        self.restart_button.pack_forget()
        self.click_button.config(image=self.matryoshka_photos[0])
        self.click_button.pack()

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
                self.update_timer_label()  # Оновлення відображення таймера
                if self.start_time is not None and time.time() - self.start_time >= self.time_limit:
                    print("Гра закінчилася через перевищення часового ліміту")
                    self.lose_game()
                else:
                    # Продовження відліку часу
                    self.timer_id = self.master.after(1000, self.timer)
            else:
                print("Гра вже завершена, таймер зупинено")

    def lose_game(self):
        self.game_over = True

        # Видаляємо кнопку для кліку та показуємо кнопку "Почати знову"
        self.click_button.pack_forget()
        self.restart_button.pack()

            # Показуємо повідомлення про поразку
        messagebox.showinfo("Піздєц!", "Ви тепер раб Дена!")

            # Відтворюємо звук образи
        self.play_opa()

            # Показуємо картинку поразки
        self.lose_label.pack()

            # Зупиняємо таймер
        if self.timer_id is not None:
            self.master.after_cancel(self.timer_id)

    def save_records(self):
        with open("records.txt", "w") as file:
            file.write(str(self.record_time))

    def load_records(self):
        filename = "records.txt"
        if os.path.exists(filename):
            with open(filename, "r") as file:
                try:
                    self.record_time = int(file.read())
                    self.record_label.config(text=f"Рекорд: {self.record_time} сек")
                except ValueError:
                    pass

def main():
    root = tk.Tk()
    app = MatryoshkaClicker(root)
    root.mainloop()

if __name__ == "__main__":
    main()
