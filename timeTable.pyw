import sqlite3, time, datetime, uuid, hashlib, sys, re, os
import tkinter as tk
from tkinter import *
from datetime import date, timedelta


LARGE_FONT = ('Verdana', 14)
MED_FONT = ('Verdana', 12)

conn = sqlite3.connect('timeTable.db')
print('Opened database successfully!')
c = conn.cursor()

CURRENT_USER = ''
STATUS = ''
BG = '#99CCCC'


class TimeTable(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self, 'Time Table')
        tk.Tk.iconbitmap(self, default='USA-Flag-icon.ico')  # add an icon to the window
        container = tk.Frame(self)
        container.pack(side='top', fill='both', expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, UserPage, NewUserPage, TimeStamp, ManualEntry, Reports):  # add each new page to this tuple
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky='nsew')
        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        tk.Frame.configure(self, bg=BG)

        self.controller = controller

        label = tk.Label(self, text='Please Log In', font=LARGE_FONT, bg=BG)
        label.pack(side='top', pady=10, padx=10)
        userLabel = tk.Label(self, text='Username:', font=MED_FONT, bg=BG)
        userLabel.pack(side='top', pady=5, padx=5)
        userBox = tk.Entry(self)
        userBox.pack(side='top', pady=5, padx=5)
        passwordLabel = tk.Label(self, text='Password:', font=MED_FONT, bg=BG)
        passwordLabel.pack(side='top', pady=5, padx=5)
        passwordBox = tk.Entry(self, show='*')
        passwordBox.pack(side='top', pady=5, padx=5)
        caseLabel = tk.Label(self, text='(password is case sensitive)', bg=BG)
        caseLabel.pack(side='top')
        okButton = tk.Button(self, command=lambda: self.checkPass(userBox.get(), passwordBox.get()),
                             text='Submit', width=10)
        okButton.pack(side='top', pady=10)
        newUserButton = tk.Button(self, text='New User', command=lambda: controller.show_frame(NewUserPage), width=10)
        newUserButton.pack(side='top', pady=10)

    def checkPass(self, user_name, user_password):
        global CURRENT_USER
        global STATUS
        user = user_name.upper()
        CURRENT_USER = user

        c.execute('SELECT password from login_data WHERE username=?', (user,))
        hashed_password = c.fetchall()  # assigns data in cell to variable

        if not hashed_password:
            wrongUser = tk.Label(self, text='Username not found', font=MED_FONT, fg='red', bg=BG)
            wrongUser.pack(side='top', pady=5)
        else:
            password, salt = hashed_password[0][0].split(':')
            if password == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest():
                c.execute('SELECT * from %s ORDER BY datestamp DESC, timestamp DESC' % CURRENT_USER)
                info = c.fetchall()
                moreInfo = info[0][4]
                if moreInfo == 'BREAK IN' or moreInfo == 'CLOCK IN':
                    STATUS = 'CLOCKED IN'
                if moreInfo == 'BREAK OUT' or moreInfo == 'CLOCK OUT':
                    STATUS = 'CLOCKED OUT'
                self.controller.show_frame(UserPage)
            else:
                wrongPass = tk.Label(self, text='Wrong Password Try Again', font=MED_FONT, fg='red', bg=BG)
                wrongPass.pack(side='top', pady=5)


class UserPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        tk.Frame.configure(self, bg=BG)
        tk.Frame.columnconfigure(self, 0, pad=20, weight=1)
        tk.Frame.columnconfigure(self, 2, pad=20, weight=1)
        tk.Frame.rowconfigure(self, 1, pad=10, weight=1)
        tk.Frame.rowconfigure(self, 3, pad=10, weight=1)
        tk.Frame.rowconfigure(self, 6, pad=10, weight=1)
        welcomeLabel = tk.Label(self, text='Welcome to Time Table', font=LARGE_FONT, bg=BG, pady=10)
        welcomeLabel.grid(row=0, column=1)
        clockButton = tk.Button(self, command=lambda: controller.show_frame(TimeStamp),
                                text='Clock IN/OUT', pady=10)
        clockButton.grid(row=2, column=1, sticky=W+E)
        reportButton = tk.Button(self, text='See my activity', pady=10, command=lambda: controller.show_frame(Reports))
        reportButton.grid(row=4, column=1, sticky=W+E)
        statusButton = tk.Button(self, text='Current status', pady=10, command=self.status)
        statusButton.grid(row=5, column=1, sticky=W + E)

    def status(self):

        if STATUS == 'CLOCKED IN':
            statusLabel = tk.Label(self, text='You are currently clocked in', font=MED_FONT, bg=BG)
            statusLabel.grid(row=6, column=1, stick=W+E)
        if STATUS == 'CLOCKED OUT':
            statusLabel = tk.Label(self, text='You are currently clocked out', font=MED_FONT, bg=BG)
            statusLabel.grid(row=6, column=1, stick=W + E)


class NewUserPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        tk.Frame.configure(self, bg=BG)
        self.controller = controller
        mainLabel = tk.Label(self, text='Please create a Username and Password', font=LARGE_FONT, bg=BG)
        mainLabel.pack(side='top', pady=10, padx=10)
        userLabel = tk.Label(self, text='Enter a Username:', font=MED_FONT, bg=BG)
        userLabel.pack(side='top', pady=5, padx=5)
        newUserBox = tk.Entry(self)
        newUserBox.pack(side='top', pady=5, padx=5)
        passwordLabel = tk.Label(self, text='Choose a Password:', font=MED_FONT, bg=BG)
        passwordLabel.pack(side='top', pady=5, padx=5)
        newPasswordBox = tk.Entry(self, show='*')
        newPasswordBox.pack(side='top', pady=5, padx=5)
        caseLabel = tk.Label(self, text='(password is case sensitive)', bg=BG)
        caseLabel.pack(side='top')
        okButton = tk.Button(self, command=lambda: self.hashPass(newUserBox.get(), newPasswordBox.get()),
                             text='Submit', width=10)
        okButton.pack(side='top', pady=25)

    def hashPass(self, username, password):
        global CURRENT_USER
        newUsername = username.upper()
        CURRENT_USER = newUsername
        salt = uuid.uuid4().hex     # uuid is used to generate a random number
        hashed_password = hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt
        self.add_user(newUsername, hashed_password)

    def add_user(self, username, hashed_password):
        c.execute('CREATE TABLE IF NOT EXISTS login_data(username TEXT, password TEXT)')
        c.execute('INSERT INTO login_data (username, password) VALUES (?, ?)', (username, hashed_password))
        c.execute('CREATE TABLE IF NOT EXISTS %s(username TEXT, unix INT, datestamp TEXT, '
                  'timestamp TEXT, reason TEXT)' % CURRENT_USER)
        conn.commit()
        print('%s added' % CURRENT_USER)                                                               
        self.controller.show_frame(TimeStamp)


