from main import main as scraper
from datetime import datetime
d1 = '2019-01-01'
d2 = '2020-01-02'
d1 = datetime.strptime(d1, '%Y-%m-%d').date()
d2 = datetime.strptime(d2, '%Y-%m-%d').date()

scraper(d1, d2)