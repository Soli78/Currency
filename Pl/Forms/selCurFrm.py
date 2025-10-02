from tkinter import *
from tkinter.ttk import Combobox
import threading, requests
from requests.exceptions import RequestException, Timeout

TIMEOUT = 6

class App(Frame):
    def __init__(self, screen):
        super().__init__(screen)
        self.master = screen
        self.CreateWidget()
        self.Error = False

        # لیست ارزها را بدون قفل شدن UI لود کن
        self.load_currencies_async()

    def CreateWidget(self):
        self.frmSearch = Frame(self.master, width=400, bg="#8B5FBF", height=200)
        self.frmSearch.place(x=0, y=0)

        self.lbl = Label(self.frmSearch, text="Enter the Amount")
        self.lbl.place(x=20, y=10)

        self.txtAmount = Entry(self.frmSearch, width=23)
        self.txtAmount.place(x=140, y=10)

        self.lbl = Label(self.frmSearch, text="From")
        self.lbl.place(x=20, y=40)
        self.txtFrom = Combobox(self.frmSearch, values=["...loading..."])
        self.txtFrom.place(x=140, y=40)

        self.lbl = Label(self.frmSearch, text="To")
        self.lbl.place(x=20, y=70)
        self.txtTo = Combobox(self.frmSearch, values=["...loading..."])
        self.txtTo.place(x=140, y=70)

        self.btn = Button(self.frmSearch, text="Convert", bg="white", fg="black", command=self.OnClickbtn)
        self.btn.place(x=172, y=110)

        self.lblResult = Label(self.frmSearch, pady=3, width=30, bg="#61BCED", text="", fg="black")
        self.lblResult.place(x=100, y=150)

    # ---------- شبکه: بکاپ و timeout ----------
    def _fetch_rates(self, base):
        """سعی می‌کند از دو سرویس بگیرد؛ هر کدام شد همان را برمی‌گرداند."""
        urls = [
            f"https://open.er-api.com/v6/latest/{base}",
            f"https://api.exchangerate.host/latest?base={base}",
        ]
        last_err = None
        for u in urls:
            try:
                r = requests.get(u, timeout=TIMEOUT)
                r.raise_for_status()
                data = r.json()
                rates = data.get("rates") or {}
                if rates:
                    return rates
            except (RequestException, Timeout) as e:
                last_err = e
        raise last_err if last_err else RuntimeError("No rates source succeeded")

    # ---------- لود اولیهٔ لیست ارزها بدون بلاک ----------
    def load_currencies_async(self):
        def worker():
            try:
                rates = self._fetch_rates("USD")
                currencies = sorted(rates.keys())
                self.master.after(0, lambda: self._apply_currency_list(currencies))
            except Exception as e:
                print("Network error in load_currencies_async:", e)
                self.master.after(0, lambda: self._apply_currency_list([], error=str(e)))
        threading.Thread(target=worker, daemon=True).start()

    def _apply_currency_list(self, currencies, error=None):
        if currencies:
            self.txtFrom["values"] = currencies
            self.txtTo["values"] = currencies
            # انتخاب پیش‌فرض
            try:
                self.txtFrom.set("USD")
                self.txtTo.set("EUR")
            except Exception:
                pass
            self.lblResult.config(text="Ready", fg="black")
        else:
            self.txtFrom["values"] = []
            self.txtTo["values"] = []
            self.lblResult.config(text="اتصال اینترنت یا DNS مشکل دارد.", fg="red")

    # ---------- تبدیل ارز بدون قفل ----------
    def OnClickbtn(self):
        try:
            amount = float(self.txtAmount.get())
        except ValueError:
            self.lblResult.config(text="مقدار نامعتبر!", fg="red")
            return

        from_currency = self.txtFrom.get()
        to_currency = self.txtTo.get()
        if not (from_currency and to_currency):
            self.lblResult.config(text="لطفاً From و To را پر کنید!", fg="red")
            return

        self.lblResult.config(text="در حال تبدیل...", fg="black")
        def worker():
            try:
                rates = self._fetch_rates(from_currency)
                rate = rates.get(to_currency)
                if rate:
                    result = amount * rate
                    self.master.after(0, lambda: self.lblResult.config(
                        text=f"{amount} {from_currency} = {result:.2f} {to_currency}", fg="black"))
                else:
                    self.master.after(0, lambda: self.lblResult.config(text="نرخ پیدا نشد.", fg="red"))
            except Exception as e:
                print("Network error in convert:", e)
                self.master.after(0, lambda: self.lblResult.config(
                    text="اتصال اینترنت یا DNS مشکل دارد.", fg="red"))
        threading.Thread(target=worker, daemon=True).start()
