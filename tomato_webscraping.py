import requests
from bs4 import BeautifulSoup
import json
import os

# URL do IMDb que você deseja fazer o scraping
url = 'https://www.rottentomatoes.com/browse/movies_at_home/sort:popular?page=5'

# Definindo um cabeçalho para simular um navegador
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

movie_data = {
                "Title": "movie_title",
                "Genres": "genre_list",
                "Release Dates": "release_dates",
                "Runtime": "runtime",
                "Rating": "rating",
                "Actors": "actor_list",
                "Tomatometer": "tomatometer",
                "Popcornmeter": "popcornmeter"
            }

with open("./teste.json", 'w') as file:
    json.dump(movie_data, file, indent=4)

# Fazendo uma requisição GET para a página com o cabeçalho
response = requests.get(url, headers=headers, timeout=10)
# Verifica se a requisição foi bem-sucedida
if response.status_code == 200:
    # Criando um objeto BeautifulSoup
    imdb_soup = BeautifulSoup(response.text, 'html.parser')
    
    # Encontrando a tabela de filmes
    lista = imdb_soup.find('div', class_='discovery-tiles__wrap')
    # Extraindo os filmes
    movie_links = []
    for item in lista.find_all('div'):  # Ignorando o cabeçalho
        # Requisição para a página do filme para obter mais detalhes
        # print()
        # print(item)
        # print()
        if item.a is None:
            continue
        movie_path = item.a['href']
        movie_link = "https://www.rottentomatoes.com" + movie_path
        # movie_response = requests.get(movie_link, headers=headers, timeout=10)
        if movie_link not in movie_links:
            movie_links.append(movie_link)
            # print(movie_link)
    # print(movie_links[0])
    for movie_link in movie_links:

        movie_response = requests.get(movie_link, headers=headers, timeout=10)
        if movie_response.status_code == 200:
            tomato_movie_soup = BeautifulSoup(movie_response.text, 'html.parser')
            
            # Extraindo mais dados da página do filme
            category_wrap_divs = tomato_movie_soup.find_all('div', class_="category-wrap")

            media_hero = tomato_movie_soup.find('media-hero')
            media_hero_rts = media_hero.find_all('rt-text')

            movie_title = ""
            for rt in media_hero_rts:
                if "title" == rt.get('slot'):
                    movie_title = rt.get_text()

            genre_list = []
            release_dates = []
            runtime = ""
            rating = ""
            for div in category_wrap_divs:
                div_dt = div.find("dt").get_text()
                if "Genre" in div_dt:
                    dd = div.find("dd")
                    rt_tags = dd.find_all("rt-link")
                    for div in rt_tags:
                        genre_list.append(div.get_text())
                
                elif "Release Date (Theaters)" in div_dt:
                    dd = div.find("dd")
                    release_dates.append("Theaters: " + dd.find("rt-text").get_text() )
                
                elif "Release Date (Streaming)" in div_dt:
                    dd = div.find("dd")
                    release_dates.append("Streaming: " +dd.find("rt-text").get_text())
                
                elif "Runtime" in div_dt:
                    dd = div.find("dd")
                    runtime = dd.find("rt-text").get_text()
                
                elif "Rating" in div_dt:
                    dd = div.find("dd")
                    rating = dd.find("rt-text").get_text()
            
            actor_list = []
            actor_section = tomato_movie_soup.find('section', class_="cast-and-crew")
            if actor_section:
                actor_wrap = actor_section.find('div', class_="content-wrap")
                actors_anchors = actor_wrap.find_all('a', {"data-qa": "person-item"})
                for actor_anchor in actors_anchors:
                    text_divs = actor_anchor.find("div", {"slot": "insetText"})
                    actor = text_divs.find("p", class_="name")
                    character = text_divs.find("p", class_="role")
                    actor_list.append(f"{actor.get_text()} ({character.get_text()})")


            tomatometer = tomato_movie_soup.find('rt-text', {"slot": "criticsScore"}).get_text()
            popcornmeter = tomato_movie_soup.find('rt-text', {"slot": "audienceScore"}).get_text()

            # Define the path to the JSON file
            json_file_path = '/Users/mathmac/local tests/ufsc/webscrapping/imdb-data-crawling/movies_data.json'

            # Load existing data from the JSON file if it exists
            if os.path.exists(json_file_path):
                with open(json_file_path, 'r') as file:
                    movies_data = json.load(file)
            else:
                movies_data = []

            # Create a dictionary with the movie data
            movie_data = {
                "Title": movie_title,
                "Genres": genre_list,
                "Release Dates": release_dates,
                "Runtime": runtime,
                "Rating": rating,
                "Actors": actor_list,
                "Tomatometer": tomatometer,
                "Popcornmeter": popcornmeter
            }
            print(movie_data)
            # Append the new movie data to the list
            movies_data.append(movie_data)

            # Save the updated data back to the JSON file
            with open(json_file_path, 'w') as file:
                json.dump(movies_data, file, indent=4)
            