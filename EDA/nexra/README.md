# Information about nexra datasets

## データの種類

- 積算水蒸気量 —> ss_vap_atm.grd (瞬間値)
- 海面更正気圧 —> ss_ps.grd　(瞬間値)
- 時間積算降水量 —>sa_tppn.grd　(1時間平均値、1時間積算に変換するとき　sa_tppn*3600にしてください。)
- 地表風速 —> ss_u10m.grd, ss_v10m.grd　(瞬間値)

## Scale

- 水平スケール 112km

## 備考

各フォルダーには予測開始時刻(yyyymmddhh)からの5日予測データが入っています。
データ形式は1時間毎のBinary、Big_endian、 4byteのデータです。
