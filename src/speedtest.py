import asyncio
import time
from urllib.parse import urlparse
import json

async def parse_proxy_url(proxy_url: str):
    parsed_url = urlparse(proxy_url)
    server_address = parsed_url.hostname
    server_port = int(parsed_url.port)
    return server_address, server_port

async def get_latency_for_proxy(proxy_url: str, respondents: list):
    server_address, server_port = await parse_proxy_url(proxy_url)
    print(f"Проверка задержки для {server_address}:{server_port}...")

    start_time = time.time()

    try:
        # Асинхронное создание сокет-соединения
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(server_address, server_port),
            timeout=30
        )
        writer.close()
        await writer.wait_closed()
        
        latency = int((time.time() - start_time) * 1000)
        print(f"{server_address}:{server_port} ответил за {latency} мс.")
        respondents.append({
            "proxy_url": proxy_url,
            "latency": int(latency),
            "address": server_address,
            "port": server_port
        })
    except asyncio.TimeoutError:
        print(f"{server_address}:{server_port} недоступен (тайм-аут).")
    except Exception as e:
        print(f"{server_address}:{server_port}. Ошибка при подключении: {e}")

async def check_proxies_from_file(filepath: str, respondents: list):
    with open(filepath, 'r', encoding="utf-8") as file:
        tasks = []
        for line in file:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            # Создаем асинхронную задачу для каждого прокси
            tasks.append(get_latency_for_proxy(line, respondents))
        
        # Ожидаем выполнения всех задач
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    respondents = []
    fin = ""
    fout = ""

    new_fin = input("Введите путь к входному файлу (../all-configs.txt)>> ")
    new_fout = input("Введите путь к выходному файлу (./result.json)>> ")

    if new_fin != '':
        fin = new_fin
    else:
        fin = "../all-configs.txt"
    
    if new_fout != '':
        fout = new_fout
    else:
        fout = "./result.json"

    asyncio.run(check_proxies_from_file(fin, respondents))

    with open(fout, 'w', encoding='utf-8') as file:
        json.dump({"data": respondents}, file, ensure_ascii=False, indent=2)
