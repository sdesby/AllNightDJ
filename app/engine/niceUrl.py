#coding: utf8

def makeMePretty(url):
    url = url.replace(' ', '%20')
    #url = url.replace(u'à', '%e0')
    #url = url.replace(u'é', '%e9')
    #url = url.replace(u'ù', '%f9')

    print 'URL : ' + url
    return url
