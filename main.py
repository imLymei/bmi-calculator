import customtkinter as ctk
import settings

class App(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color=settings.GREEN)
        self.title('')

        self.mainloop()


App()
