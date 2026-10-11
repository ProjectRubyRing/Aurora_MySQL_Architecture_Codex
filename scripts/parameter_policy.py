"""Conservative, workload-specific decisions for every parameter returned by AWS."""
ROLES_TEXT = '''
activate_all_roles_on_login|ログイン時に付与済みロールを一括有効化するか
allow-suspicious-udfs|安全性に疑義のあるユーザー定義関数のロード
aurora_binlog_replication_max_yield_seconds|binlog複製の処理を他処理へ譲る間隔
aurora_binlog_replication_sec_index_parallel_workers|binlog適用時の二次索引更新の並列数
aurora_enable_memory_management|メモリ圧迫時のAurora自動回復制御
aurora_enable_staggered_replica_restart|Readerの段階的再起動に関する互換設定
aurora_enable_validate_password_component|新しいパスワード検証componentの有効化
aurora_enhanced_binlog|強化binlog方式の利用
aurora_full_double_precision_in_json|JSONの浮動小数点を高い精度で解析
aurora_fwd_writer_idle_timeout|write forwardingでWriterに保持する無通信接続の期限
aurora_fwd_writer_max_connections_pct|write forwardingがWriterで使える接続割合
aurora_in_memory_relaylog|binlog受信ログのメモリ処理
aurora_jemalloc_background_thread|メモリ管理処理の背景スレッド
aurora_jemalloc_dirty_decay_ms|解放済みメモリを再利用する保持時間
aurora_jemalloc_tcache_enabled|小さいメモリ割当のスレッドキャッシュ
aurora_lambda_request_timeout|DBからLambdaを呼ぶ際の待ち期限
aurora_ml_inference_timeout|機械学習推論の呼出し待ち期限
aurora_oom_response|メモリ不足時の回復動作（自動管理有効時は無視）
aurora_parallel_query|ストレージ側へ分析処理を分担するParallel Query
aurora_read_replica_read_committed|Reader固有のREAD COMMITTED最適化
aurora_replica_read_consistency|write forwarding利用時の読み取り整合性
aurora_tmptable_enable_per_table_limit|内部一時表ごとのサイズ上限制御
aurora_transaction_timeout|トランザクション全体の期限（8.4.8以降）
aurora_use_vector_instructions|対応するCPU命令による処理高速化
authentication_policy|新規ユーザーの既定認証方式
auto_increment_increment|AUTO_INCREMENTの増分
auto_increment_offset|AUTO_INCREMENTの開始オフセット
autocommit|SQLごとの自動コミット
automatic_sp_privileges|ストアド作成者へ自動付与する権限
back_log|接続要求の受付待ちキュー
basedir|AWS管理のエンジン配置ディレクトリ
binlog-do-db|binlogに含めるDBの選択
binlog-ignore-db|binlogから除外するDBの選択
binlog_backup|binlogのバックアップとの連携
binlog_cache_size|トランザクション用binlogメモリバッファ
binlog_checksum|binlogの破損検知チェックサム
binlog_error_action|binlog書込エラー時の動作
binlog_format|binlogの有効化とイベント形式
binlog_group_commit_sync_delay|グループコミット同期の待ち時間
binlog_group_commit_sync_no_delay_count|グループコミット待ちを打ち切る件数
binlog_max_flush_queue_time|binlogフラッシュ待ちキューの時間
binlog_order_commits|binlog順とトランザクション確定順の一致
binlog_replication_globaldb|binlogとGlobal Databaseの連携
binlog_row_image|binlogへ記録する変更行の列範囲
binlog_row_metadata|binlogに含む行のメタデータ
binlog_row_value_options|binlogの部分的な値の記録方式
binlog_rows_query_log_events|元SQLをbinlogへ含めるか
binlog_stmt_cache_size|非トランザクション系binlogのキャッシュ
binlog_transaction_compression|binlogトランザクションの圧縮
binlog_transaction_compression_level_zstd|binlogのZstandard圧縮レベル
binlog_transaction_dependency_history_size|並列複製用の変更行依存履歴の大きさ
bulk_insert_buffer_size|MyISAM一括挿入用バッファ（業務InnoDBでは調整不要）
character_set_client|クライアントSQLを解釈する文字集合
character_set_connection|SQL処理時の接続文字集合
character_set_database|選択DBの既定文字集合
character_set_filesystem|ファイル名解釈の文字集合
character_set_results|結果セットの文字集合
character_set_server|新規DBの既定文字集合
check_proxy_users|MySQL PROXY権限の確認（RDS Proxyとは別概念）
collation_connection|接続内の文字列比較規則
collation_server|新規DBの既定照合順序
completion_type|COMMIT/ROLLBACK後の接続・次トランザクション動作
concurrent_insert|MyISAMの同時挿入
connect_timeout|初回DBハンドシェイクを待つ秒数
core-file|障害時のcoreファイル生成
cte_max_recursion_depth|再帰CTEの深さ上限
datadir|AWS管理のデータディレクトリ
default_password_lifetime|パスワードの自動有効期限
default_storage_engine|既定ストレージエンジン
default_time_zone|起動時の既定タイムゾーン
default_tmp_storage_engine|ユーザー作成一時表の既定エンジン
default_week_format|週番号計算の規則
delay_key_write|MyISAM索引の遅延書込
delayed_insert_limit|旧式遅延挿入の処理件数
delayed_insert_timeout|旧式遅延挿入スレッドの期限
delayed_queue_size|旧式遅延挿入の待ち行列
disconnect_on_expired_password|期限切れパスワード時の切断動作
div_precision_increment|除算の小数精度の増分
end_markers_in_json|JSON形式診断出力の終端マーカー
enforce_gtid_consistency|GTIDと矛盾するSQLの抑止
eq_range_index_dive_limit|等価範囲条件の索引見積もり方式
event_scheduler|DB内部の定時イベント実行
explain_format|EXPLAINの既定出力形式
explicit_defaults_for_timestamp|TIMESTAMPの暗黙挙動を抑止
flush|表変更ごとの強制フラッシュ
flush_time|表の定期フラッシュ間隔
ft_boolean_syntax|旧式全文検索の演算子定義
ft_max_word_len|MyISAM全文索引の最大語長
ft_min_word_len|MyISAM全文索引の最小語長
ft_query_expansion_limit|全文検索のクエリ拡張件数
ft_stopword_file|全文検索の除外語ファイル
general_log|全SQLログの出力
general_log_file|全SQLログの管理パス
generated_random_password_length|DBが生成するランダムパスワードの長さ
group_concat_max_len|GROUP_CONCATの結果長上限
gtid-mode|binlogレプリケーションのGTIDモード
gtid_executed_compression_period|実行済みGTID履歴の圧縮間隔
gtid_purged|削除済みbinlogに属するGTID集合
histogram_generation_max_mem_size|ヒストグラム作成時のメモリ上限
host_cache_size|接続元ホスト情報のキャッシュ
information_schema_stats_expiry|表統計のキャッシュ有効秒数
init_connect|新しいDB接続の初期化SQL
innodb_adaptive_flushing|汚れたページの自動フラッシュ調整
innodb_adaptive_hash_index|適応型ハッシュ索引
innodb_adaptive_hash_index_parts|適応型ハッシュ索引の分割数
innodb_adaptive_max_sleep_delay|InnoDBスレッドの自動待機上限
innodb_aurora_instant_alter_column_allowed|列変更時のINSTANTアルゴリズム許可
innodb_aurora_max_partitions_for_range|範囲検索でのパーティション最適化制御
innodb_autoextend_increment|内部領域の自動拡張単位
innodb_autoinc_lock_mode|自動採番のロック方式
innodb_buffer_pool_size|データページキャッシュのサイズ
innodb_buffer_pool_dump_at_shutdown|停止時のキャッシュ情報保存
innodb_buffer_pool_dump_now|キャッシュ情報の即時保存指示
innodb_buffer_pool_filename|キャッシュ情報ファイル名
innodb_buffer_pool_load_abort|キャッシュ情報読込の中断
innodb_buffer_pool_load_at_startup|起動時のキャッシュ情報読込
innodb_buffer_pool_load_now|キャッシュ情報の即時読込指示
innodb_change_buffer_max_size|変更バッファの最大割合
innodb_checksum_algorithm|InnoDBページのチェックサム方式
innodb_commit_concurrency|同時コミット処理数
innodb_concurrency_tickets|InnoDB実行スレッドの処理割当
innodb_data_home_dir|内部データ領域のパス
innodb_deadlock_detect|デッドロックの検出
innodb_default_row_format|新規InnoDB表の行形式
innodb_doublewrite|二重書込バッファ（Aurora独自ストレージ管理）
innodb_file_per_table|表ごとの表スペース利用
innodb_fill_factor|索引構築時に残すページ空き率
innodb_flush_log_at_timeout|redoフラッシュの周期
innodb_flush_log_at_trx_commit|コミット時のredo耐久性
innodb_flush_method|OSへの書込方式
innodb_flush_neighbors|周辺ページのまとめ書込
innodb_flushing_avg_loops|フラッシュの平均化期間
innodb_force_load_corrupted|破損表の強制ロード
innodb_ft_aux_table|全文索引の診断対象テーブル
innodb_ft_cache_size|全文索引のキャッシュサイズ
innodb_ft_enable_stopword|全文索引の除外語の有効化
innodb_ft_max_token_size|InnoDB全文索引の最大語長
innodb_ft_min_token_size|InnoDB全文索引の最小語長
innodb_ft_num_word_optimize|全文索引最適化の処理語数
innodb_ft_server_stopword_table|全体の全文索引除外語テーブル
innodb_ft_sort_pll_degree|全文索引構築の並列度
innodb_ft_user_stopword_table|利用者の全文索引除外語テーブル
innodb_io_capacity|背景I/O処理の容量目安
innodb_io_capacity_max|背景I/O処理の最大容量目安
innodb_lock_wait_timeout|行ロックを待つ秒数
innodb_log_compressed_pages|圧縮ページのログ処理
innodb_lru_scan_depth|ページキャッシュ回収時の探索深さ
innodb_max_dirty_pages_pct|未書込ページの割合の目安
innodb_max_purge_lag|不要履歴削除の遅延しきい値
innodb_max_purge_lag_delay|履歴削除遅延時のDML待機上限
innodb_monitor_disable|InnoDB内部計測の無効化
innodb_monitor_enable|InnoDB内部計測の有効化
innodb_monitor_reset|InnoDB計測値のリセット
innodb_monitor_reset_all|InnoDB計測値の全リセット
innodb_old_blocks_pct|ページキャッシュの古い領域割合
innodb_old_blocks_time|全件走査がキャッシュを汚すのを防ぐ待ち時間
innodb_online_alter_log_max_size|オンラインDDLの変更ログ上限
innodb_open_files|開いておくInnoDBファイル数
innodb_optimize_fulltext_only|全文索引のみ最適化する動作
innodb_page_cleaners|ページを掃除するスレッド数
innodb_page_size|InnoDBのページサイズ
innodb_parallel_read_threads|InnoDB並列読取スレッド数
innodb_print_all_deadlocks|すべてのデッドロックのログ記録
innodb_purge_batch_size|不要な行履歴を削除するバッチサイズ
innodb_purge_threads|不要な行履歴を削除するスレッド数
innodb_read_io_threads|読取I/Oスレッド数
innodb_read_only|InnoDB内部の読取専用動作
innodb_replication_delay|複製処理の待機調整
innodb_rollback_on_timeout|ロック待ち期限超過で全トランザクションを戻すか
innodb_rollback_segments|ロールバックセグメント数
innodb_sort_buffer_size|索引作成のソート領域
innodb_spin_wait_delay|競合ロックのspin待ち間隔
innodb_spin_wait_pause_multiplier|CPU pauseによるspin待ち調整
innodb_stats_auto_recalc|統計の自動再計算
innodb_stats_include_delete_marked|削除マーク行を統計へ含めるか
innodb_stats_method|NULLの統計計算方式
innodb_stats_on_metadata|メタデータ参照時の統計再計算
innodb_stats_persistent|最適化統計の永続化
innodb_stats_persistent_sample_pages|永続統計の標本ページ数
innodb_stats_transient_sample_pages|一時統計の標本ページ数
innodb_status_output|InnoDB状態の定期ログ
innodb_status_output_locks|ロック状態の定期ログ
innodb_strict_mode|InnoDB設定・DDLの厳格な検査
innodb_sync_array_size|内部待機配列のサイズ
innodb_sync_spin_loops|競合ロックのspin回数
innodb_table_locks|InnoDBとSQL表ロックの連携
innodb_thread_concurrency|内部実行スレッドの同時数
innodb_thread_sleep_delay|実行スレッドの待機間隔
innodb_trx_commit_allow_data_loss|コミット耐久性を弱める変更の許可
innodb_undo_directory|undo領域の管理パス
innodb_use_native_aio|OS非同期I/Oの利用
innodb_write_io_threads|書込I/Oスレッド数
interactive_timeout|対話型接続の無通信期限
internal_tmp_mem_storage_engine|内部一時表のメモリエンジン
join_buffer_size|索引を使えない結合等の作業メモリ
keep_files_on_create|表作成時の既存ファイル取扱い
key_buffer_size|MyISAM索引のキャッシュ
key_cache_age_threshold|MyISAM索引キャッシュの古さ判定
key_cache_block_size|MyISAM索引キャッシュのブロックサイズ
key_cache_division_limit|MyISAM索引キャッシュの分割率
lc_time_names|日付の月・曜日名の言語
local_infile|クライアントからのローカルファイル取込許可
lock_wait_timeout|メタデータロックの待ち期限
log-bin|binlogの管理ファイル名
log_bin_trust_function_creators|binlog利用時のストアド作成者の信頼
log_error|エラーログの管理パス
log_error_suppression_list|記録しないエラーコード
log_error_verbosity|エラーログの詳細度
log_output|SQLログの出力先
log_queries_not_using_indexes|索引未使用SQLの記録
log_replica_updates|複製適用イベントをbinlogへ記録
log_slow_admin_statements|遅い管理SQLの記録
log_slow_extra|slow logの追加情報
log_slow_replica_statements|複製に関する遅いSQLの記録
log_throttle_queries_not_using_indexes|索引未使用SQLログの件数制限
long_query_time|slow logへ記録する実行秒数のしきい値
low_priority_updates|MyISAM等の表ロックで更新の優先度を下げる
lower_case_table_names|テーブル名の大小文字の扱い
mandatory_roles|全ユーザーへの必須ロール
max_allowed_packet|通信/SQLパケットの最大サイズ
max_binlog_cache_size|トランザクション用binlogキャッシュの上限
max_binlog_size|binlogファイルのサイズ
max_binlog_stmt_cache_size|非トランザクション用binlogキャッシュ上限
max_connect_errors|接続元を遮断する連続通信エラー回数
max_connections|DBが受け付ける同時接続数の上限
max_delayed_threads|旧式遅延挿入スレッド数
max_digest_length|SQL集約用digestの入力サイズ
max_error_count|保持する警告・エラーの件数
max_execution_time|読取SELECTの実行上限ミリ秒
max_heap_table_size|MEMORY表のサイズ上限
max_insert_delayed_threads|旧式遅延挿入スレッド数の互換名
max_join_size|巨大結合の処理量制限
max_points_in_geometry|空間処理で許可する点の数
max_prepared_stmt_count|サーバーprepared statement数の上限
max_seeks_for_key|索引アクセスのコスト見積もり
max_sort_length|ソート時に比較する値の長さ
max_sp_recursion_depth|ストアドの再帰深さ
max_user_connections|ユーザーごとの同時接続上限
max_write_lock_count|書込ロックの優先回数
min_examined_row_limit|slow log記録対象の最小走査行数
mysql_native_password|旧認証プラグインの有効状態
mysql_native_password_proxy_users|旧認証のPROXYユーザー連携
net_buffer_length|通信バッファの初期サイズ
net_read_timeout|DBがクライアントからの受信を待つ秒数
net_retry_count|通信内部の再試行回数
net_write_timeout|DBが結果送信を待つ秒数
ngram_token_size|日本語等の全文検索を分割する文字数
optimizer_prune_level|実行計画候補の枝刈り
optimizer_search_depth|結合順序探索の深さ
optimizer_switch|SQL最適化機能の個別ON/OFF
optimizer_trace|実行計画選択の診断記録
optimizer_trace_features|最適化診断の対象機能
optimizer_trace_limit|保持する最適化診断件数
optimizer_trace_max_mem_size|最適化診断のメモリ上限
optimizer_trace_offset|取得する診断の位置
partial_revokes|部分的な権限取り消しの有効化
password_history|過去パスワードの再利用禁止回数
password_require_current|パスワード変更時の現パスワード要求
password_reuse_interval|パスワード再利用禁止日数
performance_schema|性能分析用の計測基盤
pid_file|AWS管理のプロセスIDファイル
plugin_dir|AWS管理のプラグイン配置先
port|DBの待受ポート
preload_buffer_size|索引の事前読込バッファ
profiling_history_size|旧式プロファイリング履歴件数
query_alloc_block_size|SQL処理用メモリの割当単位
query_prealloc_size|SQL処理用メモリの事前割当
range_alloc_block_size|範囲探索のメモリ割当単位
range_optimizer_max_mem_size|範囲探索の最適化メモリ上限
read_buffer_size|走査ごとの読取バッファ
read_only|通常ユーザーの更新制限。Global役割制御とは別
read_rnd_buffer_size|ソート後のランダム読取バッファ
regexp_stack_limit|正規表現処理のstack上限
regexp_time_limit|正規表現処理の時間制限
relay-log|binlog複製の受信ログ管理パス
relay-log-space-limit|binlog複製の受信ログ容量上限
relay_log_recovery|再起動時の受信ログ復旧
replica-skip-errors|binlog複製エラーのスキップ指定
replica_checkpoint_group|複製checkpointの処理件数
replica_checkpoint_period|複製checkpointの間隔
replica_parallel_type|binlog複製の並列化方式
replica_parallel_workers|binlog複製の並列worker数
replica_pending_jobs_size_max|複製worker待ちキューのメモリ上限
replica_preserve_commit_order|複製先でのコミット順維持
replica_sql_verify_checksum|複製適用時のチェックサム検査
replica_transaction_retries|複製トランザクション再試行回数
replica_type_conversions|複製時の型変換の許可範囲
require_secure_transport|暗号化通信の要求
restrict_fk_on_non_standard_key|非一意キーを参照する外部キーの制限
rpl_read_size|binlog読み出しバッファ
safe-user-create|旧式のユーザー作成制限
schema_definition_cache|スキーマ定義のキャッシュ
secure_file_priv|サーバーファイル入出力の許可ディレクトリ
server_audit_events|監査するDB操作の種類
server_audit_excl_users|監査対象から除外するユーザー
server_audit_incl_users|監査対象へ含めるユーザー
server_audit_logging|拡張監査の有効化
server_audit_logs_upload|監査ログ転送設定
server_audit_query_log_limit|監査ログに記録するSQL長
server_id|複製用サーバー識別番号
show_create_table_verbosity|SHOW CREATE TABLEの詳細表示
show_gipk_in_create_table_and_information_schema|自動生成された不可視主キーの表示
skip-replica-start|起動時にbinlog複製を自動開始するか
skip_external_locking|OS外部ファイルロックの抑止
skip_name_resolve|DB認証時のDNS逆引き抑止
skip_show_database|DB一覧表示の権限制限
slow_launch_time|スレッド起動遅延のしきい値
slow_query_log|遅いSQLの記録
slow_query_log_file|slow logの管理パス
socket|ローカル接続ソケットの管理パス
sort_buffer_size|ソートごとの作業メモリ
source_verify_checksum|binlog送信側のチェックサム検査
sql_generate_invisible_primary_key|主キーなし表への不可視主キー生成
sql_mode|SQLの厳格性・互換性・日付等の解釈
sql_select_limit|SELECTが返す行数の既定上限
ssl_cipher|TLS1.2の許可暗号スイート
ssl_session_cache_mode|TLSセッション情報の再利用
ssl_session_cache_timeout|TLSセッションキャッシュ期限
stored_program_cache|ストアド処理のキャッシュ
stored_program_definition_cache|ストアド定義のキャッシュ
sync_binlog|binlogの耐久化タイミング
sync_relay_log_info|複製位置情報の同期頻度
sync_source_info|複製元接続情報の同期頻度
sysdate-is-now|SYSDATEをNOW相当として扱うか
table_cache_element_entry_ttl|テーブルキャッシュ要素の保持時間
table_definition_cache|テーブル定義キャッシュ
table_open_cache|開いているテーブルのキャッシュ
table_open_cache_instances|テーブルキャッシュの分割数
tablespace_definition_cache|表スペース定義のキャッシュ
temptable_max_mmap|内部一時表がmmapで使う領域上限
temptable_max_ram|内部一時表が使うRAM上限
temptable_use_mmap|内部一時表のmmap利用
thread_cache_size|接続スレッドの再利用数
thread_handling|AWS管理のスレッド処理方式
thread_stack|スレッドあたりのstack領域
time_zone|DBセッションの既定タイムゾーン
tls_ciphersuites|TLS1.3の許可暗号スイート
tls_version|許可するTLSプロトコル版
tmp_table_size|内部一時表ごとのサイズ上限
tmpdir|一時ファイルの管理パス
transaction_alloc_block_size|トランザクション処理メモリの割当単位
transaction_isolation|既定のトランザクション分離レベル
transaction_prealloc_size|トランザクション用メモリの事前確保
updatable_views_with_limit|LIMIT付きviewの更新可否
validate-password|旧式パスワード検証pluginの互換設定
validate_password.changed_characters_percentage|変更後パスワードに要求する文字変更率
validate_password.check_user_name|ユーザー名とパスワードの一致検査
validate_password.dictionary_file|辞書による弱いパスワード検査
validate_password.length|パスワード最小長
validate_password.mixed_case_count|大小英字の必要数
validate_password.number_count|数字の必要数
validate_password.policy|パスワード検証強度
validate_password.special_char_count|記号の必要数
wait_timeout|通常接続の無通信期限
windowing_use_high_precision|window関数の高精度計算
xa_detach_on_prepare|XA prepare後の接続分離動作
'''
ROLES = dict(line.split('|', 1) for line in ROLES_TEXT.strip().splitlines())

