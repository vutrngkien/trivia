import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    CORS(app, resources={r"/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers['Access-Control-Allow-Origin'] = '*' 
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        response.headers['Access-Control-Allow-Methods'] = 'GET,POST,DELETE'
        return response
        

    @app.route('/categories')
    def get_categories():
        try:
            categoriesInstance = db.session.query(Category).all()
            categories = {}
            for category in categoriesInstance:
                data = category.format()
                categories[data['id']] = data['type']
            return jsonify({'categories': categories})
        except:
            abort(500)

    @app.route('/questions')
    def get_questions():
        try:
            page_number = int(request.args.get('page'))
            per_page = 10
            data = {
                        "questions": [],
                        "total_questions": 0,
                        "categories": {},
                        "current_category": None
                    }
            
            questions_instance = Question.query.order_by(Question.id.asc()).all()
            questions = []
            start = (page_number - 1)*per_page
            end = start + per_page
            total_questions = len(questions_instance) 
            if start > total_questions or start < 0:
                abort(422)
            elif end > total_questions:
                questions = questions_instance[start :]
            else:
                questions = questions_instance[start : end]

            for question in questions:
                data['questions'].append(question.format())

            categoriesInstance = db.session.query(Category).all()
            categories = {}
            for category in categoriesInstance:
                category_dict = category.format()
                categories[category_dict['id']] = category_dict['type']
            data['total_questions'] = total_questions
            data['categories'] = categories
            
            return jsonify(data)
        except:
            abort(404)

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.get(question_id)
            question.delete()
            return jsonify({'success': True, 'id': question_id})
        except:
            abort(422)


    @app.route('/categories/<int:category_id>/questions')
    def get_question_baseon_category(category_id):
        try:
            data = {
                    'questions': [],
                    'total_questions': 0,
                    'current_category': None
                }
            all_questions = db.session.query(Question).all()
            questions_instance = db.session.query(Question).filter_by(category=category_id).all()
            category = Category.query.get(category_id)
            questions = []
            for question in questions_instance:
                questions.append(question.format())
            
            data['total_questions'] = len(all_questions)
            data['questions'] = questions
            data['current_category'] = category.format()['type']
            return jsonify(data)
        except:
            abort(500)

    @app.route('/questions', methods=['POST'])
    def add_new_question_or_search():
        try:
            data = request.get_json()
            if 'searchTerm' not in data:
                new_question = Question(question=data['question'], answer=data['answer'], category=data['category'], difficulty=data['difficulty'])
                new_question.insert()
                return jsonify({'success': True})
            else:
                search_term = data['searchTerm']
                questions_instance = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
                questions_instance_all = Question.query.all()
                questions = [question.format() for question in questions_instance]
                return jsonify({
                    'questions': questions,
                    'totalQuestions': len(questions_instance_all),
                    'currentCategory': None
                })
        except:
            abort(500)

    
    @app.route('/quizzes', methods=['POST'])
    def quizzes():
        try:
            data = request.get_json()
            previous_questions = data['previous_questions']
            quiz_category = data['quiz_category']
            questions_instance = Question.query.filter(Question.category==quiz_category['id']).all() if quiz_category['type'] != 'click' else Question.query.all()
            questions = [question.format() for question in questions_instance]
            not_in_previous_questions = [question for question in questions if question['id'] not in previous_questions]
            question = not_in_previous_questions[random.randint(0, len(not_in_previous_questions)-1)] if len(not_in_previous_questions) > 0 else None
            return jsonify({
                'question': question,
            })
        except:
            abort(500)


    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'page not found!'}), 404

    @app.errorhandler(500)
    def bad_request(error):
        return jsonify({'error': 'bab request!'}), 500
    
    @app.errorhandler(422)
    def bad_request(error):
        return jsonify({'error': 'unprocessable entity'}), 422

    return app

