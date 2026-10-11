"""Build the Japanese Markdown and monochrome Meiryo UI workbook from one content set."""
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import re
import sys
import unicodedata
import zipfile

import xlsxwriter
from PIL import ImageFont

from report_content import SECTIONS
import report_settings  # registers the remaining sections
import report_runtime
from report_sources import SOURCES, SOURCE_MAP
from parameter_policy import AUTO, decision, role

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'deliverables'
OUT.mkdir(exist_ok=True)
STEM = 'Aurora_GlobalDatabase_Design_Assessment_2026-10-11'
DATE = '2026-10-11'
FONT = 'Meiryo UI'
MEASURE = ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc', 14, index=2)


def read_json(name):
    return json.loads((ROOT / 'evidence' / name).read_text(encoding='utf-8'))


CLUSTER = read_json('ap-northeast-1_cluster_group.json')['Parameters']
INSTANCE = read_json('ap-northeast-1_instance_group.json')['Parameters']
OSAKA = read_json('ap-northeast-3_cluster_group.json')['Parameters']
INSTANCE_NAMES = {p['ParameterName'] for p in INSTANCE}
MYSQL = read_json('mysql84_reference_defaults.json')['parameters']
LONG_ALLOWED = {p['ParameterName']: p['AllowedValues'] for p in CLUSTER
                if len(p.get('AllowedValues', '')) > 2000}


def mysql_ref(name):
    key = name.replace('-', '_')
    found = MYSQL.get(key)
    if not found:
        return '参考値未取得。AWS実効値は実機確認', '', ''
    default = found['default'].replace('Default Value: ', '').replace('Default Value', '既定値')
    return 'Community参考: ' + default, found['scope'], found['url']


def v2_note(p):
    n = p['ParameterName']
    if p.get('MinimumEngineVersion'):
        return '8.4.7対象外。最低版=' + p['MinimumEngineVersion']
    if n in AUTO:
        return 'v2が自動調整。カスタム値を採用しない。'
    if n == 'max_connections':
        return '最大ACU変更による自動再計算は再起動で反映。カスタム値の直接変更は別条件。'
    if n == 'mysql_native_password':
        return 'ON固定。新規認証方式はauthentication_policyで指定。'
    if n == 'aurora_parallel_query':
        return 'OFF基準。現行仕様で採否を検証。古い非対応説明を流用しない。'
    if not p['IsModifiable']:
        return 'AWS管理。設定変更の対象外。'
    if p['ApplyType'] == 'static':
        return 'DB再起動が必要。新規接続で実効値を確認。'
    return 'DBはdynamic。Proxy反映には再起動要件を確認。'


def catalog(scope, params):
    definitions, policies = [], []
    for i, p in enumerate(params, 1):
        n = p['ParameterName']
        key = ('C' if scope == 'cluster' else 'I') + f'{i:03d}'
        default = p.get('ParameterValue', 'engine-default（APIは具体値を省略）')
        if default == '':
            default = '空文字（API返値）'
        reference, sql_scope, mysql_url = mysql_ref(n)
        eligibility = '8.4.7対象外' if p.get('MinimumEngineVersion') else '8.4.7候補'
        where = ('クラスタ専用' if n not in INSTANCE_NAMES else 'クラスタ既定/個別上書き可') if scope == 'cluster' else 'インスタンス上書き'
        cat, recs, reason, decision_tag, sources = decision(p)
        definitions.append([
            key, n, role(n), default, reference, where + '\n' + eligibility,
            '可' if p['IsModifiable'] else '不可',
            p.get('ApplyType', '') + '\n返値ApplyMethod=' + p.get('ApplyMethod', '未返却'),
            p.get('DataType', ''), (f'全{len(LONG_ALLOWED[n].split(","))}値を「25_長い許容値」に省略せず掲載。'
                                    if n in LONG_ALLOWED else p.get('AllowedValues', 'API未返却')),
            sql_scope or 'MySQLのSQL scope参考値なし', v2_note(p),
            ('S56' if scope == 'cluster' else 'S57') + ' / ' + sources,
        ])
        policies.append([key, n, *recs, reason, v2_note(p), decision_tag, sources])
    return definitions, policies


