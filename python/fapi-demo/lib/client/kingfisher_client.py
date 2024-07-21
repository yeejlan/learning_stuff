import hashlib
import random
import time
from uuid import uuid4
import httpx
from typing import Any, Dict, List, Optional, Tuple
import json

from core import logbook, request_context
from core.config import getConfig
from core.exception import FluxException
from core.uuid_helper import uuid_to_base58


logger = logbook.getLogger('kingfisher')
config = getConfig()

class KingfisherClientException(FluxException):
    def __init__(self, message: str, code: int = 0):
        super().__init__(message)
        self.code = code

class KingfisherClient:
    def __init__(self):
        self.host = ''
        self.access_key = ''
        self.access_key_suffix = ''
        self.timeout = 30
        self.headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json',
        }
        self.client = httpx.AsyncClient(timeout=self.timeout)
    
    def setTimeout(self, timeout: int):
        self.timeout = timeout
        return self
    
    def getTimeout(self) -> int:
        return self.timeout

    def getRequestId(self) -> str:
        try:
            request_id = request_context.getRequestId()
        except Exception:
            request_id = uuid_to_base58(uuid4())
        return request_id
    
    def getHttpClient(self) -> httpx.AsyncClient:
        return self.client
    
    def setHttpClient(self, client: httpx.AsyncClient):
        self.client = client
        return self
    
    def getHost(self):
        if not self.host:
            host = config.get('KINGFISHER_HOST')
            if not host:
                raise KingfisherClientException('kingfisher host is missing')
            self.host = host

        return self.host
    
    def getAccessKey(self):
        if not self.access_key:
            self.access_key = config.get('KINGFISHER_KEY')

        return self.access_key
    
    def getAccessKeySuffix(self):
        if not self.access_key_suffix:
            self.access_key_suffix = config.get('KINGFISHER_KEY_SUFFIX')

        return self.access_key_suffix    

    def build_header(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        self.headers['request-id'] = self.getRequestId()
        if self.access_key:
            r = random.randint(10000000, 99999999)
            t = int(time.time())
            self.headers['r'] = str(r)
            self.headers['t'] = str(t)
            self.headers['v'] = hashlib.sha256(f"{r}{t}{json.dumps(payload)}{self.access_key}".encode()).hexdigest()
            self.headers['k'] = self.access_key_suffix
        return self.headers

    async def call(self, method: str, payload: Dict[str, Any], http_method: str = 'POST') -> Tuple[Optional[KingfisherClientException], Optional[Dict[str, Any]]]:
        host = self.getHost()
        url = f"{host}{method}"
        headers = self.build_header(payload)
        try:
            async with self.client as client:
                response = await client.request(http_method, url, headers=headers, json=payload)
                result = self.handle_response(response)
                return None, result
        except KingfisherClientException as ex:
            return ex, None
        except Exception as ex:
            msg = self.ex_to_string(ex)
            logger.error(msg)
            return KingfisherClientException(msg, -1), None

    async def call_multi(self, method_and_payload: List[Tuple[str, Dict[str, Any]]]) -> List[Tuple[Optional[KingfisherClientException], Optional[Dict[str, Any]]]]:
        tasks = []
        for endpoint, payload in method_and_payload:
            tasks.append(self.call(endpoint, payload))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        responses = []
        for result in results:
            if isinstance(result, tuple):
                responses.append(result)
            elif isinstance(result, Exception):
                msg = self.ex_to_string(result)
                logger.error(msg)
                responses.append((KingfisherClientException(msg, -1), None))
            else:
                responses.append((None, None))

        return responses

    def handle_response(self, response: httpx.Response) -> Optional[Dict[str, Any]]:
        body = response.text
        try:
            result = json.loads(body)
        except json.JSONDecodeError:
            result = {}

        status = response.status_code

        if status != 200 and status != 201:
            response_message = result.get('message', body)
            message = f"KingfisherHttpClient Error, code: {status}, message: {response_message}"
            logger.error(message)
            raise KingfisherClientException(message, -1)

        if not body or not result:
            message = f"Bad response, code: {status}, body: {body}"
            logger.error(message)
            raise KingfisherClientException(message, -1)

        if 'code' in result and result['code'] != 0:
            message = result['message']
            raise KingfisherClientException(message, result['code'])

        return result['data']

    def ex_to_string(self, ex: Exception) -> str:
        return f"{type(ex).__name__}: {ex.args[0]}"

if __name__ == "__main__":
    import asyncio

    async def main():
        client = KingfisherClient()
        error, result = await client.call('/api/method', {'param': 'value'})
        if error is None:
            print("Success:", result)
        else:
            print("Error:", error)
    asyncio.run(main())