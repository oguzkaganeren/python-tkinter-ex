from tkinter import ttk
from tkinter import *
from datetime import datetime
import sys

import sqlite3

class Product:
    # connection dir property
    db_name = 'database.db'

    def __init__(self, window):
        # Initializations 
        self.wind = window
        self.wind.title('Market Uygulaması')
        
        Grid.rowconfigure(self.wind, 0, weight=1)
        Grid.columnconfigure(self.wind, 0, weight=1)

        # Creating a Frame Container 
        root = LabelFrame(self.wind, text = 'Yeni Ürün Kaydı')
        root.grid(row = 0, column = 0, columnspan = 3)
        self.menubar = Menu(window)  
        file = Menu(self.menubar, tearoff=0)  
        file.add_command(label="Ekle/Düzenle/Sil",font=(None, 24),command=self.openCrud)  
        self.menubar.add_cascade(label="Ürün",font=(None, 24),  menu=file)  
        self.wind.config(menu=self.menubar)  

    
    # Function to Execute Database Querys
    def run_query(self, query, parameters = ()):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            result = cursor.execute(query, parameters)
            conn.commit()
        return result

    # Get Products from Database
    def get_products(self):
        # cleaning Table 
        records = self.tree.get_children()
        for element in records:
            self.tree.delete(element)
        # getting data
        query = 'SELECT * FROM product ORDER BY name DESC'
        db_rows = self.run_query(query)
        # filling data
        for row in db_rows:
            self.tree.insert('', 0, text = row[1], values = (row[4],row[2],row[3]))

    def get_product_with_barcode(self,barcode):
        # cleaning Table 
        records = self.tree.get_children()
        for element in records:
            self.tree.delete(element)
        # getting data
        query = 'SELECT * FROM product where barcode = (?) ORDER BY name DESC'
        db_rows = self.run_query(query,barcode)
        # filling data
        for row in db_rows:
            self.tree.insert('', 0, text = row[1], values = (row[4],row[2],row[3]))

    # User Input Validation
    def validation(self):
        return len(self.name.get()) != 0 and len(self.price.get()) and len(self.barcode.get()) != 0

    def add_product(self):
        if self.validation():
            query = 'INSERT INTO product VALUES(NULL, ?, ?, ?, ?)'
            now = datetime.now()
            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
            parameters =  (self.barcode.get(), self.name.get(), float(self.price.get().replace(',','.')), dt_string)
            self.run_query(query, parameters)
            self.message['text'] = '{} eklendi.'.format(self.name.get())
            self.barcode.delete(0, END)
            self.name.delete(0, END)
            self.price.delete(0, END)
        else:
            self.message['text'] = 'Barkod, isim ve fiyat alanları doldurulmalıdır.'
        self.get_products()

    def delete_product(self):
        self.message['text'] = ''
        try:
           self.tree.item(self.tree.selection())['values'][1]
        except IndexError as e:
            self.message['text'] = 'Lütfen bir kayıt seçiniz'
            return
        self.message['text'] = ''
        barcode = self.tree.item(self.tree.selection())['text']
        query = 'DELETE FROM product WHERE barcode = ?'
        self.run_query(query, (barcode, ))
        self.message['text'] = '{} silinmiştir.'.format(barcode)
        self.get_products()

    def edit_product(self):
        self.message['text'] = ''
        try:
            self.tree.item(self.tree.selection())['values'][1]
        except IndexError as e:
            self.message['text'] = 'Lütfen, bir kayıt seçin'
            return
        barcode = self.tree.item(self.tree.selection())['text']
        name = self.tree.item(self.tree.selection())['values'][1]
        old_price = self.tree.item(self.tree.selection())['values'][2]
        self.edit_wind = Toplevel()
        self.edit_wind.title = 'Ürünü Düzenle'
       
        Label(self.edit_wind,font=(None, 24), text = 'Yeni Adı:').grid(row = 1, column = 1)
        new_name = Entry(self.edit_wind, font=(None, 24), textvariable = StringVar(self.edit_wind, value = name))
        new_name.grid(row = 1, column = 2)

        
        Label(self.edit_wind,font=(None, 24), text = 'Yeni Fiyatı:').grid(row = 3, column = 1)
        new_price= Entry(self.edit_wind, font=(None, 24), textvariable = StringVar(self.edit_wind, value = old_price))
        new_price.grid(row = 3, column = 2)
        Label(self.edit_wind,font=(None, 24), text = '₺').grid(row = 3, column = 3)

        btn=Button(self.edit_wind, text = 'Güncelle',bg="#4CAF50",font=(None, 24), command = lambda: self.edit_records(barcode,new_name.get(), float(new_price.get().replace(',','.')))).grid(row = 4, column = 2, sticky = W)
        
        self.edit_wind.mainloop()

    def edit_records(self,barcode, name, price):
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        query = 'UPDATE product SET name = ?, price = ?,editDate = ? WHERE barcode = ?'
        parameters = (name, price,dt_string,barcode)
        self.run_query(query, parameters)
        self.edit_wind.destroy()
        self.message['text'] = '{} güncellendi'.format(name)
        self.get_products()
    

    def _onKeyRelease(self,event):
        ctrl  = (event.state & 0x4) != 0
        if event.keycode==88 and  ctrl and event.keysym.lower() != "x": 
            event.widget.event_generate("<<Cut>>")

        if event.keycode==86 and  ctrl and event.keysym.lower() != "v": 
            event.widget.event_generate("<<Paste>>")

        if event.keycode==67 and  ctrl and event.keysym.lower() != "c":
            event.widget.event_generate("<<Copy>>")
        
        if event.keycode==36 or event.keycode==104:
            self.search()

    def search(self, item=''):
        children = self.tree.get_children(item)
        for child in children:
            text = self.tree.item(child, 'text')
            if str(text).startswith(self.entry.get()):
                self.tree.selection_set(child)
                self.tree.see(child)
                self.entry.delete(0, END)
                return True
            else:
                res = self.search(child)
                if res:
                    self.entry.delete(0, END)
                    return True

    def openCrud(self):
        # Creating a Frame Container 
        
        frame = LabelFrame(Toplevel(), text = 'Yeni Ürün Kaydı')
        frame.grid(row = 0, column = 0, columnspan = 3,sticky="nsew")

        # Barcode Input
        Label(frame, text = 'Barkod: ',font=(None, 24), height=2).grid(row = 1, column = 0)
        self.barcode = Entry(frame,font=(None, 24), validate='key')
        self.barcode.focus()
        self.barcode.grid(row = 1, column = 1, sticky="nsew")
        self.barcode.bind_all("<Key>", self._onKeyRelease, "+")

        # Name Input
        Label(frame, text = 'Adı:',font=(None, 24), height=2).grid(row = 2, column = 0)
        self.name = Entry(frame,font=(None, 24))
        self.name.grid(row = 2, column = 1, sticky="nsew")
        self.name.bind_all("<Key>", self._onKeyRelease, "+")

        # Price Input
        Label(frame, text = 'Fiyat: ',font=(None, 24), height=2).grid(row = 3, column = 0)
        self.price = Entry(frame,font=(None, 24), validate='key')
        self.price.grid(row = 3, column = 1, sticky="nsew")
        self.price.bind_all("<Key>", self._onKeyRelease, "+")

        # Button Add Product 
        saveButton = Button(frame, text = 'Ürünü Kaydet',font=(None,24), command = self.add_product)
        saveButton["bg"]="#9CCC65"
        saveButton.grid(row = 4, columnspan = 2, sticky = W + E)

        # Output Messages 
        self.message = Label(frame,text = '',font=(None, 24), fg = 'red')
        self.message.grid(row = 5, column = 0, columnspan = 2, sticky = W + E)

        style = ttk.Style()
        style.configure("Treeview.Heading", font=(None, 18))
        style.configure("Treeview", font=(None, 15))   

        # Table
        self.tree = ttk.Treeview(frame,height = 10, columns=("#0","#1","#2"))
        self.tree.grid(row = 7, column = 0, columnspan = 2, sticky="nsew")
        self.tree.heading('#0', text = 'Barkod', anchor = CENTER)
        self.tree.heading('#1', text = 'Değiştirildiği Tarih', anchor = CENTER)
        self.tree.heading('#2', text = 'Adı', anchor = CENTER)
        self.tree.heading('#3', text = 'Fiyat(₺)', anchor = CENTER)
        
        vsb = Scrollbar(self.tree, orient="vertical", command=self.tree.yview)
        vsb.place(relx=0.985, rely=0.135, relheight=0.850, relwidth=0.015)     
        self.tree.configure(yscrollcommand=vsb.set)

        self.entry = Entry(frame,text='Ara:',font=(None, 24))
        self.entry.grid(row = 6, column = 0, sticky="nsew")
        self.button = Button(frame,text='Ara',font=(None, 24), bg="#4CAF50", command=self.search)
        self.button.grid(row = 6, column = 1, sticky="nsew")
        self.button.bind_all("<Key>", self._onKeyRelease, "+")

        # Buttons
        deleteButton = Button(frame,text = 'Sil',font=(None, 24), command = self.delete_product)
        deleteButton["bg"]="#e53935"
        deleteButton.grid(row = 8, column = 1, sticky="nsew")
        editButton = Button(frame,text = 'Düzenle',font=(None, 24), command = self.edit_product)
        editButton["bg"]="#4CAF50"
        editButton.grid(row = 8, column = 0, sticky="nsew")

        # Filling the Rows
        self.get_products()


if __name__ == '__main__':
    window = Tk()
    window.attributes('-zoomed', True)
    application = Product(window)
    window.mainloop()