class TimeStamp(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        tk.Frame.configure(self, bg=BG)
        tk.Frame.columnconfigure(self, 0, pad=20, weight=1)
        tk.Frame.columnconfigure(self, 2, pad=20, weight=1)
        tk.Frame.rowconfigure(self, 6, pad=10, weight=1)
        self.var = StringVar()

        label1 = tk.Label(self, text='Select one:', font=LARGE_FONT, bg=BG)
        label1.grid(row=0, column=1, pady=10, sticky=W)
        r1 = Radiobutton(self, text='Just Got Here', variable=self.var, value='CLOCK IN', bg=BG)
        r1.grid(row=1, column=1, sticky=W)
        r2 = Radiobutton(self, text='Taking a Break', variable=self.var, value='BREAK OUT', bg=BG)
        r2.grid(row=2, column=1, sticky=W)
        r3 = Radiobutton(self, text='Back From Break', variable=self.var, value='BREAK IN', bg=BG)
        r3.grid(row=3, column=1, sticky=W)
        r4 = Radiobutton(self, text='Done For The Day', variable=self.var, value='CLOCK OUT', bg=BG)
        r4.grid(row=4, column=1, sticky=W)
        clockButton = tk.Button(self, command=lambda: self.timeStamp(self.var.get()),
                                text='Clock IN/OUT Now')
        clockButton.grid(row=6, column=1, pady=5)
        manualButton = tk.Button(self, text='Go to MANUAL ENTRY',
                                 command=lambda: controller.show_frame(ManualEntry))
        manualButton.grid(row=7, column=1, pady=5)

    def timeStamp(self, reason):

        if reason != '':
            if reason == 'CLOCK IN' or reason == 'BREAK IN':
                if STATUS != 'CLOCKED IN' or STATUS == '':
                    self.stampTime(reason)
                if STATUS == 'CLOCKED IN':
                    alreadyIn = tk.Label(self, text='You are already clocked in', fg='red', bg=BG)
                    alreadyIn.grid(row=5, column=1, sticky=W + E)
            if reason == 'BREAK OUT':
                if STATUS != 'CLOCKED OUT' or STATUS == '':
                    self.stampTime(reason)
                if STATUS == 'CLOCKED OUT':
                    alreadyOut = tk.Label(self, text='You are already clocked out', fg='red', bg=BG)
                    alreadyOut.grid(row=5, column=1, sticky=W + E)
            if reason == 'CLOCK OUT':
                if STATUS != 'CLOCKED OUT' or STATUS == '':
                    unix = time.time()
                    datestamp = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d'))
                    c.execute("SELECT reason from %s WHERE datestamp=?" % CURRENT_USER, (datestamp,))
                    clock_out = c.fetchall()
                    if ('BREAK OUT',) and ('BREAK IN',) not in clock_out:                   # (if no breaks taken in
                        c.execute('INSERT INTO %s(username,datestamp, timestamp, reason) '  # day, creates null values 
                                  'VALUES (?, ?, ?, ?)' % CURRENT_USER,                     # for breaks; needed to
                                  (CURRENT_USER, datestamp, None, 'BREAK OUT'))             # calculate hours later)
                        c.execute('INSERT INTO %s(username,datestamp, timestamp, reason) '
                                  'VALUES (?, ?, ?, ?)' % CURRENT_USER,
                                  (CURRENT_USER, datestamp, None, 'BREAK IN'))
                        conn.commit()
                        self.stampTime(reason)
                    else:
                        self.stampTime(reason)
                if STATUS == 'CLOCKED OUT':
                    alreadyOut = tk.Label(self, text='You are already clocked out', fg='red', bg=BG)
                    alreadyOut.grid(row=5, column=1, sticky=W + E)
        if reason == '':
            selectReason = tk.Label(self, text='Select one from above ', fg='red', bg=BG)
            selectReason.grid(row=5, column=1, sticky=W + E)

    def stampTime(self, reason):

        unix = time.time()
        datestamp = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d'))
        timestamp = str(datetime.datetime.fromtimestamp(unix).strftime('%H:%M:%S'))
        c.execute('INSERT INTO %s(username, unix, datestamp, timestamp, reason) '
                  'VALUES (?, ?, ?, ?, ?)' % CURRENT_USER, (CURRENT_USER, unix, datestamp, timestamp, reason))
        conn.commit()
        c.close()
        conn.close()
        sys.exit()


class ManualEntry(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        tk.Frame.configure(self, bg=BG)
        tk.Frame.columnconfigure(self, 0, pad=10, weight=1)
        tk.Frame.columnconfigure(self, 4, pad=10, weight=1)
        self.var = StringVar()

        label1 = tk.Label(self, text='Select one:', font=LARGE_FONT, bg=BG)
        label1.grid(row=0, column=2, pady=10, sticky=W)
        r1 = Radiobutton(self, text='Just Got Here', variable=self.var, value='CLOCK IN', bg=BG)
        r1.grid(row=1, column=2, sticky=W)
        r2 = Radiobutton(self, text='Taking a Break', variable=self.var, value='BREAK OUT', bg=BG)
        r2.grid(row=2, column=2, sticky=W)
        r3 = Radiobutton(self, text='Back From Break', variable=self.var, value='BREAK IN', bg=BG)
        r3.grid(row=3, column=2, sticky=W)
        r4 = Radiobutton(self, text='Done For The Day', variable=self.var, value='CLOCK OUT', bg=BG)
        r4.grid(row=4, column=2, sticky=W)

        manualDateLabel = tk.Label(self, text='Manually enter the DATE: ', bg=BG)
        manualDateLabel.grid(row=6, column=1, sticky=E)
        manualDateEntry = tk.Entry(self)
        manualDateEntry.grid(row=6, column=2, pady=10)
        manualDateText = tk.Label(self, text='format: YYYY-MM-DD', bg=BG)
        manualDateText.grid(row=6, column=3, sticky=W)
        manualTimeLabel = tk.Label(self, text='Manually enter the TIME: ', bg=BG)
        manualTimeLabel.grid(row=7, column=1, sticky=E)
        manualTimeEntry = tk.Entry(self)
        manualTimeEntry.grid(row=7, column=2)
        manualTimeText = tk.Label(self, text='24 hr format: HH:MM:SS', bg=BG)
        manualTimeText.grid(row=7, column=3, sticky=W)
        manualButton = tk.Button(self, text='Submit',
                                 command=lambda: self.manualMatch(manualDateEntry.get(),
                                                                  manualTimeEntry.get(), self.var.get()))
        manualButton.grid(row=8, column=2, pady=5, sticky=W+E)
        backButton = tk.Button(self, text='Go back',
                               command=lambda: controller.show_frame(TimeStamp))
        backButton.grid(row=10, column=2, pady=5)

    def manualMatch(self, mDate, mTime, reason):

        dateMatch = re.match(r"\d\d\d\d-\d\d-\d\d", mDate)
        timeMatch = re.match(r"\d\d:\d\d:\d\d", mTime)

        if dateMatch is not None and timeMatch is not None and reason != '':    
            if reason == 'CLOCK OUT':
                c.execute("SELECT reason from %s WHERE datestamp=?" % CURRENT_USER, (mDate,))
                clock_out = c.fetchall()
                if ('BREAK OUT',) and ('BREAK IN',) not in clock_out:                      
                    c.execute('INSERT INTO %s(username,datestamp, timestamp, reason) '  
                              'VALUES (?, ?, ?, ?)' % CURRENT_USER,                    
                              (CURRENT_USER, mDate, None, 'BREAK OUT'))            
                    c.execute('INSERT INTO %s(username,datestamp, timestamp, reason) '
                              'VALUES (?, ?, ?, ?)' % CURRENT_USER,
                              (CURRENT_USER, mDate, None, 'BREAK IN'))
                    conn.commit()
            manual = 'manual'
            c.execute('INSERT INTO %s (username, unix, datestamp, timestamp, reason) '
                      'VALUES (?, ?, ?, ?, ?)' % CURRENT_USER, (CURRENT_USER, manual, mDate, mTime, reason))
            conn.commit()
            print('Time Stamped!')
            time.sleep(.5)
            c.close()
            conn.close()
            sys.exit()

        if dateMatch is None:
            wrongDate = tk.Label(self, text='Date format incorrect', fg='red', bg=BG)
            wrongDate.grid(row=6, column=1, sticky=W+E)
        if timeMatch is None:
            wrongTime = tk.Label(self, text='Time format incorrect', fg='red', bg=BG)
            wrongTime.grid(row=7, column=1, sticky=W+E)
        if reason == '':
            selectReason = tk.Label(self, text='Select one from above ', fg='red', bg=BG)
            selectReason.grid(row=5, column=2, sticky=W + E)


class Reports(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        tk.Frame.configure(self, bg=BG)
        tk.Frame.columnconfigure(self, 0, pad=10, weight=1)
        tk.Frame.columnconfigure(self, 4, pad=10, weight=1)
        tk.Frame.rowconfigure(self, 1, pad=5, weight=1)
        tk.Frame.rowconfigure(self, 4, pad=5, weight=1)
        tk.Frame.rowconfigure(self, 6, pad=5, weight=1)
        label1 = tk.Label(self, text='Enter date range to see your activity', font=LARGE_FONT, bg=BG)
        label1.grid(row=0, column=1, columnspan=3, pady=10, sticky=E+W)
        fromDateLabel = tk.Label(self, text='From DATE: ', bg=BG)
        fromDateLabel.grid(row=2, column=1, sticky=E)
        fromDateEntry = tk.Entry(self)
        fromDateEntry.grid(row=2, column=2)
        fromDateText = tk.Label(self, text='format: YYYY-MM-DD', bg=BG)
        fromDateText.grid(row=2, column=3, sticky=W)
        toDateLabel = tk.Label(self, text='To DATE: ', bg=BG)
        toDateLabel.grid(row=3, column=1, sticky=E)
        toDateEntry = tk.Entry(self)
        toDateEntry.grid(row=3, column=2)
        toDateText = tk.Label(self, text='format: YYYY-MM-DD', bg=BG)
        toDateText.grid(row=3, column=3, sticky=W)
        manualButton = tk.Button(self, text='See activity', width=10,
                                 command=lambda: self.getReports(fromDateEntry.get(), toDateEntry.get()))
        manualButton.grid(row=5, column=3, pady=5)
        hoursButton = tk.Button(self, text='Total hours', width=10,
                                 command=lambda: self.totalHours(fromDateEntry.get(), toDateEntry.get()))
        hoursButton.grid(row=5, column=2, pady=5)
        backButton = tk.Button(self, text='Go back', width=10,
                               command=lambda: controller.show_frame(UserPage))
        backButton.grid(row=5, column=1, pady=5)

    def getReports(self, date1, date2):     # gets and displays data in requested date range to user

        dateMatch1 = re.match(r"\d\d\d\d-\d\d-\d\d", date1)
        dateMatch2 = re.match(r"\d\d\d\d-\d\d-\d\d", date2)

        if dateMatch1 is not None and dateMatch2 is not None:
            data = []
            c.execute("SELECT * from %s WHERE datestamp BETWEEN ? and ? ORDER BY datestamp DESC, timestamp DESC "
                      % CURRENT_USER, (date1, date2))
            raw = c.fetchall()
            for row in raw:     # makes data look nicer for display to the user
                output = str(row[2:])
                output = output.replace('(', '')
                output = output.replace(')', '')
                output = output.replace("'", '')
                data.append(output)
            result = '\n\n'.join(data)
            self.new_window(result)
        if dateMatch1 is None or dateMatch2 is None:
            wrongDate = tk.Label(self, text='Date format incorrect', fg='red', bg=BG)
            wrongDate.grid(row=4, column=2, sticky=W + E)

    def totalHours(self, date1, date2):     # calculates total hours in date range requested

        dateMatch1 = re.match(r"\d\d\d\d-\d\d-\d\d", date1)
        dateMatch2 = re.match(r"\d\d\d\d-\d\d-\d\d", date2)

        if dateMatch1 is not None and dateMatch2 is not None:
            day_list = []
            period_regular = []
            period_ot = []
            period_dt = []
            startDate = datetime.datetime.strptime(date1, '%Y-%m-%d').date()    # converts string date to date object
            endDate = datetime.datetime.strptime(date2, '%Y-%m-%d').date()
            delta = endDate - startDate
            for i in range(delta.days + 1):     # creates a list of all dates between the two dates specified in Reports
                day_list.append(str(startDate + timedelta(days=i)))

            for a in day_list:  

                c.execute("SELECT timestamp, reason from %s WHERE datestamp=?" % CURRENT_USER, (a,))
                list2 = c.fetchall()
                bin_list = []
                bout_list = []

                for tup in list2:                                                       # What if they try to search including the current day? (there would be no clock out)
                    if tup[0] != None:                                                  # Maybe show error message if today's date is included in search if not clocked out
                        if tup[1] == 'CLOCK IN':                                        # or confirm for each date there are all four reasons <-----------THIS
                            in_time = datetime.datetime.strptime(tup[0], '%H:%M:%S')    # confirm there is not more than one CLOCK IN and CLOCK OUT
                        if tup[1] == 'CLOCK OUT':
                            out_time = datetime.datetime.strptime(tup[0], '%H:%M:%S')
                        if tup[1] == 'BREAK OUT':
                            b_out = datetime.datetime.strptime(tup[0], '%H:%M:%S')
                            bout_list.append(b_out)
                        if tup[1] == 'BREAK IN':
                            b_in = datetime.datetime.strptime(tup[0], '%H:%M:%S')
                            bin_list.append(b_in)
                    else:
                        if tup[1] == 'BREAK IN' or tup[1] == 'BREAK OUT':
                            b_in = datetime.datetime(1, 1, 1)
                            bin_list.append(b_in)
                            b_out = datetime.datetime(1, 1, 1)
                            bout_list.append(b_out)

                raw_break = [a - b for a, b in zip(bin_list, bout_list)]       # to account for multiple breaks in the same day
                better_break_list = []
                best_break_list = []

                for item in raw_break:
                    better_break = divmod(item.days * 86400 + item.seconds, 60)
                    better_break_list.append(better_break)
                for item in better_break_list:
                    best_break = item[1]/60 + item[0]
                    best_break_list.append(best_break)
                total_break = sum(best_break_list)

                delta_work = out_time - in_time     # calculates the total paid hours (total hours - break hours)
                raw_work = divmod(delta_work.days * 86400 + delta_work.seconds, 60)
                total_work = raw_work[1]/60 + raw_work[0]
                x = (total_work - total_break)/60
                paid_hours = round(x, 2)

                if paid_hours < 8.00:
                    regular_hours = paid_hours
                    period_regular.append(regular_hours)
                if 8.00 < paid_hours < 12.00:
                    regular_hours = 8.00
                    overtime = paid_hours - 8.00
                    period_regular.append(regular_hours)
                    period_ot.append(overtime)
                if paid_hours > 12.00:
                    regular_hours = 8.00
                    overtime = 4.00
                    doubletime = paid_hours - 12.00
                    period_regular.append(regular_hours)
                    period_ot.append(overtime)
                    period_dt.append(doubletime)

            total_period_regular = sum(period_regular)
            total_period_ot = sum(period_ot)
            total_period_dt = sum(period_dt)

            hour_text = 'Total hours for date range: ' + date1 + ' to ' + date2 + '\n\n' + str(total_period_regular) \
                        + ' regular\n' + str(total_period_ot) +  ' overtime\n' + str(total_period_dt) + ' doubletime'
            self.new_window(hour_text)

        if dateMatch1 is None or dateMatch2 is None:
            wrongDate = tk.Label(self, text='Date format incorrect', fg='red', bg=BG)
            wrongDate.grid(row=4, column=2, sticky=W + E)

    def new_window(self, info):

        window = tk.Toplevel(self)
        window.title('User: %s' % CURRENT_USER)
        label = tk.Label(window, text=info, font=MED_FONT)
        label.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        make_text = tk.Button(window, text='Export as text', command=lambda: self.export(info))
        make_text.pack(side='top', pady=10)

    def export(self, info):

        export_document = '%s_Report.txt' % CURRENT_USER
        write_export = open(export_document, 'w')
        write_export.write(info)
        write_export.close()
        os.startfile(export_document)

app = TimeTable()
app.mainloop()
c.close()
conn.close()

########################################################################################################################
# TO DO:
#
# menu bar
#
# display total hours WITH activity information in Reports
#
# make .exe
#
# make everything look better
#
# regex for username and password entry
#   
# more feedback to user: confirmation messages, options if things didn't work as expected etc.
#
# wish list:
#   store all ee data, make this a small business multipurpose program (time clock, ee database, what else?)
#   admin account: ability to delete users, change data if an employee makes a mistake in time entry
#   compatibility with CP?
#   remote clock-in/out devices? Rpi?
#
########################################################################################################################
