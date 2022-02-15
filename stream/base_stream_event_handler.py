import os
import shutil
from abc import ABC

from command_builder import get_hls_output_path
from common.data.redis_mapper import RedisMapper
from common.data.source_model import SourceModel
from common.event_bus.event_bus import EventBus
from common.event_bus.event_handler import EventHandler
from common.utilities import logger
from stream.stream_model import StreamModel
from stream.stream_repository import StreamRepository


class BaseStreamEventHandler(EventHandler, ABC):
    def __init__(self, stream_repository: StreamRepository, response_channel_name: str):
        self.event_bus = EventBus(response_channel_name)
        self.stream_repository = stream_repository

    def parse_message(self, dic: dict) -> (bool, StreamModel, SourceModel):
        if RedisMapper.is_pubsub_message_invalid(dic):
            return False, None, None

        mapper = RedisMapper(SourceModel())
        source_model: SourceModel = mapper.from_redis_pubsub(dic)
        if not source_model.id:
            logger.warn('invalid source model was requested but the stream will not be  started.')
            return False, None, None, ''
        prev_stream_model = self.stream_repository.get(source_model.id)

        return True, prev_stream_model, source_model

    @staticmethod
    def delete_prev_stream_files(source_id: str):
        hls_output_file_path = get_hls_output_path(source_id)
        folder: str = os.path.dirname(hls_output_file_path)
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                logger.error(f'Failed to delete {file_path}. Reason: {e}')
