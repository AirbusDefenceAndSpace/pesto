try:
    import loguru

    logger = loguru.logger
except ImportError as e:
    import logging

    logger = logging.getLogger(__name__)