def add_catalogs():
    for prefix, label, scope, params in [('20','クラスタ','cluster',CLUSTER),('22','インスタンス','instance',INSTANCE)]:
        defs, recs = catalog(scope, params)
        SECTIONS.append(dict(sheet=f'{prefix}_{label}既定', title=f'{label}パラメータ全件・既定値と変更条件（{len(params)}行）',
          intro='AWS APIの生値を保持。Community参考値はAuroraの実効値を保証しない。8.4.8専用行も隠さず除外表示。全件の原データはevidenceフォルダー。',
          headers=['ID','パラメータ名','日本語での役割','AWS API既定値/式','MySQL 8.4参考既定（別物）','設定位置・8.4.7適用','変更可','反映メタデータ','型','許容値（API）','SQL Scope参考','Serverless/Proxy注意','根拠'],rows=defs))
        SECTIONS.append(dict(sheet=f'{int(prefix)+1}_{label}推奨', title=f'{label}パラメータ全件・用途別推奨（{len(params)}行）',
          intro='新規/標準設計の開始値。直接online・直接batchは比較列、実際の採用列は共用Proxy。クラスタと個別群へ矛盾する値を二重設定しない。',
          headers=['ID','パラメータ名','オンライン直結の推奨','バッチ直結の推奨','共用Proxy経由の推奨','理由・影響・適用判断','Serverless/反映時の注意','判断区分','根拠'],rows=recs))
    allowed_rows = []
    for name, allowed in LONG_ALLOWED.items():
        values = allowed.split(',')
        for start in range(0, len(values), 10):
            allowed_rows.append([name, f'{start+1}～{min(start+10,len(values))} / {len(values)}',
                                 '\n'.join(values[start:start+10]),
                                 'AWS APIの許容値を原順序で列挙。1セルの高さ上限による欠落を避けて分割。範囲外の文字列や別製品の値を追加していない。', 'S56'])
    SECTIONS.append(dict(sheet='25_長い許容値', title='長い許容値の完全一覧・原順序を保持',
                         intro='20_クラスタ既定の長い列挙値を10件ずつ表示。全行を連結すると元のAPI値に一致する。個別セルのコメントと同梱JSONにも元データを保存。',
                         headers=['パラメータ名','列挙位置 / 総数','許容値（1行1値）','読み方','根拠'], rows=allowed_rows))


def add_evidence():
    evidence_rows = []
    for x in read_json('manifest.json'):
        file = ROOT / 'evidence' / x['file']
        evidence_rows.append([x['region'],x['kind'],x['parameter_count'] or 'パラメータ一覧ではない',x['file'],x['retrieved_at_utc'],hashlib.sha256(file.read_bytes()).hexdigest()])
    SECTIONS.append(dict(sheet='91_API取得証跡',title='読み取り専用AWS API取得の証跡',
      intro='取得したのはエンジン提供情報と既定パラメータ群。実リソースの設定値やDBパスワードは取得していない。JSONを同梱し、件数とSHA-256で照合できる。',
      headers=['リージョン','取得種別','パラメータ行数','原データファイル','取得時刻 UTC','SHA-256'],rows=evidence_rows))
    differences = []
    osaka_map = {p['ParameterName']: p for p in OSAKA}
    for p in CLUSTER:
        q = osaka_map[p['ParameterName']]
        different = [f for f in set(p) | set(q) if p.get(f) != q.get(f)]
        if different:
            differences.append(p['ParameterName'])
    SECTIONS.append(dict(sheet='24_全件一覧の読み方',title='APIの全件性・既定値の解釈と未確定事項',
      intro='公式Web表だけでなく実APIを全ページ取得した。不存在・固定・対象外・自動調整・実効値未取得を区別する。',
      headers=['論点','確認結果','解釈','次に行う確認','根拠'],rows=[
        ['クラスタ件数',len(CLUSTER),'クラスタ専用131 + インスタンスと共通299 = 430','429行が8.4.7候補、うちAPI変更可369。v2の自動調整はさらに除外。','S56'],
        ['インスタンス件数',len(INSTANCE),'共通パラメータの個別上書き群','298行が8.4.7候補、うちAPI変更可250。全てが業務調整対象とは限らない。','S57'],
        ['APIで具体値あり',sum('ParameterValue' in p for p in CLUSTER),'73項目。定数に加えAWSの式/置換値も含む','値/式は改変せず既定列へ収録。','S56'],
        ['APIで具体値省略',sum('ParameterValue' not in p for p in CLUSTER),'357項目。engine-defaultの数値を想像で埋めない','MySQLの参考既定と、Aurora GLOBAL/SESSIONの実測を分離。','S20'],
        ['東京/大阪の既定値','パラメータ名・既定値・変更可否・許容値は一致','クラスタAPIのSupportedEngineModesは東京あり、大阪では欠落する等のメタデータ差がある','エンジン/注文可能APIの両地域db.serverless提供を別途確認済み。欠落を機能非対応と即断しない。','S56 S57'],
        ['8.4.8専用','aurora_transaction_timeout','最低エンジン版の記載により8.4.7対象外','JTAとバッチの業務期限で対応。8.4.8への更新は本依頼では実施しない。','S56 S57'],
        ['メタデータApplyMethod','既定群の返値はpending-rebootを含む','返値だけで全dynamic項目をstaticと分類しない','ApplyType、v2例外、Proxy再起動要件、実機ステータスを合わせて判断。','S08 S17'],
        ['実効値','未取得','本番/検証DBへの接続はしていない','examples/runtime-verification.sqlを承認された管理経路で取得し照合。','設計上の残存事項'],
        ['参考既定','MySQL 8.4の公式プロパティ表','Linux/Windowsや32/64bit別の値は原記載を保持。Auroraに該当するとは限らない','AWSの明示値がある場合はAWSが優先。自動算出・内部管理・非対応機能は数値だけで採用しない。','S53 S54 S55'],
        ['API更新','後日件数・メタデータは変化し得る','家族(family)の既定群はマイナー版専用の固定スナップショットではない','設計確定直前に同じcollectorを再実行し差分とMinimumEngineVersionを確認。','S56 S57'],
      ]))
    SECTIONS.append(dict(sheet='90_公式出典',title='公式出典一覧（参照日 2026-10-11）',
      intro='AWS・Red Hat・MySQLの一次資料。各行の根拠IDはこの一覧へリンクする。APIの証跡は91シートとevidenceに保存。',
      headers=['ID','公式資料','URL','本資料で確認した対象','参照日'],rows=[[a,b,c,d,DATE] for a,b,c,d in SOURCES]))
    SECTIONS.append(dict(sheet='16_設定例と確認手順',title='同梱の設定例・参照SQL・再生成スクリプト',
      intro='設定例は設計レビュー用。クラウドリソース変更やDBへのDDL実行は行っていない。完全なデプロイ定義ではない。',
      headers=['ファイル','目的','事前条件・読むポイント','検証の範囲','根拠'],rows=[
        ['examples/ecs-container-fragment.json','SSM起動時注入','両地域に同じパス、地域別Proxyホスト。execution role、ネットワーク、秘密供給は別定義。','JSON構文を検証。ECS起動は未実施。','S31'],
        ['examples/online-datasource.cli','JBoss JNDI設定','ドライバmodule、Elytron store、環境変数を先に用意。global JTA期限の影響範囲に注意。','資料仕様との整合を静的確認。EAP管理モデルへの適用は未実施。','S24 S25'],
        ['examples/BatchConnectionExample.java','Java直接ドライバ接続','Proxy固有FQDN、Secretsから供給する秘密ファイル、承認済みConnector/Jが必要。','JDK 17でコンパイル確認。実DBへ接続はしていない。','S27'],
        ['examples/runtime-verification.sql','実効値の採取','Writer/Reader/地域/Proxyで別々に確認する。アカウント情報の出力は機密扱い。','参照SQLのみ。未実行。','S20'],
        ['examples/partition-example.sql','月単位RANGE分割例','複合主キーが業務ID単独の一意性を保証しない点と外部キー制約を確認。','DDLは未実行。業務スキーマ用の設計例。','S42 S43'],
        ['scripts/collect_aws_evidence.py','既定値の再取得','AWS CLIの読み取り権限が必要。AWSプロファイルは実行者が選ぶ。','Describeのみ。既定群とengine metadataを取得。','S56 S57'],
        ['scripts/build_deliverables.py','同じデータからExcel/MDを生成','Python、XlsxWriter、Pillow、Meiryo UI。openpyxlは検証で使用。','1つの内容集合で両成果物を同期する。','作成処理'],
      ]))


