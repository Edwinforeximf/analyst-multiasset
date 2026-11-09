import io
import os
import sys
import tempfile
from pathlib import Path

import pytest
from PIL import Image, ImageDraw
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def chart_png():
    im=Image.new('RGB',(600,750),'#080f27')
    d=ImageDraw.Draw(im)
    for i in range(15):
        d.line((10,100+i*35,530,100+i*35), fill='#263d56',width=1)
    for i in range(20):
        x=20+i*26
        cy=380+int(90*__import__('math').sin(i/2.5))
        d.line((x,cy-50,x,cy+50),fill='#90bce1',width=2)
        d.rectangle((x-6,cy-22,x+6,cy+22),fill='#45d8a1' if i%2 else '#fc7d81')
    for i,value in enumerate(range(4100,3970,-20)):
        d.text((535,100+i*71),str(value),fill='white')
    b=io.BytesIO();im.save(b,format='PNG');return b.getvalue()


FAKE = {
 'instrument':'XAUUSD','observed_instrument':'XAUUSD.m','title':'XAUUSD Swing Outlook',
 'asof':'2026-11-09T03:00:00Z','decision':'BUY','directional_bias':'BUY',
 'summary':'Harga mendekati area demand pada H1; tunggu retest untuk skenario pullback. Ini bukan kuotasi live.',
 'bias':'Skenario bullish teknikal berdasarkan H1.',
 'market_data_macro':'Fundamental belum diverifikasi.', 'the_trap':'Waspada breakout palsu di resistance.',
 'confluence_check':'H1 retest, D1 dan H4 perlu validasi.', 'execution_plan':'BUY LIMIT jika syarat terpenuhi.',
 'disclaimer':'Bukan harga real-time dan bukan jaminan keuntungan.',
 'evidence':['Chart H1 menampilkan resistance dan candle bullish'], 'warnings':[],
 'trade':{'entry_low':4020.0,'entry_high':4030.0,'stop_loss':3995.0,'tp1':4070.0,'tp2':4100.0,'tp3':4140.0,'rationale':'Entry di demand terdekat berdasarkan screenshot.'},
 'chart_scale':{'anchors':[{'price':4140,'y_ratio':.10},{'price':4000,'y_ratio':.85}],
  'chart_bounds':{'left_x_ratio':.03,'right_x_ratio':.90}}
}


def test_validity_guard():
    from ai_engine import normalize_analysis
    a=normalize_analysis(FAKE,'XAUUSD')
    assert a['decision']=='BUY'
    assert a['signal_validated']
    assert a['trade']['rr_tp1']>1
    b=dict(FAKE,observed_instrument='EURUSD')
    assert normalize_analysis(b,'XAUUSD')['decision']=='WAIT'
    c=dict(FAKE, trade=dict(FAKE['trade'],stop_loss=4055))
    assert normalize_analysis(c,'XAUUSD')['decision']=='WAIT'
    assert set(['XAUUSD','XAGUSD','EURUSD','GBPUSD','USDJPY','USOIL']) == set(__import__('ai_engine').INSTRUMENTS)


def test_full_flow(tmp_path,monkeypatch):
    monkeypatch.setenv('STORAGE_DIR',str(tmp_path))
    monkeypatch.setenv('APP_SECRET','integration-test-long-secret-not-for-production')
    monkeypatch.setenv('GEMINI_API_KEY','TEST_ONLY_MOCKED')
    monkeypatch.setenv('COOKIE_SECURE','0')
    import importlib
    if 'app' in sys.modules:
        del sys.modules['app']
    service=importlib.import_module('app')
    monkeypatch.setattr(service,'generate_analysis',lambda sym, files:FAKE)
    client=TestClient(service.app)
    assert client.get('/health').json()['status']=='ok'
    assert client.get('/api/setup').json()['needs_setup']
    assert client.post('/api/setup',json={'username':'administrator','password':'strong-password-0123456789'}).status_code==200
    assert client.post('/api/login',json={'username':'administrator','password':'strong-password-0123456789'}).status_code==200
    token=client.cookies.get('session')
    assert token
    img=chart_png()
    assert client.post('/api/watermark', files={'watermark':('watermark.png',img,'image/png')}).status_code==200
    result=client.post('/api/reports',data={'instrument':'XAUUSD'},files={
     'd1':('d1.png',img,'image/png'),'h4':('h4.png',img,'image/png'),'h1':('h1.png',img,'image/png')})
    assert result.status_code==200, result.text
    rid=result.json()['id']
    res=client.post(f'/api/reports/{rid}/generate')
    assert res.status_code==200,res.text
    assert res.json()['report']['signal_validated'] is True
    chart=client.get(f'/api/reports/{rid}/asset/annotated')
    info=client.get(f'/api/reports/{rid}/asset/infographic')
    doc=client.get(f'/api/reports/{rid}/docx')
    assert chart.status_code==info.status_code==doc.status_code==200
    assert doc.content[:2]==b'PK'
    from docx import Document
    word=Document(io.BytesIO(doc.content))
    assert len(word.inline_shapes)==2
    assert any('SENTIMEN TEKNIKAL' in p.text for p in word.paragraphs)
    assert len(word.tables)>=1
    assert info.content[:4]==b'\x89PNG'
    with Image.open(io.BytesIO(info.content)) as image:
        assert image.size==(1080,1440)
    assert client.get(f'/api/reports/{rid}/article').status_code==200
    assert client.post(f'/api/reports/{rid}/submit').status_code==200
    assert client.post(f'/api/reports/{rid}/review',json={'action':'approve','feedback':''}).json()['status']=='approved'
    assert client.get(f'/api/reports/{rid}').json()['report']['status']=='approved'
    assert client.get('/api/reports').json()['reports'][0]['instrument']=='XAUUSD'
    assert client.post('/api/reports',data={'instrument':'NOT_A_PAIR'},files={
       'd1':('d1.png',img,'image/png'),'h4':('h4.png',img,'image/png'),'h1':('h1.png',img,'image/png')}).status_code==400
