import re
import time

from aiohttp import ClientTimeout, ClientResponse
from aiohttp.formdata import FormData
from aiohttp_retry import RetryClient, ClientSession


class Request:
    def __init__(self, *args, **kwargs):
        self.client_session = ClientSession()
        self.retry_client = RetryClient(client_session=self.client_session)
        self.request = self.retry_client.request(*args, **kwargs)

    async def __aenter__(self) -> ClientResponse:
        return await self.request

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client_session.close()
        await self.retry_client.close()


def request(method, url, data=None, json=None):
    if json is not None:
        return Request(method, url, json=json, timeout=ClientTimeout(total=1000))
    else:
        return Request(method, url, data=data, timeout=ClientTimeout(total=1000))


class Memo:
    def __init__(self, domain, openid, apiver):
        self.domain = domain
        self.openid = openid
        self.apiver = apiver
        self.url = f"{domain}api/{apiver}/memo?openId={openid}"

    async def send_memo(self, content="", visibility="PRIVATE", res_id_list=None):
        if res_id_list is None:
            res_id_list = []
        if content is None:
            content = ""
        data = {
            "content": content,
            "visibility": visibility,
            "resourceIdList": res_id_list,
            "relationList": []
        }
        tags = re.findall(r"#\S+", content)
        if tags:
            tag = Tag(self.domain, self.openid, self.apiver)
            for t in tags:
                t = t.replace("#", "")
                await tag.create_tag(t)
        async with request("POST", url=self.url, json=data) as resp:
            assert resp.status == 200
            resp_data = await resp.json()
            return resp_data["data"]["id"]


class Resource:
    def __init__(self, domain, openid, apiver):
        self.apiver = apiver
        self.url = f"{domain}api/{apiver}/resource/blob?openId={openid}"

    async def create_res(self, file):
        data = FormData()
        local_time = time.localtime(time.time())
        time_str = time.strftime("%Y%m%d_%H%M")
        data.add_field("file", file, filename=f"telegram-file-{time_str}.jpg", content_type="image/jpeg")
        async with request("POST", url=self.url, data=data) as resp:
            assert resp.status == 200
            resp_data = await resp.json()
            return resp_data["data"]["id"]


class Tag:
    def __init__(self, domain, openid, apiver):
        self.apiver = apiver
        self.url = f"{domain}api/{apiver}/tag?openId={openid}"

    async def create_tag(self, name):
        data = {"name": name}
        async with request("POST", url=self.url, json=data) as resp:
            assert resp.status == 200
