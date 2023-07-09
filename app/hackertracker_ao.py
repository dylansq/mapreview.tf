import requests, time

while True:
    try:
        requests.get('http://127.0.0.1:5000/ht/ht_get_all_rich_presence',timeout=0.0000000001)
    except requests.exceptions.Timeout:
        pass
    time.sleep(60)
    try:
        requests.get('http://127.0.0.1:5000/ht/ht_update_all_steam',timeout=0.0000000001)
    except requests.exceptions.Timeout:
        pass

    time.sleep(180)
