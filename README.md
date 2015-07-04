# github.com/CrackHD/PodFM.ru
API для работы с сайтом PodFM. В настоящее время поддерживается авторизация, загрузка и публикация подкастов.

See english comments and how-to in code file!

```python
# Демонстрация загрузки и публикации подкаста на сайт PODFM.RU
# При копировании этого кода лучше не удалять комментарии

# Импортируем скрипт для работы PodFM.ru
import podfm

# Теперь, используя класс **podfm.API** авторизуемся на сайте (необходимо)
# Для работы можно использовать кастомный User-Agent
api = podfm.API('hello-world like Gecko/1.0')
if api.login('username',  'password'):
    print('Авторизация для пользователя "%s" успешна.' % api.username)
else:
    raise Exception('Авторизация не удалась.')
    
# Открываем для чтения аудиофайл, который необходимо загрузить
# Поддерживаемые форматы: MP3, лимит размера файла: 100 МБ
with open('podcast.mp3',  'rb') as audioFile:

    # Выполняем закачку на сервер PodFM
    podfile = api.upload(audioFile)    
    if not podfile:
        raise Exception('Закачка аудиофайла неудалась.')
    print('Upload done. Podfile id: %d' % podfile)
      
    # Теперь с помощью класса **podfm.PodcastInfo** определим информацию, необходимую для публикации подкаста
    # Все атрибуты обязательны, за исключением транскрипции
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

    # Можно указать не более 3 и не менее одной категории для подкаста.
    # Идентификаторы см. в перечислении **podfm.Genres**
    new.pubGenres = [ podfm.Genres.hobby,  podfm.Genres.art ]

    # Теперь получим список лент в профиле текущего пользователя
    lents = api.queryLents()
    assert len(lents) > 0

    # Мы опубликуем подкаст в самой первой из них
    new.pubLentID = lents[0]

    # Для публикации подкаста также необходимо загрузить для него отдельное изображение.
    # Поддерживаемые форматы изображения: GIF/JPG/PNG
    # Лимит размера изображения: 350 КБ
    with open('podcast.jpg',  'rb') as imageFile:
        new.imageFile = imageFile
        new.pubImageTitle = 'Just a test image.'
        
        # Выполняем публикацию в ленту
        published_id = api.publish(podfile,  new)
        if published_id:
            print('Опубликован подкаст. ID: %d' % published_id)
        else:
            print('Публикация подкаста не удалась.')

    # Для безопасности разлогинимся
    api.logout()
```
