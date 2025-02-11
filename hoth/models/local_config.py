import datetime
import fort
import logging
import os
import pathlib
import secrets

log = logging.getLogger(__name__)


def get_local_config_path() -> pathlib.Path:
    config_db_location = os.getenv('LOCAL_CONFIG', '.local/config.db')
    config_db_path = pathlib.Path(config_db_location).resolve()
    log.debug(f'Using local configuration path: {config_db_path}')
    return config_db_path


class LocalConfig(fort.SQLiteDatabase):
    _version: int = None

    def __init__(self, config_db_path: pathlib.Path):
        config_db_path.parent.mkdir(parents=True, exist_ok=True)
        super().__init__(str(config_db_path))
        self._migrate()

    def _list_tables(self) -> list[str]:
        sql = '''
            select name
            from sqlite_master
            where type = 'table'
        '''
        return [row['name'] for row in self.q(sql)]

    def _migrate(self):
        log.info(f'Local config database schema version is {self.version}')
        if self.version < 1:
            log.info('Migrating to database schema version 1')
            self.u('''
                create table schema_versions (
                    schema_version int,
                    migration_applied_at text
                )
            ''')
            self.u('''
                create table settings (
                    setting_id text primary key,
                    setting_value text
                )
            ''')
            self.version = 1

    def get_setting(self, setting_id: str) -> str | None:
        sql = '''
            select setting_value
            from settings
            where setting_id = :setting_id
        '''
        params = {
            'setting_id': setting_id,
        }
        return self.q_val(sql, params)

    @property
    def openid_client_id(self) -> str:
        return self.get_setting('openid/client-id')

    @openid_client_id.setter
    def openid_client_id(self, value: str):
        self.set_setting('openid/client-id', value)

    @property
    def openid_client_secret(self) -> str:
        return self.get_setting('openid/client-secret')

    @openid_client_secret.setter
    def openid_client_secret(self, value: str):
        self.set_setting('openid/client-secret', value)

    @property
    def secret_key(self) -> str:
        key = self.get_setting('secret-key')
        if key is None:
            key = secrets.token_hex()
            self.set_setting('secret-key', key)
        return key


    def set_setting(self, setting_id: str, setting_value: str):
        sql = '''
            insert into settings (
                setting_id, setting_value
            ) values (
                :setting_id, :setting_value
            ) on conflict (setting_id) do update set
                setting_value = excluded.setting_value
        '''
        params = {
            'setting_id': setting_id,
            'setting_value': setting_value,
        }
        self.u(sql, params)

    @property
    def version(self) -> int:
        if self._version is None:
            if 'schema_versions' in self._list_tables():
                sql = '''
                    select schema_version
                    from schema_versions
                    order by migration_applied_at desc
                    limit 1
                '''
                self._version = int(self.q_val(sql))
            else:
                self._version = 0
        return self._version

    @version.setter
    def version(self, version: int):
        sql = '''
            insert into schema_versions (
                schema_version, migration_applied_at
            ) values (
                :schema_version, :migration_applied_at
            )
        '''
        params = {
            'schema_version': version,
            'migration_applied_at': datetime.datetime.now(tz=datetime.UTC).isoformat(),
        }
        self.u(sql, params)
        self._version = version
