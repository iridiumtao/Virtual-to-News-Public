from selenium import webdriver

option = webdriver.ChromeOptions()
option.add_argument("--start-maximized")
driver = webdriver.Chrome('/home/ubuntu/content/chromedriver', options=option)
driver.implicitly_wait(30)#设置隐式等待
url='https://image.baidu.com/search/index?tn=baiduimage&ps=1&ct=201326592&lm=-1&cl=2&nc=1&ie=utf-8&word='+ keyword
driver.get(url)
driver.enconding='UTF-8'
soup=BeautifulSoup(driver.page_source,'html.parser')
body=soup.find('div',attrs={'id':'wrapper'})
body=body.find('div',attrs={'id':'imgContainer'})
body=body.find('div',attrs={'id':'imgid'})

testpic_path = '/home/ubuntu/content/gpt2-ml/scripts/test_pic/'

i=0
count=0
for txt in body.find_all('div',attrs={'class':'imgpage'}):
    txt=txt.find('ul',attrs={'class':'imglist clearfix pageNum'+str(i)})
    i+=1
    for img in txt.find_all('li',attrs={'class':'imgitem'}):
        img=img.find('img')
        img=img.attrs['data-imgurl']
        image=requests.get(img)
        print(img)
        fp = open(testpic_path+  str(count+1) + '.png','wb')
        fp.write(image.content)
        fp.close()
        count+=1
print('爬取图片总数：',count)
pathDir = os.listdir(testpic_path)

driver.quit()