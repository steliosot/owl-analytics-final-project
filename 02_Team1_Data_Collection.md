# Team 1: Data Collection

Team lead: **Elena**

Elena gives you your first task:

> "We need a reliable script that downloads market data. The API is public, but please do not send too many requests at the same time. Also, I want a proper log file because we need to know what happened if something fails."

Create:

```txt
part1_build_dataset.py
```

Your script must create:

```txt
data/clean/clean_market_data.csv
results/api_download.log
results/runtime_comparison.csv
```

Your script should create the `data/clean/` and `results/` folders automatically if they do not already exist.

## Requirements

Team 1 is worth **25 marks**.

Your script must complete these tasks:

1. Use the correct API settings. Download data for exactly these symbols: `BTCUSDT`, `ETHUSDT`, `BNBUSDT`, `SOLUSDT`, `XRPUSDT`, `ADAUSDT`, `DOGEUSDT`, `AVAXUSDT`, `LINKUSDT`, and `DOTUSDT`. Use `interval=1h` and `limit=1000` for each symbol. **4 marks**

2. Create one combined CSV dataset with exactly 10,000 records. Save it as `data/clean/clean_market_data.csv`, print the number of records saved, and check that the final dataset has 10,000 records. Your script should create the required folders automatically if they do not already exist. **4 marks**

3. Use multithreading to download API data. Your code should show that multiple API downloads can be started without waiting for each symbol to finish one by one. **4 marks**

4. Control the API request rate. Use a synchronization method to limit how many API requests can run at the same time, and limit the downloader to a maximum of 100 API requests per minute. If the downloader has to wait because of the request-per-minute limit, log that wait. **3 marks**

5. Write a reliable log file. Use a lock so that only one thread writes to the log file at a time. Log when each request starts, when each request finishes, how many records were received for each symbol, and when the final CSV is written. **4 marks**

6. Add a benchmark that compares serial API downloading with multithreaded API downloading. The benchmark must compare the download step only and save the result as `results/runtime_comparison.csv`. **4 marks**

7. Keep the script clear and easy to run. Use clear terminal output, sensible file paths, and readable code structure. **2 marks**

## Multithreading benchmark

Elena also asks:

> "Before you move to the next team, compare serial API downloading with multithreaded API downloading. I want you to understand when threads help and when thread overhead makes them slower."

Add a small benchmark that compares:

1. serial API downloading
2. multithreaded API downloading with `ThreadPoolExecutor`

Use `time.perf_counter()`.

This benchmark should compare the download step only. Do not add price calculations or analytics in Team 1; those belong to Team 2 and Team 3.

## Example outputs

Your exact numbers will be different because market data changes, but your output should have this shape.

Example terminal output:

```txt
Starting download for 10 symbols...
Downloaded BTCUSDT: 1000 records
Downloaded ETHUSDT: 1000 records
Downloaded BNBUSDT: 1000 records
Downloaded SOLUSDT: 1000 records
Downloaded XRPUSDT: 1000 records
Downloaded ADAUSDT: 1000 records
Downloaded DOGEUSDT: 1000 records
Downloaded AVAXUSDT: 1000 records
Downloaded LINKUSDT: 1000 records
Downloaded DOTUSDT: 1000 records

Saved clean_market_data.csv
Total records saved: 10000

Runtime comparison
serial_seconds: 105.1999
multithreading_seconds: 49.2628
Fastest method: multithreading
```

Example log file lines:

```txt
2026-06-07T09:11:44Z | START request symbol=BTCUSDT interval=1h limit=1000
2026-06-07T09:11:50Z | END request symbol=BTCUSDT records=1000
2026-06-07T09:11:50Z | START request symbol=ETHUSDT interval=1h limit=1000
2026-06-07T09:11:56Z | END request symbol=ETHUSDT records=1000
2026-06-07T09:12:25Z | WROTE csv=data/clean/clean_market_data.csv records=10000
```

Example `results/runtime_comparison.csv`:

| method | seconds | records | note |
| --- | ---: | ---: | --- |
| serial | 105.1999 | 10000 | downloaded the ten symbols one after another |
| multithreading | 49.2628 | 10000 | downloaded several symbols at the same time |
