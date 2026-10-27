import unittest
from flask import current_app
from app import create_app, db


class BasicsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_app_exists(self):
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])


class EmailAndCrudTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_unique_recipients_removes_duplicates(self):
        from app.email import unique_recipients
        r = unique_recipients('flaskaulasweb@zohomail.com', 'f.blanco@aluno.ifsp.edu.br',
                              'FlaskAulasWeb@zohomail.com ', '', None)
        self.assertEqual(r, ['flaskaulasweb@zohomail.com', 'f.blanco@aluno.ifsp.edu.br'])

    def test_new_user_sends_to_professor_and_institutional_once(self):
        from unittest import mock
        with mock.patch('app.main.views.send_simple_message') as m:
            self.client.post('/', data={'name': 'Ana',
                                        'email': 'flaskaulasweb@zohomail.com'})
        recipients = m.call_args[0][0]
        self.assertEqual(sorted(recipients),
                         ['f.blanco@aluno.ifsp.edu.br', 'flaskaulasweb@zohomail.com'])

    def test_edit_and_delete_user(self):
        from unittest import mock
        from app.models import User, Role
        with mock.patch('app.main.views.send_simple_message'):
            self.client.post('/', data={'name': 'Ana'})
        user = User.query.filter_by(username='Ana').first()
        self.assertEqual(user.role.name, 'User')
        admin_id = Role.query.filter_by(name='Admin').first().id
        self.client.post(f'/edit/{user.id}', data={'name': 'Ana B', 'role': admin_id})
        user = db.session.get(User, user.id)
        self.assertEqual((user.username, user.role.name), ('Ana B', 'Admin'))
        self.client.post(f'/delete/{user.id}')
        self.assertIsNone(db.session.get(User, user.id))
