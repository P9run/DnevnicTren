from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.uix.checkbox import CheckBox
from kivy.base import runTouchApp
from kivy.lang import Builder
from kivy.uix.scrollview import ScrollView
import sqlite3
sm = ScreenManager()
class MainApp(App):
    def build(self):
        sm.add_widget(FavotitScreen())
        sm.add_widget(NewTreningScreen())
        sm.add_widget(OtchetScreen())
        return sm
class FavotitScreen(Screen):
    def __init__(self):
        super().__init__()
        self.pusk()
        self.name = 'Favorit'
    def pusk(self):
        conn = sqlite3.connect('trening.sqlite')
        cur = conn.cursor()
        cur.execute('''SELECT Data, Tip, Vid, Opisanie, Time, KM, Puls FROM Trening ORDER BY Data DESC''')
        dannie = cur.fetchall()
        conn.close()
        for i in dannie:
            trenirovka =  f"""{i[0]}  {i[1]}: {i[2]}\nВремя в мин.: {i[4]}\nОписание:\n{i[3]}\nКм: {i[5]}\nПульс ср.: {i[6]}\n"""
            self.ids.output.add_widget(Label(text = trenirovka, size_hint_y = None))
    def new_widget(self, data, tip, vid, opisanie, time, km, puls):
        conn = sqlite3.connect('trening.sqlite')
        cur = conn.cursor()
        cur.execute('''SELECT COUNT (Data) FROM Trening''' )
        total_columns = cur.fetchall()
        total_columns = int(total_columns[0][0])
        x = 0
        for i in cur.execute(f'''SELECT Data FROM Trening ORDER BY Data DESC'''):
            x += 1
            if i[0] == data:
                break
        trenirovka = f"""{data}  {tip}: {vid}\nВремя в мин.: {time}\nОписание:\n{opisanie}\nКм: {km}\nПульс ср.: {puls}\n"""
        self.ids.output.add_widget(Label(text=trenirovka, size_hint_y=None), index = (total_columns - x))
        conn.close()
    def otchet(self):
        self.manager.current = 'Otchet'
    def to_new_trening(self, *args):
        self.manager.current='NewTrening'
class NewTreningScreen(Screen):
    def __init__(self):
        super().__init__()
        self.name='NewTrening'
        self.data_pr = None
        self.opisanie_pr = None
        self.radio_clic_pr = None
        self.vide_pr = None
        self.time_pr = None
        self.km_pr = None
        self.puls_pr = None
    def save(self, *args):
        conn = sqlite3.connect('trening.sqlite')
        cur = conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS Trening(Data DATE NOT NULL, Tip TEXT NOT NULL, Vid TEXT NOT NULL, Opisanie TEXT, Time INT, KM FLOAT, Puls INT)''')
        conn.commit()
        cur.execute(f'''INSERT INTO Trening(Data, Tip, Vid, Opisanie, Time, KM, Puls) VALUES (?, ?, ?, ?, ?, ?, ?)''', (self.data_pr, self.radio_clic_pr, self.vide_pr, self.opisanie_pr, self.time_pr, self.km_pr, self.puls_pr))
        conn.commit()
        conn.close()
        self.manager.current = 'Favorit'
        self.manager.get_screen('Favorit').new_widget(self.data_pr,self.radio_clic_pr, self.vide_pr, self.opisanie_pr, self.time_pr, self.km_pr, self.puls_pr)
    def radio_clic(self, instance, value):
        self.radio_clic_pr = value
    def data(self, data):
        self.data_pr = data
    def vide(self, vid):
        self.vide_pr = vid
    def opisanie(self, opisanie):
        self.opisanie_pr = opisanie
    def time(self, time):
        self.time_pr = time
    def km(self, km):
        self.km_pr = km
    def puls(self, puls):
        self.puls_pr = puls
class OtchetScreen(Screen):
    def __init__(self):
        super().__init__()
        self.name = 'Otchet'
    def nazad(self):
        self.manager.current = 'Favorit'
    def sformirovate(self):
        ot = self.ids.ot.text
        do = self.ids.do.text
        conn = sqlite3.connect('trening.sqlite')
        cur = conn.cursor()
        cur.execute('''SELECT COUNT (*) FROM Trening WHERE Data >= ? AND Data <= ? AND Tip != 'Соревнования' ''', (ot, do))
        kol_tren = cur.fetchall()
        cur.execute('''SELECT COUNT (DISTINCT Data) FROM Trening WHERE Data >= ? AND Data <= ? AND Tip != 'Соревнования' ''', (ot, do))
        kol_tren_day = cur.fetchall()
        cur.execute('''SELECT DISTINCT Vid FROM Trening WHERE Data >= ? AND Data <= ? AND Tip != 'Соревнования' ''', (ot, do))
        spisok_tren = cur.fetchall()
        str_vid_and_kol_tren = ''
        for i in spisok_tren:
            cur.execute('''SELECT COUNT (*) FROM Trening WHERE Data >= ? AND Data <= ? AND Vid == ? AND Tip != 'Соревнования' ''', (ot, do, i[0]))
            x = cur.fetchall()
            str_vid_and_kol_tren += f'{i[0]}: {x[0][0]}\n'
        cur.execute('''SELECT SUM (Time) FROM Trening WHERE Data >= ? AND Data <= ? AND Tip != 'Соревнования' ''', (ot, do))
        time = cur.fetchall()
        time = f'{time[0][0] // 60} ч. {time[0][0] - ((time[0][0] // 60) * 60)} мин.'
        cur.execute('''SELECT SUM (Km) FROM Trening WHERE Data >= ? AND Data <= ? AND Tip != 'Соревнования' ''', (ot, do))
        km = cur.fetchall()
        cur.execute('''SELECT COUNT (*) FROM Trening WHERE Data >= ? AND Data <= ? AND Tip == 'Соревнования' ''', (ot, do))
        sorev = cur.fetchall()
        conn.close()
        otchetnoste = f'Количество тренировок: {kol_tren[0][0]} \nКоличество тренировочных дней: {kol_tren_day[0][0]}\n{str_vid_and_kol_tren}\nОбщий объём нагрузки: {time}\n{' ' * 42}{km[0][0]} км\nСоревнований: {sorev[0][0]}'
        self.ids.otchet.text = otchetnoste
app = MainApp()
app.run()