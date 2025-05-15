# Кластеризация вакансий с HeadHunter

## Описание проекта

Этот проект посвящен анализу и кластеризации вакансий, собранных с портала HeadHunter (hh.ru) с использованием официального API. Основная цель – выявить основные группы (кластеры) специализаций на рынке труда на основе текстовых описаний вакансий и их ключевых навыков. Для векторизации текстов применялись методы TF-IDF и SBERT (на основе трансформеров). Кластеризация проводилась с использованием алгоритмов K-Means. DBSCAN Gaussian Mixture Models (GMM). Результаты анализа включают определение тематики кластеров, топ-характеристик (слова, навыки) и визуализацию распределений.

## Структура проекта

your-project-name/
├── .gitignore             
├── README.md              
├── requirements.txt       
│
├── data/                  
│   └── processed_data/        
│       └── processed_vacancies_dataframe.parquet 
│       └── tfidf_matrix_unigrams.npz           
│       └── tfidf_vectorizer_unigrams.pkl      
│       └── sbert_embeddings_minilm.npy         
│       └── sbert_embeddings_mpnet_base.npy     
│       └── # ... и другие сохраненные артефакты
│
├── notebooks/            
│   └── HH_clustering.ipynb  
│
├── src/                   
│   ── parser/            
│      ├── __init__.py
│      ├── main_parser.py 
│      ├── parser_utils.py
│      └── parser_config.yaml



## Установка и запуск

1.  **Клонируйте репозиторий:**
    ```bash
    git clone https://github.com/knjii/HH_vacancy_clustering
    cd HH_vacancy_clustering
    ```

2.  **Скачайте файлы для быстрой установки:**
    ```bash
    Скачайте файлы для быстрой установки и поместите их в папку, указанную на схеме (..data/processed_data) 
    ```

3.  **Установите зависимости:**
    ```bash
    pip install -r requirements.txt
    ```
    При первой установке `nltk` может потребоваться загрузка дополнительных ресурсов:
    ```python
    import nltk
    nltk.download('stopwords')
    nltk.download('punkt')
    ```

4.  **Парсинг данных (если необходимо собрать свежие данные):**
    *   Настройте файл `src/parser_config.yaml` (укажите критерии поиска, города и т.д.).
    *   Запустите парсер:
        ```bash
        python main.py
        ```

5.  **Анализ и кластеризация:**
    *   Запустите Jupyter Notebook или JupyterLab:
        ```bash
        jupyter notebook
        # или
        # jupyter lab
        ```
    *   Откройте ноутбук `notebooks/HH_clustering.ipynb`.
    *   Если у вас есть эмбеддинги и векторизованные матрицы, установите значение embeddings_matrix_calculated = True