def fmt(wb, **kwargs):
    return wb.add_format({'font_name': FONT, 'font_size': 10, 'font_color': '#242424', **kwargs})


def lines_count(value, width):
    usable = max(30, width*7-12)
    count = 0
    for line in str(value).split('\n'):
        if not line:
            count += 1
            continue
        # Measured character widths keep Japanese and long ASCII defaults visible.
        occupied, lines = 0.0, 1
        for c in line:
            advance = MEASURE.getlength(c)
            if occupied + advance > usable:
                lines += 1
                occupied = 0.0
            occupied += advance
        count += lines
    return count


def widths_for(s):
    if s['sheet']=='25_長い許容値':
        return [36,20,60,64,20]
    if s['sheet'].startswith(('20_', '22_')):
        return [9,44,36,44,45,24,10,24,12,52,22,44,20]
    if s['sheet'].startswith(('21_', '23_')):
        return [9,44,40,40,46,68,44,18,22]
    if s['sheet']=='10_タイムアウト':
        return [14,32,36,26,29,45,74,20]
    if s['sheet']=='07_Proxy設定':
        return [21,35,45,44,80,21]
    if s['sheet']=='11_Java_JNDI':
        return [20,40,45,48,78,20]
    if s['sheet']=='90_公式出典':
        return [9,58,105,65,16]
    if s['sheet']=='91_API取得証跡':
        return [22,24,20,48,38,72]
    if s['sheet']=='16_設定例と確認手順':
        return [50,35,78,64,20]
    return [27,38,76,76,22]


