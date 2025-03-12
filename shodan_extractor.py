import json
import requests
from bs4 import BeautifulSoup
import re
from requests.exceptions import ConnectionError, HTTPError, Timeout, RequestException

def is_number_greater_than_ten(html):
    # Creiamo l'oggetto BeautifulSoup per il parsing dell'HTML
    soup = BeautifulSoup(html, 'html.parser')
    
    # Troviamo l'elemento <h4> e otteniamo il suo contenuto (che dovrebbe essere un numero)
    number_tag = soup.find('h4')
    
    if number_tag:
        # Estraiamo il numero come stringa e lo convertiamo in un intero
        try:
            number = int(number_tag.get_text().strip())
            #print(number)
            # Verifica se il numero è maggiore di 10
            return number > 10
        except ValueError:
            # Se non è possibile convertire in intero, ritorniamo False
            return False
    else:
        # Se non troviamo un tag <h4>, ritorniamo False
        return False

def load_cookies_from_file(json_file):
    """Carica i cookie da un file JSON."""
    with open(json_file, 'r') as file:
        data = json.load(file)
        cookies = {}
        for cookie in data["cookies"]:
            cookies[cookie["name"]] = cookie["value"].strip('"')
        return cookies

def fetch_html_with_cookies(url, cookies):
    """Esegue una richiesta GET con i cookie specificati e restituisce l'HTML della risposta."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, cookies=cookies, headers=headers, timeout=10)  # Timeout per evitare attese infinite
        response.raise_for_status()  # Solleva un'eccezione se il codice di stato è un errore HTTP
        return response.text
    except ConnectionError as conn_err:
        #print(f"Errore di connessione: {conn_err}")
        pass
    except Timeout as timeout_err:
        #print(f"Timeout della richiesta: {timeout_err}")
        pass
    except HTTPError as http_err:
        #print(f"Errore HTTP {http_err.response.status_code}: {http_err.response.reason}")
        pass
    except RequestException as req_err:
        pass
        #print(f"Errore generico nella richiesta: {req_err}")
    return None

def extract_ip_port_pairs(html, base_url):
    """Estrae coppie IP:Porta dall'HTML usando regex e parsing."""
    ip_port_pairs = []

    # Regex per trovare IP validi
    ip_pattern = r'\/host\/(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
    port_pattern = r'port%3A(\d+)'
    if html is None:
        return []  # Restituisce una lista vuota o un valore appropriato per gestire l'errore
    soup = BeautifulSoup(html, 'html.parser')
    elements = soup.find_all('a', class_='title text-dark')

    for element in elements:
        href = element.get('href', '')
        ip_match = re.search(ip_pattern, href)
        port_match = re.search(port_pattern, base_url)

        if ip_match:
            ip = ip_match.group(1)
            port = port_match.group(1) if port_match else None
            ip_port_pairs.append(f"{ip}:{port}" if port else ip)

    return ip_port_pairs

def get_facet_data(base_url, query, facet):
    """Esegue una richiesta per ottenere i dati di un particolare facet (city, org)."""
    facet_url = f"{base_url}/search/facet?query={query}&facet={facet}"
    response = requests.get(facet_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        for div in soup.find_all("div", class_="four columns name"):
            a_tag = div.find("a", href=True)
            if a_tag:
                results.append(base_url + a_tag['href'])
        return results
    else:
        #print(f"Errore nel recupero dei dati del facet {facet}: {response.status_code}")
        return []

def main():
    base_url = "https://www.shodan.io"
    query = ''#input("Inserisci la query da cercare su Shodan: ")
    cookies_file = ''#input("Inserisci il percorso del file JSON dei cookie: ")

    cookies = load_cookies_from_file(cookies_file)

    # Ottieni le porte dalla query
    query_url = f"{base_url}/search/facet?query={query}&facet=port"
    response = requests.get(query_url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []

        for div in soup.find_all("div", class_="four columns name"):
            a_tag = div.find("a", href=True)
            if a_tag:
                results.append(a_tag['href'].split("=")[-1])

        with open("url.txt", "a") as file:
            # Elaborazione delle città e organizzazioni
            for result in results:
                cities = get_facet_data(base_url, result, "city")
                organizations = get_facet_data(base_url, result, "org")

                #print(f"Result: {result}")
                for city_url in cities:
                    html = fetch_html_with_cookies(city_url, cookies)
                    if html:
                        ip_port_pairs = extract_ip_port_pairs(html, city_url)
                        #print(f"Città ({city_url}): {ip_port_pairs}")
                        # Scrivere ogni coppia IP:Port su una riga separata
                        for ip_port in ip_port_pairs:
                            print(f"{ip_port}")
                            #file.write(f"{ip_port}")
                        if is_number_greater_than_ten(html):
                            if html:
                                html = fetch_html_with_cookies(city_url+"&page=2", cookies)
                                ip_port_pairs = extract_ip_port_pairs(html, city_url+"&page=2")
                                #print(f"Città {city_url}&page=2 (Pagina2) : {ip_port_pairs}")
                                for ip_port in ip_port_pairs:
                                    print(f"{ip_port}")
                                    #file.write(f"{ip_port}")

                for org_url in organizations:
                    html = fetch_html_with_cookies(org_url, cookies)
                    if html:
                        ip_port_pairs = extract_ip_port_pairs(html, org_url)
                        #print(f"Organizzazione ({org_url}): {ip_port_pairs}")
                        # Scrivere ogni coppia IP:Port su una riga separata
                        for ip_port in ip_port_pairs:
                            #file.write(f"{ip_port}")
                            print(f"{ip_port}")
                        if is_number_greater_than_ten(html):
                            if html:
                                html = fetch_html_with_cookies(org_url+"&page=2", cookies)
                                ip_port_pairs = extract_ip_port_pairs(html, org_url+"&page=2")
                                #print(f"Organizzazione {org_url}&page=2 (Pagina2) : {ip_port_pairs}")
                                for ip_port in ip_port_pairs:
                                    #file.write(f"{ip_port}")
                                    print(f"{ip_port}")

    else:
        #print(f"Errore nella richiesta: {response.status_code}")
        #print(response.text)
        pass

if __name__ == "__main__":
    main()
