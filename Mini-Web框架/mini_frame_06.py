def application(environ, start_response):
    # start_response('200 OK', [('Content-Type', 'text/html;charset=gbk')])
    start_response('200 OK', [('Content-Type', 'text/html;charset=utf-8')])
    return "hello world!哈哈哈"