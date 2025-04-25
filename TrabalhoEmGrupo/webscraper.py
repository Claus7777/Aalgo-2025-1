import requests
import time
import re
from sys import exit
from lxml import html
from datetime import datetime
from getpass import getpass  # Importa o módulo para entrada de senha oculta

def log_action(user_name, action):
    with open("user_actions.log", "a") as log_file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(f"[{timestamp}] {user_name}: {action}\n")

# Função para autenticação do usuário
def authenticate_user():
    while True:
        user_name = input("Digite seu nome: ").strip()
        if len(user_name) >= 3 and user_name.replace(" ", "").isalpha():
            break
        print("Nome inválido. Por favor, insira um nome com pelo menos 3 caracteres alfabéticos.")
    
    password = getpass("Digite sua senha: ").strip()
    if len(password) < 6:
        print("Senha inválida. A senha deve ter pelo menos 6 caracteres.")
        return authenticate_user()
    
    log_action(user_name, "Usuário autenticado com sucesso.")
    return user_name

def get_element_xpath(element):
    path = []
    while element is not None and element.tag != 'html':
        parent = element.getparent()
        if parent is None:
            break
        siblings = parent.findall(element.tag)
        if len(siblings) > 1:
            index = siblings.index(element) + 1
            path.append(f"{element.tag}[{index}]")
        else:
            path.append(element.tag)
        element = parent
    path.reverse()
    return '/' + '/'.join(path)

def fetch_numbers_with_xpath(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        doc = html.fromstring(response.text)
        for tag in doc.xpath('//script | //style | //noscript | //meta | //link | //head'):
            tag.getparent().remove(tag)
        
        numbers_with_xpath = []

        # Extrai só os elementos de texto da página
        for element in doc.xpath('//*[text()]'):
            text = element.text_content().strip()
            if text:
                element_numbers = re.findall(r'\d[\d,.]*', text)
                if element_numbers:
                    xpath = get_element_xpath(element)
                    for num in element_numbers:
                        numbers_with_xpath.append((num, xpath))
        return numbers_with_xpath
    except requests.exceptions.RequestException as e:
        print(f"Erro acessando URL: {e}")
        return None

def scrape_url(user_name, url, time_to_wait, number_to_monitor=None):
    log_action(user_name, f"Iniciando monitoramento da URL: {url}")
    # Fetch inicial
    initial_data = fetch_numbers_with_xpath(url)
    if not initial_data:
        log_action(user_name, "Erro ao buscar dados iniciais. Encerrando.")
        exit(1)
    initial_numbers = [item[0] for item in initial_data]
    log_action(user_name, f"Números encontrados na página: {initial_numbers}")
    print(f"Números encontrados na página: {initial_numbers}")

    if number_to_monitor is not None:
        log_action(user_name, f"Monitorando número especificado: {number_to_monitor}")
        for i, (num, xpath) in enumerate(initial_data):
            if num == number_to_monitor:
                log_action(user_name, f"Número '{number_to_monitor}' encontrado no índice {i} com XPath: {xpath}")
                target_xpath = xpath
                last_value = num
                try:
                    while True:
                        time.sleep(time_to_wait)
                        current_data = fetch_numbers_with_xpath(url)
                        if current_data is None:
                            continue
                        current_numbers = [item[0] for item in current_data]
                        if len(current_numbers) <= i:
                            log_action(user_name, f"Erro: Número no índice {i} não existe mais na página. Encerrando.")
                            print(f"Erro: Número no índice {i} não existe mais na página. Saindo.")
                            break
                        current_value = current_numbers[i]
                        if current_value != last_value:
                            log_action(user_name, f"Mudança detectada no número especificado: {last_value} -> {current_value}")
                            print(f"Mudança detectada no número especificado: {last_value} -> {current_value}")
                            last_value = current_value
                except KeyboardInterrupt:
                    log_action(user_name, "Monitoramento interrompido pelo usuário.")
                    print("\nMonitoramento interrompido por usuário.")
                return
        log_action(user_name, f"Número especificado '{number_to_monitor}' não encontrado na página. Encerrando.")
        print(f"Número especificado '{number_to_monitor}' não encontrado na página. Saindo")
        exit(0)

    time.sleep(time_to_wait)

    # Segundo fetch
    second_data = fetch_numbers_with_xpath(url)
    if not second_data:
        log_action(user_name, "Erro ao buscar dados na segunda tentativa. Encerrando.")
        exit(1)
    second_numbers = [item[0] for item in second_data]
    log_action(user_name, f"Números encontrados na página pela segunda vez: {second_numbers}")
    print(f"Números encontrados na página pela segunda vez: {second_numbers}")

    changed_index = None
    target_xpath = None
    for i in range(min(len(initial_numbers), len(second_numbers))):
        if initial_numbers[i] != second_numbers[i]:
            changed_index = i
            target_xpath = second_data[i][1]
            log_action(user_name, f"Primeira mudança detectada no índice {i}: {initial_numbers[i]} -> {second_numbers[i]}")
            print(f"Primeira mudança detectada no índice {i}: {initial_numbers[i]} -> {second_numbers[i]}")
            print(f"XPath do número: {target_xpath}")
            break

    if changed_index is None:
        log_action(user_name, f"Nenhum número mudou depois de {time_to_wait} segundos. Encerrando.")
        print(f"Nenhum número mudou depois de {time_to_wait} segundos. Saindo.")
        exit(0)

    log_action(user_name, f"Monitorando número no XPath: {target_xpath}")
    print(f"Monitorando número no XPath: {target_xpath}")
    last_value = second_numbers[changed_index]
    try:
        while True:
            time.sleep(30)
            current_numbers = fetch_numbers_with_xpath(url)
            if current_numbers is None:
                continue
            if len(current_numbers) <= changed_index:
                log_action(user_name, f"Erro: Número no índice {changed_index} não existe mais na página. Encerrando.")
                print(f"Erro: Número no índice {changed_index} não existe mais na página. Saindo.")
                break
            current_value = current_numbers[changed_index]
            if current_value != last_value:
                log_action(user_name, f"Mudança detectada: {last_value} -> {current_value}")
                print(f"Mudança detectada: {last_value} -> {current_value}")
                last_value = current_value
    except KeyboardInterrupt:
        log_action(user_name, "Monitoramento interrompido pelo usuário.")
        print("\nMonitoramento interrompido por usuário.")

# Autenticação do usuário
user_name = authenticate_user()

url = input("Escreva URL para monitorar: ")
log_action(user_name, f"URL fornecida: {url}")

time_to_wait = int(input("Escreva quantos segundos você quer que seja o intervalo entre chegagens: "))
log_action(user_name, f"Intervalo de espera definido: {time_to_wait} segundos")

selector = input("Você quer escolher um número ou quer monitorar o primeiro número da página que mudar? Tecle 1 para digitar um número ou 2 para monitorar o primeiro que aparecer: ")
log_action(user_name, f"Opção selecionada: {selector}")

if selector == '1':
    numero_para_investigar = input("Digite o número que você quer monitorar: ")
    log_action(user_name, f"Número para monitorar: {numero_para_investigar}")
    scrape_url(user_name, url, time_to_wait, numero_para_investigar)
else:
    scrape_url(user_name, url, time_to_wait)