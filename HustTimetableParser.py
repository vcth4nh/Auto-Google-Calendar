import requests
from bs4 import BeautifulSoup as bs

s = requests.session()
HOST = 'https://ctt-sis.hust.edu.vn'

"""
Parsed data will be like:
[
    {
        'date': '2',
        'time_start': '12h30',
        'time_end': '15h50',
        'week': (['25', '32'], ['34', '42']),
        'room': 'room',
        'class code': 'code',
        'subject code': 'code',
        'subject': 'name',
        'teacher': 'name'
    },
    {
    ...
    }
]
"""


class Parser:
    def __init__(self, row):
        self.date = None
        self.time_start = None
        self.time_end = None
        self.week = None
        self.no_class_week = None
        self.room = None
        self.class_code = None
        self.subject_code = None
        self.subject = None
        self.teacher = None
        self.parse(row)

    def parse(self, row):
        assert len(row) == 13
        self.get_datetime(row[0])
        self.get_week(row[1])
        self.get_no_class_week()
        self.get_room(row[2])
        self.get_classcode(row[3])
        self.get_nothing(row[4])
        self.get_nothing(row[5])
        self.get_subjectcode(row[6])
        self.get_subject(row[7])
        self.get_nothing(row[8])
        self.get_nothing(row[9])
        self.get_teacher(row[10])
        self.get_nothing(row[11])
        self.get_nothing(row[12])

    @staticmethod
    def get_nothing(text: str):
        return None

    def get_datetime(self, text: str):
        date, time = text.replace(' ', '').split(',')
        start_time, end_time = time.split('-')
        self.date = date[-1]
        self.time_start = start_time
        self.time_end = end_time
        return self.date, self.time_start, self.time_end

    def get_week(self, text: str):
        tmp = [x.split('-') for x in text.replace(' ', '').split(',')]
        self.week = [list(map(int, i)) for i in tmp]
        return self.week

    def get_firs_last_week(self):
        import functools
        import operator
        week = functools.reduce(operator.iconcat, self.week, [])
        first_week = week[0]
        last_week = week[-1]

    def get_no_class_week(self):
        if len(self.week) == 1:
            return []

        last_week_prev = None
        first_week_next = None
        no_class_week = []
        for week_range in self.week:
            if last_week_prev is None:
                last_week_prev = week_range[-1]
                continue
            first_week_next = week_range[0]
            no_class_week += list(range(last_week_prev + 1, first_week_next))
            last_week_prev = week_range[-1]

        self.no_class_week = no_class_week
        return self.no_class_week

    def get_room(self, text: str):
        self.room = text
        return self.room

    def get_classcode(self, text: str):
        self.class_code = text
        return self.class_code

    def get_subjectcode(self, text: str):
        self.subject_code = text
        return self.subject_code

    def get_subject(self, text: str):
        self.subject = text
        return self.subject

    def get_teacher(self, text: str):
        self.teacher = text
        return self.teacher

    def json(self):
        return str(self)

    # def convert_to_gg_json(self):
    #     event = {
    #         'summary': self.subject,
    #         'location': self.room,
    #         'description': f"Teacher:{self.teacher}\n"
    #                        f"Class code:{self.class_code}\n"
    #                        f"Subject code:{self.subject_code}\n"
    #                        f"Teams code:",
    #         'start': {
    #             'dateTime': '2015-05-28T09:00:00-07:00',
    #             'timeZone': 'America/Los_Angeles',
    #         },
    #         'end': {
    #             'dateTime': '2015-05-28T17:00:00-07:00',
    #             'timeZone': 'America/Los_Angeles',
    #         },
    #         'recurrence': [
    #             'RRULE:FREQ=DAILY;COUNT=2'
    #         ],
    #         'attendees': [
    #             {'email': 'lpage@example.com'},
    #             {'email': 'sbrin@example.com'},
    #         ],
    #         'reminders': {
    #             'useDefault': False,
    #             'overrides': [
    #                 {'method': 'email', 'minutes': 24 * 60},
    #                 {'method': 'popup', 'minutes': 10},
    #             ],
    #         },
    #     }
    #     return

    def __str__(self):
        return "\n\t".join(["{",
                            f"'date': '{self.date}'",
                            f"'time_start': '{self.time_start}',",
                            f"'time_end': '{self.time_end}',",
                            f"'week': {self.week},",
                            f"'no class week': {self.no_class_week},",
                            f"'room': '{self.room}',",
                            f"'class code': '{self.class_code}',",
                            f"'subject code': '{self.subject_code}',",
                            f"'subject': '{self.subject}',",
                            f"'teacher': '{self.teacher}'",
                            ]) + "\n}"


