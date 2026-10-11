# Aurora Global Database 東京・大阪 詳細設計評価

調査基準日：2026-10-11。対象はAurora MySQL 8.4.7、Serverless v2、地域別RDS Proxy、JBoss EAP 8.1とJavaバッチです。

- [Excel版](deliverables/Aurora_GlobalDatabase_Design_Assessment_2026-10-11.xlsx)：Meiryo UI、モノトーン。構成図、既定値と用途別推奨、接続数試算、公式出典を収録。
- [Markdown版](deliverables/Aurora_GlobalDatabase_Design_Assessment_2026-10-11.md)：同じ本文・全件一覧と設定例を収録。
- [設定例の前提](examples/README.md)
- [機械的な検証記録](validation/validation_report.json)

`deliverables`、`evidence`、`examples`、`validation`の相対位置を保って解凍すると、Markdown内のローカルリンクを利用できます。

## 重要な結論

東京と大阪に個別のRDS Proxyを配置し、障害時はDB、コンテナ、利用者の入口、バッチ起動をまとめて大阪へ切り替える構成を条件付きで推奨します。Proxyの登録対象は同一リージョンのAuroraクラスターIDです。任意のWriter/Reader/Globalエンドポイント名を登録する仕組みではありません。

大阪のProxy RWエンドポイントは、secondaryの間は書込先がなく接続に失敗し、primaryへ昇格後に利用可能になります。アプリは配置地域のParameter Storeから地域のProxyホストを起動時に取得します。同じアプリイメージでも、SSM値、秘密、イメージ配布先は地域ごとに用意します。

Aurora 8.4.7では`mysql_native_password`はON固定で利用可能です。ただし新規構成は`caching_sha2_password`と検証付きTLSを推奨します。一般のCommunity MySQL 8.4の既定値と混同しないでください。

## 既定値の確実性

東京・大阪の読み取り専用AWS APIから、クラスタ430行・インスタンス299行を全取得しました。その中には8.4.8以降専用の`aurora_transaction_timeout`が各1行あり、8.4.7では対象外と明示しています。8.4.7の候補は429行・298行です。API上で変更可能でも、Serverless v2が自動調整する項目は別に区別しています。

APIはクラスタ430行中357行の具体的な値を省略します。それらは`engine-default`として表示し、MySQL公式の参考既定値とAuroraでの実効値を区別しました。実効値を創作して埋めてはいません。容量依存値・利用環境の上書き値は、実機で別途取得する必要があります。

## 検証と未実施事項

全件一覧とAPI原本の照合、東京・大阪の既定値比較、Excelのセル・フォント・色・数式・リンク、UTF-8、JSON、Python構文を検査しています。Java接続例はJDK 17でコンパイルしています。検証項目ごとの結果はJSON記録を参照してください。

Excel本体のCOM起動は環境内で失敗しました。Excel本体での表示・数式再計算は未確認です。実際のセル値と書式からPillowで確認用画像を作り、代表的なシートを目視確認しました。これはExcelのスクリーンショットではありません。

AWSリソース変更、DBへの接続、DDL実行、EAP設定の適用、負荷試験、DR切替、バックアップ復元は行っていません。RTO/RPO・ACU・プール数・時間制限の数値は初期設計案です。受入試験と未確定事項を本文に示しています。

## 再生成

Windowsネイティブ、Python 3.12、`xlsxwriter`、`openpyxl`、`Pillow`、Meiryo UIフォントを使用しました。Java例の検証にはJDK 17が必要です。AWS原本の再取得には、読み取りAPIを利用できるAWS CLI認証が必要です。認証情報は同梱していません。

```powershell
# 同梱した原本から再生成（AWS接続は不要）
python scripts\build_deliverables.py
python scripts\validate_deliverables.py
python scripts\preview_workbook.py

# 必要な場合だけ、最新の公式情報を再取得
python scripts\collect_aws_evidence.py
python scripts\collect_mysql_reference.py
```

APIファミリー一覧は将来変化します。再取得で件数・最低対応版・既定値が変わった場合は、本文と検証条件を再評価してください。`render_workbook.py`はExcel COMと`pywin32`、`pymupdf`による任意の表示検証用で、本環境では起動に成功していません。
