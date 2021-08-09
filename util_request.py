import time
from copy import deepcopy
from datetime import datetime, timedelta

import pandas as pd
import requests_cache
from fake_useragent import UserAgent
from requests.exceptions import RetryError


def load_agents(filename, e_vars):
    try:
        df = pd.read_excel(filename, index_col=0, engine='openpyxl')
        e_vars.agent_list = deepcopy(df)
        e_vars.good_agent_list = deepcopy(df[(df['Works'] == 1)])
        e_vars.free_agent_list = deepcopy(
                df[(df['Works'] == 1) & (df['Last Used'] < datetime.now() - timedelta(days=1))])

    except Exception as e:
        df_dict = {'Agent': [], 'Works': [], 'Last Used': []}
        df = pd.DataFrame(df_dict)

        e_vars.agent_list = deepcopy(df)
        e_vars.good_agent_list = deepcopy(df)
        e_vars.free_agent_list = deepcopy(df)
        e_vars.agent_list.to_excel('agent_list.xlsx', engine='openpyxl')


def request_link(url, adapter, cache, e_vars, page_type):
    source = ''
    time_out_len = 5
    new_agent = False
    capt_sleep = 10
    bad_link = False

    # Item type pages don't typically have CAPTCHAs, just try a good one
    # Always just try the default, it often works

    with requests_cache.disabled():
        try:
            source = adapter.get(url, timeout=time_out_len).text
        except RetryError as e:
            print('RetryError', e)
            source = ''
            return source

        except Exception as e:
            print('Trying no agent', e)

    # If there are free agents left, use them
    # TODO: Turn this into a while loop, as long as not Captcha'd
    if len(e_vars.free_agent_list) > 0 and len(source) > 0 and not bad_link:
        random_agent = e_vars.free_agent_list.sample()

        with requests_cache.disabled():
            try:
                source = adapter.get(url, timeout=time_out_len, headers={'User-Agent': random_agent}).text
            except Exception as e:
                print('Trying free agent', e)
                source = ''
        if len(source) > 0 and 'checkCaptcha' not in source:
            e_vars.free_agent_list.remove(random_agent)
            e_vars.agent_list.loc[e_vars.agent_list['Agent'] == random_agent['Agent'], 'Last Used'] = datetime.now()

    # Grab one, use it, remove from list
    while (len(source) < 1 or 'checkCaptcha' in source) and not bad_link:
        time.sleep(2)
        ua = UserAgent()
        random_agent = ua.random
        new_agent = True
        # Keep trying random agents
        while random_agent in e_vars.agent_list['Agent']:
            random_agent = ua.random

        try:
            if e_vars.verbose: print(random_agent)
            if not cache:
                with requests_cache.disabled():
                    source = adapter.get(url, timeout=time_out_len, headers={'User-Agent': random_agent}).text
            else:
                source = adapter.get(url, timeout=time_out_len, headers={'User-Agent': random_agent}).text
        except Exception as e:
            df_bad = {'Agent': random_agent, 'Works': 0, 'Last Used': datetime.now()}
            e_vars.agent_list = e_vars.agent_list.append(df_bad, ignore_index=True)
            e_vars.agent_list.to_excel('agent_list.xlsx', engine='openpyxl')

        if 'checkCaptcha' in source:
            if e_vars.verbose: print('CAPTCHA, sleeping')
            time.sleep(capt_sleep)
            capt_sleep += 5
            df_good = {'Agent': random_agent, 'Works': 1, 'Last Used': datetime.now()}
            e_vars.agent_list = e_vars.agent_list.append(df_good, ignore_index=True)
            e_vars.good_agent_list = e_vars.good_agent_list.append(df_good, ignore_index=True)
            e_vars.agent_list.to_excel('agent_list.xlsx', engine='openpyxl')

    if new_agent:
        df_good = {'Agent': random_agent, 'Works': 1, 'Last Used': datetime.now()}
        e_vars.agent_list = e_vars.agent_list.append(df_good, ignore_index=True)
        e_vars.good_agent_list = e_vars.good_agent_list.append(df_good, ignore_index=True)
        e_vars.agent_list.to_excel('agent_list.xlsx', engine='openpyxl')

    return source
