import tkinter
from datetime import datetime
from matplotlib.figure import Figure
from matplotlib import style
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from fbprophet import Prophet
from pandas_datareader import data
import pandas as pd
from datetime import datetime
import yfinance as yf

style.use("bmh")

class App:
    def __init__(self, root):
        self.now = str(datetime.now().strftime('%Y-%m-%d'))
        f = open("save.txt", "r")
        f1 = f.read().split('\n')
        f.close()
        self.root = root
        self.root.title("Stock-Pred-Program")
        self.root.resizable(False, False)

        self.GRAPHVAR = tkinter.IntVar(value=int(f1[4]))
        self.SHORTVAR = tkinter.IntVar(value=int(f1[5]))
        self.LONGVAR = tkinter.IntVar(value=int(f1[6]))

        self.UILF = tkinter.LabelFrame(root, bd=0)
        self.UILF.grid(row=0, column=0, padx=35, pady=10)

        self.UISTOCK = tkinter.Label(self.UILF, text="Stock: ")
        self.UISTOCK.grid(row=0, column=0, sticky="W")

        self.UISTOCKE = tkinter.Entry(self.UILF)
        self.UISTOCKE.insert(0, f1[0])
        self.UISTOCKE.grid(row=0, column=1, sticky="W")

        self.UISDATE = tkinter.Label(self.UILF, text="Startdate: ")
        self.UISDATE.grid(row=1, column=0, sticky="W")

        self.UISDATEE = tkinter.Entry(self.UILF)
        self.UISDATEE.insert(0, f1[1])
        self.UISDATEE.grid(row=1, column=1, sticky="W")

        self.UIEDATE = tkinter.Label(self.UILF, text="Enddate: ")
        self.UIEDATE.grid(row=2, column=0, sticky="W")

        self.UIEDATEE = tkinter.Entry(self.UILF)
        self.UIEDATEE.insert(0, f1[2])
        self.UIEDATEE.grid(row=2, column=1, sticky="W")

        self.UIGRAPHC = tkinter.Checkbutton(self.UILF, text="Graph", variable=self.GRAPHVAR)
        self.UIGRAPHC.grid(row=3, column=0, sticky="W")

        self.UIROLLSC = tkinter.Checkbutton(self.UILF, text="Shortroll", variable=self.SHORTVAR)
        self.UIROLLSC.grid(row=4, column=0, sticky="W")

        self.UIROLLLC = tkinter.Checkbutton(self.UILF, text="Longroll", variable=self.LONGVAR)
        self.UIROLLLC.grid(row=5, column=0, sticky="W")

        self.UIPRED = tkinter.Label(self.UILF, text='Yrs of Prediction: ')
        self.UIPRED.grid(row=6, column=0, sticky="W")

        self.UIPREDS = tkinter.Scale(self.UILF, from_=0, to=3, orient='horizontal')
        self.UIPREDS.set(f1[6])
        self.UIPREDS.grid(row=6, column=1, sticky='W')

        self.BTLF = tkinter.LabelFrame(self.UILF, bd=0)
        self.BTLF.grid(row=7, column=0 , sticky="W")

        self.UIBUTTONR = tkinter.Button(self.BTLF, text="Run", command = self.run)
        self.UIBUTTONR.grid(row=0, column=0, padx=(0, 10), sticky="W")

        self.UIBUTTONS = tkinter.Button(self.BTLF, text="Save", command = self.save)
        self.UIBUTTONS.grid(row=0, column=1, sticky="W")

        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.stockplot = self.fig.add_subplot(111)
        self.stockplot.set_xlabel('Date')
        self.stockplot.set_ylabel('Adj Close Price ($)')
        self.stockplot.set_title('Stock Price')
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)  # A tk.DrawingArea.
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=1)

    def run(self):
        START_DATE = self.UISDATEE.get()
        END_DATE = self.UIEDATEE.get()
        STOCK = self.UISTOCKE.get().upper()

        stock_data = data.DataReader(STOCK,
                                    'yahoo',
                                    START_DATE,
                                    END_DATE)
        weekdays = pd.date_range(start=START_DATE, end=END_DATE)
        clean_data = stock_data['Adj Close'].reindex(weekdays)
        adj_close = clean_data.fillna(method='ffill')
        self.stockplot.clear()
        self.stockplot.set_xlabel('Date')
        self.stockplot.set_ylabel('Adj Close (p)')
        self.stockplot.set_title('Stock Price')
        pdata = yf.download(STOCK, START_DATE, END_DATE)
        pdata.reset_index(inplace=True)
        df_train = pdata[['Date', 'Close']]
        df_train = df_train.rename(columns={'Date': 'ds', 'Close': 'y'})
        m = Prophet()
        m.fit(df_train)

        if self.GRAPHVAR.get():
            self.stockplot.plot(adj_close, label=STOCK)

        if self.SHORTVAR.get():
            self.stockplot.plot(adj_close.rolling(window=50).mean(), label="50 day rolling mean")

        if self.LONGVAR.get():
            self.stockplot.plot(adj_close.rolling(window=200).mean(), label="200 day rolling mean")

        if self.UIPREDS.get():
            future = m.make_future_dataframe(periods=self.UIPREDS.get()*365)
            forecast = m.predict(future)
            fcst_t = forecast['ds'].dt.to_pydatetime()
            self.stockplot.plot(fcst_t, forecast['yhat'], ls=':', label=f'{self.UIPREDS.get()}-Year Prediction')

        self.stockplot.legend()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)  # A tk.DrawingArea.
        self.canvas.draw()

    def save(self):
        f = open('save.txt', 'w+')
        f.write(self.UISTOCKE.get() + '\n' + self.UISDATEE.get() + '\n' + self.UIEDATEE.get() + '\n' + str(self.GRAPHVAR.get()) + '\n' + str(self.SHORTVAR.get()) + '\n' + str(self.LONGVAR.get()) + '\n' + str(self.UIPREDS.get()))
        f.close()