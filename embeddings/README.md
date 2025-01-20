# Embeddings

## Data

### Posts

Для создания эмбеддинга рекламного поста используются следующие данные:

* Текст рекламного поста (атрибут `raw_text` из таблицы `parse.posts_content`)

### Channels

Для создания качественного эмбеддинга канала использую следующие текстовые данные:

* Название (атрибут `title` из таблицы `parse.channels`)
* Описание (атбрибут `about` из таблицы `parse.channels`)
* Текст последнего закрепленного поста (если имеется) (атбрибут `last_pinned_msg_id` из таблицы `parse.channels`)

Основывался на предположении о том, что описать канал можно по его названию (есть у 100%), описанию (есть у 95%), а также закрепленному посту (есть у 65%), в котором часто описана основная информация о канале.

__NOTE__: используется *последний по времени* закрепленный пост - т.е. могут быть ситуации, когда он опубликован позже таргетного рекламного поста, тогда при обучении модель будет иметь данные из будущего. Однако конкретно в этой задаче не думаю, что это проблема, так как тематика канала не сильно меняется со временем.

## Model

[ruMTEB Leaderboard](https://huggingface.co/spaces/mteb/leaderboard)

### intfloat/multilingual-e5-large-instruct

* Parameters: ~500M
* Context: 514 токенов

#### [Posts](./e5-large-instruct/posts/)

В [length-analysis](./e5-large-instruct/posts/length-analysis.ipynb) показано, что рекламные посты "влезают" в контекстное окно модели (обрезается только 5%).

Шаги для расчета эмбеддингов:

1. Скачиваем текст рекламных постов из БД (таблица `ml_house.final_basis_with_metrics_v2`) с помощью [скрипта](./download.py)
2. Рассчитываем эмбеддинги по пайплайну написанному в [calculation.ipynb](./e5-large-instruct/posts/calculation.ipynb)
3. Загружаем эмбеддинги обратно в БД (в таблицу `embeddings.ad_embs`) с помощью [load-to-db.ipynb](./e5-large-instruct/posts/load-to-db.ipynb)

## [Channels](./e5-large-instruct/channels/)

Шаги для расчета эмбеддингов:

1. Скачиваем `title`, `about` атрибуты каналов с помощью [скрипта](./download.py) из таблицы `scrape.channels`
2. Для того чтобы получить текст последних закрепленных постов написал скрипт - он лежит в репозитории `scrappers` (<https://github.com/influai/scrappers/blob/dev/scripts/get_raw_text_of_pinned_posts.ipynb>)
3. Пайплайн расчета эмбеддингов: [calculation.ipynb](./e5-large-instruct/channels/calculation.ipynb)
4. Загружаем эмбеддинги в БД (в таблицу `embeddings.channel_emb`) с помощью [load-to-db.ipynb](./e5-large-instruct/channels/load-to-db.ipynb)