STRICT = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION'
AUTO = {'innodb_buffer_pool_size', 'innodb_purge_threads', 'table_definition_cache', 'table_open_cache'}

# name: online direct, batch direct, common through proxy, rationale, references
OVERRIDES = {
 'authentication_policy': ('*:caching_sha2_password',)*3 + ('新規認証をSHA-2へ統一。既存ユーザーは別途移行。','S22'),
 'require_secure_transport': ('ON',)*3 + ('VPC内部もTLS必須。JDBCホスト名検証とProxy RequireTLSも設定。','S22 S30'),
 'tls_version': ('TLSv1.2,TLSv1.3',)*3 + ('古いTLSへの後退を防ぐ。全クライアントの対応を確認。','S22 S30'),
 'sql_mode': (STRICT,)*3 + ('新規構成は厳格モードを明示。API既定0とCommunity既定を区別。既存SQL/取込は回帰試験。','S53'),
 'character_set_server': ('utf8mb4',)*3 + ('DB/表/列の作成時の既定。既存データは自動変換されない。','S53'),
 'character_set_database': ('継承。CREATE DATABASEでutf8mb4',)*3 + ('schema定義を明示し、読み取り用の状態変数を接続ごとに乱用しない。','S53'),
 'character_set_client': ('交渉に任せる。JDBC UTF-8',)*3 + ('ドライバ・DB間の文字集合交渉とテストで合わせる。','S27'),
 'character_set_connection': ('交渉に任せる。JDBC UTF-8',)*3 + ('独自SET NAMESを追加せず、ドライバ設定で整合。','S27'),
 'character_set_results': ('交渉に任せる。JDBC UTF-8',)*3 + ('返却文字集合と文字化けをUnicode境界値で確認。','S27'),
 'collation_server': ('新規:utf8mb4_0900_ai_ci',)*3 + ('既存は維持。大小文字/濁点等の同一視を業務で確認し、識別子列は厳密な照合規則を個別採用。','S53'),
 'collation_connection': ('JDBCとDBの照合規則を一致',)*3 + ('列の照合規則と接続の規則は別。比較の暗黙変換を調査。','S27 S53'),
 'time_zone': ('UTC',)*3 + ('日本時間への変換は表示層。全地域・バッチの処理基準時刻を統一。','S53'),
 'local_infile': ('0',)*3 + ('通常アプリのローカルファイル取込を禁止。専用取込の例外は別設計。','S53'),
 'innodb_file_per_table': ('1',)*3 + ('領域回収と表単位の保守。既存表の再構築は別作業。','S37'),
 'innodb_default_row_format': ('DYNAMIC',)*3 + ('新規表を標準的な行形式に統一する。','S54'),
 'innodb_flush_log_at_trx_commit': ('1',)*3 + ('確定済みデータの耐久性を性能のために弱めない。','S20'),
 'innodb_trx_commit_allow_data_loss': ('0',)*3 + ('耐久性を弱める設定変更の入口を閉じる。','S20'),
 'innodb_strict_mode': ('ON',)*3 + ('不適切な表定義を黙認しない。','S54'),
 'innodb_deadlock_detect': ('ON',)*3 + ('競合を早期検出し、業務単位の安全な再試行へつなげる。','S54'),
 'innodb_lock_wait_timeout': ('5秒','30秒','5秒','共用Writerではonlineを優先。batchはチャンク短縮と上限付き再試行。','S54'),
 'lock_wait_timeout': ('10秒','30秒','10秒','metadata lockの無期限に近い待ちを防ぐ。DDLは保守用セッションで別管理。','S53'),
 'max_execution_time': ('5000ms','90000ms','90000ms + online SELECTヒント5000ms','SELECT用。DML全体には効かないのでJDBC/JTAの期限と組み合わせる。','S53'),
 'innodb_rollback_on_timeout': ('ON（要回帰）',)*3 + ('ロック待ち失敗時の部分確定を避ける。アプリでも全体rollback。staticのため再起動。','S54'),
 'connect_timeout': ('10秒',)*3 + ('DB側の初回通信待ち。JDBC connectTimeoutはonline3秒/batch5秒。','S53'),
 'wait_timeout': ('600秒','3600秒','28800秒','Proxy内部poolの接続を不用意に切らず、client idle1800秒/app idle300秒で整理。','S07 S53'),
 'interactive_timeout': ('600秒','3600秒','28800秒','通常JDBCはinteractive=falseのためwait_timeoutが主対象。','S27 S53'),
 'net_read_timeout': ('30秒',)*3 + ('SQL実行時間ではなく入力受信中の待ち。batchは実測がある場合のみ延長。','S53'),
 'net_write_timeout': ('60秒',)*3 + ('結果消費が遅いbatchはページングで改善。必要に応じセッションだけ延長しpinningを確認。','S53'),
 'max_connections': ('AWS式を維持・実効値採取',)*3 + ('最大ACU変更に伴う自動再計算の反映は再起動。カスタム値の直接変更はDB側では再起動不要だが、Proxy反映要件は別途確認。接続数とCPU処理能力は別。','S17 S08'),
 'max_user_connections': ('既定維持。アプリpoolで上限制御',)*3 + ('DBユーザー制限は共有poolやProxy内部利用と合わせ検証。適当な全体一律値を置かない。','S53 S07'),
 'max_allowed_packet': ('既定維持、必要payloadで検証',)*3 + ('大きいBLOBは別保管も検討。上限だけ増やすとメモリ圧迫。16KBのProxy pinningとは別の制約。','S09 S53'),
 'transaction_isolation': ('REPEATABLE-READ','REPEATABLE-READ基準、RCは個別検証','REPEATABLE-READ','SQLの読み取り一貫性を保つ。batchのRC化は業務上許される単位で行う。','S53'),
 'autocommit': ('1、JTA管理区間はEAPに任せる','1を既定、チャンク中は明示false','1を既定、JTA/チャンク終了を保証','グローバルで常時OFFにしない。短いトランザクションで接続の返却を促す。','S10'),
 'init_connect': ('空を維持','空を維持','空を維持','ProxyではDB側init_connectへ依存しない。必要な共通初期化はProxy InitQueryに限定。','S08'),
 'binlog_format': ('OFF',)*3 + ('Globalのストレージ複製にbinlogは不要。DMS/CDC等の別要件があるときだけROWを含め再設計。','S15 S20'),
 'read_only': ('AWS既定0・役割管理に任せる',)*3 + ('Global secondaryの書込保護を0で解除できると考えない。接続先の役割とDB権限を確認。','S04 S20'),
 'event_scheduler': ('OFF',)*3 + ('DR時の二重実行を防ぐため業務ジョブは外部スケジューラで切替。既存利用がある場合は移行設計。','S53'),
 'general_log': ('0',)*3 + ('全SQLの常時記録は費用と機密値の流出を増やす。調査時だけ期間限定。','S20'),
 'slow_query_log': ('1',)*3 + ('SQL改善のため有効化しCloudWatch転送と保持/権限を別設定。','S20'),
 'long_query_time': ('1秒','5秒','1秒','共用では短い側で遅延を可視化し、DBユーザー別に分析する。','S53'),
 'log_output': ('FILE',)*3 + ('ファイルログと管理された転送を使う。TABLEへの常時出力を避ける。','S20'),
 'log_queries_not_using_indexes': ('0',)*3 + ('索引未使用が必ず問題とは限らずログ量が急増。必要時に対象期間を限定。','S53'),
 'log_slow_admin_statements': ('1',)*3 + ('DDL等の長時間化を発見する。ログ保持とアクセスを管理。','S53'),
 'innodb_print_all_deadlocks': ('1',)*3 + ('競合の根拠を残す。SQLや個人情報がログに入る可能性を管理。','S20'),
 'server_audit_logging': ('1（監査要件に合わせ試験）',)*3 + ('CONNECT/DDL/DCLを初期対象。DML記録は機密値と容量を評価して追加。','S20'),
 'server_audit_events': ('CONNECT,QUERY_DDL,QUERY_DCL',)*3 + ('業務監査でDMLが必須ならQUERY_DMLを追加し負荷検証。単なる全件記録を監査設計としない。','S20'),
 'server_audit_logs_upload': ('0を継承、ログexportを別途有効',)*3 + ('AuroraのCloudWatch Logs export設定と整合を確認。パラメータ単独で転送完了と判断しない。','S20'),
 'performance_schema': ('Database Insightsと併せて有効化確認',)*3 + ('API既定0と自動管理/実効値は別。計測を有効にし最小ACUのメモリを検証。全consumerの巨大化は避ける。','S45 S46'),
 'aurora_enable_memory_management': ('ONを維持',)*3 + ('8.4の自動メモリ回復を使用。この間aurora_oom_responseの個別設定は無視される。','S20'),
 'aurora_oom_response': ('既定継承（自動管理ON時は無視）',)*3 + ('ONの自動管理を優先し、独自の回復動作へ無条件に変更しない。','S20'),
 'aurora_parallel_query': ('OFFを基準、分析用途は別途評価',)*3 + ('現行FAQはServerless互換と説明。古い非対応情報で断定しない。本件はOLTPを基準に、版・容量・I/O費用・実行計画を確認して採否を決める。','S61'),
 'aurora_read_replica_read_committed': ('OFF',)*3 + ('Readerの特殊な整合性最適化を、単なるREAD COMMITTEDの一般設定と混同しない。','S20'),
 'aurora_replica_read_consistency': ('既定継承（転送は無効）',)*3 + ('write forwardingを有効にする別設計でもProxyではSESSIONを採用しない。','S04'),
 'lower_case_table_names': ('新規0、既存は固定値を維持',)*3 + ('作成時制約があり後から簡単に変えられない。Windows開発環境の大小文字無視に依存しない。','S20'),
 'restrict_fk_on_non_standard_key': ('1',)*3 + ('参照先は一意キーを明示。互換性のため安易に制限を外さない。','S02'),
 'innodb_stats_persistent': ('ON',)*3 + ('実行計画の統計を永続化して変動を抑える。','S54'),
 'innodb_stats_auto_recalc': ('ON',)*3 + ('通常統計の自動更新。8.4.7のhistogram自動更新非対応とは別。','S02 S54'),
 'innodb_stats_on_metadata': ('OFF',)*3 + ('管理参照だけで統計再計算を増やさない。','S54'),
 'aurora_enable_validate_password_component': ('1（新規環境）',)*3 + ('Secretsの生成条件と一致を検証。既存パスワード運用への影響を先に調べる。','S23'),
 'validate_password.length': ('20',)*3 + ('機械生成の長いパスワードを基準にする。','S23'),
 'validate_password.policy': ('MEDIUM（API値1）',)*3 + ('辞書ファイル依存を避け、必要な文字種を検証。','S23'),
 'validate_password.check_user_name': ('1',)*3 + ('ユーザー名をそのまま秘密にしない。','S23'),
 'default_password_lifetime': ('0 + Secretsで期限付きrotation',)*3 + ('日数経過による突発的なアプリ停止を避ける。更新頻度は運用ポリシーで強制し放置しない。','S22 S33'),
 'generated_random_password_length': ('32',)*3 + ('DBが生成する場合の候補。Secrets側の生成設定は別に一致させる。','S23'),
}


