import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category, db


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_path = os.getenv('DB_PATH_TEST')
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_questions(self):
        res = self.client().get('/questions?page=1')
        self.assertTrue(res.__dict__['_status_code'], 200)

    def test_get_questions_fail(self):
        res = self.client().get('/questions?page=-1')
        self.assertEqual(res.__dict__['_status_code'], 404)

    def test_delete_question(self):
        question = Question(question='1', answer='1', category=1, difficulty=1)
        question.insert()
        res = self.client().delete('/questions/' + str(question.id))
        self.assertTrue(res.__dict__['_status_code'], 200)

    def test_delete_question_fail(self):
        res = self.client().delete('/questions/-1')
        self.assertTrue(res.__dict__['_status_code'], 404)

    def test_get_categories(self):
        res = self.client().get('/categories')
        self.assertTrue(res.__dict__['_status_code'], 200)

    def test_get_categories_fail(self):
        res = self.client().post('/categories')
        self.assertTrue(res.__dict__['_status_code'], 405)

    def test_add_question(self):
        res = self.client().post('/questions', data=json.dumps({
            'question':  'Heres a new question string',
            'answer':  'Heres a new answer string',
            'difficulty': 1,
            'category': 3,
        }), content_type='application/json')
        self.assertTrue(res.__dict__['_status_code'], 200)

    def test_add_question_fail(self):
        res = self.client().post('/questions')
        self.assertTrue(res.__dict__['_status_code'], 500)

    def test_search_questions(self):
        res = self.client().post('/questions', data=json.dumps({
            'searchTerm': 'this is the term the user is looking for'
        }), content_type='application/json')
        self.assertTrue(res.__dict__['_status_code'], 200)

    def test_search_questions_fail(self):
        res = self.client().post('/questions', data=json.dumps({}),
                                 content_type='application/json')
        self.assertTrue(res.__dict__['_status_code'], 500)

    def test_get_questions_based_on_category(self):
        category = Category(type='1')
        db.session.add(category)
        db.session.commit()
        res = self.client().get('/categories/' + str(category.id) + '/questions')
        self.assertTrue(res.__dict__['_status_code'], 200)

    def test_get_questions_based_on_category_fail(self):
        res = self.client().get('/categories/-1/questions')
        print(res.__dict__)
        self.assertTrue(res.__dict__['_status_code'], 404)

    def test_play_quiz(self):
        res = self.client().post('/quizzes', data=json.dumps({
            'previous_questions': [1, 4, 20, 15],
            'quiz_category': {
                'type': 'click',
                'category': 1
            }
        }), content_type='application/json')
        self.assertEqual(res.__dict__['_status_code'], 200)

    def test_play_quiz_fail(self):
        res = self.client().post('/quizzes', data=json.dumps({}),
                                 content_type='application/json')
        print(res.__dict__)
        self.assertEqual(res.__dict__['_status_code'], 500)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
