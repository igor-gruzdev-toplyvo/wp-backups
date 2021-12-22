from os import path, environ, system
from datetime import datetime


class Backup:
    def __init__(self):
        self.env = environ.Env()
        self.backups_path = "/home/toplyvosite/Project/toplyvo_landing_backups"
        self.current_date = datetime.today().strftime("%Y-%m-%d")
        self.dump_path = None
        self.mod_date_array = {}
        self.source_paths = {}

    def __src_generator(self):
        """Method generates src path's for furher operations"""
        wp_prefix = (
            "/home/toplyvosite/Project/new_wordpress_core_prod/wordpress/wp-content"
        )

        self.dump_path = f"{wp_prefix}/{self.current_date}-bc.sql"

        src_parths = {
            f"{wp_prefix}/plugins": "plugins",
            f"{wp_prefix}/uploads": "uploads",
            f"{self.dump_path}": "database",
        }

        for element in src_parths:
            self.source_paths.update(element)

    def __array_generator(self):
        """Method generates dict of folders and
        theirs modification dates for furher operations
        """
        cycle = 1
        while cycle < 6:
            key = f"{self.backups_path}/{cycle}"
            value = float(path.getmtime(key))
            element = {key: value}
            self.mod_date_array.update(element)
            cycle += 1
        else:
            print("Array successfully generated")

    def __dump_mysql(self):
        """Method creates mysql database 
        dump for further operations
        """
        user = self.env("DB_USER")
        password = self.env("DB_PW")
        database = self.env("DB_NAME")
        env_path = self.env("COMPOSE_ENV")
        compose_cfg = self.env("COMPOSE_CFG")

        return system(
            f"""env $(cat {env_path}) \
            docker-compose -f {compose_cfg} exec -T mysql \
            mysqldump -u{user} -p{password} {database} > {self.dump_path}
            """
        )

    def make_backup(self):
        """Method does backup and archive 
        of current wordpress state
        """
        self.__src_generator()
        self.__array_generator()
        self.__dump_mysql()

        last_modified_element = min(self.mod_date_array, key=self.mod_date_array.get)

        try:
            system(f"rm -rf {last_modified_element}/*")
        except Exception:
            pass

        for key, value in self.source_paths:
            system(
                f"tar -xvzf {last_modified_element}/\
                    {value}-{self.current_date}.tar.gz {key}"
            )
