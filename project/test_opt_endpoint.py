from fastapi.testclient import TestClient
from app.main import app

c = TestClient(app)
r = c.post('/api/v1/alpha/optimize', json={'sample_rows': 2000, 'n_splits': 3})
print('status:', r.status_code)
if r.status_code == 200:
    j = r.json()
    print('rows:', j['dataset_rows'], 'n_hypotheses:', j['n_hypotheses'])
    for x in j['results'][:2]:
        name = x['hypothesis']
        oos = x['mean_oos_sharpe']
        stab = x['stability']
        nfolds = x['n_folds']
        print(f"  {name:25s} OOS={oos:6.3f} stab={stab:.2f} folds={nfolds}")
else:
    print(r.text[:500])