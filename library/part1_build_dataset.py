import csv
import os 
import threading
import time
import requests
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

BASE_URL = "https://data-api.binance.vision/api/v3/klines"

SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "BNBUSDT",
    "SOLUSDT",
    "XRPUSDT",
    "ADAUSDT",
    "DOGEUSDT",
    "AVAXUSDT",
    "LINKUSDT",
    "DOTUSDT"
]

INTERVAL = "1h"
LIMIT = 1000

DATA_DIR = 'data/clean'
RESULTS_DIR = 'results'

CSV_FILE = os.path.join(DATA_DIR, "clean_market_data.csv")
LOG_FILE = os.path.join(RESULTS_DIR, "api_download.log")
BENCHMARK_FILE = os.path.join(RESULTS_DIR, "runtime_comparison.csv")

MAX_CONCURRENT_REQUESTS = 5
REQUESTS_PER_MIN = 100

semaphore = threading.Semaphore(MAX_CONCURRENT_REQUESTS)
log_lock = threading.Lock()
rate_lock = threading.Lock()

request_times = deque()
rate_wait_events = 0

# FUnctions ----------------------------------------------------------------

def create_folders():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(RESULTS_DIR, exist_ok=True)
    print("Created filders: data/clean, results")

def timestamp():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def log(message):
    with log_lock:
        with open(LOG_FILE, "a", encoding = "utf-8") as f:
            f.write(f"{timestamp()} | {message}\n")

def wait_for_rate_limit():
    #100 req per min max

    global rate_wait_events

    with rate_lock:
        while True:
            now = time.time()
            while request_times and now - request_times[0] >60:
                request_times.popleft()

            if len(request_times) < REQUESTS_PER_MIN:
                request_times.append(now)
                return
            wait_time = 60 - (now - request_times[0])
            rate_wait_events += 1
            log(f"Rate Limit Wait Seconds = {wait_time:.2f}")
            time.sleep(wait_time)

def covert_timestamp(ms):
    return datetime.fromtimestamp( ms / 1000, tz = timezone.utc).isoformat

#API--------------------------------------------------------------------------------

def download_symbol(symbol):
    with semaphore:
        wait_for_rate_limit()

        log(
            f"Start request symbol = {symbol}"
            f"interval = {INTERVAL} limit = {LIMIT}"
    
        )

        params = {
            "symbol": symbol,
            "interval": INTERVAL,
            "limit": LIMIT,
        }

        response =  requests.get(BASE_URL, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()

        rows = []

        for record in data:
            rows.append({
                "symbol": symbol,
                "interval": INTERVAL,
                "open_time": covert_timestamp(record[0]),
                "open": record[1],
                "high": record[2],
                "low": record[3],
                "close": record[4],
                "volume": record[5],
                "close_time": covert_timestamp(record[6]),
                "quote_volume": record[7],
                "trade_count": record[8],
                "taker_by_base_volume": record[9],
                "taker_buy_quote_volume": record[10],
            })

        log(f"End request symbol = {symbol} records = {len(rows)}")

        print(f"Downloaded {symbol}: {len(rows)} records")
        return rows

#CSV---------------------------------------------------------------------------

def save_csv(rows):

    fieldnames = [
        "symbol",
        "interval",
        "open_time",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "close_time",
        "quote_volume",
        "trade_count",
        "taker_by_base_volume",
        "taker_buy_quote_volume",
    ]

    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    log(f"Wrote csv = {CSV_FILE} records = {len(rows)}")

#Benchmark----------------------------------------------------------------

def serial_download():

    all_rows=[]

    start = time.perf_counter()

    for symbol in SYMBOLS:
        all_rows.extend(download_symbol(symbol))

    elapsed = time.perf_counter() - start

    return elapsed, all_rows

def threaded_download():

    all_rows = []

    start =  time.perf_counter()

    with ThreadPoolExecutor(max_workers = MAX_CONCURRENT_REQUESTS) as executor:
        futures = {
            executor.submit(download_symbol, s): s
            for s in SYMBOLS
        }

        for future in as_completed(futures):
            all_rows.extend(future.result())

    elapsed = time.perf_counter() - start
    return elapsed, all_rows

def save_benchmark(serial_time, threaded_time, serial_records, threaded_records):
    with open(BENCHMARK_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        writer.writerow([
            "method",
            "seconds",
            "records",
            "note"
        ])

        writer.writerow([
            "serial",
            f"{serial_time:.4f}",
            serial_records,
            "downloaded one symbol at a time"
        ])

        writer.writerow([
            "multithreading",
            f"{threaded_time:.4f}",
            threaded_records,
            "downloaded several symbols simutaniously"
        ])

#Main-------------------------------------------------------------------------------------

def main():
    create_folders()

    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)

    print()
    print(f"Symbols configured: {len(SYMBOLS)}")
    print(f"Interval: {INTERVAL}")
    print(f"Limit per symbol: {LIMIT}")
    print(f"Expected records: {len(SYMBOLS)*LIMIT}")
    print()

    print("Running serial benchmark\n")

    serial_time, _ = serial_download()

    print("Running multithreaded benchmark\n")

    threaded_time, rows = threaded_download()

    save_csv(rows)

    save_benchmark( serial_time, threaded_time, len(SYMBOLS)*LIMIT, len(rows))

    print(f"\nSaved: {CSV_FILE}")
    print(f"Total records saved: {len(rows)}")

    if len(rows) == len(SYMBOLS) * LIMIT:
        print("record count check: passed")
    else:
        print("record count check: failed")


    print("\nRuntime comparison\n")
    print(f"Serial: {serial_time:.4f} seconds\n")
    print(f"Multithreading: {threaded_time:.4f} seconds\n")
    print(f"Saved: {BENCHMARK_FILE} ")

    print(f"\n Rate limit wait events logged: {rate_wait_events}\n")
    print("Script completed successfullt")

if __name__ == "__main__":
    main()

    

