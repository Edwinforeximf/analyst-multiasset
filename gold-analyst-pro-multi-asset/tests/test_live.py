"""Smoke test live-data workflow with synthetic OHLC, no fake network or Gemini calls."""
import io
import os
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
import pytest
from fastapi.testclient import TestClient
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def fake_snapshot(instrument='EURUSD', trend=1):
    from market_feed import SYMBOLS
    import math
    frames={}
    start=1.12 if instrument=='EURUSD' else 4030.0
    step=0.00022 if instrument=='EURUSD' else 0.35
    amplitude=0.0012 if instrument=='EURUSD' else 4
    for tf in ('D1','H4','H1'):
        bars=[]
        for i in range(85):
            o=start+i*step*trend + math.sin(i/4)*amplitude
            c=o+step*trend*0.3
            bars.append({'open':o,'high':max(o,c)+amplitude*.6,'low':min(o,c)-amplitude*.6,
                         'close':c,'time':'2026-11-09 04:00:00'})
        frames[tf]=bars
    return {'instrument':instrument,'frames':frames,
            'quote':{'instrument':instrument,'provider_symbol':SYMBOLS[instrument],
                     'price':frames['H1'][-1]['close'],'asof':datetime.now(timezone.utc).isoformat(),
                     'age_seconds':20,'source':'Twelve Data','price_type':'indicative price'},
            'provider':'Twelve Data (indicative; broker prices may differ)',
            'retrieved_at':datetime.now(timezone.utc).isoformat()}


def test_quote_stale_and_mapping(monkeypatch):
    from market_feed import parse_quote, MarketDataError, mapping
    time=int(datetime.now(timezone.utc).timestamp())
    assert parse_quote({'close':'1.12345','timestamp':time},'EURUSD')['price']==1.12345
    with pytest.raises(MarketDataError):
        parse_quote({'close':'1.12345','timestamp':time-99999},'EURUSD')
    # A timezone-less last_update_at must not override a valid UNIX timestamp.
    assert parse_quote({'close':'1.12345','last_quote_at':'2026-01-01 00:00:00','timestamp':time},'EURUSD')['price'] == 1.12345
    assert mapping('USOIL')=='WTI/USD'
    monkeypatch.setenv('LIVE_SYMBOL_USOIL','TEST_CONFIGURED_OIL_SYMBOL')
    assert mapping('USOIL')=='TEST_CONFIGURED_OIL_SYMBOL'


def test_live_direction_and_render(tmp_path):
    from live_engine import analyze
    from visuals import live_source_chart, annotated_chart, infographic
    for direction, expected in ((1,'BUY'),(-1,'SELL')):
        snap=fake_snapshot(trend=direction)
        a=analyze(snap)
        assert a['decision']==expected
        assert a['market']['quote_price']==snap['quote']['price']
        assert isinstance(a['signal_validated'],bool)
        source=tmp_path/f'source_{expected}.png'
        live_source_chart(snap,a,source)
        assert len(a['chart_scale']['anchors'])==2
        watermark=tmp_path/'missing.png'
        ann=tmp_path/f'ann_{expected}.png';info=tmp_path/f'info_{expected}.png'
        annotated_chart(source,a,watermark,ann)
        infographic(a,watermark,info)
        assert ann.exists() and info.exists()
        with Image.open(info) as im: assert im.size==(1080,1440)


def test_live_end_to_end(tmp_path,monkeypatch):
    monkeypatch.setenv('STORAGE_DIR',str(tmp_path))
    monkeypatch.setenv('APP_SECRET','unit-test-live-secret-long-enough')
    monkeypatch.setenv('TWELVEDATA_API_KEY','TEST_ONLY_DUMMY')
    monkeypatch.delenv('GEMINI_API_KEY',raising=False)
    monkeypatch.setenv('COOKIE_SECURE','0')
    import importlib
    sys.modules.pop('app',None)
    service=importlib.import_module('app')
    monkeypatch.setattr(service,'fetch_snapshot',lambda instrument:fake_snapshot(instrument))
    monkeypatch.setattr(service,'fetch_quote',lambda instrument:fake_snapshot(instrument)['quote'])
    c=TestClient(service.app)
    assert c.get('/health').json()['live_feed_configured']
    assert c.post('/api/setup',json={'username':'administrator','password':'very-strong-password-0123456789'}).status_code==200
    assert c.post('/api/login',json={'username':'administrator','password':'very-strong-password-0123456789'}).status_code==200
    assert c.get('/api/market/EURUSD').json()['source']=='Twelve Data'
    resp=c.post('/api/reports/live',json={'instrument':'EURUSD'})
    assert resp.status_code==200,resp.text
    rid=resp.json()['id']
    generated=c.post(f'/api/reports/{rid}/generate')
    assert generated.status_code==200,generated.text
    a=generated.json()['report']
    assert a['decision'] in ('BUY','SELL')
    assert a['analysis_mode']=='live'
    assert a['signal_validated'] in (True,False)
    for suffix in ('docx','article','asset/annotated','asset/infographic'):
        assert c.get(f'/api/reports/{rid}/{suffix}').status_code==200
    report=c.get(f'/api/reports/{rid}').json()['report']
    assert report['mode']=='live'
    assert report['market_snapshot']
    assert c.get(f'/api/reports/{rid}/asset/h1').status_code==200
