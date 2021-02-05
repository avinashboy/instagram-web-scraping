from selenium import  webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time , json, os, urllib.request , argparse, cv2 , moviepy.editor as mp, shutil
from plyer import notification

class Instagram:

    def __init__(self, name, outputFormat, mode):
        self.name = name
        self.outputFormat = outputFormat
        self.posts = []
        self.mode = mode

    def jsonFile(self, posts):
        fileName = self.name + '.json'
        jsonFile = json.dumps(posts, indent = 1)
        file = open(fileName, "w")
        file.write(jsonFile)
        file.close()
        print("[+] JSON is complete")

    def noti(self, heading, description):
         return notification.notify(title=heading, message=description , timeout=3)

    def posting(self, driver):
        count = 0
        links = driver.find_elements_by_class_name('FFVAD')
        for link in links:
            post = link.get_attribute('src')
            self.posts.append( post )
            count+= 1
        print("[+] No of photo count:{}".format(count))

    def downloading(self, posts):
        down = 'downloading is initiated...'
        print("[+] {}".format(down.upper()))
        dir = self.name
        parent_dir = os.getcwd()
        path = os.path.join(parent_dir, dir)
        os.mkdir(path)
        os.chdir(path)
        count = 0
        for post in posts:
            count +=1
            urllib.request.urlretrieve( post , '{}.jpg'.format( count ))
        print("[+] The folder name is {} & total no of photo is: {}".format(self.name, count))
        os.chdir(os.path.normpath(path + os.sep + os.pardir))

    def video(self, mod = 'none'):
        dir_path = './{}'.format(self.name)
        output = self.outputFormat
        images = []
        for f in os.listdir(dir_path):
            images.append(f)
        image_path = os.path.join(dir_path, images[1])
        frame = cv2.imread(image_path)
        cv2.imshow('video',frame)
        height, width, channels = frame.shape
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output, fourcc, 5, (width, height))
        for image in images:
            image_path = os.path.join(dir_path, image)
            frame = cv2.imread(image_path)
            out.write(frame)
            cv2.imshow('video',frame)

        out.release()
        cv2.destroyAllWindows()
        print("[+] The output video is {}".format(output))
        if mod == 'v':
            shutil.rmtree('{}'.format(self.name))

    def writeIntoHtml(self, posts):
        htmlContent = """
        <!DOCTYPE html>
        <html lang="en">

        <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>"""+"IG-{}".format(self.name)+"""</title>
          <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css"
            integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
          <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/simplelightbox/2.2.2/simple-lightbox.css"/>
          <script src="https://code.jquery.com/jquery-3.5.1.js"></script>
          <script src="https://cdnjs.cloudflare.com/ajax/libs/simplelightbox/2.2.2/simple-lightbox.jquery.js"></script>
          <script src="https://cdnjs.cloudflare.com/ajax/libs/simplelightbox/2.2.2/simple-lightbox.js"></script>
        </head>
        <style>
          .kutty {
            height: 200px;
            width: 200px;
          }
          body{
            text-align: center;
          }
        </style>

        <body>

          <div class="container">
            <h1 class="font-italic">Photo:<span class="text-info" id="nophoto"></span></h1>
            <div id="pho" style="display: flex; flex-wrap: wrap; gap: 1rem; justify-content: center;">

            </div>

          </div>
        </body>
        <script>

        const arr = """ +"{}".format(posts)+"""

          getData(arr)

          function getData(d) {

            function em(gt) {
              return `<div class="gallery"><a href="${gt}" class="big"><img src="${gt}" alt="${gt.length}" class="rounded mx-auto d-block kutty"></a></div>`
            }
            document.getElementById('nophoto').innerText = d.length
            document.getElementById('pho').innerHTML = d.map(em).join('')
          }

          $(function() {
            const $gallery = $('.gallery a').simpleLightbox();
          });
        </script>

        </html>

         """
        fileName = '{}-photo'.format(self.name) + '.html'
        file = open(fileName, "w")
        file.write(htmlContent)
        file.close()
        print("[+] HTML file is complete file name: {}".format(fileName))

    def startProcessing(self):
        if not os.path.exists('chromedriver.exe'):
            chrome = 'https://drive.google.com/uc?id=1qE3yfDgzq8GJxG5ZmLiZ22ZfmAuTsyKi&export=download'
            urllib.request.urlretrieve( chrome , 'chromedriver.exe')
        time.sleep(1)
        instagramPage = "https://www.instagram.com/{}".format(self.name)
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--incognito")
        driver = webdriver.Chrome(ChromeDriverManager().install(),chrome_options=chrome_options)
        driver.get(instagramPage)
        ProfileDp = driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/header/div/div/span/img').get_attribute('src')
        self.posts.append( ProfileDp )
        lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        match=False
        time.sleep(2)
        try:  
            btnClassName = driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div[3]/div[1]/div/button')
            btnClassName.click()
        except Exception as e:
            btnClassName = driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div[2]/div[1]/div/button')
            btnClassName.click()
        while(match==False):
            lastCount = lenOfPage
            time.sleep(4)
            self.posting(driver)
            lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
            if lastCount==lenOfPage:
                match=True
        self.posts = list(dict.fromkeys(self.posts))
        if self.mode == 'j':
            self.jsonFile(self.posts)
            self.noti("Json", "process is completed...!")
        if self.mode == 'h':
            self.writeIntoHtml(self.posts)
            self.noti("Html", "process is completed...!")
        if self.mode == 'p':
            self.downloading(self.posts)
            self.noti("Photo", "process is completed...!")
        if self.mode == 'v':
            self.downloading(self.posts)
            self.video(self.mode)
            self.noti("Video", "process is completed...!")
        if self.mode == 'a':
            self.jsonFile(self.posts)
            self.downloading(self.posts)
            self.video()
            self.writeIntoHtml(self.posts)
            self.noti("All", "process is completed...!")
        driver.close()

ap = argparse.ArgumentParser()
ap.add_argument("-n", "--name", required=False, default='trishakrishnan', help="Instagram name. It must public account name.")
# ap.add_argument("-o", "--output", required=False, default='output.mp4', help="output video file.")
ap.add_argument("-m", "--mode", required=False, default='j', help=" 'j' is json file.\n 'p' is photo.\n 'v' is video.\n 'a' is all the above")
args = vars(ap.parse_args())

CheckArray = ['j', 'v' , 'p', 'a', 'h']
movie = args['name']+'.mp4'
if movie.endswith('.mp4'):
    if args['mode'].lower() in CheckArray and len(args['mode'].lower()) <= 1 :
        start = Instagram(args['name'],movie,args['mode'].lower())
        start.startProcessing()
    else:
        print("[-] Invalid mode or just pick one mode.")
else:
    print("[-] Please give the .mp4 extension.")
