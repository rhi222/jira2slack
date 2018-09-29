conf = {
	"slack": {
		"webhook_url": "https://hooks.slack.com/services/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",
		"channel": "#zzz_nishiyama_test",
		"username": "jira_bot",
		"icon": ":jira2:"
	},
	"jira": [
		{
			"explain": "今月完了したチケット",  # 必須項目：slack通知時にタイトルとして利用します
			"filterid": "12410",  # filteridでjqlを指定できます、後述のように直接jqlを記述もできます
		},
		{
			"explain": "@nishiyamaさんこのチケット確認してね",
			"jql": "project in (JALINTLSP) AND status = Closed AND Updated > startOfMonth() ORDER BY Updated DESC",  # jqslでチケット絞り込み
		},
		{
			"explain": "今月完了したチケット",  # 必須項目：slack通知時にタイトルとして利用します
			"filterid": "12410",  # 優先度は filterid > jqlです
			"jql": "project in (JALINTLSP) AND status = Closed AND Updated > startOfMonth() ORDER BY Updated DESC",
		},
	]
}
