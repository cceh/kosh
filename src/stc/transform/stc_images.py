import requests


# 1-894
def get_stc_images():
    for i in range(1, 894):
        page = 'pg_' + str(i).zfill(3)
        url = "http://www.sanskrit-lexicon.uni-koeln.de/scans/STCScan/2013/web/pdfpages/" + page + '.pdf'
        print(url)
        response = requests.get(url)
        with open('data/images/stc_' + page + '.pdf', 'wb') as f:
            f.write(response.content)


get_stc_images()
