#!/usr/bin/env python3

import re
import mechanicalsoup as ms
import pickle

class Args: pass 
args = Args()

def page_url(baseUrl, page):
    return baseUrl + f'?page={page}'
def process_page(baseurl, i, br):
    url = baseurl + f'&page={i}'
    # open the url and apge
    print( f"[INFO ] Fetching page {i}", url )
    r = br.open(url)
    assert r.ok
    html = br.get_current_page()
    trs = html.find_all('tr', recursive=True)
    res = []
    for tr in trs:
        tds = tr.find_all('td')
        tds = [x.text.strip() for x in tds]
        if len(tds) == 3:
            res.append(tds)
    print( f" + Found {len(res)} labnotes." )
    return res


def main():
    global args
    browser = ms.StatefulBrowser()
    browser.open(args.url)
    f = browser.select_form()
    browser['name'] = args.user
    browser['pass'] = args.password
    res = browser.submit_selected()
    if not res.ok:
        print( 'Failed to login.')
        quit(1)

    url = 'https://labnotes.ncbs.res.in/bhalla-lab/experiment-dates?title=&name=&date_filter%5Bmin%5D%5Byear%5D=2016&date_filter%5Bmin%5D%5Bmonth%5D=1&date_filter%5Bmin%5D%5Bday%5D=1&date_filter%5Bmax%5D%5Byear%5D=2022&date_filter%5Bmax%5D%5Bmonth%5D=1&date_filter%5Bmax%5D%5Bday%5D=1&field_bhalla_keywords_tid='
    h = browser.open(url)
    assert h.ok
    html = browser.get_current_page()
    # find the last page index.
    lastPage = html.find('a', title='Go to last page')
    if not lastPage:
        lastPage = 1
    else:
        m = re.search(r'page\=(\d+)', lastPage.attrs['href'])
        lastPage = int(m.group(1))
    print( f"[INFO ] Last page is {lastPage}" )

    data = []
    for i in range(0, lastPage+1):
        data += process_page(url, i, browser)

    with open('data.pickle', 'wb') as f:
        pickle.dump(data, f)
    print('all done')
    

if __name__ == '__main__':
    import argparse
    # Argument parser.
    description = '''description'''
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--url', '-U'
            , required = False, default = 'https://labnotes.ncbs.res.in'
            , help = 'labnote URL'
            )
    parser.add_argument('--user', '-u'
            , required = True
            , help = 'User name'
            )
    parser.add_argument( '--password', '-p'
            , required = True
            , type = str
            , help = 'password'
            )
    parser.parse_args(namespace=args)
    main()
