import requests
import numpy as np
import pandas as pd
import time

from parser_utils import load_config 

request_config = load_config('parser_config.yaml')

MAX_PAGES_TO_FETCH_PER_QUERY = 40  
VACANCIES_PER_PAGE_API = 100       

PAUSE_AFTER_DETAIL_REQUEST = 0.5 
PAUSE_AFTER_PAGE_PROCESSED = 2 

def get_detailed_vacancy_info(vacancy_id):
    """
    Получает детальную информацию по одной вакансии.
    """
    if not vacancy_id:
        return None
    
    headers_for_detailed_request = {
        'User-Agent': 'VacancyParser_for_university_project/1.1'
    }
    REQUEST_TIMEOUT_DETAILED = 10 

    detail_url = f'https://api.hh.ru/vacancies/{vacancy_id}'
    try:
        response = requests.get(detail_url, headers=headers_for_detailed_request, timeout=REQUEST_TIMEOUT_DETAILED)
        response.raise_for_status()
        return response.json()
    except Exception as e: 
        print(f"Непредвиденная ошибка для вакансии {vacancy_id}: {e}")
    return None


def process_single_vacancy(single_vacancy_item_from_list):
    """
    Обрабатывает данные одной вакансии из списка и добавляет детали.
    """
    processed_dict = {}
    processed_dict['id'] = single_vacancy_item_from_list.get('id')
    processed_dict['Vacancy_name'] = single_vacancy_item_from_list.get('name', np.nan)
    
    area_info = single_vacancy_item_from_list.get('area')
    processed_dict['City'] = area_info.get('name', np.nan) if area_info else np.nan

    employer_info = single_vacancy_item_from_list.get('employer')
    processed_dict['Employer_name'] = employer_info.get('name', np.nan) if employer_info else np.nan

    processed_dict['alternate_url'] = single_vacancy_item_from_list.get('alternate_url')

    salary_info = single_vacancy_item_from_list.get('salary')
    if salary_info:
        processed_dict['salary_from'] = salary_info.get('from')
        processed_dict['salary_to'] = salary_info.get('to')
        processed_dict['salary_currency'] = salary_info.get('currency')
    else:
        processed_dict['salary_from'] = np.nan
        processed_dict['salary_to'] = np.nan
        processed_dict['salary_currency'] = np.nan
        
    snippet_info = single_vacancy_item_from_list.get('snippet')
    if snippet_info:
        processed_dict['requirement_snippet'] = snippet_info.get('requirement')
        processed_dict['responsibility_snippet'] = snippet_info.get('responsibility')
    else:
        processed_dict['requirement_snippet'] = np.nan
        processed_dict['responsibility_snippet'] = np.nan

    employment_info = single_vacancy_item_from_list.get('employment')
    processed_dict['employment_type'] = employment_info.get('name', np.nan) if employment_info else np.nan

    schedule_info = single_vacancy_item_from_list.get('schedule')
    processed_dict['schedule_type'] = schedule_info.get('name', np.nan) if schedule_info else np.nan
    
    experience_info = single_vacancy_item_from_list.get('experience')
    processed_dict['experience_required'] = experience_info.get('name', np.nan) if experience_info else np.nan

    vacancy_id = processed_dict['id']
    detailed_info = get_detailed_vacancy_info(vacancy_id)

    if detailed_info:
        # Сохраняем HTML как есть, очистка будет в другом скрипте
        processed_dict['full_description_html'] = detailed_info.get('description', np.nan) 
        
        key_skills_list_of_dicts = detailed_info.get('key_skills', [])
        if key_skills_list_of_dicts: # Проверяем, что это не пустой список и не None
            processed_dict['key_skills_str'] = ", ".join([
                skill.get('name', '') for skill in key_skills_list_of_dicts if skill.get('name')
            ]).strip()
            if not processed_dict['key_skills_str']: # Если после join пустая строка
                 processed_dict['key_skills_str'] = np.nan
        else:
            processed_dict['key_skills_str'] = np.nan
    else:
        processed_dict['full_description_html'] = np.nan
        processed_dict['key_skills_str'] = np.nan
    return processed_dict


