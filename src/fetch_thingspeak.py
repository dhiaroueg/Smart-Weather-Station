# fetch_thingspeak.py
import requests
import pandas as pd

CHANNEL_ID = "3151053"
READ_API_KEY = "JXWN0S8WWM19D5CS"  # si nécessaire
OUT_CSV = "thingspeak_data.csv"

def fetch_field(field=1, results=800):
    url = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/fields/{field}.json?results={results}"
    if READ_API_KEY:
        url += "&api_key=" + READ_API_KEY
    r = requests.get(url, timeout=15).json()
    feeds = r.get("feeds", [])
    return feeds

# On suppose field1=temp, field2=hum, field3=light
feeds1 = fetch_field(1, results=3000)
feeds2 = fetch_field(2, results=3000)
feeds3 = fetch_field(3, results=3000)

# Convertir en DataFrame en joignant par created_at
df1 = pd.DataFrame(feeds1)[["created_at","field1"]].rename(columns={"field1":"temp"})
df2 = pd.DataFrame(feeds2)[["created_at","field2"]].rename(columns={"field2":"hum"})
df3 = pd.DataFrame(feeds3)[["created_at","field3"]].rename(columns={"field3":"light"})

# merge par created_at (raises NaN si manque) ; on fera un tri/date
df = df1.merge(df2, on="created_at", how="outer").merge(df3, on="created_at", how="outer")
df = df.sort_values("created_at").reset_index(drop=True)
df.to_csv(OUT_CSV, index=False)
print("Saved", OUT_CSV)
