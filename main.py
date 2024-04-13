import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import pygame


class MatryoshkaClicker:
    def __init__(self, master):
        self.master = master
        self.master.title("Розколи Дена!")

        self.matryoshka_count = 0
        self.max_matryoshka_count = 225  # Максимальна кількість Денів
        self.game_over = False

        # Створюємо Label для відображення кількості кліків
        self.label = tk.Label(master, text="")
        self.label.pack()

        self.update_label()

        self.matryoshka_images = [
            Image.open(f"photo/matryoshka{i}.png") for i in range(1, 10)
        ]
        self.matryoshka_photos = [ImageTk.PhotoImage(image) for image in self.matryoshka_images]

        self.click_button = tk.Button(master, image=self.matryoshka_photos[0], command=self.click_matryoshka)
        self.click_button.pack()

        # Ініціалізуємо звуки
        pygame.mixer.init()
        self.hit_sound = pygame.mixer.Sound("sound/hit_sound.wav")
        self.break_sound = pygame.mixer.Sound("sound/break_sound.wav")
        self.angry = pygame.mixer.Sound("sound/angry.wav")
        self.opa = pygame.mixer.Sound("sound/opa.wav")

        # Кнопка для початку гри
        self.restart_button = tk.Button(self.master, text="Почати знову", command=self.restart_game)

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

        # Показуємо повідомлення про перемогу
        messagebox.showinfo("Піздєц!", "Ви розкололи Дена!")

        # Відтворюємо звук образи
        self.play_angry()

    def restart_game(self):
        # Скидаємо стан гри, оновлюємо відображення та показуємо кнопку для кліку
        self.matryoshka_count = 0
        self.game_over = False
        self.update_label()
        self.restart_button.pack_forget()
        self.click_button.pack()

    def update_label(self):
        self.label.config(text=f"Ви в'єбали {self.matryoshka_count} разів!")

    def play_hit_sound(self):
        self.hit_sound.play()

    def play_break_sound(self):
        self.break_sound.play()

    def play_angry(self):
        self.angry.play()

    def play_opa(self):
        self.opa.play()


def main():
    root = tk.Tk()
    app = MatryoshkaClicker(root)
    root.mainloop()


if __name__ == "__main__":
    main()
