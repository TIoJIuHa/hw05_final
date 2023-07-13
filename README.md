# Yatube

### Описание проекта

Социальная сеть **Yatube** позволяет пользователям публиковать посты, комментировать посты других пользователей, подписываться на авторов и добавлять свои посты в группы.

Аутентифицированные пользователи могут:
- Просматривать, публиковать, удалять и редактировать свои публикации;
- Просматривать информацию о сообществах;
- Просматривать и публиковать комментарии от своего имени ко всем публикациям, удалять и редактировать свои комментарии;
- Подписываться на других авторов и просматривать свои подписки.

Анонимные пользователи могут:
- Просматривать публикации;
- Просматривать информацию о сообществах;
- Просматривать комментарии.

### Стек технологий

<div>
  <img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54"/>
  <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=green"/>
  <img src="https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white"/>
  <img src="https://img.shields.io/badge/html5-E44D26?style=for-the-badge&logo=html5&logoColor=white"/>
  <img src="https://img.shields.io/badge/bootstrap-8919e6?style=for-the-badge&logo=bootstrap&logoColor=white"/>
  <img src="https://img.shields.io/badge/unittest-%23563D7C?style=for-the-badge&logo=unittest&logoColor=white"/>
</div>

### Как запустить проект

Клонировать репозиторий и перейти в него в командной строке:
```
git clone <project_url>
```
```
cd hw05_final
```

Cоздать и активировать виртуальное окружение:
```
python -m venv venv
```
```
source venv/Scripts/activate
```

Установить зависимости из файла `requirements.txt`:
```
pip install -r requirements.txt
```

Перейти в папку с фалом `manage.py`:
```
cd yatube
```

Выполнить миграции:
```
python manage.py migrate
```

Запустить проект:
```
python manage.py runserver
```