def category(name):
    n = name.replace('-', '_')
    if n.startswith('performance_schema'):
        return '性能計測', 'S55 S46'
    if n.startswith(('binlog', 'replica', 'replicate', 'relay', 'gtid', 'sync_source', 'sync_relay')):
        return 'binlog複製', 'S20 S15'
    if n.startswith(('validate', 'password', 'authentication', 'mysql_native', 'ssl', 'tls', 'require_secure')):
        return '認証・暗号', 'S22 S23'
    if n.startswith(('aws_default_', 'aurora_lambda', 'aurora_ml')):
        return '外部サービス連携', 'S20'
    if n.startswith(('myisam', 'key_cache', 'ft_', 'delayed', 'bulk_insert')):
        return '互換・旧エンジン', 'S20 S53'
    if n.startswith(('innodb_ft', 'ngram')):
        return '全文検索', 'S54'
    if n.startswith(('log_', 'server_audit', 'slow_', 'general_', 'long_query')):
        return 'ログ・監査', 'S20'
    if n.startswith(('optimizer_', 'range_', 'eq_', 'histogram_', 'regexp_', 'cte_', 'max_join', 'sql_')):
        return 'SQL実行・最適化', 'S53'
    if 'buffer' in n or 'cache' in n or 'table_size' in n or 'temptable' in n:
        return 'メモリ・一時領域', 'S17 S38'
    if 'timeout' in n or n.startswith(('connect_', 'net_', 'max_connection', 'max_user')):
        return '接続・時間制限', 'S53 S54'
    if n.startswith('innodb'):
        return 'InnoDB・記憶領域', 'S54 S35'
    return '基本動作・互換性', 'S20 S53'


