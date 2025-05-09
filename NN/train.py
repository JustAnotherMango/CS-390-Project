import mysql.connector
import pandas as pd
from datetime import datetime
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

# --- 0. DB CONFIG ---
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'trades_db'
}

# --- 1. LOAD RAW TRADES ---
cnx = mysql.connector.connect(**db_config)
cur = cnx.cursor(dictionary=True)
cur.execute("""
  SELECT
    id, politician,
    min_roi, avg_roi, max_roi,
    published_date, trade_date
  FROM politician_trades
""")
rows = cur.fetchall()
cur.close()
cnx.close()
df = pd.DataFrame(rows)

# --- 2. PREPROCESS PER-TRADE FIELDS ---
def parse_dt(s):
    s2 = (s or "").replace("Sept","Sep")
    try:
        return datetime.strptime(s2, "%d %b %Y")
    except:
        return pd.NaT

df['trade_dt'] = df['trade_date'].apply(parse_dt)
df['pub_dt']   = df['published_date'].apply(parse_dt)
df['holding_period_days'] = (
    (df['pub_dt'] - df['trade_dt']).dt.days
    .fillna(0).astype(int)
)
for c in ('min_roi','avg_roi','max_roi'):
    df[c] = pd.to_numeric(df[c], errors='coerce')
df['roi_missing'] = df['avg_roi'].isna().astype(int)

# Impute missing ROIs as zero
imp = SimpleImputer(strategy='constant', fill_value=0)
df[['min_roi','avg_roi','max_roi']] = imp.fit_transform(
    df[['min_roi','avg_roi','max_roi']]
)

# --- 3. AGGREGATE TO POLITICIAN LEVEL ---
agg = df.groupby('politician').agg(
    avg_roi        = ('avg_roi',      'mean'),
    std_roi        = ('avg_roi',      'std'),
    profit_rate    = ('avg_roi', lambda x: (x>0).mean()),
    trade_count    = ('id',           'count'),
    avg_hold       = ('holding_period_days','mean'),
    roi_missing_rate = ('roi_missing','mean')
).reset_index()
agg['std_roi'] = agg['std_roi'].fillna(0)
agg['label']   = (agg['avg_roi'] > 0).astype(int)

# --- 4. PREPARE FOR TRAINING ---
features = ['avg_roi','std_roi','profit_rate','trade_count','avg_hold','roi_missing_rate']
X = agg[features].values
y = agg['label'].values
pols = agg['politician'].values

X_train, X_val, y_train, y_val = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
scaler = StandardScaler().fit(X_train)
X_train = scaler.transform(X_train)
X_val   = scaler.transform(X_val)

class PoliDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.float32).unsqueeze(1)
    def __len__(self):
        return len(self.X)
    def __getitem__(self, i):
        return self.X[i], self.y[i]

train_dl = DataLoader(PoliDataset(X_train, y_train), batch_size=16, shuffle=True)
val_dl   = DataLoader(PoliDataset(X_val,   y_val),   batch_size=16)

# --- 5. MODEL ---
class MLP(nn.Module):
    def __init__(self, in_f):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_f, 32), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(32, 16),   nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(16, 1),    nn.Sigmoid()
        )
    def forward(self, x):
        return self.net(x)

model = MLP(len(features))

# --- 6. TRAIN LOOP ---
crit = nn.BCELoss()
opt  = torch.optim.Adam(model.parameters(), lr=1e-3)

for epoch in range(1, 41):
    model.train()
    total_loss = 0
    for xb, yb in train_dl:
        pred = model(xb)
        loss = crit(pred, yb)
        opt.zero_grad()
        loss.backward()
        opt.step()
        total_loss += loss.item() * len(xb)
    train_loss = total_loss / len(train_dl.dataset)

    model.eval()
    with torch.no_grad():
        vp = model(torch.tensor(X_val, dtype=torch.float32))
        val_loss = crit(vp, torch.tensor(y_val, dtype=torch.float32).unsqueeze(1))
    print(f"Epoch {epoch:2d}  train={train_loss:.4f}  val={val_loss:.4f}")

# --- 7. WRITE BACK PER-POLITICIAN ---
model.eval()
with torch.no_grad():
    scores = model(torch.tensor(scaler.transform(agg[features].values), dtype=torch.float32))\
             .squeeze().numpy()

cnx = mysql.connector.connect(**db_config)
cur = cnx.cursor()
upsert = """
  INSERT INTO politician_confidence (politician,confidence_score)
  VALUES (%s,%s)
  ON DUPLICATE KEY UPDATE confidence_score=VALUES(confidence_score)
"""
for pol, sc in zip(pols, scores):
    cur.execute(upsert, (pol, float(sc)))

cnx.commit()
cur.close()
cnx.close()

print("✅ Done: per-politician confidence scores written.")
