##parameters=url, size=80
# $Id$

for pattern in ('http://', 'https://', 'ftp://'):
    if url.startswith(pattern):
        url = url[len(pattern):]
        break

if url is None or len(url) < size:
    return url

mid_size = (size-3)/2
return url[:mid_size] + '...' + url[-mid_size:]
