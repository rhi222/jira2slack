# 環境構築
- python3系
- pip install slackweb
- pip install jira

# 設定方法
- user_info.pyに自分のid/passを記載(pushしないこと)
- conf以下に設定ファイルを作成(sample_conf.pyを参照)

# 実行方法
- crontabに下記のようなコマンドを仕込めば動くと思います
- 00 10 * * * python /path/to/jira2slack/jira2slack.py -c sample_conf
