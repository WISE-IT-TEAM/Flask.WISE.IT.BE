from .sqool import BaseBlueprint
import os


class ArtistBlueprint(BaseBlueprint):
    # * ArtistDB SQL 파일 리스트
    SQL_FILES = ["Table.sql", "Artist.sql", "Member.sql", "Album.sql"]

    def __init__(self):
        super().__init__("sqool_artist", __name__, self.SQL_FILES)

    def register_routes(self):
        super().register_routes()


sqool_artist_bp = ArtistBlueprint().get_blueprint()