def role(name):
    if name in ROLES:
        return ROLES[name]
    if name.startswith('aws_default_'):
        return name.removeprefix('aws_default_').removesuffix('_role') + 'をDBから呼び出すIAMロール'
    if name.startswith(('replicate-', 'replicate_')):
        return 'binlog複製の対象を選別するフィルター（' + name + '）'
    if name.startswith('myisam_'):
        return '旧MyISAMエンジン用の内部調整（' + name + '）'
    if name.replace('-', '_').startswith('performance_schema_'):
        key = name.replace('-', '_').removeprefix('performance_schema_')
        terms = [('consumer', '収集有効化'),('events', 'イベント'),('statements', 'SQL'),('transactions','トランザクション'),('stages','処理段階'),('waits','待機'),('history_long','長期履歴'),('history','履歴'),('current','現在'),('size','件数/容量'),('max','最大'),('memory','メモリ'),('metadata_locks','メタデータロック'),('prepared','prepared'),('mutex','mutex'),('thread','スレッド'),('socket','通信'),('file','ファイル'),('table','テーブル'),('index','索引'),('digest','SQL集約'),('instrumentation','計測'),('instrument','計測対象')]
        for eng, ja in terms:
            key = key.replace(eng, ja)
        return 'Performance Schema: ' + key.replace('_','・')
    return 'エンジンの個別制御。API説明と参照仕様を確認（' + name + '）'


