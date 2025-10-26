from typing import Mapping, Never

from loguru import logger

from dispatcher.interface import IUpdateDispatcher, IUpdatesPuller, Update


class UpdatesDispatcher:
    def __init__(
        self,
        updates_puller: IUpdatesPuller,
        channel_to_dispatcher_map: Mapping[str, IUpdateDispatcher]
    ):
        self._updates_puller = updates_puller
        self._channel_to_dispatcher_map = channel_to_dispatcher_map

    async def run_dispatching(self) -> Never:
        async for update in self._updates_puller.run_pulling_updates():
            logger.info(f"Dispatching update: {update}")
            await self._dispatch_update(update)

        raise RuntimeError(f"UpdatePuller {self._updates_puller} has suddenly stopped")

    async def _dispatch_update(self, update: Update) -> None: 
        dispatcher = self._channel_to_dispatcher_map.get(update.channel)
        if dispatcher is None:
            logger.error(f"No dispatcher associated with channel {update.channel}")
            return 

        await dispatcher.dispatch(update)

