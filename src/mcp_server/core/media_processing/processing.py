import qiniu

from ...config import config


class MediaProcessingService:
    def __init__(self, cfg: config.Config):
        self.cfg = cfg
        self.auth = qiniu.Auth(cfg.access_key, cfg.secret_key)

    def execute_fop(
        self,
        bucket: str,
        key: str,
        fops: str = None,
        persistent_type: int = None,
        workflow_template_id: str = None,
        pipeline: str = None,
        notify_url: str = None,
    ) -> dict:
        """
        执行持久化处理
        :param bucket:
        :param key:
        :param fops:
        :param persistent_type:
        :param workflow_template_id:
        :param pipeline:
        :param notify_url:
        :return: 返回字典 dict
            获取 persistentId key 为 persistentId
        """

        persistent_fop = qiniu.PersistentFop(
            auth=self.auth, bucket=bucket, pipeline=pipeline, notify_url=notify_url
        )
        result, info = persistent_fop.execute(
            key=key,
            fops=fops,
            persistent_type=persistent_type,
            workflow_template_id=workflow_template_id,
        )
        return result

    def get_fop_status(self, persistent_id: str) -> dict:
        """
        查询 fop 执行状态
        :param persistent_id:
        :return: dict
            持久化处理的状态，详见 https://developer.qiniu.com/dora/1294/persistent-processing-status-query-prefop
        """
        persistent_fop = qiniu.PersistentFop(auth=self.auth, bucket="")
        result, info = persistent_fop.get_status(persistent_id=persistent_id)
        return result