def make_table(wb,s):
    ws=wb.add_worksheet(s['sheet'])
    ws.hide_gridlines(2)
    ws.set_zoom(85 if len(s['headers'])<9 else 80)
    ws.set_tab_color('#777777')
    widths=widths_for(s)
    for c,w in enumerate(widths):
        ws.set_column(c,c,w)
    title=fmt(wb,bold=True,font_size=18,bg_color='#222222',font_color='#FFFFFF',valign='vcenter',text_wrap=True)
    sub=fmt(wb,font_size=10,bg_color='#E8E8E8',text_wrap=True,valign='vcenter')
    header=fmt(wb,bold=True,bg_color='#444444',font_color='#FFFFFF',text_wrap=True,valign='vcenter',border=1,border_color='#888888')
    ws.merge_range(0,0,1,len(widths)-1,s['title'],title)
    ws.set_row(0,26); ws.set_row(1,26)
    ws.merge_range(2,0,2,len(widths)-1,s['intro'],sub); ws.set_row(2,48)
    ws.set_row(3,12)
    for c,h in enumerate(s['headers']):
        ws.write_string(4,c,h,header)
    ws.set_row(4,38)
    normal = [fmt(wb,text_wrap=True,valign='top',bg_color=bg,bottom=1,bottom_color='#D0D0D0') for bg in ['#FFFFFF','#F1F1F1']]
    linked = [fmt(wb,text_wrap=True,valign='top',bg_color=bg,bottom=1,bottom_color='#D0D0D0',underline=1) for bg in ['#FFFFFF','#F1F1F1']]
    review = fmt(wb,bold=True,text_wrap=True,valign='top',bg_color='#DDDDDD',bottom=1,bottom_color='#AAAAAA')
    for ridx,row in enumerate(s['rows'],5):
        shade=(ridx-5)%2
        max_lines=max(lines_count(value,widths[c]) for c,value in enumerate(row))
        height=max(34, math.ceil(max_lines*16.5+12))
        if height>400:
            raise ValueError(f'Excel row would exceed safe height: {s["sheet"]}:{ridx+1} ({height})')
        ws.set_row(ridx,height)
        for c,value in enumerate(row):
            text=str(value)
            style=review if '対象外' in text or text=='変更不可' else normal[shade]
            if text.startswith('https://'):
                ws.write_url(ridx,c,text,linked[shade],string=text)
            elif c==len(row)-1 and (m:=re.search(r'\bS\d{2}\b',text)) and s['sheet']!='90_公式出典':
                sid=m.group()
                if sid not in SOURCE_MAP:
                    raise ValueError(f'Unknown source {sid}')
                source_row=next(i for i,x in enumerate(SOURCES,6) if x[0]==sid)
                ws.write_url(ridx,c,f"internal:'90_公式出典'!A{source_row}",linked[shade],string=text)
                ws.write_comment(ridx,c,'\n'.join(SOURCE_MAP[x][1] for x in re.findall(r'\bS\d{2}\b',text)),{'font_name':FONT,'font_size':9,'x_scale':2,'y_scale':2})
            else:
                ws.write_string(ridx,c,text,style)
        if s['sheet'].startswith(('20_','22_')):
            param=(CLUSTER if s['sheet'].startswith('20_') else INSTANCE)[ridx-5]
            ref=mysql_ref(param['ParameterName'])[2]
            if ref:
                ws.write_comment(ridx,4,ref+'\nCommunity参考値でありAurora実効値ではありません。',{'font_name':FONT,'font_size':9,'x_scale':2,'y_scale':2})
            ws.write_comment(ridx,1,'APIメタデータ: '+json.dumps(param,ensure_ascii=False),{'font_name':FONT,'font_size':9,'x_scale':3,'y_scale':4})
    ws.autofilter(4,0,4+len(s['rows']),len(widths)-1)
    ws.freeze_panes(5,2 if len(widths)>=9 else 1)
    ws.set_landscape(); ws.set_paper(8)
    ws.fit_to_pages(2 if sum(widths)>300 else 1,0)
    ws.repeat_rows(4); ws.repeat_columns(0,1 if len(widths)>=9 else 0)
    ws.set_margins(0.3,0.3,0.45,0.45)
    ws.set_header('&L&"Meiryo UI,Regular"Aurora 8.4.7 / 東京・大阪&R2026-10-11')
    ws.set_footer('&L&"Meiryo UI,Regular"公式確認と設計提案を区別&R&P / &N')
    ws.print_area(0,0,4+len(s['rows']),len(widths)-1)
    return ws


