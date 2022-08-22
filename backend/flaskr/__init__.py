import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10
# create paginate questions function with 10 per page


def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    completed: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app)
    cors = CORS(app, resources={r"/*": {"origin": "*"}})
    """
    @Completed: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Headers',
                             'GET, POST, PATCH, DELETE, OPTIONS')
        return response
    """
    @Completed:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route("/categories", methods=["GET"])
    def get_all_categories():
        # we fetch all the categories in the database then return them
        categories = Category.query.order_by(Category.id).all()

        if categories is None:
            abort(404)

        return jsonify({
            'success': True,
            'categories': {category.id: category.type for category in categories}
        })

    """
    @Completed
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route("/questions", methods=["GET"])
    def get_questions():
        selection = Question.query.order_by(Question.id).all()
        questions_formatted = paginate_questions(request, selection)

        categories = Category.query.order_by(Category.id).all()
        categories_formatted = {cat.id: cat.type for cat in categories}

        if len(questions_formatted) == 0:
            abort(404)

        return jsonify({
            "success": True,
            "questions": questions_formatted,
            "total_questions": len(questions_formatted),
            "categories": categories_formatted,
            "current_category": None,
        })

    """
    @completed:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        question = Question.query.filter(
            Question.id == question_id).one_or_none()

        if question is None:
            abort(404)

        try:
            db.session.delete(question)
            db.session.commit()
        except:
            abort(422)
        finally:
            db.session.close()

        return jsonify({
            "success": True,
            'question_id': question_id
        })
    """
    @Completed:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route("/questions", methods=['POST'])
    def create_question():
        # getting data from the form
        body = request.get_json()

        # then we add/create/save it to the database and making sure we get each field from the frontend

        question = body.get("question", None)
        answer = body.get("answer", None)
        category = body.get("category", None)
        difficulty = body.get("difficulty", None)

        question = Question(question=question, answer=answer,
                            category=category, difficulty=difficulty)
        selection = Question.query.order_by(Question.id).all()
        currentQuestion = paginate_questions(request, selection)

        if question is None:
            abort(404)
        else:
            try:

                db.session.add(question)
                db.session.commit()

            except:
                db.session.rollback()

            return jsonify(
                {
                    "success": True,
                    "questions": currentQuestion,
                    "total_questions": len(Question.query.all())
                })

    """
    @Completed:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route("/questions/search", methods=["POST"])
    def search_question():
        body = request.json
        search = body.get("searchTerm", None)

        if search:
            questions = Question.query.order_by(Question.id).filter(
                Question.question.ilike('%{}%'.format(search)))

            questions_formatted = [question.format()
                                   for question in questions]

            return jsonify({
                'success': True,
                "questions": questions_formatted,
                "totalQuestions": len(questions.all()),
                "currentCategory": None,
            })
        else:
            abort(422)
    """
    @Completed:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route("/categories/<int:category_id>/questions", methods=['GET'])
    def get_questions_by_category(category_id):

        # fetching a specific category from the database the return that category with all her questions
        category = Category.query.filter(Category.id == category_id).first()
        if category is None:
            abort(404)
        else:
            try:
                selection = Question.query.filter(
                    Question.category == str(category_id)).all()
                current_questions = paginate_questions(request, selection)

                return jsonify({
                    'success': True,
                    'current_category': category.type,
                    'questions': current_questions,
                    'total_questions': len(selection)
                })
            except:
                abort(400)

    """
    @Completed:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route("/quizzes", methods=['POST'])
    def play():
        body = request.get_json()
        prev_questions = body.get('previous_questions', None)
        category = body.get('quiz_category', None)

        questions = Question.query.all()
        if (prev_questions is None) and (category['id'] is None):
            abort(400)

        if category['id'] != 0:
            selection = Question.query.filter(
                Question.id.notin_(prev_questions)).all()
            currentQuestion = paginate_questions(request, selection)
        else:
            selection = Question.query.order_by(Question.category == category['id']).filter(
                Question.id.notin_(prev_questions)).all()

        if len(currentQuestion) > 0:
            next_question = random.choice(currentQuestion)

        return jsonify({
            'success': True,
            "question": next_question,
            'totalQuestions': len(questions),
            "category": category
        })

    """
    @completed:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({
                "success": False,
                "error": 404,
                "message": "Error: not found"
            }),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({
                "success": False,
                "error": 422,
                "message": "Error: unprocessable"
            }),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return (
            jsonify({
                'success': False,
                "error": 400,
                "message": "Error: bad request"
            }),
            400
        )

    @app.errorhandler(500)
    def server_error(error):
        return(
            jsonify({
                'success': False,
                "error": 500,
                'message': "Error: server error"
            }),
            500
        )

    @app.errorhandler(405)
    def method_error(error):
        return (
            jsonify({
                "success": False,
                "error": 405,
                "message": "Error: method unallowed"
            }),
            405
        )

    return app
