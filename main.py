import customtkinter as ctk
import settings

try:
    from ctypes import windll, byref, sizeof, c_int
except:
    pass


def sign(value):
    return abs(value)/value


class App(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color=settings.GREEN)
        self.title('')
        self.iconbitmap('./src/empty.ico')
        self.geometry('400x400')
        self.resizable(False, False)
        self.change_title_bar_color()

        self.columnconfigure(0, weight=1)
        self.rowconfigure((0, 1, 2, 3), weight=1, uniform='a')

        self.is_meter = ctk.BooleanVar(value=True)
        self.height_int = ctk.IntVar(value=170)
        self.weight_float = ctk.DoubleVar(value=65)
        self.bmi_string = ctk.StringVar()
        self.update_bmi()

        self.height_int.trace('w', self.update_bmi)
        self.weight_float.trace('w', self.update_bmi)
        self.is_meter.trace('w', self.update_units)

        ResultText(self, self.bmi_string)
        self.weight_input = WeightInput(self, self.weight_float, self.is_meter)
        self.height_input = HeightInput(self, self.height_int, self.is_meter)
        UnitSwitcher(self, self.is_meter)

        self.mainloop()

    # ONLY WORKS ON WINDOWS!!!
    def change_title_bar_color(self):
        try:
            HWND = windll.user32.GetParent(self.winfo_id())
            windll.dwmapi.DwmSetWindowAttribute(HWND, 35, byref(c_int(settings.TITLE_HEX_COLOR)), sizeof(c_int))
        except:
            pass

    def update_bmi(self, *args):
        height_meter = self.height_int.get()/100
        weight_kg = self.weight_float.get()
        bmi_result = round(weight_kg / height_meter ** 2, 2)
        self.bmi_string.set(str(bmi_result))

    def update_units(self, *args):
        self.height_input.update_string(self.height_int.get())
        self.weight_input.update_text(self.weight_float.get())


class ResultText(ctk.CTkLabel):
    def __init__(self, master, text_var):
        text_font = ctk.CTkFont(family=settings.FONT, size=settings.MAIN_TEXT_SIZE, weight='bold')
        super().__init__(master, text='22.5', font=text_font, text_color=settings.WHITE, textvariable=text_var)

        self.grid(column=0, row=0, rowspan=2, sticky='nswe')


class WeightInput(ctk.CTkFrame):
    def __init__(self, master, weight_var, is_meter):
        super().__init__(master, fg_color=settings.WHITE)

        self.grid(column=0, row=2, sticky='nswe', padx=10, pady=10)

        self.rowconfigure(0, weight=1, uniform='b')
        self.columnconfigure(0, weight=2, uniform='b')
        self.columnconfigure(1, weight=1, uniform='b')
        self.columnconfigure(2, weight=3, uniform='b')
        self.columnconfigure(3, weight=1, uniform='b')
        self.columnconfigure(4, weight=2, uniform='b')

        self.output_weight = ctk.StringVar(value='65.0kg')
        self.is_meter = is_meter

        text_font = ctk.CTkFont(family=settings.FONT, size=settings.INPUT_FONT_SIZE)
        self.label = ctk.CTkLabel(self, text_color=settings.BLACK, font=text_font, textvariable=self.output_weight)
        self.label.grid(column=2, row=0)

        self.create_button('-', text_font, 'ns', 0, lambda: self.update_weight(weight_var, -1))
        self.create_button('-', text_font, '', 1, lambda: self.update_weight(weight_var, -0.1), padding=4)
        self.create_button('+', text_font, '', 3, lambda: self.update_weight(weight_var, 0.1), padding=4)
        self.create_button('+', text_font, 'ns', 4, lambda: self.update_weight(weight_var, 1))

    def create_button(self, text, font, sticky, column, function, padding=8):
        minus_button = ctk.CTkButton(self, text=text, font=font, text_color=settings.BLACK,
                                          fg_color=settings.LIGHT_GRAY, hover_color=settings.GRAY,
                                          corner_radius=settings.BUTTON_CORNER_RADIUS, command=function)
        minus_button.grid(column=column, row=0, sticky=sticky, padx=padding, pady=padding)

    def update_weight(self, weight_var, value):
        if self.is_meter.get():
            real_value = value
        else:
            real_value = 0.453592*sign(value) if abs(value) == 1 else 0.453592/16*sign(value)
            print(real_value)

        weight_var.set(weight_var.get() + real_value)
        self.update_text(weight_var.get())

    def update_text(self, value):
        if self.is_meter.get():
            self.output_weight.set(f'{round(value, 1)}kg')
        else:
            raw_ounces = value * 2.20462 * 16
            pounds, ounces = divmod(raw_ounces, 16)
            self.output_weight.set(f'{int(pounds)}lb {int(ounces)}oz')


class HeightInput(ctk.CTkFrame):
    def __init__(self, master, height_var, is_meter):
        super().__init__(master, fg_color=settings.WHITE)

        self.grid(column=0, row=3, sticky='nswe', padx=10, pady=10)

        self.output_string = ctk.StringVar(value='1.70m')
        self.is_meter = is_meter

        slider = ctk.CTkSlider(self, button_color=settings.GREEN, button_hover_color=settings.DARK_GREEN,
                               progress_color=settings.GREEN, fg_color=settings.LIGHT_GRAY, variable=height_var,
                               from_=100, to=250, command=self.update_string)
        slider.pack(side='left', expand=True, fill='x', padx=10, pady=10)

        output_text = ctk.CTkLabel(self, text_color=settings.BLACK,
                                   font=ctk.CTkFont(family=settings.FONT, size=settings.INPUT_FONT_SIZE),
                                   textvariable=self.output_string)
        output_text.pack(side='left', padx=20)

    def update_string(self, value):
        if self.is_meter.get():
            value_str = str(round(value))
            meter = value_str[0]
            centimeters = value_str[1:]
            self.output_string.set(f'{meter}.{centimeters}m')
        else:
            feet, inches = divmod(value / 2.54, 12)
            self.output_string.set(f'{int(feet)}\' {int(inches) if inches > 10 else f"0{int(inches)}"}\"')


class UnitSwitcher(ctk.CTkLabel):
    def __init__(self, master, is_meter):
        super().__init__(master, text='metric', text_color=settings.DARK_GREEN,
                         font=ctk.CTkFont(family=settings.FONT, size=settings.SWITCH_FONT_SIZE, weight='bold'))

        self.place(relx=0.98, rely=0, anchor='ne')

        self.is_meter = is_meter

        self.bind('<Button>', self.change_units)

    def change_units(self, event):
        self.is_meter.set(not self.is_meter.get())

        if self.is_meter.get():
            self.configure(text='metric')
        else:
            self.configure(text='imperial')


if __name__ == '__main__':
    App()
