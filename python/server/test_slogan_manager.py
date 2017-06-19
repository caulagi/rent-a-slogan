"""
Tests for interaction with db for slogans
"""
import sqlite3
from tempfile import NamedTemporaryFile
from unittest import TestCase

from .slogan_manager import SloganManager


class SloganManagerTest(TestCase):
    def test_init(self):
        with NamedTemporaryFile() as test_db:
            SloganManager(test_db.name)
            with sqlite3.connect(test_db.name) as db:
                cursor = db.cursor()
                cursor.execute('''
                    select name from sqlite_master where type = 'table' and name = 'slogan'
                ''')
                assert cursor.fetchone()[0] == 'slogan'

    def test_md5(self):
        assert SloganManager.get_md5(
            'test') == '098f6bcd4621d373cade4e832627b4f6'

    def test_create(self):
        with NamedTemporaryFile() as test_db:
            slogan_manager = SloganManager(test_db.name)
            assert slogan_manager.create('test')[1] == 'test'

    def test_create_unique_constraint(self):
        with NamedTemporaryFile() as test_db:
            slogan_manager = SloganManager(test_db.name)
            slogan_manager.create('test')
            with self.assertRaises(sqlite3.IntegrityError):
                slogan_manager.create('test')[1]

    def test_rent_when_available(self):
        with NamedTemporaryFile() as test_db:
            slogan_manager = SloganManager(test_db.name)
            slogan_manager.create('test')
            status, title = slogan_manager.rent()
            assert status
            assert title == 'test'

    def test_rent_none_available(self):
        with NamedTemporaryFile() as test_db:
            slogan_manager = SloganManager(test_db.name)
            slogan_manager.create('test')
            slogan_manager.rent()
            status, _ = slogan_manager.rent()
            assert status is False

    def test_list(self):
        with NamedTemporaryFile() as test_db:
            slogan_manager = SloganManager(test_db.name)
            slogan_manager.create('test 1')
            slogan_manager.create('test 2')
            assert len(slogan_manager.list()) == 2