def decision(param):
    n = param['ParameterName']
    cat, ref = category(n)
    note = '新規/変更後の実効値を確認。APIのApplyTypeはDB一般仕様で、Proxyとv2の追加条件は別。'
    if param.get('MinimumEngineVersion') == '8.4.mysql_aurora.8.4.8':
        return cat, ['対象外：8.4.8以降'] * 3, '8.4.7では設定しない。ファミリー一覧の存在だけで採用しない。', '対象外', 'S56 S57'
    if not param['IsModifiable']:
        extra = 'AuroraではON固定。新規ユーザーはSHA-2を推奨。' if n == 'mysql_native_password' else 'AWS管理項目。利用者がOS/エンジン内部値を変更する設計にしない。'
        return cat, ['変更不可・AWS管理値を使用'] * 3, extra, '変更不可', ref
    if n in AUTO:
        return cat, ['Serverless v2の自動調整に任せる'] * 3, 'APIは変更可だがv2はカスタム値を採用しない。固定値の最適化は行わない。', 'v2自動調整', 'S17'
    if n in OVERRIDES:
        v = OVERRIDES[n]
        return cat, list(v[:3]), v[3], '重点設計', v[4]
    reasons = {
      '性能計測': '既定の計測範囲/自動サイズを維持。全履歴・全instrumentを有効化するとCPU/メモリを増やす。必要な診断を期間限定で追加。',
      'binlog複製': '本構成のGlobal複製はストレージ層。CDC/外部binlog複製を利用しない限り既定を変更しない。複製エラーの無条件スキップは採らない。',
      '認証・暗号': 'SHA-2とTLSを前提に互換性・パスワード運用を検証。既定の暗号や認証制約を性能目的で緩めない。',
      '外部サービス連携': '今回DBからの外部呼出し要件はないため未設定/既定を維持。利用するときだけ地域別の最小権限ロールと期限を設計。',
      '互換・旧エンジン': '永続業務データはInnoDB。旧エンジン用のバッファや互換機能へメモリを増やさない。APIに存在しても利用を推奨しない。',
      '全文検索': '全文検索の業務要件がないため既定維持。変更時は索引再構築・日本語検索結果・追加領域を検証。',
      'ログ・監査': '必要な監査/遅延診断を確保し、過大な記録・機密値露出を避ける。出力先と保持期間は別途管理。',
      'SQL実行・最適化': '既定を基準に実行計画と実データの回帰試験。特定SQLの問題をグローバル変更で全SQLへ広げない。',
      'メモリ・一時領域': '最小ACUでの同時実行が制約。各接続/処理の作業領域を一律に拡大せず、SQL改善・同時実行制限を先に評価。',
      '接続・時間制限': 'ドライバ/Proxy/業務期限と対象区間を分離。不要な期限延長で混雑を隠さない。',
      'InnoDB・記憶領域': 'Aurora独自の永続化方式とServerless容量変動を尊重。実測のないI/O/スレッド/メモリ変更は行わない。',
      '基本動作・互換性': 'JNDI経由かDriverManagerかだけでエンジン動作を変える理由はない。業務契約の変更を伴う場合にのみ個別設定。',
    }
    return cat, ['明示上書きなし・既定列を継承'] * 3, reasons[cat], '既定維持', ref