def cover(wb):
    ws=wb.add_worksheet('00_はじめに')
    ws.hide_gridlines(2); ws.set_zoom(95); ws.set_tab_color('#222222')
    ws.set_column(0,0,4); ws.set_column(1,1,31); ws.set_column(2,2,73); ws.set_column(3,3,27); ws.set_column(4,4,4)
    dark=fmt(wb,bg_color='#202020',font_color='#FFFFFF',bold=True,font_size=24,text_wrap=True,valign='vcenter')
    medium=fmt(wb,bg_color='#E5E5E5',bold=True,font_size=15,text_wrap=True,valign='vcenter')
    body=fmt(wb,text_wrap=True,valign='vcenter')
    link=fmt(wb,underline=1,text_wrap=True,valign='vcenter')
    ws.merge_range('B2:D4','Aurora Global Database\n東京・大阪 DR構成 詳細評価',dark)
    for r in range(1,4): ws.set_row(r,30)
    ws.merge_range('B6:D6','Aurora MySQL 8.4.7  |  Serverless v2  |  RDS Proxy  |  JBoss EAP 8.1',medium); ws.set_row(5,35)
    ws.merge_range('B8:D9','結論：各リージョンのProxyへ接続し、災害時はDB・コンテナ・入口・ジョブをまとめて大阪へ切り替える。\n読み取り専用AWS APIと公式資料で確認。性能・DRの実機試験は未実施。',body)
    ws.set_row(7,25);ws.set_row(8,25)
    ws.merge_range('B11:D11','430 / 299  全件一覧　　61  公式資料　　3  用途別推奨列',medium);ws.set_row(10,34)
    ws.merge_range('B13:D14','430・299は現行8.4ファミリーの全行数。8.4.8専用を各1行含むため、8.4.7候補は429・298。\n「既定値維持」は意図した推奨。未取得の実効値を数値で埋めていません。',body)
    ws.set_row(12,23);ws.set_row(13,23)
    entries=[('最初に読む','01_結論と前提','採用条件と前提、実測が必要な点'),('構成をつかむ','02_構成図','平常時 / 大阪昇格後の接続経路'),('DRを設計する','05_DR手順','判定から切り戻しまで'),('Proxyを設定する','07_Proxy設定','設定区分・API名・既定値・推奨'),('待ち時間を合わせる','10_タイムアウト','online / batch / 共用Proxyの比較'),('全パラメータを探す','20_クラスタ既定','21推奨 / 22インスタンス既定 / 23推奨'),('根拠を確認する','90_公式出典','公式リンクと91_API取得証跡')]
    for r,(name,target,desc) in enumerate(entries,16):
        ws.write(r,1,name,body);ws.write_url(r,2,f"internal:'{target}'!A1",link,string=desc);ws.write(r,3,target,body);ws.set_row(r,31)
    ws.merge_range('B25:D26','調査日：2026-10-11 / 表示：Meiryo UI・モノトーン\nフィルター、固定見出し、折返し、根拠リンク、印刷設定を付与。横長の全件表は横スクロールで参照。',body)
    ws.set_row(24,25);ws.set_row(25,25)
    ws.set_portrait();ws.set_paper(9);ws.fit_to_pages(1,1);ws.print_area('B2:D26')
    ws.set_margins(0.3,0.3,0.3,0.3)