def parse_vacancies_from_hh(city_list_config, vacancy_names_config):
    base_url = 'https://api.hh.ru/vacancies'
    all_processed_vacancies = []
    headers = {
        'User-Agent': 'VacancyParser_for_university_project/1.1'
    }
    REQUEST_TIMEOUT_LIST = 15 # Таймаут для запроса списка

    total_queries = len(city_list_config) * len(vacancy_names_config)
    current_query_count = 0

    for city_params in city_list_config:
        city_id = city_params['city_id']
        city_name_for_log = city_params.get('city_name', str(city_id))
        
        for vacancy_search_text in vacancy_names_config:
            current_query_count += 1
            print(f"\n[{current_query_count}/{total_queries}] Город: {city_name_for_log}, Запрос: '{vacancy_search_text}'")
            
            for page_num in range(MAX_PAGES_TO_FETCH_PER_QUERY):
                params = {
                    'text': vacancy_search_text,
                    'area': city_id,
                    'per_page': VACANCIES_PER_PAGE_API,
                    'page': page_num 
                }
                print(f"  Страница: {page_num + 1}/{MAX_PAGES_TO_FETCH_PER_QUERY} (API page index: {page_num})")

                try:
                    response_list = requests.get(base_url, params=params, headers=headers, timeout=REQUEST_TIMEOUT_LIST)
                    response_list.raise_for_status() 
                    
                    current_page_json = response_list.json()
                    vacancy_items_on_page = current_page_json.get('items', [])
                    
                    if not vacancy_items_on_page:
                        print(f"  Вакансий на странице {page_num} нет. Завершаю для текущего запроса.")
                        break 

                    print(f"  Найдено вакансий на странице: {len(vacancy_items_on_page)}. Обрабатываю...")
                    
                    for i, single_vacancy_raw_data in enumerate(vacancy_items_on_page):
                        print(f"    Обработка вакансии {i+1}/{len(vacancy_items_on_page)} (ID: {single_vacancy_raw_data.get('id')})...", end='\r')
                        processed_vacancy = process_single_vacancy(single_vacancy_raw_data)
                        all_processed_vacancies.append(processed_vacancy)
                        # Небольшая пауза после каждого детального запроса, чтобы не превышать rps лимит
                        time.sleep(PAUSE_AFTER_DETAIL_REQUEST) 
                    print(" " * 80, end='\r') 

                    total_pages_api = current_page_json.get('pages', 0)
                    if page_num >= total_pages_api - 1: # Если текущая страница последняя по данным API
                        print(f"  Это была последняя доступная страница ({page_num + 1} из {total_pages_api}) по данным API.")
                        break 
                    
                    time.sleep(PAUSE_AFTER_PAGE_PROCESSED)

                except Exception as e: 
                    print(f"Непредвиденная ошибка (стр. {page_num}): {e}")
                    break 
            
            print(f"Закончен поиск по запросу: '{vacancy_search_text}'. Собрано всего: {len(all_processed_vacancies)} вакансий.")
                
    return all_processed_vacancies

if __name__ == "__main__":
    start_time = time.time()
    print("Запуск парсера вакансий HH.ru...")
    
    final_vacancies_list = parse_vacancies_from_hh(request_config['cities'], request_config['vacancies'])
    
    if final_vacancies_list:
        print(f"\nСбор данных завершен. Всего собрано и обработано вакансий: {len(final_vacancies_list)}")
        df = pd.DataFrame(final_vacancies_list)
        
        if not df.empty:
            print("\nПервые 3 вакансии в DataFrame:")
            print(df.head(3))
        else:
            print("\nDataFrame пуст.")
        
        from datetime import datetime
        current_date_str = datetime.now().strftime("%Y-%m-%d")
        output_filename = f'hh_parsed_vacancies_{current_date_str}.csv'
        
        try:
            df.to_csv(output_filename, index=False, encoding='utf-8')
            print(f"\nВсе данные успешно сохранены в файл: {output_filename}")
        except Exception as e:
            print(f"\n!!!! Ошибка при сохранении CSV файла '{output_filename}': {e}")
    else:
        print("\nНе было собрано ни одной вакансии.")

    end_time = time.time()
    print(f"\nВремя выполнения скрипта: {end_time - start_time:.2f} секунд.")