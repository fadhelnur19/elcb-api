# Smart ELCB - API penerima data (Tahap 1: terima + tampilkan, belum ada database)
# Deploy di Render (server gratis). Render otomatis kasih PORT lewat env var.

import os
from datetime import datetime

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

# API key dibaca dari Environment Variable di Render (JANGAN ditulis di sini).
# Di dashboard Render: Environment -> Add -> Key: API_KEY, Value: (kunci acak kamu)
# Bikin kunci: buka https://www.random.org/strings/ atau ketik acak panjang sendiri.
API_KEY = os.environ.get("API_KEY", "kunci-belum-diset")

app = FastAPI(title="Smart ELCB API")


class Reading(BaseModel):
    voltage: float      # V
    current: float      # A
    power: float        # W
    frequency: float    # Hz
    pf: float
    energy: float       # kWh
    leakage: float      # mA
    status: str         # NORMAL / WARNING / DANGER / MANUAL_TRIP / OVERCURRENT / SELF_TEST


# Penyimpanan sementara di memori - cukup buat verifikasi tahap 1.
# Tahap 3 nanti ini diganti InfluxDB.
last_reading: dict | None = None
last_received_at: str | None = None
total_received: int = 0


@app.post("/api/data")
def receive_data(r: Reading, x_api_key: str | None = Header(default=None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API key salah/kosong")

    global last_reading, last_received_at, total_received
    last_reading = r.model_dump()
    last_received_at = datetime.now().isoformat(timespec="seconds")
    total_received += 1

    # Muncul di Render Logs - bukti data masuk
    print(f"[{last_received_at}] #{total_received} {r.status} "
          f"V={r.voltage} I={r.current} P={r.power} bocor={r.leakage}mA kWh={r.energy}")

    return {"ok": True, "count": total_received}


@app.get("/api/latest")
def latest():
    # Sengaja tanpa API key biar gampang dicek dari browser HP/laptop
    return {"data": last_reading, "received_at": last_received_at, "total": total_received}


@app.get("/")
def root():
    return {"service": "Smart ELCB API", "status": "hidup", "total_diterima": total_received}