def architecture(wb):
    ws=wb.add_worksheet('02_構成図');ws.hide_gridlines(2);ws.set_zoom(95);ws.set_tab_color('#555555')
    ws.set_column('A:P',10)
    for r in range(42):ws.set_row(r,23)
    for r in [6,12]:ws.set_row(r,26)
    title=fmt(wb,bold=True,font_size=20,bg_color='#222222',font_color='#FFFFFF',valign='vcenter')
    head=fmt(wb,bold=True,font_size=13,bg_color='#555555',font_color='#FFFFFF',align='center',valign='vcenter')
    box=fmt(wb,text_wrap=True,border=1,border_color='#555555',align='center',valign='vcenter',bg_color='#EEEEEE',font_size=11)
    white=fmt(wb,text_wrap=True,border=1,border_color='#999999',align='center',valign='vcenter',font_size=11)
    arrow=fmt(wb,bold=True,font_size=16,align='center',valign='vcenter')
    note=fmt(wb,text_wrap=True,valign='vcenter',font_size=10)
    ws.merge_range('A1:P2','地域内の接続は同じ形。書き込み役とアプリの稼働地域を切り替える。',title)
    ws.merge_range('A4:G4','東京  ap-northeast-1',head);ws.merge_range('J4:P4','大阪  ap-northeast-3',head)
    ws.merge_range('A5:G6','平常時：利用者 → 東京ALB / 入口',box);ws.merge_range('J5:P6','DR後：利用者 → 大阪ALB / 入口',box)
    ws.merge_range('A7:G7','↓',arrow);ws.merge_range('J7:P7','↓',arrow)
    ws.merge_range('A8:G10','東京コンテナ / JBoss JNDI\n東京バッチ / Connector/J\n同じアプリイメージ digest',white)
    ws.merge_range('J8:P10','大阪コンテナ / JBoss JNDI\n大阪バッチ / Connector/J\n同じアプリイメージ digest',white)
    ws.merge_range('A11:G12','起動時：東京SSM → 東京Proxyホスト\n資格情報：東京Secrets Manager',box)
    ws.merge_range('J11:P12','起動時：大阪SSM → 大阪Proxyホスト\n資格情報：大阪Secrets Manager',box)
    ws.merge_range('A13:G13','↓ TLS / TCP3306',arrow);ws.merge_range('J13:P13','↓ TLS / TCP3306',arrow)
    ws.merge_range('A14:G16','東京 RDS Proxy\n既定RW → 東京Writer\n必要時のみ追加RO → 東京Reader',white)
    ws.merge_range('J14:P16','大阪 RDS Proxy\n昇格前：ROのみ利用可 / RW失敗\n昇格後：同じRW名で大阪Writerへ',white)
    ws.merge_range('A17:G17','↓ 登録対象は東京クラスターID',note);ws.merge_range('J17:P17','↓ 登録対象は大阪クラスターID',note)
    ws.merge_range('A18:G20','Aurora Serverless v2 × 2 AZ\n平常時：Writer + Reader\n大阪昇格後：secondaryへ復帰を確認',box)
    ws.merge_range('J18:P20','Aurora Serverless v2 × 2 AZ\n平常時：Reader + Reader\nDR昇格後：Writer + Reader',box)
    ws.merge_range('A22:G24','東京の共有クラスターvolume\nリージョン内3 AZの耐久ストレージ',white)
    ws.merge_range('J22:P24','大阪の共有クラスターvolume\nリージョン内3 AZの耐久ストレージ',white)
    ws.merge_range('H22:I24','→\n非同期\n複製',arrow)
    ws.merge_range('A26:P28','Global Database：平常時は東京から大阪へストレージ層で複製。大阪昇格後は新primaryからsecondaryへ複製。\nRDS ProxyのターゲットにGlobal writer endpointや任意のDNS文字列は登録しない。\nGlobal Databaseは誤削除も複製するため、独立バックアップと復元試験が必要。',note)
    ws.merge_range('A30:P32','切替順序：東京の新規書込・ジョブを抑止 → 大阪DB昇格 → 大阪Proxy RW疎通 → 大阪アプリ準備 → 入口切替 → バッチ再開\nDBだけ先に自動切替して東京コンテナを動かし続ける設計にはしない。既存の接続やトランザクションが地域間で移動するわけではない。',note)
    ws.merge_range('A34:P36','管理経路：管理端末 → VPN / 管理ホスト等 → Proxy（通常）またはAurora直結（期限付き例外）。\napp-sg / batch-sg → proxy-sg:3306 → db-sg:3306。アプリからDBへの迂回は許可しない。\nVPC内でもTLS、本人確認、DB権限、監査を別々に設計する。',note)
    ws.merge_range('A38:P39','根拠：S04 / S05 / S08 / S15 / S31 / S35。各リージョンDB2台、最小8・最大32 ACUは負荷未確定時の設計案。',note)
    ws.set_landscape();ws.set_paper(8);ws.fit_to_pages(1,1);ws.print_area('A1:P39');ws.set_margins(0.3,0.3,0.3,0.3)


def calculator(wb):
    ws=wb.add_worksheet('15_接続数試算');ws.hide_gridlines(2);ws.set_zoom(95)
    ws.set_column('A:A',6);ws.set_column('B:B',52);ws.set_column('C:C',23);ws.set_column('D:D',86)
    title=fmt(wb,bold=True,font_size=18,bg_color='#222222',font_color='#FFFFFF',valign='vcenter')
    textf=fmt(wb,text_wrap=True,valign='vcenter')
    entry=fmt(wb,bg_color='#E2E2E2',border=1,border_color='#999999',align='right',valign='vcenter',num_format='0.0')
    calc=fmt(wb,bold=True,bg_color='#F1F1F1',border=1,border_color='#999999',text_wrap=True,valign='vcenter')
    ws.merge_range('B2:D3','接続数の試算：最悪時は多重化が効かない前提で確認する',title)
    ws.merge_range('B5:D6','灰色の入力は仮定値。実測値へ置換して使う。WriterとReaderは別々に計算する。\nこれは接続枠の必要条件であり、CPU・ロック・SQL応答時間の合格を意味しない。',textf)
    inputs=[('DB実効max_connections',3000,'最大32 ACU時の公式参考値。実機で置換。'),('Proxy MaxConnectionsPercent',80,'DBの接続上限に対する割合 [%]。'),('実測MaxDatabaseConnectionsAllowed',2300,'未実測の仮値。監視用予約等を差し引いたメトリクスで置換。'),('オンライン最大コンテナ数',30,'オートスケールの上限。'),('1コンテナの最大プール接続',20,'JNDI DataSource単位。複数DSがあれば合算。'),('新旧重複係数',2,'ローリング更新中の同時稼働。'),('バッチ接続数',8,'同時worker数×worker当たり接続数。'),('Proxy外の接続予算',50,'管理・監視・例外直結等。'),('余裕係数',1.3,'観測ピーク/保守的な上限に30%の余裕を積む。')]
    for r,(label,value,note) in enumerate(inputs,7):
        ws.write(r,1,label,textf);ws.write_number(r,2,value,entry);ws.write(r,3,note,textf);ws.set_row(r,41)
    # Inputs are C8:C16.
    results=[('Proxy配下の最大接続候補','=C11*C12*C13+C14',1208,'全接続がpinningしたときの保守的な必要数。'),('30%余裕込みの必要枠','=ROUNDUP(C19*C16,0)',1571,'接続多重化を割引として先に見込まない。'),('実測許容枠との差','=C10-C20',729,'正でも性能試験は必要。負ならプール/同時実行/ACUを再設計。'),('Proxy設定上限（概算）','=ROUNDDOWN(C8*C9/100,0)',2400,'予約接続を除く実測値とは一致しない。'),('DBに残す概算接続枠','=C8-C22-C15',550,'複数Proxyやwrite forwardingがある場合は追加控除。'),('仮の接続枠判定','=IF(AND(C21>=0,C23>=0),"枠内（性能は未検証）","要再設計")','枠内（性能は未検証）','DB CPUと実行中SQLの上限は別。')]
    for r,(label,formula,cached,note) in enumerate(results,18):
        ws.write(r,1,label,textf);ws.write_formula(r,2,formula,calc,cached);ws.write(r,3,note,textf);ws.set_row(r,46)
    ws.merge_range('B27:D29','概算費用 = 両地域・全DBのACU時間 + 保存量 + I/O + Global複製 + Proxy + 追加endpoint + backup + logs。\n単価は地域・料金方式で変わるため固定額を置かない。I/O-Optimizedの比較は同じ負荷で行う。\n出典 S07 / S17 / S52 / S60。入力セルを変えるとExcelで自動再計算。',textf)
    for cells in ['C8', 'C10:C12']:
        ws.data_validation(cells,{'validate':'integer','criteria':'>','value':0})
    ws.data_validation('C9',{'validate':'integer','criteria':'between','minimum':1,'maximum':100})
    ws.data_validation('C13',{'validate':'decimal','criteria':'>=','value':1})
    ws.data_validation('C14:C15',{'validate':'integer','criteria':'>=','value':0})
    ws.data_validation('C16',{'validate':'decimal','criteria':'>=','value':1})
    ws.set_landscape();ws.set_paper(8);ws.fit_to_pages(1,1);ws.print_area('B2:D29');ws.set_margins(0.3,0.3,0.3,0.3)


