# ml_dev
data processing, mlflow, pipelines

# Описание сбора 

0_parse_adcopy - сбор из сырых данных постов. 
Выделяем индикаторы рекламы: 

`"подпишись", "подписывайся", "#реклама", "О рекламодателе", 
    "партнёрский пост", "#Ad", "Этот пост спонсирован", "📢",
    "💬", "✉️"`

Каждый индикатор проверялся в посте отдельно. Если в посте есть индикатор ему проставляся target_fla{n}, где n - порядковый номер индикатора в списке. Таким образом, получены поля target_flag1 - target_flag10. 

mapping flag2indicator: 
`target_flag1 - "подпишись"
target_flag2 - "подписывайся"
target_flag3 - "#реклама"
target_flag4 - "О рекламодателе"
target_flag5 - "партнёрский пост"
target_flag6 - "#Ad"
target_flag7 - "Этот пост спонсирован"
target_flag8 - "📢"
target_flag9 - "💬"
target_flag10 - "✉️"`

Важно: индикатор не означает, что пост рекламный. Например, при индикаторе "#реклама" чаще всего встречается реклама. Индикатор "💬" содержит много обычных постов. Поэтому внутри флагов стоит фильтроваться.

Сохранено в схеме ml_house, в таблице ad_basis

# Обработка метрик

1_metrics_shop - обработка метрик постов. Обработка произведена по всем постам

- Выделены топ-5 реакций, для них созданы отдельные поля с абсолютными значениями 
- Посчитаны относительные фичи. Везде нормировалась на количество просмотров 
- Расчитаны общее количество реакций, активностей на посте, к ним расчитаны относительные значения 

Полученные значения присоединены к ad_basis и сохранены в basis_with_metrics. 
Абсолютные/относительные значения постов из базиса можно прогнозировать. 

Агрегаты по предыдущим постам к базису будут расчитаны и сохранены отдельно (soon)

# Присоединение фичей поста, канала: 

2_flags_basis - присоединение фичей. 

- Добавлены флаги поста (флаги аудио, фото, видео и тд) из posts_flags
- Добвлена дата поста из posts_metadata
- Добавлено число подписчиков, описание канала из channels

Сохранено в final_basis в схеме ml_house

# Для моделирования: 

Фичи long_list: 
`['raw_text', 
 'cnt_urls', 
 'participants', 
 'about',  
 'is_post',
 'silent',
 'noforwards',
 'pinned',
 'fwd_from_flag',
 'photo',
 'document',
 'web',
 'audio',
 'voice',
 'video',
 'gif']` (update soon)

Таргет (можно выбрать любое поле): 
`['views',
 'forwards',
 'comments',
 'paid_reactions',
 'standard_reactions',
 'custom_reactions',
 'sum_standard_reactions',
 'sum_custom_reactions',
 'total_sum_reactions',
 'good_finger',
 'heart',
 'fire',
 'fun',
 'bad_finger',
 'total_activites',
 'relative_total_sum_reactions',
 'relative_paid_reactions',
 'relative_good_finger',
 'relative_sum_custom_reactions',
 'relative_forwards',
 'relative_heart',
 'relative_comments',
 'relative_fun',
 'relative_sum_standard_reactions',
 'relative_bad_finger',
 'relative_fire',
 'relative_total_activites'
]`
