import time
from urllib import parse

import qiniu

from mcp_server.core.storage.tools import logger

FUNC_POSITION_NONE = "none"
FUNC_POSITION_PREFIX = "prefix"
FUNC_POSITION_SUFFIX = "suffix"


def url_add_processing_func(auth: qiniu.auth, url: str, func: str) -> str:
    func_items = func.split("/")
    func_prefix = func_items[0]

    url_info = parse.urlparse(url)
    new_query = _query_add_processing_func(url_info.query, func, func_prefix)
    new_query = parse.quote(new_query, safe='&=')
    url_info = url_info._replace(query=new_query)
    new_url = parse.urlunparse(url_info)
    new_url = _sign_url(str(new_url), auth)
    return new_url


def _query_add_processing_func(query: str, func: str, func_prefix: str) -> str:
    queries = query.split("&")
    if '' in queries:
        queries.remove('')

    # query 中不包含任何数据
    if len(queries) == 0:
        return func

    # funcs 会放在第一个元素中
    first_query = parse.unquote(queries[0])

    # funcs 不存在
    if len(first_query) == 0:
        queries.insert(0, func)
        return "&".join(queries)

    # first_query 有 = 说明不是 funcs
    if first_query.find("=") >= 0:
        queries.insert(0, func)
        return "&".join(queries)

    queries.remove(queries[0])

    # 未找到当前类别的 func
    if first_query.find(func_prefix) < 0:
        func = first_query + "|" + func
        queries.insert(0, func)
        return "&".join(queries)

    query_funcs = first_query.split("|")
    if '' in query_funcs:
        query_funcs.remove('')

    # 只有一个 func，且和当前 func 相同，拼接其后
    if len(query_funcs) == 1:
        func = first_query + func.removeprefix(func_prefix)
        queries.insert(0, func)
        return "&".join(queries)

    # 多个 func，查看最后一个是否和当前 func 匹配
    last_func = query_funcs[-1]

    # 最后一个不匹配，只用管道符拼接
    if last_func.find(func_prefix) < 0:
        func = first_query + "|" + func
        queries.insert(0, func)
        return "&".join(queries)

    # 最后一个匹配，则直接拼接在后面
    func = first_query + func.removeprefix(func_prefix)
    queries.insert(0, func)
    return "&".join(queries)


def _sign_url(url: str, auth: qiniu.auth) -> str:
    url_info = parse.urlparse(url)
    query = url_info.query
    if ('e=' not in query) or ('token=' not in query):
        return url

    queries = query.split("&")
    if '' in queries:
        queries.remove('')

    # 移除之前的签名信息，但顺序不可变
    expires = 3600
    new_queries = []
    for query_item in queries:
        if query_item.startswith('e='):
            try:
                deadline = int(query_item.removeprefix('e='))
                expires = deadline - int(time.time())
            except Exception as e:
                logger.warning(f"expires parse fail for url:{url} err:{str(e)}")
                expires = 3600
        elif not query_item.startswith('token='):
            new_queries.append(query_item)

    new_query = "&".join(new_queries)
    url_info = url_info._replace(query=new_query)
    new_url = parse.urlunparse(url_info)
    return auth.private_download_url(new_url, expires=expires)
