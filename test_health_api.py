import httpx

r = httpx.get('http://127.0.0.1:8000/api/v1/health', timeout=10)
print(r.status_code, r.text)

r2 = httpx.get('http://127.0.0.1:8000/api/v1/alpha/dataset/summary', timeout=30)
print(r2.status_code, r2.text[:300])

r3 = httpx.get('http://127.0.0.1:8000/api/v1/alpha/hypotheses', timeout=30)
print(r3.status_code, r3.text[:300])