def login(mssv=None, cccd=None):
    from PIL import Image
    from io import BytesIO

    res = s.get(HOST + '/Account/Login.aspx')
    soup = bs(res.content, 'html.parser')
    captcha_url = soup.find('img', {'alt': 'Captcha image'})['src']

    url = HOST + captcha_url
    response = requests.get(url)
    img_bytes = BytesIO(response.content)
    img = Image.open(img_bytes)

    width, height = img.size
    console_img = img.convert('1').crop((int(width * 0.2), 0, int(width * 0.8), height))

    width, height = console_img.size
    console_img = console_img.resize((int(width / 2.5), int(height / 2.5)))

    width, height = console_img.size
    for y in range(height):
        for x in range(width):
            pixel = console_img.getpixel((x, y))
            if pixel == 0:
                print(' ', end='')
            else:
                print('#', end='')
        print()

    img.show()

    captcha = input('Enter captcha: ')
    data = {"__VIEWSTATE": "",
            "ctl00$ctl00$contentPane$MainPanel$MainContent$rblAccountType": "2",
            "ctl00$ctl00$contentPane$MainPanel$MainContent$tbUserName$State": f"{{&quot;rawValue&quot;:&quot;{mssv}&quot;,&quot;validationState&quot;:&quot;&quot;}}",
            "ctl00$ctl00$contentPane$MainPanel$MainContent$tbUserName": "",
            "ctl00$ctl00$contentPane$MainPanel$MainContent$tbPassword$State": f"{{&quot;rawValue&quot;:&quot;{cccd}&quot;,&quot;validationState&quot;:&quot;&quot;}}",
            "ctl00$ctl00$contentPane$MainPanel$MainContent$tbPassword": "",
            "ctl00$ctl00$contentPane$MainPanel$MainContent$ASPxCaptcha1$TB": captcha,
            "ctl00$ctl00$contentPane$MainPanel$MainContent$btLogin": "Đăng nhập"
            }

    res = s.post(HOST + "/Account/Login.aspx", data=data, allow_redirects=False)

    if res.status_code == 302:
        import pickle
        with open('hust_cookie', 'wb') as file:
            pickle.dump(s.cookies, file)
    else:
        soup = bs(res.content, 'html.parser')
        error1 = soup \
            .find('span', {'id': 'ctl00_ctl00_contentPane_MainPanel_MainContent_FailureText'}) \
            .findChild('font').text

        error2 = soup.find('td', {'id': 'ctl00_ctl00_contentPane_MainPanel_MainContent_ASPxCaptcha1_TB_EC'}).text
        raise Exception(error1 or error2)


def get_timetable():
    res = s.get(HOST + '/Students/Timetables.aspx', allow_redirects=False)
    print(f"cookie: {s.cookies.get_dict()}")
    print(f"status : {res.status_code}")

    soup = bs(res.content, 'html.parser')

    row_num = 1
    row = []
    while True:
        found = soup.find(id=f"ctl00_ctl00_contentPane_MainPanel_MainContent_gvStudentRegister_DXDataRow{row_num - 1}")
        if found is None:
            break
        row.append([td.text for td in found.find_all('td')])
        row_num += 1

    print(row)
    a = [(Parser(each_row)) for each_row in row]
    for i in a:
        print(i.json())
        # print(i.get_no_class_week())


def check_cred(mssv, cccd):
    try:
        import pickle
        with open('hust_cookie', 'rb') as file:
            s.cookies = pickle.load(file)
        status = s.get(HOST + "/Students/Timetables.aspx", allow_redirects=False).status_code
        print(f"cookie from file: {s.cookies.get_dict()}")
        print(f"status from cookie: {status}")
        if status == 302:
            login(mssv, cccd)

    except FileNotFoundError:
        print("No available cookie file")
        print("Proceed to login")
        login(mssv, cccd)


def main():
    # mssv = input("MSSV: ")
    # cccd = input("CCCD: ")
    mssv = "20200597"
    cccd = "001202019959"
    check_cred(mssv, cccd)
    get_timetable()


if __name__ == '__main__':
    main()
