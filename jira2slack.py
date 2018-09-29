#!/usr/bin/env python
# -*- coding: utf-8 -*-

from jira import JIRA
import slackweb
from user_info import personal_info
import os
import sys
import importlib
import argparse
import urllib
# import pprint

# pp = pprint.PrettyPrinter(indent=4)
base_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(base_dir, "conf"))


def parse_args():
	'''
	conf_file名を引数から取得する
	'''
	parser = argparse.ArgumentParser()
	parser.add_argument('-c', '--conf_names', type=str, help='specify conf name')
	args = parser.parse_args()
	args.conf_names = [x for x in args.conf_names.split(',')] if args.conf_names else []
	return args.conf_names


def get_conf(conf_name):
	'''
	コマンドラインの引数から、利用するconfを得る
	'''
	module = importlib.import_module(conf_name)
	conf = module.conf
	return conf


def basic_auth(personal_info, f_domain):
	'''
	jiraの認証、id/passは外部ファイルから読み込み
	'''
	f_jira = JIRA(basic_auth=(personal_info["name"], personal_info["password"]), server=f_domain)
	return f_jira


def pick_ticket(jiraconf, f_jira):
	'''
	confで指定されるjqlを利用して、チケットを絞り込む
	'''
	for c in jiraconf:
		if 'filterid' in c:
			tickets = f_jira.search_issues('filter={filterid}'.format(filterid=c['filterid']))
		else:
			tickets = f_jira.search_issues(c['jql'])
		c['tickets'] = tickets
	return jiraconf


def generate_tickets_info(jiraconf, f_jira, f_domain):
	'''
	取得したjira番号から、必要な情報を取得する
	'''
	for c in jiraconf:
		c['tickets_info'] = []
		for ticket in c['tickets']:
			ticket_info = get_ticket_info(ticket, f_domain)
			c['tickets_info'].append(ticket_info)
	return jiraconf


def get_ticket_info(ticket, f_domain):
	'''
	ticketごとに、必要な情報を取り出し
	'''
	ticket_info = {
		'number': '',
		'url': '',
		'summary': '',
		'assingee': '',
		'due_date': '',
	}
	ticket_info['number'] = ticket.key
	ticket_info['url'] = generate_ticket_url(ticket.key, f_domain)
	ticket_info['summary'] = ticket.fields.summary
	ticket_info['assingee'] = ticket.fields.assignee.name if ticket.fields.assignee else '担当者未割り当て'
	ticket_info['due_date'] = ticket.fields.duedate
	return ticket_info


def generate_ticket_url(ticket, f_domain):
	'''
	ticketのurlを造成
	'''
	ticket_url = "{domain}browse/{ticket_no}".format(domain=f_domain, ticket_no=ticket)
	return ticket_url


def create_messeage(jiraconf, jira_url):
	'''
	slack投稿用にテキストを整形
	'''
	messages = []
	# todo message type
	for c in jiraconf:
		number_of_ticket = len(c['tickets_info'])
		if number_of_ticket == 0:
			continue
		messages.append('■ {title}'.format(title=c['explain']))
		if number_of_ticket > 20:
			if 'filterid' in c:
				query_param = 'filter={filterid}'.format(filterid=c['filterid'])
			else:
				query_param = 'jql={jql}'.format(jql=urllib.parse.quote(c['jql']))
			messages.append(
				'該当チケットが{number_of_ticket}件あります。多すぎるので確認してください。 --> <{jira_url}/jira/issues/?{query_param}|here>'
				.format(number_of_ticket=number_of_ticket, query_param=query_param, jira_url=jira_url)
			)
		else:
			for t in c['tickets_info']:
				messages.append('- <{url}|{ticket_number}> | {assingee}'.format(url=t['url'], ticket_number=t['number'], assingee=t['assingee']))
				messages.append('> {summary} '.format(summary=t['summary']))
		messages.append('')  # confとconfの間には改行を入れる
	return ('\n').join(messages)


def post_slack(slack_messeage, slackconf):
	'''
	confファイルで指定された内容でslackに投稿
	'''
	slack = slackweb.Slack(url=slackconf["webhook_url"])
	slack.notify(channel=slackconf["channel"], username=slackconf["username"], text=slack_messeage, icon_emoji=slackconf["icon"])
	return


def main():
	jira_url = 'jira_url'  # set yourself
	f_jira = basic_auth(personal_info, jira_url)
	arg_list = parse_args()
	for arg in arg_list:
		conf = get_conf(arg)
		pick_ticket(conf['jira'], f_jira)
		generate_tickets_info(conf["jira"], f_jira, jira_url)
		message = create_messeage(conf["jira"], jira_url)
		if message == '':
			continue
		else:
			post_slack(message, conf["slack"])
	return


if __name__ == '__main__':
	main()
