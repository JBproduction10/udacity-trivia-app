import os
from re import S
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_host = 'localhost:5432'
        self.database_user = 'postgres'
        self.database_password = 'jbyoung10'
        self.database_name = 'trivia_test'
        self.database_path = 'postgresql://{}:{}@{}/{}'.format(self.database_user,self.database_password,self.database_host, self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            self.migrate = Migrate()
            self.migrate.init_app(self.db, self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    Completed
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_pagination_questions(self):
        res = self.client().get("/questions?page=1")
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        
    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_categories'])
        
    def test_405_get_categories(self):
        res= self.client().delete("/categories")
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data['error'], 405)
        self.assertEqual(data['message'], 'Error: method not allowed')
        
    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(data['questions'])
        
    def test_delete_question(self):
        id = Question.query.all()[-1]
        self.client().delete("/questions/2")
        res = Question.query.filter(Question.id == 2).one_or_none()
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['question_id'], 2)
        
    def test_404_delete_question(self):
        res = self.client().delete("/questions/200")
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], "Error: not found")
        
    def test_add_question(self):
        res = self.client().post("/questions",
                                json={
                                    "question": "This is a question",
                                    "answer": "This is an answer",
                                    "difficulty": 5,
                                    "category": 3
                                })    
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        
    def test_500_add_question(self):
        res = self.client().post("/questions",
                                json={
                                    "question": "This is a question",
                                    "answer": "This is an answer",
                                    "difficulty": 5,
                                    "category": 3
                                })
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 500)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 500)
        self.assertEqual(data['message'], "Error: server error")
        
    def test_search_question(self):
        res = self.client().post("/questions/search", json={
            "searchTerm": "classes"
        })
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['totalQuestions'])
        
    def test_422_search_question(self):
        res = self.client().post("/questions/search", json={'s': "classes"})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 422)
        self.assertEqual(data['message'], "Error: unprocessable")
        
    def test_get_question_by_category(self):
        res = self.client().get("/categories/1/questions")
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['currentCategory'])
        self.assertTrue(data['totalQuestions'])
        self.assertTrue(len(data['questions']))
        
    def test_404_get_questions_by_category(self):
        res = self.client().get("/categories/18200/questions")
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], "Error: not found")
        
    def test_quiz(self):
        res = self.client().post("/quizzes", json={"quiz_category": {"type":"Sports", "id": 1},
                                                    "previous_questions": [1,3,5]})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        
    def test_404_quiz(self):
        res = self.client().post("/quizzes", json={"quiz_category": {"type":"zizag", "id": 3},
                                                    "previous_questions": [4, 3, 1]})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'Error: not found')
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()