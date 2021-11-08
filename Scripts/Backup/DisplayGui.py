import ctypes
import os
import signal
import threading
import Scripts.NSE as NSE
import pandas as pd
import tkinter as tk
from pandastable import Table, TableModel, config
from tkinter import ttk
from idlelib.tooltip import *
import re
import time
from tkinter import *
import multiprocessing

from ttkwidgets.autocomplete import AutocompleteCombobox

# import PIL
# from tkinter.tix import *

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)


class DisplayGui():
    FOREGROUND = 'black'
    BACKGROUND = '#ECB8A8'
    TITLE = 'MY STOCK DATA'
    ACTIVEBACKGROUND = '#2596BE'
    ACTIVEFOREGROUND = '#ECB8A8'
    root = Tk()
    nse_class_object = NSE.NseIndiaStockData()
    stk_price_update_flag = False

    display_pan_window = PanedWindow(root, orient='horizontal', bg='black', bd=10, relief=RAISED, name='pan_window')
    display_pan_window.pack(expand=False, fill=BOTH)

    ticker_label = Label(display_pan_window, bg='gray7', fg='RosyBrown1', bd=5, relief=RAISED)
    ticker_label.pack(expand=False, fill=BOTH)
    thread1 = threading.Thread(target=nse_class_object.ticker, args=[ticker_label, root])
    thread1.daemon = True
    thread1.start()

    nse_data_display_lbl_frame = LabelFrame(display_pan_window, text='NSE STOCK DATA')

    my_stock_data_display_lbl_frame = LabelFrame(display_pan_window, text='', bg='black', fg='cyan',
                                                 relief=RAISED, bd=5,
                                                 font='Helvetica 9 bold')
    stock_details_main_frame = LabelFrame(my_stock_data_display_lbl_frame, text='', bg='black', fg='cyan',
                                          relief=RAISED, bd=0,
                                          font='Helvetica 9 bold')

    display_pan_window1 = PanedWindow(display_pan_window, orient='horizontal',
                                      bg=ACTIVEBACKGROUND,
                                      width=200,
                                      height=20,
                                      relief=RAISED,
                                      bd=3
                                      )
    nse_option_menu_display_lbl_frame = LabelFrame(display_pan_window, name='nse_label_menu_frame',
                                                   text='NSE OPTION MENU', bg='black', fg='cyan',
                                                   relief=RAISED,
                                                   font='Helvetica 9 bold')

    @staticmethod
    def thread_stop(thread_name):
        for proc in threading.enumerate():
            if proc.name == thread_name:
                exc = ctypes.py_object(SystemExit)
                res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
                    ctypes.c_long(proc.ident), exc)
                if res == 0:
                    raise ValueError("nonexistent thread id")
                elif res > 1:
                    # """if it returns a number greater than one, you're in trouble,
                    # and you should call it again with exc=NULL to revert the effect"""
                    ctypes.pythonapi.PyThreadState_SetAsyncExc(proc.ident, None)
                    raise SystemError("PyThreadState_SetAsyncExc failed")

    @staticmethod
    def disp_stock_price_detail_in_gui(stk_symbol):
        """
            This method is to display the price details of the selected stock in the stock details frame

        """
        while True:
            # On refresh delete the existing price information frame to display the latest price details
            for obj in DisplayGui.stock_details_main_frame.pack_slaves():
                if obj.winfo_name() == 'stk_price_info_lbl_frame':
                    obj.destroy()

            stock_price_information = LabelFrame(DisplayGui.stock_details_main_frame, text='Stock - Price Information',
                                                 bg='black', fg='cyan', relief=RAISED,
                                                 bd=8, name='stk_price_info_lbl_frame',
                                                 font='Helvetica 9 bold')
            stock_price_information.pack(expand=TRUE, fill=BOTH)
            canvas_object_present = stock_price_information.pack_slaves()
            for cop in canvas_object_present:
                cop.destroy()

            stk_price_detail_received = DisplayGui.nse_class_object.stock_quote_details(stk_symbol,
                                                                                        'priceInfo')
            print(stk_price_detail_received)
            stk_price_info_field_list = {
                'Last Trade Price -': 'lastPrice',
                'Change(in Rs.) -': 'change',
                'Change(in %) -': 'pChange',
                'Previous Close -': 'previousClose',
                'Open -': 'open',
                'Close -': 'close',
                'VWAP -': 'vwap',
                'Lower Band -': 'lowerCP',
                'Upper Band -': 'upperCP',
                'Price Band -': 'pPriceBand'

            }
            row_cntr = 0
            col_cntr = 0
            for lbl, df_column in stk_price_info_field_list.items():
                try:
                    get_value = round(float(stk_price_detail_received[df_column][0]), 2)
                except:
                    get_value = "-"

                stk_price = Label(stock_price_information, text=lbl, bg='black', fg='Dodgerblue2',
                                  font='Helvetica 10 bold')
                stk_price.grid(row=row_cntr, column=col_cntr, padx=5, pady=8, ipadx=10, sticky='w')

                stk_val = Label(stock_price_information, text=get_value, bg='black',
                                fg='burlywood1', font='Helvetica 10 bold')
                stk_val.grid(row=row_cntr, column=col_cntr + 1, padx=15, pady=8, ipadx=20, sticky='e')
                row_cntr = row_cntr + 1
                if row_cntr > 3:
                    row_cntr = 0
                    col_cntr = col_cntr + 2
            DisplayGui.root.update()

            time.sleep(5)

    @staticmethod
    def disp_stock_detail_in_gui(stk_symbol):
        """
            This method is to display the details of the selected stock in the stock details frame

        """
        canvas_object_present = DisplayGui.stock_details_main_frame.pack_slaves()
        for cop in canvas_object_present:
            cop.destroy()

        DisplayGui.stock_details_main_frame.pack(expand=TRUE, fill=BOTH)
        stock_information = LabelFrame(DisplayGui.stock_details_main_frame, text='Stock - General Information',
                                       bg='black', fg='cyan', relief=RAISED, name='stk_gen_info_lbl_frame',
                                       bd=8,
                                       font='Helvetica 9 bold')
        stock_information.pack(expand=False, fill=Y, anchor='n')
        stk_quote_detail_received = DisplayGui.nse_class_object.stock_quote_details(stk_symbol,
                                                                                    'info')
        stk_info_field_list = {
            'ISIN -': 'isin',
            'Symbol -': 'symbol',
            'Company Name -': 'companyName',
            'Industry -': 'industry',
            'Suspended -': 'isSuspended',
            'Delisted -': 'isDelisted',
            'Top 10 -': 'isTop10'

        }
        row_cntr = 0
        col_cntr = 0
        for lbl, df_column in stk_info_field_list.items():
            try:
                get_value = stk_quote_detail_received[df_column][0]
            except:
                get_value = "NA"

            stk_lbl = Label(stock_information, text=lbl, bg='black', fg='Dodgerblue2',
                            font='Helvetica 10 bold')
            stk_lbl.grid(row=row_cntr, column=col_cntr, padx=5, pady=8, ipadx=10, sticky='w')

            check_true_false = "No" if get_value == False else "Yes" if \
                get_value == True else get_value

            stk_val = Label(stock_information, text=check_true_false, bg='black',
                            fg='burlywood1', font='Helvetica 10 bold')
            stk_val.grid(row=row_cntr, column=col_cntr + 1, padx=15, pady=8, ipadx=20, sticky='e')
            row_cntr = row_cntr + 1
            if row_cntr > 3:
                row_cntr = 0
                col_cntr = col_cntr + 2

        DisplayGui.thread_stop('stk_price_update_thread')
        thread_disp_price = threading.Thread(name='stk_price_update_thread',
                                             target=DisplayGui.disp_stock_price_detail_in_gui, args=[stk_symbol])
        thread_disp_price.daemon = True
        thread_disp_price.start()
        DisplayGui.root.update()

    @staticmethod
    def filtered(*args):
        if len(DisplayGui.stock_symbol.get()) > 0:
            pattern = "\\S*" + DisplayGui.stock_symbol.get() + ".*"
            symbol_data = DisplayGui.nse_class_object.symbol_filter(DisplayGui.stock_symbol.get())
            update_list = [x for x in symbol_data[symbol_data["result_sub_type"] == 'equity']["symbol"].values if
                           re.compile(pattern, flags=re.IGNORECASE).match(x)]
            DisplayGui.stock_entry['values'] = update_list
            # To get the details for the stock quote selected by the user
            stock_quote_symbol = symbol_data[symbol_data['symbol'] == DisplayGui.stock_symbol.get().upper()][
                "symbol"].values
            print(stock_quote_symbol)
            if len(stock_quote_symbol) == 1:  # Matching should be only one value.It should not be empty / greater
                # than 1 to get the details
                DisplayGui.thread_stop('stk_price_update_thread')
                DisplayGui.disp_stock_detail_in_gui(stock_quote_symbol[0])

    stock_symbol = tk.StringVar()
    stock_symbol.trace('w', filtered)
    stock_entry = ttk.Combobox(my_stock_data_display_lbl_frame, width=60, font='Helvetica 9 bold',
                               textvariable=stock_symbol)

    btn_display_lbl_frame = LabelFrame(display_pan_window, bg=ACTIVEBACKGROUND)
    btn_display_lbl_frame.pack(padx=0, pady=0, ipadx=0, ipady=0, fill=BOTH, side=LEFT, expand=FALSE)

    @staticmethod
    def exit_application(btn_name):
        DisplayGui.root.quit()

    @staticmethod
    def create_live_data_menu2_item(menu_dict_values, btn_selected, menu1_selected):
        val_selected = StringVar()
        val_selected.set(menu1_selected + "- Option")
        nse_option_menu2_display_lbl_frame = LabelFrame(DisplayGui.nse_option_menu_display_lbl_frame,
                                                        name='nse_label_menu2_frame',
                                                        text=menu1_selected + "- Option", bg='black', fg='cyan',
                                                        relief=RAISED,
                                                        font='Helvetica 9 bold')
        nse_option_menu2_display_lbl_frame.pack(padx=5, pady=5, ipadx=5, ipady=5, fill=BOTH, expand=False)

        opt = OptionMenu(nse_option_menu2_display_lbl_frame, val_selected, *menu_dict_values[menu1_selected],
                         # name='nse_live_menu2',
                         command=lambda menu2_selected=val_selected.get(): DisplayGui.get_nse_data(btn_selected,
                                                                                                   menu1_selected,
                                                                                                   menu2_selected))
        opt.pack(anchor='e', fill=BOTH, pady=3)

    @staticmethod
    def create_option_menu(menu_dict_values, btn_selected):

        val_selected = StringVar()
        # To verify already options are displaying for selection
        canvas_object_present = len(DisplayGui.nse_option_menu_display_lbl_frame.pack_slaves())
        if canvas_object_present == 0:
            lbl = Label(DisplayGui.nse_option_menu_display_lbl_frame, text=btn_selected + '- OPTIONS',
                        bg='lemonchiffon4',
                        relief=RAISED)
            lbl.pack(fill=BOTH, pady=3)
            if btn_selected == 'NSE PRE-MARKET DATA':
                val_selected.set("NSE Pre-Market Data Options")
                opt = OptionMenu(DisplayGui.nse_option_menu_display_lbl_frame, val_selected, *menu_dict_values,
                                 command=lambda opt_selected=val_selected.get(): DisplayGui.get_nse_data(btn_selected,
                                                                                                         opt_selected,
                                                                                                         ""))
                opt.pack(anchor='e', fill=BOTH, pady=3)
            elif btn_selected == 'NSE HOLIDAYS':
                val_selected.set("Trading / Clearing H")
                opt = OptionMenu(DisplayGui.nse_option_menu_display_lbl_frame, val_selected, *menu_dict_values,
                                 command=lambda opt_selected=val_selected.get(): DisplayGui.get_nse_data(btn_selected,
                                                                                                         opt_selected,
                                                                                                         ""))
                opt.pack(anchor='e', fill=BOTH, pady=3)
            elif btn_selected == 'NSE LIVE DATA':
                val_selected.set("NSE Live Data Options")
                # To clear the data table when the menu1 option is changed.only data to be loaded after the menu2 is selected
                canvas_object_present = DisplayGui.nse_data_display_lbl_frame.pack_slaves()
                for cop in canvas_object_present:
                    cop.destroy()
                opt = OptionMenu(DisplayGui.nse_option_menu_display_lbl_frame, val_selected, *menu_dict_values,
                                 # name='nse_live_menu1',
                                 command=lambda opt_selected=val_selected.get(): DisplayGui.create_live_data_menu2_item(
                                     menu_dict_values,
                                     btn_selected, opt_selected))
                opt.pack(anchor='e', fill=BOTH, pady=3)

    @staticmethod
    def get_nse_data(btn_name, key1_value=None, key2_value=None):
        DisplayGui.my_stock_data_display_lbl_frame.pack_forget()

        DisplayGui.nse_data_display_lbl_frame.pack(padx=0, pady=0, ipadx=0, ipady=0, fill=BOTH, side=RIGHT, expand=TRUE)
        DisplayGui.display_pan_window1.pack(padx=50, pady=50, ipadx=10, ipady=10, expand=False, fill=BOTH, side=RIGHT)
        DisplayGui.nse_option_menu_display_lbl_frame.pack(padx=5, pady=5, ipadx=5, ipady=5, fill=BOTH, expand=TRUE,
                                                          anchor='s')
        DisplayGui.display_pan_window1.add(DisplayGui.nse_option_menu_display_lbl_frame)
        DisplayGui.nse_data_display_lbl_frame.configure(text=btn_name)

        if btn_name == 'NSE PRE-MARKET DATA':
            DisplayGui.create_option_menu(DisplayGui.nse_class_object.pre_market_key, btn_name)
            if key1_value is not None:
                df = DisplayGui.nse_class_object.nse_pre_market_data(key1_value)
            else:
                df = pd.DataFrame(['Please select the Option from Options Menu'])
        elif btn_name == 'NSE LIVE DATA':
            DisplayGui.create_option_menu(DisplayGui.nse_class_object.live_market_key, btn_name)
            if (key1_value is not None) and (key2_value is not None):
                df = DisplayGui.nse_class_object.nse_live_market_data(key1_value, key2_value)
            else:
                df = pd.DataFrame(['Please select the Option from Options Menu'])
        elif btn_name == 'NSE HOLIDAYS':
            DisplayGui.create_option_menu(DisplayGui.nse_class_object.trading_clearing, btn_name)
            if key1_value is not None:
                df = DisplayGui.nse_class_object.nse_holidays(key1_value.lower()).iloc[:, :3]
            else:
                df = pd.DataFrame(['Please select the Option from Options Menu'])
        else:
            df = pd.DataFrame(['No Data Found for the selected object'])

        tbl = Table(DisplayGui.nse_data_display_lbl_frame, dataframe=df,
                    showtoolbar=True, showstatusbar=True, cols=6)
        tbl.show()
        tbl.redraw()
        DisplayGui.root.update()

        # #Configure the table
        # options = {'align': 'w',
        #      'cellbackgr': DisplayGui.ACTIVEBACKGROUND,
        #      'cellwidth': 80,
        #      'rowheadercolor': 'skyblue4',
        #      'colheadercolor': 'skyblue3',
        #      'floatprecision': 2,
        #      'font': 'Arial',
        #      'fontsize': 12,
        #      'fontstyle': '',
        #      'grid_color': 'light goldenrod',
        #      'linewidth': 1,
        #      'rowheight': 22,
        #      'rowselectedcolor': DisplayGui.ACTIVEFOREGROUND,
        #      'textcolor': 'black'}
        # config.apply_options(options, tbl)

    @staticmethod
    def my_stock_display(btn_identity):
        DisplayGui.nse_data_display_lbl_frame.pack_forget()
        DisplayGui.display_pan_window1.pack_forget()
        DisplayGui.nse_option_menu_display_lbl_frame.pack_forget()

        # Enable to display My stock data label frame
        DisplayGui.my_stock_data_display_lbl_frame.pack(padx=0, pady=0, ipadx=0, ipady=0, fill=BOTH, side=RIGHT,
                                                        expand=TRUE)

        # To verify already options are displaying for selection
        canvas_object_present = len(DisplayGui.my_stock_data_display_lbl_frame.pack_slaves())
        if canvas_object_present == 0:
            Search_label = Label(DisplayGui.my_stock_data_display_lbl_frame, text='Search by symbol : ', bg='black',
                                 fg='cyan', width=60, bd=0,
                                 font='Helvetica 9 bold')
            Search_label.pack(padx=0, pady=0, ipadx=0, ipady=0,
                              expand=False)
            DisplayGui.stock_symbol.set('')
            DisplayGui.stock_entry.pack()
            tip_text = Hovertip(DisplayGui.stock_entry, 'Search by Equities stock symbol')
            DisplayGui.root.update()

    menu_button = {'STOCK DETAILS': my_stock_display,
                   'NSE PRE-MARKET DATA': get_nse_data,
                   'NSE LIVE DATA': get_nse_data,
                   'NSE HOLIDAYS': get_nse_data,
                   'STOCK ANALYSIS': get_nse_data,
                   'EXIT APPLICATION': exit_application,
                   }

    @classmethod
    def action(cls, btn_identity):
        DisplayGui.thread_stop('stk_price_update_thread')
        canvas_object_present = [DisplayGui.nse_option_menu_display_lbl_frame.pack_slaves(),
                                 DisplayGui.nse_data_display_lbl_frame.pack_slaves(),
                                 DisplayGui.stock_details_main_frame.pack_slaves()]
        for canvasobject in canvas_object_present:
            if len(canvasobject) > 0:
                for cop in canvasobject:
                    cop.destroy()
        if btn_identity in DisplayGui.menu_button:
            DisplayGui.menu_button[btn_identity](btn_identity)

    def __init__(self):
        DisplayGui.root.geometry('1200x600')
        DisplayGui.root.resizable(0, 0)
        # DisplayGui.root.attributes('-toolwindow', True)
        DisplayGui.root.title(DisplayGui.TITLE)
        DisplayGui.root.configure(background='black')
        DisplayGui.root.iconbitmap('.\\Images\\Root_Icon.ico')

        # Create menu buttons in the Label frame for the User actions
        btn_row = 0
        for create_btn in DisplayGui.menu_button:
            btn_row = btn_row + 40
            DisplayGui.button = Button(DisplayGui.btn_display_lbl_frame, text=create_btn, bg='black', fg='cyan',
                                       width=25,
                                       height=6,
                                       relief=RAISED,
                                       activebackground=DisplayGui.ACTIVEBACKGROUND, font='Helvetica 9 bold',
                                       command=lambda btn_label_txt=create_btn: DisplayGui.action(btn_label_txt))
            DisplayGui.button.pack(anchor='w')

        DisplayGui.root.mainloop()
