# python3
# 3.06.2015
# Original: https://github.com/CrackHD/podfm.ru-upload
# Upload API for www.podfm.ru
# ========================================================

def ___demo___():
    """This only demonstates the sample of usage in your script."""
    # If you copy this code as a snippet, better do not touch comments.

    # First import module to your script
    import podfm

    # Then create an instance of API class and authorize (required)    
    # You can use custom user-agent header
    api = podfm.API('hello-world like Gecko/1.0')
    if api.login('username',  'password'):
        print('Login for user "%s" completed.' % api.username)
    else:
        raise Exception('Login was not successful.')
        
    # First open stream to a file for upload
    # MP3 only; <= 100 MB
    with open('podcast.mp3',  'rb') as audioFile:
    
        # Now the upload itself
        podfile = api.upload(audioFile)    
        if not podfile:
            raise Exception('Upload failed.')
        print('Upload done. Podfile id: %d' % podfile)
          
        # Now let's create PodcastInfo instance and set the podcast publish data -- to publish it
        # Notice that ANY attrribute must be set
        new = podfm.PodcastInfo()
        new.pubDate = datetime.datetime.now()
        new.pubTitle = 'Hello PodFM'
        new.pubEpisode = '27'
        new.pubShortDescription = 'Hello world episode to test podfm script.'
        new.pubDescription = 'This script should work just fine. If any problems, there are changes may happen to the site.'
        new.pubDescriptionAutoFormat = True
        new.pubTranscription = None
        new.allowDownload = True
        new.fixMp3IDTags = True

        # You can specify up to 3 categories for a podcast, at least one is required
        new.pubGenres = [ podfm.Genres.hobby,  podfm.Genres.art ]

        # Now, get the lent identifiers on the current profile
        lents = api.queryLents()
        assert len(lents) > 0

        # We will use first one for our new podcast
        new.pubLentID = lents[0]

        # Open file handles for image and MP3 file:
        # GIF/JPG/PNG, <= 350 KB
        with open('podcast.jpg',  'rb') as imageFile:
            new.imageFile = imageFile
            new.pubImageTitle = 'Just a test image.'
            
            # Go on
            published_id = api.publish(podfile,  new)
            if published_id:
                print('Published podcast ID: %d' % published_id)
            else:
                print('Podcast publish failed.')

        # Logout for safety (login requests long-term cookies)
        api.logout()

# ========================================================

import datetime
import requests
from lxml import etree

class PodcastInfo:
    """Podcast prototype with all the properties we may need"""
    pubDate = None
    pubTitle = None
    pubLentID = None
    pubEpisode = None
    pubShortDescription = None
    pubDescription = None
    pubDescriptionAutoFormat = None
    pubTranscription = None
    pubGenres = None
    
    allowDownload = None
    fixMp3IDTags = None

    imageFile = None
    pubImageTitle = None

class Genres:
    """Defines genre IDs for podcasts on upload, which are fixed on PODFM.RU"""    
    audiobooks = 2
    sport = 19
    politics = 15
    business = 8
    technologies = 6
    autos = 9
    science = 20
    internet = 5
    cinema = 7
    art = 27
    diaries = 33
    guides = 37
    hobby = 32
    entertainment = 26
    carriers = 13
    history = 24
    health = 16
    news = 1
    beauty = 10
    music = 30
    relations = 18
    education = 14
    religion = 38
    travel = 22

