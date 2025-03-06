import scrapy
from bs4 import BeautifulSoup
import json
from scrapy import FormRequest

def soup_to_scheduler(soup):
    schedule = {}
    for row in soup.find_all('tr')[1:]:  # Bỏ qua hàng đầu tiên chứa tiêu đề
        columns = row.find_all('td')
        day_period = columns[0].text.strip()  # Sáng, Chiều, Tối
        
        for i, column in enumerate(columns[1:], start=2):  # Bắt đầu từ Thứ 2 đến Chủ nhật
            day_of_week = f"Thứ {i}" if i < 8 else "Chủ nhật"
            classes = column.find_all('div', class_='content')
            
            for class_ in classes:
                class_info = {
                    'Tên môn học': class_.find('a').text.strip(),
                    'Mã lớp': class_.find_all('p')[0].text.strip(),
                    'Tiết': class_.find_all('p')[1].text.strip().split('\n')[0].replace('Tiết:', '').strip(),
                    'Phòng': class_.find_all('p')[1].find('span').text.strip(),
                    'Giảng viên': class_.find_all('p')[2].text.strip().replace('GV:', '').strip()
                }
                if day_of_week not in schedule:
                    schedule[day_of_week] = {day_period: [class_info]}
                else:
                    if day_period in schedule[day_of_week]:
                        schedule[day_of_week][day_period].append(class_info)
                    else:
                        schedule[day_of_week][day_period] = [class_info]
    return schedule

class Post(scrapy.Item):
    pass

class MySpider(scrapy.Spider):
    name = 'my_spider'
    def start_requests(self):
        url = "https://sv.iuh.edu.vn/SinhVienTraCuu/GetDanhSachLichTheoTuan"
        formdata = {
            "k": "k=nzmlGyKmW2SCp8gVv0i-wxVEX2HvAGhYxRxBx38PXog"
        }
        yield scrapy.http.FormRequest(url=url, callback=self.parse, formdata=formdata)

    def parse(self, response):
        # create a html of url
        soup = BeautifulSoup(response.text, 'html.parser')
        # get schedule
        schedule = soup_to_scheduler(soup)
        with open('schedule_3.json', 'w', encoding='utf-8') as f:
            json.dump(schedule, f, ensure_ascii=False, indent=4)
        