MERMAID = '''flowchart TB
  U[利用者の入口: 災害時は大阪へ切替]
  subgraph T[東京 ap-northeast-1]
    TC[コンテナ JBoss EAP / バッチ Java]
    TS[東京 Parameter Store + Secrets]
    TP[RDS Proxy RW / 必要時RO]
    TD[Aurora Serverless v2 Writer + Reader]
    TV[東京クラスター共有ストレージ]
    TS -->|起動時に設定・資格情報| TC
    TC -->|TLS TCP3306| TP
    TP -->|クラスターIDで登録| TD
    TD --- TV
  end
  subgraph O[大阪 ap-northeast-3]
    OC[コンテナ JBoss EAP / バッチ Java]
    OS[大阪 Parameter Store + Secrets]
    OP[RDS Proxy: 昇格前RO / 昇格後RW]
    OD[Aurora Serverless v2: 昇格後Writer + Reader]
    OV[大阪クラスター共有ストレージ]
    OS -->|起動時に設定・資格情報| OC
    OC -->|TLS TCP3306| OP
    OP -->|クラスターIDで登録| OD
    OD --- OV
  end
  U -->|平常時| TC
  U -.->|DR後| OC
  TV -->|平常時: 非同期ストレージ複製| OV
'''


def md_sources(text):
    return re.sub(r'\bS\d{2}\b',lambda m: f'[{m.group()}]({SOURCE_MAP[m.group()][1]})',str(text))


def md_escape(text):
    return str(text).replace('|','\\|').replace('\r','').replace('\n','<br>')


