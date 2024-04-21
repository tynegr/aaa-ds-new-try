import abc

import httpx


class ResultsObserver(abc.ABC):
    @abc.abstractmethod
    def observe(self, data: bytes) -> None: ...


async def do_reliable_request(url: str, observer: ResultsObserver) -> None:
    async with httpx.AsyncClient() as client:
        while True:
            try:
                response = await client.get(url)
                response.raise_for_status()
                data = response.read()
                observer.observe(data)
                break
            except (httpx.HTTPError, httpx.TimeoutException):
                continue
