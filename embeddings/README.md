# Embeddings calculation

## Model

From this https://huggingface.co/spaces/mteb/leaderboard.

Выбрал эту `intfloat/multilingual-e5-large-instruct`. ~500M params, max tokens 514 - маловато.

Можно также попробовать `deepvk/USER-bge-m3` - ~350M params, max tokens 8192 - но она хуже чем е5 (но на задачах STS так же работает - а это вроде нам и надо, поэтому норм).

## Process data

### Ad posts

* Only use content from post (raw_text column)

### Channels

* Channel

  * channels.title
  * channels.about

* Posts

  * Last pinned post (channels.last_pinned_msg_id) - if any
  * Last 10 posts (posts_content.raw_text), which have text before target ad post - if any

* Similars(?) - пока не юзаю это тк не уверен что информативно

  * 5 similar channel titles (similars.similar_channel_title)

## intfloat/multilingual-e5-large-instruct

### [Ad posts](/embeddings/e5_instruct/ad_posts/)

По анализу ([ad_posts_analysis](/embeddings/e5_instruct/ad_posts/ad_posts_analysis.ipynb)) длин рекламных постов - они спокойно влезают в context window (обрезаются только ~5%) = 514.

[Embeddings for ad posts calculation](/embeddings/e5_instruct/ad_posts/ad_emb_w_e5_instruct.ipynb)

* Скачал текст рекламных постов из `ml_house.final_basis_with_metrics_v2` с помощью скрипта [download](/embeddings/download.py).
* Добавил к ним промпт для модели (так как модель instruct).
* Посчитал эмбеддинги в Colab (~3 часа).

[ipynb для загрузки эмбедов в БД](/embeddings/e5_instruct/ad_posts/ad_emb_e5_instruct_load_to_db.ipynb)

### [Channels](/embeddings/e5_instruct/channels/)

Для эмбедов канала решил использовать 2 подхода:

1. Simple - Based only on channel's title, about and text of pinned post. Т.е. без использования постов, предыдущих к рекламному
2. Not simple - как симпл, только еще использовать прошлые посты от рекламного

#### Simple

Основывался на предположении о том, что описать канал можно по его названию (есть у каждого канала 100%) + описанию (есть примерно у 95%) + в закрепе обычно тоже важная инфа по каналу (есть у 65%).

NOTE: брал *последний* закрепленный пост - вообще говоря он может быть запощен после таргетного рекламного поста - но всё же не думаю что это большая проблема, так как думаю что тематика канала в целом (которая и будет описана эмбедом) не сильно меняется со временем. Но всё равно при варианте расчета эмбеда канала не только с закрепами (not simple) - буду уже учитывать время постов и брать только прошлые по отношению к таргетному рекламному посту.

Ну и плюс решил так сделать, так как длина контекста у этой модели = 514 и если брать только (channel title, about и текст pinned post) - то уже почти 11% будет обрезано. А значит "втупую" приконкатить еще текст постов не имеет смысл.

[simple_channels_emb_e5_instruct_calculation](/embeddings/e5_instruct/channels/ch_wo_posts_emb_w_e5_instruct.ipynb)

* рассчитывал эмбеддинги по всем каналам которые есть в `scrape.channels`. channel's title, about скачал из `scrape.channels` с помощью [скрипта](/embeddings/download.py)
* для того чтобы получить текст закрепленных постов написал скрипт - он лежит в репе `scrappers` (https://github.com/influai/scrappers/blob/dev/scripts/get_raw_text_of_pinned_posts.ipynb)
* все проценты которые расписал выше, получены из анализа из этого ipynb
* тоже считал в COlab (~30min)

[ipynb для загрузки эмбедов в БД](/embeddings/e5_instruct/channels/ch_wo_posts_emb_e5_instruct_load_to_db.ipynb)

#### [Not simple](/embeddings/e5_instruct/channels/not_simple/) - WIP

ПРосто сконкатенировать посты не получится - не влезет в модель. Значит надо либо:

1. суммаризовать сконкатенированный пост другой моделькой (например мистралью (large) - там большое окно (128k) + фри апи)
2. пулинг - но тут не уверен будет ли норм
3. либо юзать модель с большим контекстным окном чтобы туда влезало это всё - например `deepvk/USER-bge-m3` - контекстное окно 8к - по идее туда может влезть много чего

##### Подход с суммаразацией

1. `SELECT id FROM parse.posts_content WHERE raw_text IS NOT NULL AND raw_text <> '';`
2. `SELECT id, channel_id, post_date FROM parse.post_metadata;`
3. `SELECT id, channel_id, post_date FROM ml_house.final_basis_with_metrics_v2;`

На основе этих таблиц [с помощью этого скрипта](/embeddings/e5_instruct/channels/not_simple/find_ids_of_prev_posts_for_ad_posts.ipynb) рассчитываем отображение от `id поста с рекламой` к `N id постов (содержащих текст) предыдущих по времени к этому рекламному посту`.

Далее, с помощью [скрипта](/embeddings/e5_instruct/channels/not_simple/load_prev_posts_texts.ipynb) скачиваем все текста прошлых постов по отношению к рекламному.

