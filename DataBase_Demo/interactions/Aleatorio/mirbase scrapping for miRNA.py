import requests
from bs4 import BeautifulSoup
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
import os
from pytictoc import TicToc

# URL base de la página web
url_base_1 = 'https://www.mirbase.org/results/?query='
url_base_2 = 'https://www.mirbase.org/mature/'  
url_base_3 = 'https://www.mirbase.org/'

# Función para buscar y extraer información
def buscar_y_extraer_2(url_base, valor, session):
    url_de_busqueda = f"{url_base}{valor}"
    response = session.get(url_de_busqueda)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        td_row_title = soup.find('td', class_='row-title', text='Sequence')
        if td_row_title:
            td_siguiente = td_row_title.find_next_sibling('td')
            if td_siguiente:
                valor = td_siguiente.text
            else:
                print('No se encontró el siguiente <td>.')
        else:
            print('No se encontró el <td> con la clase "row-title" y el texto "Sequence".')

        strong_element = soup.find('h4', class_='section-header').find('strong')
        if strong_element:
            nombre = strong_element.text.strip()
        else:
            nombre = 'No se encontró el nombre'

        td_hairpins = soup.find('td', class_='row-title', text='Hairpins')
        if td_hairpins:
            td_siguiente = td_hairpins.find_next_sibling('td')
            if td_siguiente:
                enlace = td_siguiente.find('a', href=True)
                if enlace:
                    url = enlace['href']
                else:
                    print('No se encontró el enlace <a>.')
            else:
                print('No se encontró el siguiente <td>.')
        else:
            print('No se encontró el <td> con la clase "row-title" y el texto "Hairpins".')

        return nombre, valor, url

def buscar_y_extraer_3(url_base, valor, session): 
    url_de_busqueda = f"{url_base}{valor}"
    response = session.get(url_de_busqueda)

    soup = BeautifulSoup(response.content, 'html.parser')

    span_sequence = soup.find('span', id='myspan')
    sequence = span_sequence.text if span_sequence else 'No se encontró la secuencia'

    span_structure = span_sequence.find_next_sibling('span') if span_sequence else None
    structure = span_structure.text if span_structure else 'No se encontró la estructura'

    h4_element = soup.find('h4', class_='row-title-structure')
    nombre_precursor = h4_element.find('strong').text if h4_element else 'No se encontró el valor de Stem-loop'

    return nombre_precursor, sequence, structure

# Función para ejecutar en paralelo
def worker(i):
    try:
        session = requests.Session()
        formatted_number = str(i).zfill(7)
        numero = str(formatted_number)
        buscar = 'MIMAT' + numero
        print(buscar)

        nombre_miRNA, secuencia_miRNA_especifico, url = buscar_y_extraer_2(url_base_2, buscar, session)
        nombre_precursor, secuencia_precursor, secuencia_2D_precursor = buscar_y_extraer_3(url_base_3, url, session)
        
        print(f'Nombre de miRNA: {nombre_miRNA}')
        print(f'Secuencia miRNA especifico: {secuencia_miRNA_especifico}')
        print(f'Nombre precursor: {nombre_precursor}')
        print(f'Secuencia precursor: {secuencia_precursor}')
        print(f'Secuencia 2D precursor: {secuencia_2D_precursor}')

        return f'{nombre_miRNA},{secuencia_miRNA_especifico},{nombre_precursor},{secuencia_precursor},{secuencia_2D_precursor}\n', None
    except Exception as e:
        print(f'Error en la iteración {i}: {e}')
        return None, buscar

def worker_with_threads(start, end, failed_tasks):
    results = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(worker, i) for i in range(start, end)]
        for future in futures:
            result, failed_task = future.result()
            if result:
                results.append(result)
            if failed_task is not None:
                failed_tasks.append(failed_task)
    return results

if __name__ == '__main__':
    t = TicToc()
    t.tic()
    output_file_path = "C:/Users/steve/Downloads/Test/data_miRNA_test"
    with open(output_file_path, "w") as f:
        f.write('Nombre miRNA,Secuencia miRNA Especifico,Nombre Precursor,Secuencia Precursor,Secuencia 2D Precursor\n')

    # Rango para dividir el trabajo
    num_workers = os.cpu_count()
    num_tasks = 50500
    chunk_size = num_tasks // num_workers

    failed_tasks = multiprocessing.Manager().list()

    # Crear un Pool de procesos y mapea la función worker_with_threads a los valores del rango
    with multiprocessing.Pool(processes=num_workers) as pool:
        ranges = [(i * chunk_size, (i + 1) * chunk_size, failed_tasks) for i in range(num_workers)]
        if num_tasks % num_workers != 0:
            ranges[-1] = (ranges[-1][0], num_tasks, failed_tasks)

        results = pool.starmap(worker_with_threads, ranges)

    # Escribir los resultados en el archivo
    with open(output_file_path, "a") as f:
        for result_chunk in results:
            for result in result_chunk:
                f.write(result)

    # Guardar las tareas fallidas en un archivo o imprimirlas
    if failed_tasks:
        print("Tareas fallidas:")
        with open("C:/Users/steve/Downloads/Test/failed_tasks_test.txt", "w") as f:
            for task in failed_tasks:
                f.write(f"{task}\n")
        print(list(failed_tasks))

    t.toc()