class API:
    """Allows program to login on PodFM.ru and do the trick..."""
    headers = None
    cookies = None
    username = None

    def __init__(self,  userAgent = 'Mozilla/5.0 (Windows NT 6.1)'):
        self.headers = {
            'User-Agent': userAgent, 
            }

    def login(self,  username,  password):
        """Attempts to authorize a registered user on PodFM.ru by his credentials. Returns True on success, False on fail."""    
        
        r = requests.get('http://podfm.ru/',  headers = self.headers)
        assert r.status_code == 200
        self.cookies = requests.utils.dict_from_cookiejar(r.cookies)
    
        url = 'http://podfm.ru/login/'
        formFields = {
            'a_todo': 'login_check', 
            'todo': 'login', 
            'login': username, 
            'password': password, 
            'remember': 1
            }        
        r = requests.post(url,  headers = self.headers,  data = formFields,  cookies = self.cookies)
        assert r.status_code == 200
        if 'http://podfm.ru/logout' in r.text:
            self.cookies.update(requests.utils.dict_from_cookiejar(r.cookies))
            self.username = username
            return True

        return False

    def logout(self):
        """Sends a logout request and resets API state."""
        assert self.cookies

        r = requests.get('http://podfm.ru/logout/', headers = self.headers,  cookies = self.cookies)
        assert r.status_code == 200
        self.cookies = None

    def queryLents(self):
        """Queries for current user lents and returns a list of IDs."""
        assert self.cookies

        r = requests.get('http://%s.podfm.ru/?mode=lents' % self.username, headers = self.headers,  cookies = self.cookies)
        assert r.status_code == 200
        self.cookies.update(requests.utils.dict_from_cookiejar(r.cookies))

        lents = []

        # NOTICE!! Source HTML looks really dirty, it may change in future, and xpath may not function as expected
        # TODO: Details on lents (title, episodes, link, image, etc) is present but not parsed..
        page = etree.HTML(r.text)
        for e in page.xpath("//div[@class='news' and starts-with(@id, 'slent_')]"):
            assert 'id' in e.attrib
            s = e.get('id')
            s = ''.join(c for c in s if c.isdigit())
            assert (s)
            id = int(s)
            lents.append(id)

        return lents

    def upload(self,  audioFile):
        """Uploads audio file to PodFM server. May take time. On success, returns PodFile ID, file identifier needed for publishing."""
        assert self.cookies
        
        # POST multipart/form-data form with audio file
        url = 'http://%s.podfm.ru/actionuploadpodfile/' % self.username
        formFields = {
            'todo': 'step1_upload', 
            'pod_id': '', 
            }
        files = {
            'file':  ('podcast.mp3', audioFile, 'audio/mp3')
            }            
        r = requests.post(url, cookies = self.cookies,  headers = self.headers,  files = files,  data = formFields)
        assert r.status_code == 200
        self.cookies.update(requests.utils.dict_from_cookiejar(r.cookies))
        
        # Now parse the uploaded file identifier
        assert '?file_id=' in r.url
        s = r.url[r.url.rindex('/'):]
        s = ''.join(c for c in s if c.isdigit())
        if not s:
            raise Exception('Unknown podfile ID -- cannot publish. Upload done...')
        return int(s)

    def publish(self,  podfile,  details):
        """Publishes the uploaded audio as a podcast."""
        assert self.cookies
        assert podfile and isinstance(podfile,  int)
        assert details and isinstance(details,  PodcastInfo)
        assert details.pubDate and isinstance(details.pubDate,  datetime.datetime)
        assert details.pubTitle and details.pubDescription
        assert details.pubLentID and details.imageFile
        assert details.pubEpisode and details.pubGenres
        assert isinstance(details.pubGenres,  list) and len(details.pubGenres) >= 1 and len(details.pubGenres) < 4
        
        # POST multipart/form-data form with podcast properties
        url = 'http://%s.podfm.ru/actionpodcastadd/' % self.username
        files = {
            'image':  ('podcast.jpg', details.imageFile, 'image/jpeg')
            }
        formFields = {
            'id': '', 
            'todo': 'save',
            'file_id': podfile, 
            'make_slide': 'off', 
            'write_tags': boolstr(details.fixMp3IDTags),  
            'day': details.pubDate.day, 
            'month': details.pubDate.month, 
            'year': details.pubDate.year, 
            'hour': details.pubDate.hour, 
            'min': details.pubDate.minute, 
            'number': details.pubEpisode, 
            'name': details.pubTitle, 
            'short_descr': details.pubShortDescription, 
            'body': details.pubDescription, 
            'format': boolstr(details.pubDescriptionAutoFormat), 
            'show_text_descr': bool(details.pubTranscription), 
            'image_alt': details.pubImageTitle, 
            'lent_id': details.pubLentID, 
            'cat_id': details.pubGenres[0]
            }
        if len(details.pubGenres) > 1:
            formFields.update({'cat_id_2': details.pubGenres[1]})
        if len(details.pubGenres) > 2:
            formFields.update({'cat_id_3': details.pubGenres[2]})
        
        r = requests.post(url, cookies = self.cookies,  headers = self.headers,  files = files,  data = formFields)
        assert r.status_code == 200
        self.cookies.update(requests.utils.dict_from_cookiejar(r.cookies))
        
def boolstr(val):
    return ('1' if val else '0')