def write_markdown():
    parts=[f'# Aurora Global Database 東京・大阪 DR構成 詳細評価\n\n調査基準日：{DATE}。Aurora MySQL 8.4.7 / Serverless v2 / RDS Proxy / JBoss EAP 8.1。\n',
      '**結論：地域ごとのRDS Proxy固有エンドポイントへ接続し、地域障害時はDB・コンテナ・入口・ジョブをまとめて大阪へ切り替える方針を、条件付きで推奨する。**\n',
      '本資料の数値は初期設計案。公式仕様、API取得値、Communityの参考値、設計提案、未実測を分けて記載する。実DB接続・負荷試験・DR切替は実施していない。\n',
      '## 読み方\n\nExcelと本文・一覧の内容を共通データから生成した。全パラメータの既定一覧と用途別推奨一覧は後半。クラスタ430行、インスタンス299行に8.4.8以降専用をそれぞれ1行含む。8.4.7の候補は429/298。\n',
      '「明示上書きなし・既定列を継承」は保守的な推奨判断であり、検討漏れではない。AWS APIが値を省略する357項目のAurora実効値を創作せず、MySQLの参考値を別列に示す。\n',
      '## 構成図\n\n```mermaid\n'+MERMAID+'```\n',
      '接続はリージョン内で完結する。大阪RWは昇格前に利用できず、昇格後に利用可能になる。既存東京接続を大阪へ移す機能ではない。'+md_sources('S04 S05 S08')+'\n']
    for s in sorted(SECTIONS,key=lambda x:x['sheet']):
        if s['sheet'] in ['90_公式出典','91_API取得証跡']:
            continue
        parts.append('## '+s['title']+'\n\n'+s['intro']+'\n')
        parts.append('| '+' | '.join(s['headers'])+' |\n| '+' | '.join(['---']*len(s['headers']))+' |')
        for row in s['rows']:
            cells=[md_escape(x) for x in row]
            cells[-1]=md_sources(cells[-1])
            parts.append('| '+' | '.join(cells)+' |')
        parts.append('')
    parts.append('## 接続数の試算例\n\n仮定：最大30コンテナ×各20本×更新重複2倍＋バッチ8本＝1208本。全接続がpinningしても収容する保守的な見積もりに30%の余裕を加えると1571本。`MaxDatabaseConnectionsAllowed=2300`を仮置きすれば729本の余裕。ただしこれは実測値ではなく、CPU・メモリ・SQLレイテンシの保証ではない。Excel「15_接続数試算」で入力値を変更できる。'+md_sources('S07 S17')+'\n')
    parts.append('## 実装例（未適用）\n\n前提と制約は[設定例README](../examples/README.md)を参照。次の例をAWS/DBへ適用する操作は本作業では実施していない。\n')
    for name,language in [('ecs-container-fragment.json','json'),('online-datasource.cli','text'),('BatchConnectionExample.java','java'),('runtime-verification.sql','sql'),('partition-example.sql','sql')]:
        parts.append(f'### {name}\n\n```{language}\n'+(ROOT/'examples'/name).read_text(encoding='utf-8').rstrip()+'\n```\n')
    parts.append('## 公式出典\n\n参照日：2026-10-11。設定値は日付付きのAPIスナップショットを根拠にしている。\n')
    for sid,title,url,scope in SOURCES:
        parts.append(f'- {sid} [{title}]({url}) — {scope}')
    parts.append('\n## API証跡と再現方法\n\n[evidence manifest](../evidence/manifest.json)に取得コマンド・リージョン・UTC時刻を保存。全ページを取得したJSONと、MySQL公式参考値の出典URLを同梱した。対象は既定パラメータ群とエンジン提供情報で、ユーザーの本番構成や認証秘密は取得していない。\n')
    parts.append('```powershell\npython scripts\\collect_aws_evidence.py\npython scripts\\collect_mysql_reference.py\npython scripts\\build_deliverables.py\npython scripts\\validate_deliverables.py\n```\n')
    parts.append('## 本資料の検証範囲\n\nファイルの検証結果は[検証記録](../validation/validation_report.json)を参照。AWSの変更、DB SQL実行、JBoss適用、性能試験、DR実動作は未実施。Git管理のない作業フォルダーのためgit diff --checkは利用できず、作成ファイルの内容・末尾空白・UTF-8・リンク・Excel構造を直接検査した。\n\nExcel本体のCOM自動起動は環境内で失敗したため、Excel画面やExcelによる再計算の確認は未実施。[起動結果](../validation/excel_render_report.json)と[セル情報から作成した代替プレビュー](../validation/layout_preview_report.json)を分けて記録した。代替画像はExcelのスクリーンショットではない。\n')
    (OUT/f'{STEM}.md').write_text('\n'.join(parts).rstrip()+'\n',encoding='utf-8')


def write_workbook():
    wb=xlsxwriter.Workbook(OUT/f'{STEM}.xlsx',{'strings_to_formulas':False,'strings_to_urls':False})
    wb.formats[0].set_font_name(FONT)
    wb.set_properties({'title':'Aurora Global Database 東京・大阪 設計評価','subject':'Aurora 8.4.7 Serverless v2 RDS Proxy JBoss EAP 8.1','author':'Architecture assessment','comments':'Source-backed recommendations; runtime validation remains required.'})
    cover(wb)
    for s in sorted(SECTIONS,key=lambda x:x['sheet']):
        if s['sheet'].startswith('03_'):
            architecture(wb)
        if s['sheet'].startswith('16_'):
            calculator(wb)
        make_table(wb,s)
    wb.close()


def main():
    add_catalogs();add_evidence()
    write_markdown();write_workbook()
    (ROOT/'evidence'/'report_sections.json').write_text(json.dumps(SECTIONS,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'xlsx':str(OUT/f'{STEM}.xlsx'),'md':str(OUT/f'{STEM}.md'),'table_sections':len(SECTIONS),'table_rows':sum(len(s['rows']) for s in SECTIONS),'bytes':{p.name:p.stat().st_size for p in OUT.iterdir() if p.is_file()}},ensure_ascii=True))


if __name__=='__main__':
    main()
