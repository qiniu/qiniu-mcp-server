from urllib import parse


def url_add_processing_tool(url: str, tool: str) -> str:
    tool_items = tool.split("/")
    tool_prefix = tool_items[0]

    url_info = parse.urlparse(url)
    new_query = _query_add_processing_tool(url_info.query, tool, tool_prefix)
    new_query = parse.quote(new_query, safe="")
    url_info = url_info._replace(query=new_query)
    new_url = parse.urlunparse(url_info)
    return str(new_url)


def _query_add_processing_tool(query: str, tool: str, tool_prefix: str) -> str:
    queries = query.split("&")
    if "" in queries:
        queries.remove("")

    # query 中不包含任何数据
    if len(queries) == 0:
        return tool

    # tool 会放在第一个元素中
    first_query = parse.unquote(queries[0])
    queries.remove(queries[0])

    # tool 不存在
    if len(first_query) == 0:
        queries.insert(0, tool)
        return "&".join(queries)

    # 未找到当前类别的 tool，则直接拼接在后面
    if first_query.find(tool_prefix) < 0:
        tool = first_query + "|" + tool
        queries.insert(0, tool)
        return "&".join(queries)

    query_tools = first_query.split("|")
    if "" in query_tools:
        query_tools.remove("")

    # 只有一个 tool，且和当前 tool 相同，拼接气候
    if len(query_tools) == 1:
        tool = first_query + tool.removeprefix(tool_prefix)
        queries.insert(0, tool)
        return "&".join(queries)

    # 多个 tool，查看最后一个是否和当前 tool 匹配
    last_tool = query_tools[-1]

    # 最后一个不匹配，只用管道符拼接
    if last_tool.find(tool_prefix) < 0:
        tool = first_query + "|" + tool
        queries.insert(0, tool)
        return "&".join(queries)

    # 最后一个匹配，则直接拼接在后面
    tool = first_query + tool.removeprefix(tool_prefix)
    queries.insert(0, tool)
    return "&".join(queries)
