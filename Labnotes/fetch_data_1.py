#!/usr/bin/env python3

import re
import mechanicalsoup as ms
import pickle
import itertools

def flatten(lss):
    return itertools.chain(*lss)

class Args: pass 
args = Args()

def page_url(baseUrl, page):
    return baseUrl + f'?page={page}'

def get_data_from_url(url, br):
    r = br.open(url)
    assert r.ok
    html = br.get_current_page()
    trs = html.find_all('tr')
    data = []
    for tr in trs:
        tds = [x.text.strip() for x in tr.find_all('td')]
        data.append(tds)
    print( f"  Fetched {len(data)} labnotes." )
    return data, html

def get_data(u, br):
    url = f'https://labnotes.ncbs.res.in/posts/{u}/list'
    data, html = get_data_from_url(url, br)
    
    # Now find other pages.
    lP = html.find('a', title='Go to last page')
    lastPage = 0
    if lP:
        lastPage = int(lP.attrs['href'].split('=')[-1])

    for i in range(1, lastPage+1):
        url = f'https://labnotes.ncbs.res.in/posts/{u}/list?page={i}'
        d, h = get_data_from_url(url, br)
        data += d
    return data


def main():
    global args
    br = ms.StatefulBrowser()
    br.open(args.url)
    br.select_form()
    br['name'] = args.user
    br['pass'] = args.password
    res = br.submit_selected()
    if not res.ok:
        print( 'Failed to login.')
        quit(1)

    # Find users.
    html = br.get_current_page()
    divs = html.find_all('div', class_='view-lab-members')
    users = [[x.text for x in div.find_all('a')] for div in divs]
    data = {}
    for u in flatten(users):
        userData = get_data(u, br)
        print( f"[INFO ] Total {len(userData)} entries for {u}" )
        data[u] = userData

    br.close()
    with open('data.pickle', 'wb') as f:
        pickle.dump(data, f)
    print( f"[INFO ] Saved to pickle file." )


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
